# Camada explicativa de jurisprudência do Código Civil

`HUMAN_APPROVED = 653` · `GROUP_F = 28 HOLD` (fora desta camada) · host-only.

## Arquitetura

- `O QUE DECIDIU`: um registro imutável por `precedent_id` (574 no total).
- `POR QUE ESTÁ AQUI`: um registro por `relation_id` e `target_id` (653 no total).
- `AUTORIDADE`: preservada separadamente; qualidade editorial não altera força jurídica.
- Projeção física: coluna opcional `FICHA_RELACAO` (coluna 11) aponta para uma ficha composta. Índices antigos, sem a coluna, continuam abrindo a ficha compartilhada derivada de `IDENTIFICADOR`.

O modelo anterior era `ONE_FICHA_PER_PRECEDENT = YES`, mas inseria targets dentro da ficha compartilhada. Foram encontrados 67 precedentes usados em mais de um target (máximo 5); portanto havia risco real de vazamento. O V2 mantém a fonte editorial normalizada e materializa por relação apenas na borda do dispositivo.

`BACKWARD_COMPATIBLE = YES` · `FIRMWARE_FLASHED = NO` · `SD_CHANGED = NO`.
