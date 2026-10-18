"""PORTABILITY PILOT — Código Civil (CC2002). Official evidence captured on 2026-10-18 (built-in browser, sha256 of the rendered
innerText; Planalto by direct download). Data only: what each official page says. The pilot NEVER publishes anything; every
assessment is PORTABILITY_PILOT_ONLY and nothing here is human-approved.
"""
D = '2026-10-18'
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'
TEMA = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={}'
Q1_URL = ('https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&queryString=%22do%20C%C3%B3digo%20Civil%22%20e%20%22repercuss%C3%A3o%20geral%22'
          '&sinonimo=true&plural=true&page=1&pageSize=50&sort=_score&sortBy=desc')


def _s(org, title, url, sha, proves, method='navegador embutido (innerText)'):
    return dict(tier='A', org=org, title=title, url=url, accessed_on=D, method=method, sha256=sha, proves=proves)


SOURCES = {
    'PL1': _s('Planalto', 'Lei 10.406/2002 — texto compilado', 'https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm',
              'c50bf11c560ea431e73fac7aab453e6ace2624462ce54a416c990cf6577faf5f', 'Anotações "Vide" e notas de redação por dispositivo.',
              method='download direto (curl)'),
    'Q1': _s('STF', 'Pesquisa de jurisprudência: "do Código Civil" e "repercussão geral" (50 primeiros, relevância)', Q1_URL,
             '9e95fedf1d911b7042cfc8e108b7847e1e1f9ad00ad77dd480e6b54271219931',
             '611 acórdãos; os 50 primeiros resultados com órgão, data, tema e trechos de ementa/tese que citam artigos do Código Civil.'),
    'T498': _s('STF', 'Tema 498', TEMA.format(498), '67813660fc22a2f3020e8ed8e37a83af8f56caa401f0b21471d8e47ce02774f8',
               'Leading case RE 646721; trânsito em julgado 28/03/2019.'),
    'T809': _s('STF', 'Tema 809', TEMA.format(809), '5dd5633ff4584d1d4d9a661f9e7ed1f09623d360e51b18113635f7de83cf0ee0',
               'Validade do art. 1.790 do CC (vs. art. 1.829); leading case RE 878694; trânsito em julgado 04/12/2018.'),
    'T529': _s('STF', 'Tema 529', TEMA.format(529), '93f3adff4d56c612cb2a95698cedfb45a97ef94b1b09e4e213af9b8153e89180',
               'Uniões concomitantes e rateio de pensão; leading case RE 1045273; trânsito em julgado 29/05/2021.'),
    'T1236': _s('STF', 'Tema 1236', TEMA.format(1236), 'd2500318a1c089a75cf4589639ec082b25b20dde96c02b724b6c306880461b14',
                'Constitucionalidade do art. 1.641, II, do CC; leading case ARE 1309642; trânsito em julgado 10/04/2024.'),
    'T932': _s('STF', 'Tema 932', TEMA.format(932), 'ee0d5e6495f1ae97bab47815d090b0a02df6415d70d278c07d34dde749333cb6',
               'Teoria do risco do art. 927, parágrafo único, do CC; leading case RE 828040; trânsito em julgado 05/08/2020.'),
    'T526': _s('STF', 'Tema 526', TEMA.format(526), '0c769d30b368097183079c8940602e4b566d9e6f7fc35311f5dc0c8ec4402a63',
               'Concubinato e pensão por morte (arts. 201, V, e 226, § 3º, da CF); leading case RE 883168; trânsito em julgado 02/04/2022.'),
    'T1194': _s('STF', 'Tema 1194', TEMA.format(1194), '343e767aff28193ed7c9a4bb68215589edd80bceafb9a399f7cf53f199d482aa',
                'Prescrição da execução de dano ambiental; leading case ARE 1352872; trânsito em julgado 16/04/2025.'),
    'A4815': _s('STF', 'Jurisprudência — ADI 4815', JUR.format('ADI%204815'), 'b42151c9c4280bd3c968ed04aa563b098e3037fddb505eece71330e8a77d3f48',
                'Pleno, j. 10/06/2015, publ. 01/02/2016: interpretação conforme aos arts. 20 e 21 do CC, sem redução de texto (biografias).'),
    'A6792': _s('STF', 'Jurisprudência — ADI 6792 (com ADI 7055)', JUR.format('ADI%206792'),
                'c8b36453d332a177a5c72959995d20b694b4080bb675b7b34e10d63a497aa101',
                'Pleno, j. 22/05/2024, publ. 04/04/2025: assédio judicial contra jornalistas; "ADI 7.055 que se julga totalmente procedente, para '
                'conferir interpretação conforme ... aos arts. 186 e 927 do Código Civil"; julgamento conjunto.'),
    'STJ1': _s('STJ', 'STJ — pesquisa de súmulas (canal de descoberta STJ)', 'https://scon.stj.jus.br/SCON/sumstj/toc.jsp?livre=%27203%27.num.&b=SUMU',
               'a533a79828ed5e2529b6f076db404f5a6be63c72ec03bed4db86a554d32df13a',
               'BLOQUEADO por desafio anti-robô (não contornado). Nenhum conteúdo do STJ foi acessado.'),
}

