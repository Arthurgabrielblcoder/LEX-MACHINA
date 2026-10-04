# MARIA2006_SOURCE_REPAIR — plano de implantação física

**Executado em 2026-10-04 e aprovado.** Resultado em `MARIA2006_SOURCE_REPAIR_PHYSICAL_REPORT.md`.

## FASE A — AÇÃO FÍSICA DE ARTHUR

1. Desligar o LEX MACHINA.
2. Retirar o microSD.
3. Colocar o cartão no PC.
4. Informar a letra da unidade.

Lembrete da última implantação: o leitor microSD é alimentado pelo módulo da tela. Ao recolocar o cartão (fase F), o aparelho precisa
ligar com o leitor energizado; sem isso, o boot mostra "SD indisponível" (`ENVIRONMENTAL_HARDWARE_POWER_ISSUE`).

---

**Baseline:** commit `108469319bbe903f59dfecd4c33f9642f8984b91`, tag `lex-device-v1-full-corpus-indexes-approved-2026-10-04`.

**Firmware:** não muda. O aparelho já roda o flag1 aprovado `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc`, que lê o catálogo
LXARTCT1 (limite de 4.096 entradas; agora são 72). **Sem flash.**

**Staging:** `DEVICE_INTEGRATION/staging_maria2006_source_repair/SD/`, gerado por `tools/repair_maria2006_source.py`.
Dados de deploy em `_host/MARIA2006_REPAIR_MANIFEST.json`.

## Diff aprovado (somente 3 arquivos)

| Ação | Caminho no cartão | Antes (físico) | Depois (staging) |
|---|---|---|---|
| REPLACE | `/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt` | 215.426 B `a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c` | 46.902 B `f1d43b76e1ae4013cbf812d5ac2169561e6bc6c4ecfa1e5ab7fbf2721c7d341f` |
| REPLACE | `/99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX` | 4.040 B `efadd17ee2483a325f1451d71ee40e8fedbf3c032ed0127cbdbc61a9c72b2f3b` | 4.096 B `8d7d11db81dfa1a07f647260e17a88b197b90a3b912012880a3701e5ca31a4c9` |
| ADD | `/99_LEX_V1/10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX` | — | 796 B `61e00407355f37f516eede152d0436f8e7e2897ebf4fff81eca2ecf5e86ad2d6` |

Total a escrever: 51.794 B.

**Não tocar em:**
- os 71 `*_ARTICLE_SEARCH.IDX` existentes (KEEP);
- runtime, TEXT_MAP, ENTENDA, REF/RUN3, `LEXV1.VER`;
- nenhum outro TXT.

## FASE B — manifesto e backup (somente leitura)

1. Manifesto completo do cartão, comparado com `backups/full_corpus_physical_deploy_20261003/sd_manifest_post_full.json`.
   Esperado: 0 diferenças, salvo `System Volume Information`.
   **Divergência → PARAR.**
2. Confirmar os hashes da coluna "Antes" e a ausência do `MARIA2006_ARTICLE_SEARCH.IDX`.
3. Backup verificável (size + SHA-256) do TXT e do catálogo atuais.

## FASE C — cópia

Para cada um dos 3 arquivos:
1. Gravar com nome temporário.
2. `fsync`.
3. Reler e comparar size + SHA-256.
4. Renomear para o nome final.

O TXT e o catálogo substituem os arquivos de mesmo nome. Nenhum outro arquivo é aberto para escrita.

## FASE D — readback

- 3/3 MATCH contra o staging.
- Novo manifesto completo: exatamente 2 alterados, 1 adicionado, 0 removidos; todo o resto byte-identical.

## FASE E — ejetar

"Remover hardware com segurança" e aguardar a confirmação do Windows.

## FASE F — Arthur recoloca o cartão

Com o LEX MACHINA desligado e o leitor alimentado, recolocar o cartão e ligar.

## FASE G — boot (sem flash)

Capturar a serial e conferir:
- `boot:0x2b`;
- `JUR CACHE`;
- `DIAG RESULT PASS pass=33 fail=0`;
- zero `FAIL_IO`, panic, watchdog ou `CATALOGO_INVALIDO`.

## FASE H — testes físicos

1. **Abrir a Lei Maria da Penha:** a serial deve mostrar `OPEN ARTIDX_CAT` e depois `OPEN ARTIDX .../MARIA2006_ARTICLE_SEARCH.IDX`, sem `NENHUM_INDICE_VALIDO`.
2. **Texto:** começa em "LEI Nº 11.340, DE 7 DE AGOSTO DE 2006", com acentuação correta e sem `< h t m l >`.
3. **Busca pelo número:** 1, 12, 22, 46 → artigo certo e rápido. 47 → não encontrado. Um ENTER a mais → SEM OUTRA OCORRÊNCIA.
   Os artigos com sufixo (10-A, 12-C...) ficam indexados, mas não são digitáveis no teclado numérico.
4. **Troca de norma:** Maria da Penha → CF (193) → CC (2000) → Maria da Penha. Cada texto deve carregar o próprio índice.
5. **Fluidez:** scroll, abrir e fechar camadas, sem reboot.

## Rollback (sem Git)

1. Restaurar o TXT e o catálogo a partir do backup da fase B.
2. Remover `MARIA2006_ARTICLE_SEARCH.IDX`.

Com o TXT antigo, o catálogo novo também não selecionaria o índice: o tamanho e o SHA-256 do texto não batem, e a busca volta a ser
linear. Mesmo uma combinação mista nunca usa um índice errado.
