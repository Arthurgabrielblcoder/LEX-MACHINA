# ENTENDA-CF-A1 — Piloto editorial da Constituição

Data: 2026-09-28 · Missão: ENTENDA-CF-A1 · Estado: **UNTRACKED, para revisão humana** (não versionado, sem commit e sem tag).
Dados completos: `CLEANUP_AUDIT/ENTENDA_CF_PILOT.json`.

## 0. Pré-requisito: Referências A3 versionadas

| Item | Valor |
|---|---|
| HEAD inicial | `85597db407b755fd766df908df842bbb07bfa4bd` |
| Pré-flight | tracked limpo, staging vazio; 47/47 PASS; export 2× BYTE_IDENTICAL (iguais ao run1) |
| Commit A3 | `9fcab702a9b6467b71949071ba34741e940e366d` — `feat: complete canonical CF88 reference engine` (14 arquivos, paths explícitos) |
| Tag anotada | `cf-reference-engine-final-2026-09-28` — "Completed canonical and generic CF88 reference engine pilot" |
| MOTOR_REFERENCIAS_CF_FECHADO | SIM |
| Push | não |

## 1. O que é o ENTENDA

A tela ENTENDA é uma camada explicativa derivada e editorial. Ela não é Lei Seca, não é Jurisprudência e não é Referências.

```
LEI SECA ─┐
ENTENDA  ─┤
CORRELATAS├── todas as camadas usam a mesma chave: target_id canônico (CF88:ART.37:PAR.6, ADCT:ART.10:INC.II …)
JURISPRUD.┤
REFERÊNC. ┘
```

Regras da camada:

- **A Lei Seca fica intacta.** A explicação guarda apenas um *snapshot* do texto oficial e o seu hash, para detectar mudanças. Esse snapshot nunca é exibido como texto oficial.
- **`usage_policy = EDITORIAL_OUTPUT_ONLY`.** O ENTENDA nunca é fonte para Correlatas, Jurisprudência, Referências ou para o relations engine. Um teste automático garante que nenhum código ou configuração do `LEGAL_TARGET_ID` lê o ENTENDA.
- **Sem herança automática.** `get_explanation(filho)` nunca devolve a explicação do pai. O contexto é declarado (`context_targets`), e o conteúdo do pai não é herdado.
- **Referências.** A explicação pode saber quantos vínculos existem para o target (`reference_count`, no payload). Não incorpora o conteúdo desses vínculos.

## 2. Contrato editorial (template `ENTENDA-T1`)

| Seção | Campo | Regra |
|---|---|---|
| O QUE DIZ | `o_que_diz` | Obrigatória. Resumo fiel e curto do comando normativo. Não copia a Lei Seca: o validador recusa mais de 10 palavras seguidas iguais ao texto oficial. |
| O QUE SIGNIFICA | `o_que_significa` | Obrigatória. Português claro para quem estuda Direito, sem infantilizar e sem trocar precisão por analogia. |
| EXEMPLO PRÁTICO | `exemplo_pratico` | Obrigatória. Caso hipotético concreto que ilustra a regra sem criar regra nova. Quando cabe, usa situação institucional ou processual. |
| ATENÇÃO | `atencao` | Opcional (`null`). Só quando há ponto de confusão relevante: exceção, limite, condição, dependência do pai ou erro comum. |
| PALAVRAS DIFÍCEIS | `palavras_dificeis` | De 0 a 5 pares `termo` / `explicação`. Poderão alimentar o futuro DICIONÁRIO (motor ainda não criado). |
| (camada externa) | `external_layer_notes` | Aponta que um tema depende de jurisprudência ou doutrina, sem afirmar o conteúdo de decisões. |

Os nomes das seções foram mantidos, porque não houve justificativa forte para trocá-los.

Guardas automáticas (falham fechadas):

