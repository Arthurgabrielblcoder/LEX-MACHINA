# Firmware

Esta pasta receberá a versão estável do código Arduino do cyberdeck LEX MACHINA,
baseado no ESP32-S3. Ainda não há firmware disponível neste repositório.

Ao disponibilizar a versão estável, registrar:

- Modelo exato da placa e configuração selecionada na Arduino IDE.
- Versões do core Arduino para ESP32 e das bibliotecas utilizadas.
- Pinagem, sincronizada com [HARDWARE.md](../docs/HARDWARE.md).
- Instruções de compilação, gravação e validação no dispositivo.

O sketch principal deve ficar em uma subpasta de mesmo nome que o arquivo `.ino`
(por exemplo, `firmware/lex_machina/lex_machina.ino`). Esse caminho é uma sugestão
para inclusão futura, não um arquivo já existente.

Arquivos de firmware existentes devem ser preservados. Esta organização não
exige mover, substituir ou remover versões anteriores.
