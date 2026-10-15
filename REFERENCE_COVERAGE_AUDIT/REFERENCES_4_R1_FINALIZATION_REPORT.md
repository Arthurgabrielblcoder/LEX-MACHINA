# REFERÊNCIAS Nº 4 — CF: R1, finalização das duas aprovações retidas (com R1A)

```
MISSION = R1 (+ R1A, ingestão de identidade autorizada pelo usuário em 2026-10-15) — HOST-ONLY
BRANCH = cf-references4-finalize
BRANCH_BASE = af8f68dace695de6b332c5e8cf7920e5754c6f99 (cf-correlata-coverage-audit; contém C3B.2 e CORRELATAS_1_CF_FROZEN.md)
RESULT = HOST_ONLY_CANDIDATE
SOS_SAUDE_EDITORIAL_APPROVAL = CONFIRMED            PRO_DIA_NASCER_FELIZ_EDITORIAL_APPROVAL = CONFIRMED
WORK_REGISTRY_DUPLICATE_CHECK = PASS                RETAINED_APPROVALS_MATERIALIZED = 2/2
WORK_REFERENCE_RELATIONS 122 -> 124 · WORKS_USED 54 -> 56 · W_TARGETS 63 -> 65
CORRELATA_RELATION_SET_CHANGED = 0 · C_FLAGS_CHANGED = 0 · NON_W_TARGET_FLAGS_CHANGED = 0
FIRMWARE_LOGIC_CHANGED = NO · FIRMWARE_DATA_CHANGED = YES (somente a tabela lex_ref_detail_data.h do candidato)
REFERENCE_FINALIZATION_BUILD_REPRODUCIBLE = YES · MICROSD_TOUCHED = NO · DEVICE_FLASHED = NO
```

## 1. Histórico desta rodada

A primeira execução do R1 (commit `e1e31d4`) parou em `BLOCKED_MISSING_BIBLIOGRAPHIC_METADATA`, porque nenhuma das duas obras tinha identidade com fonte no projeto.

O usuário então autorizou a missão **R1A**, de ingestão de identidade com fontes consultadas no padrão do `CATALOGO_EXPANSAO_200`. Também decidiu o ano de *Pro Dia Nascer Feliz* (2005), já que as fontes divergem. Depois disso, o R1 foi retomado.

## 2. Decisões retidas (inalteradas)

As duas decisões estão em `REFERENCE_EXPANSION_ROUND1_DECISIONS.json` (FINAL, 2026-10-02), ambas `APPROVE` / `HUMAN_APPROVED_REFERENCE_V1` / `APPROVED_PENDING_WORK_IDENTITY`:

- P20: `CF88:ART.196`, score 7,4;
- P21: `CF88:ART.206:INC.I`, score 8,0.

O arquivo de decisões não foi editado. Os textos aprovados (conexão, por que está aqui, alcance, limites, score) foram transportados sem reescrita, o que é verificado por teste.

## 3. R1A: identidade das obras

As fontes estão em `R1A_WORK_IDENTITY/03_FONTES/`. Os registros guardam só metadados de coleta (URL, data, HTTP, `snapshot_sha256`), sem texto de terceiros. Os fatos-chave foram conferidos no texto bruto das páginas.

| Obra | ID | Título no registry | Original | Ano | Criador | Fontes (tier) |
|---|---|---|---|---|---|---|
| SOS Saúde (Sicko) | `R1A-DOC-001` | Sicko - S.O.S. Saúde | Sicko | 2007 | Michael Moore | Festival de Cannes, ficha *Hors Compétition* 2007 (B); AdoroCinema (C) |
| Pro Dia Nascer Feliz | `R1A-DOC-002` | Pro Dia Nascer Feliz | Pro Dia Nascer Feliz | **2005** | João Jardim | Arquivo da Mostra SP, 29ª Mostra, pt/en (B); PLFD Dartmouth (B); UFMG Espaço do Conhecimento (B) |

**Ano de Pro Dia Nascer Feliz.** As fontes divergem:

- Mostra SP: 2005;
- UFMG: 2006;
- Dartmouth: 2007 (lançamento comercial);
- Guia da Semana: 2006, mas a página respondeu HTTP 403 e não foi consultada.

A proposta P21 trazia 2006 sem fonte. Foi adotado **2005**, por decisão do usuário, com a regra "primeira exibição pública documentada". A decisão e as divergências estão registradas em `ano_decisao`.

