# JURISPRUDÊNCIA — CF: J2B, modelo de registro de ADI + candidato HOST-ONLY do BATCH01

> **Atualização (J2B.1, 2026-10-16).** O pacote desta J2B ficou `SUPERSEDED_BEFORE_PHYSICAL_DEPLOY`: a correção temporal do Tema 558 (art. 100, § 9º → art. 100) gerou o pacote `J2B_1_CANDIDATE_HOST_ONLY`, que é o que vale para a J2C. Ver `J2B_1_TEMA558_TEMPORAL_FIX.md`. A observação da seção 9 foi resolvida assim.

```
MISSION = J2B (HOST-ONLY: modelar, materializar em candidato, auditar, testar; SEM deploy)
BRANCH = cf-jurisprudence-audit · DADOS = 1907ba0 · PACOTE = este commit
RATIFICAÇÃO = Arthur, 2026-10-16: J2A_BATCH01_USER_RATIFIED = YES (6 promoções, 4 rejeições ou duplicatas)
JURIS: 256 → 261 vínculos · 156 → 160 targets · CURRENT_256_BYTE_IDENTICAL = YES · removidos 0
FIRMWARE_CHANGE = NONE · FLASH = NO · MICROSD_TOUCHED = NO · DEPLOY = NO · BATCH02 = não iniciado
CORRELATAS_1_CF / REFERENCES_4_CF / ENTENDA_CF_ADCT = congeladas e intactas · HIGH = 42 (estado correto)
STATUS = CANDIDATO HOST-ONLY PRONTO · JURISPRUDENCE_FROZEN = NO
```

## 1. Ratificação registrada

| Rec. | Vínculo | Decisão ratificada |
|---|---|---|
| J0-BL-136 | CF art. 166, § 9º ← ADI 7697 | `PROMOTE_PROVISIONAL` |
| J0-BL-137 | CF art. 166, § 11 ← ADI 7697 | `PROMOTE_PROVISIONAL` |
| J0-BL-138 | CF art. 166-A ← ADI 7697 | `PROMOTE_PROVISIONAL` |
| J0-BL-081 | CF art. 100, § 9º ← ADI 7047 | `PROMOTE` |
| J0-BL-082 | CF art. 100, § 9º ← ADI 7064 | `PROMOTE` |
| J0-BL-084 | CF art. 100, § 12 ← ADI 4425 | `PROMOTE` |
| J0-BL-080 | CF art. 100, § 9º ← ADI 4425 | `REJECT_TEMPORAL_MISMATCH` |
| J0-BL-069 / 074 | CF arts. 92 / 98 ← ADI 3392 | `REJECT_FALSE_POSITIVE` |
| J0-BL-135 | CF art. 166 (caput) ← ADI 7697 | `DUPLICATE / DO_NOT_PROMOTE` |

O registro fica em `LEGAL_TARGET_ID/derived/CF88_JURIS_ADI_ADDITIONS_J2B.json` → `ratification`, gerado por `JURISPRUDENCE_AUDIT/apply_j2b_adi_overlay.py`.

## 2. Modelo de registro de ADI (sem mudar o firmware)

**O que o firmware atual já faz.** O firmware em uso (app `6e329c91…`) já classifica o TIPO `adi`:

- **Lista:** mostra `"ADI " + NUMERO` (`rotuloTipoJurisprudencia`).
- **Ficha:** abre `03_CONTEUDO/<IDENTIFICADOR com ":" → "_">.TXT` (`arquivoDetalheJurisCF`).
- **Título da ficha:** `"STF ADI " + NUMERO`.
- **Resolução:** o vínculo é resolvido pela chave no `JURISPRUDENCIA.IDX`. A busca é linear, procura a chave no início da linha, e a ordem das linhas não importa.

Por isso a ADI usa o **mesmo esquema de 8 colunas** do índice legado e **não precisa de firmware novo**.

```
ID|TIPO|TRIBUNAL|NUMERO|STATUS|TITULO_CURTO|IDENTIFICADOR|FONTE
STF:ADI:4425:CF88:100:12:-:-|adi|STF|4425|merito_julgado|ADI 4425|STF:ADI:4425|<url oficial>
```

