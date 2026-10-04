FASE A — AÇÃO DE ARTHUR

1. desligar totalmente o LEX MACHINA;
2. retirar o microSD;
3. colocar o microSD no leitor do PC;
4. informar a letra da unidade;
5. só então iniciar manifesto/cópia.

**ESTE PLANO NÃO FOI EXECUTADO.** Não retirar o cartão, copiar arquivos ou flashar firmware nesta missão.

## FASE B — manifesto e backup físico prévios

1. Montar o volume somente após Arthur informar a letra; validar que é o microSD esperado pelo label, capacidade e estrutura.
2. Gerar manifesto completo prévio com path relativo, bytes e SHA-256, sem escrever no volume.
3. Comparar o manifesto com a baseline física aprovada `10e199f` / tag
   `lex-device-v1-batch04-run3-physical-approved-2026-10-03`; interromper diante de divergência não explicada.
4. Fazer backup recuperável integral do cartão para novo diretório timestamped fora do SD e gerar manifesto do backup.
5. Confirmar por comparação byte a byte que backup e manifesto físico prévio coincidem.

## FASE C — revisão do candidato

1. Revisar `staging_article_indexes_full_corpus_candidate/_host/ARTICLE_INDEX_MANIFEST.json` e este relatório.
2. Manter MARIA2006 bloqueada; não copiar índice inexistente nem substituir seu TXT nesta implantação.
3. Confirmar payload esperado: 71 `*_ARTICLE_SEARCH.IDX` + `ARTICLE_SEARCH_CATALOG.IDX`, 72 arquivos, 166.760 B.
4. Confirmar que CF88 e CC2002 são byte-identical à baseline; classificá-los como KEEP e não regravá-los desnecessariamente.
5. Produzir diff exato `ADD/REPLACE/UNCHANGED/REMOVE`. Nesta fase, não remover arquivos do SD sem plano específico aprovado.

## FASE D — cópia mínima e readback

1. Copiar somente os 69 índices ADD e o catálogo para `/99_LEX_V1/10_TARGETS/`, preservando CF88/CC2002.
2. Para cada arquivo: copiar para nome temporário no mesmo diretório, `fsync`, readback completo, validar bytes+SHA-256 e só então
   substituir atomicamente o destino. Em erro, parar e preservar o backup.
3. Gerar manifesto pós-cópia de todo o SD e diff contra o manifesto prévio; aceitar somente os paths previstos.
4. Reabrir e hashear os 70 arquivos efetivamente novos após a substituição; validar também os dois KEEP.
5. Ejetar o volume pelo mecanismo seguro do sistema operacional e aguardar confirmação antes de remover o leitor.

## FASE E — ação de Arthur e teste do SD

1. Arthur remove o microSD do leitor, recoloca no LEX MACHINA e liga o aparelho.
2. Com o firmware físico ainda inalterado, validar boot, montagem e fallback legacy; não esperar uso do catálogo antes do firmware novo.
3. Registrar serial e resultados; diante de erro, desligar e restaurar o backup completo.

## FASE F — firmware, somente após validação do SD e nova autorização

1. Revalidar a imagem flag1 final: 1.098.336 B,
   SHA-256 `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc`.
2. Fazer readback das partições físicas e comparar app0 com a baseline aprovada antes de qualquer escrita.
3. Executar flash **app-only** em `0x10000`; não escrever bootloader, partition table, NVS ou outras partições.
4. Fazer readback do app0 pelo tamanho exato, validar checksum/hash de imagem e SHA-256 contra o candidato.
5. Testar boot, CF88, CC2002, uma norma além das oito primeiras, troca de normas, artigo >999, suffix, próxima ocorrência,
   catálogo ausente/corrompido/mismatch e fallback linear. Confirmar pico de um FD e um índice em PSRAM.
6. Se qualquer gate falhar, restaurar app0 e/ou SD a partir dos readbacks/backups e repetir os hashes.

