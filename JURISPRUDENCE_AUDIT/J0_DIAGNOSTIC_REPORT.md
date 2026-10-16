# JURISPRUDÊNCIA — CF: J0, auditoria diagnóstica (2026-10-16)

```
MISSION = J0 (HOST-ONLY, READ-ONLY; sem web, sem nova jurisprudência, sem novo pacote)
BRANCH = cf-jurisprudence-audit (a partir de cf-references4-finalize @ 679ba2d; contém os 3 freezes)
AUDITOR = JURISPRUDENCE_AUDIT/build_j0_diagnostic_audit.py → J0_DIAGNOSTIC_AUDIT.json (determinístico, --check UP_TO_DATE)
MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO · FROZEN_LAYERS_MODIFIED = NO
```

## 1. Estado atual

- **No aparelho:** 277 vínculos de jurisprudência visíveis em **170 targets** (76 artigos), mais 6 ocultos históricos. A camada funciona pela tecla `2 JURIS.`.
- **Origem:** os vínculos vêm todos de **extração automática por citação literal** (J4, 2026-09-21) sobre teses oficiais do STF:
  - Repercussão Geral: 811 temas analisados;
  - Súmulas Vinculantes: 63 analisadas.
- **Revisão humana:** **nenhum vínculo publicado passou por revisão humana individual**. O J4 marca `revisao_manual = nao_requerida` em 296/296.
- **Decisões humanas que existem na camada:**
  - 2 exclusões `MATERIAL_MISMATCH` (Tema 113 × art. 25 e Tema 756 × art. 31, § 3º), vindas da revisão do ENTENDA Batch04;
  - a revisão J2.5 de SV 28/SV 29, concluída sem promoção.
- **Decisões humanas formais abertas:** nenhuma.

## 2. Fonte autoritativa

```
AUTHORITATIVE_EDITORIAL_SOURCE = C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4/VINCULOS_EXPLICITOS.json
                                 (296 vínculos EXPLICITO; arquivo protegido fora do Git, sha256 fixado no J0_DIAGNOSTIC_AUDIT.json)
                                 + LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json (overlay de exclusões aprovadas)
                                 → normalizados em LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json (camada SD_JURIS_J4_6_IDS, 263 IDs)
                                   e CF88_QUARANTINE_RESOLUTION.json (17 splits de citações mistas)
AUTHORITATIVE_DEVICE_SOURCE    = baseline físico 2026-10-16:
                                 /99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX + REF_LOOKUP.IDX (linhas JURISPRUDENCE)
                                 + /99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX (flag J)
                                 + /99_JURISPRUDENCIA_V2/ (legado J4.6: JURISPRUDENCIA.IDX f85108ba…, JUR_LOOKUP.IDX 7931e28e…, 229 TXT de teses)
                                 cópia versionada: REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/
```

**Por que são fontes diferentes:**

- O dado editorial é o J4, que decide *qual tese cita qual dispositivo*.
- O dado do aparelho é o export do Reference Engine (RUN5, idêntico em jurisprudência desde o RUN2) mais o pacote legado.
  - O export decide *em que target canônico* cada vínculo aparece.
  - O pacote legado guarda o *texto da tese* exibido na ficha.
- O reference engine aplica três transformações sobre o J4:
  - canonicalização (artigo → caput, splits);
  - exclusões;
  - ocultação de targets `HISTORICAL_ONLY`.

## 3. Linha do tempo