| Campo | Regra |
|---|---|
| `ID` | Mesma convenção `STF:<TIPO>:<n>:CF88:<art>:<par>:<inc>:<al>` dos Temas (`STF:RG:349:CF88:1:1:-:-`) |
| `NUMERO` | Vai para a lista. Ex.: `4425`; `7047/7064` (julgamento conjunto); `7697 (CAUTELAR)` (marcador provisório **já na lista**) |
| `STATUS` | Status do processo, combinação de `cautelar`, `cautelar_referendada`, `merito_julgado` e `merito_pendente` (ex.: `cautelar_referendada_merito_pendente`) |
| `IDENTIFICADOR` | Define o arquivo da ficha. Vários dispositivos com a mesma ADI **compartilham uma ficha** (`STF_ADI_7697.TXT` serve aos §§ 9º, 11 e ao art. 166-A) |

**Ficha** (UTF-8, LF, mesmo layout das fichas atuais):

- cabeçalho `TRIBUNAL / STATUS / PROCESSO`;
- para decisão provisória, o bloco **DECISÃO PROVISÓRIA** logo no início;
- dispositivos alcançados;
- decisão em resumo (paráfrase, sem reproduzir o acórdão);
- modulação ou nota temporal;
- data de verificação;
- fonte oficial.

**Compatibilidade com o índice atual:**

- As 5 linhas novas entram **no fim** do `JURISPRUDENCIA.IDX`, e as 5 entradas novas **no fim** do `JUR_LOOKUP.IDX`. Os bytes atuais são prefixo exato, então nenhum offset muda.
- O cache de boot em PSRAM continua válido: todo offset começa uma linha, e a soma das quantidades bate com o número de registros (301 = 301).
- O `MANIFESTO.json` do pacote legado J4.6 não é lido pelo firmware e ficou intocado.

## 3. Julgamento conjunto: ADIs 7047 e 7064

A sua ratificação mantém **as duas ações**. A representação no aparelho foi comparada critério a critério:

| Critério | A. Duas entradas | **B. Um registro conjunto com aliases (adotado)** | C. Duas entradas, ficha compartilhada |
|---|---|---|---|
| Busca | os dois números visíveis | **os dois números no rótulo `ADI 7047/7064`**; `aliases` no export | os dois números visíveis |
| Clareza | duas linhas e duas fichas iguais | **uma linha; a ficha diz "julgamento conjunto"** e separa o que vale só para a 7064 | duas linhas que abrem a mesma ficha |
| Rastreabilidade | 2 decisões, 2 vínculos | **2 decisões ratificadas → 1 vínculo** com `aliases`, `joint_judgment`, as duas fontes e as duas decisões na provenance | 2 vínculos |
| Abertura da ficha | duas aberturas iguais | **uma** | duas aberturas iguais |
| Firmware | nada muda | **nada muda** | nada muda |
| Futuro (ex.: ADI 4357 + 4425, julgadas juntas) | multiplica duplicatas | **basta acrescentar um alias**, depois de revisão própria | multiplica linhas |

O modelo B é o adotado: chave `STF:ADI:7047-7064:CF88:100:9:-:-`, ficha `STF_ADI_7047-7064.TXT`.

A ADI 4425 continua com um registro só seu. A ADI 4357 **não** foi revisada nesta rodada; incluí-la como alias exigiria uma decisão própria.

## 4. Provisórios e gatilho de revalidação

**ADI 7697** (§§ 9º e 11 do art. 166 e art. 166-A):

- `status_processual = [cautelar_referendada, merito_pendente]` e `provisional = true` no export;
- `(CAUTELAR)` aparece na lista;
- **DECISÃO PROVISÓRIA** aparece no início da ficha.

**Registro de revalidação:** `J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json` traz:

- o gatilho `JULGAMENTO_DE_MERITO`;
- `last_verified_on 2026-10-16`;
- `max_age_days 90`;
- onde verificar;
- o que fazer quando o gatilho disparar.

**Gate:** `JURISPRUDENCE_AUDIT/check_j2b_provisional.py --as-of <data>`. Ele falha (exit 2) se a última verificação tiver mais de 90 dias ou se `merit_judged = true` estiver registrado sem nova revisão. Usa data explícita, então o resultado é reproduzível. **É obrigatório antes de qualquer deploy desses vínculos.** Hoje (2026-10-16) dá PASS.

## 5. RUN8 (motor de referências)

- **Builder:** `LEGAL_TARGET_ID/build_export_run8_juris_j2b.py`.
- **Saída:** `LEGAL_TARGET_ID/derived/export_test/run8_juris_j2b_candidate/` (3/3 idêntico).
- **Base:** o RUN7 é conferido contra `SHA256SUMS` e contra os bytes **instalados** (pacote J1.4) e reexportado byte-idêntico antes de qualquer mudança.
- **Mudança:** RUN8 = RUN7 + 5 vínculos `JURISPRUDENCE`; nada removido. Cada vínculo passa por `reference_engine.validate_link` e sai como `CURRENT_VISIBLE`.
- **Flags:** só a J muda, em 4 targets que ganham o primeiro vínculo: art. 100 § 12, art. 166 §§ 9º e 11, e art. 166-A. O § 9º do art. 100 já tinha J (Tema 558).

