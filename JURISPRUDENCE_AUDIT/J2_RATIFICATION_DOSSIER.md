# J2 — DOSSIÊ DE RATIFICAÇÃO (Batches 03, 04, 06, 07, 08, 09)

```
RATIFICADO PELO USUÁRIO em 2026-10-17: 54 decisões HUMAN_APPROVED · 1 UNRESOLVED_EXTERNAL (J0-BL-001) · registro: J2_RATIFICATION_RECORD_03_09.json
Gerado por render_j2_ratification_dossier.py a partir dos JSONs dos lotes · Batch05 = vazio (fechamento HIGH)
```

**Como ler:**

- **Linha:** cada linha é uma recomendação do backlog J0 (`J0-BL-nnn`), com uma única decisão proposta.
- **Realocação:** aparece como `ORIGINAL → CORRETO`.
- **Promoção provisória:** traz natureza, último status e gatilho de revalidação.
- **Relação:** cada relação é um par *target × precedente*; uma decisão pode gerar várias.

## Batch03 (HIGH) — `J2_HIGH_BACKLOG/J2_BATCH03_DECISIONS.json`

### Promoções (5)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 1 | J0-BL-047 | CF88:ART.29:INC.X | Súmula 702 | STF/SUMULA | CF88:ART.29:INC.X | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Súmula do STF cuja referência legislativa oficial é exatamente o art. 29, X. |
| 2 | J0-BL-054 | CF88:ART.52:PAR.UNICO | MS 21689 | STF/MS | CF88:ART.52:PAR.UNICO | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Precedente do Pleno que interpreta diretamente o art. 52, p.u.: inabilitação autônoma e efeito da renúncia (caso Collor). |
| 3 | J0-BL-061 | CF88:ART.55:INC.VI | AP 694 | STF/AP | CF88:ART.55:INC.VI | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Interpreta diretamente o art. 55, VI. |
| 4 | J0-BL-122 | CF88:ART.130 | ADI 789 | STF/ADI | CF88:ART.130 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Precedente-base do STF sobre o art. 130. |
| 5 | J0-BL-045 | CF88:ART.31:PAR.2 | Tema 157 | STF/RG | CF88:ART.31:PAR.2 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Tese vinculante que define a natureza do parecer prévio do § 2º do art. 31. |

### Promoções provisórias (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 6 | J0-BL-165 | ADCT:ART.27 | ADI 5017 | STF/ADI | ADCT:ART.27:PAR.11 | PROMOTE_PROVISIONAL_RECOMMENDED | HUMAN_APPROVED | Informação essencial para quem lê o § 11 (a criação dos TRFs pela EC 73/2013 está suspensa desde 2013). **Provisório** — natureza: cautelar monocrática não referendada; mérito pendente (conclusos em 18/06/2025); última verificação: 2026-10-17; gatilho: REFERENDO_OU_JULGAMENTO_DE_MERITO; prazo: 90 dias. |

### Realocações (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 7 | J0-BL-090 | CF88:ART.103:PAR.1 | ADI 1616; ADI 1254 | STF/ADI | CF88:ART.103:PAR.1 → CF88:ART.103:PAR.3 | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | A nota do backlog cita "art. 103, § 3º", mas o target ficou no § 1º (oitiva do PGR). |

### Rejeições (descompasso temporal) (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 8 | J0-BL-134 | CF88:ART.165:PAR.18 | ADI 7047/7064 | STF/ADI | — | REJECT_TEMPORAL_MISMATCH_RECOMMENDED | HUMAN_APPROVED | Uma decisão de 2023 não pode ter interpretado um parágrafo criado em 2025. |

### Rejeições (não material) (2)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 9 | J0-BL-053 | CF88:ART.52:PAR.UNICO | MS 34418 | STF/MS | — | REJECT_NOT_MATERIAL_RECOMMENDED | HUMAN_APPROVED | O STF não decidiu se a votação separada (perda do cargo × inabilitação) é válida: o mandado foi julgado prejudicado ou não conhecido. |
| 10 | J0-BL-048 | CF88:ART.29:INC.X | HC 232627; Inq 4787 | STF/HC, STF/INQ | — | REJECT_NOT_MATERIAL_RECOMMENDED | HUMAN_APPROVED | A tese é geral sobre foro após o fim do cargo, mas os acórdãos interpretam só o art. 53, § 1º (já aprovado no Batch02 para o HC). |

## Batch04 (HIGH) — `J2_HIGH_BACKLOG/J2_BATCH04_DECISIONS.json`

