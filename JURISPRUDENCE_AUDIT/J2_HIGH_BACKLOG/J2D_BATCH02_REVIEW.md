# JURISPRUDÊNCIA — CF: J2D, revisão externa do BATCH02 HIGH (10 candidatos)

```
MISSION = J2D (HOST-ONLY; web só para os 10 candidatos; decisões, sem materialização) · BRANCH = cf-jurisprudence-audit
DECISÕES = J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json (gerador build_j2d_batch02.py + j2d_batch02_review.py; 3/3 idêntico)
STATUS = AWAITING_USER_RATIFICATION
J2C_PHYSICAL_VALIDATION_RECORDED = PASS · BACKLOG_REBUILT_FROM_261 = PASS · RESOLVED_BATCH01_REENTERED = 0
BATCH02_SELECTED = 10/10 · BATCH02_SELECTION_REPRODUCIBLE = YES · OFFICIAL_SOURCE_REVIEW = 10/10
NAMESPACE_CHECK = 10/10 executado (9 PASS, 1 FAIL) · TEMPORAL_CHECK = 10/10 · DECISIONS_COMPLETE = 10/10
CURRENT_261_CHANGED = NO · FROZEN_LAYERS_MODIFIED = NO · MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO
```

## 0. Fechamento físico da J2C

Está registrado em `J2C_DEPLOY_REPORT.md`, seção "Resultado físico": `J2C_PHYSICAL_VALIDATION = 12/12 PASS`.

O baseline instalado tem 261 vínculos J em 160 targets e é o `REF_PAYLOAD` `62b06deb…` (pacote J2B.1). As decisões do Batch01 e a correção do Tema 558 não foram reabertas.

## A/B. Backlog reconstruído sobre a base de 261

**Método:**

- Mesma regra do J0 (categorias e prioridade): identificador nomeado, recorrência, artigo sem jurisprudência e referência descrita, com HIGH ≥ 3.
- Recalculada sobre a fila **atual**, isto é, sem os itens que o Batch01 resolveu.
- Comparada contra a base instalada.

| Contagem | J2A (base 256) | J2D (base 261) |
|---|---:|---:|
| Pendentes | 148 | **136** |
| Targets pendentes | 110 | **102** |
| HIGH | 42 | **31** |
| MEDIUM | 80 | **79** |
| LOW | 26 | **26** |

**Diferenças:**

- **−10:** as decisões do Batch01 (`J0-BL-069, 074, 080, 081, 082, 084, 135, 136, 137, 138`). Todos fora da fila: `RESOLVED_BATCH01_REENTERED = 0`.
- **−2 (MEDIUM):** notas `IDENTIFICACAO_PENDENTE` que só repetem pares já decididos no Batch01, saídas como `COVERED_BY_BATCH01`.
  - `J0-BL-083`: ADI 4425/7064 no art. 100, § 9º.
  - `J0-BL-085`: ADI 4425 no § 12.
- **HIGH −1 (`J0-BL-075`, ADI 4425 no art. 100):** caiu para MEDIUM. Antes ela era "recorrente" porque a ADI 4425 aparecia em outras recomendações (§ 9º e § 12), todas resolvidas agora. Nenhum item novo entrou em HIGH.
- **Os 4 targets que ganharam o primeiro J na J2C** (art. 100 § 12, art. 166 §§ 9º e 11, art. 166-A) não alteraram outras prioridades. As recomendações deles eram as próprias resolvidas, e os arts. 100 e 166 já contavam como artigos com jurisprudência.

**Nota de método:** para a prioridade usei a regex original do J0, que não reconhece "ADIN". A regex ampliada (com "ADIN") só entra nos critérios de seleção, como na J2A. Uma primeira versão do seletor usava a ampliada também na prioridade, o que promovia indevidamente 7 itens ao HIGH; foi corrigida antes de qualquer decisão.

## C. Seleção determinística (3/3 idêntica)

