# Auditoria de acoplamento à CF — pipeline de jurisprudência

```
ESCOPO = JURISPRUDENCE_AUDIT (45 scripts + 9 módulos de revisão), LEGAL_TARGET_ID (gramática, parser, exportadores), firmware (camada juris)
DATA = 2026-10-18 · HOST-ONLY · NENHUM MÓDULO DA CF FOI ALTERADO PARA ESTA AUDITORIA · CF_J2I_BASELINE_REGRESSION = 0
```

**Como foi feita:**
1. Contagem automática de literais acoplados à CF em cada script (`CF88`, `ADCT`, `constituicao.htm`, contagens 261/315, `REF_PAYLOAD`, `ENTENDA`).
2. Leitura dos pontos de decisão.
3. Execução real das ferramentas sobre o Código Civil (piloto, `PORTABILITY_PILOT_CC.md`).

A classificação reflete o que aconteceu no piloto, não só a leitura do código.

## Resumo

| Classificação | Scripts J2 (45) | O que significa |
|---|---:|---|
| `GENERIC_ALREADY` | 3 | Usados como estão em outra norma |
| `CF_SPECIFIC_BUT_PARAMETERIZABLE` | 7 | Basta trocar norma, namespace, pasta ou corpus (perfil ou wrapper) |
| `BLOCKER_FOR_OTHER_NORMS` | 3 | A descoberta depende das recomendações ENTENDA, que só existem para a CF |
| `CF_SPECIFIC_INTENTIONAL` | 32 | Instrumentos de uma rodada física da CF (overlays, candidatos, auditorias de isolamento, deploy, checagens semânticas). Não devem ser generalizados; são trilha histórica |

**Fora do JURISPRUDENCE_AUDIT:**
- **`LEGAL_TARGET_ID`:** a gramática de target e o índice estrutural já são genéricos; o `citation_parser` é parametrizável; os exportadores `build_export_run*` (9) são intencionalmente da CF.
- **Firmware:** é bloqueador para publicar jurisprudência de outra norma (seção 4).

## 1. Já genérico (usar direto em CC, CP, CPC etc.)

| Ferramenta | Evidência |
|---|---|
| `LEGAL_TARGET_ID/target_id.py` | Os namespaces vêm do Catálogo Mestre (72 normas, inclusive `CC2002`, `CPC2015`, `CP1940`, `CPP1941`, `CTN1966`, `CLT1943`). `CC2002:ART.927:PAR.UNICO` valida sem mudança, e `CF88:ART.5` continua igual. **Lacuna:** rejeita alínea sem inciso (`ALINEA_WITHOUT_INCISO`), ver seção 3 |
| `structure_parser.py` + `build_target_index.py` | O índice `CC2002_TARGET_INDEX.json` já existe (5.956 targets, 2.077 artigos). O adaptador do piloto reproduz 3.856 de 3.878 dispositivos; a diferença vem de revogações posteriores ao corpus do aparelho |
| `JURISPRUDENCE_AUDIT/juris_types.py` | Tribunal separado da classe. Rótulos `RG TEMA 809`, `ADI 4815`, `RE 229096` e `Súmula 203 STJ` funcionam sem mudança |
| `j2_auditors.status_signals`, `joint_scope`, `scope_allows` | Sem vocabulário da CF. No piloto, `status_signals` reconheceu 16 de 20 situações processuais; não reconhece "Julgamento: dd/mm/aaaa ... procedente" das ADIs |
| `check_j2b_provisional.py` | Gate temporal sem norma; não exercitado no piloto, que não teve provisórios |
| `j2i_flash_generic_firmware.py` | Flash do app, independente de norma |

## 2. Precisa parametrizar (trocar norma, namespace, pasta ou corpus)

