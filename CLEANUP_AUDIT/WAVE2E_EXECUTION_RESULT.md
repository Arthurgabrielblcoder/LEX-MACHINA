# ONDA 2E — Limpeza reversível da raiz (execução)

**Resultado: `ONDA_2E_CONCLUIDA_COM_DEFERIDOS`.**

| | |
|---|---|
| Movidos com identidade de bytes verificada | 17 candidatos |
| Deferidos por hold humano anterior | 1 (2E4) |
| Falhas | 0 |
| Exclusões permanentes | 0 |

- **Autoridade:** `CLEANUP_AUDIT/WAVE2R_REEVALUATION.json`, commit `63947add554bbfc1e43db0094d9dcc9c0572bc2f`, tag `pre-wave2-execution-2026-09-28`.
- **Archive root:** `C:\GitHub_LEX_MACHINA_ARCHIVE\2026-09-28-wave2`, criado nesta missão. Não existia antes.
- **Mesmo volume (C:).** O move **não é backup** e **não libera espaço físico**: espaço liberado = **0 bytes**. O ganho é organizacional.

## 1. Seleção

| Etapa | Count | Bytes |
|---|---:|---:|
| READY_TO_ARCHIVE_REVERSIBLY (HIGH) na WAVE2R | 18 | 7.613.511 |
| Human hold encontrado | 1 | 49.357 |
| Elegíveis para execução | 17 | 7.564.154 |
| Movidos e verificados | 17 | 7.564.154 |
| Bloqueados durante a execução | 0 | 0 |

**Human hold (W2R-029, `LEX-MACHINAETAPA_2E4`).** O hold vem de uma decisão humana anterior, não de um motivo técnico:

- `WAVE2C_DECOUPLING_PLAN.md:30` registra que o usuário decidiu não movê-la;
- `WAVE2C_DECOUPLING_PLAN.md:429` diz que a pasta de 49 KB já elegível "permanece parada por decisão do usuário".

Status: `DEFERRED_BY_PRIOR_HUMAN_HOLD`; classificação operacional: `READY_BUT_DEFERRED_BY_PRIOR_HUMAN_HOLD`. A pasta continua no path original, intacta.

**Não movidos, por regra:**

- os 7 `EXTRACT_UNIQUE_EVIDENCE_THEN_ARCHIVE` (2D4, 2D5, 2D6_1, 2D6_4, 2D7, 2D8, JURIS_CF_J1);
- os 55 `STILL_BLOCKED_*` (inclui 2E41 e todos os que têm protected545 ou IDX);
- `CF_SEGMENTADA_V2` (KEEP);
- os novos candidatos fora do universo antigo (`LEX-MACHINAETAPA_2B`, sandboxes `_LEX_MACHINA_*_TEMP`, `updater/.venv`, JSONs grandes da auditoria).

## 2. Movimentos

Cada candidato foi movido para `<archive_root>\<path relativo idêntico>`, em três lotes naturais da WAVE2R:

- LOTE_2E_1: cadeia 2D9→2D17;
- LOTE_2E_2: cadeia 2D6;
- LOTE_2E_3: cadeia 2E, a montante de 2E41, sem 2E4.

| ID | Candidato | Lote | Arquivos | Dirs | Bytes | Hash do inventário (pré = pós) | Pós |
|---|---|---:|---:|---:|---:|---|---|
| W2R-005 | LEX-MACHINAETAPA_2D10 | 1 | 11 | 6 | 191.937 | d26af3a805a880ab2bb31915d61a7f14a454439a59941637f6c062277b363b5c | igual |
| W2R-006 | LEX-MACHINAETAPA_2D11 | 1 | 12 | 6 | 222.508 | 8ff043208b7e42cdf8eb596e99074c0e778b5c652a5a1cf94754862a17b3a57a | igual |
| W2R-007 | LEX-MACHINAETAPA_2D12 | 1 | 35 | 7 | 1.127.159 | 0d1a5a9a8dcb02ec8e8e44f6364ec07b003c3b52c95a3db8267038ca98abf556 | igual |
| W2R-008 | LEX-MACHINAETAPA_2D13 | 1 | 12 | 6 | 297.192 | 243f41c16a3bdec536ada333054691f98cc2d3856fbb2460b978a6e2b539c35e | igual |
| W2R-009 | LEX-MACHINAETAPA_2D14 | 1 | 12 | 6 | 317.678 | 606f0f173fcd0c834e776d4b8224b945c39aaa9b4acc154649e7b2d5e0c5961e | igual |
| W2R-010 | LEX-MACHINAETAPA_2D15 | 1 | 12 | 6 | 365.122 | e27c9ddea8ece1fbd95acc31d47979e9eaa0f40df73bc191a669d64c1fa98b9d | igual |
| W2R-011 | LEX-MACHINAETAPA_2D16 | 1 | 11 | 6 | 352.185 | 1749c583bad31a2f47ffd510a3f03af68b791daefcfbff1ba5350b270f6db33b | igual |
| W2R-012 | LEX-MACHINAETAPA_2D17 | 1 | 8 | 6 | 56.208 | b58a4552912255f32f37bf7fb9a46a99eb105572a4edc6e443edf4a2a792d65a | igual |
| W2R-023 | LEX-MACHINAETAPA_2D9 | 1 | 36 | 8 | 2.102.330 | 729023850967577112d433a72aa5390410e03b5c894c545e05b7537730338879 | igual |
| W2R-016 | LEX-MACHINAETAPA_2D6 | 2 | 10 | 6 | 55.328 | 07f657d870f9b5befcad6cefb9f3658f6b0336614b57ca47b5fa296011897a97 | igual |
| W2R-018 | LEX-MACHINAETAPA_2D6_2 | 2 | 8 | 5 | 46.578 | 58a38b93a16b2f49e42b2e3e4c28904b1c493d71942c335a74316f9dcea67595 | igual |
| W2R-019 | LEX-MACHINAETAPA_2D6_3 | 2 | 8 | 5 | 48.501 | 7ed13a9a1c877595c696165848cda6af6b07d9985356c651329d457da2be1a3d | igual |
| W2R-024 | LEX-MACHINAETAPA_2E | 3 | 9 | 6 | 95.971 | e9bace7075437962c64b161344e56fe8362a019844e027e0fe630aee5e1ef88b | igual |
| W2R-025 | LEX-MACHINAETAPA_2E1 | 3 | 10 | 6 | 120.570 | ad04bba501ec06dc4e42b2e7d4d7b21a22989c1535bfd2ec0574daface2444ac | igual |
| W2R-026 | LEX-MACHINAETAPA_2E2 | 3 | 29 | 27 | 737.743 | 109b91b246867c48049ede759659da6741f10ca2e3933407121e8e56f2c4836d | igual |
| W2R-027 | LEX-MACHINAETAPA_2E3 | 3 | 25 | 23 | 683.641 | dc3c174ecf6bcd98ed582dcb0112cb9ea15e53780c3ffb62f54b46bf212c807d | igual |
| W2R-028 | LEX-MACHINAETAPA_2E31 | 3 | 29 | 27 | 743.503 | c8fe957f7b3ad82209573b4a6b9b1e65d01687bcfad258ec71b431cff4f3c176 | igual |

