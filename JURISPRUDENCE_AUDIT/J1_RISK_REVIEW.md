# JURISPRUDÊNCIA — CF: J1, revisão dirigida por risco dos vínculos existentes (2026-10-16)

```
MISSION = J1 (HOST-ONLY, sem web, sem deploy, sem materialização)
BRANCH = cf-jurisprudence-audit (base cf-references4-finalize @ 679ba2d, com os 3 freezes)
DECISÕES = JURISPRUDENCE_AUDIT/J1_DECISIONS.json (86 decisões persistidas; gerador build_j1_risk_review.py, 3/3 execuções idênticas)
AUTORIDADE = revisão de evidência local (Claude), PENDENTE DE RATIFICAÇÃO HUMANA
BACKLOG_148_TOUCHED = NO · DEVICE_DATA_CHANGED = NO · FROZEN_LAYERS_MODIFIED = NO · MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO
```

## 1. Reconciliação da contagem crítica

```
CRITICAL_SIGNAL_COUNT = 8
PROBABLE_CROSS_NORM_FALSE_POSITIVES = 7
```

Os 8 sinais HIGH do J0 são:

- 7 `LIKELY_OTHER_NORM_ARTICLE`;
- 1 `TARGET_STATUS_UNKNOWN_VALIDITY`: ADCT art. 78, § 4º ← Tema 231.

O oitavo é um vínculo **correto**. A tese cita expressamente "§ 4º do art. 78 do ADCT", e o sinal vem só da validade temporal do target. A tabela do J0 já mostrava 7 + 1; a frase "8 HIGH" do J0 está coerente com isso.

## 2. Método

**Fonte das decisões.** Cada decisão usa só o texto oficial arquivado no J4:

- `referencia_detectada` / `trecho`;
- a tese completa, com `fonte_oficial.sha256_conteudo`;
- o texto local da CF (`CF88_TARGET_INDEX.json`) quando a questão é a redação atual do dispositivo.

**Ordem de revisão:**

| Tier | Conteúdo |
|---|---|
| 1 | Confusão de norma ou de namespace (CF × ADCT) |
| 2 | Duplicação |
| 3 | Pai/filho |
| 4 | Proveniência |
| 5 | Heurísticos e temporais |

**Vínculos sem sinal.** Os 191 vínculos sem sinal receberam só o controle leve (seção 6).

## 3. Os 7 falsos positivos do J0: revalidados

| Target CF | Precedente | O trecho oficial cita | Causa | Decisão |
|---|---|---|---|---|
| art. 1º | Tema 63 (RE 561485) | art. 1º do **Decreto-Lei 491/1969** | numeração de outra norma | `REMOVE_RELATION` |
| art. 3º | Tema 1266 | art. 3º da **LC 190/2022** | numeração de outra norma | `REMOVE_RELATION` |
| art. 3º | Tema 295 | art. 3º, VII, da **Lei 8.009/1990** | numeração de outra norma | `REMOVE_RELATION` |
| art. 19 | Tema 1157 | art. 19 do **ADCT** | namespace ADCT lido como CF | `REMOVE_RELATION` (candidato a realocar: `ADCT:ART.19`) |
| art. 47 | Tema 703 | art. 47 da **Lei 6.880/1980** | numeração de outra norma | `REMOVE_RELATION` |
| art. 48, III | Tema 241 | art. 48, III, da **Lei 4.215/1963** | numeração de outra norma | `REMOVE_RELATION` |
| art. 8º, IV | Tema 241 | art. 8º, IV, da **Lei 8.906/1994** | numeração de outra norma | `REMOVE_RELATION` |

## 4. Achados novos na revisão dos sinais MEDIUM/LOW

A revisão encontrou **13 falsos positivos adicionais**, da mesma classe, que o detector do J0 não marcou como HIGH:

| Target CF | Precedente | O texto oficial cita | Causa |
|---|---|---|---|
| art. 14, § 2º | Tema 84 | § 2º do art. 14 da **Lei 4.502/1964** | outra norma |
| art. 41, § 1º | Tema 63 | § 1º do art. 41 do **ADCT** | namespace (candidato a realocar: `ADCT:ART.41:PAR.1`) |
| art. 43, caput | Tema 975 | art. 43 da **LC estadual SP 1.059/2008** | outra norma |
| art. 43, § 1º | Tema 975 | idem | outra norma |
| art. 98, caput | Tema 847 | art. 98 do **ADCT** (Defensorias) | namespace (`ADCT:ART.98`) |
| art. 98, § 2º | Tema 847 | idem | namespace (`ADCT:ART.98:PAR.2`) |
| art. 16 | Tema 1031 | art. 16.4 da **Convenção 169 da OIT** | outra norma |
| art. 227 | Tema 966 | art. 227 da **LC 75/1993** | outra norma |
| art. 227 | Tema 976 | idem (julgamento conjunto) | outra norma |
| art. 3º | Tema 396 | art. 3º da **EC 47/2005** | outra norma |
| art. 7º | Tema 396 | art. 7º da **EC 41/2003** | outra norma |
| art. 6º | Tema 455 | arts. 6º a 8º do **Decreto 21.981/1932** | outra norma |
| art. 96 | Tema 400 | art. 96 **inserido no ADCT** | namespace (`ADCT:ART.96`) |

