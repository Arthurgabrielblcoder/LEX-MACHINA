# C3B.2 — auditoria da rota da LC 63/1990

## `CF88:ART.158:PAR.1:INC.I`

- **Decisão editorial:** LEGACY_FULL_REVIEW RETARGET (`LEGACY:LEGACY_FULL_REVIEW:CORRELATA:REL_DF3F18219DDA1CD5@CF88:ART.158:PAR.1:INC.II`).
  - Rota: **route_fix {'mode': 'ABRIR_ARTIGO_INTERNO', 'articles': ['3']}**.
  - Fundamento: O inciso II do § 1º remete à lei estadual (até 35%, indicadores de educação); a LC 63 não disciplina essa parcela. O art. 3º, I, da LC 63 disciplina a parcela "na proporção do valor adicionado", que é o inciso I.
- **Registro jurídico:** `REL_21E430F499454751`, artigos ['3'], decisões ['C3A1:RELATION_TYPE:CF88:ART.158:PAR.1:INC.I', 'LEGACY:LEGACY_FULL_REVIEW:CORRELATA:REL_DF3F18219DDA1CD5@CF88:ART.158:PAR.1:INC.II'].
- **RUN4:** DEVICE_READY, DIRECT_ARTICLE_RESOLUTION; id de aparelho `REL_21E430F499454751`.
- **Aparelho (C3B.1):**
  - flags `-C----`; query keys ['CF88:ART.158:PAR.1:INC.I'];
  - REF_PAYLOAD ['CORRELATA:REL_21E430F499454751@CF88:ART.158:PAR.1:INC.I'];
  - resolução `CORRELATA:REL_21E430F499454751@CF88:ART.158:PAR.1:INC.I` → RELACOES `CF88|158|1|I||REL_21E430F499454751|…|ABRIR_ARTIGO_INTERNO|3` → offsets {'3': 1265};
  - cabeçalhos do texto {'3': [1265]}.

| Pergunta | Resposta |
|---|---|
| 1. Destino editorial pretendido | art. 3º da LC 63/1990 (critério e definição do valor adicionado) |
| 2. Tipo de vínculo | artigo específico (DESTINATION_SPECIFIC_ARTICLE) |
| 3. Por que abre no art. 3º | a linha RELACOES é `ABRIR_ARTIGO_INTERNO` com o art. 3, e o EXT_ARTIGOS aponta o cabeçalho do art. 3º |
| 4. Origem do art. 3º | da decisão jurídica (sem materialização implícita, ID compartilhado, normalização, fallback ou bug) |
| 5. Comportamento correto | art. 3º, conforme a decisão; a expectativa física "início da norma" diverge da decisão registrada |

## `CF88:ART.161:INC.I`

- **Decisão editorial:** C1A REPLACE (`LEGACY:C1A:CORRELATA:REL_B41DCE7A7582235E@CF88:ART.161:INC.I`).
  - Rota: **ABRIR_ARTIGO_INTERNO art. 3º (EXT_LC63_1990)**.
  - Fundamento: O inciso I manda a lei complementar definir valor adicionado para o art. 158, § 1º, I. A LC 62 se declara apoiada só nos incisos II e III. A definição de valor adicionado está no art. 3º, § 1º, da LC 63/1990. A LC 62 continua correta nos incisos II e III.
- **Registro jurídico:** `REL_39A8D87CD18EC477`, artigos ['3'], decisões ['LEGACY:C1A:CORRELATA:REL_B41DCE7A7582235E@CF88:ART.161:INC.I'].
- **RUN4:** DEVICE_READY, DIRECT_ARTICLE_RESOLUTION; id de aparelho `REL_39A8D87CD18EC477`.
- **Aparelho (C3B.1):**
  - flags `-C--R-`; query keys ['CF88:ART.161:INC.I'];
  - REF_PAYLOAD ['CORRELATA:REL_39A8D87CD18EC477@CF88:ART.161:INC.I'];
  - resolução `CORRELATA:REL_39A8D87CD18EC477@CF88:ART.161:INC.I` → RELACOES `CF88|161||I||REL_39A8D87CD18EC477|…|ABRIR_ARTIGO_INTERNO|3` → offsets {'3': 1265};
  - cabeçalhos do texto {'3': [1265]}.

| Pergunta | Resposta |
|---|---|
| 1. Destino editorial pretendido | art. 3º da LC 63/1990 (critério e definição do valor adicionado) |
| 2. Tipo de vínculo | artigo específico (DESTINATION_SPECIFIC_ARTICLE) |
| 3. Por que abre no art. 3º | a linha RELACOES é `ABRIR_ARTIGO_INTERNO` com o art. 3, e o EXT_ARTIGOS aponta o cabeçalho do art. 3º |
| 4. Origem do art. 3º | da decisão jurídica (sem materialização implícita, ID compartilhado, normalização, fallback ou bug) |
| 5. Comportamento correto | art. 3º, conforme a decisão; a expectativa física "início da norma" diverge da decisão registrada |

**Conclusão:** nenhuma correção de dados. Abrir a LC 63 no início exigiria uma nova decisão jurídica.