**Totais relocados:** 277 arquivos, 7.564.154 bytes, 17 diretórios de topo e 162 subdiretórios. Isso é 0,259 % do volume antigo da ONDA 2.

**Hash do inventário:** SHA-256 da concatenação, por arquivo, de `relative_path` + NUL + sha256 + NUL + tamanho + LF. Os arquivos são ordenados pelos bytes UTF-8 do path relativo (POSIX, relativo à raiz do candidato). O manifesto também traz o SHA-256 individual pré/pós de cada arquivo, com o path em casefold e em NFC.

**Verificação por candidato (todos 17/17):**

- mesma contagem de arquivos e de diretórios;
- mesmo tamanho;
- conjunto de paths idêntico (incluindo diretórios);
- conjunto de SHA-256 idêntico;
- hash do inventário idêntico;
- origem ausente depois do move;
- destino presente.

**Pré-checagens:** zero conteúdo tracked pelo Git, zero reparse points, symlinks ou junctions, zero read-only, zero colisões casefold/NFC e nenhum destino preexistente. O maior path absoluto no archive tem menos de 260 caracteres.

O move foi `os.rename` dentro do mesmo volume: nenhuma cópia intermediária e nenhuma exclusão.

## 3. Rollback

Para cada candidato movido: `rollback_from = C:\GitHub_LEX_MACHINA_ARCHIVE\2026-09-28-wave2\<rel>` e `rollback_to = C:\GitHub\LEX-MACHINA\<rel>`, com `rollback_possible = true`.

Procedimento:

1. confirmar que `rollback_to` não existe;
2. executar `os.rename(rollback_from, rollback_to)`;
3. recalcular o inventário e exigir `inventory_sha256` igual ao valor pré-move.

Os paths originais não devem ser reutilizados para outra finalidade.

## 4. Integridade

As verificações rodaram antes da execução e depois de cada lote; o resultado final está abaixo.

| Verificação | Resultado |
|---|---|
| protected545 | 545/545 idênticos, nenhum path ausente |
| IDX | 130/130 idênticos |
| V2 congelada | 281/281 |
| ENRIQUECIDO_V1 | 7/7 (6 membros + manifest `0312e5f0…`) |
| Registry (`verify_registry.py`) | PASS, 855 entradas |
| Lock (`verify_lock.py`) | PASS, 0 extras |
| Resolver (`verify_resolved_selection.py` sobre `D05_SHADOW_RESOLVED_SELECTION.json`) | PASS, 0 extras |
| Byte policy | `.gitattributes` sem alteração |
| Git | 0 alterações em arquivos tracked; staging vazio antes do commit |

Consumer/adapter, Legacy capture, R2B2 e SCA1B2 são arquivos tracked e não mudaram.

## 5. Raiz

| Medida | Antes | Depois |
|---|---:|---:|
| Candidatos da ONDA 2 na raiz | 76 | 59 |
| Diretórios de topo na raiz (sem `.git`) | 88 | 71 |
| Entradas removidas da raiz | — | 17 |
| Bytes relocados | — | 7.564.154 |
| Espaço físico liberado | — | **0** (mesmo volume) |

## 6. Artefatos

- `CLEANUP_AUDIT/WAVE2E_RELOCATION_MANIFEST.json`: um registro por candidato, com status, pré/pós, inventário por arquivo, rollback e checagens por lote.
- `CLEANUP_AUDIT/WAVE2E_MOVES.csv`: uma linha por candidato.
- `CLEANUP_AUDIT/WAVE2E_EXECUTION_RESULT.md`: este documento.

O archive externo **não** é versionado no Git.

## 7. Próximo grande bloqueio

99,7 % do volume antigo continua na raiz por causa do **protected545**: 55 pastas, 2,89 GB, com prova V2 ligada ao path físico. As 16 pastas com IDX e a descoberta dinâmica D01/D02/D12 também seguram volume.

Liberar isso exige:

- relocation ledger mais prova derivada do protected545, com nova política aprovada;
- desacoplamento de D01, D02 e D12.

Os 7 EXTRACT (23,7 MB) dependem antes de uma cópia verificada das capturas primárias em meio externo.
