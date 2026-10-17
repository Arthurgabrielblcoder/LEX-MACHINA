# JURISPRUDÊNCIA — CF: Batch03 HIGH (revisão externa; propostas aguardando ratificação)

```
BATCH = 03 · NÍVEL = HIGH · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false em todos)
DECISÕES = J2_HIGH_BACKLOG/J2_BATCH03_DECISIONS.json (build_j2_batch.py --batch 3 --level HIGH + j2_batch03_review.py; 3/3 idêntico)
FONTES = STF (navegador embutido, sha do texto renderizado), corpus oficial arquivado (J4), Planalto (P1, da J2A) · consulta 2026-10-17
```

## Fila reconstruída

**Modelo de estado usado:**

- `PHYSICALLY_INSTALLED` = J2C, 261/160.
- `EDITORIALLY_APPROVED_HOST_ONLY` = Batch02/J2E (8 relações).
- Nenhuma proposta não ratificada é tratada como vínculo.

| Contagem | Valor |
|---|---:|
| Analisadas em lotes anteriores (01–02) | 20 |
| Cobertas por decisão ratificada (BL-060, 083, 085, 168) | 4 |
| Pendentes | **124** |
| HIGH / MEDIUM / LOW | **15** / 82 / 27 |
| Sem identificador | 67 |

**Por que o HIGH caiu de 21 (após o J2D) para 15:**

- **2 cobertos:** BL-060 (ED do HC 232627) e BL-168 (nota ADCT 101).
- **4 caíram para MEDIUM:**
  - BL-055, 056 e 059: o art. 53 passou a ter jurisprudência aprovada editorialmente (Tema 950 e HC), então deixou de contar como "artigo sem jurisprudência".
  - BL-170: perdeu a recorrência e o art. 107-A tem aprovação.

O detalhe está em `reconstruction.LEFT_LEVEL_SINCE_PREVIOUS_BATCH`. A regra de prioridade é a do J0, sem alteração.

## Resultado (10/10 com fonte oficial)

| # | Target | Precedente | Tipo | Status | Proposta | Razão |
|---|---|---|---|---|---|---|
| 1 | CF 29, X | Súmula 702 | Súmula | vigente | **PROMOTE** | Referência legislativa oficial = art. 29, X |
| 2 | CF 52, p.u. | MS 34418 (+34379/34384) | MS | prejudicado | **REJECT_NOT_MATERIAL** | O STF não decidiu a cisão das votações; o MS foi julgado prejudicado ou não conhecido |
| 3 | CF 52, p.u. | MS 21689 (Collor) | MS | mérito (1993) | **PROMOTE** | Duas penas autônomas; a renúncia não paralisa o impeachment |
| 4 | CF 55, VI | AP 694 | AP | mérito (1ª Turma) | **PROMOTE** (confiança MEDIUM) | Perda do mandato: cabe à Casa, salvo regime fechado; precedente de Turma, orientação oscilante |
| 5 | CF 165, § 18 | ADI 7047/7064 | ADI | mérito | **REJECT_TEMPORAL_MISMATCH** | O § 18 é da EC 136/**2025**; o julgado é de 2023 |
| 6 | CF 103, § 1º | ADI 1616 e ADI 1254 | ADI | mérito | **REALLOCATE → CF 103, § 3º** | Os precedentes tratam do AGU (§ 3º), não do PGR (§ 1º) |
| 7 | CF 130 | ADI 789 | ADI | mérito | **PROMOTE** | "Inteligência da norma inscrita no art. 130" (MP junto ao TCU) |
| 8 | ADCT 27 | ADI 5017 | ADI | **cautelar monocrática, não referendada** | **PROMOTE_PROVISIONAL → ADCT 27, § 11** | A EC 73/2013 (novos TRFs) está suspensa desde 2013; exige gatilho de revalidação |
| 9 | CF 29, X | HC 232627 + Inq 4787 | HC/Inq | mérito (2025) | **REJECT_NOT_MATERIAL** | Os acórdãos interpretam só o art. 53, § 1º; aplicar ao art. 29, X seria extensão |
| 10 | CF 31, § 2º | Tema 157 (RE 729744) | RG | tese; trânsito em 2019 | **PROMOTE** | O parecer prévio do TC é opinativo; quem julga as contas é a Câmara (art. 31) |

```
PROMOTE_RECOMMENDED = 5 · PROMOTE_PROVISIONAL_RECOMMENDED = 1 · REALLOCATE_RECOMMENDED = 1
REJECT_NOT_MATERIAL_RECOMMENDED = 2 · REJECT_TEMPORAL_MISMATCH_RECOMMENDED = 1 · UNRESOLVED = 0 · HIGH restantes = 5
```

## Pontos de atenção

- **Tipos ainda não validados no aparelho:**
  - Súmula comum: o firmware tem o rótulo `SUMULA STF`, mas o tipo nunca foi testado fisicamente.
  - MS, AP e Inq: não existem; seria preciso desenhar como o HC.
  - Só RG, SV e ADI estão validados.
- **Alertas dos detectores da Fase D**, todos conferidos com a evidência oficial:
  - Lei 8.443/92 na ADI 789: a lei era o objeto e o art. 130 o parâmetro interpretado; namespace mantido como CF.
  - EC 136/2025 no art. 165, § 18: confirmou o descompasso temporal.
  - ADI 5017: marcada como provisória.
- **Julgamento conjunto:** o Inq 4787 AgR-QO é o mesmo julgamento do HC 232627 (mesma sessão, tese e dispositivo), com o mesmo escopo. Isso conta para o BL-059 (MEDIUM): o candidato natural é virar alias do registro do HC.
- **Limitação registrada:** a página "A Constituição e o Supremo" (`constituicao.stf.jus.br`) não terminou de carregar no navegador embutido. Por isso as ADIs foram verificadas direto na pesquisa de jurisprudência do STF. Das quatro ADIs da nota do BL-122, só a 789 foi verificada; das três do BL-090, a 1616 e a 1254 (a 4983 ficou de fora).
