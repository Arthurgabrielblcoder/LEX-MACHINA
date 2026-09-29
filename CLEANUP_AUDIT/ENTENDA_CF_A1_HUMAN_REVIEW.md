# ENTENDA-CF-A1: revisão humana aplicada

Data: 2026-09-28. Decisão: **APROVADO COM AJUSTES**. A arquitetura editorial também foi aprovada.

O diff completo, com `before`/`after`/`reason` e `human_review=true`, está em `ENTENDA_ENGINE/derived/CF88_PILOT_HUMAN_REVIEW_DIFF.json`. O rascunho original (`editorial/CF88_PILOT_DRAFTS.json`) foi preservado. A versão revisada está em `editorial/CF88_PILOT_T1_REVIEWED.json`.

## Ajustes

| Target | Versão | Ajuste | Tipo |
|---|---|---|---|
| `CF88:ART.5` | 1→2 | O § 1º passa a dizer que as normas definidoras de direitos e garantias fundamentais "devem produzir efeitos desde logo; ainda assim, determinados direitos podem depender de regulamentação para definir aspectos do seu exercício". | pedido humano |
| `CF88:ART.37:PAR.6` | 1→2 | Na relação vítima × pessoa jurídica, a explicação passa a exigir expressamente **dano + nexo causal + atuação do agente nessa qualidade**, sem prova de dolo ou culpa. O regresso continua dependendo de dolo ou culpa. | pedido humano |
| `CF88:ART.37:PAR.6` | (2) | O exemplo passa a mencionar a demonstração do dano e do nexo, e foi incluído o termo "Nexo causal". | coerência mínima |
| `CF88:ART.60:PAR.4:INC.IV` | 1→2 | A fronteira entre texto e interpretação ficou explícita: "não restringe expressamente essa proteção ao art. 5º… é questão de interpretação constitucional". | pedido humano |
| `CF88:ART.225` | 1→2 | "Bem de uso comum do povo" passou a ser definido como "bem destinado à fruição e à proteção de todos, cuja preservação interessa à coletividade". | pedido humano |
| `ADCT:ART.10:INC.II` | 1→2 | O exemplo passou a ser "Uma empregada já estava grávida quando foi dispensada sem justa causa" e não depende mais da comunicação da gravidez. | pedido humano |
| `ADCT:ART.10:INC.II` | (2) | A vigência passou a registrar `external_verification` (ver abaixo). | pedido humano |

Preservadas sem alteração de conteúdo (versão 1): `CF88:ART.1`, `CF88:ART.37`, `CF88:ART.37:PAR.10`, `CF88:ART.60`, `CF88:ART.60:PAR.4` e `CF88:ART.150`.

## Vigência do ADCT

O índice classifica o `ADCT:ART.10:INC.II` como `UNKNOWN_VALIDITY`, porque o texto operacional do produto ainda não contém o ADCT. A revisão humana verificou a vigência em material oficial externo, e a explicação agora registra essa verificação:

| Campo | Valor |
|---|---|
| `status` | `CURRENT_OFFICIAL_EXTERNAL_VERIFICATION` |
| `current_in_operational_source` | `false` |
| `current_official_external` | `true` |
| `verified_on` | `2026-09-28` |
| `content_hash_stored` | `false` (nenhum hash de conteúdo web foi inventado) |

Evidência textual registrada:

- **Câmara dos Deputados:** o material oficial traz o ADCT atualizado até a EC 139/2026, com o art. 10, II, "a" e "b" reproduzido.
- **Dispositivos sujeitos a regulamentação:** a página oficial continua listando o art. 10 do ADCT.
- **CLT:** o art. 391-A remete à estabilidade do art. 10, II, "b", do ADCT.

No SD, a vigência aparece como `CURRENT_OFFICIAL_EXTERNAL`. O SD operacional não foi alterado.

## Corpus e build

**Corpus:**

- 16 registros: 11 ACTIVE (`HUMAN_APPROVED_T1`) e 5 RETIRED (`CHANGES_REQUESTED`, com `superseded_by`).
- Os hashes de fonte não mudaram, porque o texto oficial é o mesmo.

**Build `ENTENDA_ENGINE/derived/pilot_t1`**, repetido duas vezes, BYTE_IDENTICAL:

| Arquivo | SHA-256 | Bytes |
|---|---|---|
| `ENTENDA_LOOKUP.IDX` | `690fb1d17a5e59cb66723428a91fa6fb48dbd13cd4efdae7ed08770d155679ca` | 1.158 |
| `ENTENDA_PAYLOAD.DAT` | `f757d27e051686505b371f85ecc1c3116699c11a3915664fad83b0fab0b269d1` | 27.713 |

**Testes:** ENTENDA 19/19 e LEGAL_TARGET_ID 47/47.

**Lint do piloto aprovado:** 14 avisos, apenas informativos. O conteúdo aprovado não foi reescrito por causa deles.
