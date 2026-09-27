# Política protected545

**Lista canônica:** `LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json` → `files` (545 entradas com `path`, `bytes` e `sha256`). A lista foi reverificada como `protected545` em `00_CHECKPOINTS/INTEGRITY_R1D1_FINAL.json`.

**Escopo declarado da prova:**

- todas as árvores de Referências preexistentes;
- `CF_SEGMENTADA_V2`;
- `firmware`;
- todos os IDX locais;
- `sdcard`.

**Regra obrigatória:** estes 545 arquivos devem permanecer **byte a byte idênticos e exatamente nos paths atuais**. A prova de integridade da V2 compara o path relativo e o SHA-256; mover, renomear, deduplicar, arquivar ou editar qualquer um deles torna a prova inverificável.

Proibido em qualquer onda de limpeza, sem nova autorização explícita:

- mover;
- renomear;
- deduplicar, inclusive substituir por link;
- arquivar ou compactar a pasta que os contém;
- editar.

**Consequência para a ONDA 4.** Pastas legadas que contenham arquivos do `protected545` não podem ser arquivadas inteiras. É o caso de várias `LEX_MACHINA_REFERENCIAS_*_V1…` e de `CF_SEGMENTADA_V2`. Os demais arquivos dessas pastas só podem sair se esses 545 ficarem no lugar.

**Proteção atual (ONDA 0):**

- os 545 foram verificados contra os hashes registrados;
- os não versionados estão no snapshot `C:\GitHub_LEX_MACHINA_SAFETY_PRE_CLEANUP_2026-09-26\` (zip e `SAFETY_MANIFEST.json`);
- os versionados (firmware e sdcard) estão no Git e no bundle.
