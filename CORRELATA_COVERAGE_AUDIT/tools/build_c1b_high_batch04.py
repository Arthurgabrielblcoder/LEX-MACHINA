"""CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH04 — closing batch: ALL original HIGH candidates still undecided after Batch01..03.

Same machinery and rules as Batch03 (temporal status mandatory, scope flags, device route apart from the legal decision). No limit: every
remaining original HIGH candidate enters. Decisions against the official text (Planalto, sha256 recorded). NOTHING IS APPLIED.

Writes CF88_CORRELATA_C1B_HIGH_BATCH04_{INPUT.json, DECISIONS.json, REPORT.md}. Usage: python build_c1b_high_batch04.py [--check]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_c1b_high_batch01 as B1  # noqa: E402
import build_c1b_high_batch03 as B3  # noqa: E402

AUDIT = B1.AUDIT
OUT_IN = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH04_INPUT.json'
OUT_DEC = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH04_DECISIONS.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH04_REPORT.md'
S, D3, TS, BL = B1.S, B3.D3, B3.TS, B3.BL
IN_FORCE = B3.IN_FORCE
L14701_T = TS('UNCERTAIN', effective_from='2023-10-20 (publicação)',
              note='a página oficial do Planalto anota "(Vide ADC 87) (Vide ADI 7582) (Vide ADI 7583) (Vide ADI 7586)" no art. 4º: lei sob '
                   'controle concentrado no STF; situação atual de eficácia não verificada nesta rodada')

SOURCES = {
    'CF88': B1.SOURCES['CF88'], 'EC103': B1.SOURCES['EC103'],
    'L8212': B3.SOURCES['L8212'],
    'LC141': S('Lei Complementar nº 141/2012', 'leis/lcp/lcp141.htm', 'bef7e768506e0e9c5c0666a58b41546d18549865f7e445891df62428c9efe2a3', 85924),
    'LC142': S('Lei Complementar nº 142/2013', 'leis/lcp/lcp142.htm', 'bf2272518f8b70e40fdfe6123d797e920996710c7621adcacb6edafd2a0e1172', 17481),
    'L8213': S('Lei nº 8.213/1991 (compilada)', 'leis/l8213cons.htm', 'd9b8d1fe23dfe9cbad0b99bc50f0a474b8cfc1359323f653ab25397aa198d3fc', 755476),
    'LC109': S('Lei Complementar nº 109/2001', 'leis/lcp/lcp109.htm', '98477f7eb4c8033840602397bb261fcf0fd94137617215abafe59708bc8870b9', 93736),
    'L8069': S('Lei nº 8.069/1990 (ECA)', 'leis/l8069.htm', '6c98180184cea3913ca7681d865eea766cfcc7764751e4b6cfd11a42bbcbf0af', 696951),
    'L14701': S('Lei nº 14.701/2023', '_ato2023-2026/2023/lei/l14701.htm', 'd51bcfe35e5dbf038dbd814a0b026914b0a1500b76989fe5b6ad7027a47e1bf8', 126386),
    'LC7': S('Lei Complementar nº 7/1970 (PIS)', 'leis/lcp/lcp07.htm', 'ea1bc507aa5b234d27fea2bc08da7a5d7a4feebca8d22cdf235cd92d5a9ca791', 19195),
    'LC8': S('Lei Complementar nº 8/1970 (PASEP)', 'leis/lcp/lcp08.htm', '87eed61b818add9c5e3d81de18574f1a3a2cb090183848b9f16a9129d3f6138a', 14949),
    'L7998': S('Lei nº 7.998/1990', 'leis/l7998.htm', '674335b5ec1bf3edd518c27bbbad3838cca9635225dd08967733ae88fcf36558', 118913),
    'LC146': S('Lei Complementar nº 146/2014', 'leis/lcp/lcp146.htm', '22dca8f0bef78dc879a074f183b2fb7212b1838f800b5c729d00b3bf40719d0e', 6817),
    'LC160': S('Lei Complementar nº 160/2017', 'leis/lcp/lcp160.htm', '56dca4c1d6f4d5e13ae98f7e19d33313d544757fd110ec0a88d71310006e886d', 39741),
}

HOLD_14701 = ('A Lei 14.701/2023 se declara regulamentadora do art. 231 (ementa). A página oficial, porém, anota no art. 4º, que define as terras '
              'tradicionalmente ocupadas pelo critério da data da promulgação, a remissão a ADC 87 e ADIs 7582, 7583 e 7586. O núcleo da lei '
              'está sob controle concentrado no STF, e a situação atual de eficácia não foi verificada em fonte oficial nesta rodada. Aprovar '
              'pode exibir como correlata vigente disciplina cuja validade está em disputa; rejeitar ignora uma regulamentação expressa.')

REVIEW = {
    'CORRC0-A88AB3189E73': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['L8212'],
                              'Lei 8.212/1991, Capítulo VI, art. 25: contribuição do segurado especial e do produtor rural pessoa física sobre a '
                              'receita bruta da comercialização da produção.',
                              'O § 8º prevê a contribuição do produtor em economia familiar sobre o resultado da comercialização. O art. 25 é essa '
                              'disciplina; a referência legada ao "art. 55" estava errada. A natureza muda de COMPLEMENTA para REGULAMENTA.',
                              IN_FORCE, route='art. 25'),
    'CORRC0-C4B7D896EEC4': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC141'],
                              'Ementa: "Regulamenta o § 3º do art. 198 da Constituição Federal para dispor sobre os valores mínimos a serem '
                              'aplicados anualmente ... em ações e serviços públicos de saúde; estabelece os critérios de rateio...".',
                              'O § 3º exige lei complementar sobre os percentuais mínimos em saúde, os critérios de rateio e as normas de '
                              'fiscalização. A LC 141 é essa lei, com remissão expressa.', IN_FORCE, route='art. 1º',
                              notes='O § 3º exige reavaliação pelo menos a cada cinco anos; registrado para revalidação editorial futura.'),
    'CORRC0-2053DEF59022': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC142'],
                              'Ementa: "Regulamenta o § 1º do art. 201 ..., no tocante à aposentadoria da pessoa com deficiência segurada do RGPS".',
                              'Após a EC 103/2019, o § 1º tem dois incisos: (I) segurados com deficiência e (II) exposição a agentes nocivos. A LC 142 '
                              'disciplina só a hipótese da pessoa com deficiência. O target vai para o inciso I, sem fan-out ao parágrafo inteiro.',
                              IN_FORCE, route='art. 1º', target='CF88:ART.201:PAR.1:INC.I'),
    'CORRC0-67B5D9C94E07': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['L8213'],
                              'Lei 8.213/1991, art. 41-A: "O valor dos benefícios em manutenção será reajustado, anualmente, na mesma data do '
                              'reajuste do salário mínimo ... com base no INPC".',
                              'O § 4º assegura o reajustamento para preservar o valor real "conforme critérios definidos em lei". O art. 41-A '
                              'define esses critérios. A natureza muda de COMPLEMENTA para REGULAMENTA.', IN_FORCE, route='art. 41-A'),
    'CORRC0-362157C332DE': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC109'],
                              'LC 109/2001, art. 3º, IV: a ação do Estado visa "assegurar aos participantes e assistidos o pleno acesso às '
                              'informações relativas à gestão de seus respectivos planos de benefícios".',
                              'O § 1º manda a lei complementar assegurar o pleno acesso às informações da gestão, e o art. 3º, IV, da LC 109 '
                              'reproduz e concretiza o comando. A natureza muda de COMPLEMENTA para REGULAMENTA.', IN_FORCE, route='art. 3º'),
    'CORRC0-C8087244A9DB': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['L8069'],
                              'ECA: Capítulo V, "Do Direito à Profissionalização e à Proteção no Trabalho" (art. 60: proibição de trabalho a menores '
                              'de 14 anos, salvo aprendiz); garantias processuais (arts. 110 e 111); excepcionalidade da internação (art. 121).',
                              'O § 3º enumera os aspectos da proteção especial (idade mínima, direitos trabalhistas, garantias processuais, '
                              'brevidade da privação de liberdade). O ECA disciplina esses aspectos.', IN_FORCE, route='art. 60',
                              scope=('NON_EXCLUSIVE',)),
    'CORRC0-8D80396BDEEB': D3('APPROVE', 'ALTA', 'COMPLEMENTA', ['L8069'],
                              'ECA, crimes: art. 240 (cena de sexo explícito ou pornográfica com criança ou adolescente) e art. 244-A '
                              '(submissão à prostituição ou exploração sexual).',
                              'O § 4º manda a lei punir severamente o abuso, a violência e a exploração sexual. O ECA tipifica parte dessas condutas; '
                              'o Código Penal tipifica outras.', IN_FORCE, route='art. 240', scope=('NON_EXCLUSIVE', 'ESCOPO_PARCIAL')),
    'CORRC0-A2C12E99BECD': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['L8069'],
                              'ECA, Subseção IV "Da Adoção": art. 39 ("A adoção de criança e de adolescente reger-se-á segundo o disposto nesta '
                              'Lei") e adoção internacional (arts. 51 a 52-D).',
                              'O § 5º manda a lei estabelecer casos e condições da adoção, inclusive por estrangeiros. O ECA é essa lei. A natureza '
                              'muda de COMPLEMENTA para REGULAMENTA.', IN_FORCE, route='art. 39', scope=('NON_EXCLUSIVE',)),
    'CORRC0-E86B55D28D44': D3('HOLD', 'BAIXA', None, ['L14701', 'CF88'], 'Lei 14.701/2023, art. 4º (conceito de terras tradicionalmente ocupadas).',
                              HOLD_14701, L14701_T,
                              notes='Confirmar em fonte oficial (STF/Planalto) a situação atual de ADC 87 e ADIs 7582, 7583 e 7586 antes de decidir.'),
    'CORRC0-E0C9C2F5CDBD': D3('HOLD', 'BAIXA', None, ['L14701', 'CF88'], 'Lei 14.701/2023 (regulamenta o art. 231; aproveitamento de recursos em terras indígenas).',
                              HOLD_14701, L14701_T,
                              notes='Além do status no STF, identificar o artigo da lei que disciplina a participação nos resultados da lavra (§ 3º, "na forma da lei").'),
    'CORRC0-FC57ED913387': D3('HOLD', 'BAIXA', None, ['L14701', 'CF88'], 'Lei 14.701/2023 (regulamenta o art. 231).',
                              HOLD_14701 + ' O § 6º exige, além disso, lei complementar para o relevante interesse público da União, e a Lei '
                              '14.701 é ordinária.', L14701_T,
                              notes='Espécie normativa (LO × LC exigida pelo § 6º) a verificar.'),
    'CORRC0-7F28FCF12C37': D3('APPROVE', 'MEDIA', 'COMPLEMENTA', ['LC7', 'CF88'],
                              'LC 7/1970, ementa: "Institui o Programa de Integração Social". Parte dos dispositivos aparece "(Revogado pela Lei '
                              'Complementar nº 26, de 1975)".',
                              'O caput do art. 239 cita nominalmente a LC 7/1970 como lei criadora do PIS, cuja arrecadação a Constituição '
                              'redireciona. É remissão expressa ao diploma de origem; a destinação atual está na Lei 7.998/1990.', IN_FORCE,
                              route='art. 1º', notes='Norma parcialmente revogada (LC 26/1975); vínculo útil como origem do PIS citada pelo texto.'),
    'CORRC0-D2D0CD6A150D': D3('APPROVE', 'MEDIA', 'COMPLEMENTA', ['LC8', 'CF88'],
                              'LC 8/1970, ementa: "Institui o Programa de Formação do Patrimônio do Servidor Público". Parte dos dispositivos foi '
                              'revogada pela LC 26/1975.',
                              'Remissão expressa do caput do art. 239 à lei criadora do PASEP, com o mesmo raciocínio da LC 7/1970.', IN_FORCE,
                              route='art. 1º', notes='Norma parcialmente revogada (LC 26/1975).'),
    'CORRC0-5C8AFC368627': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['L7998'],
                              'Lei 7.998/1990, art. 1º: regula o seguro-desemprego e "o abono de que tratam ... o art. 239". Art. 9º: "É assegurado '
                              'o recebimento de abono salarial anual...".',
                              'O § 3º assegura o abono anual aos empregados que ganham até o limite constitucional. O art. 9º da Lei 7.998 '
                              'disciplina o abono.', IN_FORCE, route='art. 9º'),
    'CORRC0-7867B93D94DA': D3('ADJUST', 'MEDIA', 'COMPLEMENTA', ['L7998'],
                              'Lei 7.998/1990, art. 11, IV: entre os recursos do FAT, "o produto da arrecadação da contribuição adicional pelo '
                              'índice de rotatividade, de que trata o § 4º do art. 239".',
                              'A lei destina ao FAT a contribuição adicional do § 4º, mas não verifiquei nela a disciplina de cálculo e cobrança. '
                              'A relação é direta e parcial (destinação). A natureza muda de REGULAMENTA para COMPLEMENTA.', IN_FORCE,
                              route='art. 11', scope=('ESCOPO_PARCIAL',)),
    'CORRC0-F2C3596A37CB': D3('ADJUST', 'ALTA', 'COMPLEMENTA', ['LC146', 'CF88'],
                              'Ementa: "Estende a estabilidade provisória prevista na alínea b do inciso II do art. 10 do ADCT à trabalhadora '
                              'gestante, nos casos de morte desta, a quem detiver a guarda de seu filho".',
                              'A remissão expressa é à alínea b. A LC 146 complementa a garantia, estendendo-a ao guardião. O target vai do '
                              'inciso II para a alínea b.', IN_FORCE, route='art. 1º', target='ADCT:ART.10:INC.II:AL.b', scope=('TRANSITORIA',),
                              notes='Target do ADCT: o status do motor (UNKNOWN_VALIDITY) bloqueia o overlay atual (dívida da C0).'),
    'CORRC0-A28C8B1C8F51': D3('APPROVE', 'ALTA', 'COMPLEMENTA', ['LC160', 'CF88'],
                              'LC 160/2017, ementa: convênio para remissão de créditos e reinstituição de benefícios fiscais do ICMS concedidos em '
                              'desacordo com a alínea g do inciso XII do § 2º do art. 155. O art. 3º trata dos benefícios reinstituídos e prazos.',
                              'O § 2º do art. 128 do ADCT manda reduzir os benefícios do art. 3º da LC 160, sem aplicar o § 2º-A desse artigo. A '
                              'relação é expressa e operativa na transição.',
                              TS('TRANSITIONAL', revalidate_on='2033-01-01',
                                 note='benefícios do ICMS reduzidos de 2029 a 2032 pelo ADCT, art. 128; extinção do ICMS em 2033'),
                              route='art. 3º', scope=('TRANSITORIA',),
                              notes='Target do ADCT: o status do motor bloqueia o overlay atual.'),
}

NEW_CANDIDATE_BACKLOG = [
    BL('Lei nº 8.213/1991 (arts. 57 e 58, aposentadoria especial)', 'LEI:8213/1991', 'CF88:ART.201:PAR.1:INC.II',
       'o inciso II (exposição a agentes nocivos) é hipótese distinta da LC 142, que cobre só o inciso I', 'CORRC0-2053DEF59022', 'MEDIUM',
       'vínculo distinto, sem herança do inciso I; exige verificação própria após a EC 103/2019'),
    BL('Decreto-Lei nº 2.848/1940 (Código Penal, crimes contra a dignidade sexual)', 'DL:2848/1940', 'CF88:ART.227:PAR.4',
       'o § 4º é concretizado também pelo Código Penal (NON_EXCLUSIVE com o ECA)', 'CORRC0-8D80396BDEEB', 'LOW',
       'fora da fila HIGH original'),
]


def build():
    q, pool, _ = B3.remaining_pool(json.loads(B3.OUT_IN.read_text(encoding='utf-8'))['selection']['candidate_ids'])
    return B3.build_batch('BATCH04', 'CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH04', [x['candidate_id'] for x in pool], REVIEW, SOURCES,
                          NEW_CANDIDATE_BACKLOG, dict(B3.BASE), 'HIGH original - Batch01 - Batch02 - Batch03 - C1A - duplicatas; TODOS os restantes',
                          q, len(pool), [])


if __name__ == '__main__':
    B3.main(build, (OUT_IN, OUT_DEC, OUT_MD))
