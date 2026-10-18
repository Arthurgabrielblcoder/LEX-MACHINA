# Piloto de portabilidade — Código Civil (CC2002)

```
PORTABILITY_PILOT = PASS (motor de pesquisa portável; alertas: fonte STJ e firmware CF-only) · PILOT_NORM = CODIGO_CIVIL (CC2002)
CC_CANDIDATES_ANALYZED = 20 · CC_RELATIONS_PUBLISHED = 0 · CC_FILES_DEPLOYED = 0 · SD_CHANGED = NO · FIRMWARE_CHANGED = NO
CF_BASELINE = 315/198 (J2I_FROZEN_315_198, byte-idêntico) · CF_REGRESSION = 0 · STATUS DOS RESULTADOS = PORTABILITY_EVIDENCE
```

**Artefatos:**
- **Código:** `build_pilot_cc.py` (orquestração e métricas), `discovery_planalto.py` (adaptador de descoberta), `norm_profiles.py` (perfis e wrappers).
- **Evidências:** `pilot_cc/cc_pilot_evidence.py` (fontes oficiais capturadas), `pilot_cc/PLANALTO_CC2002_ANNOTATIONS.json`.
- **Resultado:** `pilot_cc/PORTABILITY_PILOT_CC.json`, com 20 candidatos, cada etapa medida.
- **Testes:** `tests/test_portability_pilot_cc.py`.
- **Auditoria de acoplamento:** `PORTABILITY_AUDIT.md`.

## Norma piloto

| Item | Valor |
|---|---|
| Norma | Lei 10.406/2002 (Código Civil), namespace já existente `CC2002` (Catálogo Mestre; índice do aparelho `CC2002_TARGET_INDEX.json`) |
| Versão | Texto compilado do Planalto baixado em 2026-10-18, sha256 `c50bf11c…`. O índice do aparelho é do corpus de 2026-09-29 |
| Estrutura | 2.077 artigos; 5.956 targets (539 parágrafos, 392 parágrafos únicos, 856 incisos, 14 alíneas); nenhuma anomalia de gramática |
| Conferência estrutural | O adaptador reproduz 3.856 de 3.878 dispositivos do índice. A diferença são revogações recentes (Lei 15.040/2024 etc.), portanto o corpus do aparelho já tem deriva temporal |

## Como os candidatos foram gerados (sem LLM como fonte)

1. **Acervo:** o projeto não tinha recomendações, anotações nem relações de jurisprudência para o CC; só o índice estrutural.
2. **Adaptador 1, anotações "Vide" do Planalto:** o mesmo tipo de fonte que alimentou parte do backlog da CF (fonte P1 da J2A). Resultado: 10 candidatos (arts. 20, 21, 186, 927, 1.790 e 1.829; ADI 4815, ADI 6792, ADI 7055, RE 646721, RE 878694).
3. **Adaptador 2, busca oficial do STF:** consulta `"do Código Civil" e "repercussão geral"`, com os 50 primeiros resultados capturados (sha `9e95fedf…`). Regra aplicada pelo código: Plenário + Tema + acórdão de mérito (sem sufixo "RG") + artigo do CC citado. Resultado: 10 candidatos (Temas 529, 1236, 932, 526, 1194, 809, 498).
4. **STJ:** o canal de descoberta foi tentado e bloqueado por desafio anti-robô, que não foi contornado.

**O conjunto não foi escolhido a dedo e cobre as situações pedidas:**

| Situação | Exemplos |
|---|---|
| Artigo simples | arts. 20, 21 |
| Parágrafo | 927, p.u.; 1.639, § 2º; 1.723, § 1º |
| Inciso | 1.641, II; 1.566, I |
| Artigo com muita jurisprudência | 1.790 (dois temas, duas fontes) |
| Artigo com pouca jurisprudência | 1.521, 206-A |
| Classes | ADI e RG/STF |
| Falso positivo | 1.521 |
| Realocações | cinco |
| Duplicatas | por alias Tema ↔ leading case e por julgamento conjunto ADI 6792/7055 |
| Questão temporal | 1.641, II e 206-A têm redação dada por lei, ambas anteriores aos julgamentos |

## Métricas (Fase N)

