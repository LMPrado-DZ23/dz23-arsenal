# Instalação — dz23-arsenal (layer install/)

Instalador multiplataforma das skills DZ23. Um arquivo Python stdlib puro
(`scripts/dz23-install.py`), **offline por construção** (só copia arquivos do
checkout; nunca abre rede), funciona em **Windows, Linux e macOS**.

## Uso

```bash
# 1. Ver dependências (AVAILABLE / UNAVAILABLE no PATH)
python scripts/dz23-install.py detect

# 2. Simular a instalação (dry-run: não muda nada)
python scripts/dz23-install.py install --dry-run

# 3. Instalar em ~/.agents/skills (sobrescreve só com --force)
python scripts/dz23-install.py install

# 4. Desfazer (rollback preciso: remove só o que o install registrou)
python scripts/dz23-install.py rollback
```

`--dest DIR` instala/reverte em outro diretório (útil para teste). No Windows,
use `python` ou `py -3`; os scripts `install-all.ps1`/`install-all.sh` seguem
disponíveis para o caminho simples.

## Garantias (verificadas no gate: `install:autoteste`)

- **Offline**: nenhuma chamada de rede — apenas cópia de arquivos.
- **Detecção de dependências**: `detect` reporta python/git/node/pwsh; só
  `python` é obrigatório para rodar o instalador.
- **Dry-run inócuo**: `install --dry-run` não cria nenhum arquivo.
- **Manifesto + rollback preciso**: cada install grava
  `~/.agents/skills/.dz23-install-manifest.json` com as skills geridas
  presentes; `rollback` remove **exatamente** essas (mais o ponteiro e o log) e
  nunca toca em skill que não instalou. `rollback` sem manifesto é no-op seguro.
- **Idempotência**: reinstalar sem `--force` pula o que já existe e preserva o
  manifesto.
- **Log sem segredos**: `.dz23-install.log` registra só nomes de skill,
  contagens e horário — nunca token, senha, env ou dado pessoal.
- **Sem bytecode**: `__pycache__`/`*.pyc` não são copiados para o destino.

## Onde ficam as skills

`~/.agents/skills/<nome>/` — descobertas por Claude Code, DeepSeek Harness,
Codex e Cursor (via junction/symlink de `~/.claude/skills` e `~/.codex/skills`).
O ponteiro `~/.agents/skills/.dz23-arsenal` aponta de volta ao checkout, para a
skill instalada achar o arsenal e rodar as checagens comuns.
