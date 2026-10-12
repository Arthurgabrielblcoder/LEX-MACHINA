# C2 — Rotas de destino no aparelho e regra do ADCT

**Projeto.** Nada no cartão, no firmware nem nos índices `REF_LOOKUP` e `REF_PAYLOAD` foi alterado.

## Situação atual

- O botão 1 do Device V1 resolve `REF_PAYLOAD` → `relacao_id` → `RELACOES.IDX` → `EXT_NORMAS`. Só abre normas externas copiadas para o cartão.
- O cache legado do firmware limita a tabela a 64 linhas de lookup e 32 normas.
- Das relações HIGH aceitas (77): 19 têm destino no acervo principal (`MAIN_CORPUS_ROUTE_REQUIRED`), 51 exigem ingestão (`INGESTION_REQUIRED`) e 7 já resolvem no cartão.

## `destination_route = EXT_NORMAS`

- **Mantida como está** para normas externas: entrada em `EXT_NORMAS` e índice de artigos em `EXT_ARTIGOS`.
- **Ingestão:** uma norma EXT ainda não ingerida não bloqueia a decisão jurídica. Ela gera `BLOCKED_INGESTION_REQUIRED` e não é publicada.
- **Nesta missão:** nenhuma norma foi ingerida (`INGESTION_PHASE_DEFERRED_FOR_CREDIT_BUDGET`).

## `destination_route = MAIN_CORPUS`

O destino é uma norma que já está no acervo principal do Vade Mecum, por exemplo `CDC1990`, `RJU1990` ou `LAI2011`.

- **Sem duplicação.** A norma nunca é copiada como `EXT_*`. O validador rejeita `MAIN_CORPUS_NORM_DUPLICATED_AS_EXT`.
- **Payload proposto:** `MAIN|<norm_id>|<artigo>|<fallback>`. É uma linha nova em `RELACOES` com modo `ABRIR_NORMA_PRINCIPAL`; não usa `EXT_NORMAS`.
- **Resolução no aparelho:** `norm_id` → pasta e arquivo do acervo principal, pelo manifesto do cartão; artigo → índice de artigos da norma principal.
- **Fallback seguro:**
  1. abrir o artigo indicado;
  2. se o índice não tiver o artigo, abrir a norma no início e mostrar "artigo não localizado";
  3. se a norma não estiver no cartão, não exibir o vínculo e registrar o erro no log.
  - O fallback nunca leva a outra norma.
- **No build (fail closed):** `MAIN_CORPUS_UNRESOLVABLE` quando a norma não é do acervo principal; `DESTINATION_ARTICLE_INVALID` quando o artigo não está no índice.
- **Dependência:** exige firmware novo (modo `ABRIR_NORMA_PRINCIPAL`). Até lá, as 19 relações MAIN_CORPUS ficam aprovadas e não publicadas.

## ADCT (`UNKNOWN_VALIDITY` no motor)

- **O problema:** o `CF88_TARGET_STATUS.json` marca os targets ADCT como `UNKNOWN_VALIDITY` ("texto operacional vigente nao contem o ADCT"). A regra atual de additions aceita só CURRENT e STRUCTURAL, então rejeitaria todo o ADCT.
- **O que não fazer:** liberar `UNKNOWN_VALIDITY` de forma genérica. Isso abriria também os 812 targets de validade desconhecida.
- **Regra proposta:** um target ADCT com status de motor `UNKNOWN_VALIDITY` só entra quando valem **todas** as condições abaixo.
  1. O target existe no runtime do aparelho (`CF88_TARGETS.IDX` do pin C0).
  2. O `legal_status` no runtime é `CURRENT`, ou é STRUCTURAL pelo tipo.
  3. O target é alcançável: está no `CF88_TEXT_MAP.IDX`.
  4. A decisão humana está aprovada (`HUMAN_APPROVED_CORRELATA_V1`).
- **Resultado no validador:** `target_check = ADCT_RUNTIME_CONFIRMED`; se alguma condição falhar, `ADCT_NOT_CONFIRMED_BY_RUNTIME`.
- **Casos de teste:** ADCT, art. 10, II, b (LC 146) e ADCT, art. 128, § 2º (LC 160) passam. O mesmo target sem alcance no TEXT_MAP é rejeitado.
- **Correção definitiva (C3, não feita):** incluir o ADCT no texto operacional do motor, para que ele produza CURRENT ou HISTORICAL_ONLY direto. A regra do runtime é a ponte segura até lá.

## Capacidade do cartão

- Os 77 aceitos ultrapassam o cache legado de 32 normas e 64 linhas.
- A publicação em massa depende do firmware com Relations V2 sem esse limite, ou de paginação.
- Fica registrado como blocker da fase de ingestão; não foi tratado agora.