- **Tribunais nas seções.** Menções como STF, STJ, TST, "Súmula", "Tema nº", ADI, "decidiu" são recusadas (`ENTENDA_EXTERNAL_CASE_CONTENT`).
- **Faixa de tamanho.** Visão geral: 120–560 palavras. Dispositivo: 80–400 palavras.
- **Repetição entre pai e filho.** Frases iguais ou similaridade acima de 0,35 são recusadas (`ENTENDA_REPEATED_ACROSS_HIERARCHY`).
- **Tamanho do payload.** No máximo 6144 bytes.
- **Caracteres reservados.** `|`, e linhas começando por `#` ou `@`, não podem aparecer no conteúdo.

## 3. Registro de uma explicação (corpus JSONL)

| Grupo | Campos |
|---|---|
| Identificação | `contract_version`, `explanation_id`, `explanation_key`, `target_id`, `norma_id`, `namespace`, `variant`, `editorial_version`, `template_version`, `prompt_version` |
| Granularidade | `granularity.{target_kind, role, semantic_autonomy, context_targets, editorial_reason}` |
| Vigência | `validity.{target_status: CURRENT, HISTORICAL ou UNKNOWN; validity_note}` |
| Fonte | `source.{text_source_role, text_source_path, text_source_file_sha256, snapshot_scope, source_text_snapshot, source_text_sha256, context_text_sha256}` |
| Conteúdo | `content` com as 5 seções, e `external_layer_notes` |
| Situação | `status` (ACTIVE, STALE ou RETIRED), `review_status` (DRAFT, PENDING_HUMAN_REVIEW, APPROVED ou REJECTED) |
| Autoria | `authoring.generated_at`: metadado operacional; o build não o usa, o que preserva o determinismo |
| Política | `usage_policy` |

### `explanation_id`

- Formato: `ENTENDA/<target_id>/<VARIANT>/<editorial_version>`. Exemplo: `ENTENDA/CF88:ART.37:PAR.6/BASE/1`.
- `explanation_key` (`ENTENDA/<target_id>/<VARIANT>`) é estável entre versões.
- O identificador não depende do caminho físico e distingue target, variante futura (por exemplo, `RESUMO` ou `CONCURSO`) e versão editorial.
- Regras: um único registro ACTIVE por chave; id duplicado é recusado.

## 4. Política de granularidade: qual target recebe explicação

Nenhuma explicação é gerada automaticamente para todo target estrutural. A unidade é escolhida editorialmente, por semântica, e cada registro justifica a escolha em `editorial_reason`.

| Papel | Tipo de target | Quando usar | Autonomia |
|---|---|---|---|
| OVERVIEW | ARTIGO | Visão geral e estrutura do artigo. Não repete as explicações das subdivisões. | AUTONOMOUS |
| DEVICE | CAPUT / PARÁGRAFO | Dispositivo com comando completo (ex.: § 6º e § 10 do art. 37) | declarada pelo editor |
| BLOCK | PARÁGRAFO / INCISO com subdivisões | Enunciado e lista explicados em conjunto (ex.: § 4º do art. 60) | declarada pelo editor |
| ITEM | INCISO / ALÍNEA | Só quando o item tem alcance próprio (ex.: art. 60, § 4º, IV) | sempre DEPENDENT_ON_PARENT |

Outras regras:

- **Caput.** Só recebe explicação própria quando o artigo tem parágrafos e o caput traz um comando distinto da visão geral. Nos demais casos, a unidade é o ARTIGO, o que evita repetir a mesma explicação em artigo, caput e parágrafo.
- **`context_targets`.** É a cadeia estrutural completa, do artigo até o pai direto, e o validador exige exatamente essa cadeia. Por exemplo, `CF88:ART.60:PAR.4:INC.IV` → `[CF88:ART.60, CF88:ART.60:PAR.4]`, e `ADCT:ART.10:INC.II` → `[ADCT:ART.10, ADCT:ART.10:CAPUT]`.
- **Não elegíveis:** NORMA e NAMESPACE.

## 5. Art. 60: prova de composição hierárquica

