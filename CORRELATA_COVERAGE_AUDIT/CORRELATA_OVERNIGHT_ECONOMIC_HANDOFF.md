# CORRELATA — handoff da missão noturna econômica

- **Branch:** `cf-correlata-coverage-audit`. Nada foi aplicado ao motor, ao cartão ou ao firmware.
- **Branches intocadas:** `device-entenda-810`, `reconcile-macro07-macro08` e `main`.

## HIGH: 106/106, fechado sem HOLD

- **Totais:** APPROVE 36, ADJUST 41, REJECT 29, HOLD 0, NEEDS_SOURCE 0; **aceitos 77**.
- **Rota dos aceitos:**
  - MAIN_CORPUS_ROUTE_REQUIRED 19;
  - INGESTION_REQUIRED 51;
  - DEVICE_RESOLVABLE_NOW 7.
- **Temporal dos aceitos:**
  - VACATIO_LEGIS 2 (Lei 14.965, bloqueados até 2028-01-01);
  - TRANSITIONAL 2;
  - PARTIAL_EFFECTS 11: LC 214 (7) e LC 227 (2), que já vinham dos lotes, e Lei 14.701 (2).
- **Os 4 HOLD resolvidos** (camada `HIGH_FINAL_CLOSURE_REVIEW` do consolidado; os arquivos dos lotes guardam a decisão da época):
  - art. 40, § 7º × Lei 8.112: REJECT (`CURRENT_CONSTITUTIONAL_REGIME_NOT_REPRESENTED_BY_LEI_8112`);
  - art. 231, § 1º × Lei 14.701: ADJUST, REGULAMENTA, PARTIAL_EFFECTS e JUDICIAL_RESTRICTIONS;
  - art. 231, § 3º × Lei 14.701: REJECT (`CROSS_REFERENCE_ONLY`);
  - art. 231, § 6º × Lei 14.701: ADJUST, COMPLEMENTA, ESCOPO_PARCIAL e `DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION`.
- **Lei 14.701 no STF** (consulta oficial única ao portal do STF):
  - mérito em 2025-12-19, com inconstitucionalidade parcial;
  - embargos pendentes, com vista ao Min. Toffoli desde 19/08/2026;
  - `REVALIDATE_ON_FINAL_ED = true`.

## Legado: 44/44 visíveis com decisão

- **Origem das decisões:** 19 da C1A; 25 revisados agora, sem download novo (texto do cartão mais páginas oficiais já baixadas).
- **Totais:** KEEP 10, KEEP_WITH_ROUTE_FIX 5, RETARGET 5, REPLACE 5, REMOVE 18, HOLD 1. O HOLD é o da C1A: art. 37, § 3º, III.
- **Destaques:**
  - **Lei 14.965 × art. 37, II:** KEEP, mas em vacatio, com `SUPPRESS_UNTIL_EFFECTIVE`.
  - **LC 70:** retarget para o art. 195, I, b; revalidar em 2027 (extinção da COFINS).
  - **LC 63:** retarget do art. 158, § 1º, II para o inciso I.
  - **LC 199:** retarget para o art. 146, III, b; converge com um HIGH.
  - **PNE:** 6 vínculos de fan-out viram 1 no caput do art. 214.
  - **Lei 12.734:** REMOVE (lei alteradora).
- **Arquivos:** `CF88_CORRELATA_LEGACY_FULL_REVIEW.json` e `.md`.

## C2: arquitetura projetada; protótipo passou

- **Desenho:** overlay `CF88_CORRELATA_ADDITIONS.json` (não criado) com o catálogo imutável. Exclusões para os erros legados; additions para as relações novas.
- **ADCT:** passa pela confirmação do runtime, sem liberar UNKNOWN.
- **MAIN_CORPUS:** rota com fallback seguro.
- **Vacatio:** opção A, `DO_NOT_PUBLISH_AS_CURRENT`.
- **Status judicial:** estrutura mínima com aviso curto.
- **TRANSITIONAL:** exige `revalidate_on`.
- **Protótipo:** 6 fixtures válidas e 1 inválida. O fail-closed cobre todos os casos pedidos, e os testes passam.
- **Blockers para C3:**
  - firmware (modo de acervo principal e limite de 32 normas e 64 linhas);
  - ingestão de 51 relações;
  - integração do validador ao motor e status de exclusão temporária;
  - UI do aviso judicial.

## Adiado por orçamento

- `INGESTION_PHASE_DEFERRED_FOR_CREDIT_BUDGET`: nenhuma norma baixada em massa nem ingerida.
- `MEDIUM_DEFERRED = 191` (não aberto).
- `LOW_DEFERRED = 446` (não aberto).
- **NEXT_STEP registrado, não executado:** rota para anexos de norma, para a Meta 19.a do PNE no art. 214, VI.

## Próxima decisão humana

Revisar e aprovar três pontos:

1. as 4 resoluções de HOLD;
2. as 25 decisões legadas novas;
3. a arquitetura C2, em especial a recomendação de vacatio A e a regra do ADCT pelo runtime.

Depois, escolher a ordem da implementação (C3). A sugestão é esta:

1. exclusões e additions no motor, só com os 7 destinos já no cartão e os vínculos legados corrigidos;
2. firmware com a rota MAIN_CORPUS;
3. ingestão em lotes;
4. só então MEDIUM.
