# Onda 2C — arquitetura de desacoplamento do legado

**Plano somente. Não foi implementado registry, migração, alteração de discovery, movimentação ou mudança de manifest funcional. Onda 2B não autorizada.**

Base: commit `88c1de330fb64eeecb1589935b2824b8c6fb2638` e Onda 2A (81 pastas, 2.921.061.459 bytes). Reuso do inventário e dos hashes existentes; leitura estática dirigida do código. Nenhuma Engine, pipeline ou acesso ao SD foi executado.

## Recomendação e alternativas

Adotar futuramente um **registry de artefatos + lock explícito de datasets + manifest de distribuição**. Identidade lógica, identidade dos bytes, papel, proveniência e localização são dimensões diferentes. O registry descreve o que existe; o lock determina o que uma execução autorizada usa; o manifest de release descreve o que vai ao SD. A V2 congelada permanece como prova histórica, com tooling novo separado.

| Alternativa | Benefício | Limitação / decisão |
|---|---|---|
| Manter paths históricos e documentar melhor | Compatibilidade imediata com V2 e guard atual. | Não desacopla nem reduz a raiz; seleção por glob continua implícita. Usar como estado de segurança até concluir a migração. |
| Links/junctions ou cópia de compatibilidade na raiz | Pode satisfazer leitores antigos sem edição. | Mantém identidade por path, amplia ambiguidades de glob/backup e cria dependência de plataforma. Duplicar bytes não reduz espaço. Não recomendar como arquitetura principal; compatibilidade apenas em ambiente forense isolado e autorizado. |
| Registry de artefatos + lock explícito + localização separada | Seleção auditável, versionável e portável; separa bytes, papel, localização e ativação. | Exige governança, resolução inequívoca, paridade e uma nova política de integridade. RECOMENDADA, em nova linha de tooling; V2 congelada permanece intacta. |
| Armazenamento exclusivamente por hash/CAS ou banco central | Centraliza blobs e localização, facilita cópias verificáveis. | Hash não codifica papel, ordem, revisão humana ou proveniência; banco agrega migração/backup e operação. CAS não dispensa lock e não autoriza deduplicação. Opcional posteriormente; começar com documentos pequenos versionados e blobs preservados. |

## Causas estruturais — contagens não aditivas

| Causa | Pastas | Critério verificável |
|---|---:|---|
| A_PROTECTED545 | 55 | Contém pelo menos uma das 545 entradas imutáveis. |
| B_PATH_ABSOLUTO | 16 | Alvo de referência absoluta classificada ativa; há 43 pastas se incluídas menções históricas. |
| C_DESCOBERTA_DINAMICA | 50 | 49 alvos dos globs de Referências/IDX + pacote 2E41 enumerado por EXT_*. |
| D_IDX | 15 | Contém IDX, independentemente de bytes duplicados. |
| E_CONTEUDO_UNICO | 55 | Únicos sem cobertura Git/snapshot que ainda bloqueiam elegibilidade; não inclui o piloto 2E4 já classificado de baixo risco. |
| F_PROVENIENCIA | 15 | Contém RAW_SOURCE único; indicador mínimo de custódia/proveniência necessária. |
| G_OUTRAS | 26 | Receitas interetapas e/ou papel ativo de insumo/baseline. |

Existem arquivos sem cópia externa conhecida em 80 das 81 unidades. Em 56 há únicos sem cobertura Git/snapshot; a unidade 2E4 é exceção de baixo risco já estudada, mas o usuário decidiu não movê-la. O JSON contém a matriz por pasta e as evidências; causas se sobrepõem. Não se soma a coluna para obter número de pastas.

## Descoberta dinâmica e acoplamento por nome

Foram lidos estaticamente **133 módulos Python**, sem falha de parse: **83 chamadas de enumeração de filesystem**, 208 seletores de texto/path e três chamadas `walk` locais excluídas por percorrerem JSON, não diretórios. Não foram encontrados `os.listdir`/`os.scandir` nessa superfície. Inclui ferramentas de reprodução, testes e versões de geradores preservadas; não afirma que todos sejam executados atualmente.

O caso central é `06_BENCHMARKS/consolidate_labels.py:56`: `REPO.glob(LEX_MACHINA_REFERENCIAS*)`, excluindo a V2, seguido de `folder.rglob(*.json)`. O inventário reproduz **35 árvores (34 históricas + adaptador 69), 205 JSONs candidatos e 55 arquivos contendo marcadores literais de decisão humana**. Isso é apenas a pré-seleção: não são 55 fontes/votos independentes. A rotina resolve pares, gera IDs SRC em ordem e conserva proveniência; também tem `groupdefs` fixos e uma fonte ASTRA. Substituir apenas o glob sem manter ordem, multiplicidade, regras de aceitação e esses grupos mudaria a avaliação.

`canonical_input.py:23/29` infere papel pelo prefixo 02_DISPOSITIVOS/03_OBRAS; `prepare_expansion.py:190` escolhe artefato pelo sufixo FAMILIAS_TEMPLATES_V2.json. Os quatro filtros de grupo em `gerar_manifest.py:61–65` também dependem de prefixos. A arquitetura nova deve representar esses papéis explicitamente. Regex de artigos, texto e URLs continua sendo parser; não deve ser removida em nome do desacoplamento.