| Target | Papel | Contexto | Foco |
|---|---|---|---|
| `CF88:ART.60` | OVERVIEW | — | Processo de emenda: legitimados, dois turnos e 3/5, promulgação pelas Mesas, limites circunstanciais (§ 1º), reapresentação (§ 5º). Exemplo numérico: 49/81 e 308/513. |
| `CF88:ART.60:PAR.4` | BLOCK | ART.60 | Cláusulas pétreas: o limite atua antes da deliberação; a proposta proibida é a "tendente a abolir", não qualquer alteração. Atenção: o voto obrigatório não está na lista. |
| `CF88:ART.60:PAR.4:INC.IV` | ITEM | ART.60, PAR.4 | Direitos e garantias individuais: não cria direitos, protege os existentes contra a abolição por emenda; não se limita necessariamente ao art. 5º. Exemplo: PEC que extinguisse o habeas corpus. |

Similaridade entre pai e filho (Jaccard; o limite é 0,35):

| Par | máximo |
|---|---|
| ART.60 → PAR.4 | 0,068 |
| ART.60 → INC.IV | 0,094 |
| PAR.4 → INC.IV | 0,200 (em `o_que_diz`) |

Nenhuma frase se repete entre os três. As explicações são complementares. Não há um texto gigante que substitua as subdivisões.

## 6. Vigência e STALE

**Vigência:**

- **CURRENT:** gera explicação; é a prioridade do produto.
- **HISTORICAL:** recusado (`ENTENDA_HISTORICAL_NOT_ALLOWED`, `allow_historical=false`).
- **UNKNOWN:** só é aceito com `validity_note` e revisão humana.
- **Status de um ARTIGO** (estrutural): é derivado da subárvore. Se há algum dispositivo CURRENT, o artigo é CURRENT; senão, se há algum UNKNOWN, é UNKNOWN; senão, HISTORICAL.

**STALE:**

- **Snapshot.** É o texto oficial atual da subárvore do target, uma linha por dispositivo (`target_id<TAB>texto`), mais o `source_text_sha256`.
- **Contexto.** Guarda-se também o hash do texto próprio de cada `context_target`.
- **`check_stale()`** devolve um destes estados: FRESH, STALE_TEXT_CHANGED, STALE_CONTEXT_CHANGED, ORPHANED_TARGET ou NO_EXPLANATION.
- **Regra do stamp.** Um registro já carimbado mantém o hash original. Mudar o conteúdo sem aumentar `editorial_version` é recusado. Assim, uma mudança no texto legal nunca deixa a explicação silenciosamente válida.
- **Prova (teste).** Alterei só o enunciado do § 4º do art. 60 numa cópia em memória:
  - `ART.60` ficou STALE_TEXT_CHANGED (a subárvore mudou);
  - `PAR.4` ficou STALE_TEXT_CHANGED;
  - `INC.IV` ficou STALE_CONTEXT_CHANGED (o texto próprio não mudou; mudou o do pai);
  - `ART.37:PAR.6` continuou FRESH;
  - o build propaga `F|STALE_…` para o lookup e para o payload.
- **Updater completo:** não foi construído. O modelo de dados já o suporta.

## 7. Formato e armazenamento

| Opção | Avaliação |
|---|---|
| **JSONL por norma** (escolhida como fonte) | Uma linha por explicação: diff e merge por linha, atualização incremental, leitura em streaming, um arquivo por norma. |
| JSON único | Precisa carregar e reescrever tudo; diffs ruins; inviável na RAM do ESP32. |
| Arquivo por target | Dezenas de milhares de arquivos pequenos em FAT32: clusters desperdiçados, diretórios lentos e updater caro. |

A recomendação, implementada apenas para o piloto da CF, é:

- **Fonte:** `ENTENDA_ENGINE/corpus/<NORMA>.entenda.jsonl`.
- **SD** (gerado de forma determinística, por norma):
  - `ENTENDA_LOOKUP.IDX`: `TARGET_ID|OFFSET|BYTES|EXPLANATION_ID|VALIDITY|FRESHNESS|REVIEW`, ordenado em ASCII;
  - `ENTENDA_PAYLOAD.DAT`: um bloco por explicação, no formato `@ID`, depois `T|K|V|R|F|H|C|N|W`, depois as seções `#O QUE DIZ` … `#PALAVRAS DIFÍCEIS` (`termo|explicação`) e `#CAMADAS EXTERNAS`, e por fim `@END`.
