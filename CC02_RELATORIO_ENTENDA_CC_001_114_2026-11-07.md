# LEX MACHINA — CC-02 — relatório final

Data de fechamento: 2026-11-07  
Escopo: camada editorial ENTENDA do Código Civil, arts. 1 a 114  
Resultado: candidato tecnicamente validado, integralmente pendente de revisão jurídica humana

## 1. Branch e baseline

- Branch isolada: `cc02-entenda-cc-001-114`
- Worktree: `C:\GitHub\LEX-MACHINA\.codex-build\cc02-worktree`
- Baseline: `3e247ea60593ba0524462281383749f351548a1a`
- Commit da fonte/estrutura: `ffa4bcbc16b5d5fba8ce1b3a8a896a845f38ecaf`
- Commit do corpus candidato: `5a243cff58f263ba9ef4d0953d96784557c42f0e`
- Push, merge e tag: não realizados

## 2. Fonte jurídica

A fonte operacional auditada em CC-01 foi preservada byte a byte e confrontada com a consolidação oficial da Câmara dos Deputados:

- Fonte operacional completa: `DEVICE_INTEGRATION/backups/sd_20260929T163407Z/data/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt`
- SHA-256 da fonte completa: `ad5ba178613b6181e2d8a61919eda0c6223c68feb6e47bef4ea65bc45c13e6ae`
- Recorte versionado, do art. 1 ao limite anterior ao art. 115: `SOURCE_CC2002_ARTS_001_114.txt`
- SHA-256 do recorte: `0c927ce1d9817c5db5b3a1c563d8320eb334431495afeb3745a0fc8bc399e385`
- Página oficial da norma: <https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-norma-pl.html>
- Texto oficial consolidado: <https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html>

O recorte produz 378 alvos estruturais, sem duplicidade e sem anomalia do parser: 117 artigos, 117 caputs, 29 parágrafos, 24 parágrafos únicos, 90 incisos e 1 raiz normativa.

## 3. Cobertura editorial

- Artigos numéricos esperados: 114
- Artigos numéricos explicados: 114
- Artigos alfanuméricos vigentes adicionais: 48-A e 49-A
- Explicações ativas: 116
- Subdivisões presentes nos snapshots dos artigos: 259, desconsiderado o caput vetado do art. 69-A
- Art. 69-A: bloqueado; consta como vetado e não recebeu explicação ativa
- Status das 116 explicações: `PENDING_HUMAN_REVIEW`
- Status de produção aprovado: 0

Os checkpoints ficaram assim:

| Bloco | Explicações | Observação |
|---|---:|---|
| 1–25 | 25 | artigos numéricos |
| 26–50 | 27 | inclui 48-A e 49-A |
| 51–75 | 25 | 69-A vetado excluído; art. 69 vigente incluído |
| 76–100 | 25 | artigos numéricos |
| 101–114 | 14 | artigos numéricos |

## 4. Tratamento de vigência

Foi criado status explícito para nove alvos revogados ou vetados mantidos na fonte consolidada: incisos I a III do art. 3; inciso III do art. 10; inciso VI do art. 44; parágrafo único do art. 57; inciso X do parágrafo único do art. 62; art. 69-A e seu caput. Esses alvos não são tratados silenciosamente como vigentes.

O corpus explica cada artigo como unidade autônoma `OVERVIEW`, incorpora sua árvore estrutural ao snapshot de proveniência e não cria explicações independentes para subdivisões nesta missão.

## 5. Validação técnica

Comandos de aceitação executados:

```text
python -X utf8 ENTENDA_ENGINE\build_entenda_cc02.py
python -X utf8 ENTENDA_ENGINE\build_entenda_cc02.py --check
python -m unittest ENTENDA_ENGINE.tests.test_entenda_cc02
python -m unittest ENTENDA_ENGINE.tests.test_entenda_engine
```

Resultados:

- Build ENTENDA-T1: aprovado
- Rebuild determinístico: aprovado
- Testes específicos CC-02: 3/3 aprovados
- Regressão do motor ENTENDA: 19/19 aprovados
- Alertas editoriais do manifest: 0
- Duplicidades de explicação ativa: 0
- Cópia textual acima do limite: 0
- Alterações em firmware, microSD ou índices de produção: 0

## 6. Hashes do pacote candidato

- Corpus JSONL: `86ef8d8f1843650e927b2fd2fd620dd92a7fe9508dac8934efbaae238beecd4d`
- Lookup IDX: `8fad30f2865fa86995b90f031059d75d35b1d6df14eef73c56c558afe963e4c4`
- Payload DAT: `6ce9f62df0fd4ffe8048d9c91fd8b369da8df769f05b4e0f920c8071378a3f20`
- Manifest de build: `fcea66013dab8f237a7aa5d93125256d68c02b741369ea4853975bf175f3b18d`
- Índice estrutural de target IDs: `b1c59263a251dd928d41546d54df330cc2c97bc3419e3f1650be4c53acaf1315`

## 7. Riscos jurídicos e classificação

Classificação do lote:

- Tecnicamente validados: 116
- Pendentes de revisão jurídica humana: 116
- Bloqueados: 1, o art. 69-A vetado
- Aprovados para produção: 0

Prioridade alta de revisão: personalidade e capacidade; morte presumida; direitos da personalidade e bioética; responsabilidade pública; tipos recentes de pessoas jurídicas; desconsideração; associações e fundações; domicílio necessário; bens públicos; e teoria do negócio jurídico, especialmente arts. 104, 108, 110, 111, 113 e 114.

O arquivo `CC02_LEGAL_REVIEW.json` contém os grupos, motivos e protocolo. Nenhuma afirmação de aprovação humana foi gerada automaticamente.

## 8. Arquivos principais

- Gerador reproduzível: `ENTENDA_ENGINE/build_entenda_cc02.py`
- Fonte editorial revisável: `ENTENDA_ENGINE/cc02_editorial.py`
- Fonte legal fixada e proveniência: `SOURCE_CC2002_ARTS_001_114.txt`, `SOURCE_PROVENANCE.json`
- Índice e status: `CC2002_TARGET_INDEX.json`, `CC2002_TARGET_STATUS.json`
- Drafts e corpus: `CC02_DRAFTS.json`, `CC2002_CC02.entenda.jsonl`
- Pacote host-only: `index/ENTENDA_LOOKUP.IDX`, `index/ENTENDA_PAYLOAD.DAT`, `index/ENTENDA_BUILD_MANIFEST.json`
- Controle: `CC02_COVERAGE.json`, `CC02_LEGAL_REVIEW.json`, `CC02_MANIFEST.json`, `checkpoints/`
- Testes: `ENTENDA_ENGINE/tests/test_entenda_cc02.py`

## 9. Completude e próximo lote

O objetivo editorial da CC-02 está completo como pacote candidato: os arts. 1 a 114 estão cobertos, os dois artigos alfanuméricos vigentes do intervalo foram acrescentados e o dispositivo vetado foi bloqueado. O lote não está juridicamente aprovado nem autorizado para deploy.

Próxima unidade sugerida: CC-03, revisão jurídica humana dos 116 registros em cinco blocos, com prioridade aos grupos de alta atenção; somente depois disso avaliar promoção para `HUMAN_APPROVED_T1`. A expansão editorial seguinte pode iniciar no art. 115, em missão separada e mantendo a mesma barreira de produção.