| Etapa | Data / commit | Objetivo | Vínculos | Targets | Estado |
|---|---|---|---:|---:|---|
| J1 | 2026-09-21 (não versionado, `LEX_MACHINA_JURIS_CF_J1/`) | Auditoria da infraestrutura e modelo canônico | — | — | HISTÓRICO |
| J2 | 2026-09-21 (archive) | Piloto (15 RG + 15 SV) | 35 | 35 | HISTÓRICO |
| J2.5 | 2026-09-21 (archive) | Saneamento do parser; SV 28/29 revisadas sem promoção | 35 | 35 | HISTÓRICO |
| J3 | 2026-09-21 (archive; firmware v7.11.0) | 1ª integração física do piloto | 35 | 35 | HISTÓRICO |
| J4 | 2026-09-21 (archive) | Expansão: 874 registros, 221 navegáveis, 651 temáticos rejeitados | **296** | 178 | **ORIGEM EDITORIAL ATUAL** |
| J4.5 | 2026-09-21 (`firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/RELATORIO_J4_5.md`) | Cache dinâmico em PSRAM (limite 64 → 4.096) | 296 | 178 | HISTÓRICO (firmware legado) |
| J4.6 | 2026-09-21, tag `backup-v7.12.0-juris-cf-expandida-hardware-ok-20260921` (`d4e816f`) | SD + checklist físico (10 positivos e 5 negativos) aprovado no ESP32 | 296 | 178 | Validação física do **firmware legado** |
| CF-REF A2/A3 | 2026-09-28, `85597db` / `9fcab70` | Canonicalização em `target_id` e Reference Engine RUN1 (285 juris) | 285 | — | HISTÓRICO |
| RUN2 → RUN5 | 2026-10-03 (`10e199f`) até 2026-10-16 (`45a0084`) | Exclusão de Tema 113 × art. 25 e Tema 756 × art. 31 § 3º; jurisprudência inalterada nas rodadas seguintes | **277 + 6 ocultos** | **170** | **ATUAL (aparelho)** |

## 4. Contagens

| Métrica | Valor |
|---|---:|
| `JURIS_RELATIONS` (visíveis) | **277** |
| Ocultos históricos | 6 |
| `JURIS_TARGETS` | **170** (169 CF + 1 ADCT) |
| Artigos com jurisprudência | 76 |
| Fontes distintas (teses/súmulas) | 214 |
| Vínculos J4 de origem | 296 (221 registros, 178 dispositivos) |
| Exclusões aprovadas | 2 |
| Referências a outras normas (`CROSS_NORM_PENDING`, fora do catálogo CF) | 27 |
| Targets mais carregados | art. 37, XI (10); art. 150, VI, a (6); art. 37, § 6º (5) |
| Artigos mais carregados | arts. 5 e 37 (27 cada); art. 150 (21); art. 40 (18); art. 100 (17) |

## 5. Tipos de jurisprudência

Taxonomia do projeto (`tipo`):

- `repercussao_geral`: **267** (Temas de RG, `STF:RG:n`);
- `sumula_vinculante`: **10** (`STF:SV:n`).

Não há acórdãos avulsos, ADI/ADC/ADPF, súmulas comuns nem repetitivos no dataset atual. Esses tipos aparecem apenas como recomendações no backlog.

## 6. Cobertura (não é métrica de qualidade)

| Nível do target | Targets com J |
|---|---:|
| Inciso | 78 |
| Parágrafo | 52 |
| Artigo | 33 |
| Caput | 6 |
| ADCT | 1 |

A ausência de jurisprudência pode ser legítima. As lacunas estão na seção 9.

## 7. Problemas estruturais

**Integridade estrutural do aparelho: PASS.**

| Verificação | Resultado |
|---|---:|
| `J_FLAGS` | 170 |
| `J_FLAGS_WITHOUT_RELATION` | **0** |
| `J_RELATIONS_WITHOUT_FLAG` | **0** |
| Duplicatas (mesma fonte, mesmo target) | 0 |
| Vínculos órfãos (target inexistente) | 0 |
| Vínculos sem registro no `JURISPRUDENCIA.IDX` legado do cartão | 0 |
| Vínculos sem arquivo de tese no cartão | 0 |
| Identificadores incompletos | 0 |
| Vínculos sem fonte oficial verificável | 0 (todos com URL `portal.stf.jus.br`, sha do conteúdo e trecho literal) |

**`NEEDS_HUMAN_REVIEW` = 86 vínculos** (sinais objetivos; nenhum mérito foi decidido automaticamente):

