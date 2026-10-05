# ENTENDA-T1 — Adendo A6 (2026-10-04): padrão congelado após as Rodadas HIGH do Batch05

**Status:** `T1_EDITORIAL_STANDARD_FROZEN`. Este adendo consolida **somente** regras aprendidas e aprovadas nas Rodadas 01, 02, 03A e 03B do Batch05 (38 itens HIGH, revisor `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`). Não cria regra nova fora desses casos. Complementa o padrão ENTENDA-T1 (§§ 1–15, adendos A3–A5) e não revoga nada dele.

**Infraestrutura correspondente (host-side):**
- `t1_validator_v2.py` — validador v2 (camada sobre o motor e o `editorial_checks`; nunca reescreve, nunca aprova);
- `t1_triage.py` — regressão contra as decisões humanas e triagem dos pendentes em filas A–E;
- `editorial/T1_EXTERNAL_CATALOG.json` — catálogo de fontes externas (dado, expansível sem mexer no motor);
- `editorial/T1_KNOWN_RESOLUTIONS.json` — resoluções registradas por versão carimbada;
- `editorial/T1_PIPELINE_CONFIG.json` — `AUTO_APPROVE_LOW = false`, `AUTO_APPROVE_MEDIUM = false`, `MICROAUTO_APPLY = false`;
- `tests/test_t1_validator_v2.py` — regressão das decisões humanas.

**O detector não substitui revisão jurídica.** Ele serve para rotear risco. Falsos negativos conhecidos estão documentados (§ A6.9).

## A6.1 Separação rígida das camadas

| Camada | O que contém | Onde fica |
|---|---|---|
| Lei Seca | texto oficial vigente do target (runtime aprovado) | `source.source_text_snapshot`; nunca alterada |
| Explicação T1 (núcleo) | o que o dispositivo diz e significa, para o leitor iniciante | 5 seções |
| Camada externa | o que não está no dispositivo e o leitor precisa saber que existe | `external_layer_notes` |
| Jurisprudência | teses, temas, ADIs, súmulas | só na camada externa / camada JURISPRUDÊNCIA; número nunca no corpo |
| Legislação correlata | leis que regulamentam o dispositivo (ex.: LC 152/2015) | camada externa; no corpo só com proveniência (`CORE_WITH_PROVENANCE`) |
| Regras de transição | artigos de emendas (ex.: EC 103/2019, arts. 6º, 7º, 9º, 13) | camada externa ou ATENÇÃO, sempre identificadas como externas |

Casos de origem: R01 (XI, XVI, §§ 9, 14, 15), R02 (39, 39 § 9), R03A (40 § 1º II, § 5º, § 6º), R03B (§§ 11, 14, 18, 22).

## A6.2 Proibições

1. **Identificador interno no corpo** (ex.: `CF88_RUNTIME`). R02, art. 39. → `HARD_FAIL`.
2. **Controvérsia tratada como aberta quando já resolvida** (ex.: "qual redação produz efeitos" no art. 39 após o julgamento definitivo da ADI 2.135). R02. → `REVIEW_REQUIRED` (FULL).
3. **Fato jurídico externo sem proveniência** (tema, ADI, lei nº, artigo de emenda). Rodadas 01–03B. → `HARD_FAIL` em aprovação feita sob o A6; `REVIEW_REQUIRED` (FULL) em pendente.
4. **Consequência automática não prevista** ("pode ser exonerado", "como se não tivesse saído", "busca a diferença", "automaticamente"). R02 (41 §§ 2º e 4º), R03A (40 § 2º), R03B (§§ 9º, 14).
5. **Finalidade teleológica especulativa apresentada como regra** ("o objetivo é transparência", "evitar fragmentação", "incentivo", "reduz custos"). R01 (XVI), R02 (38 V, 39 § 4º, 39 § 9º), R03B (§§ 19, 20). Exceção: quando a própria Lei Seca declara a finalidade ("para preservar…", 40 § 8º, aprovado sem alteração).
6. **Generalização universal além do texto** ("todos os servidores", "cada ente tem um único", "só pode perder o cargo nas hipóteses do § 1º", "qualquer atividade"). R02 (41), R03A (40, 40 § 1º I), R03B (§§ 11, 13, 20). Não vale quando o quantificador está na própria Lei Seca.
7. **Exemplo que cria requisito inexistente** ("assiduidade, produtividade e responsabilidade"; "promovida para a vaga"). R02 (41 §§ 2º e 4º).
8. **Exceção ou interpretação transformada em regra constitucional** ("a leitura usual é"; "aplicação subsidiária… quando o art. 40 e a lei do ente não tratam"; "pode ficar abaixo do salário mínimo"). R03B (§§ 7º, 12, 18).
9. **Jurisprudência complexa resolvida no núcleo** ("a soma se sujeita ao teto"; "magistério = sala de aula"). R01 (XI, XVI), R03A (§§ 5º, 6º), R03B (§ 11). O núcleo remete; a camada externa traz o tema.

