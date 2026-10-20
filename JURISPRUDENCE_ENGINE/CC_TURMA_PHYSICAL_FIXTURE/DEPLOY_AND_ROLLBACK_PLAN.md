# Deploy/rollback do fixture Fase B

Execução real é proibida nesta preparação. O script recusa escrita sem volume removível FAT/FAT32/exFAT, baseline byte-exato, confirmação `CC_TURMA_FIXTURE_B`, firmware Gate A declarado e backup externo.

Ordem: PRE → backup dos quatro agregados → seis fichas via temp/fsync/readback → staging no mesmo filesystem → replaces → `JUR_LOOKUP.IDX` por último → readback/recontagem. Rollback restaura os quatro bytes PRE e remove somente as fichas criadas pela transação.
