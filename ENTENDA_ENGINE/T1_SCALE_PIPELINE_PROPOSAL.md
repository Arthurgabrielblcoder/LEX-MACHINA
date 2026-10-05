# T1 — PROPOSTA DE PIPELINE ESCALÁVEL (pós-Batch05)

Projeto, **não executado**. Parte do padrão congelado (A6) e da infraestrutura do validador v2. Princípio: **a automação resolve o normal; humanos revisam exceções e risco jurídico real.** Nenhuma autoaprovação está ligada (`T1_PIPELINE_CONFIG.json`). A ativação depende de decisão humana após avaliar a primeira triagem (`derived/production_batch_05/T1_PENDING_TRIAGE_REPORT.md`).

## 1. Fluxo

```
LAW TEXT (runtime aprovado, Lei Seca autoridade)
→ STRUCTURAL TARGETS (LEGAL_TARGET_ID; vigência; históricos/revogados fora)
→ SELECT / SKIP (agressivo; ver § 3)
→ DRAFT T1 (com o checklist A6 embutido no prompt de redação)
→ EDITORIAL CHECKS (editorial_checks.py; achados resolvidos com justificativa)
→ VALIDATOR V2 (t1_validator_v2.py: HARD_FAIL / REVIEW_REQUIRED / AUTO_FIX / INFO)
→ EXTERNAL DEPENDENCY CHECK (T1_EXTERNAL_CATALOG.json: link, contradição, controvérsia resolvida, proveniência)
→ RISK ROUTING (risco temático + achados → filas A/B/C/D/E)
→ MICROAUTO (sugestão de microajuste A6; aplicação só quando MICROAUTO_APPLY=true, sempre registrada)
→ FILAS A/B/C/D/E (formatos compactos; § 4)
→ revisão humana só onde necessário
→ approval (round_approvals; versão imutável)
→ build determinístico (3 builds idênticos; testes do lote)
```

## 2. Unidade de produção

Lotes por **bloco temático coerente**, não por 4–5 artigos. O limite é operacional (tamanho do pacote D e tempo de revisão), não o número de artigos.

| Lote | Escopo | Targets estruturais vigentes | Explicações (alvo) |
|---|---|---|---|
| Batch05 (referência) | arts. 37–41 (Administração Pública e servidores) | 118 | 69 (58%) |
| **Batch06 proposto** | **arts. 42–75**: fecho do Título III (militares dos Estados, regiões) e todo o Capítulo I do Título IV (Poder Legislativo) | **309** (34 artigos, 86 §§, 6 §§ únicos, 127 incisos, 22 alíneas) | **~110–140** (35–45%, com SKIP mais agressivo) |

Sub-blocos para organizar a revisão (não lotes separados):
- arts. 42–43, militares e regiões (17 targets);
- arts. 44–58, estrutura e estatuto dos congressistas (153);
- arts. 59–69, processo legislativo (92);
- arts. 70–75, fiscalização e Tribunais de Contas (47).

Risco temático esperado para a fila D, a confirmar na triagem:
- imunidades (art. 53);
- CPIs (art. 58, § 3º);
- emendas à Constituição e limites materiais (art. 60);
- medidas provisórias (art. 62);
- sanção e veto (art. 66);
- competências do TCU (art. 71).

O catálogo externo deve ganhar entradas apenas quando uma revisão humana as validar.

`hard_cap` do lote: 150. Acima disso, `BATCH_SPLIT_RECOMMENDED`, como hoje.

## 3. SELECT / SKIP mais agressivo

**Criar ENTENDA** quando houver ganho pedagógico real:
- conceitos jurídicos;
- requisitos, exceções, prazos relevantes;
- competências, direitos, sanções, procedimentos;
- regras cobradas em estudo e prova;
- dispositivos cuja leitura seca não é autoexplicativa.

**SKIP** (`NO_SEPARATE_EXPLANATION`):
- dispositivos puramente formais ou autoexplicativos;
- listas cobertas por BLOCK (incisos de competência, rol de matérias);
- remissões simples.

Lei Seca, busca, correlatas, jurisprudência e referências continuam completas para todos os targets, com ou sem ENTENDA.

Estratégia por norma:
- **ENTENDA robusto:** CF, CC, CPC, CP, CPP, CTN, CLT, CDC, LEP, ECA e outras normas nucleares do estudo jurídico.
- **ENTENDA seletivo:** normas secundárias, só nos conceitos e requisitos centrais.
- **Não** assumir que as 12.896 estruturas do corpus precisam de explicação própria. A meta é cobertura pedagógica, não cobertura estrutural.

## 4. Formatos de revisão por fila (economia de tokens)

| Fila | Formato | Conteúdo mostrado |
|---|---|---|
| A — CLEAN_LOW | tabela | target, título, risco, 1ª frase, checks, motivo de "limpo"; T1 completo só sob pedido |
| B — CLEAN_MEDIUM | lista agregada | ponto central, dependência externa (sim/não), alertas, amostra curta do núcleo; sem Lei Seca inteira |
| C — QUICK_REVIEW | trechos | só a frase problemática, o motivo, o contexto mínimo e a ação proposta |
| D — FULL_HUMAN_REVIEW | pacote completo | padrão das Rodadas HIGH (Lei Seca, T1, camada externa, alertas) |
| E — HARD_FAIL | lista de erros | corrigir antes de qualquer revisão |

