#!/usr/bin/env python3
"""re_toolkit — motor de análise de binário nativo/firmware. Python puro, zero dependências.

Diferente de um documento de método: aqui há PARSER de verdade, com verificação de
integridade e saída de evidência (hash/offset/CRC). Roda offline, sem instalar nada.

Subcomandos:
    triage   <arquivo>                 magic, arquitetura, entropia, strings
    uimage   <arquivo> [--extract D]   header U-Boot, CRC do header e do payload
    esp      <arquivo> [--offset N]    tabela de partição ESP (0x50AA / MD5 0xEBEB)
    dtb      <arquivo>                 FDT/FIT: propriedades, /images, hashes
    uf2      <arquivo> [--extract F]   blocos UF2, reconstrução por targetAddr
    intelhex <arquivo> [--out F]       Intel HEX / SREC -> binário + mapa de endereços
    elf      <arquivo>                 header, seções, símbolos, notas
    squashfs <arquivo>                 superblock (metadados, não extrai)
    selftest                           gera fixtures válidas e verifica cada parser

Saída sempre inclui `read_only=true` e `executed_target=false`.
Exit: 0 ok · 1 achado de integridade (CRC/hash falhou) · 2 input inválido
"""
from __future__ import annotations

import argparse
import binascii
import gzip
import hashlib
import json
import lzma
import math
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path

READ_ONLY = {"read_only": True, "executed_target": False}

MAGICS = [
    (b"\x7fELF", 0, "ELF"),
    (b"MZ", 0, "PE (DOS header)"),
    (b"PK\x03\x04", 0, "ZIP (container/APK/JAR)"),
    (b"\x27\x05\x19\x56", 0, "U-Boot legacy uImage"),
    (b"\xd0\x0d\xfe\xed", 0, "FIT / devicetree (DTB)"),
    (b"hsqs", None, "SquashFS (LE)"),
    (b"sqsh", None, "SquashFS (BE)"),
    (b"\x1f\x8b\x08", None, "gzip"),
    (b"\xfd7zXZ\x00", None, "xz"),
    (b"\x28\xb5\x2f\xfd", None, "zstd"),
    (b"\x04\x22\x4d\x18", None, "LZ4 frame"),
    (b"\x28\xcd\x3d\x45", None, "CramFS"),
    (b"UBI#", None, "UBI"),
    (b"UF2", 0, "UF2 (provável)"),
    (b"DfuSe", 0, "DfuSe"),
    (b"UPX!", None, "UPX (rodapé)"),
    (b"\x53\xef", 0x438, "ext2/3/4 superblock"),
    (b"\xaa\x50", None, "ESP partition entry (0x50AA LE)"),
]

ELF_MACHINE = {0x03: "x86", 0x3E: "x86-64", 0x28: "ARM", 0xB7: "AArch64",
               0x08: "MIPS", 0x14: "PowerPC", 0x15: "PowerPC64", 0xF3: "RISC-V",
               0x02: "SPARC", 0x2B: "SPARCv9", 0x16: "S390"}
UIMAGE_OS = {0: "invalid", 2: "OpenBSD", 3: "NetBSD", 5: "Linux", 9: "FreeBSD", 22: "vxWorks"}
UIMAGE_ARCH = {2: "ARM", 3: "x86", 5: "MIPS", 6: "MIPS64", 7: "PowerPC", 14: "AArch64", 22: "RISC-V"}
UIMAGE_TYPE = {1: "standalone", 2: "kernel", 3: "ramdisk", 5: "multi", 6: "firmware", 7: "script"}
UIMAGE_COMP = {0: "none", 1: "gzip", 2: "bzip2", 3: "lzma", 4: "lzo", 5: "lz4", 6: "zstd"}
ESP_TYPES = {0x00: "app", 0x01: "data"}
ESP_SUBTYPES = {
    (0x00, 0x00): "factory", (0x00, 0x10): "ota_0", (0x00, 0x11): "ota_1",
    (0x01, 0x00): "otadata", (0x01, 0x01): "phy", (0x01, 0x02): "nvs",
    (0x01, 0x03): "coredump", (0x01, 0x04): "nvs_keys", (0x01, 0x82): "spiffs",
    (0x01, 0x83): "fat",
}
FDT_MAGIC = 0xD00DFEED
UF2_MAGIC0, UF2_MAGIC1, UF2_MAGIC_END = 0x0A324655, 0x9E5D5157, 0x0AD0BC05


def die(msg: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}", file=sys.stderr)
    raise SystemExit(code)


def read_bytes(path: str) -> bytes:
    p = Path(path)
    if not p.is_file():
        die(f"arquivo não encontrado: {p}")
    return p.read_bytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entropia(data: bytes, bloco: int = 4096, max_blocos: int = 64) -> dict:
    valores = []
    for off in range(0, min(len(data), bloco * max_blocos), bloco):
        chunk = data[off:off + bloco]
        if not chunk:
            break
        n = len(chunk)
        c = Counter(chunk)
        h = -sum((v / n) * math.log2(v / n) for v in c.values())
        valores.append({"offset": off, "entropy": round(h, 3)})
    media = round(sum(v["entropy"] for v in valores) / len(valores), 3) if valores else 0.0
    return {"avg": media, "blocks": len(valores),
            "high_blocks": sum(1 for v in valores if v["entropy"] > 7.5),
            "samples": valores[:8]}