## A6.3 Regra permanente × transição

- O núcleo T1 explica o **texto constitucional vigente** do dispositivo.
- Regra de transição que não está no dispositivo fica **identificada como externa** (ATENÇÃO e/ou camada externa), com o artigo da emenda quando conhecido e proveniência.
- Nunca misturar regra transitória e permanente sem marcação. O `editorial_checks` mantém `TRANSITION_IN_CORE`; o teste do art. 40 proíbe "regra(s) de transição" em O QUE DIZ / O QUE SIGNIFICA.
- Afirmação sobre **estado de lei externa** (editada, pendente, "está na camada") só com proveniência (R03A § 1º II; R03B § 22).

## A6.4 Proveniência externa

- `content_provenance` em `human_review`, com `source_type = HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`, `in_cf88_runtime = false`, seção e nota.
- Usar quando a informação não vem do runtime, mas foi introduzida e validada pela revisão humana com fonte oficial.
- Origem de emenda confirmada pela fonte estrutural canônica do projeto (ex.: "Incluído pela EC 103/2019") não exige proveniência.
- A proveniência não altera o payload (`render_payload` ignora `human_review`).
- Aplicável às aprovações com `reviewed_on ≥ 2026-10-04`. O acervo anterior (220) é legado, e o validador o trata como `INFO`.

## A6.5 Versionamento

- Versão carimbada é **imutável** (motor: `ENTENDA_CONTENT_CHANGED_WITHOUT_VERSION_BUMP`; validador v2: `VERSION_MUTATION`).
- Mudança de conteúdo exige nova `editorial_version`; a anterior fica `RETIRED` / `CHANGES_REQUESTED`.
- `superseded_by` aponta para a **versão vigente** da mesma chave (regra do motor). A cadeia completa fica no registro da rodada (`version_history`; ex.: art. 39 v1 → v2 → v3, R02).
- Mudança só de status (aprovação) não exige nova versão.

## A6.6 Política de microajustes T1 (aprovada na R03A, válida na R03B)

Podem ser aplicados e **registrados** sem nova consulta humana, desde que o significado jurídico seja idêntico:

1. sigla → nome por extenso (ex.: "STF" → "Supremo Tribunal Federal");
2. artigo, preposição, pequena inversão sintática ou sinônimo estritamente equivalente, para evitar cópia literal ou `NEAR_COPY`;
3. remoção de termo redundante do glossário acima de 5;
4. ajuste gramatical exigido pelo validador;
5. retirada ou substituição de identificador interno.

Mudanças jurídicas, factuais, numéricas, conceituais ou de alcance **não** são microajustes: param e voltam à revisão humana. Cada desvio registra o item da política, e o teste da rodada prova que só houve adaptação T1 (texto final = texto do revisor + desvios; números iguais; nos desvios do item 2, só palavras funcionais diferem). O validador v2 sugere o microajuste (`suggest_copy_microfix`). Nesta fase ele **não aplica** (`MICROAUTO_APPLY = false`).

## A6.7 Severidades do validador v2