Critérios aplicados em ordem lexicográfica (`selection_rules`):

1. identificador explícito;
2. peso constitucional direto (efeito geral/vinculante);
3. target sem jurisprudência;
4. recorrência;
5. relevância prática (artigo sem jurisprudência);
6. menor ambiguidade;
7. ID estável.

Havia 31 HIGH; nenhum MEDIUM foi usado. **Restam 21 HIGH** depois do lote.

## D–K. Resultado da revisão

| # | Rec. | Target (backlog) | Precedente | Tipo | Status | Decisão | Razão |
|---|---|---|---|---|---|---|---|
| 1 | J0-BL-166 | ADCT art. 101 | ADI 7047 | ADI | mérito julgado | **REALLOCATE_RECOMMENDED** → ADCT art. 101, **§ 5º** | A decisão invalida só o § 5º (EC 113/21); usar o registro conjunto 7047/7064 |
| 2 | J0-BL-167 | ADCT art. 101 | ADI 7064 | ADI | mérito julgado | **REALLOCATE_RECOMMENDED** → ADCT art. 101, § 5º | Mesmo julgamento conjunto: um único vínculo cobre os itens 1 e 2 |
| 3 | J0-BL-169 | ADCT art. 107-A | ADI 7064 | ADI | mérito julgado | **PROMOTE** | Interpretação conforme do caput (só 2022), incisos II/III e §§ 3º, 5º, 6º invalidados; nível de artigo correto |
| 4 | J0-BL-039 | CF art. 23, II | Tema 793 (RE 855178) | RG | tese fixada; trânsito em 2020 | **PROMOTE** | A tese funda a solidariedade em saúde na "competência comum" (art. 23, II) |
| 5 | J0-BL-049 | CF art. 29-A, § 2º | SV 46 | SV | vigente | **REALLOCATE_RECOMMENDED** → CF art. 22, I (+ art. 85, par. único) | A referência legislativa oficial da SV é art. 22, I e art. 85, parágrafo único, não o art. 29-A |
| 6 | J0-BL-052 | CF art. 36, I | ADI 2167 | ADI | mérito julgado | **REJECT_FALSE_POSITIVE** | O objeto é a **Constituição de Roraima** (arguição prévia de nomeações); a ação não interpreta o art. 36, I |
| 7 | J0-BL-057 | CF art. 53, caput | Tema 950 (RE 632115) | RG | tese fixada; trânsito em 10/12/2025 | **PROMOTE** | A tese cita o "art. 53, caput": a imunidade material exclui a responsabilidade objetiva do Estado |
| 8 | J0-BL-076 | CF art. 100 | ADI 7047 | ADI | mérito julgado | **REALLOCATE_RECOMMENDED** → CF art. 100, **§ 11** | No art. 100 o julgado atinge o § 9º (já instalado) e dá interpretação conforme ao § 11 (EC 113/21) |
| 9 | J0-BL-077 | CF art. 100 | ADI 7064 | ADI | mérito julgado | **REALLOCATE_RECOMMENDED** → CF art. 100, § 11 | Mesmo julgamento conjunto: um único vínculo cobre os itens 8 e 9 |
| 10 | J0-BL-058 | CF art. 53, § 1º | HC 232627 | **HC** | mérito do Pleno (2025); ED integrativos (2026) | **PROMOTE** (tipo novo) | A tese do Plenário cita o "art. 53, § 1º": o foro para crimes funcionais subsiste após o mandato. `NEW_JURIS_TYPE_REQUIRES_DESIGN = YES` |

```
BATCH02_SIZE = 10 · PROMOTE = 4 · PROMOTE_PROVISIONAL = 0 · REJECT_FALSE_POSITIVE = 1 · REJECT_TEMPORAL_MISMATCH = 0
REJECT_NOT_MATERIAL = 0 · ALREADY_COVERED = 0 · DUPLICATE = 0 · REALLOCATE_RECOMMENDED = 5 · UNRESOLVED_EXTERNAL = 0
```

