# ENTENDA CF — PRODUCTION BATCH 03 (arts. 18 a 24)

Missão ENTENDA-CF-A4 · base `35b7aaa1` (tag `entenda-cf-batch02-approved-2026-09-28`) · as_of 2026-09-28

**Status:** APROVADO (HUMAN_APPROVED_T1) na A5 — ver seção "A5" ao final. As seções abaixo descrevem o lote como entregue à revisão.

## Números

| item | valor |
|---|---|
| targets avaliados | 134 |
| CURRENT | 134 |
| REVOKED | 0 |
| explicações selecionadas | 46 (soft 25–45, hard cap 55: OUTSIDE_JUSTIFIED) |
| OVERVIEW | 7 |
| DEVICE | 6 |
| BLOCK | 26 |
| ITEM | 7 |
| NO_SEPARATE_EXPLANATION | 88 |
| média de palavras | 189 |
| média de bytes no payload | 1731 |
| maior explicação | `CF88:ART.21:INC.XII` (244 palavras, 2407 bytes) |
| linhas no lookup | 105 |
| warnings | 28 {"ABSOLUTE_CLAIM": 1, "EXAMPLE_REQUIREMENT_LANGUAGE": 7, "NEAR_COPY_OF_OFFICIAL_TEXT": 14, "PARENT_REPETITION": 4, "TERM_NOT_USED": 2} |

Justificativa (46 > 45): 46 explicacoes novas (uma acima da meta de 45, abaixo do teto de 55). Os arts. 21 e 22 somam 56 incisos com alineas; mesmo com 16 blocos de irmaos cobrindo 42 dispositivos, a distincao entre competencia material (art. 21) e legislativa privativa (art. 22), a delegacao do art. 22, paragrafo unico, e o mecanismo dos §§ 1º a 4º do art. 24 exigem explicacoes proprias. Fundir mais misturaria categorias que o lote deve distinguir.

Avisos informativos mantidos (quase-copia em listas de materias, linguagem de exemplo, repeticao do pai). Corrigidos nesta etapa: 20 explicacoes com copia literal >10 palavras do texto oficial (bloqueio ENTENDA_COPIES_OFFICIAL_TEXT) e 1 remissao a jurisprudencia no corpo (21.XVI).

## Estratégia por artigo

| artigo | targets | OV | DEV | BLOCK | ITEM | NO_SEP |
|---|---|---|---|---|---|---|
| ART.18 | 6 | 1 | 2 | 0 | 0 | 3 |
| ART.19 | 5 | 1 | 0 | 0 | 0 | 4 |
| ART.20 | 15 | 1 | 2 | 2 | 1 | 9 |
| ART.21 | 38 | 1 | 0 | 7 | 3 | 27 |
| ART.22 | 33 | 1 | 1 | 8 | 3 | 20 |
| ART.23 | 15 | 1 | 1 | 3 | 0 | 10 |
| ART.24 | 22 | 1 | 0 | 6 | 0 | 15 |

