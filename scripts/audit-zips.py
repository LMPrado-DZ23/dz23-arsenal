#!/usr/bin/env python3
"""audit-zips.py — compara as skills deste repo com as instaladas em ~/.agents/skills.

Uso:
    python scripts/audit-zips.py            # relatório legível
    python scripts/audit-zips.py --json     # JSON para automação
    python scripts/audit-zips.py --strict   # exit 1 também quando a skill não está instalada

Exit:
    0 = todas as skills instaladas batem com o repo
    1 = há divergência de conteúdo ou versão
    2 = erro de input (pasta skills/ ausente)

Não altera nada. Só lê e compara.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

IGNORAR = re.compile(r"(/__pycache__/|/\.git/|\.bak-|_sources|\.pyc$|/\.DS_Store$)")

# O README da skill no repo recebe a seção "Arsenal" (instalação, quando usar, gates).
# Essa seção não existe na cópia instalada, então o README de raiz fica fora da comparação de
# conteúdo. A versão (VERSION/frontmatter) continua sendo comparada.
IGNORAR_ARQUIVOS = {"README.md"}


def sha(p: Path) -> str:
    """Hash de conteúdo normalizado por fim de linha.

    Comparar bytes crus fazia o auditor reportar CONTEUDO_DIVERGENTE entre repo e instalação
    quando os dois têm o mesmo texto com EOL diferente — acontece em qualquer máquina com
    core.autocrlf=false, onde o git materializa LF enquanto a cópia instalada conserva CRLF
    (o install-all usa Copy-Item, que não converte). O veredito era falso e empurrava a pessoa
    para reinstalar algo que já estava igual.

    Arquivos binários seguem comparados byte a byte: normalizar linha neles corromperia o hash
    de um artefato real (ícone, zip de pacote), que é justamente o que se quer detectar.
    """
    h = hashlib.sha256()
    if _e_parece_texto(p):
        with open(p, "rb") as fh:
            dados = fh.read()
        h.update(dados.replace(b"\r\n", b"\n"))
        return h.hexdigest()
    with open(p, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


EXT_TEXTO = {".md", ".txt", ".json", ".py", ".sh", ".ps1", ".yml", ".yaml", ".toml",
             ".cfg", ".ini", ".csv", ".js", ".mjs", ".ts"}


def _e_parece_texto(p: Path) -> bool:
    """Decide by CONTENT, not by extension.

    A checagem por sufixo deixou `VERSION` de fora -- arquivo sem extensão, portanto "binário",
    hasheado byte a byte. Resultado medido nesta sessão: com o blob em LF e o disco em CRLF
    (`core.autocrlf=false` não converte ao materializar), repo e instalação continham o mesmo texto
    `1.1.3\r\n` vs `1.1.3\n`, e o auditor declarava CONTEUDO_DIVERGENTE apontando exatamente
    VERSION -- um veredito falso que empurraria alguém a reinstalar algo já igual. Era o quarto
    membro da classe das rodadas 47/48, escondido justamente no arquivo que guarda a versão.

    Arquivo sem sufixo reconhecido é testado como texto real: se decodifica como UTF-8 e não tem
    byte nulo, é texto e merece normalização de EOL. Binários autênticos (ícone, zip) falham nos
    dois critérios e continuam comparados byte a byte.
    """
    if p.suffix.lower() in EXT_TEXTO:
        return True
    if p.suffix:
        return False          # extensão desconhecida: tratar como binário, comportamento antigo
    try:
        dados = p.read_bytes()
    except OSError:
        return False
    if b"\x00" in dados[:8192]:
        return False
    try:
        dados.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def mapa(root: Path) -> dict[str, str]:
    saida: dict[str, str] = {}
    for p in root.rglob("*"):
        if p.is_file():
            rel = "/" + str(p.relative_to(root)).replace("\\", "/")
            if IGNORAR.search(rel):
                continue
            if rel[1:] in IGNORAR_ARQUIVOS:
                continue
            saida[rel[1:]] = sha(p)
    return saida


def versao(root: Path) -> str:
    v = root / "VERSION"
    if v.is_file():
        return v.read_text(encoding="utf-8", errors="replace").strip()
    # fallback: frontmatter do SKILL.md
    s = root / "SKILL.md"
    if s.is_file():
        for linha in s.read_text(encoding="utf-8", errors="replace").splitlines()[:12]:
            if linha.lower().startswith("version:"):
                return linha.split(":", 1)[1].strip().strip('"\'')
    return "?"


def auditar(repo: Path, dest: Path) -> list[dict]:
    skills_repo = repo / "skills"
    itens = []
    for pasta in sorted(p for p in skills_repo.iterdir() if p.is_dir()):
        nome = pasta.name
        alvo = dest / nome
        item = {"skill": nome, "versao_repo": versao(pasta)}

        if not alvo.is_dir():
            item["status"] = "NAO_INSTALADA"
            item["versao_instalada"] = "—"
            item["arquivos_repo"] = len(mapa(pasta))
            itens.append(item)
            continue

        item["versao_instalada"] = versao(alvo)
        a = mapa(pasta)
        b = mapa(alvo)
        faltando = sorted(set(b) - set(a))    # existe no instalado, não no repo
        sobrando = sorted(set(a) - set(b))    # existe no repo, não no instalado
        divergentes = sorted(k for k in set(a) & set(b) if a[k] != b[k])

        item.update({
            "arquivos_repo": len(a),
            "arquivos_instalado": len(b),
            "faltando_no_repo": faltando,
            "sobrando_no_repo": sobrando,
            "divergentes": divergentes,
        })

        if faltando or sobrando or divergentes:
            item["status"] = "CONTEUDO_DIVERGENTE"
        elif item["versao_repo"] != item["versao_instalada"]:
            item["status"] = "VERSAO_DIVERGENTE"
        else:
            item["status"] = "EM_DIA"
        itens.append(item)
    return itens


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--dest", type=Path, default=Path.home() / ".agents" / "skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 também quando a skill não está instalada")
    args = ap.parse_args(argv)

    if not (args.repo / "skills").is_dir():
        print(f"INVALID pasta skills/ ausente em {args.repo}", file=sys.stderr)
        return 2

    itens = auditar(args.repo, args.dest)

    if args.json:
        print(json.dumps({"dest": str(args.dest), "skills": itens}, indent=2, ensure_ascii=False))
    else:
        print(f"# Auditoria skills/ → {args.dest}\n")
        print(f"{'skill':<42}{'repo':<10}{'instalada':<11}status")
        print("-" * 80)
        for it in itens:
            print(f"{it['skill']:<42}{it['versao_repo']:<10}"
                  f"{it['versao_instalada']:<11}{it['status']}")
        problemas = [i for i in itens if i["status"] != "EM_DIA"]
        if problemas:
            print("\n## Detalhe")
            for it in problemas:
                print(f"\n### {it['skill']} — {it['status']}")
                for rotulo, chave in (("faltando no repo", "faltando_no_repo"),
                                      ("sobrando no repo", "sobrando_no_repo"),
                                      ("conteúdo divergente", "divergentes")):
                    lista = it.get(chave) or []
                    if lista:
                        print(f"- {rotulo} ({len(lista)}):")
                        for n in lista[:10]:
                            print(f"  - {n}")
                        if len(lista) > 10:
                            print(f"  - … e mais {len(lista) - 10}")

        total = len(itens)
        ok = sum(1 for i in itens if i["status"] == "EM_DIA")
        print(f"\n{ok}/{total} em dia · {sum(1 for i in itens if i['status'] == 'NAO_INSTALADA')} "
              f"não instaladas · {sum(1 for i in itens if 'DIVERGENTE' in i['status'])} divergentes")

    falhou = any(
        i["status"].endswith("DIVERGENTE") or (args.strict and i["status"] == "NAO_INSTALADA")
        for i in itens
    )
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
