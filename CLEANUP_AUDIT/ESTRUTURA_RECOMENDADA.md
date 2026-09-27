# Estrutura recomendada (proposta — NÃO implementada)

**Princípio:** preservar a lógica funcional do LEX MACHINA, que tem três pipelines reais:

1. **firmware**: ESP32/Arduino;
2. **updater**: coleta de fontes oficiais → build de LEXDATA/IDX → implantação no SD;
3. **referências**: engine de vínculos Constituição↔obra e catálogo cultural (V2).

A desordem atual não está nesses pipelines, e sim na **raiz poluída por ~70 pastas-snapshot** de etapas e versões anteriores. A proposta mexe o mínimo possível nos caminhos ativos.

## Proposta

```text
LEX-MACHINA/
├── README.md · HISTORICO_RELEASES.md · docs/            (sem mudança)
├── firmware/
│   ├── LEX_MACHINA.ino/                                 (sem mudança: sketch ativo)
│   └── releases/  v7.10.1_FAST, v7.11.0, v7.11.1, v7.12.0 (versões anteriores agrupadas)
├── updater/                                             (sem mudança de caminhos; scripts têm paths relativos)
│   └── saida/ · cache_* · backup_sd/                    (mantidos; ver política de versionamento)
├── referencias/
│   ├── V2/          ← LEX_MACHINA_REFERENCIAS_V2 (congelado; mover só com atualização dos manifests)
│   └── catalogo_69/ ← LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1
├── sdcard/                                              (sem mudança)
└── _ARCHIVE_PRE_CLEANUP_2026-09/                        (fora da árvore ativa ou em repositório/armazenamento separado)
    ├── updater_etapas/        LEX-MACHINAETAPA_2B…2E6, updater_stage2a_corrigida_v2, LEX_MACHINA_UPDATER_*
    ├── referencias_v1/        LEX_MACHINA_REFERENCIAS_*_V1…V1_4_ALPHA3, CF_SEGMENTADA_V2
    ├── juris_cf/              LEX_MACHINA_JURIS_CF_J1…J4_6
    └── firmware_backups/      LEX_MACHINA_BACKUP_POS_CODEX_16-09
```

## Mudanças realmente úteis, em ordem de valor

1. **Tirar da raiz as ~70 pastas de etapa e versão.** É a maior melhoria de legibilidade, reduz 2,9 GB da árvore ativa e não afeta nenhum pipeline ativo.
2. **Versionar a V2 e o catálogo 69.** Isso é mais segurança do que estrutura, mas é pré-requisito de tudo.
3. **Agrupar as versões de firmware** em `firmware/releases/`.
4. **Consolidar referências** em `referencias/`.

   **Atenção:** `REFERENCIA_CATALOGO_69.json` e vários scripts da V2 usam **caminhos absolutos** (por exemplo `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1\...`). Mover exige atualizar esses caminhos e regenerar os manifests, o que quebra a verificação histórica por hash de caminho. **Recomendação:** não mover a V2 nem o ADAPTADOR; se mover, fazê-lo numa release nova, nunca sobre os congelados.

## O que NÃO recomendar

- Estrutura genérica `/src /data /tools` para o projeto inteiro: os pipelines já têm organização própria e caminhos relativos internos.
- Renomear pastas congeladas da V2 (RC1, RC2, ENRIQUECIDO_V1): os manifests e as provas dependem dos caminhos atuais.
- Deduplicar arquivo a arquivo **dentro** de snapshots de etapa: cada snapshot deixaria de ser autocontido. É melhor arquivar a pasta inteira, se possível comprimida (a compressão elimina a redundância sem apagar nada).
