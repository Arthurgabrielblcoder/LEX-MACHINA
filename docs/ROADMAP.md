# Roadmap

As etapas abaixo são propostas de desenvolvimento. Não representam recursos
já implementados nem um cronograma de entrega.

## 1. Registrar a base do projeto

- [ ] Disponibilizar uma versão estável do firmware em `firmware/`, preservando os originais.
- [ ] Identificar a placa ESP32-S3 e os módulos de tela, microSD e touch.
- [ ] Confirmar a pinagem da montagem em `HARDWARE.md`.
- [ ] Documentar versões do core ESP32, bibliotecas e opções de compilação/gravação.

## 2. Validar os periféricos

- [ ] Validar inicialização, orientação e desenho na TFT ILI9341.
- [ ] Validar montagem e leitura do cartão microSD.
- [ ] Identificar, testar e calibrar o touch.
- [ ] Verificar funcionamento conjunto dos periféricos e possíveis conflitos de barramento.

## 3. Validar a consulta offline

- [ ] Implementar ou conferir listagem de pastas e arquivos TXT no firmware disponível.
- [ ] Permitir navegar por subpastas e retornar ao diretório anterior.
- [ ] Exibir textos em trechos, com controle da posição de leitura.
- [ ] Definir suporte a codificação, acentos e quebras de linha.
- [ ] Tratar cartão ausente, arquivos ilegíveis e diretórios vazios.

## 4. Consolidar a versão estável

- [ ] Testar documentos pequenos e grandes e hierarquias com vários níveis.
- [ ] Medir uso de memória e tempo de resposta no hardware real.
- [ ] Documentar limites conhecidos e um roteiro de validação manual.
- [ ] Atualizar o README com os recursos efetivamente demonstrados.

Melhorias adicionais devem ser priorizadas após a validação da base, com seus
requisitos registrados antes de serem anunciadas como funcionalidades.
