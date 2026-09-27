# Continuidade R1C — 25/09/2026 (prioridade sobre o histórico abaixo)

Estado atual: R1C_CURATION_IN_PROGRESS. Inventário dos 105 concluído e imutável. Handoff vigente: 9375eed2-6b52-479f-b8b9-e3f73cdd0758. Retomar do primeiro grupo sem checkpoint R1C: triagem, 52 representações, 24 propostas, 17 fontes, 12 contratos (análise), 4 FP (análise), 4 mecanismos. Curadoria factual agora expressamente autorizada; contratos/compiler/ontologia congelados. Pesquisar somente RECUPERAVEL_PESQUISA_FONTE. Congelar input e provas antes de UMA regressão R1C. Execução completa somente se gate passar. Não refazer inventário/R1/R1B/holdout. Manifest histórico não cobre atualizações autorizadas destes dois arquivos de continuidade. Não substituir snapshot dos 545 arquivos protegidos.

## Histórico encerrado R1B — não é autorização atual

Estado: **EXPANSION_R1B_REGRESSION_COMPLETE_GATE_FAILED / V2_EXPERIMENTAL_INCOMPLETA**.

## Já concluído e persistido

R1: 50 TP, 4 FP, 230 TN/não publicado, 110 FN. R1B factual único: 55 TP, 4 FP, 230 TN, 105 FN. São 398 pares, 394 binários, 3 conflitos e 1 pendente. Resultados e hashes em RESUME_STATE.json e FINAL_ARTIFACT_MANIFEST.json. Não refazer regressões.

110 FN R1 e 105 FN remanescentes possuem diagnóstico individual. Quatro FP foram documentados. Holdout de 120 pares reservado, sem novos rótulos. 122 testes aprovados; 545 arquivos protegidos intactos. Nenhuma fase 9 final, determinismo integral em duas rodadas ou RC executado. Os freezes globais R1 anteriores NÃO são resultados globais R1B.

## Ordem de leitura ao retomar

1. Validar hashes em FINAL_ARTIFACT_MANIFEST.json e verificar INTEGRITY_FINAL.json contra o snapshot já existente; não produzir novo snapshot de referência.
2. Ler ../09_RELATORIOS/V2_EXPERIMENTAL_INCOMPLETA.md e FINAL_DEVELOPMENT_GATE.json.
3. Consultar ../06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1B.json, DIAGNOSTICO_FP_REMANESCENTES.json e ROTULOS_PENDENTES_ADJUDICACAO.json, com suas proveniências.
4. Aguardar decisão humana sobre curadoria prioritária e fronteira entre analogia da garantia e transposição de regime. Qualquer nova versão estrutural exige nova missão expressa; não tratar este arquivo como autorização para implementá-la.

## Limites consumidos

Uma revisão estrutural: EXPANSION_R1. Um passe factual: EXPANSAO_R1B, restrito a três dossiês e um núcleo. Não há autorização para R2 ou segundo passe factual. Não manipular rótulos/contratos para atingir metas. Os dados do overlay não substituem catálogo, DNA ou fonte oficiais.

## Comando seguro de verificação técnica, se necessário

`python -B -X utf8 -m unittest discover -s LEX_MACHINA_REFERENCIAS_V2/tests -v`

Não executar novamente run_regression_r1.py, run_regression_r1b.py, preparadores ou freezes: os resultados completos já existem. O runner integral está bloqueado por gate. Não avaliar/autorrotular a reserva humana nesta etapa.

## Não fazer

Não repetir snapshot, ASTRA, piloto, anotação dos 210, construção dos 69 dossiês, pesquisa já concluída ou consolidação dos 398 pares. Não gerar RC/IDX, integrar firmware, escrever no SD, avançar automaticamente ou criar commit/tag de release.