- **ART.18:** Visao geral (entes, autonomia x soberania, Capital, Territorios) + DEVICE § 3º (Estados: plebiscito + lei complementar) + DEVICE § 4º (Municipios: lei estadual, periodo em LC federal, EVM, plebiscito). §§ 1º e 2º na visao geral.
- **ART.19:** Uma visao geral cobre caput e incisos I-III: vedacoes de estabelecer/subvencionar/embaracar cultos, ressalva de colaboracao de interesse publico, fe dos documentos publicos, vedacao de distincoes entre brasileiros. Laicidade como neutralidade, nunca "Estado ateu". Tema 1157 excluido por mismatch material.
- **ART.20:** Visao geral (bem pertencente a Uniao x competencia da Uniao; I e II na visao geral) + BLOCK III/IV/VI/VII (aguas, ilhas, mar territorial, terrenos de marinha) + BLOCK V/VIII/IX/X (recursos naturais, energia hidraulica, minerios, cavidades e sitios arqueologicos) + ITEM XI (terras indigenas) + DEVICE § 1º (participacao/compensacao) + DEVICE § 2º (faixa de fronteira).
- **ART.21:** Visao geral "fazer, nao legislar" + 7 BLOCKs semanticos: I-VI relacoes internacionais/defesa/estados de excecao; VII-VIII moeda e fiscalizacao financeira; IX/XV/XX/XXI planejamento, estatistica, diretrizes urbanas e viacao; X-XII servicos federais (correios, telecom, radiodifusao, energia, transportes, portos); XIII/XIV/XXII instituicoes do DF e Territorios e policia de fronteiras; XVIII-XIX calamidades e recursos hidricos; XXIII atividade nuclear (alineas). ITEMs XVI (classificacao indicativa), XVII (anistia), XXVI (protecao de dados). XXIV e XXV sem explicacao propria.
- **ART.22:** Visao geral "legislar; privativa nao e indelegavel" + ITEM I (ramos do direito) + 8 BLOCKs: II-III desapropriacao/requisicoes; IV/V/IX/X/XI aguas, energia, comunicacoes, transportes; VI/VII/VIII/XIX/XX moeda, credito, comercio, poupanca, consorcios; XII/XXVI minerios e atividades nucleares; XIII-XV nacionalidade, indigenas, estrangeiros; XVI/XXIII/XXIV profissoes, seguridade, diretrizes da educacao; XVII/XXI/XXII/XXVIII organizacao judiciaria do DF, forcas de seguranca, defesa; XVIII/XXV sistemas de informacao e registros publicos. ITEMs XXVII (licitacao) e XXX (dados) + DEVICE paragrafo unico (delegacao por LC). XXIX sem explicacao propria.
- **ART.23:** Visao geral "comum = administrativa, todos os entes, nao e legislar" + 3 BLOCKs (saude/assistencia/moradia/pobreza; patrimonio cultural/acesso a cultura; meio ambiente/recursos) + DEVICE paragrafo unico (leis complementares de cooperacao). I e XII na visao geral.
- **ART.24:** Visao geral "concorrente = legislativa, Uniao/Estados/DF, Municipio via art. 30" + 4 BLOCKs de materias + BLOCK §§ 1º-2º (normas gerais x suplementar) + BLOCK §§ 3º-4º (competencia plena e suspensao da eficacia, nao revogacao).

## Distinção central

- **Art. 21:** competências materiais/administrativas da União (fazer, explorar, organizar, fiscalizar).
- **Art. 22:** competências legislativas privativas da União; parágrafo único: lei complementar pode autorizar os Estados a legislar sobre questões específicas (privativa ≠ indelegável).
- **Art. 23:** competência comum administrativa de União, Estados, DF e Municípios; parágrafo único: leis complementares de cooperação.
- **Art. 24:** competência legislativa concorrente (União: normas gerais; Estados/DF: suplementar; sem lei federal: competência plena; lei federal superveniente **suspende a eficácia** da lei estadual no que lhe for contrário — não revoga).

Exemplo art. 21 × art. 22: Art. 21, XI: a Uniao EXPLORA os servicos de telecomunicacoes (diretamente ou por concessao; ex.: atuacao de agencia reguladora). Art. 22, IV: a Uniao LEGISLA sobre telecomunicacoes (Congresso Nacional). Lei municipal sobre telecomunicacoes invade o art. 22, IV.

Lookup coberto: `CF88:ART.22:INC.V` → COVERED_BY_BLOCK -> CF88:ART.22:INC.IV; `CF88:ART.24:PAR.4` → COVERED_BY_BLOCK -> CF88:ART.24:PAR.3

## Jurisprudência (camada externa; nada vinculado no corpo)

READY_TO_LINK 10 · IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION 1 · PENDING_EXTERNAL_INGESTION 5 · MATERIAL_MISMATCH_EXCLUDED 1