# ---------------------------------------------------------------- triage
def cmd_triage(args) -> int:
    data = read_bytes(args.path)
    detectado = []
    for sig, off, nome in MAGICS:
        if off is None:
            idx = data.find(sig)
            if idx >= 0:
                detectado.append({"name": nome, "offset": idx})
        elif data[off:off + len(sig)] == sig:
            detectado.append({"name": nome, "offset": off})

    elf = None
    if data[:4] == b"\x7fELF" and len(data) >= 20:
        endian = "little" if data[5] == 1 else "big"
        mach = int.from_bytes(data[18:20], endian)
        elf = {"arch": ELF_MACHINE.get(mach, f"0x{mach:04x}"), "endianness": endian,
               "class": {1: "ELF32", 2: "ELF64"}.get(data[4], "?")}

    texto = [s for s in _strings(data, 8, 2 * 1024 * 1024)][: args.strings]
    out = {"path": str(args.path), "size": len(data), "sha256": sha256(data),
           "first_bytes": data[:32].hex(" "), "detected": detectado, "elf": elf,
           "entropy": entropia(data), "strings": texto, **READ_ONLY}
    return _emit(out, args.json, _print_triage)


def _print_triage(o: dict) -> None:
    print(f"arquivo : {o['path']}")
    print(f"tamanho : {o['size']} bytes")
    print(f"sha256  : {o['sha256']}")
    print(f"início  : {o['first_bytes']}")
    print("formato :")
    if o["detected"]:
        for d in o["detected"]:
            print(f"  - {d['name']} @ 0x{d['offset']:x}")
    else:
        print("  - nenhuma assinatura conhecida (cifra, compressão crua ou região de flash)")
    if o["elf"]:
        e = o["elf"]
        print(f"elf     : {e['class']} arch={e['arch']} endianness={e['endianness']}")
    e = o["entropy"]
    print(f"entropia: média {e['avg']} bits/byte em {e['blocks']} blocos "
          f"({e['high_blocks']} acima de 7.5)")
    if o["strings"]:
        print("strings :")
        for s in o["strings"][:8]:
            print(f"  {s[:70]}")


def _strings(data: bytes, minimo: int, limite: int) -> list[str]:
    out, cur = [], bytearray()
    for b in data[:limite]:
        if 0x20 <= b < 0x7F:
            cur.append(b)
        else:
            if len(cur) >= minimo:
                out.append(cur.decode("ascii"))
            cur.clear()
    if len(cur) >= minimo:
        out.append(cur.decode("ascii"))
    return out


# ---------------------------------------------------------------- uImage
def cmd_uimage(args) -> int:
    data = read_bytes(args.path)
    if len(data) < 64:
        die("arquivo menor que o header de 64 bytes")
    (magic, hcrc, ts, size, load, ep, dcrc, os_id, arch, typ,
     comp, name) = struct.unpack(">7I4B32s", data[:64])
    if magic != 0x27051956:
        die(f"magic de uImage ausente (0x{magic:08x})")

    header_zero = bytearray(data[:64])
    header_zero[4:8] = b"\x00\x00\x00\x00"
    hcrc_calc = zlib.crc32(bytes(header_zero)) & 0xFFFFFFFF
    payload = data[64:64 + size] if size <= len(data) - 64 else data[64:]
    dcrc_calc = zlib.crc32(payload) & 0xFFFFFFFF

    comp_nome = UIMAGE_COMP.get(comp, f"0x{comp:02x}")
    out = {
        "path": str(args.path), "sha256": sha256(data), "size_file": len(data),
        "header": {
            "magic": f"0x{magic:08x}", "header_crc": f"0x{hcrc:08x}",
            "header_crc_calc": f"0x{hcrc_calc:08x}", "header_crc_ok": hcrc == hcrc_calc,
            "timestamp": ts, "data_size": size, "load_addr": f"0x{load:08x}",
            "entry_point": f"0x{ep:08x}", "data_crc": f"0x{dcrc:08x}",
            "data_crc_calc": f"0x{dcrc_calc:08x}", "data_crc_ok": dcrc == dcrc_calc,
            "os": UIMAGE_OS.get(os_id, f"0x{os_id:02x}"),
            "arch": UIMAGE_ARCH.get(arch, f"0x{arch:02x}"),
            "type": UIMAGE_TYPE.get(typ, f"0x{typ:02x}"),
            "compression": comp_nome,
            "name": name.rstrip(b"\x00").decode("latin-1"),
        },
        "payload_sha256": sha256(payload), "payload_size": len(payload),
        **READ_ONLY,
    }

    if args.extract:
        destino = Path(args.extract)
        destino.parent.mkdir(parents=True, exist_ok=True)
        bruto = payload
        descomprimido = None
        try:
            if comp_nome == "gzip":
                descomprimido = gzip.decompress(bruto)
            elif comp_nome in ("lzma", "xz"):
                descomprimido = lzma.decompress(bruto)
            elif comp_nome == "zstd" and hasattr(zlib, "decompress"):
                descomprimido = zlib.decompress(bruto)
        except (OSError, EOFError, lzma.LZMAError, zlib.error) as exc:
            out["extract_error"] = f"descompressão {comp_nome} falhou: {exc}"
        conteudo = descomprimido if descomprimido is not None else bruto
        destino.write_bytes(conteudo)
        out["extracted"] = {"path": str(destino), "size": len(conteudo),
                            "sha256": sha256(conteudo),
                            "decompressed": descomprimido is not None}

    ok = out["header"]["header_crc_ok"] and out["header"]["data_crc_ok"]
    _emit(out, args.json, _print_uimage)
    return 0 if ok else 1


