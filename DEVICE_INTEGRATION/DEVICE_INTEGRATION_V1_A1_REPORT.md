# DEVICE INTEGRATION V1-A1 — relatório para revisão humana

HEAD `2e2211c0` (tag `entenda-cf-batch03-approved-2026-09-29`) · pacote **SD_OVERLAY_CANDIDATE** · build `74a4e732eecde950` (2026-09-29T14:27:22Z, derivado do commit)

## Tamanho do pacote (overlay `/99_LEX_V1`)

| COMPONENT | FILE COUNT | BYTES | % |
|---|---|---|---|
| Lei Seca (nao incluida no overlay) | 0 | 0 | 0.0 |
| Indices estruturais | 2 | 321,088 | 45.43 |
| References | 2 | 72,125 | 10.21 |
| ENTENDA | 2 | 309,714 | 43.83 |
| Metadata | 2 | 3,771 | 0.53 |
| **TOTAL** | 8 | **706,698** | 100 |

Referência legada (fora do pacote): `cf.txt` estrutural 928.009 B; CF operacional 429.832 B; `updater/saida` 64.985.501 B em 935 arquivos; Relations V2 28.586 B; J4.6 263.895 B.

## Simulador (consultas da missão)

| consulta | target | status | ENTENDA | resolução | âncora | offset/len | refs | seeks |
|---|---|---|---|---|---|---|---|---|
| CF88.5 | `CF88:ART.5` | OK | sim | DIRECT | `CF88:ART.5` | 148885/2755 | 0 | 23 |
| CF88.5.V | `CF88:ART.5:INC.V` | OK | sim | COVERED_BY_BLOCK | `CF88:ART.5:INC.IV` | 156266/2570 | 1 | 24 |
| CF88.7.XII | `CF88:ART.7:INC.XII` | OK | sim | DIRECT | `CF88:ART.7:INC.XII` | 251917/1446 | 0 | 24 |
| CF88.8.I | `CF88:ART.8:INC.I` | OK | sim | DIRECT | `CF88:ART.8:INC.I` | 270021/1653 | 0 | 23 |
| CF88.12.5 | `CF88:ART.12:PAR.5` | OK | sim | COVERED_BY_BLOCK | `CF88:ART.12:PAR.4` | 13556/1876 | 0 | 24 |
| CF88.20.XI | `CF88:ART.20:INC.XI` | OK | sim | DIRECT | `CF88:ART.20:INC.XI` | 69378/1669 | 0 | 23 |
| CF88.21.XXIV | `CF88:ART.21:INC.XXIV` | OK | sim | DIRECT | `CF88:ART.21:INC.XXIV` | 93378/1368 | 0 | 23 |
| CF88.22.XXIX | `CF88:ART.22:INC.XXIX` | OK | sim | DIRECT | `CF88:ART.22:INC.XXIX` | 117025/1365 | 0 | 24 |
| CF88.24.4 | `CF88:ART.24:PAR.4` | OK | sim | COVERED_BY_BLOCK | `CF88:ART.24:PAR.3` | 142849/2183 | 0 | 23 |
| CF88.25 | `CF88:ART.25` | OK | não | NONE | `—` | —/— | 1 | 23 |
| CF88.999 | `CF88:ART.999` | INVALID_OR_UNKNOWN_TARGET | não | NONE | `—` | —/— | 0 | 10 |
| CF88.5.XCIX | `CF88:ART.5:INC.XCIX` | INVALID_OR_UNKNOWN_TARGET | não | NONE | `—` | —/— | 0 | 10 |
| CF88.37.6 | `CF88:ART.37:PAR.6` | OK | não | NONE | `—` | —/— | 5 | 30 |
| ADCT.10.II | `ADCT:ART.10:INC.II` | OK | não | NONE | `—` | —/— | 0 | 31 |

## Benchmark host-side (complexidade, não tempo do ESP32)

```json
{
 "targets": {
  "queries": 19770,
  "mean_us": 37.5,
  "max_seeks": 10,
  "mean_seeks": 10.0
 },
 "entenda_lookup": {
  "queries": 19770,
  "mean_us": 26.76,
  "max_seeks": 8,
  "mean_seeks": 7.48
 },
 "entenda_lookup+payload": {
  "queries": 19770,
  "mean_us": 27.31,
  "max_seeks": 9,
  "mean_seeks": 7.55
 },
 "references_lookup+payload": {
  "queries": 19770,
  "mean_us": 18.51,
  "max_seeks": 6,
  "mean_seeks": 5.06
 },
 "block_resolution": {
  "queries": 600,
  "mean_us": 29.14
 },
 "log2_bound": {
  "targets": 11,
  "entenda": 8,
  "references": 6
 }
}
```

## Parser de runtime × TEXT_MAP

Concordância 3986/4074 (97.84%); categorias: {'ADCT': 8, 'INCISO_SEM_SEPARADOR (ex.: "I portadores")': 49, 'ORDINAL_COM_PONTO (ex.: § 2.º)': 10, 'OUTROS': 1, 'SUFIXO_LETRA_NAO_LIDO (ex.: § 4º-A, I-A)': 20}. Nenhuma divergência nos arts. 1–24.

## Documentos

- `REPOSITORY_DEVICE_MAP.md` (mapa e candidatos de firmware)
- `DEVICE_DATA_CONTRACT_V1.md`
- `TARGET_RESOLUTION_STRATEGY.md`
- `ESP32_RESOURCE_BUDGET.md`
- `UI_LAYER_CONTRACT_V1.md`
- `ROLLBACK_PLAN.md`
- `LEGACY_SD_BACKUP_REPORT.md`

## Excluídas do pacote

9 explicações do piloto aprovadas fora do escopo arts. 1–24: `CF88:ART.37`, `CF88:ART.37:PAR.6`, `CF88:ART.37:PAR.10`, `CF88:ART.60`, `CF88:ART.60:PAR.4`, `CF88:ART.60:PAR.4:INC.IV`, `CF88:ART.150`, `CF88:ART.225`, `ADCT:ART.10:INC.II` (decisão humana pendente).

## Físico

- Cartão: SD_NOT_UNIQUELY_IDENTIFIED → BACKUP_NOT_AVAILABLE (nenhum volume removível).
- Flash: PHYSICAL_FLASH_BACKUP_NOT_PERFORMED (ESP32 não conectado; esptool ausente).
- Nenhuma escrita em hardware; nada commitado.