# Official facts per precedent (canonical id -> facts). alias: process numbers that identify the same record (leading case of a theme).
PRECEDENTS = {
    'STF:ADI:4815': dict(tipo='adi', number='4815', judgment_year=2015, status_text='Julgamento: 10/06/2015 ... AÇÃO DIRETA JULGADA PROCEDENTE',
                         sources=['A4815'], evidence='AÇÃO DIRETA JULGADA PROCEDENTE PARA DAR INTERPRETAÇÃO CONFORME À CONSTITUIÇÃO AOS ARTS. 20 E 21 DO '
                                                     'CÓDIGO CIVIL, SEM REDUÇÃO DE TEXTO.', joint_with=[]),
    'STF:ADI:6792': dict(tipo='adi', number='6792', judgment_year=2024, status_text='Julgamento: 22/05/2024 ... Pedido parcialmente procedente',
                         sources=['A6792'], evidence='ADI 7.055 que se julga totalmente procedente, para conferir interpretação conforme a Constituição '
                                                     'aos arts. 186 e 927 do Código Civil', joint_with=['STF:ADI:7055']),
    'STF:ADI:7055': dict(tipo='adi', number='7055', judgment_year=2024, status_text='julgada em conjunto com a ADI 6792 (22/05/2024)',
                         sources=['A6792'], evidence='ADI 7.055 que se julga totalmente procedente, para conferir interpretação conforme a Constituição '
                                                     'aos arts. 186 e 927 do Código Civil', joint_with=['STF:ADI:6792']),
    'STF:RG:498': dict(tipo='repercussao_geral', number='498', judgment_year=2017, alias=['STF:RE:646721'], status_text='Trânsito em Julgado - em 28/03/2019',
                       sources=['T498', 'Q1'], evidence='É inconstitucional a distinção de regimes sucessórios entre cônjuges e companheiros prevista no art. '
                                                         '1.790 do CC/2002, devendo ser aplicado ... o regime do art. 1.829 do CC/2002.', joint_with=[]),
    'STF:RG:809': dict(tipo='repercussao_geral', number='809', judgment_year=2017, alias=['STF:RE:878694'], status_text='Trânsito em Julgado - em 04/12/2018',
                       sources=['T809', 'Q1'], evidence='É inconstitucional a distinção de regimes sucessórios entre cônjuges e companheiros prevista no art. '
                                                         '1.790 do CC/2002, devendo ser aplicado ... o regime do art. 1.829 do CC/2002.', joint_with=[]),
    'STF:RG:529': dict(tipo='repercussao_geral', number='529', judgment_year=2020, alias=['STF:RE:1045273'], status_text='Trânsito em Julgado - 29/05/2021',
                       sources=['T529', 'Q1'], evidence='A preexistência de casamento ou de união estável de um dos conviventes, ressalvada a exceção do '
                                                         'artigo 1723, § 1º, do Código Civil, impede o reconhecimento de novo vínculo referente ao mesmo período',
                       joint_with=[]),
    'STF:RG:1236': dict(tipo='repercussao_geral', number='1236', judgment_year=2024, alias=['STF:ARE:1309642'], status_text='Trânsito em Julgado - 10/04/2024',
                        sources=['T1236', 'Q1'], evidence='art. 1.641, II, do Código Civil, atribuindo-lhe o sentido de norma dispositiva, que deve prevalecer '
                                                          'à falta de convenção das partes em sentido diverso', joint_with=[]),
    'STF:RG:932': dict(tipo='repercussao_geral', number='932', judgment_year=2020, alias=['STF:RE:828040'], status_text='Trânsito em Julgado - 05/08/2020',
                       sources=['T932', 'Q1'], evidence='O artigo 927, parágrafo único, do Código Civil é compatível com o artigo 7º, XXVIII, da Constituição '
                                                         'Federal', joint_with=[]),
    'STF:RG:526': dict(tipo='repercussao_geral', number='526', judgment_year=2021, alias=['STF:RE:883168'], status_text='Trânsito em Julgado - 02/04/2022',
                       sources=['T526', 'Q1'], evidence='tendo o Código Civil traçado sua distinção em face do concubinato (art. 1.727 do Código Civil '
                                                         'Brasileiro) ... art. 1.521 do Código Civil – que trata dos impedimentos para casar', joint_with=[]),
    'STF:RG:1194': dict(tipo='repercussao_geral', number='1194', judgment_year=2025, alias=['STF:ARE:1352872'], status_text='Trânsito em Julgado - 16/04/2025',
                        sources=['T1194', 'Q1'], evidence='É imprescritível a pretensão executória e inaplicável a prescrição intercorrente na execução de '
                                                          'reparação de dano ambiental ... art. 206-A do Código Civil', joint_with=[]),
}

