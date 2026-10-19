# CC MASS — requisitos de apresentação para acórdãos de Turma

`TURMA_DISPLAY_GATE = PENDING`

Nenhuma alteração de firmware é feita nesta etapa. Uma relação de Turma ratificada não pode ser materializada enquanto este gate estiver pendente.

## Lista compacta

- Exibir tribunal, classe e número: `STJ · REsp 2.145.365`.
- Quando couber no TFT, acrescentar órgão abreviado: `STJ · REsp 2.145.365 · 3ª T.`.
- Nunca rotular acórdão de Turma como repetitivo, IAC, súmula ou precedente vinculante.
- Preservar truncamento previsível sem esconder classe ou número.

## Ficha

- Tribunal, órgão julgador, classe, processo, data e fonte oficial.
- Natureza: `jurisprudência persuasiva, não vinculante`.
- Nota editorial e eventual substituição do representante.
- Corroboração, quando existente, sem afirmar consolidação ou pacificação.

## Compatibilidade retroativa

- Súmulas, repetitivos, IAC, RG e controle concentrado já existentes não podem mudar de identidade ou navegação.
- Registros legados `ACORDAO n` devem continuar legíveis durante a migração.
- O novo metadado não pode alterar as chaves congeladas CF 315/198 e CC 49/39.

## Testes futuros no hardware

1. REsp da 3ª Turma e AREsp da 4ª Turma, com números longos.
2. Acórdão corroborado e acórdão isolado.
3. Representante substituto, confirmando que o número antigo não aparece.
4. Navegação lista → ficha → voltar.
5. Regressão de súmula, repetitivo, IAC, RG e ADI legados.

`FIRMWARE_CHANGED = NO`
