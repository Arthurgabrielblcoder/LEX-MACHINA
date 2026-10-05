# ENTENDA — reprodutibilidade a partir do Git (hardening pós-Batch05, 2026-10-04)

## Quais bytes importam

| Artefato | Como é consumido | Byte-sensível? | Regra (`.gitattributes`) |
|---|---|---|---|
| `ENTENDA_PAYLOAD.DAT` | lido em binário por OFFSET/BYTES do `LOOKUP.IDX` (motor `lookup_idx` e firmware); sha256 no manifesto | **sim** — CRLF desloca todos os offsets | `ENTENDA_ENGINE/derived/**/ENTENDA_PAYLOAD.DAT -text` |
| `ENTENDA_LOOKUP.IDX` | offsets/bytes + sha256 no manifesto | **sim** | `*.IDX -text` (já existia) e `ENTENDA_ENGINE/derived/**/*.IDX -text` (reafirmação após a regra de `derived/**`) |
| Gerados em `ENTENDA_ENGINE/derived/**` (`.jsonl`, `.json`, `.md`) | o motor lê como texto, mas os testes comparam builds novos byte a byte com os versionados; as decisões das rodadas gravam sha256 das cópias de evidência; os manifestos gravam sha256 | **sim** (pelos hashes) | `ENTENDA_ENGINE/derived/** text eol=lf` |
| `DEVICE_INTEGRATION/runtime/**` (Lei Seca) | sha256 do runtime fixado (`7ef82290…`) no plano do lote e na proveniência | **sim** | `DEVICE_INTEGRATION/runtime/** text eol=lf` |
| `LEGAL_TARGET_ID/derived/**` (export RUN3, índices) | exports determinísticos comparados byte a byte e por sha256 | **sim** | `LEGAL_TARGET_ID/derived/** text eol=lf` |
| `ENTENDA_ENGINE/corpus/*.jsonl` (corpus aprovado principal) | lido por linhas (`splitlines`); conferido só via `git diff` (comparação lógica) | **não** — a normalização é segura | nenhuma regra (decisão documentada) |

Os arquivos são gerados em LF (`write_bytes`). O índice do Git já os guarda em LF, então as regras não mudaram nenhum blob: só garantem que o checkout devolva os mesmos bytes, mesmo com `core.autocrlf=true`.

## Evidência (esta máquina, `core.autocrlf=true`)

| Materialização | Arquivos críticos idênticos | Blocos de payload legíveis | ENTENDA (falhas) | LEGAL_TARGET_ID (falhas) |
|---|---|---|---|---|
| commit `342ab9a` (regras antigas) | 15/184 | 0/720 | 30 | 5 |
| índice com as regras novas | 184/184 | 720/720 | 0 | 0 |

**Testes que exigem estar dentro do repositório Git:** os testes de imutabilidade que chamam `git diff HEAD` / `git rev-parse HEAD` (`test_approved_batches_immutable` ×2, `test_approved_content_immutable`, `test_protected_registry_untouched`) não rodam numa árvore materializada fora do repositório. A ferramenta os lista à parte, sem escondê-los. Num clone real eles rodam normalmente.

## Como verificar

```
python ENTENDA_ENGINE/git_materialization_check.py --source HEAD               # bytes/offsets/hashes do commit
python ENTENDA_ENGINE/git_materialization_check.py --source INDEX --run-tests   # + suítes ENTENDA e LEGAL_TARGET_ID na árvore materializada
```

`tests/test_git_materialization.py` roda a verificação de bytes, offsets e hashes em toda execução da suíte ENTENDA.

## Dependências externas não versionadas (pré-existentes)

- **Texto-fonte da CF** (`updater/saida/1- CONSTITUIÇÃO FEDERAL/...`), **fonte estrutural do ADCT** (`updater/backup_catalogos/...`) e **`CF_SEGMENTADA_V2/`**: um clone puro não roda as suítes ENTENDA/LEGAL completas sem esses dados locais. A verificação os copia do worktree principal só para `--run-tests`.
- **Pastas de trabalho do Relations Engine** (`LEX-MACHINAETAPA_2D4/2E41`): usadas só pelo teste opcional de integração com a relação real da Lei 12.813/2013. A lógica do resolvedor é provada de forma hermética em `tests/test_t1_external_resolver.py`, com `tests/fixtures/t1_relations_fixture.json`.