| target | referência | status |
|---|---|---|
| `CF88:ART.18:PAR.4` | STF Tema 400 (Repercussão Geral) — plebiscito na criação de Municípios | READY_TO_LINK |
| `CF88:ART.18:PAR.4` | STF — Municípios criados sem a lei complementar federal (omissão legislativa) | PENDING_EXTERNAL_INGESTION |
| `CF88:ART.19` | Vínculo local existente (STF Tema 1157) — verificar pertinência ao art. 19 da CF | MATERIAL_MISMATCH_EXCLUDED |
| `CF88:ART.19` | STF — ensino religioso em escolas públicas e laicidade | PENDING_EXTERNAL_INGESTION |
| `CF88:ART.20:INC.VII` | STF Tema 676 (Repercussão Geral) — terrenos de marinha após a EC 46/2005 | READY_TO_LINK |
| `CF88:ART.20:INC.XI` | STF Tema 1031 (Repercussão Geral) — demarcação de terras indígenas | IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION |
| `CF88:ART.21:INC.XII:AL.b` | STF Tema 774 (Repercussão Geral) — norma estadual e concessionária de energia elétrica | READY_TO_LINK |
| `CF88:ART.21:INC.XVI` | STF — classificação indicativa e horários de exibição | PENDING_EXTERNAL_INGESTION |
| `CF88:ART.22:INC.I` | STF Tema 1246 (Repercussão Geral) — norma penal em branco complementada por atos dos entes | READY_TO_LINK |
| `CF88:ART.22:INC.IV` | STF Tema 1235 (Repercussão Geral) — lei municipal e telecomunicações | READY_TO_LINK |
| `CF88:ART.22:INC.IV` | STF Tema 919 (Repercussão Geral) — taxa de fiscalização de torres e antenas | READY_TO_LINK |
| `CF88:ART.22:INC.VI` | STF Tema 5 (Repercussão Geral) — sistema monetário (Lei 8.880/1994) | READY_TO_LINK |
| `CF88:ART.22:INC.XI` | STF Tema 967 (Repercussão Geral) — transporte individual por aplicativo | READY_TO_LINK |
| `CF88:ART.22:INC.XX` | STF — consórcios e sorteios e exploração de loterias pelos Estados | PENDING_EXTERNAL_INGESTION |
| `CF88:ART.22:INC.XXI` | STF Tema 1177 (Repercussão Geral) — normas gerais sobre inatividades e pensões de militares estaduais | READY_TO_LINK |
| `CF88:ART.23:PAR.UNICO` | STF — cooperação federativa em matéria ambiental (lei complementar de cooperação) | PENDING_EXTERNAL_INGESTION |
| `CF88:ART.24:INC.VI` | STF Tema 145 (Repercussão Geral) — Município e legislação ambiental no interesse local | READY_TO_LINK |

**Tema 1157 × art. 19:** o vínculo local aponta para o art. 19, mas a tese local trata do reenquadramento de servidor admitido sem concurso (estabilidade excepcional do art. 19 do **ADCT**). Não trata de laicidade. Status `MATERIAL_MISMATCH_EXCLUDED`; não deve ser vinculado ao art. 19 da CF.

**Tema 1031 × art. 20, XI:** a tese local trata de demarcação de terras indígenas, mas o vínculo curado está em `CF88:ART.16`, não no target; fica `IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION` até curadoria do vínculo.

## Mudança no motor

- production_batch.py: status MATERIAL_MISMATCH_EXCLUDED (declarado na spec via material_mismatch, confirmado pela tese local; falha se a tese local contiver o assunto). Contador so emitido quando > 0: Batch 01/02 byte-identical.

## Determinismo e testes

- Batch 03: BYTE_IDENTICAL (2 builds)
- rebuild_all: BYTE_IDENTICAL (2 execucoes completas)
- Batch 01 final: inalterado vs HEAD; Batch 02 final: inalterado vs HEAD
- ENTENDA: 67/67 PASS (55 + 12 do Batch 03); LEGAL_TARGET_ID: 47/47 PASS

## Explicações

