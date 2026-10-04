# KNOWN LIMITATION — CONTEXTO_EM_TRANSCRICAO_LEGISLATIVA

**Registrada em:** 2026-10-04, na validação física de `LEX_CONTEXT_CITATION_GUARD` (`CONTEXT_CITATION_GUARD_PHYSICAL_REPORT.md`, § 5).

**Estado:** ABERTA. Melhoria futura, não bloqueante. Não será corrigida na missão do guard; não introduzir quote-state nem look-behind agora.

## Sintoma

Um artigo **alterador** transcreve entre aspas dispositivos de **outra** norma. Uma linha transcrita como `§ 9º …` tem forma
estrutural legítima, e o CONTEXTO a aplica ao artigo alterador como se fosse subdivisão local.

## Exemplo físico confirmado

**Texto:** Lei 11.340/2006 (MARIA2006), art. 44:

```
Art. 44. O
art. 129 do Decreto-Lei nº 2.848, de 7 de dezembro de 1940
(Código Penal), passa a vigorar com as seguintes alterações:
"Art. 129. ......
§ 9º
Se a lesão for praticada contra ascendente, descendente, ...
```

**Serial:** `backups/context_citation_guard/flash/serial_boot_and_tests.log`, SHA-256 `667f9bf8…69d9`:

```
CONTEXTO: ART=44 PAR=-
CONTEXTO: ART=44 PAR=9
```

O § 9º pertence ao art. 129 do Código Penal, não ao art. 44 da Lei Maria da Penha.

## O que já está correto

**Remissões** (`art. 129 do Decreto-Lei`, `§ 3º do art. 100`): não mudam o CONTEXTO, por causa do `CONTEXT_CITATION_GUARD`, que foi aprovado
fisicamente.

## Por que a correção atual não cobre

A linha `§ 9º` é idêntica a um cabeçalho real e está sozinha na linha. A decisão do guard usa só os bytes da própria linha. Distinguir
texto transcrito exige saber que há aspas abertas, ou seja, um estado entre linhas. Esse estado precisaria ser mantido de forma idêntica
em scroll DOWN, scroll UP, pouso, refill, reconstrução e âncora.

## Escopo

**Afeta:** só a exibição do CONTEXTO dentro de transcrições de artigos alteradores.

**Não afeta:**
- ACTIVE_TARGET e camadas (vêm do TEXT_MAP);
- busca indexada;
- pouso;
- texto.

**Mesmo comportamento** do firmware anterior ao guard.

## Direção futura (não implementada)

Reconhecer o bloco transcrito, aberto por `“` / `"` após "passa a vigorar com…" e fechado no fim da transcrição (`” (NR)`), e suspender
o CONTEXTO estrutural local dentro dele. É preciso fazer isso com o mesmo estado em todos os caminhos do leitor. Exige firmware novo,
testes de caminho (DOWN/UP/pouso/refill/âncora) e validação física.
