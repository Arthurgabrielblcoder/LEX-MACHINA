# Plano de expansão da camada 4 REFERÊNCIAS — CF88

**Objetivo:** corrigir os grandes vazios sem forçar uma referência em todo artigo. Status: **PENDING_HUMAN_REVIEW**; nada foi inserido no corpus.

## Ponto de partida (auditoria de 2026-10-01)

- 101 vínculos WORK_REFERENCE em 43 targets e 18 artigos da CF (6.5% dos 276 artigos estruturais); ADCT sem nenhuma obra.
- Maior vazio: Art. 24 a Art. 169 (168 artigos consecutivos sem obra), cobrindo Organização do Estado (a partir do art. 24), Organização dos Poderes, Defesa do Estado e Tributação e Orçamento.
- Registry: 69 obras, 34 sem uso na CF; catálogo de expansão com 199 obras ainda não integradas.

## Prioridades

1. Dispositivos constitucionalmente importantes (art. 37; separação de Poderes; tributação; ordem social).
2. Artigos de grande utilidade didática.
3. Temas em que uma obra realmente facilita compreender, lembrar, problematizar ou visualizar.
4. Partes quase sem cobertura (blocos com 0%: Organização dos Poderes, Defesa do Estado, Tributação e Orçamento, Disposições Gerais, ADCT).
5. Artigos testados por Arthur e confirmados vazios (37, 43, 62, 98, 201, 202).

## Efeito das propostas se aprovadas

- Prioritárias: arts. 37, 43, 62 e 201 deixam de ser lacuna; 98 e 202 continuam lacuna por falta de obra adequada; 193 já tem obra (retestar no aparelho).
- Adicionais: 19 vínculos em blocos hoje vazios (Poderes, Defesa do Estado, Tributação, Ordem Econômica, Ordem Social, ADCT).
- Total: 25 vínculos propostos; 21 artigos distintos.

## Regras de qualidade aplicadas

- Rejeitadas conexões genéricas ("a obra tem governo, então serve para Administração Pública"; "fala de dinheiro, então serve para orçamento").
- Score na mesma escala do RC2, com justificativa; nenhuma nota alta para preencher lacuna.
- Obras fora do registry ficam como NEW_WORK_CANDIDATE e exigem ingestão própria (identidade, evidências, ficha) antes de qualquer vínculo.
- Sistemas estrangeiros e ficção sempre com limites de transposição explícitos.

## Próximos passos (fora desta missão)

1. Revisão humana de `REFERENCE_EXPANSION_REVIEW.md`.
2. Ingestão das obras novas aprovadas no registry (pipeline do catálogo).
3. Geração dos vínculos aprovados pelo pipeline editorial atual e novo export (run3), com regressão contra o run2.
4. Reteste físico do art. 193 com `CONTEXTO: ART. 193` no rodapé.
