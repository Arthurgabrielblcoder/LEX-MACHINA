# ONDA 2R — Reavaliação dos candidatos da ONDA 2

**ANTES DA MIGRAÇÃO** (`WAVE2_ARCHIVE_PLAN.json`, HEAD `53c419a`)

| | |
|---|---|
| Candidatos | 81 (76 pastas da raiz + 5 subpastas de firmware), 23.379 arquivos |
| Bytes | 2.921.061.459 (≈ 2,92 GB) |
| Bloqueios principais | protected545 (55 pastas, 2,889 GB); revisão manual (8); ajuste de receitas/paths absolutos (17); liberado só o piloto 2E4 (1, 49 KB) |

**AGORA** (HEAD `804d14f`, tag `shadow-coexistence-d05-2026-09-28`)

| Classe | Count | Bytes |
|---|---:|---:|
| READY_TO_ARCHIVE_REVERSIBLY | 18 | 7.613.511 (≈ 7,6 MB) |
| READY_TO_DELETE_CACHE_DUPLICATE | 0 | 0 |
| EXTRACT_UNIQUE_EVIDENCE_THEN_ARCHIVE | 7 | 23.697.830 (≈ 23,7 MB) |
| STILL_BLOCKED | 55 | 2.888.016.527 (≈ 2,89 GB) |
| MANUAL_REVIEW | 0 | 0 |
| KEEP_IN_ROOT_INTENTIONALLY | 1 | 1.733.591 (≈ 1,7 MB) |
| **IMMEDIATE_REVERSIBLE_CLEANUP** | **18** | **7.613.511 (≈ 7,6 MB)** |

**PERCENTUAL DO VOLUME ANTIGO LIBERADO: 0,261 %** (22,2 % dos candidatos por contagem).

Se as 7 extrações forem feitas, o total condicional sobe para 25 candidatos e 31.311.341 bytes (1,07 %).

Esta missão foi somente leitura. Nada foi movido, apagado, renomeado ou compactado. O archive root **não** foi criado.

---

## 1. Resposta direta

> Com a arquitetura atual, quantos dos candidatos antigos podem sair da pasta raiz **agora**, sem perda de operação, integridade ou prova?

**18 de 81 (22,2 %), totalizando 7,6 MB (0,26 % do volume antigo).** Todos são etapas intermediárias do updater Relations V2 (2D6…2D17 e 2E…2E4). A saída é um move reversível, verificado por hash, para fora da raiz.

**O volume grande (99,7 %) continua preso**, e não por motivo genérico: está em 55 pastas que contêm membros protected545. Dezesseis delas contêm também IDX; a maior parte é `updater_stage2a_corrigida_v2` (954 MB), mais as cópias `LEX-MACHINAETAPA_2C`/`2D`/`2D2`/`2D3` e as três `LEX_MACHINA_UPDATER_*`.

**A migração D05 não mudou esse quadro.** Nenhum dos 81 candidatos é membro do Registry ou do Lock D05.

## 2. Universo original recuperado

- **Fonte:** `CLEANUP_AUDIT/WAVE2_ARCHIVE_PLAN.json` (`schema lex-machina-wave2a/1`), com matriz por pasta, 3.457 referências, lotes e protocolo. Não foi assumido nenhum nome: tudo veio desse arquivo.
- **Universo:** ORIGINAL_CANDIDATE_COUNT = **81**; ORIGINAL_TOTAL_SIZE = **2.921.061.459**; FAMILY_COUNT = **7**.

| Família | Pastas | Resultado agora |
|---|---:|---|
| UPDATER_ETAPAS | 32 | 18 READY · 6 EXTRACT · 7 BLOCKED_P545 · 1 BLOCKED_ACTIVE (2E41) |
| REFERENCIAS_V1 | 34 | 34 BLOCKED_P545 |
| JURIS_CF_ETAPAS | 6 | 5 BLOCKED_P545 · 1 EXTRACT (J1) |
| FIRMWARE_ANTIGO | 5 | 5 BLOCKED_P545 |
| RELATIONS_VERSOES_ANTIGAS | 2 | 2 BLOCKED_P545 |
| BACKUPS_MANUAIS | 1 | 1 BLOCKED_P545 |
| OUTROS_LEGADOS | 1 | 1 KEEP (`CF_SEGMENTADA_V2`) |