A busca de jurisprudência por basename nos geradores recusa seleção arbitrária quando há múltiplos candidatos (`gerar_indice_esp32_v6.py:2424`). O resolvedor futuro deve preservar esse comportamento de falha, selecionando por identidade, snapshot e camada. `main.configurar_destino` aceita uma raiz externa; destinos/SD de runtime não foram acessados.

Cada uma das 83 chamadas tem no JSON arquivo, função, linha, expressão/padrão, finalidade, consumo, risco, alternativa, raízes, candidatos e diretórios. A resolução estática identifica parâmetros desconhecidos explicitamente. Por exemplo, `gerar_relatorios.py:312` enumera um diretório de compilação temporário criado por `tempfile.mkdtemp`, e `CF_SEGMENTADA_V2.tree` percorre a Engine V1.2 apenas para calcular hashes. Diretórios vazios e `.git` não integram o inventário reutilizado.

### Grupos de descoberta

**D01 — Descobrir JSONs de árvores de referências anteriores e filtrar marcas de decisão humana.**

Raízes de referência: `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1`, `LEX_MACHINA_REFERENCIAS_AUDITORIA_ASTRA_V1`, `LEX_MACHINA_REFERENCIAS_AUDITORIA_CAUSAL_V132_V1`, `LEX_MACHINA_REFERENCIAS_AUDITORIA_CONTRATO_ENGINE_V1`, `LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V1`, `LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V2_FINAL`, `LEX_MACHINA_REFERENCIAS_BENCHMARK_69_HUMANO_V1`, `LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2` (lista completa no JSON). Diretórios no domínio/candidatos do inventário: 47. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Ledger de rótulos, fontes SRCnnn, pares, conflitos e grupos de avaliação; não são features do compilador. Risco: **ALTO**. Alternativa: Lista ordenada de fontes de avaliação autorizadas com hashes, versões e papel; preservar ordem, multiplicidade, rejeições e groupdefs explícitos.

**D02 — Encontrar todos os IDX locais para integridade.**

Raízes de referência: `1- LEX-MACHINAETAPA_2D3`, `LEX-MACHINAETAPA_2C`, `LEX-MACHINAETAPA_2D`, `LEX-MACHINAETAPA_2D2`, `LEX-MACHINAETAPA_2E5`, `LEX-MACHINA_ETAPA_2E6_SD_TESTE`, `LEX_MACHINA_JURIS_CF_J2`, `LEX_MACHINA_JURIS_CF_J2_5` (lista completa no JSON). Diretórios no domínio/candidatos do inventário: 44. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Lista de 130 ocorrências path+hash e monitoramento temporal. Risco: **ALTO**. Alternativa: Manifest fechado de ocorrências IDX e seus papéis, separado do conjunto ativo da release.

**D03 — Monitorar arquivos fora da missão pela data de modificação.**

Raízes de referência: `1- LEX-MACHINAETAPA_2D3`, `CF_SEGMENTADA_V2`, `CLEANUP_AUDIT`, `LEX-MACHINAETAPA_2C`, `LEX-MACHINAETAPA_2D`, `LEX-MACHINAETAPA_2D10`, `LEX-MACHINAETAPA_2D11`, `LEX-MACHINAETAPA_2D12` (lista completa no JSON). Diretórios no domínio/candidatos do inventário: 3094. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Relatório de escritas fora do escopo histórico da expansão. Risco: **ALTO**. Alternativa: Escopo explícito da missão e diário de mudanças; preservar o relatório histórico, não reexecutá-lo como gate temporal de uma missão nova.

**D04 — Freeze e seleção de artefatos R1D/R1D1 dentro da própria V2.**

Raízes de referência: `LEX_MACHINA_REFERENCIAS_V2`. Diretórios no domínio/candidatos do inventário: 30. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Manifests de entrada, integridade e release congelada. Risco: **ALTO**. Alternativa: Manifest de artefatos da nova execução, mantendo os freezes V2 existentes imutáveis.

**D05 — Selecionar lotes, capturas, overlays, checkpoints e catálogos da expansão.**

Raízes de referência: `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200`. Diretórios no domínio/candidatos do inventário: 13. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Curadoria, relatórios e manifests do catálogo/enriquecimento. Risco: **MEDIO**. Alternativa: Entradas explícitas por papel, candidate_id e ordem; preservar contagens, identidades e pacote congelado.

**D06 — Conferir hash da Engine preservada, enumerar JSON local e detectar IDX inesperados em teste de segmentação.**

Raízes de referência: `CF_SEGMENTADA_V2`, `LEX_MACHINA_REFERENCIAS_ENGINE_V1_2`. Diretórios no domínio/candidatos do inventário: 7. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Asserções de preservação da segmentação constitucional. Risco: **MEDIO**. Alternativa: Contrato de fixture/arquivos esperados; testes negativos continuam procurando intrusos em seu sandbox.

**D07 — Selecionar backups catalogo_mestre_* e buscar arquivos de recuperação.**

Raízes de referência: `updater/backup_catalogos`. Diretórios no domínio/candidatos do inventário: 38. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Auditoria/restauração baseada em candidatos de backup. Risco: **ALTO**. Alternativa: Registro de backups por captura/data/hash; seleção explícita pelo operador, nunca o primeiro/mais recente arbitrário.

**D08 — Inventariar acervo da origem/destino configurado.**