### Promoções (4)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 1 | J0-BL-046 | CF88:ART.31:PAR.2 | Tema 835 | STF/RG | CF88:ART.31:PAR.2 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Complementa o Tema 157 (Batch03) no mesmo § 2º: também as contas de gestão do prefeito são julgadas pela Câmara. |
| 2 | J0-BL-051 | CF88:ART.35:INC.IV | ADI 7369; AI 343461; ADI 336 | STF/ADI, STF/AI | CF88:ART.35:INC.IV, CF88:ART.35 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Divisão por alvo. |
| 3 | J0-BL-067 | CF88:ART.86 | MS 21564; ADPF 378 | STF/ADPF, STF/MS | CF88:ART.86, CF88:ART.86:PAR.1:INC.II, CF88:ART.52:INC.I | PROMOTE_RECOMMENDED | HUMAN_APPROVED | O MS 21564 (mérito, caso Collor) interpreta o caput do art. 86: a Câmara faz juízo político de admissibilidade. **Provisório (STF:ADPF:378)** — natureza: MS 21564: mérito; ADPF 378: medida cautelar do Plenário (com ED); última verificação: 2026-10-17; gatilho: JULGAMENTO_DE_MERITO_OU_EXTINCAO; prazo: 180 dias. |
| 4 | J0-BL-068 | CF88:ART.86:PAR.3 | ADI 978; Inq 672 | STF/ADI, STF/INQ | CF88:ART.86:PAR.3, CF88:ART.86:PAR.4 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Divisão por alvo: a ADI 978 vai para o § 3º (imunidade à prisão cautelar, exclusiva do Presidente) e o Inq 672 QO para o § 4º. |

### Promoções provisórias (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 5 | J0-BL-072 | CF88:ART.96:INC.III | Rcl 84738 | STF/RCL | CF88:ART.96:INC.III | PROMOTE_PROVISIONAL_RECOMMENDED | HUMAN_APPROVED | Pertinente ao art. 96, III, mas a própria ementa diz que é provisória e depende do Tema 1147. **Provisório** — natureza: orientação de Turma condicionada ao Tema 1147 (RG, pendente) ou a pronunciamento do Plenário; última verificação: 2026-10-17; gatilho: JULGAMENTO_DO_TEMA_1147_OU_PLENARIO; prazo: 90 dias. |

## Batch06 (MEDIUM) — `J2_MEDIUM_BACKLOG/J2_BATCH06_DECISIONS.json`

### Promoções (5)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 1 | J0-BL-116 | CF88:ART.114:PAR.3 | ADI 3392 | STF/ADI | CF88:ART.114:PAR.3 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | O § 3º (legitimidade do MPT para o dissídio na greve em atividade essencial) foi objeto expresso e foi declarado constitucional. |
| 2 | J0-BL-117 | CF88:ART.114:PAR.3 | ADI 3432 | STF/ADI | CF88:ART.114:PAR.3 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Mesmo julgamento e mesmo escopo do J0-BL-116: um único vínculo pelo registro conjunto. |
| 3 | J0-BL-144 | CF88:ART.198 | ADPF 672 | STF/ADPF | CF88:ART.198 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Julgado de mérito (o referendo foi convertido) sobre o federalismo sanitário: a União coordena, mas não afasta medidas de Estados e Municípios. |
| 4 | J0-BL-002 | CF88:ART.5:INC.XVI | Tema 855 | STF/RG | CF88:ART.5:INC.XVI | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Tese vinculante sobre o aviso prévio da liberdade de reunião, exatamente o objeto do art. 5º, XVI. |
| 5 | J0-BL-004 | CF88:ART.5:INC.LV | SV 5 | STF/SV | CF88:ART.5:INC.LV | PROMOTE_RECOMMENDED | HUMAN_APPROVED | SV cuja referência legislativa oficial é o art. 5º, LV (ampla defesa). |

### Realocações (2)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 6 | J0-BL-102 | CF88:ART.114 | ADI 3392 | STF/ADI | CF88:ART.114 → CF88:ART.114:PAR.2, CF88:ART.114:PAR.3 | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | A anotação no caput do art. 114 é a genérica da EC 45; o julgado atinge os §§ 2º (comum acordo no dissídio coletivo) e 3º (MPT na greve em atividade essencial). |
| 7 | J0-BL-103 | CF88:ART.114 | ADI 3432 | STF/ADI | CF88:ART.114 → CF88:ART.114:PAR.2, CF88:ART.114:PAR.3 | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | Mesma situação do J0-BL-102 (mesmo julgamento e mesma ementa): um único registro conjunto cobre os dois. |