| target | role | cobre | título |
|---|---|---|---|
| `CF88:ART.18` | OVERVIEW | — | Art. 18 — Organização político-administrativa e autonomia dos entes |
| `CF88:ART.18:PAR.3` | DEVICE | — | Art. 18, § 3º — Criação e alteração de Estados |
| `CF88:ART.18:PAR.4` | DEVICE | — | Art. 18, § 4º — Criação, incorporação, fusão e desmembramento de Municípios |
| `CF88:ART.19` | OVERVIEW | — | Art. 19 — Vedações federativas: laicidade, fé pública e igualdade entre brasileiros |
| `CF88:ART.20` | OVERVIEW | — | Art. 20 — Bens da União |
| `CF88:ART.20:INC.III` | BLOCK | INC.IV, INC.VI, INC.VII | Art. 20, incisos III, IV, VI e VII — Águas, ilhas, mar territorial e terrenos de marinha |
| `CF88:ART.20:INC.V` | BLOCK | INC.VIII, INC.IX, INC.X | Art. 20, incisos V, VIII, IX e X — Recursos naturais, minerais e patrimônio arqueológico |
| `CF88:ART.20:INC.XI` | ITEM | — | Art. 20, inciso XI — Terras tradicionalmente ocupadas pelos índios |
| `CF88:ART.20:PAR.1` | DEVICE | — | Art. 20, § 1º — Participação e compensação pela exploração de recursos |
| `CF88:ART.20:PAR.2` | DEVICE | — | Art. 20, § 2º — Faixa de fronteira |
| `CF88:ART.21` | OVERVIEW | — | Art. 21 — Competências materiais da União |
| `CF88:ART.21:INC.I` | BLOCK | INC.II, INC.III, INC.IV, INC.V, INC.VI | Art. 21, incisos I, II, III, IV, V e VI — Relações internacionais, defesa e estados de exceção |
| `CF88:ART.21:INC.VII` | BLOCK | INC.VIII | Art. 21, incisos VII e VIII — Moeda e fiscalização financeira |
| `CF88:ART.21:INC.IX` | BLOCK | INC.XV, INC.XX, INC.XXI | Art. 21, incisos IX, XV, XX e XXI — Planejamento nacional, informação e diretrizes urbanas e de viação |
| `CF88:ART.21:INC.XII` | BLOCK | INC.X, INC.XI | Art. 21, incisos X, XI e XII — Serviços públicos federais: correios, telecomunicações, radiodifusão, energia, transportes e portos |
| `CF88:ART.21:INC.XIII` | BLOCK | INC.XIV, INC.XXII | Art. 21, incisos XIII, XIV e XXII — Instituições do Distrito Federal e dos Territórios e polícia de fronteiras |
| `CF88:ART.21:INC.XVI` | ITEM | — | Art. 21, inciso XVI — Classificação indicativa |
| `CF88:ART.21:INC.XVII` | ITEM | — | Art. 21, inciso XVII — Anistia |
| `CF88:ART.21:INC.XVIII` | BLOCK | INC.XIX | Art. 21, incisos XVIII e XIX — Calamidades públicas e recursos hídricos |
| `CF88:ART.21:INC.XXIII` | BLOCK | — | Art. 21, inciso XXIII — Atividade nuclear |
| `CF88:ART.21:INC.XXVI` | ITEM | — | Art. 21, inciso XXVI — Organização e fiscalização da proteção de dados |
| `CF88:ART.22` | OVERVIEW | — | Art. 22 — Competência legislativa privativa da União |
| `CF88:ART.22:INC.I` | ITEM | — | Art. 22, inciso I — Ramos do direito de competência legislativa da União |
| `CF88:ART.22:INC.II` | BLOCK | INC.III | Art. 22, incisos II e III — Desapropriação e requisições |
| `CF88:ART.22:INC.IV` | BLOCK | INC.V, INC.IX, INC.X, INC.XI | Art. 22, incisos IV, V, IX, X e XI — Águas, energia, comunicações e transportes |
| `CF88:ART.22:INC.VI` | BLOCK | INC.VII, INC.VIII, INC.XIX, INC.XX | Art. 22, incisos VI, VII, VIII, XIX e XX — Moeda, crédito, comércio, poupança e consórcios |
| `CF88:ART.22:INC.XII` | BLOCK | INC.XXVI | Art. 22, incisos XII e XXVI — Minérios, metalurgia e atividades nucleares |
| `CF88:ART.22:INC.XIII` | BLOCK | INC.XIV, INC.XV | Art. 22, incisos XIII, XIV e XV — Nacionalidade, populações indígenas e estrangeiros |
| `CF88:ART.22:INC.XVI` | BLOCK | INC.XXIII, INC.XXIV | Art. 22, incisos XVI, XXIII e XXIV — Emprego e profissões, seguridade social e diretrizes da educação |
| `CF88:ART.22:INC.XVII` | BLOCK | INC.XXI, INC.XXII, INC.XXVIII | Art. 22, incisos XVII, XXI, XXII e XXVIII — Organização judiciária do DF e Territórios, forças de segurança e defesa |
| `CF88:ART.22:INC.XVIII` | BLOCK | INC.XXV | Art. 22, incisos XVIII e XXV — Sistemas nacionais de informação e registros públicos |
| `CF88:ART.22:INC.XXVII` | ITEM | — | Art. 22, inciso XXVII — Normas gerais de licitação e contratação |
| `CF88:ART.22:INC.XXX` | ITEM | — | Art. 22, inciso XXX — Legislação sobre proteção de dados pessoais |
| `CF88:ART.22:PAR.UNICO` | DEVICE | — | Art. 22, parágrafo único — Delegação aos Estados por lei complementar |
| `CF88:ART.23` | OVERVIEW | — | Art. 23 — Competência comum |
| `CF88:ART.23:INC.II` | BLOCK | INC.VIII, INC.IX, INC.X | Art. 23, incisos II, VIII, IX e X — Saúde, assistência, pessoas com deficiência, moradia, abastecimento e combate à pobreza |
| `CF88:ART.23:INC.III` | BLOCK | INC.IV, INC.V | Art. 23, incisos III, IV e V — Patrimônio cultural, cultura, educação e ciência |
| `CF88:ART.23:INC.VI` | BLOCK | INC.VII, INC.XI | Art. 23, incisos VI, VII e XI — Meio ambiente e recursos naturais |
| `CF88:ART.23:PAR.UNICO` | DEVICE | — | Art. 23, parágrafo único — Cooperação entre os entes |
| `CF88:ART.24` | OVERVIEW | — | Art. 24 — Competência legislativa concorrente |
| `CF88:ART.24:INC.I` | BLOCK | INC.II, INC.III, INC.IV | Art. 24, incisos I, II, III e IV — Direito tributário, financeiro, econômico e urbanístico, orçamento, juntas comerciais e custas |
| `CF88:ART.24:INC.V` | BLOCK | INC.VI, INC.VII, INC.VIII | Art. 24, incisos V, VI, VII e VIII — Consumo, meio ambiente, patrimônio cultural e responsabilidade por danos |
| `CF88:ART.24:INC.IX` | BLOCK | INC.XII, INC.XIV, INC.XV | Art. 24, incisos IX, XII, XIV e XV — Educação, cultura, ciência, previdência, saúde, pessoas com deficiência, infância e juventude |
| `CF88:ART.24:INC.X` | BLOCK | INC.XI, INC.XIII, INC.XVI | Art. 24, incisos X, XI, XIII e XVI — Juizados, procedimentos processuais, assistência jurídica e polícias civis |
| `CF88:ART.24:PAR.1` | BLOCK | PAR.2 | Art. 24, §§ 1º e 2º — Normas gerais da União e competência suplementar dos Estados |
| `CF88:ART.24:PAR.3` | BLOCK | PAR.4 | Art. 24, §§ 3º e 4º — Competência plena dos Estados e suspensão da eficácia |