**Outros pontos registrados:**

- As produtoras de *Pro Dia Nascer Feliz* não foram transcritas, porque a única lista consultada traz grafia divergente.
- A data de estreia de *Sicko* no Brasil não foi confirmada.

**Duplicatas.** A busca normalizada no registry V2 (73 obras), no catálogo de 199 obras e nas 200 candidatas não encontrou nenhuma correspondência (`not_in_registry` / `duplicates_in_registry = []`).

## 4. Registry e overlay

- **`REFERENCE_REGISTRY/WORK_REGISTRY_V3.json` (75 obras).** As 73 do V2 foram copiadas sem alteração, e o V2 continua versionado como base do RUN3. A promoção (`apply_references4_r1.py`) repete os checks de `promote()`: identidade, tipo, ano, ID livre, ausência de duplicata e fonte de identidade consultada. Para o ano, a única exceção documentada é P21.
- **`LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json`.** Contém exatamente P20 e P21. O overlay do RUN3 não foi editado.
- `NEW_EDITORIAL_RELATIONS = 0` além dessas duas.

## 5. RUN5 candidato (motor oficial)

**Builder:** `LEGAL_TARGET_ID/build_export_run5_references4_r1.py`. O build segue estes passos:

1. Parte do `run4_candidate/device_ready`, cujos bytes são iguais ao pacote físico C3B.2.
2. Reconstrói os vínculos do RUN4 e reexporta pelo `reference_engine.export`. O resultado precisa reproduzir o RUN4 **byte a byte**.
3. Adiciona somente os dois vínculos validados pelo motor, com o mesmo gate *fail-closed* do RUN3 e o registry V3.

| Arquivo | Delta vs C3B.2 |
|---|---|
| `REF_PAYLOAD.IDX` | +2 linhas `WORK_REFERENCE` (`R1A-DOC-001@CF88:ART.196`, status STRUCTURAL como em ART.192/ADCT.68; `R1A-DOC-002@CF88:ART.206:INC.I`, CURRENT). Nenhuma outra linha alterada |
| `REF_LOOKUP.IDX` | +2 linhas (os dois targets não tinham nenhuma referência). Nenhuma contagem alterada |
| `CF88_TARGETS.IDX` | Só a posição W: `CF88:ART.196` `E----X → E--W-X`; `CF88:ART.206:INC.I` `------ → ---W--` |
| `RELACOES` / `REL_LOOKUP` / `EXT_ARTIGOS` | Idênticos (cópias de byte) |

**W flag.** Os dois targets **não tinham W**, então o total sobe de 63 para 65. O W foi derivado do conjunto final de `WORK_REFERENCE` visíveis, com a mesma regra do gerador de staging, e o builder verifica que o W do C3B.2 já obedecia essa regra.

**R flag.** R (posição [4]) não é lido pelo firmware e foi mantido como no C3B.2. Os dois novos targets ficam com R=`-` apesar de ganharem linha no lookup. Com isso, a divergência R-only em relação ao gerador passa de 23 para 25, e está registrada no manifesto.

**Isolamento** (`REFERENCES_4_R1_ISOLATION_AUDIT.json`): CORRELATA conjunto/IDs/rotas/destinos = 0/0/0/0. Continuam valendo:

- 24 CORRELATA visíveis e 2 ocultas;
- relação 1:1 entre `REFERENCE_ID` e `RELACOES`;
- flag C = CORRELATA visíveis;
- flags E/C/J/R/X = 0 mudanças;
- jurisprudência inalterada;
- `OLD_WORK_REFERENCE_SET_PRESERVED = PASS`.

## 6. Header de detalhes e firmware

**Header.** Foi gerado pelo gerador oficial **sem modificação** (`DEVICE_INTEGRATION/tools/build_ref_detail_header.py`), a partir do RUN5 `REF_PAYLOAD` e do overlay efetivo `CF88_WORK_REFERENCE_ADDITIONS_RUN5_EFFECTIVE.json` (21 do RUN3 + 2 do R1, cópia sem alteração). O resultado é `run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h`:

- 124 fichas;
- as 122 antigas são byte a byte iguais;
- chaves únicas, ordenadas para o `strcmp` da busca binária.

O header do firmware versionado **não** foi substituído (sha `2ca5820a…710b`).

