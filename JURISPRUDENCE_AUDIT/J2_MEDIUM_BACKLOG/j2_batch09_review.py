"""J2 BATCH09 (MEDIUM, 4th) — review of the 10 selected recommendations. Official STF sources consulted on 2026-10-17 in the built-in browser
(sha256 = rendered innerText): Repercussão Geral theme pages and the STF jurisprudence search. Reused: J2A (P1 Planalto, S1/S2 ADI 3392/3423,
S3 ADI 4425, S5/S6 ADI 7047/7064), Batch06 W1 (ADPF 672). Coverage checked against the INSTALLED baseline (J2C, 261) and the ratified Batch02
overlay (J2E). PROPOSALS ONLY.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from j2_review_common import make_decisions  # noqa: E402

D = '2026-10-17'
_J2A = json.loads((HERE.parent / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json').read_text(encoding='utf-8'))['sources']
_B06 = json.loads((HERE / 'J2_BATCH06_DECISIONS.json').read_text(encoding='utf-8'))['sources']
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'
TEMA = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={}'


def _s(title, ident, url, sha, proves):
    return dict(tier='A', org='STF', title=title, identifier=ident, url=url, accessed_on=D, method='navegador embutido (innerText)',
                dom_text_sha256=sha, proves=proves)


def P(pid, klass, number, judgment, publication, **kw):
    return dict(id=pid, court='STF', klass=klass, number=number, judgment=judgment, publication=publication, **kw)


SOURCES = {
    'P1': dict(_J2A['P1'], reused_from='J2A'), 'S1': dict(_J2A['S1'], reused_from='J2A'), 'S2': dict(_J2A['S2'], reused_from='J2A'),
    'S3': dict(_J2A['S3'], reused_from='J2A'), 'S5': dict(_J2A['S5'], reused_from='J2A'), 'S6': dict(_J2A['S6'], reused_from='J2A'),
    'W1': dict(_B06['W1'], reused_from='BATCH06'),
    'Z1': _s('Jurisprudência — ADPF 964', 'ADPF 964', JUR.format('ADPF%20964'), 'acf12139558da827dec0e1cb15ebd2c4344170431656865cd984046c150be3f3',
             'Pleno, Rel. Min. Rosa Weber, j. 10/05/2023, publ. 17/08/2023: decreto de indulto de 21/04/2022; indulto como ato político sujeito a '
             'controle judicial; desvio de finalidade caracterizado; "Indulto não atinge os efeitos secundários da pena, tanto os penais quanto os '
             'extrapenais".'),
    'Z2': _s('Repercussão Geral — Tema 841', 'Tema 841 / RE 1002295', TEMA.format(841), 'f974898465308d6f8c8a20f1fc2d5453f14d2f406b84b9154b4997db8de13470',
             'Título: "Constitucionalidade do art. 114, § 2º, da Constituição Federal, alterado pela EC 45/2004, que prevê a necessidade de comum '
             'acordo ..."; leading case RE 1002295; trânsito em julgado 21/10/2020.'),
    'Z3': _s('Repercussão Geral — Tema 184', 'Tema 184 / RE 593727', TEMA.format(184), 'aa3129173503ec0343a9365464b80f32ce64592b5fda0b86cc2a0528a511bdf7',
             'Título: "Poder de investigação do Ministério Público"; descrição: à luz dos arts. 5º, LIV e LV; 129, III e VIII; e 144, IV, § 4º; '
             'leading case RE 593727; trânsito em julgado 02/12/2025.'),
    'Z4': _s('Jurisprudência — HC 70648', 'HC 70648', JUR.format('HC%2070648'), '834468b26bc5da4606dc1471bec7ad36fac33fe1585ce5e36f156c4eb8cd3bfd',
             '1ª Turma, Rel. Min. Moreira Alves, j. 09/11/1993, publ. 04/03/1994: sentido da restrição do habeas corpus quanto às punições '
             'disciplinares militares (art. 142, § 2º); exame dos quatro pressupostos de legalidade.'),
    'Z5': _s('Repercussão Geral — Tema 201', 'Tema 201 / RE 593849', TEMA.format(201), '57b67c6fbe10df663a4ee15e0a281ed94a07d333cb46a52d753c8a8b26c8066e',
             'Título: "Restituição da diferença de ICMS pago a mais no regime de substituição tributária"; descrição: à luz do art. 150, § 7º; '
             'leading case RE 593849; trânsito em julgado 22/02/2018.'),
    'Z6': _s('Jurisprudência — ADI 2777', 'ADI 2777', JUR.format('ADI%202777'), 'f09d9484c4333965b0bb825de87a5364c524de6421aa2eb99d80960a741279ec',
             'Pleno, Rel. Min. Cezar Peluso, red. p/ acórdão Min. Ricardo Lewandowski, j. 19/10/2016, publ. 30/06/2017: "Com base no § 7° do art. 150 '
             'da Constituição Federal, é constitucional exigir-se a restituição de quantia cobrada a maior"; ADI improcedente.'),
    'Z7': _s('Repercussão Geral — Tema 1093', 'Tema 1093 / RE 1287019', TEMA.format(1093), '438d3e4df738df40c54cfc38995c9758e4451c999e281c68b7b15e5ce9726314',
             'Título: necessidade de lei complementar para a cobrança do DIFAL nas operações interestaduais com consumidor final não contribuinte, '
             'nos termos da EC 87/2015; descrição: art. 155, § 2º, VII e VIII, na redação da EC 87/2015; leading case RE 1287019; trânsito em '
             'julgado 30/03/2022.'),
    'Z8': _s('Jurisprudência — MI 7300 (mérito e EDs)', 'MI 7300', JUR.format('MI%207300'), 'eba22a157bae70fa007a45a5e4d7811d81bdaa450454755aa81ec1b38d8fe929',
             'Mérito: Pleno, Rel. Min. Marco Aurélio, red. p/ acórdão Min. Gilmar Mendes, j. 27/04/2021, publ. 23/08/2021: renda básica de cidadania '
             '(Lei 10.835/2004), arts. 3º, III; 6º; 23, X da CF e art. 81 do ADCT. EDs rejeitados em 23/11/2021. Nenhuma menção ao art. 107-A do ADCT.'),
    'Z9': _s('Repercussão Geral — Tema 509', 'Tema 509 / RE 655265', TEMA.format(509), '80bf814619df3fd28c6b791de82ccbcba96445201cff2db29d8a2a73b844851b',
             'Título: "Momento de comprovação do triênio de atividade jurídica para ingresso no cargo de juiz substituto"; à luz dos arts. 5º, caput, '
             '37, I, e 93, I; leading case RE 655265; trânsito em julgado 10/05/2019.'),
    'Z10': _s('Jurisprudência — ADI 3460', 'ADI 3460', JUR.format('ADI%203460'), '923798be5ec0f3137e33fe225a194581a14a30969ce10fcb065e5aaf7ea44fb0',
              'Pleno, Rel. Min. Carlos Britto, j. 31/08/2006, publ. 15/06/2007: resolução do CSMP do MPDFT; triênio de atividade jurídica para a '
              'carreira do Ministério Público, contado da conclusão do curso e comprovado na inscrição; ação improcedente.'),
    'Z11': _s('Jurisprudência — MS 28226 AgR', 'MS 28226', JUR.format('MS%2028226'), 'b2355da150d9124fe2db92146a6d484758c3f5e456f8b0f915b3032366bb8f85',
              '1ª Turma, Rel. Min. Luiz Fux, j. 04/08/2015, publ. 26/08/2015: concurso da magistratura (TJ/MA); "ART. 129, § 3º"; atividade '
              'jurídica pode incluir cargo não privativo de bacharel.'),
}

REVIEW = {
    'J0-BL-145': dict(
        precedents=[P('STF:ADPF:672', 'ADPF', '672', 'Pleno, 13/10/2020 (MC-Ref convertido em mérito)', 'DJe 29/10/2020', rapporteur='Min. Alexandre de Moraes')],
        namespace='CF88', namespace_evidence='Mesma anotação oficial do art. 198 ("Vide ADPF 672") tratada no Batch06.', temporal_version='CURRENT',
        temporal_note='Art. 198 vigente.', target_check='DUPLICATE', recommended_targets=[], decision='DUPLICATE_RECOMMENDATION', confidence='HIGH',
        status_processual='mérito julgado (conversão do referendo)', sources=['W1', 'P1'],
        evidence_excerpt='prescrevendo ainda a descentralização político-administrativa do Sistema de Saúde (art. 198, CF, e art. 7º da Lei 8.080/1990).',
        reason='Mesmo target (CF88:ART.198) e mesmo precedente da J0-BL-144, já proposta no Batch06 (PROMOTE). Um segundo vínculo duplicaria a ficha.'),
    'J0-BL-078': dict(
        precedents=[P('STF:ADI:4425', 'ADI', '4425', 'Pleno, mérito 14/03/2013; QO 25/03/2015', 'DJe 19/12/2013; DJe 04/08/2015'),
                    P('STF:ADI:7047', 'ADI', '7047', 'Pleno, sessão virtual de 30/11/2023 (conjunto com a ADI 7064)', 'ver fonte S5'),
                    P('STF:ADI:7064', 'ADI', '7064', 'Pleno, sessão virtual de 30/11/2023 (conjunto com a ADI 7047)', 'ver fonte S6')],
        namespace='CF88', namespace_evidence='Art. 100 da CF (precatórios).', temporal_version='MIXED',
        temporal_note='A ADI 4425 julgou a redação da EC 62/2009; as ADIs 7047/7064, a da EC 113/2021 (e o art. 107-A do ADCT, EC 114/2021).', target_check='DUPLICATE',
        recommended_targets=[], decision='DUPLICATE_RECOMMENDATION', confidence='HIGH', status_processual='mérito julgado (as três)',
        sources=['S3', 'S5', 'S6'],
        evidence_excerpt='ADI 4425 (§§ 2º, 9º, 10 e 12 na redação da EC 62/2009, com modulação) e ADI 7047/7064 (30/11/2023): inconstitucionais o art. 100, § 9º e o art. 101, § 5º do ADCT (EC 113/21); interpretação conforme ao art. 100, § 11.',
        reason='Os três precedentes já estão tratados: a ADI 4425 no art. 100 foi proposta no Batch06 (J0-BL-075, com nota temporal) e está instalada '
               'nos §§ 9º e 12 (J2C); a ADI 7064 está instalada no § 9º (J2C); o par 7047/7064 foi ratificado no § 11 e no ADCT 101, § 5º (Batch02/J2E). '
               'Um vínculo no caput duplicaria fichas. Nada novo a vincular.'),
    'J0-BL-066': dict(
        precedents=[P('STF:ADPF:964', 'ADPF', '964', 'Pleno, 10/05/2023 (julgamento conjunto com as ADPFs 965, 966 e 967)', 'publ. 17/08/2023',
                      rapporteur='Min. Rosa Weber')],
        namespace='CF88', namespace_evidence='O objeto é o decreto presidencial de indulto de 21/04/2022; o parâmetro é a competência do art. 84, XII.',
        temporal_version='CURRENT', temporal_note='Art. 84, XII na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.84:INC.XII'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado', sources=['Z1'],
        evidence_excerpt='Indulto como ato político, espécie de ato administrativo. Elementos do ato administrativo. Controle pelo Poder Judiciário. '
                         'Legitimidade. Desvio de finalidade caracterizado. ... Indulto não atinge os efeitos secundários da pena, tanto os penais quanto '
                         'os extrapenais.',
        reason='Precedente de mérito do Pleno sobre os limites do indulto presidencial (art. 84, XII): o indulto é controlável por desvio de finalidade e '
               'não alcança os efeitos secundários da pena. Rótulo "ADPF 964": o tipo ADPF ainda não foi validado no aparelho. As ADPFs 965 a 967, '
               'do mesmo julgamento, não foram consultadas uma a uma.'),
    'J0-BL-112': dict(
        precedents=[P('STF:RG:841', 'RG', '841', 'RE 1002295 (Rel. Min. Marco Aurélio)', 'trânsito em julgado 21/10/2020'),
                    P('STF:ADI:3423', 'ADI', '3423', 'Pleno, 29/05/2020 (grupo ADI 3423/3392/3432/3520)', 'DJe 18/06/2020'),
                    P('STF:ADI:3392', 'ADI', '3392', 'Pleno, 29/05/2020 (com ADI 3423)', 'DJe 18/06/2020')],
        namespace='CF88', namespace_evidence='O título oficial do Tema 841 cita o "art. 114, § 2º"; o grupo da ADI 3423 julgou o § 2º (comum acordo) e o § 3º.',
        temporal_version='CURRENT', temporal_note='§ 2º na redação da EC 45/2004, vigente.', target_check='WRONG_TARGET', recommended_targets=[],
        decision='ALREADY_COVERED', confidence='HIGH', status_processual='Tema 841: trânsito em julgado; ADIs: mérito julgado',
        sources=['Z2', 'S1', 'S2', 'P1'],
        evidence_excerpt='Constitucionalidade do art. 114, § 2º, da Constituição Federal, alterado pela EC 45/2004, que prevê a necessidade de comum acordo '
                         'entre as partes como requisito para o ajuizamento de dissídio coletivo de natureza econômica.',
        reason='O § 1º (arbitragem) não é objeto de nenhum dos precedentes: a anotação oficial do § 1º não remete a eles. O Tema 841 já está instalado no '
               '§ 2º (base de 261), e o grupo da ADI 3423 já foi proposto nos §§ 2º e 3º no Batch06 (J0-BL-102/116). Nada a vincular no § 1º.'),
    'J0-BL-121': dict(
        precedents=[P('STF:RG:184', 'RG', '184', 'RE 593727 (Rel. Min. Cezar Peluso; tese 2015)', 'trânsito em julgado 02/12/2025')],
        namespace='CF88', namespace_evidence='A descrição oficial do tema cita os arts. 129, III e VIII, e 144, IV, § 4º.', temporal_version='CURRENT',
        temporal_note='Art. 129 (funções institucionais do MP) na redação vigente.', target_check='PASS', recommended_targets=['CF88:ART.129'],
        decision='PROMOTE_RECOMMENDED', confidence='MEDIUM', status_processual='tese fixada; trânsito em julgado em 02/12/2025', sources=['Z3', 'P1'],
        evidence_excerpt='Poder de investigação do Ministério Público. Recurso extraordinário em que se discute, à luz dos artigos 5º, LIV e LV; 129, III e '
                         'VIII; e 144, IV, § 4°, da Constituição Federal, a constitucionalidade, ou não, da realização de procedimento investigatório de '
                         'natureza penal pelo Ministério Público.',
        reason='Tema central das funções do MP (art. 129). Fica no artigo, não em um inciso, porque o tema toca os incisos III e VIII ao mesmo tempo. '
               'Confiança MEDIUM: a página do tema não exibe o texto da tese, que foi conferido só pela nota oficial da recomendação. O trânsito '
               'em julgado é recente (02/12/2025).'),
    'J0-BL-124': dict(
        precedents=[P('STF:HC:70648', 'HC', '70648', '1ª Turma, 09/11/1993', 'publ. 04/03/1994', rapporteur='Min. Moreira Alves')],
        namespace='CF88', namespace_evidence='Ementa: "punições disciplinares militares (artigo 142, PAR. 2., da Constituição Federal)".',
        temporal_version='CURRENT', temporal_note='O § 2º do art. 142 mantém a redação originária, a mesma interpretada em 1993.', target_check='PASS',
        recommended_targets=['CF88:ART.142:PAR.2'], decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='acórdão de Turma (1993)',
        sources=['Z4'],
        evidence_excerpt='não impedia que se examinasse, nele, a ocorrencia dos quatro pressupostos de legalidade dessas transgressões (a hierarquia, o '
                         'poder disciplinar, o ato ligado a função e a pena susceptivel de ser aplicada disciplinarmente), continua valido para o disposto '
                         'no PAR. 2. do ARTIGO 142 da atual Constituição',
        reason='Precedente clássico que delimita a vedação do § 2º: cabe HC para examinar a legalidade da punição disciplinar militar, não o mérito. É '
               'acórdão de Turma, sem efeito vinculante. Tipo HC: só existe no protótipo de firmware; nunca usar o rótulo "OUTRO".'),
    'J0-BL-130': dict(
        precedents=[P('STF:RG:201', 'RG', '201', 'RE 593849 (Rel. Min. Edson Fachin; tese 2016)', 'trânsito em julgado 22/02/2018'),
                    P('STF:ADI:2777', 'ADI', '2777', 'Pleno, 19/10/2016', 'publ. 30/06/2017', rapporteur='red. p/ acórdão Min. Ricardo Lewandowski')],
        namespace='CF88', namespace_evidence='A descrição do tema e a ementa da ADI citam expressamente o "art. 150, § 7º".', temporal_version='CURRENT',
        temporal_note='§ 7º incluído pela EC 3/1993, vigente.', target_check='PASS', recommended_targets=['CF88:ART.150:PAR.7'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='Tema 201: trânsito em julgado; ADI 2777: mérito julgado (improcedente)',
        sources=['Z5', 'Z6'],
        evidence_excerpt='Com base no § 7° do art. 150 da Constituição Federal, é constitucional exigir-se a restituição de quantia cobrada a maior, nas '
                         'hipóteses de substituição tributária para frente em que a operação final resultou em valores inferiores àqueles utilizados '
                         'para efeito de incidência do ICMS.',
        reason='O Tema 201 e a ADI 2777 foram julgados juntos em outubro de 2016 e fixam a mesma orientação sobre o § 7º: é devida a restituição quando a '
               'base de cálculo efetiva é menor que a presumida. Propõe-se uma ficha por precedente: "Tema 201" e "ADI 2777".'),
    'J0-BL-132': dict(
        precedents=[P('STF:RG:1093', 'RG', '1093', 'RE 1287019 (Rel. Min. Marco Aurélio)',
                      'trânsito em julgado 30/03/2022')],
        namespace='CF88', namespace_evidence='A descrição oficial cita o "artigo 155, § 2º, incisos VII e VIII, na redação dada pela EC 87/2015".',
        temporal_version='CURRENT', temporal_note='O inciso VII mantém a redação da EC 87/2015, a mesma julgada no tema.', target_check='PASS',
        recommended_targets=['CF88:ART.155:PAR.2:INC.VII'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='tese fixada; trânsito em julgado', sources=['Z7'],
        evidence_excerpt='se a instituição do diferencial de alíquota de ICMS, conforme previsto no artigo 155, § 2º, incisos VII e VIII, na redação dada '
                         'pela Emenda Constitucional nº 87/2015, exige, ou não, a edição de lei complementar disciplinando o tema',
        reason='O DIFAL instituído pela EC 87/2015 depende de lei complementar. O inciso VII é o dispositivo do DIFAL; o VIII só reparte a '
               'responsabilidade. O seletor registrou "Tema 1" por truncamento do regex: o identificador correto, conferido na fonte, é "Tema 1093".'),
    'J0-BL-170': dict(
        precedents=[P('STF:ADI:7064', 'ADI', '7064', 'Pleno, sessão virtual de 30/11/2023 (conjunto com a ADI 7047)', 'ver fonte S6'),
                    P('STF:MI:7300', 'MI', '7300', 'Pleno, 27/04/2021 (EDs rejeitados em 23/11/2021)', 'publ. 23/08/2021',
                      rapporteur='red. p/ acórdão Min. Gilmar Mendes')],
        namespace='ADCT', namespace_evidence='Art. 107-A do ADCT (incluído pela EC 114/2021).', temporal_version='MIXED',
        temporal_note='O MI 7300 (27/04/2021; EDs em 23/11/2021) é anterior à EC 114/2021, que incluiu o art. 107-A; por isso não interpreta esse '
                      'dispositivo.', target_check='ALREADY_COVERED', recommended_targets=[], decision='ALREADY_COVERED', confidence='HIGH',
        status_processual='ADI 7064: mérito julgado; MI 7300: mérito julgado', sources=['S6', 'Z8', 'P1'],
        evidence_excerpt='Mandado de injunção. Renda básica de cidadania. Lei 10.835/2004. Art. 2º. Omissão do Poder Executivo Federal em fixar o valor do '
                         'benefício.',
        reason='A ADI 7064 já foi ratificada no ADCT 107-A (Batch02/J2E, rótulo "ADI 7064"). O MI 7300 trata da renda básica (Lei 10.835/2004; arts. '
               '3º, III, 6º e 23, X da CF; art. 81 do ADCT) e é anterior ao art. 107-A, logo não deve ser vinculado nele. Uma eventual relação do MI '
               '7300 com outro dispositivo exigiria recomendação própria; não é proposta aqui. Tipo MI: ainda não existe no aparelho.'),
    'J0-BL-070': dict(
        precedents=[P('STF:RG:509', 'RG', '509', 'RE 655265 (Rel. Min. Luiz Fux)', 'trânsito em julgado 10/05/2019'),
                    P('STF:ADI:3460', 'ADI', '3460', 'Pleno, 31/08/2006', 'publ. 15/06/2007', rapporteur='Min. Carlos Britto'),
                    P('STF:MS:28226', 'MS', '28226', '1ª Turma, 04/08/2015 (AgR)', 'publ. 26/08/2015', rapporteur='Min. Luiz Fux')],
        namespace='CF88', namespace_evidence='O título oficial do Tema 509 trata do ingresso no cargo de juiz substituto (art. 93, I). A ADI 3460 e o MS '
                                             '28226 têm como parâmetro o art. 129, § 3º.',
        temporal_version='CURRENT', temporal_note='Art. 93, I na redação da EC 45/2004, vigente.', target_check='ALREADY_COVERED', recommended_targets=[],
        decision='ALREADY_COVERED', confidence='HIGH', status_processual='Tema 509: trânsito em julgado; ADI 3460 e MS 28226 AgR: julgados',
        sources=['Z9', 'Z10', 'Z11'],
        evidence_excerpt='Momento de comprovação do triênio de atividade jurídica para ingresso no cargo de juiz substituto.',
        reason='O Tema 509 já está instalado em CF88:ART.93:INC.I (base de 261). A ADI 3460 (carreira do MPDFT) e o MS 28226 AgR (que aplica o art. 129, '
               '§ 3º, a um concurso da magistratura) são de outro dispositivo e só reforçariam a mesma orientação. Não se propõe vínculo novo.'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
