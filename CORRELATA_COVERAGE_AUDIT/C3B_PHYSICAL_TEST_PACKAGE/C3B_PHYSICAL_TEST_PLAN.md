# C3B — plano de teste físico (preparado, NÃO executado)

**Candidato `RUN4_CANDIDATE_HOST_ONLY`.** Não é baseline nem aprovado. Nada foi copiado para nenhum cartão. Arthur executa; o Claude não toca no cartão.

## Arquivos do pacote (somente os que mudam)

| Caminho no cartão | SHA256 baseline | SHA256 candidato | Bytes (baseline → candidato) |
|---|---|---|---|
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` | `27c67eea6a38e3cba012d4a3d02c3856d37fd4cd1bae15473854fab0edea5430` | 6955 → 6702 |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` | `235b8db6c8d1c6b608853ec2a659b7b911d1d77d61983947555b151cc913013b` | 68075 → 65248 |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` | `a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad` | `5c54face7ea7eff62dbbb0a4193b5e2452e7fb03d82012d09919e74d234b3e5e` | 15904 → 15960 |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` | `bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d` | `a1d467beff5127ba72af042713aac7af4ee27a048d7d25c4211ec8b79b6582a8` | 8101 → 4650 |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` | `863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e` | `efac06cee0a1d8f0676564ba128d0ab8f474b89399f40de6422cc6fded37ef2c` | 934 → 626 |

- **Cache do firmware:** REL_LOOKUP 26/64 linhas; 15/32 normas.
- **Não mudam:** Lei Seca (05_TEXT), TARGETS, ENTENDA, 00_SYS, textos das normas externas, EXT_NORMAS.IDX e firmware.
- **Aviso:** o `00_SYS/LEX_DEVICE_MANIFEST.json` do cartão registra o SHA dos REF_* e ficará desatualizado durante o teste.
  - O firmware não lê esse arquivo (verificado no código-fonte); o rollback restaura a coerência.

## Procedimento

1. **Backup.** Com o aparelho desligado, retire o microSD e copie o cartão inteiro para uma pasta nova no PC (ex.: `D:\BACKUP_C3B_<data>`). Confira que a cópia tem o mesmo número de arquivos.
2. **Identificar o cartão.** Confirme que `99_LEX_V1/00_SYS/LEXV1.VER` contém:
   - `BUILD_ID|de963699728cb66e`;
   - `GIT_COMMIT|fa9719a6bd335275252473a5f154e4e11f5532f4`;
   - `REFERENCE_ENGINE|cf-reference-engine-run3`.
   - Confira também que o SHA256 de cada arquivo da tabela acima no cartão é igual ao **baseline**.
   - Se qualquer um divergir, PARE: não é o cartão esperado.
3. **Copiar, nesta ordem**, de `candidate/SD/` para a raiz do cartão, substituindo:
   1. `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX`
   2. `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX`
   3. `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX`
   4. `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX`
   5. `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX`
   - Os índices de relação vêm antes dos REF_*: se a cópia for interrompida, os REF_* antigos continuam coerentes com os vínculos antigos.
4. **Conferir** o SHA256 de cada arquivo copiado contra a coluna **candidato**. Se divergir, refaça a cópia ou faça o rollback.
5. **Ejetar** o cartão com segurança e reinseri-lo no aparelho desligado.
6. **Ligar** o aparelho. Esperado: boot normal, sem erro de diagnóstico.
7. **Executar os testes abaixo** e anotar OK/FALHA em cada um.
8. **Rollback (se qualquer teste falhar ou houver dúvida).**
   - Desligue o aparelho, retire o cartão e copie de `rollback/SD/` os mesmos arquivos.
   - Confira cada SHA256 contra a coluna **baseline** (`C3B_ROLLBACK_MANIFEST.json`) e repita os testes 10 e 11 no estado antigo.
   - O backup completo do passo 1 é a última garantia.

## Testes manuais (11)

| # | Cobre | Onde | Esperado |
|---|---|---|---|
| 1 | KEEP legado | CF art. 5º, XLIII → botão 1 (correlatas) | EXT_LEI13260_2016 aparece e abre o art. 1º |
| 2 | ROUTE_FIX | CF art. 202, § 5º → correlata LC 108/2001 | abre direto o art. 26 (antes abria o art. 1º) |
| 3 | RETARGET | CF art. 158, § 1º, I e depois § 1º, II | LC 63/1990 aparece no inciso I (abre o art. 3º) e NÃO aparece mais no inciso II |
| 4 | REPLACE resolvível | CF art. 161, I | aparece a LC 63/1990 (abre o art. 3º); a LC 62/1989 não aparece mais no inciso I (continua nos incisos II e III) |
| 5 | Novo HIGH | CF art. 202, § 1º | aparece a LC 109/2001 e abre o art. 3º |
| 6 | PNE no caput | CF art. 214 (caput) e incisos I a VI | Lei 15.388/2026 aparece uma única vez, no artigo/caput; nenhum inciso a mostra |
| 7 | Salto LC 87 art. 10 | CF art. 150, § 7º → LC 87/1996 | abre exatamente no "Art. 10. É assegurado ao contribuinte substituído..." |
| 8 | Salto Lei 7.998 art. 9º | CF art. 239, § 3º → Lei 7.998/1990 | abre exatamente no "Art. 9º É assegurado o recebimento de abono salarial..." |
| 9 | HOLD suprimido | CF art. 37, § 3º, III | nenhuma correlata (a Lei 13.460/2017 não aparece); no § 3º, I ela continua |
| 10 | Vacatio suprimida | CF art. 37, II; art. 131, § 2º; art. 132 | a Lei 14.965/2024 não aparece em nenhum dos três |
| 11 | Outras camadas | CF art. 5º (caput) e um dispositivo com ENTENDA; abrir Lei Seca de qualquer norma | jurisprudência, obras, ENTENDA e texto iguais ao estado anterior; nenhuma tela nova de erro |

Visíveis DEVICE_READY no candidato: 24 vínculos CORRELATA. Fora do pacote:
- 21 MAIN_CORPUS;
- 55 que dependem de ingestão;
- 2 ADCT (bloqueados por ingestão);
- 3 supressões temporais (Lei 14.965);
- 1 HOLD.