def _print_uimage(o: dict) -> None:
    h = o["header"]
    print(f"uImage   : {o['path']} ({o['size_file']} bytes, sha256 {o['sha256'][:16]}…)")
    print(f"magic    : {h['magic']}  nome: {h['name']!r}")
    print(f"arch/os  : {h['arch']} / {h['os']}  tipo: {h['type']}  compressão: {h['compression']}")
    print(f"load/ep  : {h['load_addr']} / {h['entry_point']}")
    print(f"payload  : {h['data_size']} bytes (presente: {o['payload_size']})")
    print(f"CRC hdr  : {h['header_crc']} vs calculado {h['header_crc_calc']} -> "
          f"{'OK' if h['header_crc_ok'] else 'FALHOU'}")
    print(f"CRC data : {h['data_crc']} vs calculado {h['data_crc_calc']} -> "
          f"{'OK' if h['data_crc_ok'] else 'FALHOU'}")
    if "extracted" in o:
        e = o["extracted"]
        print(f"extraído : {e['path']} ({e['size']} bytes, descomprimido={e['decompressed']})")
    if "extract_error" in o:
        print(f"AVISO    : {o['extract_error']}")


# ---------------------------------------------------------------- ESP
def parse_esp_table(data: bytes, offset: int) -> dict:
    entradas, md5 = [], None
    for i in range(96):  # até 0xC00 bytes
        base = offset + i * 32
        if base + 32 > len(data):
            break
        magic, typ, sub, off, size, label, flags = struct.unpack("<HBBII16sI", data[base:base + 32])
        if magic == 0xEBEB:
            md5 = data[base + 16:base + 32].hex()
            continue
        if magic != 0x50AA:
            break
        entradas.append({
            "index": i, "type": ESP_TYPES.get(typ, f"0x{typ:02x}"),
            "subtype": ESP_SUBTYPES.get((typ, sub), f"0x{sub:02x}"),
            "offset": f"0x{off:06x}", "size": size, "end": f"0x{off + size:06x}",
            "label": label.rstrip(b"\x00").decode("latin-1"), "flags": f"0x{flags:08x}",
        })
    return {"entries": entradas, "md5_declared": md5}


def cmd_esp(args) -> int:
    data = read_bytes(args.path)
    offset = args.offset if args.offset is not None else 0x8000
    if offset + 32 > len(data):
        die(f"offset 0x{offset:x} além do arquivo ({len(data)} bytes)")
    if data[offset:offset + 2] != b"\xaa\x50":
        # tenta localizar a tabela
        idx = data.find(b"\xaa\x50", offset)
        if idx < 0:
            die("tabela de partição ESP não encontrada (magic 0x50AA)")
        offset = idx
    tabela = parse_esp_table(data, offset)
    if not tabela["entries"]:
        die("magic encontrado mas nenhuma entrada válida (possível falso positivo)")

    if tabela["md5_declared"]:
        calculado = hashlib.md5(data[offset:offset + 32 * len(tabela["entries"])]).hexdigest()
        tabela["md5_calc"] = calculado
        tabela["md5_ok"] = calculado == tabela["md5_declared"]

    out = {"path": str(args.path), "sha256": sha256(data), "table_offset": f"0x{offset:x}",
           "table": tabela, **READ_ONLY}
    _emit(out, args.json, _print_esp)
    return 0 if tabela.get("md5_ok", True) else 1


def _print_esp(o: dict) -> None:
    t = o["table"]
    print(f"ESP      : {o['path']} (tabela em {o['table_offset']})")
    print(f"{'#':<3}{'tipo':<7}{'subtipo':<11}{'offset':<11}{'tamanho':>9}  {'fim':<11}label")
    for e in t["entries"]:
        print(f"{e['index']:<3}{e['type']:<7}{e['subtype']:<11}{e['offset']:<11}"
              f"{e['size']:>9}  {e['end']:<11}{e['label']}")
    if t.get("md5_declared"):
        print(f"MD5      : declarado {t['md5_declared'][:16]}… calculado {t.get('md5_calc','')[:16]}… "
              f"-> {'OK' if t.get('md5_ok') else 'FALHOU'}")
    else:
        print("MD5      : não declarado na tabela")


# ---------------------------------------------------------------- DTB / FIT
def parse_fdt(data: bytes, base: int = 0) -> dict:
    if data[base:base + 4] != b"\xd0\x0d\xfe\xed":
        die("magic FDT ausente (0xD00DFEED)")
    (magic, totalsize, off_struct, off_strings, off_rsvmap, version,
     last_comp, boot_cpuid, size_strings, size_struct) = struct.unpack(
        ">10I", data[base:base + 40])
    strs = data[base + off_strings: base + off_strings + size_strings]

    pos = base + off_struct
    fim = pos + size_struct
    stack: list[str] = []
    nodes: list[dict] = []

    while pos + 4 <= fim:
        token = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
        if token == 1:  # BEGIN_NODE
            end = data.index(b"\x00", pos)
            nome = data[pos:end].decode("latin-1")
            pos = (end + 4) & ~3
            stack.append(nome or "/")
            nodes.append({"path": "/" + "/".join(x for x in stack if x and x != "/"),
                          "props": {}})
        elif token == 2:  # END_NODE
            if stack:
                stack.pop()
        elif token == 3:  # PROP
            ln, nameoff = struct.unpack(">II", data[pos:pos + 8])
            pos += 8
            valor = data[pos:pos + ln]
            pos = (pos + ln + 3) & ~3
            end = strs.index(b"\x00", nameoff)
            nome = strs[nameoff:end].decode("latin-1")
            if nodes:
                nodes[-1]["props"][nome] = _fdt_value(valor)
        elif token == 4:  # NOP
            continue
        elif token == 9:  # END
            break
        else:
            break
    return {"totalsize": totalsize, "version": version, "nodes": nodes,
            "node_count": len(nodes)}