### Explicações (promoções e realocações)

- **ADI 7047/7064 → ADCT art. 101, § 5º (itens 1 e 2).** O dispositivo declara inconstitucional "o art. 101, § 5º, do ADCT, com redação estabelecida pelo art. 1º da EC 113/21". O texto é o vigente no compilado, então a versão é CURRENT. O vínculo vai no § 5º, não no artigo inteiro, e usa o registro conjunto já instalado. A ratificação de duas decisões gera um só vínculo, como no Batch01.
- **ADI 7064 → ADCT art. 107-A (item 3).** Só a ADI 7064 julgou o art. 107-A (EC 114/2021). A decisão limitou o teto de precatórios ao exercício de 2022, invalidou os incisos II e III e, por arrastamento, os §§ 3º, 5º e 6º. **A decidir na ratificação:** usar o registro conjunto, cuja ficha já tem a seção "SOMENTE NA ADI 7064", ou criar um registro próprio da ADI 7064.
- **Tema 793 → CF art. 23, II (item 4).** A tese diz que os entes são solidariamente responsáveis "em decorrência da competência comum", e a competência comum em saúde é a do art. 23, II. O tema não está na base nem no índice legado: precisa de registro RG e ficha nova, no formato RG já validado.
- **SV 46 → CF art. 22, I e art. 85, parágrafo único (item 5).** A página oficial da súmula traz "Referência Legislativa: … art. 22, I; e art. 85, parágrafo único". O § 2º do art. 29-A só lista crimes do Prefeito; a SV não o interpreta. O art. 22, I já tem o Tema 1246; o art. 85, parágrafo único não tem jurisprudência.
- **Tema 950 → CF art. 53, caput (item 7).** Tese de 2025, com trânsito em julgado: a imunidade material do art. 53, caput exclui a responsabilidade civil objetiva do Estado, e o excesso é responsabilidade pessoal do parlamentar.
- **ADI 7047/7064 → CF art. 100, § 11 (itens 8 e 9).** Interpretação conforme ao § 11 (EC 113/2021) para excluir "com auto aplicabilidade para a União". O § 9º já está instalado; o vínculo novo vai no § 11, com o registro conjunto.
- **HC 232627 → CF art. 53, § 1º (item 10).** Tese do Plenário (DJe 16/07/2025), com os dispositivos relevantes limitados ao art. 53, § 1º. Os ED de 2026 complementam o mesmo registro; eles são a recomendação `J0-BL-060`, fora do lote. **HC é um tipo novo:** o firmware atual exibiria "OUTRO 232627". Não materializar sem antes desenhar o tipo.

### Rejeição

- **ADI 2167 → CF art. 36, I (item 6).** É falso positivo de namespace, a mesma lição da J1:
  - **Objeto:** os arts. 33, XVIII; 46, § 3º; 62, parágrafo único, e 103 da **Constituição do Estado de Roraima**, que tratavam de arguição e aprovação prévias de nomeações pela Assembleia.
  - **Uso da CF:** só aparece o procedimento do art. 36, **§ 1º**, citado na MC.
  - **Recomendação original:** atribuía à ação a tese de "intervenção vinculada ou discricionária", que ela não contém.

### Controles

- **Namespace:**
  - 9 PASS: 6 na CF e 3 no ADCT, com target no mesmo namespace.
  - 1 FAIL: Constituição estadual.
- **Versão temporal:**
  - 9 CURRENT.
  - 1 NOT_APPLICABLE: o dispositivo apontado não foi objeto da ação.
  - Nenhum HISTORICAL.
- **Provisórios:** nenhum.
- **Julgamentos conjuntos:** os itens 1/2 e 8/9 usam o registro `STF:ADI:7047-7064` já validado, sem entradas duplicadas.

## L–N. Nada materializado

