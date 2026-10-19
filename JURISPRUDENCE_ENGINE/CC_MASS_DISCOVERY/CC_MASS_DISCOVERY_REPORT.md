# CC MASS DISCOVERY — relatório executivo (host-only)

```
CC_MASS_DISCOVERY_STATUS = PARTIAL · BASELINE CC 49/39 · CF 315/198
RAW 2534 · PARES ÚNICOS 1975 · NOVOS 1878 · TIER A 29 · TIER B 160 · TIER C 1786 · QUALIFICADOS 189
NOVOS TARGETS 93 · NOVOS ARTIGOS 82 · SD_CHANGED NO · FIRMWARE_CHANGED NO · RATIFICAÇÃO NÃO REALIZADA
```

## Respostas

1. Relações novas descobertas (pares únicos ainda não publicados nem decididos): 1878 (de 2534 registros brutos).
2. Com fonte oficial confirmada: todos os registros brutos (2534) têm fonte oficial e hash de captura.
3. Passaram nos controles automáticos (TIER A + B): 189.
4. TIER A: 29. 5. TIER B: 160. 6. Rejeitadas automaticamente (TIER C): 1786 (MENTION_ONLY_UNVERIFIED 1204, INCIDENTAL_DECISION 187, CLASS_WITHOUT_CIVIL_THESIS 146, NAMESPACE_CC1916_BY_DATE 62, REVOKED_DISPOSITIVO 59, DUPLICATE_PHYSICAL_BASELINE 52, PREVIOUSLY_DECIDED 36, INVALID_TARGET 11, PREVIOUSLY_DECIDED_PRECEDENT 9, PRECEDENT_NOT_CURRENT 8, NO_MERIT_DECISION 6, SUBSUMED_BY_SPECIFIC_TARGET 4, SUBSUMED_BY_PUBLISHED_SPECIFIC 1, TESE_ADOTOU_OUTRA_NORMA 1).
7. Novos targets que podem receber jurisprudência: 93. 8. Novos artigos: 82.
9. Livro com maior expansão: PARTE_GERAL (87 relações candidatas).
10. Fonte com mais resultados úteis: STJ_ESPELHOS_ACORDAOS (153 relações qualificadas).
11. Casos que exigem análise humana: 160 (TIER B), agrupados por risco na fila; os 29 TIER A podem ir em bloco.
12. Código novo de motor: 0 linhas em `batch_engine.py`/`generic_packager.py`. Código novo: adapters genéricos (#5 STF, #6 espelhos STJ, v2 do #4) e o construtor desta operação.
13. Escala: sim — a operação processou o dataset inteiro de precedentes qualificados (2.403), as 676 súmulas, 331 acórdãos de mérito do STF e 30610 espelhos de acórdãos do STJ sem triagem manual por item; o juízo humano ficou concentrado no TIER B.
14. Projeção (não é aprovação): só TIER A → CC 78/52; TIER A + B → CC 238/132.
15. Estratégia de ratificação em massa: aprovar o GREEN (TIER A) em bloco; revisar o YELLOW por grupo de risco (temporalidade, provisório, realocação, não qualificado, homologatória, evidência indireta), decidindo por regra de grupo e só os casos sinalizados individualmente; manter o RED fora.

## Cobertura por livro

| Livro | Artigos no CC | Artigos com J física | Novos targets candidatos | Relações candidatas (A/B) | Lacuna |
|---|---:|---:|---:|---:|---|
| PARTE_GERAL | 236 | 10 | 32 | 87 (12/75) | OK |
| OBRIGACOES | 736 | 9 | 32 | 55 (8/47) | OK |
| EMPRESA | 232 | 1 | 4 | 4 (0/4) | LACUNA |
| COISAS | 350 | 8 | 6 | 7 (1/6) | LACUNA |
| FAMILIA | 259 | 4 | 15 | 19 (0/19) | OK |
| SUCESSOES | 245 | 2 | 4 | 6 (2/4) | LACUNA |
| DISPOSICOES_FINAIS_TRANSITORIAS | 19 | 1 | 0 | 11 (6/5) | OK |

## Fontes

| Fonte | Registros processados | Com o CC | Hash |
|---|---:|---:|---|
| PLANALTO_VIDE | 10 | — | `f9a857b82647b0e6…` |
| STF_JURISPRUDENCIA | 331 | 283 | `f39ba7d3d2829e12…` |
| STJ_ESPELHOS_ACORDAOS | 30610 | 574 | `3b99a5b6c3bfbe64…` |
| STJ_PRECEDENTES_QUALIFICADOS | 2403 | 41 | `1d5ddb4abf05cdb0…` |
| STJ_SUMULAS_PDF | 676 | — | `2cba87a2d83e278f…` |

Bloqueadas (registradas, não contornadas): STJ_JURISPRUDENCIA_EM_TESES: https://scon.stj.jus.br/SCON/jt/ — desafio Cloudflare com resposta exigida (não contornado), 2026-10-19; STJ_PESQUISA_PRONTA: https://scon.stj.jus.br/SCON/pesquisa_pronta/ — mesmo desafio (403), 2026-10-19; STJ_PUBLICACOES_INSTITUCIONAIS: https://www.stj.jus.br/publicacaoinstitucional/ (Súmulas Anotadas, Jurisprudência em Teses PDF) — página de desafio / 404 no navegador, 2026-10-19; STF_API_DIRETA_DO_HOST: POST direto do host recebe desafio WAF 202; captura feita pelo navegador (caminho normal da página).

## Riscos jurídicos identificados

- Lei 14.905/2024 (arts. 406 e 591) e Lei 15.040/2024 (seguros, arts. 757–802 revogados): pares temporais marcados ou rejeitados.
- Precedentes anteriores ao CC/2002 e regras de transição (art. 2.028): marcados para revisão.
- Acórdãos não qualificados (EREsp/EAREsp/REsp da Segunda Seção e da Corte Especial, homologações) ficam no máximo em B.
- Indexação documental (legislação citada) não basta: exige o artigo no texto da tese/ementa.
- Temas afetados/sobrestados/"RE pendente": provisórios (B).

Auditoria da amostra: 0/40 revisados; erros de identidade 0, de target 0, temporais 0, de pertinência 0, duplicatas 0 (ver CC_MASS_DISCOVERY_AUDIT.md).

## Próxima missão proposta

`MASS HUMAN RATIFICATION` — aprovar o TIER A em bloco, revisar o TIER B por grupos, manter o TIER C fora. Não executada.