**Total de falsos positivos de numeração: 20 de 277 (7,2%).** Os mesmos temas continuam corretamente vinculados aos dispositivos da CF que de fato citam:

- Tema 295 → art. 6º;
- Tema 455 → art. 5º, XIII;
- Tema 1031 → art. 231;
- Temas 966/976 → arts. 73, § 3º, 75, 102, I, 121, § 2º, 131 e 134, § 2º.

## 5. Decisões dos 86 sinais

| Decisão | n | Observação |
|---|---:|---|
| `KEEP_CONFIRMED` | **61** | A citação nomeia o dispositivo da CF/ADCT; o sinal era heurístico (granularidade de artigo, split fiel, outra norma só como objeto, pai/filho citados separadamente, validade temporal do target) |
| `REMOVE_FALSE_POSITIVE` | **20** | Seções 3 e 4 |
| `EXTERNAL_REVIEW_REQUIRED` | **4** | A tese cita **redação anterior**, e o § atual (texto local) trata de outra matéria: SV 17 e Tema 147 → art. 100, § 1º (prazo de pagamento hoje no § 5º?); Tema 594 → art. 40, §§ 4º e 5º (redação anterior à EC 20/98) |
| `DUPLICATE_OR_REDUNDANT` | **1** | Tema 387 → art. 16: tese literalmente idêntica à do Tema 367 no mesmo target. Os dois são válidos; decidir se a exibição consolida |
| `WEAK_PROVENANCE` | **0** | Todos os 86 têm URL oficial, sha do conteúdo e trecho literal |

**Notas registradas sem mudança de decisão:**

- SV 7 e Tema 98 → art. 192, § 3º: o vínculo é correto, porque o § revogado é o próprio objeto. Mas o target revogado aparece com status `CURRENT` no catálogo de status, o que é dívida de metadados da Lei Seca.
- Tema 1254 → art. 40: cita "na redação dada pela EC 20/98".

## 6. Vínculos sem sinal: controle leve

| Item | Resultado |
|---|---|
| Vínculos | **191** |
| Classificação | `NO_SIGNAL_KEEP_PENDING_GLOBAL_REVIEW` |
| Estrutura e proveniência | OK |
| Detector ampliado de outra norma | 5 ocorrências, todas citações **da CF** com nota "na redação da EC…" (Temas 825, 1177, 282, 1207, 1167). **0 suspeitos** |

**Teses idênticas com IDs diferentes**, observação para a materialização:

- RG 367 = RG 387;
- RG 40 = SV 12;
- RG 533 = RG 987;
- RG 61 = SV 18;
- RG 630 = RG 684.

## 7. Quadro final (reconcilia com os 277)

```
KEEP_CONFIRMED            = 61
REMOVE_FALSE_POSITIVE     = 20
EXTERNAL_REVIEW_REQUIRED  =  4
DUPLICATE_OR_REDUNDANT    =  1
WEAK_PROVENANCE           =  0
NO_SIGNAL                 = 191
TOTAL                     = 277   (86 sinais + 191 sem sinal)
```

## 8. Impacto das remoções propostas (simulação lógica; nada foi regenerado)

| Item | Valor |
|---|---:|
| Vínculos antes / depois | 277 → **257** |
| Targets afetados | 17 |
| Perdem o último vínculo J (flag J mudaria de `J` para `-`) | **13** |
| Continuam com J por outro precedente | 4 (arts. 6º, 8º IV, 16, 227) |

**Os 13 targets que perderiam a flag J:**

- CF art. 1, 3, 7, 19, 47 e 96;
- CF art. 14, § 2º;
- CF art. 41, § 1º;
- CF art. 43, caput e § 1º;
- CF art. 48, III;
- CF art. 98, caput e § 2º.

As mesmas 13 linhas do leitor deixariam de mostrar `2 JURIS.`.

**Realocação possível** (exige decisão própria; não é automática): `ADCT:ART.19`, `ADCT:ART.41:PAR.1`, `ADCT:ART.96`, `ADCT:ART.98`, `ADCT:ART.98:PAR.2`.

**Materializar** exige:

- o overlay `CF88_LINK_EXCLUSIONS.json`, mecanismo já usado para Tema 113/756;
- um export RUN6;
- a prova de invariância das linhas CORRELATA/WORK_REFERENCE e das flags C/W/E/X;
- teste físico.

## 9. Próxima missão

```
NEXT_RECOMMENDED_MISSION = J1.1 — RATIFICAR E MATERIALIZAR AS 20 REMOÇÕES (host-only: overlay de exclusões + RUN6 candidato + prova de invariância das camadas congeladas)
```

As 4 `EXTERNAL_REVIEW_REQUIRED`, as 5 realocações para o ADCT e o backlog de 148 ficam para uma rodada com pesquisa externa (J2).