| Métrica | Valor |
|---|---|
| CANDIDATES_ANALYZED | **20** |
| Etapas automáticas | **133/140 (95%)**: descoberta 20/20, normalização de target 17/20, namespace 20/20, temporal 20/20, situação processual 16/20, duplicatas 20/20, fonte oficial 20/20 |
| Candidatos 100% automáticos | **9** |
| ITEMS_REQUIRING_HUMAN_JUDGMENT | **11** (realocação 3, julgamento conjunto 4, pertinência material 4) |
| ITEMS_BLOCKED_BY_SOURCE_ACCESS | **0** candidatos. O canal STJ inteiro ficou bloqueado, então nenhum candidato STJ chegou a existir |
| FALSE_POSITIVES_DETECTED | **1** (art. 1.521 no Tema 526, previdenciário) |
| REALLOCATIONS_DETECTED | **5**, das quais **2** o motor determinou sozinho: 927 → p.u. pelo parser de citação; 206 → 206-A pelo sufixo no texto oficial |
| Duplicatas | **4**: 2 automáticas (alias Tema ↔ RE) e 2 por julgamento conjunto, sinalizadas pelo texto oficial e confirmadas por humano |
| Alertas temporais | 0 (as redações de 1.641, II e 206-A são anteriores aos julgamentos) |
| Alertas falsos do auditor de namespace da CF | 19 de 20; eliminados pelo perfil |
| TOOLS_REUSED_WITHOUT_CHANGE | **4** (`target_id`, índice estrutural, `juris_types`, `status_signals`/`joint_scope`) |
| TOOLS_REUSED_AFTER_PARAMETERIZATION | **3** (`citation_parser`, `namespace_alerts`, `temporal_alerts`, via wrappers; nenhuma linha da CF mudou) |
| TOOLS_REQUIRING_NEW_CODE | **3** (`discovery_planalto`, `norm_profiles`, `build_pilot_cc`: 370 linhas, mais 138 de dados de evidência) |
| Ferramentas não reutilizáveis | 2 (validador de decisão com namespace fixo; descoberta via ENTENDA) |

**Avaliações do piloto:** PROMOTE 10 · REALLOCATE 5 · DUPLICATE 4 · REJECT_NOT_MATERIAL 1. Todas são `PORTABILITY_PILOT_ONLY` e nenhuma é HUMAN_APPROVED.

## Respostas

1. **Quanto do motor atual já é genérico?** O núcleo que roda por candidato já é. Das 9 ferramentas exercitadas, 4 rodaram sem mudança e 3 só com wrappers de perfil; nenhum módulo da CF foi alterado. Dos 45 scripts J2, 3 são genéricos e 7 parametrizáveis. Os outros 32 são instrumentos de rodadas físicas da CF, que por natureza não se reutilizam.
2. **Quanto ainda é específico da CF?** A descoberta (recomendações ENTENDA), o validador de decisões (namespace CF88/ADCT fixo), os exportadores e deploys da CF, e o firmware, onde a camada juris só consulta `CF88`. Além disso, a gramática de target não aceita alínea sem inciso. O CC não tem essa lacuna, mas CP, CPP, CTN e CLT têm.
3. **Quantas mudanças foram necessárias para processar o CC?** Nenhuma em código da CF. Foram necessários 3 módulos novos (370 linhas) e um arquivo de evidências. O adaptador do Planalto teve 2 defeitos corrigidos durante o piloto (atributo HTML no início do parágrafo; títulos herdando a posição do artigo anterior).
4. **Quantos candidatos foram processados automaticamente?** 9 de 20 de ponta a ponta. As etapas mecânicas foram 95% automáticas.
5. **Quantos exigiram julgamento humano?** 11 de 20, para granularidade do alvo, registro conjunto e pertinência. O mesmo tipo de julgamento existiu na CF, mas lá incluía também identificar o precedente: no Batch10, 8 de 10 recomendações não traziam identificador. No CC, os 20 chegaram já identificados pela fonte.
6. **Quais fontes externas são gargalos?** O **STJ**: anti-robô em todas as tentativas (Súmulas 403 e 203 e o canal do CC), e é o tribunal dominante para CC e CPC. TST (CLT) e TSE (CE) **não foram testados**. As anotações do Planalto rendem pouco em todos os códigos (5 a 71 por código). O STF funcionou bem: "A Constituição e o Supremo" (só para a CF), páginas de tema e busca de jurisprudência.
7. **O segundo arquivo tende a ser muito mais rápido que a CF?** Por candidato, sim, porque as etapas mecânicas e a identificação ficam automáticas. Pela norma inteira, não necessariamente: a cobertura do CC depende do STJ, e publicar exige firmware multinorma.
8. **Estimativa prudente de aceleração:** **2x–3x por candidato processado**, para a parte respaldada pelo STF. Não há dado que sustente 5x–10x. Sem acesso ao STJ, o universo alcançável do CC fica pequeno (no piloto, 18 pares distintos vindos de 2 canais STF).
9. **Devemos terminar toda a CF antes de avançar?** Não. O backlog restante da CF tem 59 itens, **todos sem identificador** (MEDIUM 30, LOW 29). O Batch10 rendeu 5 vínculos propostos em 10 itens, com 2 pendências e 1 rejeição, ou seja, retorno decrescente com custo alto de identificação manual.
10. **Qual norma processar em seguida?** O **Código Civil**, no escopo STF. Ele já tem namespace, índice do aparelho, perfil e adaptadores, e nenhuma lacuna de gramática. Em paralelo, decidir o canal STJ. Depois, CPC ou CE (também sem lacuna de gramática; CE depende do TSE, ainda não testado). CPP rendeu mais anotações (66), mas exige antes a extensão de gramática (43 alíneas sem inciso).

## Estimativa de escala (Fase O)

Estimativa qualitativa: as contagens vêm de `PLANALTO_DISCOVERY_YIELD_7_NORMS.json`, e o resto é inferência prudente.

