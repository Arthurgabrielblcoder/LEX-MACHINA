# Mapa do repositório para o dispositivo (DEVICE INTEGRATION V1-A1)

Levantamento somente leitura feito em 2026-09-29 sobre o HEAD `2e2211c0`. Nada foi alterado.

## Componentes

| COMPONENT | PATH | PURPOSE | STATUS | SOURCE_OF_TRUTH | USED_BY_DEVICE? | SAFE_TO_MODIFY? |
|---|---|---|---|---|---|---|
| Firmware v7.12.0 JURIS CF EXPANDIDA | `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/` | sketch validado fisicamente (21/09/2026) | CONGELADO; sha256 do `.ino`, `contexto_juridico.h` e `lex_boot_screen.h` conferem com `HISTORICO_RELEASES.md` | sim, do firmware físico provável | provavelmente sim (ver candidatos) | NÃO (baseline física; desenvolvimento em pasta nova) |
| Firmware v7.9.4 (`LEX_MACHINA.ino`) | `firmware/LEX_MACHINA.ino/` | sketch antigo (banner serial "V7.9.1") | histórico | não | não | NÃO |
| Firmware v7.10.1 RELATIONS V2 FAST | `firmware/LEX MAQUINA INO 2/…_FAST/` e `.zip` (não rastreado) | snapshot anterior | histórico | não | não | NÃO |
| Snapshots de firmware fora do repo | `C:/LMA/p545e/20260928/firmware/` (v7.11.0, v7.11.1, backup pós-Codex 16/09) | preservação | somente leitura | não | não | NÃO (área protegida) |
| Parser de contexto | `firmware/…v7.12.0…/contexto_juridico.h` | texto visível → (artigo, parágrafo, inciso, alínea) | validado no aparelho | sim (runtime) | sim | NÃO |
| Lei Seca CF (fonte estrutural) | `updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt` | texto consolidado com ADCT e redações históricas; base do índice estrutural aprovado | sha256 `d9f3d6b9…`, 928.009 bytes, UTF-8, CRLF | sim, para target_id (índice aprovado) | provavelmente é o `cf.txt` do cartão (o firmware trata `cf.txt` como caso especial), **não confirmado** | NÃO |
| Lei Seca CF (texto operacional) | `updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt` | texto vigente usado pelo ENTENDA para frescor | sha256 `3100e097…`, 429.832 bytes, LF, sem ADCT; `updater/saida` é ignorado pelo Git | sim, para vigência/frescor | desconhecido | NÃO |
| Árvore de saída do updater | `updater/saida/` (935 arquivos, 64,99 MB, ignorada) | acervo gerado pelo pipeline `updater/main.py` | contém pastas duplicadas com nomes escapados (`#U00c7`) | parcial (Lei Seca por norma) | desconhecido | NÃO nesta fase |
| Gerador/implantador de SD legado | `updater/implantar_sd.py` (+ `test_implantar_sd.py`) | cópia controlada de índices CDC/correlatas para o cartão, com backup no PC | legado; não formata nem remove | não para o novo overlay | indiretamente (montou o cartão antigo) | NÃO |
| Backup parcial do cartão | `updater/backup_sd/microSD_20260916_223312_378647/` (736 KB, não rastreado) | cópia de subárvore CDC/jurisprudência feita pelo implantador | parcial; não é backup completo | não | não | NÃO |
| Relations V2 (correlatas) | `LEX-MACHINAETAPA_2E5/…/PACOTE_INDICES_ESP32_2E5/99_RELATIONS_V2/` e `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/SD_PRONTO/` | `REL_LOOKUP.IDX`, `RELACOES.IDX`, `EXT_NORMAS.IDX`, `EXT_ARTIGOS.IDX` | legado validado (lidos pelo v7.12.0) | sim para o cartão legado | sim (`/99_RELATIONS_V2/05_INDICES_ESP32_V2/`) | NÃO |
| Jurisprudência J4 | `C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/` | `JUR_LOOKUP.IDX` (178 chaves), `JURISPRUDENCIA.IDX`, 221 TXT | sha do `JUR_LOOKUP.IDX` igual ao J4 (`7931e28e…`); corresponde ao "corpus físico J4" do HISTORICO | sim para o cartão legado | sim (`/99_JURISPRUDENCIA_V2/`) | NÃO (área protegida) |
| Índice estrutural de targets | `LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json` (+ `CF88_TARGET_STATUS.json`) | 3.956 targets canônicos com `line_start` no `cf.txt` estrutural | aprovado (Reference Engine final) | sim | não (derivado para o overlay) | NÃO |
| Reference Engine | `LEGAL_TARGET_ID/reference_engine.py`, `derived/export_test/run1/REF_LOOKUP.IDX`, `REF_PAYLOAD.IDX` | par ESP32 target_id → referências | aprovado (tag `cf-reference-engine-final-2026-09-28`) | sim | ainda não | NÃO (só empacotado byte a byte) |
| ENTENDA Engine | `ENTENDA_ENGINE/` (`entenda_engine.py`, `production_batch.py`, `derived/production_batch_0{1,2,3}_final/`) | explicações aprovadas e par `ENTENDA_LOOKUP.IDX`/`ENTENDA_PAYLOAD.DAT` | aprovado (154 explicações HUMAN_APPROVED_T1) | sim | ainda não | NÃO (só unificado para o overlay) |
| Piloto ENTENDA fora do escopo | `ENTENDA_ENGINE/corpus/CF88.entenda.jsonl` | 11 explicações aprovadas no piloto; 2 (arts. 1 e 5) entram via Batch 01; 9 (arts. 37, 60, 150, 225 e ADCT 10, II) ficam fora | aprovado, fora do escopo arts. 1–24 | sim | não (excluídas do pacote) | NÃO |
| Firmware candidato V1 | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/` | cópia da v7.12.0 com `lex_device_v1.h` atrás de `LEX_DEVICE_V1_ENABLED` | candidato (A2), compilado e não gravado | não | não | sim (candidato) |
| Staging novo | `DEVICE_INTEGRATION/staging_sd_v1/` (ignorado pelo Git) | SD_OVERLAY_CANDIDATE `/99_LEX_V1` | gerado nesta fase | derivado | não (nada foi copiado para cartão) | sim (derivado, reconstruível) |

## Candidatos de firmware

| Candidato | Valor | Confiança | Evidência |
|---|---|---|---|
| `CURRENT_PHYSICAL_FIRMWARE_CANDIDATE` | v7.12.0 JURIS CF EXPANDIDA (`firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/`) | **HIGH — `PHYSICAL_FIRMWARE_CONFIRMED_V7_12_0` (A2: banner serial + string na flash + dump verificado)**; na A1 era MEDIUM | `HISTORICO_RELEASES.md` registra aprovação física em 21/09/2026 com J4 (178 chaves/296 bindings); hashes conferem; commit `d4e816f` antecede a limpeza (`f251cea`), o Reference Engine e o ENTENDA, o que bate com "versão antiga". Não há dump da flash nem conexão serial para confirmar o banner `LEX MACHINA V7.12.0 JURIS CF EXPANDIDA`. |
| `CURRENT_REPO_FIRMWARE_CANDIDATE` (base da integração nova) | v7.12.0 (a ser copiada para pasta nova, ex.: `firmware/LEX_MACHINA_v8.0.0_DEVICE_V1/`) | **HIGH** | é o sketch mais recente do Git, validado no aparelho, e já contém o parser de contexto e os caches PSRAM que o contrato V1 reaproveita. |

## Observações do firmware legado (sem alterar)

- O cache de Relations V2 tem teto `MAX_LOOKUP_V2_CACHE 64` e para de ler `REL_LOOKUP.IDX` ao atingir 64 linhas (sem aviso). Com mais de 64 chaves, entradas seriam ignoradas.
- O lookup jurídico (J4) em PSRAM é linear sobre 178 entradas. É aceitável nesse tamanho, mas não escala.
- Os índices legados usam a tupla `NORMA|ARTIGO|PARAGRAFO|INCISO|ALINEA`, não o `target_id` canônico.
