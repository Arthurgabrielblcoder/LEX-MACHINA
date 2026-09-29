# DEVICE_INTEGRATION

Preparação da integração física da nova arquitetura (target_id canônico, Reference Engine e ENTENDA aprovado) com o ESP32-S3 e o microSD.

- **V1-A1 (2026-09-29):** só trabalho no PC. Nada foi escrito em cartão ou firmware.
- **V1-A2 (2026-09-29):**
  - dump da flash verificado e firmware físico confirmado (v7.12.0);
  - pacote com 163 explicações ENTENDA;
  - firmware candidato em `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/`;
  - CF88_RUNTIME bloqueado (`CANONICAL_ADCT_SOURCE_NOT_RESOLVED`);
  - backup do cartão pendente, porque o cartão está no aparelho.
- **V1-A2B (2026-09-29):**
  - ADCT oficial ingerido (Senado 604119);
  - `CF88_RUNTIME` canônico criado, com targets e mapa reconstruídos sobre os mesmos bytes;
  - backup do cartão verificado;
  - `FULL_PHYSICAL_ROLLBACK_AVAILABLE`;
  - firmware candidato com guarda de sha256.

| Arquivo | Conteúdo |
|---|---|
| `REPOSITORY_DEVICE_MAP.md` | componentes, fonte de verdade, candidatos de firmware |
| `DEVICE_DATA_CONTRACT_V1.md` | formatos, offsets, versões, falhas seguras |
| `TARGET_RESOLUTION_STRATEGY.md` | posição na Lei Seca → target_id |
| `ESP32_RESOURCE_BUDGET.md` | RAM/PSRAM/SD estimados |
| `UI_LAYER_CONTRACT_V1.md` | flags de camada para a interface |
| `ROLLBACK_PLAN.md` / `LEGACY_SD_BACKUP_REPORT.md` | retorno ao estado legado; situação dos backups |
| `DEVICE_INTEGRATION_V1_A1_REPORT.md` / `.json` | relatório da fase |
| `tools/build_sd_staging.py` | gera `staging_sd_v1/` (determinístico; recusa saída fora desta pasta) |
| `tools/device_lookup_simulator.py` | simula as consultas do ESP32 (`--demo`, `--bench N`) |
| `tools/context_parser_port.py` | porte do parser de contexto do v7.12.0 para validar a estratégia |
| `CF88_RUNTIME_SOURCE_AUDIT.md` | auditoria das fontes da CF/ADCT (A2) |
| `RELATIONS_V2_LEGACY_64_LINE_LIMIT.md` | issue do limite de 64 linhas (A2, NON_BLOCKING) |
| `tests/` | `python -B -m unittest discover -s tests` |

`staging_sd_v1/` e `backups/` são ignorados pelo Git e reconstruíveis.