# STF search Q1, discovery adapter #2: the 50 captured rows as (header, órgão, julgamento, tema, CC articles extracted by the capture regex,
# citation text of the first CC mention). Rule applied by the builder (not by hand): Pleno + Tema + merits (no "RG" suffix) + >= 1 article.
Q1_ROWS = [
    ('RE 878694 RG', 'Tribunal Pleno', '16/04/2015', '809', ['1.790'], 'validade do art. 1.790 do Código Civil'),
    ('RE 1045273', 'Tribunal Pleno', '21/12/2020', '529', ['1.727', '1.566'], '1.566, I, do Código Civil'),
    ('ARE 1309642', 'Tribunal Pleno', '01/02/2024', '1236', ['1.641', '1.639, § 2º'], 'art. 1.641, II, do Código Civil'),
    ('RE 828040', 'Tribunal Pleno', '12/03/2020', '932', ['927'], 'O artigo 927, parágrafo único, do Código Civil é compatível'),
    ('RE 1167478 RG', 'Tribunal Pleno', '06/06/2019', '1053', [], ''),
    ('RE 828075 RG', 'Tribunal Pleno', '06/10/2016', '920', ['927'], ''),
    ('RE 646721 RG', 'Tribunal Pleno', '10/11/2011', '498', [], ''),
    ('RE 878694', 'Tribunal Pleno', '10/05/2017', '809', ['1790'], 'art. 1790 do Código Civil'),
    ('RE 611639 RG', 'Tribunal Pleno', '09/12/2010', '349', [], ''),
    ('RE 1269353 RG', 'Tribunal Pleno', '16/12/2021', '1191', ['406'], ''),
    ('RE 646721', 'Tribunal Pleno', '10/05/2017', '498', ['1790'], 'art. 1790 do Código Civil'),
    ('RE 883168', 'Tribunal Pleno', '03/08/2021', '526', ['1.521', '1.727'], 'art. 1.521 do Código Civil'),
    ('RE 835818 AgR-segundo-AgR', 'Tribunal Pleno', '15/03/2021', '', [], ''),
    ('RE 1531050 AgR', 'Segunda Turma', '24/03/2025', '', ['1.723, § 1º'], ''),
    ('RE 566471', 'Tribunal Pleno', '26/09/2024', '6', [], ''),
    ('ARE 1352872', 'Tribunal Pleno', '31/03/2025', '1194', ['206'], 'art. 206-A do Código Civil'),
    ('RE 1355870', 'Tribunal Pleno', '06/10/2025', '1153', [], ''),
    ('RE 631537', 'Tribunal Pleno', '22/05/2020', '361', [], ''),
    ('RE 1387795', 'Tribunal Pleno', '13/10/2025', '1232', [], ''),
]
Q1_ROWS_TOTAL = 50   # the other 31 rows are Turma decisions (Rcl/ARE/MS AgR) without a theme: excluded by the rule before any judgment

