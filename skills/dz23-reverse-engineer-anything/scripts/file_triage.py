#!/usr/bin/env python3
"""Triagem read-only de arquivo/binário: magic, arquitetura, entropia, assinaturas.

Não executa o alvo, não descompacta, não acessa rede. Só lê bytes.

Uso:
    python scripts/file_triage.py <arquivo> [--json] [--strings N]

Exit 0 = relatório gerado
Exit 2 = input inválido
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

MAX_BYTES = 512 * 1024 * 1024
BLOCK = 4096
MAX_BLOCKS = 64  # amostra: primeiros 256 KiB

# (assinatura, offset fixo ou None para busca, nome)
MAGICS: list[tuple[bytes, int | None, str]] = [
    (b"\x7fELF", 0, "ELF"),
    (b"MZ", 0, "PE (DOS header)"),
    (b"PK\x03\x04", 0, "ZIP (container/APK/JAR)"),
    (b"\xcf\xfa\xed\xfe", 0, "Mach-O 64 LE"),
    (b"\xce\xfa\xed\xfe", 0, "Mach-O 32 LE"),
    (b"\xca\xfe\xba\xbe", 0, "Mach-O fat / Java class"),
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

ARCH_ELF = {
    0x03: "x86", 0x3E: "x86-64", 0x28: "ARM", 0xB7: "AArch64",
    0x08: "MIPS", 0x14: "PowerPC", 0x15: "PowerPC64", 0xF3: "RISC-V",
    0x02: "SPARC", 0x2B: "SPARCv9",
}


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}", file=sys.stderr)
    raise SystemExit(2)


def shannon(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def find_all(data: bytes, sig: bytes, limit: int = 5) -> list[int]:
    out: list[int] = []
    start = 0
    while len(out) < limit:
        idx = data.find(sig, start)
        if idx < 0:
            break
        out.append(idx)
        start = idx + 1
    return out


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Triagem read-only de binário/firmware.")
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strings", type=int, default=15, help="quantas strings listar (0 = nenhuma)")
    args = ap.parse_args(argv)

    path = Path(args.path)
    if not path.is_file():
        fail(f"arquivo não encontrado: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        fail(f"arquivo grande demais para triagem ({size} bytes)")

    with path.open("rb") as fh:
        data = fh.read()

    head = data[:64]
    detected: list[dict] = []
    for sig, off, name in MAGICS:
        if off is None:
            hits = find_all(data, sig, limit=3)
            if hits:
                detected.append({"name": name, "offset": hits[0], "hits": hits})
        else:
            chunk = data[off:off + len(sig)]
            if chunk == sig:
                detected.append({"name": name, "offset": off, "hits": [off]})

    elf_arch = None
    elf_endian = None
    if data[:4] == b"\x7fELF" and len(data) > 20:
        elf_endian = "little" if data[5] == 1 else "big" if data[5] == 2 else "?"
        machine = int.from_bytes(data[18:20], "little" if data[5] == 1 else "big")
        elf_arch = ARCH_ELF.get(machine, f"machine 0x{machine:04x}")

    entropy = []
    for i, off in enumerate(range(0, min(len(data), BLOCK * MAX_BLOCKS), BLOCK)):
        block = data[off:off + BLOCK]
        if not block:
            break
        entropy.append({"offset": off, "entropy": round(shannon(block), 3)})

    ascii_runs: list[str] = []
    if args.strings > 0:
        cur = bytearray()
        for byte in data[: min(len(data), 2 * 1024 * 1024)]:
            if 0x20 <= byte < 0x7F:
                cur.append(byte)
            else:
                if len(cur) >= 8:
                    ascii_runs.append(cur.decode("ascii"))
                cur.clear()
        if len(cur) >= 8:
            ascii_runs.append(cur.decode("ascii"))
        ascii_runs = ascii_runs[: args.strings]

    avg = round(sum(e["entropy"] for e in entropy) / len(entropy), 3) if entropy else 0.0
    high = [e for e in entropy if e["entropy"] > 7.5]
    payload = {
        "path": str(path),
        "size": size,
        "sha256": __import__("hashlib").sha256(data).hexdigest(),
        "first_bytes": head.hex(" "),
        "detected": detected,
        "elf": {"arch": elf_arch, "endianness": elf_endian} if elf_arch or elf_endian else None,
        "entropy_avg": avg,
        "entropy_high_blocks": len(high),
        "entropy_blocks": len(entropy),
        "strings_sample": ascii_runs,
        "read_only": True,
        "executed_target": False,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"arquivo   : {path}")
    print(f"tamanho   : {size} bytes")
    print(f"sha256    : {payload['sha256']}")
    print(f"primeiros : {payload['first_bytes'][:47]}")
    print("formato   :")
    if detected:
        for item in detected:
            print(f"  - {item['name']} @ 0x{item['offset']:x}")
    else:
        print("  - nenhuma assinatura conhecida (possível cifra, compressão crua ou região de flash)")
    if elf_arch:
        print(f"elf       : arch={elf_arch} endianness={elf_endian}")
    print(f"entropia  : média {avg} bits/byte em {len(entropy)} blocos de {BLOCK} B "
          f"({len(high)} acima de 7.5)")
    if args.strings > 0 and ascii_runs:
        print("strings   :")
        for s in ascii_runs[:8]:
            print(f"  {s[:70]}")
    print("read_only=true executed_target=false")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
