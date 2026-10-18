"""J2 BATCH10 (MEDIUM, 5th; first batch after the J2I freeze) — review of the 10 selected recommendations. Official sources consulted on
2026-10-18 in the built-in browser (sha256 = rendered innerText, or innerText of the fetched page for "A Constituição e o Supremo" and the
process tabs): STF "A Constituição e o Supremo", STF jurisprudence search, Repercussão Geral theme pages, STF process portal; the STJ súmula
search was blocked by an anti-robot challenge (NOT bypassed). Coverage checked against the FROZEN physical baseline J2I_FROZEN_315_198 and the
ratified Batches 01–09. PROPOSALS ONLY (AWAITING_USER_RATIFICATION).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from j2_review_common import make_decisions  # noqa: E402

D = '2026-10-18'
_J2A = json.loads((HERE.parent / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json').read_text(encoding='utf-8'))['sources']
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'
TEMA = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={}'
CS = 'https://portal.stf.jus.br/constituicao-supremo/artigo.asp?abrirBase=CF&abrirArtigo={}'


def _s(title, ident, url, sha, proves, org='STF', method='navegador embutido (innerText)'):
    return dict(tier='A', org=org, title=title, identifier=ident, url=url, accessed_on=D, method=method, dom_text_sha256=sha, proves=proves)


def _cs(art, sha, proves):
    return _s(f'A Constituição e o Supremo — art. {art}', f'CF art. {art}', CS.format(art), sha, proves,
              method='navegador embutido (fetch da página oficial; innerText)')


def P(pid, klass, number, judgment, publication, court='STF', **kw):
    return dict(id=pid, court=court, klass=klass, number=number, judgment=judgment, publication=publication, **kw)


SOURCES = {
    'P1': dict(_J2A['P1'], reused_from='J2A'),
    'K1': _s('Repercussão Geral — Tema 656', 'Tema 656 / RE 608588', TEMA.format(656), 'aff8802c42b8b9994c3a09c87869d53ff4bcacf6a33d84c607f10c6d27e47a69',
             'Título: limites da atuação legislativa local para disciplinar as atribuições das guardas municipais; à luz do art. 144, § 8º; leading '
             'case RE 608588; acórdão de mérito publicado em 22/08/2025.'),
    'K2': _s('Repercussão Geral — Tema 796', 'Tema 796 / RE 796376', TEMA.format(796), 'b1b0f25b5366cb626d5e8b7bfbd14bd0660d86248b560d2bf4eb6dc972dcd3f5',
             'Título: alcance da imunidade do ITBI (art. 156, § 2º, I) sobre imóveis incorporados acima do capital a integralizar; leading case '
             'RE 796376.'),
    'K3': _s('A Constituição e o Supremo — art. 17 (página renderizada)', 'CF art. 17', CS.format(17),
             'd71bc23eb4ebf2635ebce465c97682b9af605e98ea9cd67f4841b788e8999060',
             'Sob o § 1º ("... normas de disciplina e fidelidade partidária", red. EC 97/2017): "Inaplicabilidade da regra de perda do mandato por '
             'infidelidade partidária ao sistema eleitoral majoritário" [ADI 5.081, j. 27-5-2015, P]. O § 6º (incluído pela EC 111/2021) não tem '
             'julgado anotado.'),
    'K4': _s('Jurisprudência — ADI 5081', 'ADI 5081', JUR.format('ADI%205081'), 'd72cac96b80d1a102d0604404063ba55ddf5b37e024875bec86c2da9b67895bf',
             'Pleno, Rel. Min. Roberto Barroso, j. 27/05/2015, publ. 19/08/2015: Res. TSE 22.610/2007; "inaplicabilidade da regra de perda do '
             'mandato por infidelidade partidária ao sistema eleitoral majoritário".'),
    'K5': _cs(19, 'ce6db4af927703d1df0f25a18d438244e268c9cddd99ecab02574f5052559478',
              'Art. 19, I: "Vide ADI 4.439, red. do ac. min. Alexandre de Moraes, j. 27-9-2017, P, DJE de 21-6-2018".'),
    'K6': _cs(210, 'ac57f54587f799daa3bdbd61e6cf78add05c5c850377db3d713eaea8ea8cad89',
              'Art. 210, § 1º: ADI 4.439 (constitucionalidade do ensino religioso confessional como disciplina facultativa).'),
    'K7': _s('Jurisprudência — ADI 4439', 'ADI 4439', JUR.format('ADI%204439'), '95bf1edbf16e3f0b5437845bd24ba054a9c861a48cd998c758d569cb839a1be4',
             'Pleno, Rel. Min. Roberto Barroso, red. p/ acórdão Min. Alexandre de Moraes, j. 27/09/2017, publ. 21/06/2018: "binômio Laicidade do '
             'Estado (CF, art. 19, I)/Consagração da Liberdade religiosa"; conformidade com o art. 210, § 1º.'),
    'K8': _cs(25, 'be4fd0805b2ec2d7484c9c0956b33cd13e60f29da330ed04ca8996323673bedc',
              'Art. 25, § 3º: ADI 1.842 (red. do ac. min. Gilmar Mendes, j. 6-3-2013, P) — titularidade conjunta do interesse metropolitano; '
              'saneamento básico como função de interesse comum.'),
    'K9': _s('Jurisprudência — ADI 1842 (mérito e EDs)', 'ADI 1842', JUR.format('ADI%201842'), '32e8ae0b2c5f550fdce5a53a608c3229cf34c1f4007216346185af36c4ab54ea',
             'Mérito: Pleno, Rel. Min. Luiz Fux, red. p/ acórdão Min. Gilmar Mendes, j. 06/03/2013, publ. 16/09/2013 ("nos termos do art. 25, § 3º, '
             'da Constituição Federal"). ED, ED-segundos e ED-terceiros rejeitados em 23/11/2020 (publ. 03/12/2020).'),
    'K10': _s('Jurisprudência — ADC 12 (mérito e MC)', 'ADC 12', JUR.format('ADC%2012'), '52a60caa8019922860eeb2be5a4361df09a82007cee6181167d3b492dab78acc',
              'Mérito: Pleno, Rel. Min. Carlos Britto, j. 20/08/2008, publ. 18/12/2009: Resolução CNJ 7/2005; "caráter normativo primário, dado que '
              'arranca diretamente do § 4º do art. 103-B". MC: j. 16/02/2006.'),
    'K11': _cs(105, '50666f6fffaf2c6daebdf979bdfedc3ea0e4b142672bd5f363b949dc244ec8fc',
               'Art. 105: nenhum julgado do STF anotado no inciso III sobre recurso especial contra decisão de turma recursal (só o CC 7.090 sobre '
               'conflito de competência, art. 105, I, d).'),
    'K12': _s('STJ — pesquisa de súmulas (Súmula 203)', 'Súmula STJ 203', 'https://scon.stj.jus.br/SCON/sumstj/toc.jsp?livre=%27203%27.num.&b=SUMU',
              'a533a79828ed5e2529b6f076db404f5a6be63c72ec03bed4db86a554d32df13a',
              'BLOQUEADO: "Verificação automática em andamento ... responda ao desafio abaixo" (anti-robô). O desafio NÃO foi contornado; o conteúdo '
              'da súmula não foi acessado. O hash é da página de bloqueio.', org='STJ'),
    'K13': _cs(124, '8806dc70b76f1d0d2783f46b9922f88bf1a67e621aeb2e02a0acaa1d66b0bbcb',
               'Art. 124: julgados sobre civis na Justiça Militar quase todos de Turma (HC 83.003, HC 110.286, RMS 26.315 etc.), em sentidos '
               'casuísticos; nenhum precedente plenário de mérito sobre o tema geral.'),
    'K14': _s('Portal — ADPF 289 (abas Decisões e Andamentos)', 'ADPF 289', 'https://portal.stf.jus.br/processos/detalhe.asp?incidente=4448028',
              '3745be8066e78ea594dca9076557e27bbd3fb18942cddfdf995c9bb3c892bf68',
              'Julgamento de civis pela Justiça Militar em tempo de paz: mérito incluído na sessão virtual de 29/08/2025 e retirado de pauta em '
              '20/08/2025; conclusos ao relator (Min. Gilmar Mendes) em 08/06/2026; sem julgamento de mérito.', method='navegador embutido (fetch das abas; innerText)'),
    'K15': _cs(151, '71f46d104e804e8d08b74551f73448bc6e9ec580d9408bd16b8798513ba1767e',
               'Art. 151, III: RE 229.096 (red. do ac. min. Cármen Lúcia, j. 16-8-2007, P) — isenção prevista em tratado (GATT) não é isenção '
               'heterônoma; = AI 235.708 AgR; vide RE 543.943 AgR (tributos locais, como o ISS).'),
    'K16': _s('Jurisprudência — RE 229096', 'RE 229096', JUR.format('RE%20229096'), 'de90dfceb3fa9a7917f413513b9646cfb079b486fbf903f0b131b590eeff28fc',
              'Pleno, Rel. Min. Ilmar Galvão, red. p/ acórdão Min. Cármen Lúcia, j. 16/08/2007, publ. 11/04/2008: "ISENÇÃO DE TRIBUTO ESTADUAL '
              'PREVISTA EM TRATADO INTERNACIONAL ... ARTIGO 151, INCISO III ... NÃO CARACTERIZAÇÃO DE ISENÇÃO HETERÔNOMA".'),
}

REVIEW = {
    'J0-BL-125': dict(
        precedents=[P('STF:RG:656', 'RG', '656', 'RE 608588 (Plenário, 20/02/2025)', 'acórdão de mérito publicado em 22/08/2025')],
        namespace='CF88', namespace_evidence='O tema é decidido "à luz do art. 144, § 8º, da Constituição federal" (página oficial do tema).',
        temporal_version='CURRENT', temporal_note='Art. 144, § 8º, vigente (redação originária).', target_check='ALREADY_COVERED', recommended_targets=[],
        decision='ALREADY_COVERED', confidence='HIGH', status_processual='mérito julgado; acórdão publicado em 22/08/2025', sources=['K1'],
        evidence_excerpt='Recurso extraordinário em que se discute, à luz do art. 144, § 8º, da Constituição federal, o limite da atuação legislativa dos '
                         'municípios para fixar as atribuições de suas guardas municipais.',
        reason='O RE 608588 é o leading case do Tema 656, que já está instalado em CF88:ART.144:PAR.8 no baseline J2I (STF:RG:656). O seletor não '
               'casou "RE 608588" com "Tema 656" porque os números diferem. Nenhum vínculo novo.'),
    'J0-BL-133': dict(
        precedents=[P('STF:RG:796', 'RG', '796', 'RE 796376 (Plenário, 2020)', 'mérito julgado')],
        namespace='CF88', namespace_evidence='Título oficial: imunidade do ITBI "prevista no art. 156, § 2º, I, da Constituição".',
        temporal_version='CURRENT', temporal_note='Art. 156, § 2º, I, vigente.', target_check='ALREADY_COVERED', recommended_targets=[],
        decision='ALREADY_COVERED', confidence='HIGH', status_processual='mérito julgado', sources=['K2'],
        evidence_excerpt='Alcance da imunidade tributária do ITBI, prevista no art. 156, § 2º, I, da Constituição, sobre imóveis incorporados ao '
                         'patrimônio de pessoa jurídica.',
        reason='O RE 796376 é o leading case do Tema 796, já instalado em CF88:ART.156:PAR.2 no baseline J2I (STF:RG:796). Uma eventual descida do '
               'vínculo para o inciso I seria realocação de vínculo já aprovado, fora do escopo deste lote. Nenhum vínculo novo.'),
    'J0-BL-023': dict(
        precedents=[P('STF:ADI:5081', 'ADI', '5081', 'Pleno, 27/05/2015', 'DJe 19/08/2015', rapporteur='Min. Roberto Barroso')],
        namespace='CF88', namespace_evidence='A compilação oficial do STF anota a ADI 5081 no art. 17, § 1º (fidelidade partidária), não no § 6º.',
        temporal_version='CURRENT',
        temporal_note='A cláusula "normas de disciplina e fidelidade partidária" do § 1º existe desde a EC 52/2006 e continua na redação da EC 97/2017. '
                      'O § 6º só foi incluído pela EC 111/2021, depois do julgamento (2015); ele positiva a perda do mandato apenas para cargos '
                      'proporcionais, em linha com a ADI 5081.',
        target_check='REALLOCATED', recommended_targets=['CF88:ART.17:PAR.1'], decision='REALLOCATE_RECOMMENDED', confidence='MEDIUM',
        status_processual='mérito julgado', sources=['K3', 'K4'],
        evidence_excerpt='INAPLICABILIDADE DA REGRA DE PERDA DO MANDATO POR INFIDELIDADE PARTIDÁRIA AO SISTEMA ELEITORAL MAJORITÁRIO.',
        reason='A nota pede a situação dos eleitos pelo sistema majoritário. O precedente oficial é a ADI 5081, mas ele é anterior ao § 6º (EC '
               '111/2021) e o STF o anota no § 1º. Vincular no § 6º atribuiria ao acórdão a interpretação de um texto que ele não examinou. '
               'Proposta: § 1º. Julgamento humano necessário: o usuário pode preferir só nível de artigo (CF88:ART.17), com nota temporal.'),
    'J0-BL-027': dict(
        precedents=[P('STF:ADI:4439', 'ADI', '4439', 'Pleno, 27/09/2017', 'DJe 21/06/2018', rapporteur='Min. Alexandre de Moraes (redator)')],
        namespace='CF88', namespace_evidence='A ementa cita o "binômio Laicidade do Estado (CF, art. 19, I)"; a compilação oficial traz "Vide ADI 4.439" '
                                             'no art. 19, I, e o acórdão no art. 210, § 1º.',
        temporal_version='CURRENT', temporal_note='Art. 19, I, e art. 210, § 1º, na redação originária, vigentes.', target_check='REALLOCATED',
        recommended_targets=['CF88:ART.19:INC.I'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (improcedência)',
        sources=['K5', 'K6', 'K7'],
        evidence_excerpt='A singularidade da previsão constitucional de ensino religioso, de matrícula facultativa, observado o binômio Laicidade do '
                         'Estado (CF, art. 19, I)/Consagração da Liberdade religiosa.',
        reason='A nota é sobre laicidade e ensino religioso; o dispositivo da laicidade é o inciso I do art. 19, não o caput. O art. 210, § 1º, onde o '
               'STF ancora o acórdão, é um segundo target possível, mas fica fora da recomendação original; não é proposto aqui (decisão do usuário).'),
    'J0-BL-050': dict(
        precedents=[P('STF:ADI:1842', 'ADI', '1842', 'Pleno, 06/03/2013 (EDs rejeitados em 23/11/2020)', 'DJe 16/09/2013',
                      rapporteur='Min. Gilmar Mendes (redator)')],
        namespace='CF88', namespace_evidence='A ementa decide "nos termos do art. 25, § 3º, da Constituição Federal"; a compilação oficial anota a ADI 1.842 '
                                             'no § 3º.',
        temporal_version='CURRENT', temporal_note='Art. 25, § 3º, na redação originária, vigente.', target_check='PASS', recommended_targets=['CF88:ART.25:PAR.3'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado; três embargos de declaração rejeitados (23/11/2020)',
        sources=['K8', 'K9'],
        evidence_excerpt='A função pública do saneamento básico frequentemente extrapola o interesse local e passa a ter natureza de interesse comum no '
                         'caso de instituição de regiões metropolitanas, aglomerações urbanas e microrregiões, nos termos do art. 25, § 3º, da '
                         'Constituição Federal.',
        reason='Precedente plenário central sobre os limites da atuação estadual na região metropolitana (titularidade conjunta, vedação de '
               'concentração do poder decisório). O alvo da recomendação já é o § 3º. Nenhum julgamento conjunto aparece na ementa.'),
    'J0-BL-091': dict(
        precedents=[], namespace='CF88', namespace_evidence='Nota terminológica sobre o art. 103-A; nenhum precedente é indicado.',
        temporal_version='NOT_APPLICABLE', temporal_note='—', target_check='NOT_MATERIAL', recommended_targets=[],
        decision='REJECT_NOT_MATERIAL_RECOMMENDED', confidence='HIGH', status_processual='não se aplica', sources=['P1'],
        evidence_excerpt='Termo constitucional: súmula vinculante (o contrato ENTENDA reserva a palavra à camada JURISPRUDÊNCIA ...). A fonte canônica '
                         'remete à Lei n. 11.417, de 2006, que disciplina o procedimento, na camada de legislação.',
        reason='A nota não pede jurisprudência: trata da palavra "súmula vinculante" no texto ENTENDA e remete à Lei 11.417/2006 (camada de '
               'legislação correlata). Não há precedente a vincular; criar um vínculo genérico seria escolha editorial sem base na recomendação.'),
    'J0-BL-092': dict(
        precedents=[P('STF:ADC:12', 'ADC', '12', 'Pleno, 20/08/2008 (MC 16/02/2006)', 'DJe 18/12/2009', rapporteur='Min. Carlos Britto')],
        namespace='CF88', namespace_evidence='A ementa: a Resolução CNJ 7/2005 tem "caráter normativo primário, dado que arranca diretamente do § 4º do art. '
                                             '103-B".',
        temporal_version='CURRENT',
        temporal_note='Caput do § 4º (incluído pela EC 45/2004) inalterado; a EC 103/2019 mexeu só no inciso III, que não é o fundamento da ADC 12.',
        target_check='PASS', recommended_targets=['CF88:ART.103-B:PAR.4'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='mérito julgado (procedência)', sources=['K10'],
        evidence_excerpt='A Resolução nº 07/05 se dota, ainda, de caráter normativo primário, dado que arranca diretamente do § 4º do art. 103-B da '
                         'Carta-cidadã.',
        reason='Precedente plenário de referência sobre o poder normativo do CNJ (e seus limites: a resolução só "debulha" princípios do art. 37). '
               'Tipo ADC: rótulo existe no firmware genérico, ainda sem teste físico.'),
    'J0-BL-093': dict(
        precedents=[P('STJ:SUMULA:203', 'SUMULA_STJ', '203', 'não verificado (fonte oficial bloqueada)', 'não verificado', court='STJ')],
        namespace='CF88', namespace_evidence='Não confirmado: a página oficial do STJ não foi acessada (desafio anti-robô). A compilação do STF não anota '
                                             'julgado sobre o tema no art. 105, III.',
        temporal_version='NOT_APPLICABLE', temporal_note='Não avaliável sem a fonte oficial.', target_check='UNVERIFIED', recommended_targets=[],
        decision='UNRESOLVED_EXTERNAL', confidence='N/A', status_processual='não verificado', sources=['K12', 'K11'],
        evidence_excerpt='Verificação automática em andamento. Aguarde a verificação automática. Caso não seja redirecionado, responda ao desafio abaixo.',
        reason='O candidato natural é a Súmula 203 do STJ (recurso especial contra decisão de órgão de segundo grau dos juizados). A fonte oficial do '
               'STJ bloqueou o acesso com desafio anti-robô, que não foi contornado; nenhum texto foi presumido e não se usou fonte secundária. '
               'Mesma pendência estrutural da Súmula 403/STJ.'),
    'J0-BL-118': dict(
        precedents=[P('STF:ADPF:289', 'ADPF', '289', 'mérito pendente (retirado de pauta em 20/08/2025; conclusos em 08/06/2026)', 'não julgado',
                      rapporteur='Min. Gilmar Mendes')],
        namespace='CF88', namespace_evidence='Tema (julgamento de civis pela Justiça Militar da União) ligado ao art. 124; a compilação oficial só traz '
                                             'julgados de Turma, casuísticos.',
        temporal_version='CURRENT', temporal_note='Art. 124, vigente.', target_check='UNRESOLVED', recommended_targets=[],
        decision='UNRESOLVED_IDENTIFICATION', confidence='N/A', status_processual='ADPF 289: mérito pendente', sources=['K13', 'K14'],
        evidence_excerpt='ADPF 289 Mérito: Sessão Ordinária Virtual do Plenário 27-2025 ... Retirado de pauta.',
        reason='Não há precedente plenário de mérito sobre o tema geral: a questão está pendente na ADPF 289, e os julgados anotados são de Turma, '
               'sobre hipóteses específicas do CPM. Escolher um deles seria decisão editorial sem base suficiente. Retomar quando a ADPF 289 for '
               'julgada (ou por decisão humana de usar um julgado de Turma).'),
    'J0-BL-131': dict(
        precedents=[P('STF:RE:229096', 'RE', '229096', 'Pleno, 16/08/2007', 'DJe 11/04/2008', rapporteur='Min. Cármen Lúcia (redatora)')],
        namespace='CF88', namespace_evidence='A ementa cita o "ARTIGO 151, INCISO III, DA CONSTITUIÇÃO DA REPÚBLICA"; a compilação oficial anota o RE 229.096 '
                                             'no inciso III.',
        temporal_version='CURRENT', temporal_note='Art. 151, III, na redação originária, vigente.', target_check='REALLOCATED',
        recommended_targets=['CF88:ART.151:INC.III'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado',
        sources=['K15', 'K16'],
        evidence_excerpt='ISENÇÃO DE TRIBUTO ESTADUAL PREVISTA EM TRATADO INTERNACIONAL FIRMADO PELA REPÚBLICA FEDERATIVA DO BRASIL. ARTIGO 151, INCISO '
                         'III, DA CONSTITUIÇÃO DA REPÚBLICA. ARTIGO 98 DO CÓDIGO TRIBUTÁRIO NACIONAL. NÃO CARACTERIZAÇÃO DE ISENÇÃO HETERÔNOMA.',
        reason='Precedente plenário sobre isenção por tratado. O alvo desce do caput para o inciso III (vedação de isenção heterônoma). O RE 543.943 AgR '
               '(Turma) estende o raciocínio a tributos locais e fica como reforço, sem vínculo próprio. Tipo RE: suportado pela arquitetura, ainda '
               'sem teste físico.'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