## Arquivos (sha256)

- `ENTENDA_ENGINE/derived/production_batch_03/BATCH_03_DRAFTS.json` `e3c084f981f49cc7`
- `ENTENDA_ENGINE/derived/production_batch_03/BATCH_SPEC.json` `3ab3e5987b6ace25`
- `ENTENDA_ENGINE/derived/production_batch_03/CF88_BATCH_03.entenda.jsonl` `5dfc4f94fcc7432b`
- `ENTENDA_ENGINE/derived/production_batch_03/index/ENTENDA_BUILD_MANIFEST.json` `305ed948532d931d`
- `ENTENDA_ENGINE/derived/production_batch_03/index/ENTENDA_LOOKUP.IDX` `970765ad0387951b`
- `ENTENDA_ENGINE/derived/production_batch_03/index/ENTENDA_PAYLOAD.DAT` `728979fb6da92602`
- `ENTENDA_ENGINE/derived/production_batch_03/JURISPRUDENCE_LINK_RECOMMENDATIONS.json` `bd701814e0d83c3b`
- `ENTENDA_ENGINE/derived/production_batch_03/REVIEW_BATCH_03.md` `732dbb2d73ab2c39`
- `ENTENDA_ENGINE/derived/production_batch_03/SELECTION_REPORT.json` `e6b8834fd414c280`

