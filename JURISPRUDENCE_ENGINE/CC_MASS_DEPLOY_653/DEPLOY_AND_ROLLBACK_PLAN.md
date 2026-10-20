# Deploy massivo 653 — plano operacional

`RECOMMENDED_PHYSICAL_PATH = POST_FIXTURE_VALIDATED`: após a Fase B aprovada, promove diretamente ao conjunto 653 e evita seis escritas aditivas. `CLEAN_BASELINE` também é aceito. Ambos exigem hashes exatos e CF/ADCT 315/198.

O deploy real exige o token `CC_MASS_653`, declaração do firmware Gate A por SHA-256 e backup externo. A transação grava fichas ausentes, faz readback, prepara os quatro índices no mesmo filesystem, substitui `JUR_LOOKUP.IDX` por último e reconta 702/636 e 833 lookups. Rollback restaura exatamente o estado PRE detectado e apaga apenas fichas registradas na transação, sem glob.
