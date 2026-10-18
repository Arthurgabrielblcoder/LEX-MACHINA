# Sprint de escala multinorma — relatório (estimativa V2)

```
HOST-ONLY · SEM DEPLOY · SEM FLASH · CARTÃO NÃO ACESSADO · BATCH11 NÃO INICIADO · CC NÃO PUBLICADO
CF_BASELINE = 315/198 (J2I_FROZEN_315_198, byte-idêntico) · CF_REGRESSION = 0
```

## 0. Ratificação do Batch10

Registro: `JURISPRUDENCE_AUDIT/J2_RATIFICATION_RECORD_10.json`. O arquivo de decisões do lote ficou byte-idêntico e é fixado por hash.

| Contagem | Valor |
|---|---|
| BATCH10_RATIFIED_RECOMMENDATIONS | 8 |
| BATCH10_NEW_RELATIONS | **6**: ADI 1842 → CF 25 § 3º; ADC 12 → CF 103-B § 4º; ADI 5081 → CF 17 § 1º; ADI 4439 → CF 19, I **e** CF 210 § 1º; RE 229096 → CF 151, III |
| BATCH10_NEW_TARGETS | **6** (nenhum deles tinha jurisprudência no J2I) |
| BATCH10_ALREADY_COVERED | 2 (Temas 656 e 796) |
| BATCH10_REJECTED | 1 (art. 103-A) |
| BATCH10_UNRESOLVED | 2 (Súmula 203/STJ: UNRESOLVED_EXTERNAL; art. 124: UNRESOLVED_IDENTIFICATION) |

**Particularidades:**
- **ADI 5081:** traz proveniência temporal: julgada em 2015, com o § 1º na redação da EC 52/2006; não interpreta a EC 111/2021. É uma exceção à regra J1.4/J2B.1, ratificada expressamente pelo usuário.
- **ADI 4439:** é a única modificação editorial, com dois vínculos independentes.
- **Materialização:** nada foi materializado.

## 1. Bloqueador 1 — firmware multinorma (protótipo, não gravado)

**Acoplamento encontrado na camada juris legada** (`JUR_LOOKUP`/`JURISPRUDENCIA.IDX`):

| Ponto | Classificação | Tratamento |
|---|---|---|
| `arquivoAtualPertenceACF()` como único gate de `carregarRelacoesDoArtigo` | BLOCKER | Novo ramo para qualquer norma do catálogo **com** linhas no lookup; ramo CF intacto |
| Literais `"CF88"` em `buscarMelhorLookupJurisCF` e no rótulo de contexto | BLOCKER | `normaJurisConsulta` (padrão `"CF88"`) |
| `LookupJurisCFCache.norma[8]` | **BLOCKER oculto** | IDs do catálogo com mais de 7 caracteres (ex.: `HEDIONDOS1990`) eram truncados e nunca casavam; o campo passou a `[16]` |
| Seleção da norma | GENERIC (novo) | `normaJurisAtual()` usa a tabela **gerada do Catálogo Mestre** (71 normas). Pasta de uma norma identifica pela pasta; pasta compartilhada exige o nome do arquivo. Sem correspondência, retorna `""` (fail closed). As 72 normas foram conferidas contra os arquivos do cartão J2H, sem conflito |
| ADCT | CF_SPECIAL_CASE | Sub-namespace no runtime da CF. A jurisprudência do ADCT continua vindo da camada LEXV1 (`REF_PAYLOAD`), porque o `JUR_LOOKUP` não tem linhas ADCT. Comportamento inalterado |
| Caminhos `JUR_LOOKUP`, `JURISPRUDENCIA.IDX`, `03_CONTEUDO` | GENERIC | O formato já tinha `ORIGEM_NORMA`; as fichas são compartilhadas entre normas (ex.: `STF_RG_932.TXT`, já no cartão, serve à CF e ao CC) |
| Abertura direta da lista única | CF_SPECIAL_CASE | Estendida ao ramo multinorma |

**Medidas** (compilado com esp32 3.3.11, mesmo FQBN; `firmware_multinorm/MULTINORM_PROTOTYPE_BUILD.json`):

| Item | Base J2I (recompilada) | Multinorma | Δ |
|---|---:|---:|---:|
| Programa | 1.102.031 B | 1.107.119 B | **+5.088 B** |
| RAM estática | 126.148 B | 126.172 B | **+24 B** |
| app0 livre | 208.544 B | 203.456 B | −5.088 B |

- **PSRAM:** +8 B por lookup (+1.896 B no cartão J2I).
- **Boot:** nenhuma leitura nova.
- **Limites:** 4096 lookups, 32 relações por artigo e quantidade ≤ 255, inalterados.
- **Não verificado:** teste físico, tempos reais no ESP32, PSRAM em execução.

**Simulação** (`multinorm_sim.py`, que espelha as funções C; `tests/test_multinorm_firmware_sim.py`):