| Ferramenta | Acoplamento | Solução usada no piloto (sem alterar a CF) |
|---|---|---|
| `citation_parser.py` | A CF é a norma de referência: "do Código Civil" volta como `norm = OTHER` | `norm_profiles.citation_granularity`: aceita o rótulo da norma do perfil. **Lacuna de gramática:** "art. 1.641, II" sem a palavra "inciso" dá UNPARSEABLE |
| `j2_auditors.namespace_alerts` | Qualquer norma que não seja a CF dispara alerta (19 de 20 alertas falsos no CC) | `norm_profiles.namespace_check` com marcadores da norma do perfil |
| `j2_auditors.temporal_alerts` | Só reconhece EC e "redação originária" | `norm_profiles.temporal_check`: notas "Redação dada pela Lei ..." do próprio dispositivo (Planalto) × ano do julgamento |
| `j2_review_common.make_decisions` | Namespace fixo `CF88`/`ADCT`; tabela `DEVICE_TYPES` desatualizada (marca ADPF como "não validado", embora a J2I tenha validado) | Não reutilizado no piloto. A correção é pequena (namespace por perfil), mas mexe no validador dos lotes ratificados; fica para missão própria, preservando o `--check` dos Batches 03–10 |
| `build_j2_batch.py` (seleção) | A regra de prioridade é genérica; as entradas (backlog J0, baseline REF_PAYLOAD 261/315) são da CF | A seleção pode receber outra fonte de candidatos; no piloto, a regra de descoberta ficou no `build_pilot_cc.py` |
| `build_j2_provisional_registry.py`, `build_j2_ratification_record.py`, `build_j2_backlog_state.py` | Pastas `J2_*_BACKLOG` e registros J2 | Trocar pastas e prefixo da rodada |
| `render_j2_batch_report.py` | `t()` formata só `CF88:`/`ADCT:` | Formatação por namespace |

## 3. Precisa redesenhar (dependência real)

| Ponto | Por que bloqueia | Dado do piloto |
|---|---|---|
| **Descoberta** (`build_j0_diagnostic_audit`, `build_j2a_batch01`, `build_j2d_batch02`) | O backlog constitucional nasceu das recomendações ENTENDA (`JURISPRUDENCE_LINK_RECOMMENDATIONS.json`), que só existem para a CF | Substituída por dois adaptadores novos: anotações "Vide" do Planalto e busca oficial do STF. O rendimento do Planalto é baixo em todos os códigos: CC 10, CPC 12, CP 11, CPP 66, CTN 5, CLT 71, CE 12 anotações (`PLANALTO_DISCOVERY_YIELD_7_NORMS.json`) |
| **Fonte STJ** | Bloqueio anti-robô nas pesquisas oficiais do STJ (Súmulas 403 e 203 na CF; canal de descoberta do CC). Não contornado | Para CC e CPC, o STJ é o tribunal dominante; sem um adaptador autorizado, a cobertura fica restrita ao STF |
| **Gramática de alínea** (`target_id.py`) | `ALINEA_WITHOUT_INCISO`: na CF, a alínea sempre está sob um inciso; nos códigos, não | CP 26, CPP 43, CTN 31, CLT 406 dispositivos irrepresentáveis; CC, CPC e CE 0. Extensão compatível: aceitar `ART.n:AL.x` e `ART.n:PAR.n:AL.x` só fora da CF |
| **Firmware (camada juris)** | `arquivoAtualPertenceACF()` e `"CF88"` fixos na consulta do `JUR_LOOKUP`; LEXV1 indexa só `CF88_TARGETS.IDX` | O formato de dados já é genérico (`JUR_LOOKUP` tem a coluna `ORIGEM_NORMA`), mas o código não consulta outra norma. Publicar o CC exige mudança de firmware e novo teste físico |

## 4. Não deve ser generalizado (regra constitucional legítima)

- **ADCT:** sub-namespace com pai CF88 (`namespaces.json`); `ADCT:ART.5` nunca colide com `CF88:ART.5`.
- **Política temporal da CF** (J1.4/J2B.1): precedente sobre redação histórica de EC só no nível de artigo. A ideia (alerta temporal) é genérica; o vocabulário (EC) é da CF.
- **Rodadas físicas J1–J2J:** overlays, candidatos, auditorias de isolamento, scripts de deploy e checagens semânticas. Cada um responde a uma rodada específica e é trilha de auditoria. O padrão de processo (candidato host-only → isolamento → ratificação → gate → deploy → teste físico) é que se generaliza, não o código.
- **Camadas congeladas:** CORRELATAS 1, REFERÊNCIAS Nº 4, ENTENDA e J2I_FROZEN_315_198.

## 5. Modelo genérico de target (Fase J)

O motor já trabalha com `NORMA:ART.n[:PAR.n|:PAR.UNICO][:INC.r][:AL.x]`, sem depender de `CF88`, porque os namespaces vêm do catálogo:
- **CF:** `CF88:ART.5:INC.XLIII` e `ADCT:ART.107-A` continuam válidos (compatibilidade obrigatória mantida).
- **Código Civil:** já usa a convenção `CC2002` (índice do aparelho e catálogo); nenhum namespace novo foi inventado.
- **Formato pipe:** `CC2002|927|unico||` sai de `to_pipe_fields` sem mudança.
- **Única extensão necessária, e só para outros códigos:** alínea fora de inciso (seção 3).
