# 09_CATALOGO_EXPANSAO_200 — Relatório final (retomada após o Codex)

> **Atualização 2026-09-26 (saneamento pré-enriquecimento):** as contagens abaixo são as da conclusão da expansão. Após o saneamento: 28 APTA, 171 APTA_COM_RESSALVA, 0 FONTE_EM_REVISAO, 1 duplicata, 199 utilizáveis, 221 cards. Ver `SANEAMENTO_PRE_ENRIQUECIMENTO.md`.

Concluído em 2026-09-26. Os números vêm de `METRICAS_FINAIS.json`, `ESTADO_FINAL.json` e `08_MANIFEST/INTEGRIDADE_DEPOIS.json`.

Nesta missão **a Engine não foi executada** e **nenhum vínculo obra↔dispositivo foi gerado**.

## 1. Ponto exato de retomada

- **Lotes fechados:** 1–4 (candidatas 1–100), com checkpoint; os 205 hashes do checkpoint conferem.
- **Lote 5 interrompido sem checkpoint:**
  - 101–120 tinham só `BUSCA_*.json` (listas de título e URL, sem fonte selecionada nem paráfrase);
  - 121–125 não tinham nenhum arquivo.
- **Primeira candidata não processada:** #101 The People v. O.J. Simpson.
- Registro completo em `RETOMADA_APOS_CODEX.md` e `ESTADO_RETOMADA.json`.

## 2. Trabalho do Codex reaproveitado

- **333 arquivos preservados.** Os 332 anteriores à retomada seguem com mtime inalterado. `CHECKPOINT_LOTES.json` só recebeu, por append, as entradas dos lotes 5–8.
- **Decisões dos lotes 1–4 mantidas:** 100 decisões editoriais e 97 dossiês; nenhuma alterada, já que não houve erro objetivo.
- **Buscas reaproveitadas:** `BUSCA_101..120` serviram de ponto de partida, sem repetir as buscas. Em 18 das 20 candidatas, a fonte final saiu da própria lista do Codex. As exceções foram #114 e #120, cujas URLs da lista estavam fora do ar ou bloqueadas.
- **Scripts:** `editorial.py` foi reutilizado sem alteração como processador dos lotes 5–8. `from_table.py` foi preservado, mas não foi usado, porque pré-decidia status de candidatas ainda não pesquisadas.

## 3. Arquivos incompletos ou inconsistências encontradas

- `BUSCA_101..120` brutos, sem seleção de fonte.
- `BUSCA_51..54` ausentes, embora o lote 3 esteja fechado.
- `05_REJEITADAS/REJEICOES.json` inexistente.
- `from_table.py` com status pré-fixados para 126–200.
- `pais_origem` nulo nas 100 primeiras.
- Mensagem de handoff com "~73 arquivos", quando eram 333.

## 4. Candidatas recebidas

**200:** 50 jogos, 40 filmes, 35 séries, 35 documentários e 40 livros. Cada uma tem estado final e nenhuma desapareceu.

## 5. APTA

**28**: 8 documentários e 20 livros.

## 6. APTA_COM_RESSALVA

**167**.

## 7. FONTE_EM_REVISAO

**3**:

| # | Obra | Pendência |
|---|---|---|
| 41 | Kingdom Come: Deliverance II | Descrição oficial insuficiente (decisão do Codex) |
| 113 | Black Mirror | Antologia; exige curadoria por episódio |
| 142 | Terms and Conditions May Apply | Páginas bloqueadas; conteúdo só por resultado de busca |

## 8. Rejeitadas por categoria

| Categoria | Total | Obras |
|---|---|---|
| REJEITADA_DUPLICATA_EXISTENTE | 1 | #92 The Wire |
| REJEITADA_EVIDENCIA_FRACA | 1 | #9 Cyberpunk 2077 (decisão do Codex) |
| REJEITADA_FONTE_INSUFICIENTE | 0 | — |
| REJEITADA_REDUNDANCIA_EXTREMA | 0 | — |
| REJEITADA_INCOMPATIBILIDADE | 0 | — |

**Soma: 28 + 167 + 3 + 2 = 200.**

## 9. Duplicatas