- **Edição:** `editorial/<NORMA>_*_DRAFTS.json`, legível. O comando `stamp` carimba o snapshot e o hash.

## 8. Implicações para o ESP32 (nada implementado no firmware)

- **Chave.** A consulta usa o mesmo `target_id` canônico das Referências: namespace obrigatório, ADCT separado e buffer `char[48]`.
- **Leitura.** Busca binária no lookup por *seek*, sem carregar o arquivo na RAM. Depois, `seek(OFFSET)` e `read(BYTES)` de um único bloco (no máximo 6144 bytes; o maior do piloto tem 2858).
- **Tela.** As seções são marcadas por `#` e a tela pagina o conteúdo. O texto é UTF-8 com acentos.
- **Avisos na tela.** O firmware deve avisar quando `F` for diferente de FRESH, `V` for UNKNOWN ou `R` for diferente de APPROVED.
- **Contexto.** As linhas `C|` permitem ao firmware oferecer links de navegação para as explicações dos pais, sem mesclar o conteúdo delas.
- **Crescimento.** Com mais de cerca de 100 KB de lookup numa norma, usar registros de largura fixa ou um índice em dois níveis.

## 9. Piloto

| Target | Papel | Vigência | Palavras | Bytes | Refs |
|---|---|---|---|---|---|
| `CF88:ART.1` | OVERVIEW | CURRENT | 317 | 2290 | 1 |
| `CF88:ART.5` | OVERVIEW | CURRENT | 337 | 2624 | 0 |
| `CF88:ART.37` | OVERVIEW | CURRENT | 325 | 2582 | 0 |
| `CF88:ART.37:PAR.6` | DEVICE | CURRENT | 335 | 2566 | 5 |
| `CF88:ART.37:PAR.10` | DEVICE | CURRENT | 299 | 2554 | 0 |
| `CF88:ART.60` | OVERVIEW | CURRENT | 343 | 2342 | 0 |
| `CF88:ART.60:PAR.4` | BLOCK | CURRENT | 271 | 2219 | 0 |
| `CF88:ART.60:PAR.4:INC.IV` | ITEM | CURRENT | 261 | 2105 | 0 |
| `CF88:ART.150` | OVERVIEW | CURRENT | 369 | 2581 | 0 |
| `CF88:ART.225` | OVERVIEW | CURRENT | 351 | 2540 | 0 |
| `ADCT:ART.10:INC.II` | BLOCK | UNKNOWN | 325 | 2858 | 0 |

A coluna Refs traz `reference_count` (vínculos visíveis no próprio target, sem incluir filhos).

**Totais:**

- payload: 27.261 bytes em blocos (arquivo `ENTENDA_PAYLOAD.DAT`: 27.340);
- média: 2.478 bytes por explicação;
- mínimo: 2.105 (`CF88:ART.60:PAR.4:INC.IV`); máximo: 2.858 (`ADCT:ART.10:INC.II`);
- palavras: média de 321;
- `ENTENDA_LOOKUP.IDX`: 1.101 bytes, com média de 91,5 bytes por entrada.

**Arquivos do build:**

| Arquivo | SHA-256 |
|---|---|
| `ENTENDA_LOOKUP.IDX` | `b511b69218100e83e97ca8e17de22be9655e9d771a5b15c5fb3ecde24ea5536d` |
| `ENTENDA_PAYLOAD.DAT` | `e117ccf4e95a58e431976499299e2ffd6e7f4db7f166443b11220d01e7ba296f` |
| `ENTENDA_BUILD_MANIFEST.json` | `d85392a9706a3a98808eaf2e906e75cb8932e649bc06708bbfe375246a120bd0` |

**Determinismo:** dois builds deram BYTE_IDENTICAL, e o teste reconstrói e compara com `pilot_run1`.

