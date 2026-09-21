# Relatório J4.5 — capacidade jurisprudencial dinâmica

Data: 21/09/2026.

## Causa exata

A v7.11.x declarava `MAX_JUR_LOOKUP_CF 64`. A mesma constante era usada para reservar o array de `LookupJurisCFCache`, encerrar o laço de carga e calcular os bytes do cache. Ao chegar à entrada 64, o loader parava, detectava conteúdo restante e recusava o cache como truncado. O limite não vinha do formato dos índices nem da PSRAM; era artificial e estava codificado no firmware.

## Solução

O loader da v7.12.0 faz duas passagens no boot:

1. conta todas as linhas de dados de `JUR_LOOKUP.IDX`;
2. valida zero e o limite defensivo de 4.096 entradas;
3. aloca exatamente `N × sizeof(LookupJurisCFCache)` em PSRAM;
4. carrega as N entradas sem corte silencioso;
5. carrega `JURISPRUDENCIA.IDX` integralmente em PSRAM;
6. valida schema, inteiros, offsets, alinhamento de linha, quantidade individual e soma total;
7. em qualquer falha, libera as alocações e preserva o fallback SD sem crash.

Durante o caminho normal, lookup e registros são lidos exclusivamente do cache. Não há varredura de SD durante a rolagem.

O teto de 4.096 é somente uma barreira contra arquivo corrompido e não causa pré-alocação. A capacidade operacional é dinâmica.

## Capacidade e memória

- máximo testado nesta etapa: **256 chaves simuladas**;
- corpus real J4 testado: **178 chaves e 296 registros**;
- `LookupJurisCFCache`: **60 bytes** no ESP32-S3;
- PSRAM prevista com J4: `178 × 60 + 54.207 + 1` = **64.888 bytes**;
- redução esperada da PSRAM livre após o cache J4: **64.888 bytes**;
- PSRAM livre absoluta: **não mensurável por compilação** e deliberadamente não inventada, pois depende da placa e dos caches já ativos. O firmware registra `PSRAM_livre_antes` e `PSRAM_livre_depois` no Serial para a futura validação física.

## Compilação

- placa: **ESP32S3 Dev Module**;
- PSRAM: **OPI PSRAM** (`PSRAM=opi`);
- flash: **989.379 bytes / 1.310.720 bytes (75%)**;
- RAM global: **124.452 bytes / 327.680 bytes (37%)**;
- RAM interna restante indicada pelo linker: **203.228 bytes**;
- resultado: **aprovado**.

Advertência não bloqueante: a biblioteca EspBle declarou suporte pré-compilado, mas não havia binário `esp32s3`; o toolchain compilou a biblioteca normalmente. Nenhum warning funcional do novo loader foi emitido.

## Testes

- J4.5/capacidade e contexto: **13/13**;
- J4/corpus e determinismo: **6/6**;
- regressão J2.5: **42/42**;
- regressão J3: **15/15**;
- total: **76/76**.

Casos de capacidade: 0 rejeitado com segurança; 1, 64, 65, 178 e 256 carregados integralmente. Também foram testados offsets inválidos, quantidade zero/excessiva, total inconsistente, preservação de assets/contexto, hashes dos índices J4, Relations V2, BACK e lookup granular.

## Preservação

`contexto_juridico.h`, `assets/lex_boot_screen.h` e o preview permanecem byte a byte iguais à v7.11.1. Os índices J4 permanecem com os SHA-256:

- `JUR_LOOKUP.IDX`: `7931e28e7a0592e2bd1a1872ee0904149eac50365c1c98990370a1235c618956`;
- `JURISPRUDENCIA.IDX`: `f85108baf4ee296a7672e11733d63a32be60882d60364063a5a466e7a982b6f1`.

Nenhum índice foi copiado para SD e nenhum upload foi feito no ESP32.

## Recomendação

**Recomenda-se avançar para uma integração física controlada da J4**, em etapa explicitamente autorizada, para medir a PSRAM livre real e validar no aparelho as 178 chaves. Esta J4.5, por si só, não executa essa integração.