**1:** #92 The Wire = `EXP-SER-002` A Escuta (título original The Wire, 2002). A tradução PT-BR não gerou nova obra.

## 10. Novas obras utilizáveis

**195** (APTA + APTA_COM_RESSALVA).

## 11. Total potencial com as 69

- **69 + 28 APTA = 97**
- **69 + 195 utilizáveis = 264**

Tudo com `status_catalogo = CANDIDATO_NAO_INTEGRADO`.

## 12. Jogos (50)

- **Estados:** 0 APTA, 48 APTA_COM_RESSALVA, 1 FONTE_EM_REVISAO, 1 rejeitado.
- **Tipo de evidência:** 34 com evidência mecânica (MECANICA_INTERATIVA) e 14 com evidência narrativa.
- Detalhes em `JOGOS_EXPANSAO.md`.

## 13. Filmes (40)

40 APTA_COM_RESSALVA (lotes 3–4, do Codex).

## 14. Séries (35)

33 APTA_COM_RESSALVA, 1 FONTE_EM_REVISAO e 1 duplicata.

## 15. Documentários (35)

8 APTA, 26 APTA_COM_RESSALVA e 1 FONTE_EM_REVISAO.

- **APTA:** Coded Bias, The Cleaners, We Are Guardians, Ônibus 174, Notícias de uma Guerra Particular, Juízo, A Lei da Água e Cidadão Boilesen.
- **Formato:** Dirty Money foi mantida como DOCUMENTÁRIO, com subtipo SERIE_DOCUMENTAL.

## 16. Livros (40)

20 APTA e 20 APTA_COM_RESSALVA.

## 17. Evidence cards

**213**, todas com `not_targeted_to_device: true`.

- **Centralidade:** 195 CENTRAL, 17 FORTE, 1 PONTUAL.
- **Tipo de conteúdo:**

| Tipo | Cards |
|---|---|
| EVENTO_NARRATIVO | 96 |
| MECANICA_INTERATIVA | 34 |
| EVENTO_HISTORICO | 28 |
| ARGUMENTO_ACADEMICO | 27 |
| ARGUMENTO_DOCUMENTAL | 15 |
| EVENTO_AUTOBIOGRAFICO | 9 |
| PRATICA_INSTITUCIONAL | 4 |

Toda obra utilizável tem ao menos 1 card CENTRAL.

## 18. Fontes por tier

- **Registros de fonte (239):** A 159, B 60, C 20.
- **Fonte principal dos cards:** A 142, B 58, C 13.
- **Forma de verificação nos lotes 5–8:**
  - 110 páginas efetivamente consultadas;
  - 17 apoios obtidos por resultado de busca;
  - 4 páginas bloqueadas.
- Os lotes 1–4 (Codex) não registram a forma de verificação.

## 19. Lacunas jurídicas restantes

Mapa editorial em `COBERTURA_EDITORIAL.json`; não é saída da Engine.

- **Permanecem POBRES:** sucessões (herança), propriedade intelectual, processo civil, deficiência e responsabilidade civil.
- **MODERADAS:** contratos/obrigações, eleitoral, infância e adolescência, povos indígenas.

Nenhum vínculo foi inventado para preencher lacuna.

## 20. Redundâncias

Nenhuma candidata chegou ao nível de redundância extrema. As principais proximidades:

- **Caso Snowden em três mídias:** #61, #126, #180.
- **Theranos:** #117 e #181.
- **Opioides:** #98 e #182.
- **Carandiru:** filme #84 e livro #194.
- **Proximidade mecânica com Papers, Please:** #46 e #32.
- **Proximidade temática com obras das 69:**
  - #171 com A 13ª Emenda;
  - #134 com Privacidade Hackeada;
  - #136 com A Grande Aposta.

Detalhes em `REDUNDANCIA_69_MAIS_200.json` e `.md`.

## 21. Determinismo

`compilar_catalogo.py` foi executado 2 vezes, mais a gravação local. Os hashes das três saídas são idênticos:

| Arquivo | SHA-256 |
|---|---|
| CATALOGO_EXPANSAO_200.json | `8f107e65d7b3184b80aff40226c93d93b02c9631cf803048c33703690ecfac38` |
| CATALOGO_TOTAL_69_MAIS_APTAS.json | `5c31b22450c74e6bc08661bd956bdf5f74e7f470feef1e6be1887a91c86db9ba` |