**Estado físico atual.** O universo está idêntico ao original:

- 81/81 pastas presentes, com 23.379 arquivos e 2.921.061.459 bytes;
- nos 26 candidatos sem protected545, 781 arquivos foram reconferidos por SHA-256 contra o inventário, sem nenhuma divergência, ausência ou arquivo novo.

**Verificações executadas agora (somente leitura).**

| Verificação | Resultado |
|---|---|
| Registry (`verify_registry.py`) | PASS: 855 entradas; 0 conflitos, 0 ausentes, 0 órfãos |
| Lock (`verify_lock.py`) | PASS: member, order, multiplicity, absence e dependency; 0 extras |
| Resolver (`resolve_selection.py` + `verify_resolved_selection.py`) | PASS, 0 extras; seleção gerada no scratchpad byte-idêntica a `D05_SHADOW_RESOLVED_SELECTION.json` |
| protected545 | 545/545 idênticos |
| IDX | 130/130 idênticos ao inventário |

Nenhum pipeline foi executado.

## 3. TOP CANDIDATOS PARA ONDA 2E

Ordem: confiança HIGH, maior espaço, menor risco, menos arquivos. Todos são HIGH e não têm blockers.

| # | Candidato | Bytes | Arquivos | Lote proposto |
|---:|---|---:|---:|---|
| 1 | `LEX-MACHINAETAPA_2D9` | 2.102.330 | 36 | LOTE_2E_1 |
| 2 | `LEX-MACHINAETAPA_2D12` | 1.127.159 | 35 | LOTE_2E_1 |
| 3 | `LEX-MACHINAETAPA_2E31` | 743.503 | 29 | LOTE_2E_3 |
| 4 | `LEX-MACHINAETAPA_2E2` | 737.743 | 29 | LOTE_2E_3 |
| 5 | `LEX-MACHINAETAPA_2E3` | 683.641 | 25 | LOTE_2E_3 |
| 6 | `LEX-MACHINAETAPA_2D15` | 365.122 | 12 | LOTE_2E_1 |
| 7 | `LEX-MACHINAETAPA_2D16` | 352.185 | 11 | LOTE_2E_1 |
| 8 | `LEX-MACHINAETAPA_2D14` | 317.678 | 12 | LOTE_2E_1 |
| 9 | `LEX-MACHINAETAPA_2D13` | 297.192 | 12 | LOTE_2E_1 |
| 10 | `LEX-MACHINAETAPA_2D11` | 222.508 | 12 | LOTE_2E_1 |
| 11 | `LEX-MACHINAETAPA_2D10` | 191.937 | 11 | LOTE_2E_1 |
| 12 | `LEX-MACHINAETAPA_2E1` | 120.570 | 10 | LOTE_2E_3 |
| 13 | `LEX-MACHINAETAPA_2E` | 95.971 | 9 | LOTE_2E_3 |
| 14 | `LEX-MACHINAETAPA_2D17` | 56.208 | 8 | LOTE_2E_1 |
| 15 | `LEX-MACHINAETAPA_2D6` | 55.328 | 10 | LOTE_2E_2 |
| 16 | `LEX-MACHINAETAPA_2E4` | 49.357 | 5 | LOTE_2E_3 |
| 17 | `LEX-MACHINAETAPA_2D6_3` | 48.501 | 8 | LOTE_2E_2 |
| 18 | `LEX-MACHINAETAPA_2D6_2` | 46.578 | 8 | LOTE_2E_2 |

**Lotes propostos.** Cada lote é uma cadeia de receitas; mover a cadeia inteira mantém coerentes os LEIA_ME históricos entre irmãs.

| Lote | Pastas | Bytes | Arquivos |
|---|---|---:|---:|
| LOTE_2E_1 (cadeia 2D9→2D17) | 9 | 5.032.319 | 149 |
| LOTE_2E_2 (cadeia 2D6) | 3 | 150.407 | 26 |
| LOTE_2E_3 (cadeia 2E→2E4, a montante de 2E41) | 6 | 2.430.785 | 107 |
| LOTE_2E_4 (condicional, após extração) | 7 | 23.697.830 | 468 |

**Por que esses 18 são liberáveis com confiança HIGH:**

