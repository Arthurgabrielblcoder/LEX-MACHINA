# JURIS UPDATER — especificação curta (Parte L)

> Fluxo de linha de comando sobre as ferramentas que já existem em `JURISPRUDENCE_AUDIT/`. Sem GUI e sem projeto novo. Ele **nunca** publica sozinho.

## Objetivo

Manter a camada de jurisprudência CF/ADCT atualizada e auditável:

- revalidar os itens provisórios;
- pesquisar o backlog em lotes;
- registrar a ratificação humana;
- materializar só o que foi ratificado, em pacote host-only, para deploy manual.

## Regras fixas

1. **Fontes:** só oficiais (STF, STJ, TSE, Planalto). Nada de blogs, Jusbrasil ou snippets.
2. **Captura:** cada fonte guarda URL, data, método e sha256 do texto renderizado ou dos bytes.
3. **Bloqueios:** CAPTCHA e desafios anti-robô nunca são contornados. O item fica UNRESOLVED_EXTERNAL.
4. **Propostas:** toda decisão nasce `AWAITING_USER_RATIFICATION`, com `human_approved=false`. Só o registro de ratificação do usuário muda isso.
5. **Fail closed:** item provisório vencido, fonte ausente, namespace ou tempo divergente, ou tipo desconhecido bloqueiam a etapa.
6. **Camadas congeladas:** CORRELATAS_1_CF, REFERENCES_4_CF e ENTENDA_CF_ADCT não são tocadas. O builder verifica os bytes da base.

## Etapas e comandos

| # | Etapa | Comando | Saída | Bloqueia quando |
|---|---|---|---|---|
| 1 | Gate de provisórios | `check_j2b_provisional.py --registry J2_PROVISIONAL_REGISTRY.json --as-of AAAA-MM-DD` | PASS / REVALIDATION_REQUIRED | prazo vencido ou gatilho disparado |
| 2 | Registro de provisórios | `build_j2_provisional_registry.py [--check]` | `J2_PROVISIONAL_REGISTRY.json` | lote com `revalidation` fora do registro |
| 3 | Seleção do lote | `build_j2_batch.py --batch N --level L --selection-only` | fila determinística (regra J0) | lote anterior ausente |
| 4 | Pesquisa | módulo `J2_<L>_BACKLOG/j2_batchNN_review.py` (`SOURCES`, `REVIEW`) | evidências oficiais | campo, fonte ou namespace faltando |
| 5 | Decisões e relatório | `build_j2_batch.py --batch N --level L` + `render_j2_batch_report.py` | `J2_BATCHNN_DECISIONS.json` e `.md` | validador `j2_review_common` |
| 6 | Dossiê e reconciliação | `render_j2_ratification_dossier.py [--check]` | `J2_RATIFICATION_DOSSIER.md` e `J2_RECONCILIATION.json` | físico ≠ 261/160 (ou o novo baseline instalado) |
| 7 | Ratificação (humana) | o usuário responde no chat; um registro `RATIFICATION` com autor, data e decisões é gravado no overlay | — | qualquer item sem ratificação explícita |
| 8 | Materialização | overlay `apply_j2*_overlay.py` → export RUNn (verifica os bytes da base e só recalcula a flag J) | pacote host-only | tipo sem suporte (`juris_types.label` lança erro), bytes da base divergentes |
| 9 | Auditoria de isolamento | `build_j2*_isolation_audit.py` | relatório | diff fora da camada de jurisprudência |
| 10 | Deploy | **manual, pelo usuário**, com checklist físico | — | sem teste físico, não congela |

## Tipos

Rótulos, fichas e tribunais vêm de `juris_types.py`; ver `JURIS_TYPE_ARCHITECTURE.md`. Tipos novos (HC, MS, AP, AI, Inq, Rcl, MI e súmulas do STJ/TSE) só entram em pacote junto com o firmware de tipos genéricos, depois de gravado e testado fisicamente.

## Fora do escopo

- Coleta automática em massa de portais.
- Agendamento.
- Publicação sem ratificação.
- Escrita no microSD.
- Gravação de firmware.
