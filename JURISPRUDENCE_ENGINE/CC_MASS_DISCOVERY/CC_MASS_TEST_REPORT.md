# CC MASS DISCOVERY — relatório de testes (2026-10-19)

```
JURISPRUDENCE_ENGINE 88/88 OK · JURISPRUDENCE_AUDIT 119/119 OK · LEGAL_TARGET_ID 93/93 OK · REFERENCE_COVERAGE_AUDIT 15/15 OK
CORRELATA_COVERAGE_AUDIT 115/120 (as mesmas 5 falhas históricas) · test_cc_mass_discovery 13/13 OK
build_cc_mass_discovery --check UP_TO_DATE · CC-J1 (3) e CC-J2 (4) --check UP_TO_DATE · SD_CHANGED NO · FIRMWARE_CHANGED NO
```

## Suítes

Cada suíte foi rodada a partir da pasta `tests` com `python -m unittest discover -p 'test_*.py'`. As Correlatas foram rodadas arquivo por arquivo.

| Suíte | Resultado |
|---|---|
| JURISPRUDENCE_ENGINE | 88 testes, OK (inclui os 13 de `test_cc_mass_discovery.py`) |
| JURISPRUDENCE_AUDIT | 119 testes, OK |
| LEGAL_TARGET_ID | 93 testes, OK |
| REFERENCE_COVERAGE_AUDIT | 15 testes, OK |
| CORRELATA_COVERAGE_AUDIT | 115/120. As 5 falhas são as históricas (uma em cada: c0, c3a1_c3b_prep, c3a_engine, c3b1, c3b2) |

## O que `test_cc_mass_discovery.py` garante

- **Saídas reproduzíveis:** `--check` confere byte a byte. O teste é pulado, com o motivo, quando o índice local das Turmas não existe, porque esse índice não é versionado.
- **Qualificado íntegro:**
  - ids únicos e nenhum par (target, precedente) contado duas vezes;
  - targets válidos no índice do CC2002;
  - nada que já esteja no cartão;
  - fonte oficial com hash;
  - `AWAITING_USER_RATIFICATION` e `human_approved = false` em todas as relações.
- **Regras de tier:**
  - TIER A só para precedente qualificado com evidência forte e sem sinal de risco;
  - nenhuma evidência fraca no qualificado;
  - nenhum dispositivo revogado.
- **Regressões de precisão, cada uma corrigida na regra e coberta por teste:**
  - CC/1916 lido como CC/2002: Tema 426 → art. 993 e Tema 74 → art. 1.062;
  - julgamentos conjuntos contados uma vez: REsp 2082647/2100103/1929926 e ADC 29;
  - fallback resolvido antes da deduplicação: Tema 1173 → art. 723;
  - recurso não conhecido por óbice: REsp 2172770. "A origem negou provimento" não conta como mérito;
  - menção só na alegação ou no óbice: AREsp 3120248 e EREsp 1280825 → art. 200;
  - acórdão antigo que decide e depois "não conhece", sem óbice, permanece: REsp 976968 → art. 205;
  - correspondência com o CC/1916 sinalizada e nunca TIER A: EREsp 1171820 e REsp 665651.
- **Turmas:**
  - um representante por dispositivo, sempre TIER B;
  - só para dispositivo sem vínculo de fonte superior;
  - evidência forte na ementa;
  - corroborações contadas à parte.
- **Política de dados:** os arquivos versionados têm menos de 10 MB cada; os `_local/` estão no `.gitignore`.
- **Amostra (Passagem 2):** 40/40 revisados; nenhum erro de identidade, de target ou de duplicata.
- **Baselines e simulação:** CC 49/39, CF 315/198, SD e firmware inalterados, regressão 0 na CF e no CC-J1/J2, nenhuma chave de consulta duplicada.
- **Checkpoint:** hashes de saída conferem e nenhuma fonte ficou pendente.

## Integridade das camadas congeladas

- **Métricas do CC-J2:** `CC_J2_SCALE_METRICS.json` e o dossiê final contavam ao vivo as linhas de `discovery_stj_precedentes.py` e do próprio builder. Esses arquivos cresceram nesta missão (adapter v2), então os geradores do CC-J2 acusavam STALE. A medição passou a ler essas ferramentas no commit `a8a4d7a`, o estado congelado do CC-J2, como o CC-J1 já fazia. As saídas do CC-J2 continuam idênticas byte a byte, e nenhuma saída congelada foi reescrita.
- **Arquivos não alterados:** `CC_J2_MATERIALIZATION_CANDIDATE/`, `CC_J2_PHYSICAL_DEPLOY/` e o índice de targets do CC (`git diff` vazio).