| Teste | Resultado |
|---|---|
| CF | Idêntica ao firmware J2I nas 237 linhas de lookup (355 registros), nos dois pacotes. CF315 e CF198 inalterados |
| ADCT | Caminho anterior (`PREVIOUS_FLOW`) |
| Código Civil | Target → lista → ficha → BACK, com rótulos `ADI 4815`, `RG TEMA 498/809/932`. Contexto "ART. 927, PAR. UNICO". Fallback do inciso para o artigo |
| Alternância CF → CC → CF | Estado idêntico ao voltar |
| Norma sem jurisprudência (CPC, Lei 8.429) | Fluxo anterior |
| Namespace inválido ou arquivo fora do catálogo | `""`, fail closed; offset desalinhado recusa o cache inteiro |

**Achado lateral (pré-existente):** o `JUR_LOOKUP` do J2I tem chaves repetidas, porque a J2G/J2H acrescentaram grupos novos para targets que já tinham linhas: são 221 chaves distintas em 237 linhas. O caminho legado devolve só o primeiro grupo, nos dois firmwares. Na CF isso não aparece no aparelho, porque a lista vem da camada LEXV1. **Para outras normas, que usam o caminho legado, o empacotador deve fundir grupos da mesma chave.** O pacote de simulação do CC já usa um grupo por chave.

## 2. Bloqueador 2 — alínea sem inciso

- **Regra:** `namespaces.json: alinea_requires_inciso = [CF88, ADCT]`. CF e ADCT continuam estritos; nos demais namespaces, `NS:ART.n:AL.x` (pai = caput) e `NS:ART.n:PAR.n:AL.x` (pai = parágrafo) são válidos.
- **Exemplos reais** do texto oficial (Planalto, 2026-10-18), contando dispositivos distintos: CP 24 (ex.: `CP1940:ART.7:PAR.2:AL.a`), CPP 43, CTN 7, CLT 388. Todos passam pela ida e volta parse → serialize → parse sem perda. Anomalias após a extensão: 0.
- **Compatibilidade:** `EXISTING_TARGET_IDS_CHANGED = 0`. Os 9.914 IDs distintos de 38 índices versionados (todos os `CF88_TARGETS.IDX`, `TARGET_INDEX` da CF e o `CC2002_TARGET_INDEX`) têm parse e serialização idênticos.

## 3. Bloqueador 3 — STJ

```
STJ_AUTOMATION = PARTIAL · STJ_SUMULA403_OFFICIAL_SOURCE = RESOLVED · CAPTCHA_OR_CHALLENGE_BYPASSED = NO
```

| Via oficial | Resultado |
|---|---|
| `scon.stj.jus.br` (pesquisa e súmulas) | Desafio anti-robô (403); não contornado |
| `www.stj.jus.br` (portal, revista de súmulas) | "Request Rejected" para cliente automatizado |
| `dadosabertos.web.stj.jus.br` (dados abertos, API CKAN) | Sem resposta (timeout de 40 s) |
| Página "Súmulas do STJ" (`processo.stj.jus.br/SCON/sumstj/`) → **PDF oficial completo** (`/SCON/getFile?url=.../SumulasSTJ.pdf`) | **Disponível**: 40 MB, sha256 `bf92bdb1…`; download autorizado pela missão |

**Adaptador** `discovery_stj_sumulas.py`:
- 676 súmulas: 641 vigentes, 5 alteradas, 29 canceladas, 1 revogada.
- De cada uma extrai enunciado, órgão, data, fonte e as **referências legislativas estruturadas do próprio STJ**, mapeadas para targets via catálogo (0 rejeições).
- **Pares por norma:** CF88 180, CTN 79, CP 71, CC2002 59, LEP 43, CDC 38, CPP 31, CPC2015 22, CLT 11, CE 1.
- **Juízo temporal necessário:** referências só a leis revogadas, CPC/73 em 215 casos e CC/16 em 46.

**Súmulas resolvidas em fonte oficial** (`JURISPRUDENCE_AUDIT/STJ_OFFICIAL_SOURCE_RESOLUTIONS.json`). O estado editorial continua UNRESOLVED_EXTERNAL e nada foi materializado.
- **Súmula 403:** "Independe de prova do prejuízo a indenização pela publicação não autorizada de imagem de pessoa com fins econômicos ou comerciais." Segunda Seção, 28/10/2009, DJe 24/11/2009. Referências: CF 5º V e X; CC/02 186 e 927.
- **Súmula 203:** CF 105, III.

**Por que PARTIAL:**
- Súmulas são automatizáveis pelo PDF oficial.
- Acórdãos, temas repetitivos (precedentes qualificados) e pesquisa livre continuam atrás do anti-robô.

**Intervenção humana necessária para a "fábrica":** uma das três opções abaixo.
1. Pedir ao STJ acesso institucional ou API (ou confirmar a disponibilidade do portal de dados abertos).
2. O usuário baixa periodicamente os arquivos oficiais de repetitivos/precedentes e os entrega ao pipeline.
3. Abrir manualmente as páginas oficiais dos casos selecionados.

## 4. Tabela de tipos (fonte única)