**ADCT.** O `ADCT:ART.5` não é adequado: trata das eleições de 1988, cujos efeitos se esgotaram. Nenhum alvo ADCT é CURRENT, porque o texto operacional não contém o ADCT. Por isso usei o **`ADCT:ART.10:INC.II`** (estabilidade do cipeiro e da gestante): é uma regra transitória com aplicação prática. Ele está com status UNKNOWN, com `validity_note` obrigatória, e o texto foi lido da fonte estrutural `cf.txt` (`STRUCTURAL_CANONICAL_SOURCE_FALLBACK`).

**Pontos de qualidade validados:**

- **§ 6º do art. 37.** A explicação cobre:
  - as pessoas jurídicas de direito público e as privadas prestadoras de serviço público;
  - os danos causados por seus agentes;
  - a exigência de que o agente atue "nessa qualidade";
  - o regresso, condicionado a dolo ou culpa.
  
  O contraste objetiva/subjetiva é tirado do próprio texto: dolo ou culpa só aparecem no regresso. Contra quem ajuizar, as excludentes e a omissão ficam marcados como camada externa.
- **§ 10 do art. 37.** A vedação é de percepção simultânea de proventos (arts. 40, 42 e 142) com remuneração pública, e as três exceções são literais. As regras previdenciárias e o teto ficam marcados como contexto externo. O texto registra que o RGPS não aparece na redação.

Conteúdo completo, legível para revisão: `ENTENDA_ENGINE/editorial/CF88_PILOT_DRAFTS.json`.

## 10. Estimativas (ordens de grandeza, não precisão)

**Metodologia:**

- unidades = artigos vigentes + uma fração dos parágrafos + uma fração dos incisos e alíneas (conforme a política de granularidade);
- tamanho de 1.800 a 3.200 bytes por explicação (1.500 a 3.200 para as 72 normas);
- lookup de cerca de 92 bytes por entrada.

**Contagens da CF usadas:** 276 artigos CF88 CURRENT, 790 parágrafos CURRENT, 1.578 incisos e alíneas CURRENT, 148 artigos ADCT UNKNOWN.

**Cenários:**

| Cenário | CF: explicações | CF: payload | CF: lookup | 72 normas: explicações | 72 normas: payload | 72 normas: lookup |
|---|---|---|---|---|---|---|
| A — só artigos | 276–424 | 0,5–1,4 MB | 25–39 KB | 5,5k–9,1k | 8–29 MB | 0,5–0,8 MB |
| **B — recomendado** (artigos + 25–45% dos §§ + 5–12% dos incisos/alíneas) | **580–880** | **1,1–2,8 MB** | **53–81 KB** | **9k–27k** | **14–87 MB** | **0,8–2,5 MB** |
| C — máximo razoável | 1.130–1.530 | 2,0–4,9 MB | 103–140 KB | 20k–46k | 29–146 MB | 1,8–4,2 MB |

Premissas para as 72 normas:

- 9.136 artigos;
- as razões da CF por artigo (2,86 parágrafos e 5,72 incisos/alíneas) multiplicadas por 0,4 a 1,0;
- cobertura de 60% a 100% dos artigos.

Em qualquer cenário, o volume cabe folgadamente no cartão SD. O custo real está na produção e na revisão editorial.

## 11. Motor genérico

- **Motor:** `ENTENDA_ENGINE/entenda_engine.py`. Não contém nenhuma norma codificada, o que é verificado por teste.
- **Configuração por norma:** `ENTENDA_ENGINE/entenda_config.json` (índice, status, fontes de texto por namespace, corpus, export de referências, `allow_historical`, status de revisão exportáveis).
- **Funções:**
  - `validate_explanation()` e `validate_corpus()`;
  - `get_explanation(target_id)` e `context_links()`;
  - `check_stale(target_id, current_text)` e `stale_report()`;
  - `stamp()`;
  - `build_entenda_index()` e `lookup_idx()`.