**Compilação.** Feita com arduino-cli e core esp32 3.3.11, FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`, `-DLEX_DEVICE_V1_ENABLED=1`. Foi usada uma cópia do sketch em `DEVICE_INTEGRATION/_tmp_fw_references4_r1/`, com binários em `DEVICE_INTEGRATION/backups/references4_r1/`, fora do Git. Nada foi gravado no aparelho.

| Build | Programa | RAM estática | App .bin | sha256 |
|---|---|---|---|---|
| Baseline (sketch versionado) | 1.099.791 B | 126.148 B | 1.099.936 B | `f45ca4e7…e09e` |
| Candidato (header RUN5) | 1.100.991 B (+1.200) | 126.148 B (=) | 1.101.136 B | `6e329c91…d31c` |

A partição app0 tem 1.310.720 B, o que deixa 209.584 B livres.

**Limites da camada 4** (todos com folga):

| Item | Valor máximo | Limite |
|---|---|---|
| `target_id` | 35 | 48 |
| Linha do payload | 193 B | 256 |
| Itens por consulta | 8 | 40 |
| `work_id` | 12 | 47 |
| Rótulo | 42 B | 119 |
| `reference_id` | 68 | 95 |
| Chave da ficha | 37 | 103 |

A lógica do firmware não mudou: só a tabela de dados do header candidato.

## 7. Pacote host-only

O pacote está em `REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/`:

- `candidate/SD/99_LEX_V1/`: os 5 arquivos que mudam (`LEXV1.VER`, `LEX_DEVICE_MANIFEST.json`, `CF88_TARGETS.IDX`, `REF_LOOKUP.IDX`, `REF_PAYLOAD.IDX`);
- `rollback/SD/…`: os bytes do C3B.2, com manifesto `6186c357…665a`;
- `REFERENCES_4_R1_PACKAGE_MANIFEST.json`: diff, hashes e a lista R-only;
- `REFERENCES_4_R1_PHYSICAL_TEST_PLAN.md`.

**Builder do pacote:** `REFERENCE_COVERAGE_AUDIT/build_references4_r1_candidate.py`. Ele usa o gerador oficial `build_sd_staging` com o mesmo perfil `FULL_CF_ENTENDA_810` da promoção C3B.2, com `GIT_COMMIT` fixado em `453922f`, o commit que contém os bytes RUN5.

- **Antes de construir:** reexecuta a promoção C3B.2 oficial e exige o staging aprovado inteiro, byte a byte.
- **Depois:** constrói duas vezes, com resultado idêntico, e exige que o diff contra o C3B.2 seja exatamente esses 5 arquivos.

O builder e o teste de aparelho ficam em `REFERENCE_COVERAGE_AUDIT/`, e não em `DEVICE_INTEGRATION/`. O motivo é o guard de Correlatas 1 (`test_correlata_c3a_engine.test_16`, `test_correlata_c3a1_c3b_prep.test_14`), que proíbe arquivos novos ou modificados em `DEVICE_INTEGRATION/` e `firmware/`. Nenhum arquivo versionado dessas duas pastas foi alterado.

## 8. Testes

| Suíte | Resultado |
|---|---|
| `LEGAL_TARGET_ID/tests` (inclui `test_references4_r1.py`, 13 testes novos) | ver contagem final no commit |
| `REFERENCE_COVERAGE_AUDIT/tests/test_references4_r1_device.py` (9 testes: simulador do aparelho, header, pacote, Correlatas críticas) | ver contagem final |
| `DEVICE_INTEGRATION/tests` | ver contagem final |
| `CORRELATA_COVERAGE_AUDIT/tests`, por arquivo | 4 falhas **pré-existentes**, idênticas num checkout limpo de `af8f68d`: C0 `test_committed_artifacts_are_the_build`, C3A.1 `test_15`, C3B.1 `test_reproducible`, C3B.2 `test_c3b2_package_reproducible…`. São hashes de relatórios reconstruídos que diferem dos versionados, e não foram introduzidas pela R1 |

As contagens finais estão na mensagem de commit e na saída da missão.

## 9. Fora do escopo (não feito)

- Sem deploy, sem acesso ao microSD e sem flash.
- Sem tag e sem merge em `main`.
- Nenhuma revisão dos 122 vínculos.
- Nenhuma expansão: as 199 candidatas e as 19 obras sem vínculo continuam reserva, e os arts. 98 e 202 continuam lacunas confirmadas.
