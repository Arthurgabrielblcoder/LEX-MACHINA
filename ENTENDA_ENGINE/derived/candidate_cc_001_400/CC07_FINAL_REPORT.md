# CC-07 — relatório final

## Resumo executivo

A missão produziu 149 explicações para os artigos vigentes 251–400, corrigiu de modo versionado os arts. 157 e 202 e reuniu 399 explicações ativas em um corpus candidato isolado. O art. 374, revogado, permaneceu sem explicação ativa. Não houve deploy, alteração de firmware, acesso ao dispositivo físico nem modificação dos índices de produção.

## Resultado

- Baseline: `cc06-entenda-cc-115-250` em `06a6c29b0a4285e24aab80993cec25385256502b`.
- Branch: `cc07-entenda-cc-251-400`.
- Art. 157: glossário corrigido na versão editorial 2, sem sugerir intenção de exploração.
- Art. 202: versão editorial 2 cobre as seis causas, distingue o despacho da citação efetiva e registra as condições do art. 240 do CPC.
- Intervalo examinado: 150 numerações; 149 vigentes; art. 374 histórico.
- Classificação delegada: A=149, B=2, C=0, D=0; nenhuma aprovação humana alegada.
- Corpus: 562 versões; 399 explicações ativas; SHA-256 `922ac3466e0675578dfa8a86f741d320ea1d08c3f45ea737917f1ad9235f10ab`.
- Índice candidato: SHA-256 lookup `078c8139b56344ac8a66f77ea3bde60a763733151892395b0e3004c8d339bdf4`; payload `3182b47328cc441103d8699215ca2a8d12220ecf64dbf6a4d4b4df04af6b5551`.
- Deploy: não realizado.

## Verificação

O contrato ENTENDA, a cobertura, os cinco checkpoints, os glossários, UTF-8, unicidade, preservação histórica, revogação, determinismo e imutabilidade do índice de produção são verificados pela suíte `test_entenda_cc07.py` e pelos checks dos scripts CC-07. A regressão dirigida CC-02–CC-07 passou em 44/44 testes. A suíte ENTENDA global executou 221 testes; sete falhas e dois erros ficaram restritos a hashes, perfis e fontes congeladas dos antigos Batch06/Macro07/Macro08, que já divergem do estado atual e não foram alterados pela CC-07. Os testes estruturais não constituem garantia autônoma de correção jurídica.

## Próximo intervalo recomendado

Arts. 401–550 do Código Civil, em missão separada (CC-08), após eventual revisão humana do candidato CC-07.