- **Sem protected545, sem IDX, sem restricted_local e sem segredo.**
- **Nenhuma referência em código ativo** (updater, firmware, V2, Registry/Lock/Resolver/Adapter, testes).
- **Referências restantes são só históricas:**
  - a lista `git_before` congelada em `INTEGRITY_BEFORE/FINAL/R1C_FINAL.json`, que é uma string de `git status` e não é verificada por nenhum código;
  - os LEIA_ME de etapas irmãs.
- **Nenhum `glob`/`rglob`/`walk` ativo seleciona essas pastas.**
- **Os únicos são artefatos derivados da própria etapa:** código, testes, LEIA_ME, outputs e ZIP de entrega. Cada ZIP foi aberto: CRC OK e 100 % dos membros idênticos a arquivos da própria pasta.
- **O move preserva tudo byte a byte e o rollback exato é possível.**

**Observações.**

- **2E4:** `WAVE2C_DECOUPLING_PLAN.md:30` registra que o usuário decidiu não movê-la naquela onda. A evidência técnica a libera, mas a decisão deve ser reconfirmada.
- **2E, 2E1, 2E31:** são citadas pela receita histórica de 2E41, que permanece na raiz. O ledger deve registrar o mapeamento de prefixo, sem editar o LEIA_ME.

## 4. EXTRACT_UNIQUE_EVIDENCE_THEN_ARCHIVE (7)

Pastas sem nenhum bloqueio operacional, mas com **evidência primária única** sem cópia em Git ou snapshot. São capturas de textos oficiais ou dados curados, não reproduzíveis localmente.

| Candidato | Bytes | Arquivos | Evidência única |
|---|---:|---:|---|
| `LEX-MACHINAETAPA_2D7` | 14.748.414 | 200 | 177 capturas brutas de busca de normas externas (`EXT_LC*.html`) |
| `LEX-MACHINAETAPA_2D8` | 6.618.625 | 137 | 81 textos oficiais P2 (LC 70/1991, 73/1993, 113/2001…) |
| `LEX-MACHINAETAPA_2D4` | 1.512.426 | 80 | 64 capturas camara.leg.br/planalto da validação estrutural |
| `LEX-MACHINAETAPA_2D5` | 552.521 | 24 | 6 textos oficiais incorporados (LC 140/141/142…) |
| `LEX-MACHINAETAPA_2D6_4` | 166.471 | 12 | 2 decretos recuperados (DEC 7724/2012, DEC 11249/2022) |
| `LEX-MACHINAETAPA_2D6_1` | 56.716 | 10 | 2 LCs recuperadas (LC 78/1993, LC 103/2000) |
| `LEX_MACHINA_JURIS_CF_J1` | 42.657 | 5 | `MODELO_CANONICO_JURISPRUDENCIA.json` (schema canônico proposto) e documentação J1 |

**Ação prévia:**

1. inventariar as capturas (path original, SHA-256, URL derivável do nome, etapa);
2. fazer uma cópia verificada em meio externo (fora do disco C:), já que o snapshot da ONDA 0 não cobre essas pastas.

Só depois disso a pasta entra no LOTE_2E_4.

## 5. O QUE AINDA IMPEDE LIMPEZA COMPLETA

**Por classe principal (exatamente uma por candidato):**

| Classe principal | Candidatos | Bytes |
|---|---:|---:|
| STILL_BLOCKED_PROTECTED545 | 54 | 2.887.175.712 |
| STILL_BLOCKED_ACTIVE_DEPENDENCY (`2E41`) | 1 | 840.815 |
| KEEP_IN_ROOT_INTENTIONALLY (`CF_SEGMENTADA_V2`) | 1 | 1.733.591 |
| EXTRACT (condicional) | 7 | 23.697.830 |

**Por causa (as causas se sobrepõem; não somar):**

| Causa | Candidatos | Bytes |
|---|---:|---:|
| PROTECTED545 + PATH_IDENTITY | 55 | 2.888.909.303 |
| NOT_DECOUPLED | 55 | 2.888.016.527 |
| UNIQUE_EVIDENCE | 60 | 2.910.204.288 |
| DYNAMIC_DISCOVERY | 36 | 2.845.117.936 |
| IDX | 16 | 2.826.848.037 |
| ABSOLUTE_PATH | 22 | 2.863.855.597 |
| PROVENANCE | 13 | 28.956.870 |
| ACTIVE_BUILD | 11 | 15.154.353 |
| CANONICAL_ACTIVE / MANIFEST_REFERENCE | 1 | 1.733.591 |
| MANUAL uncertainty | 0 | 0 |

