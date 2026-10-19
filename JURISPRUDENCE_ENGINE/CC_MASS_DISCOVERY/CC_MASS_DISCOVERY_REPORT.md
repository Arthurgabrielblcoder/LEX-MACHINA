# CC MASS DISCOVERY — relatório executivo (host-only)

```
CC_MASS_DISCOVERY_STATUS = SUCCESS · BASELINE CC 49/39 · CF 315/198
RAW 33385 · PARES ÚNICOS 27889 · NOVOS 27792 · TIER A 29 · TIER B 903 · TIER C 26957 · QUALIFICADOS 932
NOVOS TARGETS 840 · NOVOS ARTIGOS 661 · SD_CHANGED NO · FIRMWARE_CHANGED NO · RATIFICAÇÃO NÃO REALIZADA
```

## Respostas

1. Relações novas descobertas (pares únicos ainda não publicados nem decididos): 27792 (de 33385 registros brutos).
2. Com fonte oficial confirmada: todos os registros brutos (33385) têm fonte oficial e hash de captura.
3. Passaram nos controles automáticos (TIER A + B): 932.
4. TIER A: 29. 5. TIER B: 903. 6. Rejeitadas automaticamente (TIER C): 26957 (INCIDENTAL_DECISION 8752, MENTION_ONLY_UNVERIFIED 6629, COVERED_BY_HIGHER_SOURCE 2526, NAMESPACE_CC1916_BY_DATE 1909, MENTION_IN_CLAIM_ONLY 1905, CORROBORATION_NON_QUALIFIED 1360, NON_QUALIFIED_WEAK_EVIDENCE 1209, NO_MERIT_DECISION 1051, REVOKED_DISPOSITIVO 1011, CLASS_WITHOUT_CIVIL_THESIS 239, SUBSUMED_BY_SPECIFIC_TARGET 175, INVALID_TARGET 84, DUPLICATE_PHYSICAL_BASELINE 52, PREVIOUSLY_DECIDED 36, PREVIOUSLY_DECIDED_PRECEDENT 9, PRECEDENT_NOT_CURRENT 8, SUBSUMED_BY_PUBLISHED_SPECIFIC 1, TESE_ADOTOU_OUTRA_NORMA 1).
7. Novos targets que podem receber jurisprudência: 840. 8. Novos artigos: 661.
9. Livro com maior expansão: OBRIGACOES (318 relações candidatas).
10. Fonte com mais resultados úteis: STJ_ESPELHOS_TURMAS (749 relações qualificadas).
11. Casos que exigem análise humana: 903 (TIER B), agrupados por risco na fila; os 29 TIER A podem ir em bloco.
12. Código novo de motor: 0 linhas em `batch_engine.py`/`generic_packager.py`. Código novo: adapters genéricos (#5 STF, #6 espelhos STJ, v2 do #4) e o construtor desta operação.
13. Escala: sim — a operação processou o dataset inteiro de precedentes qualificados (2.403), as 676 súmulas, 331 acórdãos de mérito do STF e 212467 espelhos de acórdãos do STJ sem triagem manual por item; o juízo humano ficou concentrado no TIER B.
14. Projeção (não é aprovação): só TIER A → CC 78/52; TIER A + B → CC 981/879.
15. Estratégia de ratificação em massa: aprovar o GREEN (TIER A) em bloco; revisar o YELLOW por grupo de risco (temporalidade, provisório, realocação, não qualificado, homologatória, evidência indireta), decidindo por regra de grupo e só os casos sinalizados individualmente; manter o RED fora.

## Composição do qualificado (leitura honesta)

- Precedentes qualificados, Seções, Corte Especial e STF: 184 relações (TIER A 29).
- Representantes de acórdãos da 3ª/4ª Turma: 748 relações, uma por dispositivo sem outro vínculo; todas TIER B (precedente não qualificado). 1360 acórdãos ficaram como corroboração e 2526 já estavam cobertos por fonte superior (não contados).
- Sem os acórdãos de Turma o total seria inferior a 200: a meta foi atingida com jurisprudência oficial real, mas em grande parte não vinculante — o ganho é cobertura (dispositivos sem nenhuma jurisprudência), não autoridade.

## Dados não versionados (política de datasets brutos)

- `stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json` (índice derivado, 47 MB) e `CC_MASS_DISCOVERY/_local/` (RAW completo e rejeições das Turmas) ficam fora do git; os hashes estão em CC_MASS_DISCOVERY_SHA256.json e CC_MASS_SOURCE_INVENTORY.json (arquivo a arquivo).
- Reconstrução: baixar os recursos dos datasets `espelhos-de-acordaos-terceira-turma` e `espelhos-de-acordaos-quarta-turma` do portal https://dadosabertos.web.stj.jus.br (CKAN, CC-BY) e rodar `python discovery_stj_espelhos.py --dir <3ª Turma> --dir <4ª Turma> --out stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json`, depois `python build_cc_mass_discovery.py`; o `--check` confere byte a byte.

## Cobertura por livro

| Livro | Artigos no CC | Artigos com J física | Novos targets candidatos | Relações candidatas (A/B) | Lacuna |
|---|---:|---:|---:|---:|---|
| PARTE_GERAL | 236 | 10 | 155 | 208 (12/196) | OK |
| OBRIGACOES | 736 | 9 | 297 | 318 (8/310) | OK |
| EMPRESA | 232 | 1 | 53 | 53 (0/53) | LACUNA |
| COISAS | 350 | 8 | 131 | 132 (1/131) | LACUNA |
| FAMILIA | 259 | 4 | 126 | 130 (0/130) | OK |
| SUCESSOES | 245 | 2 | 68 | 70 (2/68) | LACUNA |
| DISPOSICOES_FINAIS_TRANSITORIAS | 19 | 1 | 10 | 21 (6/15) | OK |

## Fontes

| Fonte | Registros processados | Com o CC | Hash |
|---|---:|---:|---|
| PLANALTO_VIDE | 10 | — | `f9a857b82647b0e6…` |
| STF_JURISPRUDENCIA | 331 | 283 | `f39ba7d3d2829e12…` |
| STJ_ESPELHOS_ACORDAOS | 30610 | 574 | `3b99a5b6c3bfbe64…` |
| STJ_ESPELHOS_TURMAS | 181857 | 16528 | `e48d7fcd2a688429…` |
| STJ_PRECEDENTES_QUALIFICADOS | 2403 | 41 | `1d5ddb4abf05cdb0…` |
| STJ_SUMULAS_PDF | 676 | — | `2cba87a2d83e278f…` |

Bloqueadas (registradas, não contornadas): STJ_JURISPRUDENCIA_EM_TESES: https://scon.stj.jus.br/SCON/jt/ — desafio Cloudflare com resposta exigida (não contornado), 2026-10-19; STJ_PESQUISA_PRONTA: https://scon.stj.jus.br/SCON/pesquisa_pronta/ — mesmo desafio (403), 2026-10-19; STJ_PUBLICACOES_INSTITUCIONAIS: https://www.stj.jus.br/publicacaoinstitucional/ (Súmulas Anotadas, Jurisprudência em Teses PDF) — página de desafio / 404 no navegador, 2026-10-19; STF_API_DIRETA_DO_HOST: POST direto do host recebe desafio WAF 202; captura feita pelo navegador (caminho normal da página).

## Riscos jurídicos identificados

- Lei 14.905/2024 (arts. 406 e 591) e Lei 15.040/2024 (seguros, arts. 757–802 revogados): pares temporais marcados ou rejeitados.
- Precedentes anteriores ao CC/2002 e regras de transição (art. 2.028): marcados para revisão.
- Acórdãos não qualificados (Seções, Corte Especial, Turmas, homologações) ficam no máximo em B; os de Turma, só como representante.
- Recurso não conhecido por óbice de admissibilidade e dispositivo citado só na alegação da parte: rejeitados (C).
- Decisões que aplicaram o CC/1916 citando o artigo correspondente do CC/2002: sinalizadas (CORRESPONDENCIA_CC1916).
- Indexação documental (legislação citada) não basta: exige o artigo no texto da tese/ementa.
- Temas afetados/sobrestados/"RE pendente": provisórios (B).

Auditoria da amostra: 40/40 revisados; erros de identidade 0, de target 0, temporais 0, de pertinência 3, duplicatas 0 (ver CC_MASS_DISCOVERY_AUDIT.md).

## Próxima missão proposta

`MASS HUMAN RATIFICATION` — aprovar o TIER A em bloco, revisar o TIER B por grupos, manter o TIER C fora. Não executada.
