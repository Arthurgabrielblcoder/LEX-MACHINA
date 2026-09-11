# Hardware e pinagem

## Estado da documentação

Componentes informados para o projeto: ESP32-S3, TFT ILI9341, cartão microSD e
touch. O repositório ainda não contém firmware, esquema elétrico ou tabela de
conexões que permita verificar a pinagem atual. Nenhum GPIO foi presumido.

As tabelas abaixo são um registro pendente de confirmação, não instruções de
ligação. Preencher a partir do firmware original e conferir com a montagem.

## ESP32-S3

| Item | Configuração atual |
| --- | --- |
| Modelo da placa/módulo | A confirmar |
| Tamanho da flash e presença de PSRAM | A confirmar |
| Alimentação e reguladores da montagem | A confirmar |
| Configuração USB e método de gravação | A confirmar |

## TFT ILI9341

A interface utilizada pelo módulo precisa ser confirmada. A lista abaixo serve
para registrar os sinais caso a montagem utilize SPI; os rótulos podem variar
conforme o módulo.

| Sinal | GPIO/conexão atual |
| --- | --- |
| SCK / CLK | A confirmar |
| MOSI / SDI | A confirmar |
| MISO / SDO, se utilizado | A confirmar |
| CS | A confirmar |
| DC / RS | A confirmar |
| RST | A confirmar |
| LED / BL (iluminação) | A confirmar |
| VCC e GND | A confirmar na montagem |

## Cartão microSD

O modo de conexão (SPI ou SDMMC) não está documentado. Registrar apenas os sinais
correspondentes à interface efetivamente utilizada.

| Sinal | GPIO/conexão atual |
| --- | --- |
| CLK / SCK | A confirmar |
| CMD (SDMMC) / MOSI (SPI) | A confirmar |
| D0 (SDMMC) / MISO (SPI) | A confirmar |
| CS (SPI) | A confirmar |
| D1, D2 e D3 (SDMMC, conforme modo) | A confirmar |
| Alimentação e GND do módulo/slot | A confirmar na montagem |

## Touch

O controlador e o tipo de interface do touch não foram informados. Não se presume
que seja um XPT2046 nem que compartilhe o barramento da tela.

| Item | GPIO/configuração atual |
| --- | --- |
| Modelo do controlador | A confirmar |
| Interface de comunicação | A confirmar |
| Sinais de comunicação e respectivos GPIOs | A confirmar após identificar o controlador |
| CS, IRQ e RESET, quando aplicáveis | A confirmar |
| Alimentação e GND | A confirmar na montagem |
| Orientação e calibração | A confirmar |

## Pendências de integração

- Conferir quais barramentos são compartilhados e quais sinais de seleção são usados.
- Registrar os GPIOs efetivos e possíveis conflitos com recursos da placa.
- Confirmar alimentação e níveis elétricos nas especificações dos módulos exatos.
- Anexar esquema ou fotos identificadas da montagem para tornar a pinagem verificável.