**protected545.**

- Os 55 candidatos contêm 545 membros verificados por **path histórico + SHA-256** (`INTEGRITY_BEFORE.json` → `r1d_support.integrity()` lê `ROOT.parent/path`).
- Não existe relocation ledger, prova derivada aprovada nem política nova de integridade. Mover quebraria a prova V2, que ainda depende do path físico original.
- O Registry D05 não cobre nenhum desses paths.
- **Resultado:** BLOCKED_PROTECTED545_PATH_IDENTITY para os 55. `CF_SEGMENTADA_V2` recebeu KEEP porque, além disso, é entrada canônica ativa (adaptador do catálogo 69, `prepare_expansion.py`, testes V2).

**IDX (16 pastas, 130 arquivos).**

- Os arquivos continuam intactos, 130/130.
- A reprodução não foi provada.
- O binding IDX↔texto depende do layout local de `saida/`.
- `gerar_manifest.py:50` e `enriquecer_v1.py:28` fazem `REPO.rglob('*.IDX')`.

**Dependência ativa.**

- `2E41` é o default absoluto de `--pacote` no montador SD preservado (`LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:46`) e alvo da enumeração D12 (`iterdir`/`glob('EXT_*/*.txt')`).
- Referências `.py` ativas mantêm 9 pastas `REFERENCIAS_V1` presas:
  - por nome em `adaptar_catalogo_69.py`, `compare_pilot*.py`, `consolidate_labels.py`, `r1d1_pipeline.py` e `run_regression*.py`;
  - `TESTE_COMPLETO_ALPHA3_V1`, por exemplo, é lido pelo pipeline R1D1 e pelas regressões.

**Dynamic discovery.**

- **D01:** `consolidate_labels.py:56` faz `REPO.glob('LEX_MACHINA_REFERENCIAS*')` + `rglob('*.json')`, selecionando 55 arquivos marcadores em 20 pastas candidatas. Os IDs `SRCnnn` dependem da ordem dos paths.
- **D02/D05:** o `rglob` de IDX atinge as 16 pastas com IDX.
- **D12:** atinge 2E41.
- Nenhum desses grupos foi desacoplado (só o D05 foi).

**Not decoupled.** Os 55 bloqueados dependem de desacoplamento ainda não feito: D01, D02, D12, relocation ledger e prova derivada do protected545. O bloqueio é específico de cada pasta; não se usa "72 normas não migradas" como motivo.

## 6. Impacto da migração D05

- **Cobertura:** o Registry e o Lock D05 governam só `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200` (managed) e `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1` (externo). São **0 membros** entre os 81 candidatos.
- **Efeito direto na liberação:** nenhum. A prova D05 não é extrapolada para D01, IDX, firmware, updater nem etapas.
- **Efeito indireto útil:**
  - o replay A5B byte-idêntico e a coexistência SCA1B2 mostram que o D05 **não depende** de nenhum candidato;
  - as referências do D05 aos candidatos (130 IDX e o firmware em `BASELINE_ENRIQUECIMENTO_V1.json`; o `rglob` de IDX em `gerar_manifest.py`/`enriquecer_v1.py`) são fotografia histórica. Essas ferramentas não foram executadas no replay.
- **Byte Policy (`.gitattributes`):** protege a V2 contra mutação de EOL em checkout. Não se aplica aos candidatos, que são untracked, exceto firmware v7.12.0 e `LEX MAQUINA INO 2`, parcialmente tracked.
- **Por que 17 pastas passaram de ARQUIVAR_APOS_AJUSTE/REVISAR para READY:**
  - A reavaliação separou referência histórica de dependência operacional. Os "paths absolutos" que bloqueavam eram LEIA_ME de etapas irmãs (receitas de execuções já concluídas) e a string `git_before` congelada, que nenhum código verifica.
  - Mover a cadeia inteira em um lote, com ledger de mapeamento e rollback exato, resolve o ajuste que o plano antigo exigia, sem editar nada congelado.
  - A falta de cobertura do snapshot deixa de ser impedimento para um **move** verificado (os bytes são preservados), mas continua sendo impedimento para exclusão.
  - Onde a unicidade é evidência primária, a pasta foi para EXTRACT, e não para READY.