| Severidade | Regras |
|---|---|
| `HARD_FAIL` | `ENGINE_CONTRACT` (qualquer bloqueio do motor: cópia > 10 palavras, sigla de tribunal, glossário > 5, faixa de palavras, caracteres reservados, estrutura); `LEI_SECA_DIVERGENCE` (snapshot ≠ runtime); `INTERNAL_IDENTIFIER`; `EXTERNAL_FACT_NO_PROVENANCE` (aprovação sob A6); `VERSION_MUTATION`, `VERSION_CHAIN_BROKEN`, `DUPLICATE_ACTIVE` |
| `REVIEW_REQUIRED` — rota QUICK | `TELEOLOGY_SPECULATIVE`, `UNIVERSAL_CLAIM`, `AUTOMATIC_CONSEQUENCE`, `PERMISSION_NOT_IN_TEXT`, `QUALIFIER_NOT_IN_TEXT`, `EXAMPLE_INVENTED_REQUIREMENT`, `EDITORIAL_CHECK_UNRESOLVED` |
| `REVIEW_REQUIRED` — rota FULL | `CATALOG_CONTRADICTION`, `CATALOG_LINK_MISSING`, `RESOLVED_TREATED_AS_OPEN`, `OUTDATED_CONTROVERSY`, `LAW_STATUS_CLAIM`, `INTERPRETATION_AS_RULE`, `EXTERNAL_FACT_NEEDS_PROVENANCE` |
| `EDITORIAL_AUTO_FIX_ELIGIBLE` | `NEAR_COPY_MICROFIX` (item 2), `SIGLA_EXPANSION` (item 1) |
| `INFO` | achados do `editorial_checks` já resolvidos, lint informativo, tema do catálogo já vinculado, fato externo com proveniência, resolução conhecida registrada |

Os detectores combinam **padrão textual + metadados + catálogo**:
- **negação:** "não… automaticamente" não dispara;
- **Lei Seca:** quantificador ou finalidade presente no próprio texto não dispara;
- **contexto do catálogo:** o "teto" do subsídio de vereador não é o tema dos Temas 377/384;
- **target catalogado:** dispara quando o target já tem entrada no catálogo e a nota correspondente falta.

## A6.8 Roteamento (filas)

| Fila | Critério | O que o revisor vê |
|---|---|---|
| A — CLEAN_LOW | LOW, nenhum `REVIEW_REQUIRED`/`HARD_FAIL` | lista compacta (título, 1ª frase, checks, motivo); T1 completo só sob pedido |
| B — CLEAN_MEDIUM | MEDIUM, nenhum `REVIEW_REQUIRED`/`HARD_FAIL` | revisão agregada: ponto central, dependência externa, alertas, amostra do núcleo |
| C — QUICK_REVIEW | só achados QUICK, no máximo 2 tipos | trecho, motivo, contexto mínimo, ação proposta |
| D — FULL_HUMAN_REVIEW | qualquer achado FULL, mais de 2 tipos, ou risco HIGH | pacote completo no padrão das Rodadas HIGH |
| E — HARD_FAIL | qualquer `HARD_FAIL` | corrigir antes de qualquer revisão |

**Autoaprovação desligada.** A e B continuam `PENDING_HUMAN_REVIEW` até decisão humana sobre a ativação.

## A6.9 Regressão e limites conhecidos

Medição contra as decisões reais (`T1_VALIDATOR_V2_REGRESSION.json`, `tests/test_t1_validator_v2.py`):

- **v1 que receberam CHANGES_REQUESTED:** 28 de 31 detectadas (90%). Desse total, 24 por regra generalizável (padrão ou tema do catálogo no texto) e 4 só pela memória de target catalogado.
- **Falsos negativos conhecidos (3):**
  - `CF88:ART.37:PAR.9`;
  - `CF88:ART.40:CAPUT` (definição conceitual de "contributivo/solidário");
  - `CF88:ART.40:PAR.9` (contagem recíproca descrita como transferência).

  São correções conceituais sem marca textual estável. Não se criou regra frágil para eles.
- **v1 aprovadas sem alteração:** 2 de 7 disparam (falsos positivos), ambas registradas em `T1_KNOWN_RESOLUTIONS.json`.
- **Textos finais aprovados (38):** 0 alertas pendentes após as resoluções registradas; 0 `HARD_FAIL`.
- **Pilotos e acervo aprovado anterior (220):** 0 `HARD_FAIL`. 45 dos 220 recebem algum alerta, o que estima a taxa de encaminhamento à revisão de texto já bom (proxy de falso positivo). Entre esses alertas há 2 afirmações reais sobre estado de lei sem fonte ("lei complementar que ainda não foi editada", art. 7º I; art. 5º LXXI): candidatas a auditoria, não alteradas.