Revisão humana: `ENTENDA_ENGINE/derived/production_batch_03/REVIEW_BATCH_03.md`. Nada foi commitado; art. 25 em diante não foi iniciado.

## A5 (2026-09-29): revisão humana aplicada

- Decisões: {'APPROVED': 14, 'APPROVED_AFTER_ADJUSTMENT': 35} · criadas pela revisão: `CF88:ART.21:INC.XXIV`, `CF88:ART.21:INC.XXV`, `CF88:ART.22:INC.XXIX`
- Total final: 49 explicações HUMAN_APPROVED_T1; 35 versões anteriores RETIRED; nenhuma PENDING.
- Targets: 134 avaliados, 134 CURRENT, 0 REVOKED.
- Classificação: {"BLOCK": 26, "DEVICE": 6, "ITEM": 10, "NO_SEPARATE_EXPLANATION": 85, "OVERVIEW": 7}
- Média de palavras 197; maior `CF88:ART.18:PAR.4` (219 palavras, 3097 bytes); warnings 26 {"ABSOLUTE_CLAIM": 1, "EXAMPLE_REQUIREMENT_LANGUAGE": 6, "NEAR_COPY_OF_OFFICIAL_TEXT": 14, "PARENT_REPETITION": 3, "TERM_NOT_USED": 2}.
- Jurisprudência: {"total": 18, "READY_TO_LINK": 11, "IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION": 0, "PENDING_EXTERNAL_INGESTION": 6, "MATERIAL_MISMATCH_EXCLUDED": 1}.
- Tema 1031: vínculo principal `CF88:ART.231`, correlato `CF88:ART.20:INC.XI`; vínculo local com `CF88:ART.16` excluído (falso positivo do art. 16.4 da Convenção 169 OIT) como overlay, sem editar as fontes.
- Tema 1157 × art. 19: segue `MATERIAL_MISMATCH_EXCLUDED`. ADI 2404 (art. 21, XVI) e Tema 793 (art. 23, II): fora do acervo local → `PENDING_EXTERNAL_INGESTION`.
- Notas temporais: `LC_230_2026_DESMEMBRAMENTO_INCORPORACAO_LIMITROFE` (CF88:ART.18:PAR.4, IN_EFFECT); `ANPD_AGENCIA_REGULADORA_LEI_15352_2026` (CF88:ART.21:INC.XXVI, IN_EFFECT).
- Fontes externas verificadas: LC 230/2026: Camara (texto original publicado; DOU 16/04/2026): art. 1º caput e §§ 1º-3º, art. 8º; Lei 15.352/2026 / MP 1.317/2025 (ANPD): gov.br/anpd (base juridica): agencia reguladora, rol da Lei 13.848/2019; EC 118/2022 (art. 21, XXIII, b e c): texto da Lei Seca local ja consolidado (comercializacao/producao de radioisotopos); LC 103/2000: ementa: autoriza Estados e DF a instituir piso salarial por aplicacao do paragrafo unico do art. 22; LC 140/2011: art. 13: licenciamento por um unico ente federativo; Lei 14.133/2021 e Lei 13.303/2016: citadas apenas na camada externa.
- Motor: production_batch.py: primary_target_id/correlated_target_id e excluded_local_links (overlay) na verificacao material; campos so emitidos quando presentes (Batch 01/02 byte-identical) | apply_batch_review.py: decisions_schema 2 (review_scope e hashes da evidencia original) | ENTENDA_T1_EDITORIAL_STANDARD.md §15: linguagem para iniciantes, dados institucionais so na camada externa, MATERIAL_MISMATCH_EXCLUDED e vinculos corrigidos
- Determinismo: production_batch_03_final e rebuild_all completos: BYTE_IDENTICAL em 2 execucoes; Batch 01/02 inalterados vs HEAD; evidencia do Batch 03 identica ao snapshot pre-revisao.
- Testes: ENTENDA 80/80 PASS (67 + 13 do Batch 03 final); LEGAL_TARGET_ID 47/47 PASS.