## 7. Arquivos e bytes únicos

- **60 candidatos têm arquivos sem cópia conhecida fora da pasta.**
- **Nos 18 READY:** os únicos são derivados da etapa. A ação é PRESERVED_WHOLE_BY_VERIFIED_MOVE.
- **Nos 7 EXTRACT:** há evidência primária. A ação é EXTRACT_UNIQUE_EVIDENCE_BEFORE_ARCHIVE.
- **Duplicatas:** registradas por candidato em `duplicates.sample`, com `duplicate_group`, `canonical_copy_candidate`, `secondary_copy`, `byte_identity` e `removal_allowed_by_hash_alone=false`. Hash igual **não** libera nenhuma ocorrência.
- **READY_TO_DELETE_CACHE_DUPLICATE = 0:** os `__pycache__` e zips dentro dos candidatos fazem parte do inventário da pasta e saem junto no move; não são apagados isoladamente.

## 8. Proposta para a ONDA 2E (não executada)

- **Archive root proposto:** `C:\GitHub_LEX_MACHINA_ARCHIVE\2026-09-28-wave2\`. Hoje ele não existe e **não foi criado**.
- **Destino:** `<archive_root>\<path relativo idêntico>`. O rollback é uma substituição de prefixo.
- **Modo:** MOVE REVERSÍVEL (copiar → reverificar 100 % dos hashes no destino → remover a origem). Nada é destruído, compactado ou deduplicado.
- **Registro por diretório:**
  - `source_path`, `archive_path`;
  - `size`, `file_count`, `sha256 inventory` (lista ordenada path+size+sha256 e hash do inventário);
  - `classification`, `reason`;
  - `pre_move_hash`, `post_move_hash`, `verified`;
  - `rollback_source`, `rollback_destination`.
- **Registro por arquivo:** path, size, pre/post sha256 e verified.
- **Timestamp:** só no relatório operacional, nunca na identidade.
- **Ledger:** append-only e com hash encadeado.
- **Gates (antes e depois de cada lote):**
  - HEAD, tracked limpo e staging vazio;
  - inventário da pasta = inventário desta ONDA 2R (abortar se divergir);
  - protected545 545/545, IDX 130/130, V2 281/281;
  - Registry, Lock e Resolver PASS;
  - destino inexistente (nunca mesclar);
  - um lote por vez, com autorização explícita.
- **Riscos antecipados** (verificados nos 25 liberáveis ou condicionais):

  | Risco | Situação |
  |---|---|
  | Nomes repetidos | Não colidem, porque o path relativo completo é preservado |
  | Casefold/NFC | 0 colisões |
  | Nomes não-ASCII | 0 |
  | Paths longos | Maior path no destino: 207 caracteres (< 260) |
  | Read-only | 0 arquivos |
  | Symlinks e reparse points | 0 |
  | Mesmo disco | Mover dentro de C: **não libera espaço físico**; só organiza a raiz |
  | Receitas absolutas nos LEIA_ME | Registradas no ledger; nunca editadas |

## 9. Novos candidatos fora do universo antigo

Estão registrados separadamente como NEW_CLEANUP_CANDIDATE e **não** fazem parte da execução futura:

- `LEX-MACHINAETAPA_2B`: diretório vazio na raiz;
- `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP` e `C:\GitHub\_LEX_MACHINA_SCA1B2_TEMP`: sandboxes de evidência fora do repositório;
- `updater/.venv` (139 MB): fica em área ativa;
- os JSONs grandes regeneráveis da auditoria em `CLEANUP_AUDIT/`.

## 10. Arquivos desta missão

- `CLEANUP_AUDIT/WAVE2R_REEVALUATION.json`: todos os 81 candidatos, com classificação, blockers, razões, confiança, referências atuais, dynamic discovery, únicos, duplicatas, dados físicos, proposta de archive e rollback, agregados e protocolo.
- `CLEANUP_AUDIT/WAVE2R_REEVALUATION.md`: este documento.
- `CLEANUP_AUDIT/WAVE2R_CANDIDATES.csv`: uma linha por candidato.

Os scripts de análise ficaram no scratchpad da sessão, fora do repositório. Nenhum arquivo funcional foi alterado.
