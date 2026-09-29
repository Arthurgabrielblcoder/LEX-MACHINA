# ENTENDA CF Production Batch 02: arts. 6º a 17

Data: 2026-09-28. Estado: **PENDING_HUMAN_REVIEW** e **UNTRACKED** (sem stage, commit ou tag). Padrão: ENTENDA-T1 aprovado, com o adendo A3.

A folha de revisão está em `ENTENDA_ENGINE/derived/production_batch_02/REVIEW_BATCH_02.md`, agrupada por artigo. Cada explicação traz TARGET, DISPLAY TITLE, ROLE, COVERED TARGETS, as cinco seções, CAMADA EXTERNA, WARNINGS, STATUS e as caixas APROVAR, AJUSTAR ou REJEITAR.

## Números

| Métrica | Valor |
|---|---|
| Targets avaliados | 151 |
| Targets CURRENT | 151 |
| Revogados excluídos | 4. São alíneas com apenas a marca de revogação: art. 7º, XXIX, "a" e "b", e art. 12, § 4º, II, "a" e "b" (EC 131/2023) |
| Históricos excluídos | 0 |
| Selecionados (novas explicações) | **48**, dentro da meta de 30–55 e abaixo do teto de 65 |
| OVERVIEW / DEVICE / BLOCK / ITEM | 12 / 8 / 21 / 7 |
| NO_SEPARATE_EXPLANATION | 99, todos cobertos por uma explicação real (bloco ou visão geral) |
| Média de palavras | 201 |
| Média de bytes | 1.743 |
| Maior explicação | `CF88:ART.7:INC.I` (bloco despedida, seguro-desemprego, FGTS e aviso prévio): 2.418 bytes, 280 palavras |
| Payload | 83.750 bytes |
| Lookup | 8.457 bytes, 78 linhas (48 DIRECT e 30 COVERED_BY_BLOCK) |
| Targets com referências | 13 |
| Avisos de lint | 41, apenas consultivos |

Detalhe dos avisos de lint:

| Aviso | Qtde |
|---|---|
| Quase-cópia da Lei Seca (8–10 palavras) | 22 |
| Exemplo com linguagem de exigência | 10 |
| Repetição do pai | 3 (0,21 a 0,26, abaixo do bloqueio de 0,35) |
| Afirmação absoluta | 3 (dois falsos positivos em "incapacidade civil absoluta") |
| Termo de baixa utilidade | 2 |
| Termo difícil não usado no texto | 1 |

Antes do build, a trava de cópia (mais de 10 palavras seguidas) recusou 16 explicações; os trechos foram reescritos por paráfrase.

## Estratégia por artigo

| Artigo | Explicações | Estratégia |
|---|---|---|
| 6º | 1 (OVERVIEW) | Rol de direitos sociais e renda básica familiar (parágrafo único) na visão geral |
| **7º** | **13** de 39 targets | Ver "Art. 7º por famílias", abaixo |
| 8º | 5 | Visão geral da liberdade sindical, cobrindo os incisos I, V e VII e o parágrafo único. Explicações próprias: unicidade (II), representação e negociação (III + VI), contribuição confederativa (IV) e estabilidade do dirigente (VIII) |
| 9º | 1 | Greve: texto constitucional separado da lei de greve e da greve de servidores (art. 37, VII), que ficam como camada externa |
| 10, 11, 13, 16 | 1 cada | Artigos curtos: a unidade é o artigo |
| **12** | **6** | Ver "Art. 12: nacionalidade", abaixo |
| **14** | **11** | Ver "Art. 14: direitos políticos", abaixo |
| 15 | 1 | Vedação de cassação e as cinco hipóteses; a classificação perda × suspensão aparece como doutrinária |
| 17 | 6 | Visão geral (cobre §§ 2º e 4º), caput como BLOCK, § 1º (autonomia e coligações), BLOCK § 3º + § 5º (cláusula de desempenho, com a transição da EC 97/2017 na ATENÇÃO), § 6º (desfiliação) e BLOCK §§ 7º–9º (recursos para mulheres e para pessoas pretas e pardas) |

### Art. 7º por famílias

O art. 7º tem 34 incisos, mas não virou 34 explicações. Foram 13, montadas a partir do texto:

- **Visão geral** do artigo.
- **7 blocos:**
  - I + II, III, XXI (despedida, seguro-desemprego, FGTS e aviso prévio);
  - IV + V, VI, VII, X (salário);
  - VIII + IX, XVI, XXIII (décimo terceiro e adicionais);
  - XIII + XIV, XV, XVII (jornada e descansos);
  - XVIII + XIX, XX, XXV (maternidade, paternidade e creche);
  - XXII + XXVIII (saúde, segurança e acidentes);
  - XXX + XXXI, XXXII, XXXIV (igualdade e não discriminação).
- **4 itens isolados:**
  - XI (participação nos lucros);
  - XXVI (convenções e acordos coletivos);
  - XXIX (prescrição);
  - XXXIII (trabalho do menor).
- **Parágrafo único** (domésticos) como explicação própria.
- **Sem explicação própria, com motivo registrado:**
  - XII (salário-família): candidato, se a revisão pedir;
  - XXIV (aposentadoria): inciso de uma palavra, o regime está nos arts. 40 e 201;
  - XXVII (automação): comando que depende de lei.

### Art. 12: nacionalidade

- **Brasileiros natos:** bloco próprio (inciso I, com as alíneas "a" a "c"), com critério territorial, critério sanguíneo e opção depois da maioridade.
- **Naturalizados:** bloco próprio (inciso II, com as alíneas "a" e "b"), incluindo o regime facilitado para originários de países de língua portuguesa.
- **§ 1º:** portugueses com residência permanente, que não se tornam naturalizados.
- **Bloco §§ 2º–3º:** a regra de que natos e naturalizados são iguais, ligada aos cargos privativos de nato.
- **Bloco §§ 4º–5º:** perda e reaquisição da nacionalidade na redação da EC 131/2023. Adquirir outra nacionalidade não é mais causa de perda, e a apatridia é ressalvada.

### Art. 14: direitos políticos

- **Visão geral** do artigo.
- **Caput como BLOCK:** sufrágio, voto, plebiscito, referendo e iniciativa popular.
- **§§ 1º–2º:** alistamento e voto.
- **§§ 3º–4º:** condições de elegibilidade e inelegíveis.
- **Explicações próprias:**
  - § 5º, reeleição;
  - § 6º, desincompatibilização;
  - § 7º, inelegibilidade de cônjuge e parentes;
  - § 8º, elegibilidade do militar;
  - § 9º, inelegibilidades criadas por lei complementar (Lei Complementar 64/1990 e Lei da Ficha Limpa).
- **§§ 10–11:** ação de impugnação de mandato eletivo.
- **§§ 12–13:** consultas populares locais.

## Jurisprudência (recomendações; nada incorporado ao corpo)

São 12 recomendações. **7 estão `READY_TO_LINK`**: a identidade foi comprovada por `source_id` no acervo local curado, e o registro já está vinculado ao próprio target:

| Target | Recomendação |
|---|---|
| Art. 7º, IV | STF, SV 16 |
| Art. 7º, XXVIII | STF, Tema 932 |
| Art. 7º, XXIX | STF, Tema 608 |
| Art. 8º, IV | STF, SV 40 |
| Art. 14, § 5º | STF, Tema 564 |
| Art. 14, § 7º | STF, SV 18 |
| Art. 15, III | STF, Tema 370 |

A comprovação é pelo tribunal, tipo e número; o tema material não foi reverificado localmente.

**5 estão `PENDING_EXTERNAL_INGESTION`**:

- Tema 1046 (negociado sobre o legislado);
- substituição processual pelos sindicatos;
- greve de servidores;
- Lei da Ficha Limpa;
- fidelidade partidária de eleitos pelo sistema majoritário.

## Determinismo e testes

- O Batch 02 foi gerado duas vezes: BYTE_IDENTICAL. A reconstrução completa (`rebuild_all.py`) também deu BYTE_IDENTICAL.
- **Suíte ENTENDA: 46/46 OK.** Inclui 7 testes do Batch 02:
  - todo o escopo avaliado e pendente;
  - revogados excluídos;
  - sem duplicação com o Batch 01;
  - art. 7º sem explosão;
  - BLOCK e títulos de exibição;
  - recomendações jurisprudenciais só com identidade local;
  - build determinístico.
- **LEGAL_TARGET_ID: 47/47 OK.**

## Mudança de motor pendente (não commitada, faz parte do Batch 02)

`ENTENDA_ENGINE/production_batch.py` tem duas mudanças:

- classificação `EXCLUDED_REVOKED` para rótulos que só trazem a marca de revogação;
- `local_label` e `identity_basis` nas recomendações que encontraram registro local.

As duas não alteram as saídas do Batch 01 aprovado.

## Recomendação para a revisão humana

Pontos que merecem mais atenção:

1. **Art. 7º, I:** a afirmação sobre a lei complementar não editada e a remissão à indenização provisória do ADCT.
2. **Art. 7º, XVIII:** a licença-paternidade sem número fixo e a remissão ao ADCT e à legislação vigente.
3. **Art. 12, §§ 4º–5º:** a redação da EC 131/2023.
4. **Art. 14, § 3º:** a idade mínima e o momento de verificação, remetidos à legislação.
5. **Art. 15:** perda × suspensão como classificação doutrinária.
6. **Art. 17, § 3º:** a transição da cláusula de desempenho.
7. **Candidatos a explicação própria**, se a revisão pedir: art. 7º, XII (salário-família) e art. 8º, I (autonomia sindical).

---

## Adendo A4 (2026-09-28): Batch 02 aprovado pela revisão humana

### Decisões e lote final

- **Decisões:** 50 decisões em `ENTENDA_ENGINE/derived/production_batch_02/HUMAN_REVIEW_DECISIONS.json` (`HUMAN_REVIEW_COMPLETED`, escopo `CF88_ARTS_6_17`).
  - 23 APPROVED, contando as duas explicações criadas pela revisão.
  - 27 APPROVED_AFTER_ADJUSTMENT.
- **Explicações criadas pela revisão:**
  - `CF88:ART.7:INC.XII`: "Art. 7º, inciso XII — Salário-família";
  - `CF88:ART.8:INC.I`: "Art. 8º, inciso I — Liberdade sindical: registro não é autorização".
- **Lote final** (`ENTENDA_ENGINE/derived/production_batch_02_final/`):
  - **50 explicações**, todas `HUMAN_APPROVED_T1`;
  - 27 versões anteriores ficaram `RETIRED`;
  - o lote pendente foi preservado como evidência congelada.

### Vigência em dois eixos

- **Contagem:** 151 targets estruturalmente presentes, 147 vigentes e 4 `REVOKED`: art. 7º, XXIX, "a" e "b", e art. 12, § 4º, II, "a" e "b".
- **Tratamento dos revogados:** continuam reconhecíveis na estrutura, mas não recebem ENTENDA vigente e não entram na contagem CURRENT.

### Notas temporais

São 3 notas, com data de referência 2026-09-28:

| Target | Nota | Estado em 2026-09-28 | Revisar após |
|---|---|---|---|
| Art. 7º, XVIII (licença-paternidade) | Lei 15.371/2026: vigência em 2027-01-01; transição de 10, 15 e 20 dias; até lá permanece relevante o ADCT, art. 10, § 1º | `NOT_YET_EFFECTIVE` | 2027-01-01 |
| Art. 14, § 3º (idade mínima) | Momento de aferição conforme a Lei 9.504/1997, art. 11, § 2º | — | 2027-09-28 |
| Art. 17, § 3º (cláusula de desempenho) | Transição da EC 97/2017 nas eleições de 2026: 2,5% dos votos válidos com 1,5% por unidade, ou 13 deputados; regime permanente a partir de 2030 | escopo `ELEICOES_2026` | 2027-01-01 |

### Jurisprudência

São 16 recomendações:

- **7 `READY_TO_LINK`**, com assunto comprovado no texto oficial da tese armazenado localmente: SV 16, Tema 932, Tema 608, SV 40, Tema 564, SV 18 e Tema 370.
- **0 `IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION`.**
- **9 `PENDING_EXTERNAL_INGESTION`:**
  - Tema 1046 e Tema 935 (contribuição assistencial, separada da confederativa);
  - substituição processual pelos sindicatos;
  - greve de servidores;
  - Tema 1229 (a tese informada pela revisão fica em `human_supplied`);
  - Lei da Ficha Limpa;
  - TSE Súmula 9;
  - anualidade eleitoral e emendas constitucionais;
  - fidelidade partidária no sistema majoritário.

### Determinismo e testes

- **Build final:** duas vezes, BYTE_IDENTICAL.
- **Suítes:** ENTENDA 55/55 e LEGAL_TARGET_ID 47/47.