- **Dados publicados:** RUN9, `REF_PAYLOAD`, `REF_LOOKUP`, `CF88_TARGETS`, índices legados, fichas, SD e firmware estão intactos. O teste confere o hash instalado, o `SHA256SUMS` do RUN9, o pacote J2B.1 e o `apply_j2b_adi_overlay --check`.
- **Camadas congeladas:** Correlatas 1, Referências nº 4 e ENTENDA não foram tocadas.

**Pontos para a futura materialização** (registrados, sem ação agora):

1. **HC:** tipo novo, que precisa de desenho.
2. **Temas 793 e 950 e SV 46:** precisam de registro e ficha nova no índice legado, nos tipos RG/SV já validados.
3. **ADCT:** o índice legado codifica chaves de ADCT com o prefixo `CF88` (ex.: `STF:RG:231:CF88:78:4:-:-` para o ADCT, art. 78, § 4º). A J2B.x deve fixar a convenção antes de criar chaves `…:101:5:…` e `…:107-A:…`.

## O. Fontes (todas TIER A)

| Id | Órgão | Página | Captura |
|---|---|---|---|
| P1 | Planalto | CF compilada (reuso J2A, 2026-10-16) | bytes `51ac764a…` |
| S4 | STF | Acórdão ADI 7064 (reuso J2A) | texto renderizado `4d1e398d…` |
| S5 | STF | ADI 7047, aba Decisões (reuso J2A) | texto renderizado `d63a0050…` |
| S6 | STF | ADI 7064, aba Decisões (reuso J2A) | texto renderizado `b71b5b66…` |
| T1 | STF | Tema 793, página do tema | texto renderizado `e9c3a924…` |
| T2 | STF | RE 855178 ED (tese do Tema 793) | texto renderizado `c286582b…` |
| T3 | STF | Súmula Vinculante 46 (página oficial) | texto renderizado `18f8caf4…` |
| T4 | STF | ADI 2167 (mérito e MC) | texto renderizado `e340485a…` |
| T5 | STF | Tema 950, página do tema | texto renderizado `61f651fa…` |
| T6 | STF | RE 632115 (tese do Tema 950) | texto renderizado `06e36da8…` |
| T7 | STF | HC 232627 e ED | texto renderizado `310ca610…` |

**Como as fontes foram obtidas:**

- **Data de consulta:** 2026-10-17, para T1–T7.
- **Captura:** o `portal.stf.jus.br` responde 403 a clientes automáticos, então as páginas foram lidas no navegador embutido (sha256 do texto renderizado), como na J1.3 e na J2A.
- **Proveniência:** URLs completas, provas e campos (tribunal, classe, número, processo, tema/súmula, relator, julgamento, publicação, situação, target, versão temporal) estão no JSON.
- **Sem fontes secundárias:** não foram usados blogs, Jusbrasil, cursinhos ou snippets.

## Q. Testes

`JURISPRUDENCE_AUDIT/tests/test_j2d.py`, 6 testes:

- gerador atualizado;
- seleção 3/3;
- backlog 136/31/79/26 sem reentrada do Batch01;
- 10 únicos e HIGH;
- decisões completas, com namespace, temporal, fontes Tier A com hash e tipo novo sinalizado;
- base de 261 e entradas inalteradas.

| Suíte | Resultado |
|---|---|
| `JURISPRUDENCE_AUDIT/tests` (J1.1, J1.3, J1.4, J2A, J2B, J2B.1, J2D) | **52/52 OK** |
| `LEGAL_TARGET_ID/tests` | 90/90 OK |
| `REFERENCE_COVERAGE_AUDIT/tests` | 15/15 OK |

O seletor J2D restaura o hook da J2A depois de usá-lo; sem isso, o teste da J2A rodaria sobre a base errada quando os dois correm no mesmo processo.

```
NEXT_RECOMMENDED_MISSION = RATIFICAÇÃO DO BATCH02
```