### Rejeições (falso positivo) (3)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 8 | J0-BL-086 | CF88:ART.102 | ADI 3392 | STF/ADI | — | REJECT_FALSE_POSITIVE_RECOMMENDED | HUMAN_APPROVED | Falso positivo da anotação genérica da EC 45/2004, o mesmo padrão dos arts. 92 e 98 rejeitados no Batch01. |
| 9 | J0-BL-088 | CF88:ART.102:PAR.2 | ADI 3392 | STF/ADI | — | REJECT_FALSE_POSITIVE_RECOMMENDED | HUMAN_APPROVED | Falso positivo da anotação genérica da EC 45/2004; a ADI 3392 não trata do efeito vinculante. |
| 10 | J0-BL-111 | CF88:ART.114:PAR.1 | ADI 3432 | STF/ADI | — | REJECT_FALSE_POSITIVE_RECOMMENDED | HUMAN_APPROVED | A ADI 3432 não tratou do § 1º do art. 114; o vínculo foi gerado pela proximidade com os §§ 2º e 3º. |

## Batch07 (MEDIUM) — `J2_MEDIUM_BACKLOG/J2_BATCH07_DECISIONS.json`

### Promoções (6)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 1 | J0-BL-011 | CF88:ART.7:INC.XXVI | Tema 1046 | STF/RG | CF88:ART.7:INC.XXVI | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Tese central sobre o reconhecimento das convenções e acordos coletivos (art. 7º, XXVI): o negociado prevalece, respeitados os direitos absolutamente indisponíveis. |
| 2 | J0-BL-031 | CF88:ART.21:INC.XVI | ADI 2404 | STF/ADI | CF88:ART.21:INC.XVI | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Interpreta diretamente o art. 21, XVI: a classificação indicativa é informativa e não autoriza censura nem condiciona a exibição. |
| 3 | J0-BL-063 | CF88:ART.63 | ADI 3114 | STF/ADI | CF88:ART.63 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Firma os dois limites do poder de emenda: pertinência temática e não aumento de despesa. |
| 4 | J0-BL-075 | CF88:ART.100 | ADI 4425 | STF/ADI | CF88:ART.100 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Mesma política do Tema 558 (J2B.1) e do Tema 594: as partes históricas do julgado ficam no art. 100, com nota temporal. |
| 5 | J0-BL-006 | CF88:ART.5:INC.LXVII | SV 25 | STF/SV | CF88:ART.5:INC.LXVII | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Informação indispensável no próprio inciso LXVII: o texto ainda prevê a prisão do depositário infiel, mas ela é ilícita. |
| 6 | J0-BL-017 | CF88:ART.14:PAR.5 | Tema 1229 | STF/RG | CF88:ART.14:PAR.5 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Tese específica sobre a contagem de mandato para a reeleição do art. 14, § 5º. |

### Realocações (3)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 7 | J0-BL-064 | CF88:ART.63 | ADI 2681 | STF/ADI | CF88:ART.63 → CF88:ART.63:INC.I | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | A recomendação citava a MC; o mérito (2018) a substituiu e decide especificamente o inciso I do art. 63, onde o Tema 686 já está instalado. |
| 8 | J0-BL-005 | CF88:ART.5:INC.LVII | Tema 1068 | STF/RG | CF88:ART.5:INC.LVII → CF88:ART.5:INC.XXXVIII | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | A tese se apoia na soberania dos veredictos (art. 5º, XXXVIII, c). |
| 9 | J0-BL-013 | CF88:ART.8:INC.IV | Tema 935 | STF/RG | CF88:ART.8:INC.IV → CF88:ART.7:INC.XXVI | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | O art. 8º, IV trata da contribuição confederativa (SV 40, já instalada ali). |

### Já cobertas (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 10 | J0-BL-065 | CF88:ART.63 | Tema 686 | STF/RG | — | ALREADY_COVERED | HUMAN_APPROVED | O Tema 686 já está instalado no dispositivo exato (CF88:ART.63:INC.I, base de 261). |

## Batch08 (MEDIUM) — `J2_MEDIUM_BACKLOG/J2_BATCH08_DECISIONS.json`

