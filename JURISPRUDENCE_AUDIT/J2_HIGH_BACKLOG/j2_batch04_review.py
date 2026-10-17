"""J2 BATCH04 (HIGH, last 5) — review of the selected recommendations. Official STF sources consulted on 2026-10-17 in the built-in browser
(sha256 = rendered innerText) + archived official RG corpus (J4, 2026-09-21). PROPOSALS ONLY (AWAITING_USER_RATIFICATION).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from j2_review_common import make_decisions  # noqa: E402

D = '2026-10-17'
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'


def _s(title, ident, url, sha, proves):
    return dict(tier='A', org='STF', title=title, identifier=ident, url=url, accessed_on=D, method='navegador embutido (innerText)',
                dom_text_sha256=sha, proves=proves)


def P(pid, klass, number, judgment, publication, **kw):
    return dict(id=pid, court='STF', klass=klass, number=number, judgment=judgment, publication=publication, **kw)


SOURCES = {
    'V1': _s('Repercussão Geral — Tema 835 (página do tema)', 'Tema 835 / RE 848826', 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=835',
             '1b3d6fa98be24d1d5fcf5307f17daf60576a516176c545b3aeeaef2fd0ace681',
             'Discussão "à luz dos arts. 5º, XXXIV, a, XXXV, LIV e LV, 31, § 2º, 71, I, 75, e 93, IX"; Rel. Min. Luís Roberto Barroso; '
             'trânsito em julgado 08/10/2019. Tese no corpus oficial arquivado (J4).'),
    'V2': _s('Jurisprudência — ADI 336', 'ADI 336', JUR.format('ADI%20336'), '0a6a19fc471fd91cd050a9f5641eb4d22a3b8198c0b2a5fb44d1fe7c571bfe01',
             'Pleno, Rel. Min. Eros Grau, j. 10/02/2010, DJe 17/09/2010: Constituição de Sergipe; "O artigo 35 da Constituição do Brasil prevê as '
             'hipóteses de intervenção dos Estados nos Municípios. A Constituição sergipana acrescentou outras hipóteses" (inconstitucional).'),
    'V3': _s('Jurisprudência — ADI 7369', 'ADI 7369', JUR.format('ADI%207369'), 'e5814ff5311de056317d3a2a54ec7d4ae973c2c44b803dcff4789902db26603b',
             'Pleno, Rel. Min. Cármen Lúcia, j. 13/05/2024, DJe 08/08/2024: hipóteses de intervenção estadual taxativas (art. 34, VII e art. 35); '
             'princípios sensíveis de observância obrigatória pelos Estados, sem necessidade de reprodução na Constituição estadual.'),
    'V4': _s('Jurisprudência — AI 343461 AgR', 'AI 343461', JUR.format('AI%20343461'), '0578345990f1979c850077ab9fc01fce2dbba4d5cb4a0d4681c0e62ee62d210a',
             '2ª Turma, Rel. Min. Celso de Mello, j. 18/06/2002, DJ 29/11/2002: intervenção estadual por inexecução de ordem judicial '
             '"(CF, ART. 35, IV)"; procedimento de caráter político-administrativo; inviável o recurso extraordinário.'),
    'V5': _s('Jurisprudência — ADPF 378 (MC e ED)', 'ADPF 378', JUR.format('ADPF%20378'), '4685348c08714fc638a6a38403a8e6266105a88388e1a2c266b2a761247ea146',
             'MC: Pleno, red. p/ acórdão Min. Roberto Barroso, j. 17/12/2015, DJe 08/03/2016: Câmara autoriza (art. 51, I); Senado processa e '
             'julga, incluído o juízo inicial de instauração (art. 52, I); arts. da Lei 1.079/50 não recepcionados por incompatibilidade com os '
             'arts. 51, I; 52, I; e 86, § 1º, II. ED: j. 16/03/2016.'),
    'V6': _s('Jurisprudência — MS 21564', 'MS 21564', JUR.format('MS%2021564'), '0f5aefaaca850bf7611c8f4d72fc45dd90a2f444bf72d56a8e694d7d8e9d0eef',
             'Pleno, red. p/ acórdão Min. Carlos Velloso, j. 23/09/1992, DJ 27/08/1993: "a Câmara dos Deputados ... examina a admissibilidade '
             'da acusação (C.F., art. 86, caput)" e "profere juízo político"; Senado processa e julga (art. 52, I; art. 86, § 1º, II).'),
    'V7': _s('Jurisprudência — ADI 978', 'ADI 978', JUR.format('ADI%20978'), '025e6325fa05e4bf9811dd1f549f0605d46819701aca64595695396400e6bb49',
             'Pleno, red. p/ acórdão Min. Celso de Mello, j. 19/10/1995, DJ 17/11/1995: Constituição da Paraíba; prerrogativas inerentes ao '
             'Presidente "(CF/88, ART. 86, PAR. 3. E 4.)"; imunidade à prisão cautelar não extensível ao Governador.'),
    'V8': _s('Jurisprudência — Inq 672 QO', 'Inq 672', JUR.format('Inq%20672'), '4d82e98e47f479e085dcfe5e0f5b3e76be7cfb249bb0e20fd1abba85037e8ba4',
             'Pleno, Rel. Min. Celso de Mello, j. 16/09/1992, DJ 16/04/1993: "CF, ART. 86, § 4º": imunidade temporária do Presidente à persecução '
             'penal por atos estranhos à função; exegese estrita; inaplicável a situações extrapenais.'),
    'V9': _s('Jurisprudência — Rcl 84738 AgR', 'Rcl 84738', JUR.format('Rcl%2084738'), 'd735d7e62842bb525c09bd75372762c4984ec48b1054fd7f6e201d02af631bbc',
             '2ª Turma, Rel. Min. Dias Toffoli, j. 14/04/2026, DJe 03/09/2026: membro do MP mantém o foro (TJ) mesmo por crime não relacionado à '
             'função; "enquanto não sobrevier o julgamento do Tema nº 1.147 da Repercussão Geral ou eventual pronunciamento do Plenário".'),
}

REVIEW = {
    'J0-BL-046': dict(
        precedents=[P('STF:RG:835', 'RG', '835', 'RE 848826 (Rel. Min. Luís Roberto Barroso); tese de 2016', 'trânsito em julgado 08/10/2019')],
        namespace='CF88', namespace_evidence='A tese é fixada "para os fins do art. 1º, I, g, da LC 64/1990" (alerta), mas define a competência das '
                                             'Câmaras e o quórum de 2/3 do art. 31, § 2º; o tema é discutido "à luz do art. 31, § 2º".',
        temporal_version='CURRENT', temporal_note='Art. 31, § 2º na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.31:PAR.2'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='tese fixada; trânsito em julgado', sources=['V1'],
        evidence_excerpt='Para os fins do art. 1º, inciso I, alínea "g", da Lei Complementar 64, a apreciação das contas de prefeitos, tanto as de '
                         'governo quanto as de gestão, será exercida pelas Câmaras Municipais, com o auxílio dos Tribunais de Contas competentes, cujo '
                         'parecer prévio somente deixará de prevalecer por decisão de 2/3 dos vereadores. (arts. 31, § 2º, 71, I, da Constituição Federal)',
        reason='Complementa o Tema 157 (Batch03) no mesmo § 2º: também as contas de gestão do prefeito são julgadas pela Câmara. O alerta de namespace '
               '(LC 64/90) foi conferido: a lei é o contexto da inelegibilidade, e a regra aplicada é a do art. 31, § 2º.'),
    'J0-BL-051': dict(
        precedents=[P('STF:ADI:7369', 'ADI', '7369', 'Pleno, 13/05/2024', 'DJe 08/08/2024', target='CF88:ART.35:INC.IV'),
                    P('STF:AI:343461', 'AI', '343461', '2ª Turma, 18/06/2002 (AgR)', 'DJ 29/11/2002', target='CF88:ART.35:INC.IV'),
                    P('STF:ADI:336', 'ADI', '336', 'Pleno, 10/02/2010', 'DJe 17/09/2010', target='CF88:ART.35')],
        namespace='CF88', namespace_evidence='As ADIs julgaram Constituições estaduais (MT, SE) usando como parâmetro o art. 35 da CF; o AI cita '
                                             '"CF, ART. 35, IV". O objeto é norma estadual, mas o dispositivo interpretado é a CF.',
        temporal_version='CURRENT', temporal_note='Art. 35 na redação originária.', target_check='PASS_WITH_SPLIT',
        recommended_targets=['CF88:ART.35:INC.IV', 'CF88:ART.35'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='mérito julgado (ADIs no Pleno; AI na Turma)', sources=['V3', 'V4', 'V2'],
        evidence_excerpt='Na intervenção estadual, as hipóteses excepcionais estão taxativas e exaustivamente previstas no inc. VII do art. 34 e no art. 35 '
                         'da Constituição da República. INTERVENÇÃO ESTADUAL EM MUNICÍPIO - INEXECUÇÃO DE ORDEM JUDICIAL (CF, ART. 35, IV). '
                         'Constituição do Estado de Sergipe.',
        reason='Divisão por alvo. ADI 7369 e AI 343461 vão para o inciso IV: princípios sensíveis e natureza político-administrativa da representação '
               'interventiva. A ADI 336 (taxatividade das hipóteses) vai para o art. 35 como um todo. AI é tipo novo no aparelho.'),
    'J0-BL-067': dict(
        precedents=[P('STF:MS:21564', 'MS', '21564', 'Pleno, 23/09/1992', 'DJ 27/08/1993', target='CF88:ART.86'),
                    P('STF:ADPF:378', 'ADPF', '378', 'Pleno, MC 17/12/2015; ED 16/03/2016', 'DJe 08/03/2016',
                      target='CF88:ART.86:PAR.1:INC.II', provisional=True, additional_target='CF88:ART.52:INC.I')],
        namespace='CF88', namespace_evidence='MS 21564 cita "C.F., art. 86, caput"; ADPF 378 cita "arts. 51, I; 52, I; e 86, § 1º, II, todos da CF/1988".',
        temporal_version='CURRENT', temporal_note='Art. 86 na redação originária.', target_check='PASS_WITH_SPLIT',
        recommended_targets=['CF88:ART.86', 'CF88:ART.86:PAR.1:INC.II', 'CF88:ART.52:INC.I'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='MS 21564: mérito; ADPF 378: medida cautelar do Plenário (com ED)', sources=['V6', 'V5'],
        revalidation=dict(applies_to='STF:ADPF:378', trigger='JULGAMENTO_DE_MERITO_OU_EXTINCAO', max_age_days=180, last_verified_on=D,
                          check='https://portal.stf.jus.br/processos/listarProcessos.asp?classe=ADPF&numeroProcesso=378'),
        evidence_excerpt='No regime da Carta de 1988, a Câmara dos Deputados examina a admissibilidade da acusação (C.F., art. 86, caput). Medida cautelar '
                         'em ADPF. Não foram recepcionados os arts. da Lei nº 1.079/1950 incompatíveis com os arts. 51, I; 52, I; e 86, § 1º, II.',
        reason='O MS 21564 (mérito, caso Collor) interpreta o caput do art. 86: a Câmara faz juízo político de admissibilidade. A ADPF 378 (rito do caso '
               'Dilma) é medida cautelar do Plenário, por isso entra marcada como provisória e com revalidação: no § 1º, II do art. 86 e no art. 52, I. '
               'MS e ADPF não estão validados no aparelho.'),
    'J0-BL-068': dict(
        precedents=[P('STF:ADI:978', 'ADI', '978', 'Pleno, 19/10/1995', 'DJ 17/11/1995', target='CF88:ART.86:PAR.3'),
                    P('STF:INQ:672', 'INQ', '672', 'Pleno, 16/09/1992 (QO)', 'DJ 16/04/1993', target='CF88:ART.86:PAR.4')],
        namespace='CF88', namespace_evidence='ADI 978: objeto é a Constituição da Paraíba, parâmetro "CF/88, art. 86, par. 3. e 4."; Inq 672: "CF, art. 86, § 4º".',
        temporal_version='CURRENT', temporal_note='Art. 86, §§ 3º e 4º na redação originária.', target_check='PASS_WITH_SPLIT',
        recommended_targets=['CF88:ART.86:PAR.3', 'CF88:ART.86:PAR.4'], decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado',
        sources=['V7', 'V8'],
        evidence_excerpt='PRERROGATIVAS INERENTES AO PRESIDENTE DA REPUBLICA ENQUANTO CHEFE DE ESTADO (CF/88, ART. 86, PAR. 3. E 4.). Constituição do Estado da '
                         'Paraiba. O art. 86, § 4º, da Constituição exclui o Presidente, durante o mandato e por atos estranhos ao seu exercício, da persecução.',
        reason='Divisão por alvo: a ADI 978 vai para o § 3º (imunidade à prisão cautelar, exclusiva do Presidente) e o Inq 672 QO para o § 4º. O backlog '
               'punha os dois no § 3º. A ADI 1021 da nota não foi verificada e fica de fora. Inq é tipo novo no aparelho.'),
    'J0-BL-072': dict(
        precedents=[P('STF:RCL:84738', 'RCL', '84738', '2ª Turma, 14/04/2026 (AgR)', 'DJe 03/09/2026', rapporteur='Min. Dias Toffoli')],
        namespace='CF88', namespace_evidence='A decisão mantém o processo no TJ (foro do membro do MP estadual), competência do art. 96, III.',
        temporal_version='CURRENT', temporal_note='Art. 96, III na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.96:INC.III'],
        decision='PROMOTE_PROVISIONAL_RECOMMENDED', confidence='MEDIUM',
        status_processual='orientação de Turma condicionada ao Tema 1147 (RG, pendente) ou a pronunciamento do Plenário', sources=['V9'],
        revalidation=dict(trigger='JULGAMENTO_DO_TEMA_1147_OU_PLENARIO', max_age_days=90, last_verified_on=D,
                          check='https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=1147'),
        evidence_excerpt='enquanto não sobrevier o julgamento do Tema nº 1.147 da Repercussão Geral ou eventual pronunciamento do Plenário, referida '
                         'prerrogativa abarca quaisquer crimes comuns.',
        reason='Pertinente ao art. 96, III, mas a própria ementa diz que é provisória e depende do Tema 1147. Proposta como provisória, com gatilho no '
               'julgamento do tema. Rcl é tipo novo no aparelho.'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