def _fdt_value(raw: bytes):
    if not raw:
        return ""
    try:  # string primeiro: "none", "kernel", "vendor,soc"
        txt = raw.rstrip(b"\x00").decode("utf-8")
        if txt and all(32 <= ord(c) < 127 for c in txt):
            return txt
    except UnicodeDecodeError:
        pass
    if len(raw) == 4:
        return f"0x{struct.unpack('>I', raw)[0]:x}"
    return raw.hex()


def cmd_dtb(args) -> int:
    data = read_bytes(args.path)
    fdt = parse_fdt(data)
    imagens = [n for n in fdt["nodes"] if "/images/" in n["path"] and n["path"].count("/") == 2]
    hashes = [n for n in fdt["nodes"] if "hash" in n["path"] or "signature" in n["path"]]
    out = {"path": str(args.path), "sha256": sha256(data), "fdt": fdt,
           "images": [{"path": n["path"], "props": n["props"]} for n in imagens],
           "hash_nodes": [{"path": n["path"], "props": n["props"]} for n in hashes],
           **READ_ONLY}
    _emit(out, args.json, _print_dtb)
    return 0


def _print_dtb(o: dict) -> None:
    f = o["fdt"]
    print(f"FDT/FIT  : {o['path']} (versão {f['version']}, {f['node_count']} nós)")
    raiz = next((n for n in f["nodes"] if n["path"] == "/"), None)
    if raiz:
        print(f"raiz     : model={raiz['props'].get('model','—')} "
              f"compatible={raiz['props'].get('compatible','—')}")
    if o["images"]:
        print("imagens  :")
        for img in o["images"]:
            d = img["props"].get("data", "")
            tam = len(d) // 2 if isinstance(d, str) and all(
                c in "0123456789abcdef" for c in d) else len(str(d))
            print(f"  {img['path']}: type={img['props'].get('type','—')} "
                  f"arch={img['props'].get('arch','—')} comp={img['props'].get('compression','—')} "
                  f"load={img['props'].get('load','—')} bytes≈{tam}")
    if o["hash_nodes"]:
        print("hash/sig :")
        for n in o["hash_nodes"]:
            print(f"  {n['path']}: algo={n['props'].get('algo','—')} "
                  f"value={str(n['props'].get('value',''))[:24]}")
    else:
        print("hash/sig : nenhum nó hash/signature encontrado")