- **Fonte única:** `juris_types.device_status()`, com `PHYSICALLY_VALIDATED` = RG, SV, ADI, HC, MS, AP, AI, Inq, Rcl, ADPF, Súmula STF e Súmula TSE (J2I 32/32).
- **`j2_review_common`:** consulta essa função a partir do Batch11. Os Batches 03–10 usam a tabela antiga congelada.
- **Hashes:** `HISTORICAL_BATCH_HASHES_UNCHANGED = YES`. Os 7 arquivos fixados nas ratificações conferem, e todos os lotes 03–10 passam no `--check`.

## 5. Piloto do CC refeito (sem publicar)

| | Antes (5e7e4f6) | Depois, mesmos 20 candidatos |
|---|---|---|
| Etapas automáticas | 133/140 | **133/140** |
| Candidatos ponta a ponta | 9 | 9 |
| Com julgamento humano | 11 | 11 |
| Pares distintos (canais STF) | 18 | 18 |

**Leitura honesta:** os bloqueadores atacados não mudam essas etapas, e por isso os números são iguais; não alterei critério para mostrar melhora. O ganho real está no **alcance**: o canal STJ mede 59 pares para o CC2002 (33 súmulas, 46 targets).
- **Etapas mecânicas do canal STJ:** 412 de 413 automáticas. A única falha é um target fora do índice do aparelho.
- **Alertas temporais:** 14 reais (por exemplo, arts. 757 e seguintes, de seguros, alterados pela Lei 15.040/2024; art. 406, pela Lei 14.905/2024).
- **Súmulas só sobre o CC/1916:** 34, que exigem juízo temporal.
- **Pertinência:** a pertinência material de cada par **não foi avaliada**, porque o CC não foi expandido além do piloto.
- **Alcance total:** os pares distintos alcançáveis passam de **18 para 77**.

**Simulação no firmware multinorma:** `CC_SIMULATION_ON_MULTINORM_FW = PASS`. O pacote `SIMULATION_ONLY` tem 7 relações (5 lookups) sobre os bytes J2I intactos.

## 6. Estimativa de escala V2

| Dimensão | Estado |
|---|---|
| **Pesquisa jurídica** | Por candidato, **2x–3x** (sem mudança em relação ao piloto). Onde há fonte estruturada (súmulas do STJ), as etapas mecânicas são praticamente 100% automáticas e o humano fica só com pertinência e temporalidade |
| **Materialização** | Ainda **não generalizada**: os empacotadores atuais são da CF. Com o caminho legado multinorma, uma norma nova precisa de um gerador de `JUR_LOOKUP`/`JURISPRUDENCIA.IDX`/fichas por norma, que é o mesmo padrão do pacote de simulação, e de fusão de grupos por chave. Estimativa: 1 empacotador genérico serve todas as normas |
| **Firmware** | Com o protótipo, **qualquer norma do catálogo sem patch novo** (dados apenas). Falta compilar o candidato definitivo, gravar e fazer o teste físico |
| **Fonte** | STF: pronto. STJ: súmulas prontas, acórdãos e repetitivos parciais. TST e TSE: **não testados** |

| Norma | Tribunal dominante | Motor | Fonte | Firmware | Dificuldade |
|---|---|---|---|---|---|
| CF | STF | pronto | pronto | pronto (físico) | LOW (backlog restante sem identificador) |
| CC | STJ/STF | pronto | STF pronto + súmulas STJ (59 pares); repetitivos parcial | protótipo pronto (simulação PASS) | **MEDIUM** |
| CPC | STJ/STF | pronto | súmulas STJ 22 pares (+215 só CPC/73); repetitivos parcial | protótipo pronto | HIGH |
| CP | STF/STJ | pronto (gramática estendida) | súmulas STJ 71 pares; STF pronto | protótipo pronto | MEDIUM |
| CPP | STF/STJ | pronto (gramática estendida) | STF (HC) pronto; súmulas STJ 31 | protótipo pronto | MEDIUM |
| CTN | STF/STJ | pronto (gramática estendida) | STF (RG) pronto; súmulas STJ 79 | protótipo pronto | **MEDIUM (bom candidato)** |
| CLT | TST/STF | pronto (gramática estendida, 388 alíneas) | TST **não testado**; súmulas STJ 11 | protótipo pronto | HIGH |
| Eleitoral | TSE/STF | pronto | TSE **não testado** (Súmula 9 TSE já validada no aparelho) | protótipo pronto | MEDIUM-HIGH |

## 7. Próximo passo recomendado

**A — começar o CC de verdade.**
- **Infraestrutura:** o CC já tem o perfil, os 3 canais de descoberta (Planalto, STF e súmulas do STJ), o índice do aparelho, nenhuma lacuna de gramática e a simulação no firmware multinorma aprovada.
- **Alcance:** já são 77 pares distintos alcançáveis, contra 18 antes do sprint.
- **Restrições:**
  - publicar exige gravar o firmware multinorma, com missão e teste físico próprios;
  - o empacotador genérico precisa fundir grupos da mesma chave;
  - os repetitivos do STJ continuam parciais.
- **Por que não B:** o Batch11 da CF rende pouco (59 itens sem identificador).
- **Por que não C:** TST e TSE podem esperar a próxima norma que dependa deles, porque o CC não depende.