# Human assessment of each candidate (what a reviewer concludes reading the official evidence). PORTABILITY_PILOT_ONLY: never ratified.
# key = (discovered target, canonical precedent)
ASSESSMENT = {
    ('CC2002:ART.20', 'STF:ADI:4815'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.20'], False, 'Ementa nomeia os arts. 20 e 21 do CC.'),
    ('CC2002:ART.21', 'STF:ADI:4815'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.21'], False, 'Idem.'),
    ('CC2002:ART.186', 'STF:ADI:6792'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.186'], True,
                                        'Julgamento conjunto ADI 6792/7055: um único registro conjunto (como ADI 7047/7064 na CF) é decisão humana.'),
    ('CC2002:ART.186', 'STF:ADI:7055'): ('DUPLICATE_RECOMMENDATION', [], True, 'Mesmo acórdão da ADI 6792 (julgamento conjunto).'),
    ('CC2002:ART.927', 'STF:ADI:6792'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.927'], True, 'Idem ao art. 186 (registro conjunto).'),
    ('CC2002:ART.927', 'STF:ADI:7055'): ('DUPLICATE_RECOMMENDATION', [], True, 'Mesmo acórdão da ADI 6792.'),
    ('CC2002:ART.1790', 'STF:RG:498'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1790'], False, 'Tese declara inconstitucional o art. 1.790.'),
    ('CC2002:ART.1790', 'STF:RG:809'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1790'], False, 'Mesma tese, tema próprio (registro separado).'),
    ('CC2002:ART.1829', 'STF:RG:498'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1829'], False, 'Tese manda aplicar o regime do art. 1.829.'),
    ('CC2002:ART.1829', 'STF:RG:809'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1829'], False, 'Idem.'),
    ('CC2002:ART.1727', 'STF:RG:529'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.1723:PAR.1'], True,
                                       'A tese ressalva a exceção do art. 1.723, § 1º; o art. 1.727 é só fundamento.'),
    ('CC2002:ART.1566', 'STF:RG:529'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.1566:INC.I'], True,
                                       'Ementa cita "1.566, I" (dever de fidelidade); pertinência secundária, decisão humana.'),
    ('CC2002:ART.1641', 'STF:RG:1236'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.1641:INC.II'], True,
                                        'Tese sobre o inciso II (maior de 70 anos); o extrator só pegou o artigo.'),
    ('CC2002:ART.1639:PAR.2', 'STF:RG:1236'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1639:PAR.2'], True,
                                              'Citado entre parênteses (mudança de regime); pertinência a confirmar.'),
    ('CC2002:ART.927', 'STF:RG:932'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.927:PAR.UNICO'], False,
                                      'Tese nomeia o parágrafo único; o parser de citação já aponta o alvo certo.'),
    ('CC2002:ART.1521', 'STF:RG:526'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], True,
                                       'Tema previdenciário; o art. 1.521 (impedimentos) aparece só como fundamento.'),
    ('CC2002:ART.1727', 'STF:RG:526'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1727'], True,
                                       'Concubinato (art. 1.727) é o conceito decisivo, mas o tema é previdenciário; baixa confiança.'),
    ('CC2002:ART.206', 'STF:RG:1194'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.206-A'], True,
                                       'O texto oficial diz "206-A" (prescrição intercorrente); o extrator truncou para 206.'),
}
