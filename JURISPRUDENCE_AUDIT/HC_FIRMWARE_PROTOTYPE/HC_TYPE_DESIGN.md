# FASE C — Tipo HC no LEX DEVICE V1 (estudo + protótipo HOST-ONLY)

```
HC_TYPE_DESIGN = PASS · HC_HOST_PROTOTYPE = PASS (compilado; não gravado) · HC_FIRMWARE_FLASHED = NO · PHYSICAL_APPROVAL = NO
FIRMWARE_BASELINE_REPRODUCED = YES (base recompilada = app aprovado 6e329c91…, exceto 70 bytes de metadados de build)
firmware/ NÃO modificado · protótipo só em DEVICE_INTEGRATION/_tmp_fw_hc/ e backups/ (fora do Git)
```

## C1. Onde o firmware trata o tipo (inspeção do código real)

| Ponto | Local no `.ino` | Comportamento atual |
|---|---|---|
| Enumeração | `enum TipoJurisprudencia` (~l. 764) | `SV, SUMULA_STF, RG, REPETITIVO_STJ, IAC, SIRDR, ADI, ADC, ADPF, ACORDAO, OUTRO`; não existe HC |
| Parser do `JURISPRUDENCIA.IDX` | `adicionarLinhaJurisCF` (~l. 2009) | Lê 8 colunas; `TIPO` = coluna 1, `NUMERO` = coluna 3, `IDENTIFICADOR` = coluna 6; exige `ID` iniciando com `STF:` |
| Resolução da chave (camada V1) | `lexV1AdicionarJurisPorId` (~l. 6718) | Linha cuja chave começa com `<chave>|` (PSRAM ou SD); independe do tipo |
| Rótulo da lista e título da ficha | `rotuloTipoJurisprudencia` (~l. 1073) | `"hc"` cai no `default`, e aparece **`OUTRO 232627`** |
| Arquivo da ficha | `arquivoDetalheJurisCF` (~l. 1090) | `STF:HC:232627` vira `03_CONTEUDO/STF_HC_232627.TXT`; independe do tipo |
| Abertura e BACK | `abrirItemRelacaoSelecionado` / `restaurarArtigoAposReferencia` | Genéricos; independem do tipo |
| Contadores e categorias | `contabilizarTipoJurisCF` + filtro de categorias (~l. 3931) | Na camada V1 a categoria é sempre `REL_JURIS_TODAS`; os contadores só servem ao caminho legado |
| Cache PSRAM | `carregarCacheJurisCF` | Valida offsets e soma; independe do tipo |
| Limites | `MAX_RELACOES_ARTIGO` 32, rótulo 34 colunas | `HC 232627` tem 9 caracteres |

## C2. Existe solução sem firmware novo?

**Não, sem falsificar dados.** O rótulo é sempre `<prefixo do TIPO> + NUMERO`, e os prefixos existentes são `SV`, `SUMULA STF`, `RG TEMA`, `REPETITIVO STJ`, `IAC`, `SIRDR`, `ADI`, `ADC`, `ADPF`, `ACORDAO` e `OUTRO`.

| Alternativa | Por que não |
|---|---|
| `TIPO=hc` | Exibe `OUTRO 232627` |
| `TIPO=acordao` | Exibe `ACORDAO 232627` (não é o rótulo pedido) ou, com `NUMERO="HC 232627"`, `ACORDAO HC 232627` (tipo deturpado) |
| `TIPO=adi` / `adpf` com `NUMERO` manipulado | Falsifica a classe processual |

Conclusão: o HC exige uma mudança de firmware, e por isso foi para a variante B do J2E.

## C3. Protótipo

`build_hc_firmware_prototype.py` faz quatro coisas:

1. Monta a **base reproduzível**: o sketch de `firmware/`, sem mudança desde `e9c7d53`, com `lex_ref_detail_data.h` substituído pelo header **versionado de 124 fichas** (`run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h`).
2. Compila a base e compara byte a byte com o app aprovado. As 70 diferenças estão todas em metadados de build:
   - o hash do ELF no `esp_app_desc`;
   - `__TIME__`/`__DATE__` do banner "Software Info" do core;
   - o checksum e o sha no fim da imagem.
3. Aplica `hc_type.patch`: 4 edições com âncora exata, que falham se a âncora não for única.
   - `JTIPO_HC` no enum, antes de `JTIPO_OUTRO`;
   - `"hc"` e `"habeas_corpus"` classificados como `JTIPO_HC`;
   - `case JTIPO_HC: return "HC "+r.numero;`;
   - HC contado com o grupo ADI/ADC/ADPF/ACORDAO.
4. Compila o protótipo HC.

| Build | Programa | RAM estática | App .bin | Livre em app0 | sha256 |
|---|---:|---:|---:|---:|---|
| Aprovado (R2) | 1.100.991 | 126.148 | 1.101.136 | 209.584 | `6e329c91…` |
| Base recompilada | 1.100.991 | 126.148 | 1.101.136 | 209.584 | `e4da3863…` (só metadados) |
| **Protótipo HC** | **1.101.127 (+136)** | **126.148 (=)** | **1.101.280 (+144)** | **209.440** | `169b6619…` |

## C4. Dívida do header (122 × 124)

**Não foi resolvida no diretório `firmware/`**: o header ali continua com 122 fichas (`2ca5820a…`). Mesmo assim, ela **não bloqueia** o protótipo:

- o build usa o header de 124 fichas versionado, o mesmo que gerou o app aprovado;
- a base recompilada é idêntica ao aprovado, exceto pelos metadados de build.

Por isso o estado não é `HC_FIRMWARE_PROTOTYPE_BLOCKED_BY_REPRODUCIBILITY`. A dívida em `firmware/` continua registrada; corrigi-la exige mexer em `firmware/`, o que o guard das Correlatas proíbe.

## C5/C6. Testes e impacto

- **Simulação** (`J2E_ISOLATION_AUDIT`, variante B): com o firmware HC, a lista do art. 53, § 1º mostra `HC 232627`, e a ficha `STF_HC_232627.TXT` resolve. Com o firmware atual, mostraria `OUTRO 232627`.
- **RG, SV, ADI e o julgamento conjunto:** rótulos idênticos nas duas simulações.
- **Flags, cache e BACK:** nada muda. São independentes do tipo, e a auditoria J2E confere cache e flags.
- **Impacto:**
  - flash: +144 B;
  - RAM estática: 0;
  - PSRAM: 0, porque o cache do índice só cresce pelos dados, não pelo código;
  - partição app0: sobra 209.440 B.
- **Não verificado**, porque depende do aparelho: tempo de boot, comportamento real da tela e do BLE. Compilar não é passar no teste físico.

## C7. Dois candidatos, sem mistura

| Candidato | Conteúdo | Firmware | Exige gravação futura? |
|---|---|---|---|
| **A** (`VARIANT_A_CURRENT_FIRMWARE`) | Batch02 sem HC (268/166) | app aprovado atual | **Não** (só SD) |
| **B** (`VARIANT_B_REQUIRES_HC_FIRMWARE`) | A + HC 232627 (269/167) | protótipo HC (`169b6619…`), **não aprovado** | **Sim**: firmware novo + teste físico próprio |

Nenhum dos dois foi instalado.
