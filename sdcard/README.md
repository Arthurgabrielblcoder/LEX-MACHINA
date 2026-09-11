# Organização do cartão microSD

O cartão pode conter pastas, subpastas e arquivos TXT. Uma organização sugerida
para os textos jurídicos é:

```text
/
├── legislacao/
│   ├── constitucional/
│   │   └── constituicao.txt
│   └── civil/
│       └── codigo_civil.txt
└── notas/
    └── leitura.txt
```

Os nomes acima são exemplos; esses arquivos não acompanham o repositório.
É possível agrupar os textos por assunto e criar subpastas conforme necessário.
Esta pasta `sdcard/` documenta a organização e não é uma imagem do cartão.

Ainda não há firmware no repositório para confirmar a navegação por essa
estrutura. O sistema de arquivos aceito, a capacidade suportada, os limites de
caminhos e a codificação dos TXT precisam ser definidos e testados na versão
estável. O suporte a acentos também deverá ser validado com a fonte da tela.

Usar arquivos de texto simples com extensão `.txt`. A estrutura do cartão,
por si só, não garante que o firmware consiga ler outros formatos de documento.
