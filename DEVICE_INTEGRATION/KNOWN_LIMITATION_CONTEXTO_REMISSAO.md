# KNOWN LIMITATION — CONTEXTO lê remissão textual como estrutura local

**Registrada em:** 2026-10-04, durante a validação física de `MARIA2006_SOURCE_REPAIR`.

**Estado:** CORRIGIDA (remissões), aprovada fisicamente em 2026-10-04: `CONTEXT_CITATION_GUARD_PHYSICAL_REPORT.md`. Os 68 casos ambíguos
continuam abertos. Texto transcrito por artigo alterador: `KNOWN_LIMITATION_CONTEXTO_EM_TRANSCRICAO_LEGISLATIVA.md`.

**Atualização (2026-10-04, LEX_CONTEXT_CITATION_GUARD):** correção candidata em `contexto_juridico.h` (somente DEVICE V1), ainda
**sem teste físico**. O caso do art. 1 da MARIA2006 deixa de produzir `PAR=8`. A auditoria das 72 normas eliminou 996 gatilhos falsos
sem perder nenhum registro estrutural aprovado. Continuam abertos 68 casos ambíguos, em que o marcador fica sozinho na linha e a
remissão segue na linha seguinte. Detalhes em `CONTEXT_CITATION_GUARD_REPORT.md`.

## Sintoma

Ao rolar o texto, o `CONTEXTO` (`CONTEXTO: ART=.. PAR=.. INC=.. ALINEA=..`) pode tomar uma remissão a outro dispositivo como se
fosse um parágrafo, inciso ou alínea do artigo em leitura.

## Exemplo físico confirmado

**Norma:** Lei 11.340/2006 (Lei Maria da Penha), art. 1º. O texto do artigo cita "§ 8º do art. 226 da Constituição Federal".

**Serial:** `backups/maria2006_physical_deploy_20261004/serial/serial_boot.log`, SHA-256 `000ab09b…bc62`.

```
CONTEXTO: ART=1 PAR=8 INC=- ALINEA=-
```

O correto seria `ART=1 PAR=- ...`, porque o § 8º pertence ao art. 226 da CF, não ao art. 1º da Lei.

## Escopo

**Afeta:** só a exibição do CONTEXTO, pelo detector genérico de estrutura no firmware.

**Não afeta:**
- o texto;
- a busca indexada (`*_ARTICLE_SEARCH.IDX`), que não indexa remissões (0 falsos positivos na auditoria da MARIA2006);
- o catálogo;
- o pouso da busca;
- os alvos jurídicos (ACTIVE_TARGET).

Não tem relação com o reparo da fonte da MARIA2006.

## Direção futura (não implementada)

O detector só deveria aceitar `§`, inciso ou alínea como estrutura local quando o marcador abre uma linha estrutural. Uma menção no
meio da frase, sobretudo seguida de "do art.", "da Lei" ou "da Constituição", não deveria contar. Uma mudança assim exige firmware
novo, com o fluxo normal de build, flash e validação física.
