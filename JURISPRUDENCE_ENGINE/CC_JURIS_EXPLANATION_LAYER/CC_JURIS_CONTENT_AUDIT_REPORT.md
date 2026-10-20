# Auditoria da camada explicativa CC

## Resultado

- Precedentes: `574/574`; relações: `653/653`.
- Conteúdo pronto: `648`; revisão: `5`; evidência requerida: `0`.
- Confiança HIGH/MEDIUM/LOW: `39/614/0`.
- Evidência oficial local: `574` precedentes; pesquisa externa: `0`.
- Erros genéricos: `0`; leakage: `0`; conflitos de resumo: `0`; Group F: `0`.
- Amostra semântica estratificada: `131` relações, incluindo todos Group A e os seis fixtures. A amostra valida regras e provenance; não é uma segunda revisão humana independente.
- Renderização 320×240/UTF-8/abertura/BACK: `PASS`.
- Suítes: Engine `153/153`; Audit `119/119`; Legal Target ID `93/93`; Correlatas `115/120`, as mesmas cinco falhas históricas.
- Firmware Content V2: compilado host-side; programa `1109011` bytes, RAM estática `127724` bytes, app0 livre `201568` bytes. Flash: não.

## Tamanho

- Fichas antigas compartilhadas (572 artefatos da materialização V1): `300824` bytes.
- Fichas V2 compostas (653): `545159` bytes.
- Delta: `244335` bytes; máxima `1320`; média `834.85`.

## Diagnóstico legado

`LEGACY_FICHAS_WITHOUT_SUBSTANTIVE_CONTENT = 277` no inventário físico conhecido. É diagnóstico; nenhuma ficha legada de CF/CC foi alterada.

## Limites

As relações continuam humanamente aprovadas. Registros marcados `CONTENT_EVIDENCE_REQUIRED` não devem ser promovidos automaticamente. O renderer V2 foi preparado host-side; nenhuma mídia física foi acessada.