## 6. Pacote SD HOST-ONLY

**Ferramenta:** `JURISPRUDENCE_AUDIT/build_j2b_candidate.py --commit 1907ba0`.

**Gates:**

- **Cartão reproduzido primeiro:** o builder J1.4 (fixado em `7786bbc`) reproduz o manifesto físico pós-J1.5.
- **Legado:** os bytes vêm do arquivo J4.6, conferidos contra o manifesto do cartão.
- **`/99_LEX_V1`:** gerado pelo gerador oficial (`FULL_CF_ENTENDA_810`, `require_committed_refs`).
- **Reconstrução:** idêntica.
- **Manifesto do aparelho × pacote:** PASS.
- **`CF88_TARGETS`:** só difere do gerado na posição R (42 linhas).

**Pacote:** `J2B_CANDIDATE_HOST_ONLY/`, com `candidate/`, `rollback/` (bytes do cartão hoje) e `J2B_PACKAGE_MANIFEST.json`.

- `BUILD_ID 4802b4a304f3a784`;
- `REFERENCE_ENGINE cf-reference-engine-run8-juris-j2b`.

| Arquivo | Mudança | Bytes | SHA-256 do candidato |
|---|---|---:|---|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | alterado | 62.364 → 63.104 | `77e2ca6c3bab8a2dc0834bd6972fd9e1487680bdeba4c210edee829b382ccc37` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | alterado | 6.450 → 6.556 | `588f85f74a30dc6042bdaea3e05c5aa71ddcc2cfbcd0bd952d11b7d231318be8` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | alterado | 165.466 | `103abadec9c4af3c131de744d49efd1f11c291b16f39f676bdca8b204056d570` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | alterado | 7.641 → 7.626 | `4fb0bf018e9b3bd8aa362e4478eb2dc4cb5b6783dceca5a8edc85e2c358b91d2` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | alterado | 596 → 595 | `cb1438cfa4a2c1925e9974c7a5784c7dae3072acdaf768a7d50e6ad4d4aa8f79` |
| `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX` | **acréscimo no fim** | 54.207 → 55.106 | `05e9c2afec5991d25a84ccc99ba4077b4a9730e9009a70983b00dd304d1bc09d` |
| `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` | **acréscimo no fim** | 3.755 → 3.863 | `603d9963181727d22aa8a99af50f197cfc71702e136309ace536979bc936c1f3` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_4425.TXT` | **novo** (rollback = apagar) | 1.441 | `be757508b3472dc4a25fa538a3f7915f290f10c7be5c7e5850982c3b5aa1a3eb` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7047-7064.TXT` | **novo** (rollback = apagar) | 1.338 | `1a4ca8c76dc0588ca1b6fbc9063c0d4cbc4746d9777d4c52b771bd6b784a283b` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7697.TXT` | **novo** (rollback = apagar) | 1.206 | `0b62db3e0d5b3f9032f4cbf1733afe5b385fd569737d0ea902b957d5e6e68527` |

**Deploy futuro:** diferente das J1.2 e J1.5, este pacote **adiciona** arquivos e toca `/99_JURISPRUDENCIA_V2`. A ferramenta da missão de deploy precisa tratar arquivos novos (rollback por remoção) e rodar antes o gate de revalidação.

## 7. Auditoria de isolamento

- **Arquivo:** `J2B_ISOLATION_AUDIT.json`.
- **Gerador:** `build_j2b_isolation_audit.py` (`--check` dá `UP_TO_DATE` 3/3).

| Verificação | Resultado |
|---|---|
| `CURRENT_256_BYTE_IDENTICAL` | **YES**: as 256 linhas de jurisprudência instaladas estão no candidato sem nenhuma alteração |
| Linhas removidas / adicionadas | 0 / **5** (exatamente os 5 ratificados) |
| Correlatas / obras (Referências nº 4) | 0 / 0; arquivos Correlatas e ENTENDA byte-idênticos |
| Flags | J **4** · E 0 · C 0 · W 0 · R 0 · X 0; J = jurisprudência visível |
| `R_FLAG_KNOWN_DIVERGENCE` | 37 → 38 (J1.4) → **42**: 4 targets novos no `REF_LOOKUP` sem R; o firmware não lê R |
| Índices legados | só acréscimo; regras do cache de boot válidas (301 registros = 301) |
| Espelho do firmware (REF_LOOKUP → REF_PAYLOAD → chave no IDX → rótulo → ficha) | as 5 ADIs resolvem, com ficha presente |
| Regressão (art. 100 § 5º, art. 40, art. 16, art. 37 XI) | idêntica à base |

**Como cada dispositivo aparece no aparelho (simulação):**

| Dispositivo | Lista `2 JURIS.` |
|---|---|
| CF art. 100, § 9º | `ADI 7047/7064` · `RG TEMA 558` |
| CF art. 100, § 12 | `ADI 4425` |
| CF art. 166, § 9º | `ADI 7697 (CAUTELAR)` |
| CF art. 166, § 11 | `ADI 7697 (CAUTELAR)` |
| CF art. 166-A | `ADI 7697 (CAUTELAR)` |

## 8. Testes

`JURISPRUDENCE_AUDIT/tests/test_j2b.py`, 8 testes:

- geradores atualizados;
- RUN8 reproduzível;
- modelo ratificado (6 → 5, registro conjunto, provisórios, schema de 8 colunas);
- fichas (nomes, aviso provisório, julgamento conjunto, UTF-8 sem BOM e LF);
- pacote e rollback;
- isolamento;
- gate de revalidação (PASS hoje; falha após 90 dias ou com mérito julgado);
- firmware intocado.

| Suíte | Resultado |
|---|---|
| `JURISPRUDENCE_AUDIT/tests` (J1.1, J1.3, J1.4, J2A, J2B) | **38/38 OK** |
| `LEGAL_TARGET_ID/tests` | 90/90 OK |
| `REFERENCE_COVERAGE_AUDIT/tests` | 15/15 OK |
| `CORRELATA_COVERAGE_AUDIT/tests` (módulo a módulo) | Só as falhas já conhecidas: as 4 de `PREEXISTING_CORRELATA_TEST_DEBT` e o `test_16`, que acusa os `DEVICE_INTEGRATION/_tmp_det_*.log` não versionados |

## 9. Observação para decisão (nada foi alterado)

O **Tema 558**, que faz parte dos 256, está no art. 100, § 9º. Pela ficha, a tese trata da compensação dos §§ 9º e 10 **incluídos pela EC 62/2009**. É o mesmo descompasso temporal que levou à rejeição da ADI 4425 nesse parágrafo (J2A). Como a J1 está fechada e os 256 são imutáveis nesta rodada, o tema **não foi tocado**. Ele fica sinalizado para uma decisão sua, que pode ser mantê-lo ou tratá-lo como a SV 17 e o Tema 594.

## 10. Plano do teste físico (para uma futura missão de deploy; NÃO executado)

**Pré-requisito:** `check_j2b_provisional.py --as-of <data do deploy>` precisa dar PASS.

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal; o cache de jurisprudência carrega (log `JUR CACHE … fonte=CACHE`, se houver serial) |
| 2 | CF art. 100, § 9º → `2 JURIS.` | `ADI 7047/7064` **uma vez** e `RG TEMA 558`; abrir a ADI: ficha "julgamento conjunto"; BACK funciona |
| 3 | CF art. 100, § 12 → `2 JURIS.` | `ADI 4425`; a ficha mostra a modulação e a nota sobre a SELIC |
| 4 | CF art. 166, § 9º → `2 JURIS.` | `ADI 7697 (CAUTELAR)`; a ficha começa com **DECISÃO PROVISÓRIA** |
| 5 | CF art. 166, § 11 e art. 166-A | `ADI 7697 (CAUTELAR)`, a mesma ficha |
| 6 | CF art. 166, caput | **Sem** `2 JURIS.` (`DUPLICATE / DO_NOT_PROMOTE`) |
| 7 | CF arts. 92 e 98 | **Sem** ADI 3392 |
| 8 | CF art. 100, § 5º; art. 40; art. 16 | Como na J1.5 (SV 17/Temas 147/1037/1335; Tema 594; Temas 367/387) |
| 9 | Regressão de camadas | Correlata art. 202 § 5º; Sicko no art. 196; ENTENDA no art. 127 |

```
NEXT_RECOMMENDED_MISSION = J2C — DEPLOY CONTROLADO DO SD (candidato J2B, com arquivos novos) + TESTE FÍSICO
                           (ou J2A_BATCH02, sem deploy; restam 32 HIGH)
```