Raízes de referência: `updater/saida`. Diretórios no domínio/candidatos do inventário: 119. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Contagens, diagnóstico, auditoria e inventário de legislação/jurisprudência. Risco: **MEDIO**. Alternativa: Perfil explícito de acervo e lista de distribuição; manter scanner de diagnóstico como observador, sem promover descobertas a ativo.

**D09 — Buscar jurisprudência pelo basename sob raiz CDC/19_JURISPRUDENCIA ou 19_JURISPRUDENCIA.**

Raízes de referência: `updater/saida/19_JURISPRUDENCIA`. Diretórios no domínio/candidatos do inventário: 20. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Documento único para build, IDX, saneamento e auditoria. Risco: **ALTO**. Alternativa: Resolver documento por logical_id e snapshot; ambiguidades de basename devem falhar, preservando a recusa atual de seleção arbitrária.

**D10 — Enumerar build e staging temporário para cópia/verificação.**

Raízes de referência: parametrizadas por execução. Diretórios no domínio/candidatos do inventário: 0. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Conjunto publicado, checksums e teste de determinismo. Risco: **MEDIO**. Alternativa: RELEASE_MANIFEST fechado e lista de outputs do build; diretórios temporários são parâmetros da execução, não fontes descobertas.

**D11 — Validar árvore de implantação, textos catalogados, órfãos e referências.**

Raízes de referência: `updater/saida`. Diretórios no domínio/candidatos do inventário: 0. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Plano de implantação/validação; parâmetros cartao/saida variam. Risco: **ALTO**. Alternativa: Perfil SD explícito por release, manifest de distribuição e índice de paths; SD não acessado nesta análise.

**D12 — Selecionar pastas EXT_* e um TXT por norma no pacote de correlatas.**

Raízes de referência: `LEX-MACHINAETAPA_2E41/etapa2e4_work/saida/PACOTE_FUSAO_CF_2E4`, `LEX-MACHINA_ETAPA_2E6_SD_TESTE`. Diretórios no domínio/candidatos do inventário: 20. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: 20 normas externas do pacote de teste, índices e hashes. Risco: **ALTO**. Alternativa: Pacote de correlatas com lista de 20 membros e entrada --pacote resolvida por release; não confundir com as 72 normas do menu.

**D13 — Enumerar fixtures temporárias ou procurar artefatos proibidos.**

Raízes de referência: parametrizadas por execução. Diretórios no domínio/candidatos do inventário: 3. O JSON distingue resolução exata e parametrizada por chamada; domínio local não equivale a resultado de runtime.

Consumo: Asserções de teste; não são seleção de datasets produtivos. Risco: **BAIXO**. Alternativa: Fixture manifest explícito; preservar testes negativos contra arquivos extras.

### Locais precisos de enumeração

Cada linha herda finalidade, diretórios encontrados, consumo, risco e alternativa do grupo acima. O JSON guarda expressão e contexto por chamada; o inventário de seletores permite revisar falsos positivos.

