# Reauditoria de qualidade da camada jurisprudencial CC

## Resultado

- Resumos examinados: `574/574`; explicações examinadas: `653/653`.
- Flags automáticos iniciais: `480` resumos e `647` explicações.
- Reparos: `523` resumos e `647` explicações.
- Truncamentos não resolvidos: `0`; fragmentos crus não resolvidos: `0`.
- Conteúdo pronto/revisão/evidência: `653/0/0`.
- A auditoria preserva as 653 decisões humanas; nenhum vínculo A–E foi redecidido.

## Causa sistêmica e saneamento

O extrator anterior fragmentava enumerações e abreviações jurídicas e aplicava corte por tamanho sem garantir fechamento sintático. O saneamento passou a separar apenas fronteiras fortes, proteger abreviações, rejeitar fragmentos e selecionar proposições completas na fonte oficial integral. Nenhuma palavra faltante foi completada por adivinhação.

### Flags iniciais por tipo

- Resumos `ABRUPT_END`: `381`.
- Resumos `BROKEN_ENUMERATION`: `84`.
- Resumos `INCOMPLETE_SENTENCE`: `381`.
- Resumos `LEADING_FRAGMENT`: `70`.
- Resumos `RAW_EXCERPT_NOT_SUMMARY`: `67`.
- Resumos `SUSPICIOUS_ARTICLE_FRAGMENT`: `5`.
- Resumos `SUSPICIOUS_LOWERCASE_START`: `62`.
- Resumos `TRAILING_FRAGMENT`: `136`.
- Resumos `UNBALANCED_PARENTHESES`: `15`.
- Resumos `UNBALANCED_QUOTES`: `52`.
- Explicações `ABRUPT_END`: `513`.
- Explicações `INCOMPLETE_SENTENCE`: `511`.
- Explicações `RAW_EXCERPT_NOT_SUMMARY`: `12`.
- Explicações `TEMPLATE_LIKE_EXPLANATION`: `647`.
- Explicações `TRAILING_FRAGMENT`: `190`.
- Explicações `UNBALANCED_PARENTHESES`: `21`.
- Explicações `UNBALANCED_QUOTES`: `36`.

### Estratégias editoriais finais

- `FAMILY_RULE`: `34`.
- `GOLDEN_CURATED`: `6`.
- `LIABILITY_RULE`: `50`.
- `OBLIGATION_RULE`: `124`.
- `PENDING_RESOLVED_LOCAL_OFFICIAL`: `5`.
- `PROPERTY_RULE`: `49`.
- `SPECIFIC_HOLDING`: `222`.
- `SUCCESSION_RULE`: `66`.
- `TEMPORAL_RULE`: `97`.

## Cinco pendências

| ID | Target | Precedente | Status | O que decidiu | Por que está aqui |
|---|---|---|---|---|---|
| CCMD-4C1E3147DA | CC2002:ART.405 | STJ:SUMULA:426 | CONTENT_READY | Os juros de mora na indenização do seguro DPVAT fluem a partir da citação. | O art. 405 define a citação como marco inicial dos juros moratórios; a Súmula 426 aplica essa regra à indenização do seguro DPVAT. |
| CCMD-6263C35580 | CC2002:ART.206:PAR.5:INC.I | STJ:SUMULA:504 | CONTENT_READY | A ação monitória contra o emitente de nota promissória sem força executiva prescreve em cinco anos, contados do dia seguinte ao vencimento do título. | O art. 206, § 5º, inciso I fornece o prazo quinquenal para cobrar dívida líquida constante de instrumento; a Súmula 504 aplica-o à nota promissória sem força executiva. |
| CCMD-741CADCA02 | CC2002:ART.206:PAR.3:INC.IX | STJ:REPETITIVO:883 | CONTENT_READY | A cobrança e o pedido de diferenças do seguro obrigatório DPVAT prescrevem em três anos; para diferenças, o prazo começa no pagamento administrativo feito a menor. | O art. 206, § 3º, inciso IX estabelece o prazo trienal aplicado pelo Tema 883 às pretensões de cobrança e complementação do seguro obrigatório DPVAT. |
| CCMD-EE1186426A | CC2002:ART.1025 | STJ:RESP:1422461 | CONTENT_READY | O novo sócio que assume dívida na forma do art. 1.025 não pode, em regra, questionar a higidez do crédito, mas pode exigir sua verificação pericial quando houver dúvida sobre a legalidade da desconsideração. | O art. 1.025 rege a assunção da dívida pelo novo sócio e sustenta a presunção de que o crédito foi verificado na admissão, sem impedir perícia diante de dúvida concreta sobre sua regularidade. |
| CCMD-F29DA91B52 | CC2002:ART.1698 | STJ:SUMULA:596 | CONTENT_READY | A obrigação alimentar dos avós é complementar e subsidiária e somente surge quando os pais não conseguem cumpri-la total ou parcialmente. | O art. 1.698 dá suporte à responsabilidade complementar dos demais parentes; a Súmula 596 delimita que os avós só respondem diante da impossibilidade total ou parcial dos pais. |

## Round 1 e Round 2

Round 1: `200` relações; classificações `{'MINOR_EDIT': 18, 'CORRECT': 182}`.
Round 2: `50` relações novas, sem sobreposição com Round 1; classificações `{'CORRECT': 40, 'MINOR_EDIT': 10}`.

As amostras são verificações determinísticas e estratificadas de evidência, completude, target e consistência editorial. Elas não são apresentadas como revisão humana independente.

## Multitarget e projeção

Foram verificados `67/67` precedentes multitarget. Cada precedente mantém um resumo único, enquanto cada target recebe explicação própria. Leakage detectado: `0`.

## Limites operacionais

Operação exclusivamente host-side. SD, ESP32 e firmware físico não foram acessados ou modificados. O backlog legado de 277 fichas sem conteúdo substantivo permanece fora do escopo.