| Severidade | n | Sinais |
|---|---:|---|
| **HIGH** | **8** | 7 `LIKELY_OTHER_NORM_ARTICLE` + 1 `TARGET_STATUS_UNKNOWN_VALIDITY` |
| MEDIUM | 31 | `NORM_CONTEXT_CF_AND_OTHER_NORM_IN_SAME_CITATION` (29), `NORM_CONTEXT_NO_NORM_MARKER` (8), `PARENT_CHILD_SAME_SOURCE` (3) |
| LOW | 47 | `BROAD_ARTICLE_TARGET_WITH_SUBDIVISIONS` (35), `SPLIT_FROM_MIXED_CITATION` (22) |

Um vínculo pode ter mais de um sinal.

**Achado principal: falsos positivos de numeração.** São da mesma classe já excluída humanamente (Tema 113 × art. 25), e o próprio trecho oficial arquivado no J4 cita o artigo de **outra norma**:

| Target exibido | Fonte | O trecho cita |
|---|---|---|
| CF art. 1º | RG 63 | art. 1º do Decreto-Lei 491/1969 |
| CF art. 3º | RG 1266 | art. 3º da LC 190/2022 |
| CF art. 3º | RG 295 | art. 3º, VII, da Lei 8.009/1990 |
| CF art. 19 | RG 1157 | art. 19 **do ADCT** (erro de namespace) |
| CF art. 47 | RG 703 | art. 47 da Lei 6.880/80 |
| CF art. 48, III | RG 241 | art. 48, III, da Lei 4.215/63 |
| CF art. 8º, IV | RG 241 | art. 8º, IV, da Lei 8.906/94 |

Esses 7 estão visíveis hoje no aparelho, alguns em artigos muito consultados (arts. 1º, 3º e 19). Os demais sinais exigem leitura humana do trecho, sem pesquisa externa.

## 8. Backlog de recomendações

O backlog vem das versões finais de cada lote do ENTENDA (`JURISPRUDENCE_LINK_RECOMMENDATIONS.json`), deduplicado por target e referência normalizada. Os números históricos foram **confirmados**:

| Categoria | n |
|---|---:|
| Recomendações únicas | 170 (0 duplicatas entre lotes) |
| `ALREADY_LINKED` | **19** |
| `EXCLUDED_MATERIAL_DIVERGENCE` | **3** |
| `NEEDS_EXTERNAL_INGESTION` | **148** em **110 targets** |

**Detalhe dos 148:**

- **Identificação:** 72 nomeiam um identificador explícito (Tema, SV, Súmula, ADI/ADPF/RE…); 67 estão como `IDENTIFICACAO_PENDENTE` e exigem pesquisa para sequer identificar a decisão.
- **Concentração:** 33 caem em targets que já têm jurisprudência.
- **Por lote:** Macro07 73, Macro08 32, Batch06 13, Batch04 8, Batch02 9, Batch01 7, Batch03 6.

**Prioridade técnica/editorial** (não é mérito). Critérios objetivos:

- identificador nomeado;
- recorrência;
- artigo hoje sem jurisprudência;
- referência descrita.

| Prioridade | n | Targets |
|---|---:|---:|
| **HIGH** | **40** | 26 |
| MEDIUM | 81 | — |
| LOW | 27 | — |

Os itens HIGH incluem, por exemplo, o Tema 793 (art. 23, II), os Temas 157/835 (art. 31, § 2º), a Súmula 702 (art. 29, X) e a SV 46 (art. 29-A, § 2º). A lista completa e a base de cada prioridade estão em `J0_DIAGNOSTIC_AUDIT.json` → `backlog.items`.

## 9. Lacunas

Foram considerados 411 artigos vigentes ou estruturais (CF + ADCT), sem regra de que todo artigo precise de J.

