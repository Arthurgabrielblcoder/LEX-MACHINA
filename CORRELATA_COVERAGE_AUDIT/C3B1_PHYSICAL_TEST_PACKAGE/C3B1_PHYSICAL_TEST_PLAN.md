# C3B.1 — plano do segundo teste físico (preparado, NÃO executado)

**Candidato `C3B1_CANDIDATE_HOST_ONLY`.** Não é baseline nem aprovado. Nada foi copiado para nenhum cartão. Arthur executa; o Claude não toca no cartão.

- **Origem:** corrige as duas causas raiz do primeiro teste C3B (`C3B_PHYSICAL_TEST_FAILURE_REPORT.md`).
  - Flags C antigas no `CF88_TARGETS.IDX`.
  - ID de relação compartilhado por várias linhas do `RELACOES.IDX`.

## Arquivos do pacote (somente os que mudam)

| Caminho no cartão | SHA256 baseline | SHA256 candidato | Bytes (baseline → candidato) |
|---|---|---|---|
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `616a469b11dd673347dc665232a83fc8d5bcd8e3c6bfd5f07a4a56c62f5972a7` | `d2fcc15bbe41ef16c51bbe1ef7cb201bd9677b6ac54198b96ad2abc08395e06c` | 165466 → 165466 |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` | `27c67eea6a38e3cba012d4a3d02c3856d37fd4cd1bae15473854fab0edea5430` | 6955 → 6702 |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` | `1762642d337aff83ac5b95e074235bc58028b8a68bac17a384e9eed4a4a5addd` | 68075 → 65248 |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` | `a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad` | `5c54face7ea7eff62dbbb0a4193b5e2452e7fb03d82012d09919e74d234b3e5e` | 15904 → 15960 |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` | `bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d` | `691790f3ee5d4aaa9b88235bca33008357b99d87324c07b1da8b51355c20685c` | 8101 → 4650 |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` | `863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e` | `efac06cee0a1d8f0676564ba128d0ab8f474b89399f40de6422cc6fded37ef2c` | 934 → 626 |

- **Cache do firmware:** REL_LOOKUP 26/64 linhas; 15/32 normas.
- **`CF88_TARGETS.IDX`:** muda só na posição C (disponibilidade de `1 CORR.`).
  - Não mudam ENTENDA (E/B), JURIS (J), obras (W), R, X, status, IDs nem a ordem.
- **Não mudam:** Lei Seca (05_TEXT), ENTENDA (30_ENTENDA), 00_SYS, textos das normas externas, EXT_NORMAS.IDX e firmware.
- **Aviso:** o `00_SYS/LEX_DEVICE_MANIFEST.json` registra o SHA dos REF_* e do TARGETS e ficará desatualizado durante o teste.
  - O firmware não lê esse arquivo; o rollback restaura a coerência.

## Procedimento

1. **Backup.** Com o aparelho desligado, retire o microSD e copie o cartão inteiro para uma pasta nova no PC. Confira que a cópia tem o mesmo número de arquivos.
2. **Identificar o cartão.** Confirme que `99_LEX_V1/00_SYS/LEXV1.VER` contém:
   - `BUILD_ID|de963699728cb66e`;
   - `GIT_COMMIT|fa9719a6bd335275252473a5f154e4e11f5532f4`;
   - `REFERENCE_ENGINE|cf-reference-engine-run3`.
   - Confira que o SHA256 de cada arquivo da tabela no cartão é o **baseline**. Se divergir, PARE.
3. **Copiar, nesta ordem**, de `candidate/SD/` para a raiz do cartão (cópia binária):
   1. `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX`
   2. `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX`
   3. `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX`
   4. `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX`
   5. `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX`
   6. `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX`
   - Os índices de relação vêm primeiro, depois os REF_* e por último o `CF88_TARGETS.IDX`.
   - Assim o `1 CORR.` só passa a ser anunciado quando as listas já estão no lugar.
4. **Conferir** cada SHA256 contra a coluna **candidato**.
5. **Ejetar**, reinserir no aparelho desligado e **ligar**. Esperado: boot normal.
6. **Executar os testes abaixo** e anotar OK/FALHA.
7. **Rollback** (qualquer falha ou dúvida): copiar de `rollback/SD/` TODOS os arquivos da tabela e conferir a coluna **baseline** (`C3B1_ROLLBACK_MANIFEST.json`).

## Testes manuais

| # | Cobre | Onde | Esperado |
|---|---|---|---|
| 1 | KEEP legado | CF art. 5º, XLIII | `1 CORR.` aparece; a Lei 13.260/2016 abre no art. 1º |
| 2 | ROUTE_FIX (reteste do teste 2) | CF art. 202, § 5º | a LC 108/2001 abre DIRETO no art. 26, e não no art. 1º |
| 3 | Mesma relação nos §§ 4º e 6º | CF art. 202, § 4º e § 6º | o § 4º abre o art. 1º; o § 6º lista a LC 108 nos arts. 11 e 20 |
| 4 | RETARGET (reteste do teste 3) | CF art. 158, § 1º, I e § 1º, II | no inciso I aparece `1 CORR.` com a LC 63 (art. 3º); no inciso II `1 CORR.` NÃO aparece |
| 5 | REPLACE | CF art. 161, I, II e III | I: LC 63 (art. 3º); II e III: LC 62 (art. 1º) |
| 6 | Novo HIGH (reteste do teste 5) | CF art. 202, § 1º | `1 CORR.` aparece; a LC 109/2001 abre no art. 3º (o caput continua com a LC 109 no art. 1º) |
| 7 | PNE (reteste do teste 6) | CF art. 214 (artigo/caput) e incisos I a VI | no artigo, `1 CORR.` com a Lei 15.388/2026; nos incisos I a VI, `1 CORR.` NÃO aparece |
| 8 | Salto LC 87 | CF art. 150, § 7º | abre no "Art. 10. É assegurado ao contribuinte substituído..." |
| 9 | Salto Lei 7.998 (reteste do teste 8) | CF art. 239, § 3º | `1 CORR.` aparece; abre no "Art. 9º É assegurado o recebimento de abono salarial..." |
| 10 | HOLD (reteste do teste 9, obrigatório) | CF art. 37, § 3º, III | `1 CORR.` AUSENTE; pressionar `1` não abre nada nem mostra lista; ENTENDA/JURIS/REFERÊNCIAS do dispositivo iguais ao baseline |
| 11 | Vacatio (reteste do teste 10) | CF art. 37, II; art. 131, § 2º; art. 132 | a Lei 14.965/2024 não aparece; no art. 37, II, `1 CORR.` AUSENTE (ENTENDA e JURIS continuam) |
| 12 | Outras camadas (teste 11) | CF art. 5º (caput), um dispositivo com ENTENDA e Lei Seca de qualquer norma | jurisprudência, obras, ENTENDA e texto iguais ao estado anterior; nenhuma tela de erro |

Visíveis DEVICE_READY no candidato: 24 vínculos CORRELATA. Fora do pacote:
- MAIN_CORPUS, ingestão e ADCT (bloqueados por ingestão);
- supressões temporais (Lei 14.965);
- HOLD.

