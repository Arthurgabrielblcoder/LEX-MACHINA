# C3B.2 — plano do terceiro teste físico (preparado, NÃO executado)

**Candidato `C3B2_CANDIDATE_HOST_ONLY`.** Não é baseline nem aprovado. Nada foi copiado para nenhum cartão.

- **Bytes iguais ao C3B.1:** os arquivos do aparelho são byte a byte os do C3B.1.
  - A auditoria C3B.2 (`C3B2/C3B2_ROOT_CAUSE_REPORT.md`) não encontrou defeito de dados nas duas falhas residuais.
  - As expectativas físicas é que divergiam das decisões humanas registradas.
- **Se você aceitar as expectativas corrigidas:** o resultado físico do C3B.1 já cobre os testes, e basta reconfirmar os 3 itens abaixo.
- **Se preferir outro destino** (ex.: a LC 63 abrindo no início da norma): isso é uma NOVA decisão jurídica. Ela entra como decisão humana e gera outro candidato.

## Arquivos do pacote (idênticos ao C3B.1)

| Caminho no cartão | SHA256 baseline | SHA256 candidato |
|---|---|---|
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `616a469b11dd673347dc665232a83fc8d5bcd8e3c6bfd5f07a4a56c62f5972a7` | `d2fcc15bbe41ef16c51bbe1ef7cb201bd9677b6ac54198b96ad2abc08395e06c` |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` | `27c67eea6a38e3cba012d4a3d02c3856d37fd4cd1bae15473854fab0edea5430` |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` | `1762642d337aff83ac5b95e074235bc58028b8a68bac17a384e9eed4a4a5addd` |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` | `a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad` | `5c54face7ea7eff62dbbb0a4193b5e2452e7fb03d82012d09919e74d234b3e5e` |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` | `bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d` | `691790f3ee5d4aaa9b88235bca33008357b99d87324c07b1da8b51355c20685c` |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` | `863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e` | `efac06cee0a1d8f0676564ba128d0ab8f474b89399f40de6422cc6fded37ef2c` |

- **Cache do firmware:** REL_LOOKUP 26/64 linhas; 15/32 normas.
- **Instalação e rollback:** mesmo procedimento do `C3B1_PHYSICAL_TEST_PLAN.md`, com os hashes desta tabela.

## Testes com expectativa corrigida

| # | Onde | Expectativa corrigida (decisão registrada) |
|---|---|---|
| 3 | CF art. 158, § 1º, I | LC 63/1990 abre NO art. 3º (critério e definição do valor adicionado), não no início da norma |
| 5 | CF art. 161, I | LC 63/1990 abre NO art. 3º (definição do valor adicionado, art. 3º, § 1º), não no início da norma |
| 7 | CF art. 202 (caput) | LC 109/2001 CONTINUA, abrindo no art. 1º (KEEP legado); no § 1º, a LC 109 abre no art. 3º (decisão HIGH independente) |

## Regressão mínima (já PASS no C3B.1; repetir só se reinstalar)

- Art. 202, § 5º → LC 108 no art. 26.
- Art. 158, § 1º, II, art. 214, I a VI, art. 37, § 3º, III e art. 37, II: sem `1 CORR.`.
- Art. 214 (caput) e art. 239, § 3º: com `1 CORR.`.
- Art. 150, § 7º → LC 87 no art. 10.
- Lei 14.965 ausente nos arts. 131, § 2º e 132.
- ENTENDA, JURIS e REFERÊNCIAS sem efeito colateral.

