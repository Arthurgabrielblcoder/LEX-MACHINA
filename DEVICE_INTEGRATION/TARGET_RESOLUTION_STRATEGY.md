# TARGET_RESOLUTION_STRATEGY (V1)

> **Atualização V1-A2B: estratégia ativa.**
>
> - A fonte primária é o `CF88_TEXT_MAP.IDX` sobre o `CF88_RUNTIME.txt` (`RUNTIME`), com a guarda de tamanho e sha256.
> - A concordância do parser legado do firmware com o novo mapa é de 97,31% (3.295/3.387). As divergências são sufixos de letra (16) e fragmentos de link do ADCT (75), que o parser insensível a maiúsculas lê como artigo. Por isso o parser segue apenas como diagnóstico.
> - A resolução do ADCT usa `#NAMESPACE_START_ADCT|429242`.

> **Atualização V1-A2.** O texto exibido e o texto indexado precisam ser **os mesmos bytes**. O `TEXT_MAP` v2 declara `RUNTIME_STATUS`; hoje ele vale `LEGACY_STRUCTURAL_NOT_RUNTIME`, porque o `CF88_RUNTIME` (CF vigente + ADCT vigente) não foi resolvido.
>
> Enquanto isso, o firmware candidato recusa o mapa (`LEXV1_FAIL_TEXT_MAP_NOT_RUNTIME`). O parser legado fica apenas como diagnóstico e não resolve camadas V1.
>
> A comparação parser × mapa, refeita na A2, deu o mesmo resultado: 97,84% de concordância e **0 divergências nos 163 targets com ENTENDA**.

Pergunta: ao exibir um trecho da Lei Seca, como o ESP32 sabe que está em `CF88:ART.5:INC.V` ou em `CF88:ART.37:PAR.6`?

## O que já existe

1. **Firmware v7.12.0.** `contexto_juridico.h` aplica, linha a linha, regras simples ao texto visível:
   - `Art.` → artigo;
   - `§` → parágrafo;
   - `Parágrafo único` → `unico`;
   - letra seguida de `)` → alínea;
   - romano seguido de separador → inciso.

   A linha central da tela define o dispositivo ativo, e a tupla resultante já é usada pelos índices legados.
2. **Índice estrutural aprovado** (`LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json`). Traz 3.956 targets com `line_start` e `occurrences` no `cf.txt` estrutural (sha256 `d9f3d6b9…`, 928.009 bytes), incluindo o ADCT.

## Estratégia V1: pré-processar no PC, lookup barato no aparelho

### Primária: `CF88_TEXT_MAP.IDX`

O mapa é derivado do índice aprovado, sem parser novo.
- **Linhas:** uma por linha física que inicia um dispositivo, no formato `OFFSET(10 dígitos)|LINHA|TARGET_ID`.
- **Prioridade na mesma linha:** vence o tipo mais específico. Na linha do artigo vale `ART.n`, e não `ART.n:CAPUT`.
- **Validação no build:** cada linha é conferida contra o texto real:
  - `Art` para artigo;
  - `§` para parágrafo;
  - `Par` para parágrafo único;
  - romano para inciso;
  - `x)` para alínea.

  O resultado foi 0 divergência em 4.074 linhas.

**No aparelho:**
1. O leitor já conhece o offset (byte) da linha central (`origemTopoByte` e afins).
2. A busca binária do *floor* no `TEXT_MAP` devolve o target_id em cerca de 9 seeks no SD, ou sem nenhum seek se o mapa estiver em PSRAM (148 KB).
3. O namespace sai de `#NAMESPACE_START_ADCT|661181`: a partir desse offset o texto é ADCT. O parser de runtime não sabe disso sozinho.

**Condição de uso.** O arquivo aberto precisa ter exatamente `#SOURCE_BYTES` bytes, e o sha256 do cabeçalho é conferido pelo updater. Se o texto for outro (por exemplo, o texto operacional de 429.832 bytes do `updater/saida`), o mapa **não** é usado.

### Fallback: parser de runtime + conversão canônica

`ContextoJuridicoAtivo` → `CF88:ART.<artigo>[:PAR.<n>|:PAR.UNICO][:INC.<romano>][:AL.<letra>]` (implementado em `Device.from_context`).
Em seguida, o target_id é validado em `CF88_TARGETS.IDX`.

**Medição no PC.** O porte fiel do parser (`tools/context_parser_port.py`), rodado sobre o `cf.txt` estrutural, concorda com o `TEXT_MAP` em **3.986 de 4.074 linhas (97,84%)**. As 88 divergências ficam **todas fora dos arts. 1–24**:

| Categoria | Linhas | Exemplo |
|---|---|---|
| Inciso sem separador | 49 | `I portadores de deficiência` |
| Sufixo de letra não lido | 20 | `§ 4º-A`, `I-A`, `VIII-A` |
| Ordinal com ponto | 10 | `§ 2.º` gera `PAR.2.Â` |
| ADCT | 8 | `Art. 1` do ADCT lido como `CF88` sem o offset de namespace |
| Outros | 1 | — |

Essas falhas são do parser legado e não foram corrigidas: o firmware não foi tocado. Elas justificam usar o `TEXT_MAP` como fonte primária.

## Por que não um parser jurídico pesado no ESP32

O índice aprovado já resolve casos que o parser simples erra: sufixos, ordinais com ponto, redações históricas repetidas e ADCT. Consultar um offset é O(log n) e não exige regras jurídicas novas em runtime.

## Pendências (antes do firmware)

- Confirmar **qual arquivo de CF está no cartão físico** (nome, tamanho e sha256). Sem isso, não se sabe se o `TEXT_MAP` vale para ele.
- Decidir a fonte da Lei Seca da CF no pacote novo:
  - o `cf.txt` estrutural, com ADCT e redações históricas;
  - ou o texto operacional, só vigente.

  Se for o texto operacional, gerar um `TEXT_MAP` para ele. Isso exige reindexar os `line_start` sobre esse texto, uma decisão do Reference Engine que não é tomada nesta fase.
