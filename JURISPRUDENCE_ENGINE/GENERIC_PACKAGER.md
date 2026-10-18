# Empacotador genérico multinorma de jurisprudência

```
GENERIC_PACKAGER = PASS · DUPLICATE_QUERY_KEYS_IN_NORMALIZED_OUTPUT = 0
CF_RELATIONS_REPRODUCED = 315/315 · CF_TARGETS_REPRODUCED = 198/198 · CF_LABELS_IDENTICAL = YES · CF_FICHAS_IDENTICAL = YES
CF_BACK_BEHAVIOR_IDENTICAL = YES (uma união documentada: art. 62 artigo + caput)
HOST-ONLY · baseline físico J2I intocado · arquivos legados 05_INDICES_ESP32 intocados
```

Código: `generic_packager.py`. Testes: `tests/test_generic_packager.py`.

## Problema que resolve

O `JUR_LOOKUP.IDX` legado do J2I tem **237 linhas para 221 chaves**. As rodadas J2G/J2H acrescentaram grupos novos para targets que já tinham linhas. O caminho legado do firmware usa só o **primeiro** grupo de cada chave.

- **Na CF:** isso não aparece no aparelho, porque a lista vem da camada LEXV1 (`REF_PAYLOAD`).
- **Nas outras normas:** elas usam o caminho legado, então o defeito apareceria. Por isso o problema precisava ser corrigido antes de publicar o CC.

## Entrada (sem nada específico da CF)

- **Relação normalizada:** `{norm, target_id, precedent_id}`. A norma vem do namespace do target, pela gramática `LEGAL_TARGET_ID`.
- **Registro do precedente**, um por precedente: `{tribunal, tipo, numero, status, titulo, fonte}`. A ficha é `JT.ficha(precedent_id)`.
- **Fichas:** as que já estão no cartão, mais textos de fichas novas.

## Saída: camada normalizada paralela

Pasta: `99_JURISPRUDENCIA_V2/06_NORMALIZADO/`.

| Arquivo | Conteúdo |
|---|---|
| `JUR_LOOKUP.IDX` | Mesmo esquema do legado (`ORIGEM_NORMA\|ARTIGO\|PARAGRAFO\|INCISO\|ALINEA\|OFFSET\|QUANTIDADE`), com **uma linha por chave de consulta**: todos os vínculos da chave ficam num único grupo contíguo |
| `JURISPRUDENCIA.IDX` | Mesmas 8 colunas. O ID da linha leva o namespace real do target (no legado, linhas do ADCT diziam `CF88`) |
| `03_CONTEUDO/*.TXT` | Só fichas **novas**. Cada precedente tem uma ficha, compartilhada por todos os targets de todas as normas |
| `MULTINORM_MANIFEST.json` | Por norma: relações, targets com J, chaves, precedentes distintos, fichas, tipos, tribunais e provisórios. Também lista as fichas compartilhadas entre normas e o sha256 de cada arquivo |

**Por que uma camada paralela, e não reescrever o legado:**
- os arquivos `05_INDICES_ESP32` são os do baseline físico J2I e não mudam;
- o firmware multinorma (protótipo, edição 7) prefere a camada normalizada quando os dois arquivos dela existem no cartão; sem eles, usa os arquivos legados exatamente como antes.

## Regras (fail closed)

O empacotador recusa:
- target malformado, de namespace desconhecido ou **inexistente no índice real** da norma (`known_targets`: CF88/ADCT do J2I mais CC2002);
- precedente sem registro;
- tribunal fora da lista (ou divergente do prefixo do ID);
- grupo com mais de 32 relações (`MAX_RELACOES_ARTIGO`) ou de 255 (`uint8`);
- campo com `|` ou quebra de linha;
- ficha ausente (nem no cartão, nem nova).

Vínculo repetido conta uma vez.

## Fixture da CF: J2I_FROZEN_315_198

**Entrada:**
- as 315 relações visíveis do `REF_PAYLOAD` (LEXV1);
- os registros de precedente do `JURISPRUDENCIA.IDX` legado, por identificador (270 registros, consistentes entre linhas).

| Verificação | Resultado |
|---|---|
| Relações | 315/315 (CF88 311 + ADCT 4) |
| Targets com J | 198/198 (CF88 194 + ADCT 4) |
| Chaves de consulta | 197, **0 duplicadas** |
| Rótulo do aparelho (`juris_types.label` sobre tipo/tribunal/número) | idêntico ao do registro J2I nas 315 relações |
| Título curto | idêntico ao `REF_PAYLOAD` (multiconjunto das 315) |
| Fichas | 257, **todas já no cartão**; 0 fichas novas |
| BACK | Reabrir a mesma chave devolve a mesma lista; a ordem dentro da chave é a do `REF_PAYLOAD` |

**Diferenças deliberadas, explicadas e testadas:**
1. **Art. 62 da CF:** `CF88:ART.62` (Tema 33) e `CF88:ART.62:CAPUT` (Tema 1196) caem na mesma chave `CF88|62|||`. A posição de leitura do caminho legado não distingue o artigo-unidade do caput, então a chave mostra a união dos dois. As relações continuam individualmente contáveis (315). No aparelho, a CF segue pela LEXV1, que mantém os dois separados.
2. **Grupos repetidos do legado:** viram um grupo só. Nas 16 linhas extras do J2I, a lista normalizada mostra todos os vínculos, e não apenas o primeiro grupo. Isso corrige o defeito, e é intencional.
3. **ID de linha do ADCT:** usa `ADCT:` em vez de `CF88:`. O firmware não lê o ID para consulta; ele só serve de rastreabilidade.

## Multinorma

| Caso | Resultado |
|---|---|
| CF88 + ADCT + CC2002 no mesmo pacote | Manifesto por norma (ex.: CF88 311/194, ADCT 4/4, CC2002 3/3) |
| Ficha compartilhada | `STF_RG_932.TXT`: 1 registro, servindo a CF art. 7º, XXVIII e a CC art. 927, p.u.; sem ficha duplicada; vínculos contados separadamente |
| Súmula 403/STJ | Dois targets do CC (186 e 927), uma única ficha nova `STJ_SUMULA_403.TXT` |
| Alternância CF → CC → CF | Lista da CF idêntica antes e depois |
| Norma sem jurisprudência (CPC) | Fluxo anterior |
| Target inexistente (`CC2002:ART.9999`) | Recusado |
| Tribunal fora da lista; ficha ausente | Recusado |

## Firmware multinorma: build atual (host-only, NÃO gravado)

Arquivo: `firmware_multinorm/MULTINORM_PROTOTYPE_BUILD.json`. São 10 edições sobre a fonte do app J2I.

| Item | Valor |
|---|---|
| Programa | 1.107.363 B (**+5.332 B**) |
| RAM estática | 126.188 B (**+40 B**) |
| app0 livre | 203.216 B |
| PSRAM | +8 B por lookup (campo `norma[16]`); a camada normalizada da CF tem 197 lookups, contra 237 no legado |
| IDs longos | `HEDIONDOS1990`, `CONSORCIO2008` e `ALIENPAR2010` identificados e sem truncamento (char[16]). No char[8] do J2I, os três falham |