| Classe | CF | ADCT |
|---|---:|---:|
| `HIGH_VALUE_GAP` (artigo sem J e ≥ 2 recomendações pendentes) | 9 | 3 |
| `POTENTIAL_GAP` (1 recomendação) | 24 | 6 |
| `NO_LOCAL_GAP_SIGNAL` (nenhum sinal local; **não** significa "deveria ter") | 165 | 128 |

**`HIGH_VALUE_GAP`:**

- CF arts. 23, 29, 31, 52, **53** (6 recomendações), 86, 103, 166 e 226;
- ADCT arts. 27, 101 e 107-A.

## 10. Aparelho

**`EDITORIAL_DATA`:** J4 (`VINCULOS_EXPLICITOS`), mais as exclusões e o catálogo canônico.

**`DEVICE_DATA`:**

- linhas `JURISPRUDENCE` de `REF_PAYLOAD`/`REF_LOOKUP` (283 linhas; 170 chaves);
- flag J (`CF88_TARGETS.IDX`, posição [2], lida pelo firmware);
- `99_JURISPRUDENCIA_V2` legado: índices byte-idênticos ao J4.6 e 229 TXT de teses.

**Fluxo no firmware DEVICE V1:**

1. O rodapé mostra `2 JURIS.` quando a flag J está ativa no target ou no seu par artigo/caput.
2. A lista vem do `REF_PAYLOAD`, com limite de `LEXV1_REL_REGS_MAX = 32` registros por chave (o máximo atual é 10).
3. A ficha abre pela chave do vínculo (`STF:RG:n:CF88:…`) no `JURISPRUDENCIA.IDX` legado e no texto `03_CONTEUDO/STF_*.TXT`.

Não há header de firmware específico de jurisprudência.

**Dependência compartilhada (só registrada):** qualquer correção em J regenera `REF_LOOKUP`/`REF_PAYLOAD`/`CF88_TARGETS`, os mesmos arquivos das camadas congeladas CORRELATAS 1 e REFERÊNCIAS Nº 4. Uma rodada J1 com efeito no aparelho precisa provar a invariância das linhas CORRELATA e WORK_REFERENCE e das flags C/W/E/X, como fizeram a C3B.2 e a R1.

## 11. Estado físico

```
JURIS_DEDICATED_PHYSICAL_TEST = NO (na arquitetura atual DEVICE V1)
```

- **J4.6 (firmware legado v7.12.0, 2026-09-21):** teve validação física dedicada (checklist de 10 positivos e 5 negativos, tag `backup-v7.12.0-juris-cf-expandida-hardware-ok-20260921`). Isso foi **antes** da migração para o DEVICE V1 e para o `target_id` canônico.
- **DEVICE V1 (2026-10-01 em diante):** a jurisprudência funcionou **incidentalmente** nas validações físicas de arquitetura (`DEVICE_V1_PHYSICAL_BASELINE_APPROVED.md`: separação JURIS × REF, resolução por target canônico, 0 *mismatches*). Nunca houve rodada física dedicada ao conteúdo J.
- **Freeze:** não existe.

## 12. Próxima rodada recomendada

```
NEXT_RECOMMENDED_MISSION = J1 — REVISÃO HUMANA DIRIGIDA POR RISCO DOS 277 VÍNCULOS EXISTENTES
```

**Escopo:**

1. Os **8 HIGH**: decidir exclusão ou realocação. Os 7 de numeração são candidatos naturais a `MATERIAL_MISMATCH_EXCLUDED`, pelo mesmo mecanismo das exclusões já aprovadas.
2. Os **31 MEDIUM**: leitura do trecho arquivado.
3. Os **47 LOW**: amostragem ou regra de granularidade (artigo × caput/inciso).
4. Um candidato host-only com prova de invariância das camadas congeladas.

**Por que antes da ingestão dos 148:**

- corrige erros **já visíveis** no aparelho;
- não exige web (todo o texto oficial está arquivado com sha);
- tem volume pequeno (86 sinais, 8 críticos);
- normaliza o dataset antes de expandi-lo.

A ingestão dos 40 HIGH do backlog fica para um **J2**, que exige pesquisa externa.
