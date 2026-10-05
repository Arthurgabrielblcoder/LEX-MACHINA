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

## Atualização (recalibração do Batch06, 2026-10-05): texto da CF reconstruído do Git

O texto operacional da CF (`updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt`, ignorado pelo Git) passou a ser **reconstruível byte a byte** a partir de conteúdo versionado:

- receita: `ENTENDA_ENGINE/editorial/TEXT_SOURCE_RECONSTRUCTION.json` = cabeçalho do updater (`criar_cabecalho_mestre`, data fixa `14/09/2026 17:07`) + corpo travado do Senado (`updater/fontes_oficiais_senado/CF88/16434817_5beff7a4/normalizado.txt`, sha256 `d2f681e0…`) + `\n`;
- resultado conferido: sha256 `3100e097…` (o mesmo `text_source_file_sha256` de todos os registros ENTENDA; os 682 snapshots carimbados coincidem);
- `entenda_engine.read_source_bytes` lê o arquivo local quando existe; na ausência (clone limpo, Cloud) usa a reconstrução, com falha fechada se o hash divergir. Nenhuma palavra da lei é editada;
- `.gitattributes`: `updater/fontes_oficiais_senado/** -text` (os blobs já eram LF; nenhum blob mudou), para que a reconstrução funcione também com `core.autocrlf=true`.

Com isso as suítes ENTENDA rodam num clone puro. Seguem dependências locais: `CF_SEGMENTADA_V2/` e a materialização CRLF do `cf.txt` legado (LEGAL_TARGET_ID, 2 testes), o staging do SD, a tag local `lex-device-v1-physical-approved-2026-10-01` e a cópia de verificação da EC 45 (DEVICE_INTEGRATION), e as pastas do Relations Engine (o Batch06 usa `BATCH06_RELATIONS_PIN.json`).

Builder do Batch06: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` (Python ≥ 3.12).