### Promoções (4)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 1 | J0-BL-062 | CF88:ART.62:PAR.6 | MS 27931 | STF/MS | CF88:ART.62:PAR.6 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Precedente do Plenário que define o alcance do trancamento de pauta por MP (art. 62, § 6º). |
| 2 | J0-BL-055 | CF88:ART.53:CAPUT | Inq 4781 | STF/INQ | CF88:ART.53:CAPUT | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Precedente do Plenário sobre o limite da imunidade material (nexo com a função). |
| 3 | J0-BL-105 | CF88:ART.114:INC.I | ADI 3395 | STF/ADI | CF88:ART.114:INC.I | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Interpretação conforme do inciso I: a Justiça do Trabalho não julga causas estatutárias. |
| 4 | J0-BL-123 | CF88:ART.142 | ADI 6457 | STF/ADI | CF88:ART.142 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Julgado de 2024 que interpreta diretamente o art. 142: as Forças Armadas não exercem poder moderador e sua missão é limitada. |

### Realocações (2)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 5 | J0-BL-020 | CF88:ART.15 | Súmula 9 TSE | TSE/SUMULA | CF88:ART.15 → CF88:ART.15:INC.III | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | Súmula do TSE cuja referência é o inciso III do art. 15 (condenação criminal), e não o artigo inteiro. |
| 6 | J0-BL-104 | CF88:ART.114 | ADI 3395; ADI 3684 | STF/ADI | CF88:ART.114 → CF88:ART.114:INC.I, CF88:ART.114:INC.IV, CF88:ART.114:INC.IX | REALLOCATE_RECOMMENDED | HUMAN_APPROVED | Do caput para os incisos que os julgados interpretam: ADI 3395 no inciso I (estatutários); ADI 3684 nos incisos I, IV e IX (sem competência penal). |

### Rejeições (não material) (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 7 | J0-BL-071 | CF88:ART.93:INC.XII | ADI 3085 | STF/ADI | — | REJECT_NOT_MATERIAL_RECOMMENDED | HUMAN_APPROVED | Questão de ordem que julgou a ação prejudicada; não há tese de mérito sobre o art. 93, XII (mesma lógica do MS 34418). |

### Duplicatas (2)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 8 | J0-BL-056 | CF88:ART.53:CAPUT | Pet 7174 | STF/PET | — | DUPLICATE_RECOMMENDATION | HUMAN_APPROVED | Mesma tese do Inq 4781 Ref (item anterior), que é do Plenário. |
| 9 | J0-BL-059 | CF88:ART.53:PAR.1 | Inq 4787 | STF/INQ | — | DUPLICATE_RECOMMENDATION | HUMAN_APPROVED | Mesmo julgamento e mesmo escopo do HC 232627, já ratificado no Batch02 (SAME_JUDGMENT_SAME_SCOPE). |

### Não resolvidas (fonte externa) (1)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 10 | J0-BL-001 | CF88:ART.5:INC.X | Súmula 403 STJ | STJ/SUMULA | — | UNRESOLVED_EXTERNAL | UNRESOLVED_EXTERNAL | A fonte oficial do STJ bloqueou o acesso com um desafio anti-robô, que não foi contornado (regra de segurança). |

## Batch09 (MEDIUM) — `J2_MEDIUM_BACKLOG/J2_BATCH09_DECISIONS.json`

### Promoções (5)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 1 | J0-BL-066 | CF88:ART.84:INC.XII | ADPF 964 | STF/ADPF | CF88:ART.84:INC.XII | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Precedente de mérito do Pleno sobre os limites do indulto presidencial (art. 84, XII): o indulto é controlável por desvio de finalidade e não alcança os efeitos secundários da pena. |
| 2 | J0-BL-121 | CF88:ART.129 | Tema 184 | STF/RG | CF88:ART.129 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Tema central das funções do MP (art. 129). |
| 3 | J0-BL-124 | CF88:ART.142:PAR.2 | HC 70648 | STF/HC | CF88:ART.142:PAR.2 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | Precedente clássico que delimita a vedação do § 2º: cabe HC para examinar a legalidade da punição disciplinar militar, não o mérito. |
| 4 | J0-BL-130 | CF88:ART.150:PAR.7 | Tema 201; ADI 2777 | STF/ADI, STF/RG | CF88:ART.150:PAR.7 | PROMOTE_RECOMMENDED | HUMAN_APPROVED | O Tema 201 e a ADI 2777 foram julgados juntos em outubro de 2016 e fixam a mesma orientação sobre o § 7º: é devida a restituição quando a base de cálculo efetiva é menor que a presumida. |
| 5 | J0-BL-132 | CF88:ART.155:PAR.2:INC.VII | Tema 1093 | STF/RG | CF88:ART.155:PAR.2:INC.VII | PROMOTE_RECOMMENDED | HUMAN_APPROVED | O DIFAL instituído pela EC 87/2015 depende de lei complementar. |

