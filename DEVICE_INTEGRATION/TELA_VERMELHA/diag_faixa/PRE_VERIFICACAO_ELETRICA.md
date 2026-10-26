# Pré-verificação elétrica da tela vermelha (antes do LEX_DIAG_FAIXA)

Data: 2026-10-25 · Nenhuma gravação; firmware INVON=0 e microSD inalterados.

## Regulador e J1: evidências

- LCDwiki MSP3218 (3,2" SPI, ILI9341, 320×240, 14 pinos): VCC "3.3V~5V", IO "3.3V(TTL)". **Não descreve J1 nem o regulador.**
- Protosupplies (3,2" 240×320 SPI com XPT2046): tem regulador 3,3 V on-board; VCC 3,6–5,5 V; os pads **J1**, quando
  curto-circuitados, fazem o **bypass** do regulador para alimentar direto com 3,3 V. Consumo típico de 55–60 mA. Não informa a peça do regulador.
- done.land (placa irmã de 2,8"): J1 aberto (padrão) → VCC passa pelo regulador e deve ser 5 V; J1 fechado → bypass e VCC deve ser 3,3 V.
  Com 3,3 V e J1 aberto, a tensão interna fica abaixo de 3 V, o que "pode ainda funcionar", mas com o backlight bem mais escuro.
- A peça exata do regulador e sua queda (dropout) **não** estão documentadas para este módulo. A placa física precisa ser conferida.

## Avaliação

- Com 3,3 V no VCC e J1 aberto, o controlador recebe a entrada menos a queda do regulador, provavelmente algo entre 2,9 e 3,2 V,
  conforme a peça e a carga. A faixa de alimentação do ILI9341 (VCI 2,5–3,3 V; IOVCC 1,65–3,3 V) cobre esse valor, logo o mais provável é que
  seja **funcional**, mas sem margem caso o fio ou a solda também derrubem tensão (já houve uma solda ruim no VCC).
- Subtensão costuma produzir efeitos **globais**: backlight fraco, contraste/gama alterados, cintilação, falha de partida, imagem que apaga.
  Uma faixa **fixa** de ~80 px com o restante perfeito é assinatura de endereçamento/geometria ou de defeito localizado (vidro/FPC/linha de gate).
  Conclusão: a alimentação é causa **improvável** da faixa, mas precisa ficar dentro da especificação antes do diagnóstico, para não confundir os resultados.

## Medições seguras (multímetro em DC; USB ligado; não encostar a ponta em dois pinos ao mesmo tempo)

| # | Onde medir | Esperado | Leitura ruim |
|---|---|---|---|
| M1 | VCC → GND **nos pinos do módulo**, com a tela acesa | 5 V no pino → 4,7–5,1 V; 3V3 no pino → ≥ 3,20 V | < 3,15 V (com 3V3) |
| M2 | Pino de origem no ESP32 (3V3 ou 5V) → GND do ESP32 | Igual a M1 ± 0,05 V | Diferença > 0,1 V = fio/solda resistivos |
| M3 | GND do ESP32 → GND do módulo (multímetro em mV) | < 30 mV | > 50 mV = terra ruim |
| M4 | Cada pad de J1 → GND (um pad é VCC; o outro é a saída do regulador, o 3,3 V interno) | Saída ≈ 3,3 V (com VCC 5 V) ou ≥ 3,0 V (com VCC 3,3 V) | Saída < 2,9 V |
| M5 | LED → GND (backlight) | ≈ tensão de onde está ligado | Muito abaixo = carga/ligação ruim |

Medir M1 e M4 em dois momentos: no splash e na tela de erro do SD (estável).
Observação sem medidor: a faixa muda ao pressionar **de leve** a borda do vidro ou o cabo flexível? Se mudar, aponta para FPC/vidro.

## Regras de segurança

- **Não fechar J1 se o VCC estiver no 5 V** (VBUS): isso coloca 5 V direto no ILI9341, que só tolera 3,3 V.
- Não fechar J1 nem mudar fios agora. Qualquer mudança vem depois, uma de cada vez, com nova autorização.
- Para uma solução definitiva, considerar como o aparelho será alimentado na bateria: se não existir 5 V nesse modo, a opção é
  3V3 + J1 fechado; se existir 5 V estável, a opção é 5 V + J1 aberto.

## Critério para liberar o diagnóstico

- Rail interno (M4) ≥ 3,0 V, M2 com diferença ≤ 0,1 V e M3 < 50 mV → alimentação **descartada** como causa; pode gravar o LEX_DIAG_FAIXA.
- Fora disso → corrigir a alimentação primeiro (uma alteração só) e observar a faixa de novo com o firmware INVON=0, ainda sem o diagnóstico.

## Medições reais (informadas pelo usuário, 2026-10-25)

Configuração: VCC da tela no **3V3** do ESP32, J1 **aberto**, ESP32 alimentado pelo USB.

| # | Leitura | Critério | Resultado |
|---|---|---|---|
| M1 | VCC → GND nos pinos da tela: **3,2 V** | ≥ 3,15 V (3V3) | OK |
| M2 | 3V3 do ESP32 → GND: **3,2 V** | diferença M1/M2 ≤ 0,1 V | OK (≈ 0 V) |
| M3 | GND ESP32 ↔ GND módulo, aparelho ligado: **28–34 mV** | < 50 mV | OK |
| M4 | J1: pad 1 = **3,30 V** (entrada) · pad 2 = **3,11 V** (saída do regulador) | saída ≥ 3,0 V | OK; queda no regulador ≈ 0,19 V |

`POWER_PREFLIGHT = PASS` · `POWER_AS_PRIMARY_CAUSE = UNLIKELY`

Evidência experimental (teste curto feito pelo usuário; **não repetir**): só o VCC da tela foi passado de 3,3 V para 5 V, com J1 aberto.
A tela ficou totalmente escura, sem imagem, e o aparelho foi desligado imediatamente. Com o VCC de volta em 3,3 V, a tela voltou a
funcionar como antes, e a faixa anômala continuou igual. Decisão: manter 3,3 V, J1 aberto, sem novos testes de alimentação.

Fontes: https://www.lcdwiki.com/3.2inch_SPI_Module_ILI9341_SKU:MSP3218 ·
https://protosupplies.com/product/tft-lcd-3-2-240x320-rgb-spi-display-with-touchscreen/ ·
https://done.land/components/humaninterface/display/tft/ili9341/2.8inch320x240/
