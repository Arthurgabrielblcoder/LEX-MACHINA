# MACRO08 — AUDITORIA ESTRUTURAL DO ADCT

Lote `ENTENDA_CF_MACRO_BATCH_08` · data de referência 2026-10-05 · gerado por `build_entenda_macro_segment.py` (determinístico, só conteúdo versionado).

**Decisão:** ADCT_PROCESSABLE (texto oficial versionado; lacuna era de targetizacao/status/leitor, resolvida pelo perfil generico).

## Respostas

**1. O ADCT ja possui targets estruturais?**

Sim. O indice canonico CF88_TARGET_INDEX.json ja tinha 961 targets do namespace ADCT (fonte estrutural legada cf.txt), mas 812 estavam UNKNOWN_VALIDITY e o texto vinha da compilacao multivigente. O perfil CF88_OFFICIAL_RUNTIME usa 891 targets do runtime oficial e mantem 72 targets so legados como HISTORICAL_ONLY.

**2. Qual e o norma_id real?**

CF88 (campo norma_id dos targets); o ADCT e o subnamespace 'ADCT' com parent 'CF88' (LEGAL_TARGET_ID/namespaces.json; source_marker 'ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS').

**3. Qual e a gramatica real dos IDs?**

ADCT:ART.<n>[-<LETRA>][:CAPUT | :PAR.<n>[-<LETRA>] | :PAR.UNICO][:INC.<romano>[-<LETRA>]][:AL.<letra>] (LEGAL_TARGET_ID/target_id.py). Exemplos do indice: ADCT:ART.2:PAR.1, ADCT:ART.10:INC.II:AL.b, ADCT:ART.18-A, ADCT:ART.21:PAR.UNICO, ADCT:ART.76-B.

**4. O ADCT esta dentro de CF88 ou e norma separada?**

Dentro de CF88: namespace proprio (ADCT:ART.5 nao colide com CF88:ART.5), mesma norma e mesmo indice. Nenhum namespace novo foi criado.

**5. Quantos artigos estruturais existem?**

148 artigos (10 com letra: 18-A, 54-A, 60-A, 76-A, 76-B, 92-A, 92-B, 107-A, 111-A, 116-A); 814 dispositivos abaixo do artigo; tipos: {'ALINEA': 71, 'ARTIGO': 148, 'CAPUT': 148, 'INCISO': 272, 'NAMESPACE': 1, 'PARAGRAFO': 286, 'PARAGRAFO_UNICO': 37}.

**6. Quantos estao vigentes/operativos?**

Status do texto: 138 artigos com texto vigente na compilacao monovigente. Camada temporal editorial: {'EFFECT_EXHAUSTED': 26, 'EXTERNAL_STATUS_REQUIRED': 22, 'NAO_CLASSIFICADO': 75, 'OPERATIVE_CURRENT': 8, 'OPERATIVE_TRANSITION': 2, 'PARTIALLY_OPERATIVE': 5, 'REVOKED': 10}.

**7. Quantos estao revogados?**

10 artigos com caput apenas '(Revogado)': 91, 106, 107, 108, 109, 110, 111, 111-A, 112, 114; dispositivos revogados: 49.

**8. Quantos possuem efeitos temporais ja exauridos?**

26 artigos classificados EFFECT_EXHAUSTED (prova pelo texto e pela data de promulgacao versionada); 5 parcialmente operantes; 0 com marco futuro.

**9. Existem lacunas ou erros de segmentacao?**

Runtime x indice legado: 72 targets so legados (redacoes revogadas ou renumeradas), 2 so do runtime (ADCT:ART.77:INC.I:AL.a, ADCT:ART.77:INC.I:AL.b, diferenca revisada em TARGET_DIFF_REVIEWED.json). Sanity: {'REPEATED_LABEL': 1} (ver MACRO08_SOURCE_ANOMALIES).

**10. E possivel reconstrui-lo integralmente apenas com conteudo versionado?**

Sim. Fonte oficial travada (SOURCES_LOCK: Senado 604119, raw 2e7bf19d5951..., normalizado 887617267a64...), runtime da Lei Seca versionado (7ef82290d30f...) e perfil gerado com prova de ida e volta: PASS (742 textos).

## Representação

| Item | Valor |
|---|---|
| Namespace / parent | `ADCT` / `CF88` |
| norma_id | `CF88` |
| Fonte oficial | Senado 604119 · `ADCT/16434816_2e7bf19d` · normalizado `887617267a648ccc…` |
| Runtime da Lei Seca | `DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt` · `7ef82290d30f4af1…` |
| Leitor legado (config global) | `updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt` · 961 targets, 812 UNKNOWN_VALIDITY |
| Perfil usado no lote | `CF88_OFFICIAL_RUNTIME` · origem dos targets {'LEGACY_STRUCTURAL_ONLY': 72, 'OFFICIAL_RUNTIME': 891} |
| Artigos / com letra | 148 / 10 |
| Targets / tipos | 963 / {'ALINEA': 71, 'ARTIGO': 148, 'CAPUT': 148, 'INCISO': 272, 'NAMESPACE': 1, 'PARAGRAFO': 286, 'PARAGRAFO_UNICO': 37} |
| Status dos artigos | {'CURRENT': 138, 'REVOKED': 10} |
| Camada temporal | {'EFFECT_EXHAUSTED': 26, 'EXTERNAL_STATUS_REQUIRED': 22, 'NAO_CLASSIFICADO': 75, 'OPERATIVE_CURRENT': 8, 'OPERATIVE_TRANSITION': 2, 'PARTIALLY_OPERATIVE': 5, 'REVOKED': 10} |
| Decisões | {'EXCLUDED_HISTORICAL': 3, 'EXCLUDED_REVOKED': 7, 'NAO_DECIDIDO': 75, 'SELECT': 22, 'SKIP_APPROVED_PILOT_LEGACY_MODEL': 1, 'SKIP_CONSUMED_CONSTITUTIVE_ACT': 4, 'SKIP_EXHAUSTED_TRANSITION': 21, 'SKIP_RESIDUAL_PERSONAL_TRANSITION': 8, 'SKIP_TRANSITION_EVENT_DEPENDENT': 7} |

## Blocos do ADCT

Regra: blocos de ~25-35 artigos estruturais, determinados pela estrutura real (148 artigos; 831 targets CURRENT): fronteiras por numero de artigo, equilibrando targets (147/171/164/151/196)

| Bloco | Artigos | Intervalo | Targets vigentes |
|---|---|---|---|
| MACRO_08_D | 31 | 1–30 | 147 |
| MACRO_08_E | 32 | 31–60 | 173 |
| MACRO_08_F | 32 | 61–90 | 164 |
| MACRO_08_G | 29 | 91–115 | 151 |
| MACRO_08_H | 24 | 116–138 | 196 |

## Conflito com piloto aprovado

ADCT:ART.10:INC.II (HUMAN_APPROVED_T1) carimbado com o cf.txt legado: ADCT art. 10 fora do lote (SKIP_APPROVED_PILOT_LEGACY_MODEL); BACKLOG