Registro em `DETERMINISMO_COMPILACAO.json`.

## 22. Integridade

| Item | Resultado |
|---|---|
| Congelados da V2 | 281/281 idênticos |
| Engine R1D1 | 65/65 |
| RC1 | 15/15 |
| RC2 | 6/6 |
| Holdout | 3/3 |
| Ontologia e contratos | 37/37 |
| Catálogo 69 | sha256 igual ao declarado |
| Firmware | hash inalterado; a modificação `M` no git é de 2026-09-17, anterior à missão |
| IDX (130 arquivos) | nenhum alterado |
| SD | não tocado |
| Arquivos fora da pasta da missão | 0 alterados |

## 23. Arquivos produzidos na retomada

- **Triagem e processamento:**
  - `02_TRIAGEM/lote_retomada.py`;
  - `CURADORIA_RETOMADA_05..08.json`;
  - `LOTE_05..08.json`.
- **Identidade:** `01_IDENTIDADE/LOTE_05..08.json`.
- **Fontes e dossiês:**
  - `03_FONTES/EXP2-SER-011..035`, `EXP2-DOC-*` e `EXP2-LIV-*`;
  - `04_DOSSIERS`: 98 novos dossiês.
- **Rejeições e revisão:** `05_REJEITADAS/REJEICOES.json` e `FONTE_EM_REVISAO.json`.
- **Relatórios (`06_RELATORIOS`):**
  - `RETOMADA_APOS_CODEX.md`, `ESTADO_RETOMADA.json` e `ESTADO_FINAL.json`;
  - `CORRECOES_ENTRADA.json` e `REDUNDANCIA_69_MAIS_200.json/.md`;
  - `JOGOS_EXPANSAO.md`, `METRICAS_FINAIS.json` e `COBERTURA_EDITORIAL.json`;
  - `DETERMINISMO_COMPILACAO.json`, `RELATORIO_FINAL.md`;
  - scripts `estado_retomada.py` e `gerar_relatorios.py`.
- **Catálogo candidato:** `07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json`, `CATALOGO_TOTAL_69_MAIS_APTAS.json` e `compilar_catalogo.py`.
- **Manifesto:** `08_MANIFEST/INTEGRIDADE_DEPOIS.json`, `MANIFEST.json` e `gerar_manifest.py`.
- **Checkpoint:** `CHECKPOINT_LOTES.json` recebeu as entradas dos lotes 5–8 por append.

## 24. 20 obras mais promissoras

Juízo editorial, não score da Engine.

1. Juízo (#157)
2. Rota 66 (#195)
3. Holocausto Brasileiro (#193)
4. Estação Carandiru (#194)
5. A Lei da Água (#158)
6. Ônibus 174 (#155)
7. Notícias de uma Guerra Particular (#156)
8. Cidadão Boilesen (#160)
9. The Rule of Law (#161)
10. The Spirit of the Laws (#163)
11. On Liberty (#162)
12. Coded Bias (#140)
13. Weapons of Math Destruction (#177)
14. The Immortal Life of Henrietta Lacks (#183)
15. Phoenix Wright: Ace Attorney Trilogy (#2)
16. Crusader Kings III (#25)
17. Designated Survivor (#109)
18. Succession (#106)
19. A Queda do Céu (#199)
20. We Are Guardians (#153)

## 25. Próximo passo recomendado

1. **Resolver as 3 FONTE_EM_REVISAO:**
   - #41: press kit;
   - #113: curadoria por episódio;
   - #142: página acessível.
2. **Fazer revisão humana amostral** das paráfrases dos lotes 1–4, que não têm registro de verificação.
3. **Mapear os cards na ontologia congelada.** Hoje todos carregam `ONTOLOGY_GAP` `REVISAO_SEMANTICA_PRE_INGESTAO`. O mapeamento deve ser feito numa missão própria, antes de qualquer ingestão pela Engine R1D1.
4. **Buscar candidatas dirigidas às lacunas** (sucessões, processo civil, propriedade intelectual, deficiência e responsabilidade civil) numa expansão futura. Nesta missão, nenhum vínculo foi forçado para cobri-las.