### Já cobertas (3)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 6 | J0-BL-112 | CF88:ART.114:PAR.1 | Tema 841; ADI 3423; ADI 3392 | STF/ADI, STF/RG | — | ALREADY_COVERED | HUMAN_APPROVED | O § 1º (arbitragem) não é objeto de nenhum dos precedentes: a anotação oficial do § 1º não remete a eles. |
| 7 | J0-BL-170 | ADCT:ART.107-A | ADI 7064; MI 7300 | STF/ADI, STF/MI | — | ALREADY_COVERED | HUMAN_APPROVED | A ADI 7064 já foi ratificada no ADCT 107-A (Batch02/J2E, rótulo "ADI 7064"). |
| 8 | J0-BL-070 | CF88:ART.93:INC.I | Tema 509; ADI 3460; MS 28226 | STF/ADI, STF/MS, STF/RG | — | ALREADY_COVERED | HUMAN_APPROVED | O Tema 509 já está instalado em CF88:ART.93:INC.I (base de 261). |

### Duplicatas (2)

| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |
|---|---|---|---|---|---|---|---|---|
| 9 | J0-BL-145 | CF88:ART.198 | ADPF 672 | STF/ADPF | — | DUPLICATE_RECOMMENDATION | HUMAN_APPROVED | Mesmo target (CF88:ART.198) e mesmo precedente da J0-BL-144, já proposta no Batch06 (PROMOTE). |
| 10 | J0-BL-078 | CF88:ART.100 | ADI 4425; ADI 7047; ADI 7064 | STF/ADI | — | DUPLICATE_RECOMMENDATION | HUMAN_APPROVED | Os três precedentes já estão tratados: a ADI 4425 no art. 100 foi proposta no Batch06 (J0-BL-075, com nota temporal) e está instalada nos §§ 9º e 12 (J2C); a ADI 7064 está instalada no § 9º (J2C); o par 7047/7064 foi ratificado no § 11 e no ADCT 101, § 5º (Batch02/J2E). |

## Reconciliação de estados (Parte C)

Recomendações, decisões, relações, precedentes e targets **não** são somados entre si.

| Campo | Estado | Valor |
|---|---|---|
| PHYSICAL_RELATIONS | PHYSICALLY_INSTALLED (J2C, CURRENT_VISIBLE) | 261 relações / 160 targets |
| RATIFIED_HOST_ONLY_RELATIONS | EDITORIALLY_APPROVED_HOST_ONLY (Batch02 → J2E e Batches 03–09 → J2F; nada instalado) | 54 relações normalizadas (Batch02: 8; Batches 03–09: 46) · grupo A, firmware atual: 38 · grupo B, firmware genérico: 16 |
| RATIFIED_RECOMMENDATIONS | HUMAN_APPROVED | 54 de 55 recomendações (39 decisões que vinculam) |
| AWAITING_RATIFICATION_RECOMMENDATIONS | UNAPPROVED_RESEARCH_PROPOSAL | 0 |
| UNRESOLVED_RECOMMENDATIONS | não resolvidas | 1 (J0-BL-001) |
| IN_RESEARCH | em pesquisa | 0 (Batch09 concluído nesta operação; nenhum lote em pesquisa. Batch10 NÃO iniciado.) |
| NOT_RESEARCHED | não pesquisadas | 69 pendentes (LOW 27, MEDIUM 42) |
| UNRATIFIED_RELATIONS_PUBLISHED | — | **0** |

**Decisões por tipo (Batches 03–09; classificação preservada na ratificação):**

| Decisão | Quantidade |
|---|---:|
| PROMOTE_RECOMMENDED | 29 |
| PROMOTE_PROVISIONAL_RECOMMENDED | 2 |
| REALLOCATE_RECOMMENDED | 8 |
| REJECT_FALSE_POSITIVE_RECOMMENDED | 3 |
| REJECT_TEMPORAL_MISMATCH_RECOMMENDED | 1 |
| REJECT_NOT_MATERIAL_RECOMMENDED | 3 |
| ALREADY_COVERED | 4 |
| DUPLICATE_RECOMMENDATION | 4 |
| UNRESOLVED_EXTERNAL | 1 |

O limite superior bruto era de 58 pares *target × precedente*. Após a normalização J2F (divisão por alvo, registro conjunto da ADI 3423 e deduplicação) ficam 46 relações novas dos Batches 03–09 (`LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json`).