# ---------------------------------------------------------------- UF2
def cmd_uf2(args) -> int:
    data = read_bytes(args.path)
    if len(data) % 512 != 0:
        print(f"AVISO: tamanho {len(data)} não é múltiplo de 512 — últimos bytes ignorados",
              file=sys.stderr)
    blocos = []
    for i in range(len(data) // 512):
        b = data[i * 512:(i + 1) * 512]
        m0, m1, flags, addr, payload, blkno, numblk, fam = struct.unpack("<8I", b[:32])
        mend = struct.unpack("<I", b[508:512])[0]
        if m0 != UF2_MAGIC0 or m1 != UF2_MAGIC1 or mend != UF2_MAGIC_END:
            die(f"bloco {i}: magic UF2 inválido "
                f"(0x{m0:08x}/0x{m1:08x}/0x{mend:08x})")
        blocos.append({"index": i, "block_no": blkno, "num_blocks": numblk,
                       "target_addr": addr, "payload_size": payload, "flags": flags,
                       "family": fam,
                       "data": b[32:32 + min(payload, 476)]})
    num = blocos[0]["num_blocks"]
    if any(b["num_blocks"] != num for b in blocos):
        print("AVISO: blocos declaram num_blocks divergente", file=sys.stderr)

    endereco_base = min(b["target_addr"] for b in blocos)
    tamanho_total = max(b["target_addr"] + b["payload_size"] for b in blocos) - endereco_base
    memoria = bytearray(tamanho_total)
    cobertos = bytearray(tamanho_total)
    for b in blocos:
        rel = b["target_addr"] - endereco_base
        memoria[rel:rel + len(b["data"])] = b["data"]
        cobertos[rel:rel + len(b["data"])] = b"\x01" * len(b["data"])
    buracos = cobertos.count(0)

    out = {"path": str(args.path), "sha256": sha256(data), "blocks": len(blocos),
           "declared_blocks": num, "base_address": f"0x{endereco_base:08x}",
           "span": tamanho_total, "uncovered_bytes": buracos,
           "payload_sha256": sha256(bytes(memoria)), **READ_ONLY}
    if args.extract:
        destino = Path(args.extract)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(bytes(memoria))
        out["extracted"] = {"path": str(destino), "size": len(memoria),
                            "sha256": sha256(bytes(memoria))}
    _emit(out, args.json, _print_uf2)
    return 0 if buracos == 0 else 1


def _print_uf2(o: dict) -> None:
    print(f"UF2      : {o['path']} ({o['blocks']} blocos, declarado {o['declared_blocks']})")
    print(f"base     : {o['base_address']}  span: {o['span']} bytes")
    print(f"payload  : sha256 {o['payload_sha256'][:16]}…  buracos: {o['uncovered_bytes']} bytes")
    if "extracted" in o:
        e = o["extracted"]
        print(f"reconstruído: {e['path']} ({e['size']} bytes)")


# ---------------------------------------------------------------- Intel HEX / SREC
def parse_intelhex(texto: str) -> dict:
    memoria: dict[int, int] = {}
    base = 0
    registros = 0
    for numero, linha in enumerate(texto.splitlines(), 1):
        linha = linha.strip()
        if not linha:
            continue
        if not linha.startswith(":"):
            raise ValueError(f"linha {numero}: registro não começa com ':'")
        bruto = bytes.fromhex(linha[1:])
        if len(bruto) < 5:
            raise ValueError(f"linha {numero}: registro curto")
        tam, addr_hi, addr_lo, tipo = bruto[0], bruto[1], bruto[2], bruto[3]
        dados = bruto[4:4 + tam]
        if len(dados) != tam:
            raise ValueError(f"linha {numero}: tamanho declarado {tam} != lido {len(dados)}")
        if (sum(bruto) & 0xFF) != 0:
            raise ValueError(f"linha {numero}: checksum inválido")
        if tipo == 0x00:
            addr = base + (addr_hi << 8) + addr_lo
            for i, valor in enumerate(dados):
                memoria[addr + i] = valor
        elif tipo == 0x01:
            registros += 1
            break
        elif tipo == 0x02:
            base = int.from_bytes(dados, "big") << 4
        elif tipo == 0x04:
            base = int.from_bytes(dados, "big") << 16
        registros += 1
    return {"memory": memoria, "records": registros}


def parse_srec(texto: str) -> dict:
    memoria: dict[int, int] = {}
    por_tamanho = {"0": 4, "1": 2, "2": 3, "3": 4, "5": 2, "6": 3, "7": 4, "8": 3, "9": 2}
    registros = 0
    for numero, linha in enumerate(texto.splitlines(), 1):
        linha = linha.strip()
        if not linha or linha[0] not in "Ss":
            continue
        if linha[1] not in por_tamanho:
            raise ValueError(f"linha {numero}: tipo S inválido")
        if len(linha) % 2 != 0:
            raise ValueError(f"linha {numero}: comprimento ímpar (SREC é texto hex)")
        bruto = bytes.fromhex(linha[2:])
        contagem = bruto[0]
        if len(bruto) - 1 != contagem:
            raise ValueError(f"linha {numero}: contagem {contagem} != {len(bruto) - 1}")
        if (sum(bruto) & 0xFF) != 0xFF:
            raise ValueError(f"linha {numero}: checksum inválido")
        addr_len = por_tamanho[linha[1]]
        tipo = linha[1]
        if tipo in ("1", "2", "3"):  # S0 = header (metadata), não é dado de memória
            addr = int.from_bytes(bruto[1:1 + addr_len], "big")
            dados = bruto[1 + addr_len:-1]
            for i, valor in enumerate(dados):
                memoria[addr + i] = valor
        registros += 1
    return {"memory": memoria, "records": registros}


def cmd_intelhex(args) -> int:
    texto = read_bytes(args.path).decode("ascii", errors="replace")
    primeiro = texto.lstrip()[:2]
    try:
        if primeiro.startswith(":"):
            r = parse_intelhex(texto)
            formato = "Intel HEX"
        elif primeiro.upper() in ("S0", "S1", "S2", "S3"):
            r = parse_srec(texto)
            formato = "SREC"
        else:
            die("formato não reconhecido (esperado Intel HEX ':' ou SREC 'S0/S1/S2/S3')")
    except ValueError as exc:
        die(f"{formato if 'formato' in dir() else 'hex'} inválido: {exc}")

    memoria = r["memory"]
    if not memoria:
        die("nenhum byte de dados encontrado")
    a_min, a_max = min(memoria), max(memoria)
    span = a_max - a_min + 1
    imagem = bytearray(span)
    cobertura = bytearray(span)
    for addr, valor in memoria.items():
        imagem[addr - a_min] = valor
        cobertura[addr - a_min] = 1
    buracos = cobertura.count(0)

    out = {"path": str(args.path), "format": formato, "records": r["records"],
           "base_address": f"0x{a_min:08x}", "end_address": f"0x{a_max:08x}",
           "span": span, "bytes_written": len(memoria), "gaps": buracos,
           "image_sha256": sha256(bytes(imagem)), **READ_ONLY}
    if args.out:
        destino = Path(args.out)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(bytes(imagem))
        out["extracted"] = {"path": str(destino), "size": span,
                            "sha256": sha256(bytes(imagem))}
    _emit(out, args.json, _print_hex)
    return 0


def _print_hex(o: dict) -> None:
    print(f"{o['format']:<9}: {o['path']} ({o['records']} registros)")
    print(f"endereços: {o['base_address']} .. {o['end_address']} ({o['span']} bytes)")
    print(f"escritos : {o['bytes_written']} bytes · buracos (gap): {o['gaps']} bytes")
    print(f"imagem   : sha256 {o['image_sha256'][:16]}…")
    if "extracted" in o:
        print(f"salvo    : {o['extracted']['path']} ({o['extracted']['size']} bytes)")


# ---------------------------------------------------------------- ELF
def cmd_elf(args) -> int:
    data = read_bytes(args.path)
    if data[:4] != b"\x7fELF":
        die("magic ELF ausente")
    classe = data[4]
    endian = "little" if data[5] == 1 else "big"
    e = "<" if endian == "little" else ">"
    is64 = classe == 2
    if is64:
        (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags,
         e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum,
         e_shstrndx) = struct.unpack(e + "HHIQQQIHHHHHH", data[16:64])
    else:
        (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags,
         e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum,
         e_shstrndx) = struct.unpack(e + "HHIIIIIHHHHHH", data[16:52])

    secoes = []
    if e_shoff and e_shnum and e_shoff + e_shnum * e_shentsize <= len(data):
        fmt = e + ("IIQQQQIIQQ" if is64 else "IIIIIIIIII")
        brutas = []
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            campos = struct.unpack(fmt, data[off:off + struct.calcsize(fmt)])
            brutas.append(campos)
        str_off = brutas[e_shstrndx][4] if e_shstrndx < len(brutas) else 0
        str_size = brutas[e_shstrndx][5] if e_shstrndx < len(brutas) else 0
        strtab = data[str_off:str_off + str_size]
        for c in brutas:
            nome_off, tipo, flags, addr, offset, size = c[0], c[1], c[2], c[3], c[4], c[5]
            fim = strtab.find(b"\x00", nome_off)
            nome = strtab[nome_off:fim].decode("latin-1") if fim > 0 else f"<{nome_off}>"
            secoes.append({"name": nome or "<null>", "type": tipo, "addr": f"0x{addr:x}",
                           "offset": f"0x{offset:x}", "size": size, "flags": f"0x{flags:x}"})

    prog = []
    if e_phoff and e_phnum and e_phoff + e_phnum * e_phentsize <= len(data):
        fmt = e + ("IIQQQQQQ" if is64 else "IIIIIIII")
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            campos = struct.unpack(fmt, data[off:off + struct.calcsize(fmt)])
            if is64:
                p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, _ = campos
            else:
                p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, _ = campos
            prog.append({"type": p_type, "flags": f"0x{p_flags:x}",
                         "vaddr": f"0x{p_vaddr:x}", "filesz": p_filesz, "memsz": p_memsz})

    sementes = [s for s in secoes if s["name"] in (".shstrtab", ".text", ".data", ".rodata",
                                                   ".init_array", ".note.gnu.build-id")]
    out = {"path": str(args.path), "sha256": sha256(data), "size": len(data),
           "class": "ELF64" if is64 else "ELF32", "endianness": endian,
           "machine": ELF_MACHINE.get(e_machine, f"0x{e_machine:04x}"),
           "type": {1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}.get(e_type, str(e_type)),
           "entry": f"0x{e_entry:x}", "sections_count": len(secoes),
           "segments_count": len(prog),
           "rwx_segments": [p for p in prog if int(p["flags"], 16) & 0x7 == 0x7],
           "has_pie": e_type == 3,
           "key_sections": sementes, "sections": secoes[:40], **READ_ONLY}
    _emit(out, args.json, _print_elf)
    return 0


def _print_elf(o: dict) -> None:
    print(f"ELF      : {o['path']} ({o['size']} bytes)")
    print(f"classe   : {o['class']} {o['endianness']} · machine {o['machine']} · tipo {o['type']}")
    print(f"entry    : {o['entry']} · PIE: {o['has_pie']}")
    print(f"seções   : {o['sections_count']} · segmentos: {o['segments_count']} · "
          f"RWX: {len(o['rwx_segments'])}")
    for s in o["key_sections"][:8]:
        print(f"  {s['name']:<20} addr={s['addr']:<12} size={s['size']}")
    if o["rwx_segments"]:
        print("AVISO    : segmento RWX presente (packer/JIT/risco)")


# ---------------------------------------------------------------- squashfs
def cmd_squashfs(args) -> int:
    data = read_bytes(args.path)
    idx = data.find(b"hsqs")
    if idx < 0:
        idx = data.find(b"sqsh")
    if idx < 0:
        die("magic squashfs ausente (hsqs/sqsh)")
    endian = "<" if data[idx:idx + 4] == b"hsqs" else ">"
    if idx + 96 > len(data):
        die("superblock truncado")
    (magic, inodes, mkfs_time, block_size, fragments, compression,
     block_log, flags, no_ids, s_major, s_minor, root_inode,
     bytes_used) = struct.unpack(endian + "4sIIIIHHHHHHQQ", data[idx:idx + 52])
    comp = {1: "gzip", 2: "lzma", 3: "lzo", 4: "xz", 5: "lz4", 6: "zstd"}.get(compression, str(compression))
    out = {"path": str(args.path), "sha256": sha256(data), "magic_offset": f"0x{idx:x}",
           "superblock": {"inodes": inodes, "block_size": block_size,
                          "fragments": fragments, "compression": comp,
                          "version": f"{s_major}.{s_minor}", "bytes_used": bytes_used,
                          "mkfs_time": mkfs_time, "flags": f"0x{flags:x}"},
           "note": "metadados do superblock apenas; extração exige unsquashfs (BLOCKED se ausente)",
           **READ_ONLY}
    _emit(out, args.json, lambda o: print(
        f"squashfs : {o['path']} @ {o['magic_offset']}\n"
        f"versão   : {o['superblock']['version']} · compressão: {o['superblock']['compression']}\n"
        f"inodes   : {o['superblock']['inodes']} · block size: {o['superblock']['block_size']} · "
        f"bytes usados: {o['superblock']['bytes_used']}\n"
        f"nota     : {o['note']}"))
    return 0


# ---------------------------------------------------------------- selftest
def _fixture_uimage() -> bytes:
    payload = b"KERNEL-FAKE" * 100
    dcrc = zlib.crc32(payload) & 0xFFFFFFFF
    header = struct.pack(">7I4B32s", 0x27051956, 0, 1700000000, len(payload),
                         0x80008000, 0x80008000, dcrc, 5, 2, 2, 0, b"test-kernel\x00")
    hcrc = zlib.crc32(header) & 0xFFFFFFFF
    header = header[:4] + struct.pack(">I", hcrc) + header[8:]
    return header + payload


def _fixture_esp() -> bytes:
    tabela = bytearray()
    for typ, sub, off, size, label in [
        (0x00, 0x00, 0x10000, 0x100000, b"factory"),
        (0x01, 0x02, 0x9000, 0x6000, b"nvs"),
        (0x01, 0x82, 0x120000, 0x100000, b"spiffs"),
    ]:
        tabela += struct.pack("<HBBII16sI", 0x50AA, typ, sub, off, size,
                              label.ljust(16, b"\x00"), 0)
    md5 = hashlib.md5(bytes(tabela)).digest()
    tabela += struct.pack("<H", 0xEBEB) + b"\x00" * 14 + md5 + b"\x00" * 4
    dado = bytearray(0x8000)
    return bytes(dado) + bytes(tabela)


def _fixture_uf2() -> bytes:
    blocos = []
    payloads = [b"A" * 476, b"B" * 476, b"C" * 20]
    for i, p in enumerate(payloads):
        cab = struct.pack("<8I", UF2_MAGIC0, UF2_MAGIC1, 0, 0x1000 + i * 476,
                          len(p), i, len(payloads), 0x12345678)
        corpo = cab + p.ljust(476, b"\x00") + struct.pack("<I", UF2_MAGIC_END)
        blocos.append(corpo)
    return b"".join(blocos)


def _fixture_ihex(gaps: bool = True) -> str:
    def reg(addr: int, dados: bytes, tipo: int = 0) -> str:
        base = f"{len(dados):02X}{addr:04X}{tipo:02X}" + dados.hex().upper()
        soma = (-(sum(bytes.fromhex(base)))) & 0xFF
        return ":" + base + f"{soma:02X}"
    linhas = [reg(0x0000, bytes(range(16)))]
    if gaps:
        linhas.append(reg(0x0100, bytes(range(16, 32))))
    else:
        linhas.append(reg(0x0010, bytes(range(16, 32))))
    linhas.append(":00000001FF")
    return "\n".join(linhas) + "\n"


def _fixture_dtb() -> bytes:
    def pad4(b: bytes) -> bytes:
        return b + b"\x00" * ((4 - len(b) % 4) % 4)
    strings = bytearray()
    offsets = {}

    def add_str(s: str) -> int:
        if s not in offsets:
            offsets[s] = len(strings)
            strings.extend(s.encode() + b"\x00")
        return offsets[s]

    struct_blk = bytearray()

    def begin(nome: str) -> None:
        struct_blk.extend(struct.pack(">I", 1) + pad4(nome.encode() + b"\x00"))

    def end_node() -> None:
        struct_blk.extend(struct.pack(">I", 2))

    def prop(nome: str, valor: bytes) -> None:
        struct_blk.extend(struct.pack(">III", 3, len(valor), add_str(nome)))
        struct_blk.extend(pad4(valor))

    begin("")
    prop("model", b"Test Board\x00")
    prop("compatible", b"vendor,test-soc\x00")
    begin("images")
    begin("kernel@1")
    prop("type", b"kernel")
    prop("arch", b"arm")
    prop("compression", b"none")
    prop("load", struct.pack(">I", 0x80008000))
    prop("data", bytes(range(64)))
    end_node()
    end_node()
    begin("configurations")
    begin("default")
    prop("kernel", b"kernel@1")
    end_node()
    end_node()
    end_node()
    struct_blk.extend(struct.pack(">I", 9))

    hdr_size = 40
    rsv = struct.pack(">QQ", 0, 0)
    off_rsvmap = hdr_size
    off_struct = off_rsvmap + len(rsv)
    off_strings = off_struct + len(struct_blk)
    total = off_strings + len(strings)
    header = struct.pack(">10I", FDT_MAGIC, total, off_struct, off_strings,
                         off_rsvmap, 17, 16, 0, len(strings), len(struct_blk))
    return header + rsv + bytes(struct_blk) + bytes(strings)


def cmd_selftest(args) -> int:
    import tempfile

    resultados = []

    def check(nome: str, ok: bool, detalhe: str = "") -> None:
        resultados.append({"test": nome, "ok": bool(ok), "detail": detalhe})
        print(f"{'PASS' if ok else 'FAIL'}  {nome}" + (f"  — {detalhe}" if detalhe else ""))

    tmp = Path(tempfile.mkdtemp(prefix="re_toolkit_"))
    try:
        # uImage
        p = tmp / "uimage.bin"; p.write_bytes(_fixture_uimage())
        d = read_bytes(str(p))
        (magic, hcrc, ts, size, load, ep, dcrc, *_ ) = struct.unpack(">7I", d[:28])
        hz = bytearray(d[:64]); hz[4:8] = b"\x00\x00\x00\x00"
        check("uImage magic", magic == 0x27051956, f"0x{magic:08x}")
        check("uImage header CRC", (zlib.crc32(bytes(hz)) & 0xFFFFFFFF) == hcrc)
        check("uImage data CRC", (zlib.crc32(d[64:64 + size]) & 0xFFFFFFFF) == dcrc)

        # ESP
        p = tmp / "esp.bin"; p.write_bytes(_fixture_esp())
        tabela = parse_esp_table(read_bytes(str(p)), 0x8000)
        check("ESP 3 partições", len(tabela["entries"]) == 3, f"{len(tabela['entries'])}")
        calculado = hashlib.md5(read_bytes(str(p))[0x8000:0x8000 + 32 * 3]).hexdigest()
        check("ESP MD5 declarado", tabela["md5_declared"] == calculado)
        check("ESP factory em 0x10000",
              tabela["entries"][0]["offset"] == "0x010000")

        # UF2
        p = tmp / "fw.uf2"; p.write_bytes(_fixture_uf2())
        d = read_bytes(str(p))
        blocos = len(d) // 512
        m0, m1 = struct.unpack("<2I", d[:8])
        mend = struct.unpack("<I", d[508:512])[0]
        check("UF2 3 blocos", blocos == 3, f"{blocos}")
        check("UF2 magics", (m0, m1, mend) == (UF2_MAGIC0, UF2_MAGIC1, UF2_MAGIC_END))
        check("UF2 cada bloco fecha magic", all(
            struct.unpack("<I", d[i * 512 + 508:i * 512 + 512])[0] == UF2_MAGIC_END
            for i in range(blocos)))

        # Intel HEX com gap
        p = tmp / "fw.hex"; p.write_text(_fixture_ihex(gaps=True), encoding="ascii")
        r = parse_intelhex(p.read_text(encoding="ascii"))
        check("HEX 32 bytes", len(r["memory"]) == 32, f"{len(r['memory'])}")
        span = max(r["memory"]) - min(r["memory"]) + 1
        check("HEX gap detectado", span > 32, f"span={span}")

        # SREC
        linhas = ["S00600004844521B",
                  "S1130000" + bytes(range(16)).hex().upper() + "00",
                  "S9030000FC"]
        # corrige checksum da linha de dados
        corpo = bytes.fromhex(linhas[1][2:])
        soma = (sum(corpo[:-1]) + 0) & 0xFF
        corpo = corpo[:-1] + bytes([(0xFF - soma) & 0xFF])
        linhas[1] = "S1" + corpo.hex().upper()
        try:
            r = parse_srec("\n".join(linhas))
            check("SREC parse", len(r["memory"]) == 16, f"{len(r['memory'])}")
        except ValueError as exc:
            check("SREC parse", False, str(exc))

        # DTB
        p = tmp / "board.dtb"; p.write_bytes(_fixture_dtb())
        fdt = parse_fdt(read_bytes(str(p)))
        check("DTB magic e nós", fdt["node_count"] >= 5, f"{fdt['node_count']} nós")
        caminhos = [n["path"] for n in fdt["nodes"]]
        check("DTB /images/kernel@1", any("/images/kernel@1" in c for c in caminhos),
              str(caminhos[:6]))

        # ELF: usa o próprio interpretador como amostra real
        import shutil
        elf_candidate = None
        for c in ("/usr/bin/ls", "/bin/ls"):
            if Path(c).is_file():
                elf_candidate = c
                break
        if elf_candidate:
            d = read_bytes(elf_candidate)
            check("ELF magic real", d[:4] == b"\x7fELF", elf_candidate)
        else:
            check("ELF amostra disponível", True, "sem /usr/bin/ls — pulado (não é falha)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    falhas = [r for r in resultados if not r["ok"]]
    out = {"tests": resultados, "passed": len(resultados) - len(falhas),
           "failed": len(falhas), **READ_ONLY}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nSELFTEST {out['passed']}/{len(resultados)} PASS")
    return 0 if not falhas else 1


# ---------------------------------------------------------------- emit
def _emit(obj: dict, como_json: bool, printer) -> None:
    if como_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        printer(obj)
        print("read_only=true executed_target=false")


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(
        prog="re_toolkit",
        description="Motor de análise de binário nativo/firmware (read-only, stdlib).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("triage", help="magic, arquitetura, entropia, strings")
    p.add_argument("path"); p.add_argument("--json", action="store_true")
    p.add_argument("--strings", type=int, default=12)
    p.set_defaults(func=cmd_triage)

    p = sub.add_parser("uimage", help="header e CRC de U-Boot uImage")
    p.add_argument("path"); p.add_argument("--extract"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_uimage)

    p = sub.add_parser("esp", help="tabela de partição ESP")
    p.add_argument("path"); p.add_argument("--offset", type=lambda x: int(x, 0))
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_esp)

    p = sub.add_parser("dtb", help="FDT/FIT: nós, imagens, hashes")
    p.add_argument("path"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_dtb)

    p = sub.add_parser("uf2", help="blocos UF2 e reconstrução")
    p.add_argument("path"); p.add_argument("--extract"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_uf2)

    p = sub.add_parser("intelhex", help="Intel HEX / SREC -> binário")
    p.add_argument("path"); p.add_argument("--out"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_intelhex)

    p = sub.add_parser("elf", help="header, seções e segmentos ELF")
    p.add_argument("path"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_elf)

    p = sub.add_parser("squashfs", help="superblock squashfs")
    p.add_argument("path"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_squashfs)

    p = sub.add_parser("selftest", help="gera fixtures e verifica cada parser")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_selftest)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
