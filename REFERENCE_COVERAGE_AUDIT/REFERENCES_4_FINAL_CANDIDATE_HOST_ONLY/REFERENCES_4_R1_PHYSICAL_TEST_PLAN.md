# REFERÊNCIAS Nº 4 R1: plano de teste físico (próxima missão, NÃO executado)

```
STATUS = HOST_ONLY_CANDIDATE (nada instalado; cartão e ESP32 não tocados)
PACOTE = REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/
BASELINE FÍSICO VIGENTE = C3B.2 (tag lex-device-v1-correlata-c3b2-physical-approved-2026-10-12)
```

## O que muda no aparelho

**SD:** 5 arquivos em `/99_LEX_V1`. Os bytes estão em `candidate/SD/`, e os hashes, em `REFERENCES_4_R1_PACKAGE_MANIFEST.json`.

- `00_SYS/LEXV1.VER`
- `00_SYS/LEX_DEVICE_MANIFEST.json`
- `10_TARGETS/CF88_TARGETS.IDX`
- `20_REFERENCES/REF_LOOKUP.IDX`
- `20_REFERENCES/REF_PAYLOAD.IDX`

Não mudam:

- `99_RELATIONS_V2`: RELACOES, REL_LOOKUP e EXT_ARTIGOS, que são de CORRELATAS 1;
- ENTENDA, texto, TEXT_MAP e índices de artigos.

**Firmware:** app novo (flag 1). A única diferença é a tabela `lex_ref_detail_data.h`, que passa de 122 para 124 fichas, sem lógica nova.

- Binário candidato: `DEVICE_INTEGRATION/backups/references4_r1/build_cand/` (fora do Git). O sha256 está no relatório R1.
- Header: `LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h`.
- Na missão física, ele deve ser copiado para `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h`, e o sketch deve ser recompilado a partir da pasta versionada.

**Ordem e atomicidade:** SD e firmware precisam ir juntos.

- Com o firmware antigo, as 2 novas obras aparecem na lista, mas sem ficha de detalhe (`d = nullptr`).
- Com o firmware novo e o SD antigo, nada aparece para os arts. 196 e 206, I.

## Pré-voo (host, antes de tocar o cartão)

1. Fazer backup verificável de `/99_LEX_V1` e `/99_RELATIONS_V2` do cartão, conferindo bytes e sha256.
2. Conferir que o cartão está no C3B.2: `LEX_DEVICE_MANIFEST.json` com sha256 `6186c357…665a`, igual a `rollback/SD/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json`.
3. Rodar `python -B -m unittest discover -s DEVICE_INTEGRATION/tests -p test_references4_r1_device.py` e o equivalente em `LEGAL_TARGET_ID/tests`, ambos com PASS.

## Roteiro físico (mínimo)

| # | Ação no aparelho | Esperado |
|---|---|---|
| 1 | Ligar | Boot normal e DIAG de boot PASS (inclui `references_single_result` em `CF88:ART.127`). `LEXV1.VER` com `REFERENCE_ENGINE cf-reference-engine-run5-references4-r1` |
| 2 | Referência antiga: CF art. 37 → tecla 4 | Lista com Os Donos do Poder e Raízes do Brasil; ficha de detalhe abre |
| 3 | CF art. 196 → tecla 4 | Rodapé com `4 REF.` e lista com **Sicko - S.O.S. Saúde**. A ficha mostra DOCUMENTÁRIO 2007, nota 7,4, o "sobre" (Michael Moore) e o alcance com "Limites" |
| 4 | CF art. 206, I → tecla 4 | Rodapé com `4 REF.` e lista com **Pro Dia Nascer Feliz**. A ficha mostra DOCUMENTÁRIO 2005, nota 8,0 e o "sobre" (João Jardim) |
| 5 | CF art. 206 (caput) e art. 206, II | **Sem** `4 REF.`: não há herança para outras linhas |
| 6 | CORRELATA crítica: CF art. 202, § 5º → tecla 1 | LC 108/2001, art. 26, como no C3B.2 |
| 7 | CORRELATA: CF art. 37, § 3º, III | Sem `1 CORR.` fantasma |
| 8 | Lacunas confirmadas: CF arts. 98 e 202 | Sem `4 REF.` |
| 9 | Navegar lista → detalhe → voltar nos arts. 196 e 206, I | Sem travamento; título, tipo e ano legíveis na tela |

## Rollback

Restaurar os 5 arquivos de `rollback/SD/99_LEX_V1/`, que têm os bytes do C3B.2, e regravar o app do baseline C3B.2.

## Fora do escopo

- Nenhuma alteração em CORRELATAS 1.
- Nenhum vínculo novo além de P20/P21.
- Sem tag até a aprovação física.
