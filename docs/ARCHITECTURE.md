# Arquitetura do software

## Estado atual

Não há código-fonte de firmware neste repositório. Esta documentação descreve
uma proposta inicial para um projeto Arduino no ESP32-S3; os módulos e fluxos
abaixo ainda precisam ser implementados ou conferidos com o firmware original.

## Responsabilidades propostas

| Parte | Responsabilidade |
| --- | --- |
| Sketch principal | Inicializar o dispositivo em `setup()` e coordenar eventos em `loop()` |
| Configuração de hardware | Centralizar pinagem, parâmetros da tela e configuração dos barramentos |
| Armazenamento | Acessar o microSD, listar diretórios e abrir/ler/fechar arquivos TXT |
| Navegação | Manter o diretório atual, a seleção e o retorno à pasta anterior |
| Leitor de texto | Ler trechos de arquivo e controlar a posição da leitura |
| Interface gráfica | Desenhar listas, texto e mensagens na TFT ILI9341 |
| Entrada touch | Converter a entrada do controlador em ações de navegação após calibração |

Essas responsabilidades podem começar no mesmo sketch e ser separadas em
arquivos conforme a complexidade crescer. Nenhuma biblioteca específica foi
escolhida ou verificada neste repositório.

## Fluxo proposto

1. Inicializar os barramentos, a tela, o touch e o cartão microSD.
2. Exibir o conteúdo do diretório inicial ou uma mensagem de falha de acesso.
3. Interpretar ações do usuário para entrar em pastas ou retornar à pasta anterior.
4. Ao selecionar um TXT, ler e exibir seu conteúdo em trechos.
5. Permitir voltar à listagem, fechando o arquivo quando a leitura terminar.

## Critérios para implementação

- Evitar carregar arquivos inteiros na RAM; definir buffers conforme a placa real.
- Manter acesso a arquivos separado da apresentação para facilitar manutenção.
- Tratar cartão ausente, falha de abertura, diretório vazio e arquivo vazio.
- Definir e documentar codificação de texto, quebras de linha e suporte a acentos.
- Validar caminhos com pastas e subpastas e definir limites de navegação.
- Conferir a coordenação dos periféricos caso compartilhem um barramento.

A organização dos conteúdos está em [sdcard/README.md](../sdcard/README.md).
A configuração elétrica depende das confirmações de [HARDWARE.md](HARDWARE.md).