- **Norma sintética de teste:** CDC1990 fez o ciclo completo — `stamp`, `build` duas vezes (idêntico), `lookup` e STALE após a mudança do texto.
- **Outras normas:** nenhuma foi gerada.

## 12. Testes

**ENTENDA: 18/18 OK** (`ENTENDA_ENGINE/tests/test_entenda_engine.py`). Os testes cobrem:

- target válido, target inválido e target histórico;
- detecção de STALE, unitária e ponta a ponta;
- contexto do pai, declarado e não herdado;
- composição do art. 60;
- ADCT;
- lookup;
- `explanation_id` duplicado e dois registros ativos para a mesma chave;
- hash ausente ou errado;
- guardas editoriais (tribunais nas seções, cópia da Lei Seca, seção vazia);
- `stamp` exigindo nova versão;
- build determinístico;
- norma sintética;
- rejeição de norma não configurada;
- ausência de norma codificada;
- ENTENDA não usado como fonte por outra camada.

**LEGAL_TARGET_ID: 47/47 OK.**

## 13. Critério ENTENDA-CF-A1

Os 10 itens do checklist do JSON passaram:

- contrato editorial definido;
- `target_id` reutilizado;
- granularidade coerente;
- art. 60 provando a composição hierárquica;
- STALE detectável;
- lookup funcionando;
- armazenamento determinístico;
- piloto legível;
- motor genérico;
- nenhuma camada oficial ou jurisprudencial alterada.

Nada foi alterado em Lei Seca, jurisprudência, referências, firmware, SD, arquivos de archive, protected545 ou D05.

## 14. Arquivos (untracked)

- `ENTENDA_ENGINE/entenda_engine.py`
- `ENTENDA_ENGINE/entenda_config.json`
- `ENTENDA_ENGINE/editorial/CF88_PILOT_DRAFTS.json`
- `ENTENDA_ENGINE/corpus/CF88.entenda.jsonl`
- `ENTENDA_ENGINE/build/pilot_run1/` (`ENTENDA_LOOKUP.IDX`, `ENTENDA_PAYLOAD.DAT`, `ENTENDA_BUILD_MANIFEST.json`)
- `ENTENDA_ENGINE/tests/test_entenda_engine.py`
- `CLEANUP_AUDIT/ENTENDA_CF_PILOT.md` e `CLEANUP_AUDIT/ENTENDA_CF_PILOT.json`

## 15. Recomendação para ENTENDA-CF-A2 (não iniciada)

1. **Revisão humana das 11 explicações.** Prioridade para o § 6º do art. 37, o § 10 do art. 37 e o trio do art. 60. Confirmar a vigência do ADCT, art. 10. Aprovar (APPROVED) ou pedir versão 2.
2. **Versionar o motor e o piloto aprovados.**
3. **Definir o lote A2.** Por exemplo, os Títulos I e II completos pelo cenário B, com a lista de units escolhida antes da redação.
4. **Arquivo ADCT separado.** Criar o arquivo ADCT operacional (contrato da A3) para tirar os alvos ADCT de UNKNOWN.
5. **Firmware.** Só depois: tela ENTENDA no firmware lendo o par IDX/DAT pelo `target_id`, junto com a correção de namespace das Referências.

---

## Adendo A2: revisão humana (2026-09-28)

- **Decisão:** o piloto foi APROVADO COM AJUSTES. Foram cinco ajustes, detalhados em `CLEANUP_AUDIT/ENTENDA_CF_A1_HUMAN_REVIEW.md` e em `ENTENDA_ENGINE/derived/CF88_PILOT_HUMAN_REVIEW_DIFF.json`.
- **Status:** as 11 explicações estão como `HUMAN_APPROVED_T1`, e o padrão ENTENDA-T1 está APROVADO (`ENTENDA_ENGINE/ENTENDA_T1_EDITORIAL_STANDARD.md`).
- **Build canônico:** o build `build/pilot_run1` descrito acima foi substituído por `derived/pilot_t1` (formato de lookup v2, com as colunas `REVIEW` e `MATCH`). Os hashes das seções 9 e 12 deste relatório registram o estado da A1.
