# LEX-MACHINA
Cyberdeck jurídico portátil baseado em ESP32-S3 para consulta offline de legislação brasileira.

O projeto tem como objetivo oferecer consulta local de textos jurídicos em um
dispositivo portátil. O hardware informado inclui ESP32-S3, tela TFT ILI9341,
cartão microSD e touch.

## Estado atual

Este repositório contém a estrutura inicial e a documentação do projeto. Ainda
não há código Arduino versionado aqui; portanto, leitura de arquivos, navegação
por pastas e interação por touch não estão comprovadas como implementadas.
A pinagem também depende de confirmação com o hardware ou o firmware original.

## Organização

```text
firmware/              Versão estável do código Arduino, quando disponibilizada
  README.md
docs/
  HARDWARE.md          Componentes e pinagem a confirmar
  ARCHITECTURE.md      Arquitetura proposta do software
  ROADMAP.md           Próximas etapas do projeto
sdcard/
  README.md            Organização sugerida para o cartão microSD
```

- [Firmware](firmware/README.md)
- [Hardware e pinagem](docs/HARDWARE.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Organização do microSD](sdcard/README.md)

As propostas na documentação orientam o desenvolvimento e não representam
funcionalidades já disponíveis. As instruções de compilação e gravação serão
registradas quando o firmware estável e sua configuração estiverem disponíveis.
