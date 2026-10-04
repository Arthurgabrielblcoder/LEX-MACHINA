# KNOWN LIMITATION — CONTEXTO lê remissão textual como estrutura local

**Registrada em:** 2026-10-04, durante a validação física de `MARIA2006_SOURCE_REPAIR`.

**Estado:** ABERTA. Não será corrigida durante o freeze da MARIA2006.

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
