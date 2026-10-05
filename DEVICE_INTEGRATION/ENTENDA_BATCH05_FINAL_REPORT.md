# ENTENDA BATCH05 — RELATÓRIO FINAL (CF88, arts. 37–41)

**`BATCH05_ENTENDA_HUMAN_REVIEW_COMPLETE` — 69 de 69 novos aprovados. `T1_EDITORIAL_STANDARD_FROZEN_AND_CALIBRATED`.**

Data: 2026-10-04. Host-side apenas: sem staging físico, sem flash, sem alteração de SD, sem commit, tag ou push. O detalhamento das etapas está em `ENTENDA_BATCH05_REPORT.md`.

## 1. Resultado

| Item | Valor |
|---|---|
| Entradas do lote | 72 = 69 novas + 3 pilotos reutilizados, todas `HUMAN_APPROVED_T1` |
| `PENDING_HUMAN_REVIEW` | 0 |
| Versões `RETIRED` (evidência preservada) | 47 |
| editorial_checks sem resolução | 0 |
| `HARD_FAIL` (validator v2) | 0 |
| Acervo ENTENDA aprovado (build real do candidato host) | **289** = 220 anteriores + 69 do Batch05 |
| Candidato host | `HOST_CANDIDATE_ALL_APPROVED_NOT_STAGED`; 448 linhas de lookup, todas aprovadas; 3 builds idênticos byte a byte; nada removido ou alterado no par aprovado; 86 linhas acrescentadas = targets do Batch05 |

## 2. Como os 69 foram aprovados

| Etapa | Itens | Aprovados sem alteração | Ajustados |
|---|---|---|---|
| Rodada 01 (art. 37, HIGH) | 7 | 1 | 6 |
| Rodada 02 (arts. 38, 39, 41, HIGH) | 9 | 2 | 7 (art. 39 em v3) |
| Rodada 03A (art. 40, HIGH) | 11 | 3 | 8 |
| Rodada 03B (art. 40, HIGH) | 11 | 1 | 10 |
| Fila D da triagem | 2 | 0 | 2 |
| Revisão final calibrada (29 restantes) | 29 | 19 (1 deles com microajuste T1, art. 38) | 10 |
| **Total** | **69** | **26** | **43** |

**Pós-aprovação:** art. 37, § 7º, foi de v2 para **v3**, com a finalidade não declarada retirada. A v2 ficou `RETIRED` com `superseded_by` → v3. Pela regra do motor, a v2 mantém o `review_status` histórico `HUMAN_APPROVED_T1`.

## 3. Revisão final calibrada (29)

- **Confirmados como limpos:**
  - 4 de 5 CLEAN_LOW;
  - 11 de 15 CLEAN_MEDIUM;
  - 4 alertas da fila C reclassificados como falso positivo (art. 37, II, X, XII; art. 39, § 2º).
- **Ajustados (10):**
  - art. 37, VIII: condição de compatibilidade sem base no inciso;
  - art. 37, IX: Tema 612 na camada externa; a natureza permanente não invalida sozinha;
  - art. 37, XV: irredutibilidade protege o montante nominal;
  - art. 38, I: enumeração não exaustiva;
  - art. 38, IV: ressalva da promoção por merecimento;
  - caput do art. 37: legalidade sem formulação absoluta;
  - art. 37, XVIII: generalização retirada;
  - art. 37, § 13: finalidade presumida retirada;
  - art. 38, II: justificativa econômica retirada;
  - art. 39, § 7º: finalidade presumida retirada.
