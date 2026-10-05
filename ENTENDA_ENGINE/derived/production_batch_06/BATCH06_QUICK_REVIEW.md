# BATCH06 — REVISÃO RÁPIDA (fila C)

Lote `ENTENDA_CF_PRODUCTION_BATCH_06` · 3 itens · só o trecho com problema; nenhuma correção foi aplicada.

## `CF88:ART.57:PAR.2` — Art. 57, § 2º — Recesso condicionado à aprovação da LDO · risco LOW

- **Trecho:** "É um incentivo institucional ligado ao calendário, sem sanção pessoal aos parlamentares."
- **Contexto mínimo:** o_que_significa: … Para garantir a votação, a Constituição condiciona o recesso de meio de ano à aprovação desse projeto: enquanto não for aprovado, o…
- **Detector:** TELEOLOGY_SPECULATIVE (TELEOLOGY_SPECULATIVE)
- **Motivo:** TELEOLOGY_SPECULATIVE (incentivo)
- **Proposta de correção segura:** retirar a frase de finalidade (o texto nao a declara) ou reduzi-la ao que o dispositivo diz

- [ ] ACEITAR PROPOSTA   - [ ] AJUSTAR   - [ ] MANDAR PARA D

## `CF88:ART.68:PAR.2` — Art. 68, §§ 2º e 3º — Forma da delegação e apreciação pelo Congresso · risco MEDIUM

- **Trecho:** "A resolução autoriza o Presidente a elaborar lei sobre um programa de incentivos e exige que o projeto volte ao Congresso."
- **Contexto mínimo:** exemplo_pratico ⟦trecho⟧ O Congresso vota o texto em uma só votação, aprovando ou rejeitando, sem alterar o conteúdo.
- **Detector:** TELEOLOGY_SPECULATIVE (TELEOLOGY_SPECULATIVE)
- **Motivo:** TELEOLOGY_SPECULATIVE (incentivos)
- **Proposta de correção segura:** retirar a frase de finalidade (o texto nao a declara) ou reduzi-la ao que o dispositivo diz

- [ ] ACEITAR PROPOSTA   - [ ] AJUSTAR   - [ ] MANDAR PARA D

## `CF88:ART.71:INC.II` — Art. 71, inciso II — Julgamento das contas de administradores · risco LOW

- **Trecho:** "O inciso II atribui ao Tribunal julgar as contas de quem administra ou responde por dinheiro, bens e valores públicos da administração direta e indireta, inclusive fundações e sociedades criadas e mantidas pelo poder público federal, e também as contas de quem causar perda, extravio ou outra irregularidade com prejuízo aos cofres públicos."
- **Contexto mínimo:** o_que_diz
- **Detector:** LONG_SENTENCE (EDITORIAL_CHECK_UNRESOLVED)
- **Motivo:** EDITORIAL_CHECK_UNRESOLVED (LONG_SENTENCE)
- **Proposta de correção segura:** dividir a frase em duas ou mais, sem alterar o conteudo juridico

- [ ] ACEITAR PROPOSTA   - [ ] AJUSTAR   - [ ] MANDAR PARA D

