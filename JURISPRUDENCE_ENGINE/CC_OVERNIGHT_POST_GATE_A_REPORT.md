# Operação noturna pós-Gate A — checkpoint

Data: 2026-10-19 · branch `cf-jurisprudence-audit` · início `9a7f617f6559ca117fb0be87a2e51b53486b5a31`.

## Estado em uma página

- Gate A físico registrado: técnico PASS e validação humana 20/20 PASS.
- Firmware físico aprovado: `e2945cf55a00f27f6c35ff709e81732d804fd8c6f01958230cef0016f740a4a0`.
- Escopo da aprovação: regressão/compatibilidade legada. Turma Display continua `PENDING_PHASE_B`.
- Fase B pronta, não implantada: seis relações C/D/E, seis targets novos, projeção CC `55/45`.
- Deploy 653 pronto, não implantado: CC `702/636`, 572 fichas novas, duas reutilizadas, 833/4096 lookups e zero Group F.
- Mock: fixture e mass deploy PASS; rollback PRE→POST→PRE byte-exato; idempotência PASS; cinco falhas injetadas recuperadas.
- Checklist massivo: 48 itens estratificados.
- Group F: 28/28 revisadas, zero ratificadas; 7 recomendadas com nota, 3 para rejeição/relocação e 18 ainda em hold.
- Hardware/SD: não acessados nem alterados nesta missão.

## Aprovação física e tag

O registro está em `firmware_turma_display/TURMA_DISPLAY_PHYSICAL_GATE_A_APPROVAL.{json,md}`. A tag anotada
`lex-device-v1-turma-display-gate-a-firmware-physical-approved-2026-10-19` aponta somente para esse gate e declara no texto que a Fase B permanece pendente. Nenhuma tag física foi criada para fixture ou mass deploy.

## Fase B

| ID | Grupo | Target | Render representativo |
| --- | --- | --- | --- |
| CCMD-0124F833D5 | C | CC2002:ART.102 | STJ 3ª T. · REsp 2.032.586 |
| CCMD-151AFCE0D1 | C | CC2002:ART.206:PAR.1 | STJ 4ª T. · AREsp 2.604.779 |
| CCMD-0C72C29089 | D | CC2002:ART.332 | STJ 3ª T. · AREsp 2.482.762 |
| CCMD-006371F260 | D | CC2002:ART.1 | STJ 4ª T. · REsp 2.142.132 |
| CCMD-0BCA168976 | E | CC2002:ART.110 | replacement por REsp 1.102.424 |
| CCMD-11CED92827 | E | CC2002:ART.750 | replacement por AREsp 2.081.145 |

O fixture contém apenas as seis fichas necessárias e os quatro agregados candidatos. O motor recusa escrita sem estrutura esperada, hashes PRE exatos, volume removível FAT/FAT32/exFAT, backup externo, confirmação explícita e declaração do firmware aprovado.

## Deploy 653 e rollback

O manifesto autoritativo lista as 653 relações, os targets, precedentes, fichas e hashes. As fichas são referenciadas no conteúdo compartilhado existente; não foram triplicadas entre HIGH_AUTHORITY, TURMA e COMBINED.

Há dois estados PRE autorizados:

1. `CLEAN_BASELINE`, CC 49/39;
2. `POST_FIXTURE_VALIDATED`, CC 55/45.

O segundo é recomendado após a validação física B, pois preserva o fixture já validado e requer seis writes aditivos a menos. Em ambos os casos, o rollback restaura os quatro agregados byte a byte e remove somente as fichas efetivamente criadas pela transação, sem glob.

## Testes

- Pós-Gate A: 18/18.
- Jurisprudence Engine: 145/145.
- Jurisprudence Audit: 119/119.
- Legal Target ID: 93/93.
- Correlatas: 115/120; exatamente as mesmas cinco falhas históricas (`c0`, `c3a1_c3b_prep`, `c3a_engine`, `c3b1`, `c3b2`).
- Determinismo: PASS com `PYTHONHASHSEED=1` e `777`.
- Nova regressão: 0.

## Próxima sequência física — não executar durante esta missão

1. Retirar o cartão e conectá-lo ao PC; identificar manualmente a raiz removível correta.
2. Executar somente o preflight do fixture:
   `python JURISPRUDENCE_ENGINE/deploy_cc_turma_fixture.py --root <SD_ROOT> --preflight`
3. Se o PRE passar, executar o deploy com backup externo, token `CC_TURMA_FIXTURE_B` e o SHA-256 de firmware registrado.
4. Recolocar o cartão no LEX MACHINA e responder ao checklist `CC_TURMA_PHYSICAL_FIXTURE/PHYSICAL_CHECKLIST_B.md` no formato `1-13 OK` ou com os números de falha.
5. Somente depois do PASS físico B, escolher promoção direta `POST_FIXTURE_VALIDATED` para o deploy 653 ou rollback do fixture.

Nenhuma dessas ações físicas foi executada nesta preparação.