Na triagem do Batch05, o volume apresentado caiu de **85.155** caracteres (pacote completo dos 31 pendentes) para **21.751** (relatório das filas + pacote D), redução de **74,5%**.

## 5. Ativação gradual da automação (proposta)

1. **Agora:** só classificar (feito). Revisão humana da triagem dos 31 pendentes do Batch05, para medir se A/B estavam de fato limpos.
2. **Se A/B se confirmarem:** `AUTO_APPROVE_LOW = true` com auditoria por amostragem de 20% e reversão automática para D se a amostra encontrar erro jurídico; MEDIUM continua em revisão agregada (B).
3. **Depois de 2 lotes sem erro jurídico na amostra de B:** discutir `AUTO_APPROVE_MEDIUM`.
4. `MICROAUTO_APPLY = true` só com o teste de "apenas adaptação T1" (já existe nas Rodadas 03A/03B) rodando no lote.

Métricas por lote:
- % de ajuste humano por fila;
- cobertura e falsos positivos do validador v2 contra as decisões do lote;
- desvios T1 por item;
- itens movidos de A/B para C/D na revisão.

Se a cobertura cair abaixo da atual (90% das v1 corrigidas por humanos), voltar a rodadas completas.

## 6. Outras normas

Mesma esteira, com o runtime aprovado de cada norma como autoridade textual e um catálogo externo próprio. Começar por uma norma nuclear curta, para calibrar a taxa de falso positivo das regras fora da CF. O catálogo e as resoluções conhecidas são dados por norma, e o motor não muda.

## 7. Pré-requisitos antes do Batch06

- Decisão sobre os 31 pendentes do Batch05, com base na triagem.
- Fechamento do Batch05: aprovação, staging físico e teste físico, quando autorizados.
- Revisão desta proposta e do A6.

---

## Atualização pós-calibração (2026-10-04) — `T1_SCALE_PIPELINE_PROPOSAL_UPDATED`

A calibração humana dos 31 pendentes do Batch05 mudou três premissas desta proposta.

### 1. Filas sem alerta não são seguras para aprovação automática

| Fila | Itens | Problemas encontrados pelo humano |
|---|---|---|
| A — CLEAN_LOW | 5 | 1 (art. 37, VIII: condição sem base no inciso) |
| B — CLEAN_MEDIUM | 15 | 4 (art. 37, IX e XV; art. 38, I e IV) |
| C — QUICK_REVIEW | 9 | 5 alertas úteis; 4 falsos positivos |

**Consequências:**
- O passo 2 do § 5 (ligar `AUTO_APPROVE_LOW` com amostragem) fica **suspenso**. A e B continuam em revisão humana, mas no formato compacto (lista/agregado), que foi suficiente para achar os 5 problemas.
- A meta passa a ser reduzir o volume lido, não eliminar a leitura.
- A ativação só volta a ser discutida quando 2 lotes seguidos tiverem 0 problema substantivo em A.

### 2. O validador ganhou três regras generalizáveis

`EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE`, `EXCEPTION_OR_RESSALVA_DROPPED` e `EXHAUSTIVE_ENUMERATION_RISK` (A6.11). As três teriam mandado para C os itens 37 VIII, 38 IV e 38 I, que a triagem deixou em A/B.

Os dois casos de B sem regra (37 IX e 37 XV) são de conteúdo jurídico: só entram pelo catálogo, depois de revisão humana. Não se criou detector frágil para eles.

### 3. Dependência externa tem três estados

`EXTERNAL_EVIDENCE_AVAILABLE` / `EXTERNAL_EVIDENCE_LOCAL_PENDING` / `EXTERNAL_VERIFICATION_REQUIRED`. O resolvedor consulta o Relations Engine, mas relação pendente não resolve sozinha.

ENTENDA e Relations Engine seguem processos independentes. Aprovar um ENTENDA com proveniência humana não promove relação.

### Fluxo revisado

```
... → VALIDATOR V2 (+ regras semânticas) → EXTERNAL RESOLVER (3 estados) → RISK ROUTING
→ A/B: revisão compacta obrigatória (lista/agregado; T1 completo sob pedido)
→ C: só o trecho + leitura do validador (provável problema / falso positivo / indeterminado)
→ D: pacote completo
→ decisões humanas → microajustes registrados → nova versão → approval → build determinístico
```

### Orçamento de revisão estimado para o Batch06 (arts. 42–75)

Batch05: pacote completo de 85 mil caracteres para 31 itens; pacote calibrado de 37 mil (−57%), e todas as decisões saíram desse pacote.

Para ~110–140 explicações no Batch06, a mesma proporção daria algo como 130–170 mil caracteres em pacotes compactos, em vez de ~300–390 mil no modelo antigo. É uma estimativa por proporção, não uma medição.

### Pré-requisitos do Batch06 (inalterados)

1. Staging e teste físico do Batch05 (289 aprovados), quando autorizados.
2. Revisão desta proposta.

Batch06 não iniciado.