## A6.10 Expansão

Novas entradas do catálogo e novas resoluções conhecidas são **dados**. Uma regra de padrão nova só entra com:
- o caso humano de origem (`learned_from`);
- teste de regressão;
- medição de falso positivo no acervo aprovado.

## A6.11 Calibração final do Batch05 (2026-10-04)

**Dependência externa: três estados do resolvedor** (`t1_external_resolver.py`). O resolvedor consulta, em ordem: catálogo T1, relações validadas do Relations Engine, texto local e proveniência do ENTENDA.

| Estado | Significado |
|---|---|
| `EXTERNAL_EVIDENCE_AVAILABLE` | evidência aceita por uma das fontes da ordem acima (relação validada: A/B + EXIBIR, ou status ATUAL no catálogo global) |
| `EXTERNAL_EVIDENCE_LOCAL_PENDING` | a relação existe localmente, mas está pendente, em quarentena ou não validada pelo Relations Engine |
| `EXTERNAL_VERIFICATION_REQUIRED` | não há evidência suficiente nas fontes consultadas |

**ENTENDA e Relations Engine têm processos editoriais independentes.**
- A proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE` pode sustentar a aprovação editorial de um ENTENDA mesmo quando a relação correspondente continua `EXTERNAL_EVIDENCE_LOCAL_PENDING`. Caso: art. 37, § 7º → Lei nº 12.813/2013, relação em quarentena 2D3.
- Essa aprovação não promove, não valida e não altera a relação no Relations Engine.
- A relação, por sua vez, é evidência para o ENTENDA, nunca verdade para o núcleo T1.

**Regras generalizáveis acrescentadas** (`semantic_findings`, rota QUICK):
- `EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE`: condição atribuída ao sujeito ("deve ser/ter/possuir/estar + termo") com termos ausentes da Lei Seca e do contexto runtime citado, sem proveniência. Caso: art. 37, VIII v1.
- `EXCEPTION_OR_RESSALVA_DROPPED`: o texto tem exceção expressa ("exceto", "salvo"), e um parágrafo da explicação reafirma a regra em termos gerais sem a palavra-chave da exceção. Caso: art. 38, IV v1.
- `EXHAUSTIVE_ENUMERATION_RISK`: "X são os A e B" sem "como/por exemplo" e com itens ausentes do texto. Caso: art. 38, I v1.

Falsos positivos conhecidos estão registrados (art. 37, V; visão geral do art. 38). Não se criou detector específico para o art. 37, XV, nem para o IX: esses dois casos ficam cobertos pelo catálogo (`STF_IRREDUTIBILIDADE_MONTANTE_NOMINAL`, `STF_TEMA_612`).

**Lições da calibração humana dos 31 pendentes:**
- Fila C: 5 de 9 alertas úteis (precisão 5/9). Falsos positivos: art. 37, II, X, XII; art. 39, § 2º.
- Fila A (CLEAN_LOW): 1 problema substantivo em 5 (art. 37, VIII).
- Fila B (CLEAN_MEDIUM): 4 problemas em 15 (art. 37, IX e XV; art. 38, I e IV).
- **Sem alerta ≠ aprovação automática segura.** O pipeline serve para triagem e redução do volume humano, não para aprovação autônoma. `AUTO_APPROVE_LOW` e `AUTO_APPROVE_MEDIUM` continuam desligados.
- O sugeridor automático de microajuste pode propor troca gramaticalmente pior (art. 38: "da" → "de"). A sugestão é só sugestão, e a escolha final do microajuste é registrada.

**Regressão atualizada** (substitui os números do § A6.9; fonte: `T1_VALIDATOR_V2_REGRESSION.json`):
- versões que receberam CHANGES_REQUESTED: 40 de 43 detectadas (34 por regra generalizável, 6 só por memória do catálogo);
- falsos negativos: os mesmos 3 do § A6.9;
- textos finais aprovados (69): 0 alertas pendentes após as resoluções registradas, 0 `HARD_FAIL`;
- acervo anterior (220): 0 `HARD_FAIL`, 49 com algum alerta (backlog de auditoria).