| Arquivo:linha | Função | Padrão/mecanismo | Grupo |
|---|---|---|---|
| `CF_SEGMENTADA_V2/test_segmentacao_cf_v2.py:10` | `tree` | `rglob('*')` | D06 |
| `CF_SEGMENTADA_V2/test_segmentacao_cf_v2.py:15` | `main` | `glob('*.json')` | D06 |
| `CF_SEGMENTADA_V2/test_segmentacao_cf_v2.py:18` | `main` | `glob('*.json')` | D06 |
| `CF_SEGMENTADA_V2/test_segmentacao_cf_v2.py:40` | `main` | `rglob('*.IDX')` | D06 |
| `CF_SEGMENTADA_V2/test_segmentacao_cf_v2.py:40` | `main` | `rglob('*.idx')` | D06 |
| `LEX-MACHINAETAPA_2E5/etapa2e5_work/gerar_indice_esp32_v6.py:2458` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:71` | `main` | `iterdir()` | D12 |
| `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:78` | `main` | `glob('*.txt')` | D12 |
| `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:144` | `main` | `glob('EXT_*/*.txt')` | D12 |
| `LEX_MACHINA_REFERENCIAS_V2/05_COMPILADOR/r1d1_pipeline.py:71` | `freeze` | `rglob('*')` | D04 |
| `LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/consolidate_labels.py:56` | `build` | `glob('LEX_MACHINA_REFERENCIAS*')` | D01 |
| `LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/consolidate_labels.py:56` | `build` | `rglob('*.json')` | D01 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/editorial_enriquecimento_v1.py:4` | `src` | `glob(f'{n:03}_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/editorial_enriquecimento_v1.py:18` | `dec` | `glob(f'{n:03}_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/enriquecer_v1.py:23` | `baseline` | `rglob('*')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/enriquecer_v1.py:28` | `baseline` | `rglob('*.IDX')` | D02 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/enriquecer_v1.py:30` | `baseline` | `glob('CATALOGO_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/estado_retomada.py:40` | `main` | `glob('LOTE_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/estado_retomada.py:43` | `main` | `glob('LOTE_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/gerar_relatorios.py:312` | `<module>` | `glob('*.json')` | D10 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/gerar_relatorios.py:313` | `<module>` | `glob('CATALOGO_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/relatorios_enriquecimento_v1.py:25` | `<module>` | `glob('CP_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/relatorios_enriquecimento_v1.py:27` | `<module>` | `glob('*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/relatorios_enriquecimento_v1.py:105` | `<module>` | `glob('*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py:116` | `main` | `glob('*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py:136` | `main` | `glob('*')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/08_MANIFEST/gerar_manifest.py:50` | `<module>` | `rglob('*')` | D02 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/08_MANIFEST/gerar_manifest.py:54` | `<module>` | `rglob('*')` | D03 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/08_MANIFEST/gerar_manifest.py:80` | `<module>` | `rglob('*')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/08_MANIFEST/gerar_manifest.py:88` | `<module>` | `glob('CATALOGO_*.json')` | D05 |
| `LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/finalize_r1d.py:34` | `run` | `rglob('*')` | D04 |
| `LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/release_r1d1.py:221` | `main` | `rglob('*')` | D04 |
| `LEX_MACHINA_REFERENCIAS_V2/tests/test_expansion_r1b.py:108` | `test_26_no_rc_or_idx` | `rglob('*.IDX')` | D13 |
| `LEX_MACHINA_REFERENCIAS_V2/tests/test_expansion_r1b.py:109` | `test_26_no_rc_or_idx` | `iterdir()` | D13 |
| `updater/auditar_8_suspeitas.py:258` | `inventariar` | `rglob('*')` | D08 |
| `updater/auditar_8_suspeitas.py:364` | `localizar_backups` | `glob('catalogo_mestre_*')` | D07 |
| `updater/auditar_8_suspeitas.py:384` | `localizar_backups` | `rglob('*')` | D07 |
| `updater/auditar_acervo_geral.py:97` | `inventariar_saida` | `walk(PASTA_SAIDA)` | D08 |
| `updater/auditar_acervo_geral.py:321` | `pastas_raiz` | `iterdir()` | D08 |
| `updater/auditar_catalogo_mestre.py:153` | `inventariar` | `rglob('*')` | D08 |
| `updater/auditar_integridade_72.py:223` | `inventariar` | `rglob('*')` | D08 |
| `updater/auditar_integridade_72.py:284` | `localizar_backup` | `glob('catalogo_mestre_*')` | D07 |
| `updater/auditar_integridade_72.py:292` | `localizar_backup` | `rglob('*')` | D07 |
| `updater/auditar_vademecum_completo.py:207` | `inventariar` | `walk(origem)` | D08 |
| `updater/auditar_vademecum_completo.py:358` | `pastas_principais` | `iterdir()` | D08 |
| `updater/auditar_vigencia_5.py:263` | `inventariar` | `rglob('*')` | D08 |
| `updater/auditar_vigencia_72.py:362` | `inventariar` | `rglob('*')` | D08 |
| `updater/auditoria_final_saida.py:258` | `localizar_arquivo` | `rglob(nome_arquivo)` | D09 |
| `updater/auditoria_final_saida.py:583` | `auditar_orfaos` | `rglob('*.txt')` | D09 |
| `updater/baixar_prioridade_a.py:198` | `inventariar` | `rglob('*')` | D08 |
| `updater/baixar_prioridade_b.py:198` | `inventariar` | `rglob('*')` | D08 |
| `updater/baixar_prioridade_c.py:198` | `inventariar` | `rglob('*')` | D08 |
| `updater/comparar_catalogo_mestre.py:140` | `inventariar` | `rglob('*')` | D08 |
| `updater/construir_lexdata_oficial_v2.py:3519` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/construir_lexdata_oficial_v2.py:3612` | `publicar_build` | `rglob('*')` | D10 |
| `updater/construir_lexdata_oficial_v2.py:3620` | `publicar_build` | `rglob('*')` | D10 |
| `updater/construir_lexdata_oficial_v3.py:3955` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/construir_lexdata_oficial_v3.py:4048` | `publicar_build` | `rglob('*')` | D10 |
| `updater/construir_lexdata_oficial_v3.py:4056` | `publicar_build` | `rglob('*')` | D10 |
| `updater/construir_lexdata_oficial_v4.py:4291` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/construir_lexdata_oficial_v4.py:4384` | `publicar_build` | `rglob('*')` | D10 |
| `updater/construir_lexdata_oficial_v4.py:4392` | `publicar_build` | `rglob('*')` | D10 |
| `updater/diagnosticar_artigos.py:185` | `inventariar` | `rglob('*')` | D08 |
| `updater/gerar_indice_esp32.py:831` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/gerar_indice_esp32_v3.py:403` | `inventariar` | `rglob('*')` | D08 |
| `updater/gerar_indice_esp32_v3.py:1487` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/gerar_indice_esp32_v4.py:1877` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/gerar_indice_esp32_v5.py:2229` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/gerar_indice_esp32_v6.py:2458` | `localizar_jurisprudencia` | `rglob(arquivo)` | D09 |
| `updater/gerar_indices_binarios_v1.py:469` | `verify_copy` | `rglob('*')` | D10 |
| `updater/gerar_indices_binarios_v1.py:470` | `verify_copy` | `rglob('*')` | D10 |
| `updater/implantar_sd.py:86` | `validar_destino` | `rglob('*.txt')` | D11 |
| `updater/implantar_sd.py:136` | `arquivos_catalogados` | `rglob(arquivo)` | D11 |
| `updater/implantar_sd.py:156` | `auditar_orfaos` | `rglob('*.txt')` | D11 |
| `updater/implantar_sd.py:239` | `validar_referencias.existe_na_arvore` | `rglob(arquivo)` | D11 |
| `updater/implantar_sd.py:254` | `validar_referencias` | `rglob('*.txt')` | D11 |
| `updater/implantar_sd.py:298` | `validar_referencias` | `glob('*.txt')` | D11 |
| `updater/main.py:1702` | `inventariar_vademecum` | `rglob('*')` | D08 |
| `updater/main_v1_before_acordaos_precedentes.py:1684` | `inventariar_vademecum` | `rglob('*')` | D08 |
| `updater/restaurar_3_confirmados.py:78` | `encontrar_backups` | `glob('catalogo_mestre_*')` | D07 |
| `updater/restaurar_3_confirmados.py:95` | `encontrar_backups` | `rglob('*')` | D07 |
| `updater/sanear_saida.py:253` | `localizar_copias` | `rglob(nome_arquivo)` | D09 |
| `updater/test_implantar_sd.py:89` | `test_backup_e_copia_atomica_preservam_lei` | `rglob('*.lex-novo')` | D13 |

O monitor global `gerar_manifest.py:54` registra arquivos alterados fora da missão por mtime. É diferente de selecionar entradas. Reexecutá-lo com a data da missão antiga não é um gate válido para futuras mudanças documentais. A prova original permanece intacta.

### Navegação no firmware, separada do repo

No sketch atual há quatro `openNextFile`: `indexarCaminhosJurisprudencia:1269`, `localizarArquivoRecursivo:1474`, `primeiroTXTDaPasta:1498` e `carregarPastas:1529`. Há prefixos de nomes para categorias e fallback recursivo por basename. Esses mecanismos percorrem o **SD**, não árvores LEX_MACHINA_REFERENCIAS no PC. O exportador deve manter o layout compatível; não é necessário mudar esse firmware para organizar o repositório. O SD não foi acessado.

## Auditoria dos 171 registros absolutos

| Categoria | Registros entre os 122 ativos |
|---|---:|
| ESSENCIAL_RUNTIME | 0 |
| TESTE | 0 |
| MANIFEST | 121 |
| PROVENIENCIA | 0 |
| RELATORIO | 0 |
| PIPELINE_BUILD | 1 |
| OUTRO | 0 |

**121 MANIFEST:** entradas de IDX históricos no `BASELINE_ENRIQUECIMENTO_V1.json`, em 15 pastas históricas. O baseline completo tem 132 externos: 130 IDX, firmware e catálogo 69; os nove IDX fora dessas pastas e os dois outros artefatos não integram os 121 registros-alvo da Onda 2A. São referências de prova/custódia. Não há evidência estática de que a lista externos seja um seletor de runtime do ESP32; os verificadores P545/IDX continuam impondo preservação de paths.

**1 PIPELINE_BUILD:** `montador_sd/montar_sd_teste_relations_v2.py:46` fixa o pacote 2E41 como default de `--pacote`. Pode futuramente receber um argumento resolvido pelo lock sem editar a cópia congelada. Mover o pacote hoje quebraria a invocação padrão.

Os **49 restantes** são receitas históricas, proveniência e relatórios. Cada registro foi mantido e classificado no JSON. Receita de reprodução pode exigir ajuste; simples menção histórica não prova dependência de runtime. Zero em ESSENCIAL_RUNTIME refere-se somente a esses 122 registros, não a todos os caminhos fixos existentes.

## Protected545: regra atual e política futura

545 entradas contêm path, bytes, sha256. Leitor monta ROOT.parent/path e calcula hash; hash igual em outro lugar não satisfaz esse leitor. Os bytes/tamanho são evidência adicional; o verificador atual confere existência/hash e cardinalidade, sem tornar path dispensável.

A resposta é **E: combinação de B + C + D**. `r1d_support.integrity:39–40` lê files e faz `file_hash(ROOT.parent / path)`; `r1d1_pipeline.integrity` agrega esse gate. Não basta encontrar bytes iguais em outro diretório. Manifests também apontam para fontes e provas encadeadas.

- Não reescrever/recalcular para substituir INTEGRITY_BEFORE nem chamar a migração de mesma prova original.
- Criar prova derivada versionada que fixa hash do manifest original e todas as 545 ocorrências.
- Para cada ocorrência exigir identidade lógica, path histórico, hash/size esperados, locator novo, origem e vínculo da transação. Verificar completude, unicidade de mapeamento e ausência de conteúdo substituído.
- Preservar cápsulas históricas inteiras com fechamento das dependências e plano de restauração aos paths originais. Testar restauração/verificação em ambiente isolado antes de mover qualquer unidade.
- O verificador legado no checkout atual continuará exigindo paths originais. Só uma política nova explicitamente aprovada pode tornar a prova derivada gate operacional; a antiga permanece reproduzível pela restauração.
- Não usar symlinks/junctions como prova de equivalência nem usar Git normalizado como única cópia de bytes CRLF congelados.

**Decisão necessária em etapa futura:** aprovar explicitamente uma nova política operacional de integridade. Um novo manifest sozinho não modifica a obrigação vigente. Nunca declarar que o verificador legado continua passando no checkout reorganizado se os paths que ele lê deixaram de existir. A prova derivada e a prova original restaurada devem ser distinguidas por nome, escopo e evidência.

## Identidade por conteúdo e localização

Chave lógica: `logical_id + version`; identidade dos bytes: `sha256 + size_bytes`; cada ocorrência histórica mantém `occurrence_id`. Locators (`storage_root_id + relative_path`) e paths históricos são metadados versionados. Um hash pode aparecer em muitos papéis; isso não autoriza deduplicação nem colapso de votos humanos.

- Hash de bytes brutos; nunca normalizar newline, acentos ou codificação dos congelados.
- Mesmo logical_id/version com hash diferente é erro; novo conteúdo exige nova versão, nunca substituição silenciosa.
- Hashes iguais podem ter papéis/proveniências distintos; não colapsar evidências ou votos humanos.
- Localização pode mudar apenas por ledger append-only aprovado; conteúdo e lineage permanecem imutáveis.
- IDs sem path/drive; locators relativos a storage roots aprovados. Rejeitar traversal, escape por links, ambiguidades casefold/Unicode e colisões de destino.
- Não inferir ativo de maior versão, pasta recente, nome ou presença de arquivo.
- Referências por hash comprovam identidade dos bytes, não autoridade da fonte nem verdade jurídica.

Vantagens: seleção explícita, portabilidade, auditoria de dependências e movimentos controlados. Desvantagens: mais metadados, regras de atualização, resolvedor e testes; hash não comprova qualidade semântica. Risco principal: duas versões lógicas ou proveniências distintas serem indevidamente tratadas como uma. Compatibilidade V2: manter congelados intactos e adaptar apenas nova linha de tooling. Updater passa a resolver locks; ESP32 recebe a mesma árvore de distribuição.

## Registry e manifests propostos — não criados

| Documento conceitual | Responsabilidade |
|---|---|
| ARTIFACT_REGISTRY.v1.json | Todos os artefatos: logical_id, papel/função, versão, hash/bytes, paths atual/histórico, dataset, source, provenance, status, dependencies e regeneração. |
| ACTIVE_DATASET_LOCK.v1.json | Profile exato: fontes autorizadas, ordem, versões/hashes e fechamento das dependências. Nenhum wildcard ou latest. |
| RELEASE_MANIFEST.v1.json | Conjunto distribuído ao SD: path relativo, formato/encoding, hash/bytes, entradas, gerador/config e firmware/profile compatível. |
| LEGACY_RELOCATION_LEDGER.v1.json | Trilha append-only aprovada entre cada ocorrência/path histórico e local de custódia; ancora o manifest original por hash. |

Estados: candidato, ativo por profile, histórico e rejeitado são explícitos. Ser catalogado não ativa um dataset. REFERENCIAS da V2 continua isolada; ENTENDA fica não implementado/não aprovado. Roles de avaliação e holdout não podem entrar nas features do compilador. Lock ordenado substitui a seleção implícita de fontes, mas preserva primeiro a semântica comprovada da seleção anterior.

O JSON deste plano contém apenas um exemplo não funcional (`execution_enabled=false`, IDs/hashes não preenchidos). Não existe ACTIVE_DATASET_LOCK operacional nesta entrega.

## Fontes únicas e proveniência

Capturas oficiais únicas aparecem em 15 pastas segundo a classificação existente; isso não significa cobertura integral. Separar metadados de proveniência e custódia dos bytes. Capture_id liga raw_sha256, URL canônica, data de coleta, publisher, request sanitizado, media type, encoding, extrator, localizador e derived_from.

- Capturas são snapshots imutáveis. URL ao vivo não substitui captura nem prova reprodução exata.
- Metadados públicos sanitizados e bytes restritos separados; preservar original sob custódia. Não copiar BUSCA_118.json para Git ou registry público.
- Se fonte única for necessária, criar futuramente custódia verificável de captura e metadados; até lá pasta não é liberada.
- Para manter a versão histórica inteira, registrar a captura em um volume de proveniência ou como membro endereçável de cápsula histórica completa. Eventual exportação é cópia autorizada, nunca extração destrutiva da única unidade.
- Manifest de origem liga cada derivado às capturas e localizadores usados. Sem prova de cobertura, classificação permanece manual.
- Mudança remota gera nova captura e revisão; não sobrescrever snapshot antigo.

Essa separação permite que o pipeline dependa de capturas identificadas, sem exigir a pasta de etapa na raiz operacional. A versão histórica ainda deve ir **inteira** para custódia quando aprovada. Uma cópia futura da fonte ativa ou leitura de membro da cápsula não permite apagar o original único ou desmontar a pasta.

## Política dos 130 IDX

| Questão | Proposta |
|---|---|
| distribuicao | SIM: membros de uma release SD fechada, não necessariamente todas as 130 cópias históricas. |
| gerados | SIM, existem geradores; manter os snapshots atuais. |
| versionados | Manifests e geradores versionados. Binários em armazenamento de release/snapshot verificado; política atual IDX_SNAPSHOT_APENAS permanece. |
| reproduziveis | NÃO COMPROVADO byte a byte para todos; rede/fontes mutáveis impedem presumir. Gate futuro exige entradas congeladas, toolchain/config e paridade. |
| manifestados_hash | SIM, hash/bytes por ocorrência e release; proibir mistura de índices e textos de builds distintos. |
| associados_norma | Snapshot da norma + camada + versão/formato do índice; índices globais/lookup associam-se ao manifest de todo o corpus, não a uma única norma. |

Offsets dependem dos bytes/encoding/fins de linha do texto e do layout. Tratar 130 ocorrências != 130 normas. Gerador binário registra MAGIC LEXART01, versão 1 e struct little-endian; outros IDX são texto delimitado e exigem seus próprios formatos.

O inventário registra 17 hashes distintos para 130 ocorrências. A distinção serve à auditabilidade, não a uma ordem de deduplicação. Há índices textuais de jurisprudência/correlatas e binários de artigos; cada formato requer contrato próprio. A release deve ligar índices globais ao conjunto de normas e cada índice específico ao snapshot textual e aos bytes que seus offsets referenciam.

## Preparação para 72 normas, ENTENDA e atualização

Modelar `norm_id` estável, `text_snapshot_id` e versões independentes das camadas legislação seca, correlatas, jurisprudência, referências, ENTENDA, dicionário, IDX e proveniência. O gerador já declara EXPECTED_NORMS=72; o futuro lock deve enumerar os 72 IDs e as camadas habilitadas. As 20 normas externas do pacote de correlatas e as 130 cópias IDX são cardinalidades diferentes.

ENTENDA será uma camada editorial opcional ligada à norma/dispositivo, ao snapshot de texto, fontes, versão e revisão. Dicionário terá termo/sentido/versionamento e ligações explícitas. Nenhum conteúdo ENTENDA ou jurídico foi gerado. Atualização automática deverá criar nova captura/candidata e diff; validações e revisão promovem um lock/release, sem sobrescrever a última release verificada.

Estrutura conceitual de desenvolvimento (não criada):

```text
registry/
datasets/<dataset_id>/<version>/
sources/<capture_id>/
provenance/
pipelines/
runs/<run_id>/inputs.lock + outputs.manifest
releases/<release_id>/sd/
[custódia externa]/historical_units/<unit_id>/
```

Execuções novas ficam em runs; ambientes e caches são infraestrutura, não identidade de dataset. Não criar uma árvore de etapa na raiz a cada execução.

## Desenvolvimento versus SD/ESP32

O host gerencia registry, proveniência, validação, captura, build e histórico. O SD recebe uma árvore fechada de release. O primeiro exportador futuro deve preservar paths, bytes/encoding, índices e formatos que o firmware já consome, incluindo nomes/categorias de jurisprudência e correlatas. O registry completo não precisa caber na RAM do ESP32. Otimização de layout ou firmware é uma release separada, com teste de memória/latência/hardware e autorização; não é pré-requisito para desacoplar o repo.

## Migração em checkpoints reversíveis

A sequência privilegia catálogo e comparação sombra. Dual-read significa duas resoluções comparadas, nunca mistura de resultados nem dupla contagem de evidências. Nenhuma etapa abaixo foi executada.

### A — Especificação e catálogo sombra

Criar futura versão de registry somente descritiva com roots e schema; sem alterar leitores.

**Gate/testes:** Schema, unicidade logical_id/version, cobertura e ausência de dados sensíveis.

**Rollback:** Descartar a referência ao registry sombra; checkout funcional intacto.

**Evidência/checkpoint:** Schema/documento e hash do catálogo sombra. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

### B — Paridade de descoberta

Capturar em ambiente isolado conjuntos e ordem da descoberta antiga; comparar lock proposto, incluindo exclusões e multiplicidades.

**Gate/testes:** 35 árvores/205 JSON candidatos/55 marcadores como observação inicial, fontes efetivamente aceitas, ordens, IDs e hashes; missing/extra/reorder devem falhar.

**Rollback:** Manter leitor legado como único autoritativo.

**Evidência/checkpoint:** Diff de cobertura e hash do lock; sem regenerar Engine/RC/holdout. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

### C — Resolvedor em shadow mode

Tooling novo resolve lista explícita em paralelo para comparação, sem unir datasets nem trocar produção.

**Gate/testes:** Comparar manifest/bytes selecionados, casos de nome duplicado, ausência, case, encoding, traversal e arquivo estranho na raiz.

**Rollback:** Desabilitar shadow; preservar leitor e artefatos antigos.

**Evidência/checkpoint:** Relatório de paridade, versão do resolvedor e testes de falha. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

### D — Build paralelo de distribuição

Perfil explícito do updater gera pacote isolado a partir de entradas congeladas, após autorização de implementação.

**Gate/testes:** Hash/bytes e offsets de textos/IDX, formatos/menu/paths, 72 normas e camadas habilitadas; nada gravado no SD.

**Rollback:** Descartar seleção do pacote candidato, reter última release verificada.

**Evidência/checkpoint:** RELEASE_MANIFEST e comparação de artefatos; eventuais divergências justificadas, não aceitas silenciosamente. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

### E — Autoridade explícita em novo tooling

Selecionar lock autoritativo por profile; sem fallback para glob e sem editar V2 congelada.

**Gate/testes:** Entrada desconhecida ou nova pasta na raiz não altera build; hash faltante aborta; paridade aprovada.

**Rollback:** Voltar atomicamente à seleção/versionamento anterior; não unir old/new.

**Evidência/checkpoint:** Checkpoint de ativação do profile e plano de rollback. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

### F — Prova derivada e custódia do legado

Projetar/implementar futuramente, com aprovação específica, ledger das 545 ocorrências e cápsulas completas verificadas.

**Gate/testes:** Verificar closure de fontes únicas, IDX, referências e provas; ensaio de restauração aos paths originais; guard antigo funciona no estado restaurado.

**Rollback:** Não mover se falhar; se política já ativada, reativar gate original com árvore restaurada verificada.

**Evidência/checkpoint:** Manifest original intacto, ledger, hashes de custódia, prova derivada e ata de aprovação. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

### G — Revisão de elegibilidade e arquivamento

Somente depois de E/F, repetir elegibilidade dirigida por pasta; arquivar lotes inteiros com autorização.

**Gate/testes:** Sem consumidores implícitos, perda de proveniência/únicos ou alteração SD; destino/hash/custódia conferidos por lote.

**Rollback:** Restaurar a unidade inteira, locators e lock anterior; nenhuma versão parcialmente desmontada.

**Evidência/checkpoint:** Commit e checkpoint por lote; registro de origem/destino/validação. Nenhum lote liberado por esta missão. Commit local dedicado ao concluir a etapa; registrar hashes e estado, sem push automático.

## Riscos e critérios de sucesso

| Risco | Controle |
|---|---|
| Mudança da seleção/ordem contamina ledger ou altera source IDs | Comparar lista ordenada, multiplicidade, rejeições e origem; não unir old/new; avaliação isolada do compilador. |
| Confundir hash igual com papel/proveniência igual | occurrence_id e papel separados; não deduplicar votos/capturas por hash. |
| Reescrever prova frozen para ocultar deslocamento | Manifest antigo imutável e prova derivada nomeada; política explícita e restauração validada. |
| Atualização remota muda o texto e invalida IDX | Capture novo snapshot, revisão e release atômica com hash de entradas/textos/índices. |
| Registry aponta fora da custódia ou omite fonte única | Roots aprovados, anti-traversal, completude de closure, hashes e custódia integral por unidade. |
| Renomear/mover altera encoding/CRLF ou colisões Windows | Identidade de bytes brutos, mapeamento histórico preservado e teste casefold/Unicode. |
| Sobrecarga no ESP32 e quebra de layout | Manifests completos no host; exportador mantém paths e formatos atuais; limites de memória/latência testados em etapa própria. |

Sucesso exige: lista autorizada exata e determinística; nenhuma alteração por pasta extra na raiz; completude das dependências; paridade de hashes/ordem/IDs; falha em fontes ausentes, ambíguas ou alteradas; segregação de avaliação/holdout; provas antigas intactas; custódia e restauração testadas; release SD compatível; rollback por checkpoint. Testes de arquitetura foram apenas especificados, não executados como pipelines.

## Potencial de liberar legado

| Grupo da Onda 2A | Potencial condicionado | Evidência/limite |
|---|---|---|
| 55 bloqueadas P545 | 52 MÉDIO; 3 BAIXO | 52 unidades históricas podem ser candidatas após prova derivada e fechamento de dependências. CF_SEGMENTADA_V2, J4 e firmware v7.12 têm papel ativo/baseline: não se presume que devam sair. |
| 17 após ajuste | 17 MÉDIO | Caminhos de receitas/consumo e custódia dos únicos precisam ser resolvidos; registry sozinho não basta. |
| 8 revisão manual | 8 DESCONHECIDO | Seis pastas com capturas únicas, schema J1 e resultados únicos 2E3; depende de revisão/proveniência. |

**Pastas liberadas por esta missão: zero.** Os números descrevem classes com evidência da Onda 2A, não estimam quantas acabarão arquivadas. Não há promessa de recuperar 2,9 GB: arquivo no mesmo disco não é economia física. A pasta de 49 KB já elegível permanece parada por decisão do usuário.

## Quando a Onda 2B poderá ser liberada

- Migração de implementação explicitamente autorizada e concluída nos checkpoints aplicáveis.
- Registry/lock autoritativo validado sem alterar entradas/ordem/features/labels da V2 congelada.
- Capturas e conteúdo único com custódia completa, provenance e prova de restauração.
- Nova política P545 aprovada quando houver mudança de paths; prova histórica original preservada e reconstruível.
- IDX/textos/firmware e perfil SD compatíveis, hashes e dependências fechados.
- Revisão dirigida de cada pasta inteira e nova autorização por lote; nenhuma liberação automática por contagem ou potencial.

## Verificação desta entrega

**Integridade final: PASSA.** Protected545: **545/545**; IDX: **130/130**; congelados V2: **281/281**; firmware e catálogo 69 idênticos aos hashes de referência. Engine/RC1/RC2/holdout/ontologia, pacote enriquecido, snapshot e bundle também passaram nas verificações de integridade. A Engine não foi executada. O JSON registra o resultado detalhado de `_concluir_onda0.verify`, usado somente para leitura e hashes; nenhuma rotina de pipeline foi executada.

Os **28.846 arquivos preexistentes** mantêm tamanho e mtime, sem exclusões nem alterações detectadas. As únicas adições são WAVE2C_DECOUPLING_PLAN.md e WAVE2C_DECOUPLING_PLAN.json. A comparação global de metadados não substitui hashes de todo o legado; os hashes constitucionais foram verificados separadamente, sem refazer a auditoria. O diff de arquivos rastreados e o índice estavam vazios antes do staging seletivo. Apenas esses dois documentos são permitidos no commit. Scripts auxiliares permanecem no diretório temporário.

Commit local solicitado: `docs: plan legacy decoupling architecture`. Tag local solicitada: `pre-legacy-decoupling-2026-09-27`. Sem push.

**Próximo passo:** revisar a arquitetura e a política de integridade derivada; eventual implementação da migração exige uma missão autorizada própria.

ONDA_2C_PLANEJADA — AGUARDANDO_REVISAO
