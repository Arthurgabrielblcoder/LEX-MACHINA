# JURISPRUDÊNCIA — CF: cobertura da fila HIGH (fechamento da fase HIGH)

```
FILA HIGH = ESGOTADA após o Batch04 (Batch05 = lote vazio de fechamento, J2_BATCH05_DECISIONS.json)
Nenhuma recomendação não ratificada foi contada como promoção aprovada · nada dos Batches 03–05 materializado
```

## Respostas

| # | Pergunta | Resposta |
|---|---|---|
| 1 | Quantos HIGH existiam no início? | **42**, na reconstrução da J2A sobre a base de 256. O J0, sobre a base de 277, tinha 40. Mudaram 2: J0-BL-072 e J0-BL-074 subiram porque a J1.1 deixou os arts. 96 e 98 sem jurisprudência |
| 2 | Quantos já estavam resolvidos? | **0** no início. Ao longo do trabalho, **2** ficaram cobertos por decisões ratificadas: J0-BL-060 (ED do HC 232627) e J0-BL-168 (nota do ADCT 101) |
| 3 | Quantos foram pesquisados? | **35**: Batch01 10 + Batch02 10 + Batch03 10 + Batch04 5 |
| 4 | Quantos receberam proposta de promoção? | **27**: Batch01 6 + Batch02 9 (4 promoções e 5 realocações) + Batch03 7 (5 + 1 provisória + 1 realocação) + Batch04 5 (4 + 1 provisória) |
| 5 | Quantos receberam proposta de rejeição? | **8**: Batch01 4 (2 falsos positivos, 1 temporal, 1 duplicata) + Batch02 1 (falso positivo) + Batch03 3 (2 não materiais, 1 temporal) + Batch04 0 |
| 6 | Quantos precisam de revisão externa adicional? | **0** recomendações `UNRESOLVED`. Precedentes citados nas notas e não verificados (fora das propostas): ADI 4983 (BL-090); ADIs 3315, 3804 e 4427 (BL-122); ADI 1021 (BL-068) |
| 7 | Quantos continuam pendentes como HIGH? | **0**. Outros **5** saíram do HIGH sem pesquisa e estão na fila MEDIUM: BL-075 (ADI 4425 no art. 100: perdeu a recorrência); BL-055, 056 e 059 (art. 53 passou a ter jurisprudência aprovada); BL-170 (ADI 7064 / MI 7300 no ADCT 107-A) |
| 8 | Quantos já estão editorialmente aprovados? | **15 decisões** dos Batches 01 e 02 (6 + 9), que viram **13 relações** no aparelho (5 + 8) |
| 9 | Quantos estão fisicamente instalados? | As **5 relações** do Batch01 (ADIs 4425, 7047/7064 e 7697 ×3), instaladas na J2C (12/12). Também está instalada a realocação temporal do Tema 558. As 8 relações do Batch02 estão só no candidato host-only J2E |

**Reconciliação dos 42:** 35 pesquisados + 2 cobertos + 5 rebaixados a MEDIUM = 42.

## Estado por lote

| Lote | Pesquisados | Promoções | Realocações | Rejeições | Pendentes | Estado |
|---|---:|---:|---:|---:|---:|---|
| Batch01 (J2A) | 10 | 6 | 0 | 4 | 0 | **ratificado; instalado (J2C)** |
| Batch02 (J2D) | 10 | 4 | 5 | 1 | 0 | **ratificado; candidato J2E (não instalado)** |
| Batch03 | 10 | 6 (1 provisória) | 1 | 3 | 0 | aguardando ratificação |
| Batch04 | 5 | 5 (1 provisória) | 0 | 0 | 0 | aguardando ratificação |
| Batch05 | 0 | 0 | 0 | 0 | 0 | fila HIGH esgotada |

## Lições que se repetiram

- **Namespace:** várias ADIs julgaram **Constituições estaduais**. Nesses casos, o vínculo com a CF só vale se a decisão interpretar expressamente o dispositivo federal como parâmetro:
  - **ADI 2167:** rejeitada, porque não interpretou o art. 36, I.
  - **ADI 336, 7369 e 978:** aceitas, porque interpretam os arts. 35 e 86 da CF.
- **Alvo trocado:** notas do backlog citavam um parágrafo e o target ficava em outro:
  - ADI 1616 e 1254 tratam do art. 103, § 3º, não do § 1º;
  - Inq 672 trata do art. 86, § 4º, não do § 3º;
  - a SV 46 se refere ao art. 22, I e ao art. 85, parágrafo único.
- **Tempo:**
  - Tema 558 e ADI 4425 julgaram o § 9º do art. 100 na redação da EC 62/2009;
  - o art. 165, § 18 é de 2025, posterior ao julgado.
- **Provisórios:**
  - ADI 7697 (cautelar referendada, ratificada);
  - ADI 5017 (liminar monocrática de 2013, nunca referendada);
  - ADPF 378 (cautelar do Plenário);
  - Rcl 84738 (orientação de Turma condicionada ao Tema 1147).
- **Tipos novos no aparelho:** MS, AP, AI, Inq, Rcl e HC (este com protótipo na Fase C); a súmula comum e a ADPF têm rótulo no firmware, mas nunca foram validadas fisicamente.