| Norma | Esforço | Fator principal | Dados medidos |
|---|---|---|---|
| Código Civil | **MEDIUM** | STJ dominante e bloqueado; o STF cobre poucos temas | 10 anotações; 0 lacunas de gramática; índice do aparelho já existe |
| CPC | **HIGH** | STJ (repetitivos e súmulas processuais) | 12 anotações; 0 lacunas |
| Código Penal | **MEDIUM** | STF (HC, RG) mais STJ (súmulas) | 11 anotações; **26 alíneas sem inciso** |
| CPP | **MEDIUM** | STF (HC) acessível; STJ relevante | 66 anotações (13 precedentes); **43 alíneas sem inciso** |
| CTN | **MEDIUM** | STF (RG tributário) acessível, STJ (repetitivos) relevante | 5 anotações; **31 alíneas sem inciso** |
| CLT | **HIGH** | TST (fonte não testada) | 71 anotações (18 precedentes); **406 alíneas sem inciso** |
| Código Eleitoral | MEDIUM | TSE (fonte não testada; a Súmula 9 TSE já funciona no aparelho) | 12 anotações; 0 lacunas |

**Adaptadores de fonte a planejar:**
- **STF:** pronto (tema, jurisprudência, processo).
- **STJ:** exige solução autorizada: acesso oficial, página fornecida pelo usuário ou API.
- **TST e TSE:** testar antes de planejar.

## Proposta de "fábrica" (Fase Q, só backend)

| Etapa | Peça | Estado |
|---|---|---|
| INGEST | texto compilado oficial (Planalto) + índice estrutural (`structure_parser`/`build_target_index`) | **pronto** (genérico) |
| DISCOVER | adaptadores por fonte: `discovery_planalto` (pronto); busca STF por norma (regra pronta no piloto, a extrair para módulo); STJ, TST e TSE | **parcial** |
| NORMALIZE | `target_id` + `citation_granularity` (perfil) + detector de sufixo | **pronto**, com 2 lacunas: "art. N, II" sem "inciso"; alínea sem inciso |
| RISK SCORE | regra de prioridade do `build_j2_batch` (identificador, recorrência, artigo sem juris, referência descrita) | parametrizar a entrada |
| OFFICIAL SOURCE VERIFY | captura com sha (navegador embutido), registro de fontes por lote | pronto para STF; STJ bloqueado |
| NAMESPACE AUDIT | `norm_profiles.namespace_check` | **pronto** |
| TEMPORAL AUDIT | `norm_profiles.temporal_check` (notas de redação do Planalto × ano do julgamento) + gate de provisórios | **pronto** |
| DECISION PROPOSAL | `j2_review_common` com namespace por perfil | **a fazer** (pequeno; preservar o `--check` dos lotes ratificados) |
| HUMAN RATIFICATION | registro de ratificação com hashes (`build_j2_ratification_record`) | parametrizar pastas |
| MATERIALIZE | overlay + exportador por norma (hoje `build_export_run*` só da CF) | **a fazer** |
| TEST | testes por rodada (padrão J2) | padrão pronto |
| DEPLOY | firmware multinorma na camada juris + índice de targets por norma + teste físico | **bloqueador** |

## Critério de sucesso (Fase R)

O motor de pesquisa atende ao critério de "muito bom". O que variou foram exatamente os adaptadores:
- **norma:** perfil `CC2002`;
- **fonte:** Planalto e busca STF;
- **namespace:** wrapper de auditoria;
- **tribunal:** `juris_types` já genérico.

Nenhum pipeline novo foi necessário para pesquisar, mas há três alertas reais fora do motor:
1. o acesso ao STJ;
2. o firmware que só publica jurisprudência da CF;
3. a gramática de alínea para CP, CPP, CTN e CLT.

## Estratégia recomendada (Fase V)

**B — CF + outras normas em paralelo.**

- **Por que não A:** a CF restante tem 59 itens sem identificador e baixo rendimento. Terminá-la primeiro adiaria a escala sem ganho proporcional.
- **Por que não C:** o motor de pesquisa já é portável sem refatorar a CF. Congelar a CF só para generalizar não é necessário.
- **B na prática:**
  - **Trilha CF:** lotes em cadência menor (Batch11 em diante, só por decisão do usuário).
  - **Trilha CC:** pesquisa no escopo STF com os adaptadores do piloto.
  - **Infraestrutura, em missões explícitas:** validador de decisão por perfil, extensão da gramática de alínea fora da CF, firmware multinorma na camada juris e decisão sobre o canal STJ.

## Garantias (Fases P, S e T)

```
CC_RELATIONS_PUBLISHED = 0 · CC_FILES_DEPLOYED = 0 · SD_CHANGED = NO · FIRMWARE_CHANGED = NO
CF_J2I_BASELINE_REGRESSION = 0: REF_PAYLOAD J2I b16f1f81… inalterado; 315/198; nenhum `CC2002` no JUR_LOOKUP do pacote J2I
Módulos da CF alterados para o piloto: nenhum (wrappers e módulos novos em JURISPRUDENCE_ENGINE/)
```