- **Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`:** art. 37, IX (Tema 612) e XV (irredutibilidade; nenhum número de tema foi indicado e nenhum foi acrescentado).

## 4. Lições da calibração

- Fila C: 5 de 9 alertas úteis.
- CLEAN_LOW: 1 problema em 5 (art. 37, VIII).
- CLEAN_MEDIUM: 4 problemas em 15.
- **Sem alerta ≠ aprovação automática segura**: o pipeline reduz o volume humano, mas não aprova sozinho. `AUTO_APPROVE_LOW` e `AUTO_APPROVE_MEDIUM` continuam OFF.
- Três regras generalizáveis entraram no validador v2: `EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE`, `EXCEPTION_OR_RESSALVA_DROPPED`, `EXHAUSTIVE_ENUMERATION_RISK`.
  - Cada uma pega o seu caso de regressão e fica em silêncio na versão aprovada.
  - Nos 69 aprovados há 2 falsos positivos conhecidos, registrados.
- Regressão do validador v2:
  - 40 de 43 versões corrigidas por humanos detectadas;
  - 3 falsos negativos conhecidos (correções conceituais);
  - 0 alertas pendentes nos 69 aprovados.
- O sugeridor automático de microajuste errou uma vez (art. 38, "da" → "de"). A sugestão continua sendo só sugestão.

## 5. Dependência externa

O resolvedor tem três estados: `EXTERNAL_EVIDENCE_AVAILABLE`, `EXTERNAL_EVIDENCE_LOCAL_PENDING` e `EXTERNAL_VERIFICATION_REQUIRED`.

- **Art. 37, § 7º → Lei nº 12.813/2013:** a relação local segue em quarentena (`C_EXTERNA_PENDENTE_VALIDACAO` / `OCULTAR_ATE_VALIDAR_VIGENCIA`) e **não foi promovida**.
- A aprovação do ENTENDA apoia-se na proveniência da revisão humana com fonte oficial. ENTENDA e Relations Engine são processos independentes (A6.11).

## 6. Integridade

- Lei Seca: runtime `7ef82290…` inalterado.
- Rodadas 01, 02, 03A, 03B e fila D: arquivos inalterados.
- Pilotos: corpus principal inalterado.
- Firmware e SD: não tocados.
- Único arquivo versionado alterado: `ENTENDA_T1_EDITORIAL_STANDARD.md` (seção 16 → A6).
- Testes: ENTENDA 139/139, LEGAL_TARGET_ID 65/65, DEVICE 353/353. Builds do lote, triagem e candidato determinísticos.

## 7. Pendências e próximos passos (não executados)

- **Staging físico e teste físico do Batch05** (220 + 69): dependem de autorização explícita.
- **Backlog de auditoria do acervo anterior:** `T1_LEGACY_AUDIT_BACKLOG.md`, com 49 itens. Prioridade para art. 7º, I, e art. 5º, LXXI. Não bloqueia.
- ~~Observação sobre o art. 38, II~~: resolvida na correção final (§ 8).
- **Próximo lote:** `ENTENDA_ENGINE/T1_SCALE_PIPELINE_PROPOSAL.md` (atualizada). Batch06 não iniciado.

## 8. Correção editorial final (2026-10-04) — `BATCH05_ENTENDA_BASELINE_EDITORIALLY_CLOSED`

- **Art. 38, II, de v2 para v3 (escopo `CF88_BATCH05_FINAL_SANITY_FIX`):** em O QUE SIGNIFICA, "O afastamento é obrigatório, porque o cargo de Prefeito exige dedicação ao Executivo municipal." passou a "O afastamento do cargo, emprego ou função é obrigatório."
  - A conclusão (afastamento obrigatório, inciso II) foi mantida e só a justificativa causal não declarada saiu.
  - A opção de remuneração não foi repetida: o mesmo parágrafo já diz que "O servidor afastado pode escolher entre a remuneração do vínculo funcional e a remuneração do mandato de Prefeito."
- **Versionamento:** a v2 ficou `RETIRED` com o status histórico `HUMAN_APPROVED_T1` (semântica normal do motor, não alterada) e `superseded_by` → v3. A v3 está `HUMAN_APPROVED_T1`.
  - Evidências: `BATCH_05_DRAFTS_PRE_SANITY_FIX.json` e `SANITY_FIX_POST_APPROVAL_EDIT.json`.
- **Regressão:** a regra `TELEOLOGY_SPECULATIVE` ganhou a alternativa causal "porque o/a X exige/requer/demanda", sem regra nova e sem detector específico.
  - Ela dispara nas v1/v2 do art. 38, II, e em mais nenhum dos 289 textos aprovados nem nas versões retiradas.
  - A v3 não dispara.
- **Estado:**
  - 72/72 do lote e 69/69 novos `HUMAN_APPROVED_T1`; 0 pendentes; 0 `HARD_FAIL`; 47 versões `RETIRED`;
  - candidato host com 289 aprovados, 3 builds idênticos e o par aprovado preservado;
  - autoaprovação OFF;
  - Lei Seca, Relations Engine e firmware intactos.
- **Testes:** ENTENDA 141/141, LEGAL_TARGET_ID 65/65, DEVICE 353/353.
