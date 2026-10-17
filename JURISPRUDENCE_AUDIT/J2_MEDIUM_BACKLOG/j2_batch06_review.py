"""J2 BATCH06 (MEDIUM, 1st) — review of the 10 selected recommendations. Official STF sources consulted on 2026-10-17 in the built-in browser
(sha256 = rendered innerText), J2A sources reused (P1 Planalto, S1/S2 ADI 3392/3423), archived official corpus (J4). PROPOSALS ONLY.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from j2_review_common import make_decisions  # noqa: E402

D = '2026-10-17'
_J2A = json.loads((HERE.parent / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json').read_text(encoding='utf-8'))['sources']
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'


def _s(title, ident, url, sha, proves):
    return dict(tier='A', org='STF', title=title, identifier=ident, url=url, accessed_on=D, method='navegador embutido (innerText)',
                dom_text_sha256=sha, proves=proves)


def P(pid, klass, number, judgment, publication, **kw):
    return dict(id=pid, court='STF', klass=klass, number=number, judgment=judgment, publication=publication, **kw)


SOURCES = {
    'P1': dict(_J2A['P1'], reused_from='J2A',
               proves_here='Art. 114: "Vide ADIN 3392" e "Vide ADIN 3432" no caput (anotação de toda a EC 45); "Vide ADI 3423/3392/3431/3432/3520" no '
                           '§ 2º e "Vide ADI 3423/3520/3392/3432" no § 3º; NENHUMA anotação no § 1º. Art. 102 (caput e § 2º): só "Vide ADIN 3392" '
                           '(anotação genérica da EC 45). Art. 198: "Vide ADPF 672".'),
    'S1': dict(_J2A['S1'], reused_from='J2A'), 'S2': dict(_J2A['S2'], reused_from='J2A'),
    'W1': _s('Jurisprudência — ADPF 672 MC-Ref (convertido em mérito)', 'ADPF 672', JUR.format('ADPF%20672'),
             '725dbec9e9648f92bffa0d23d900dbb0ef97368ecaae17fb18d35223ea037915',
             'Pleno, Rel. Min. Alexandre de Moraes, j. 13/10/2020, DJe 29/10/2020: referendo convertido em julgamento definitivo de mérito; '
             'competência comum (art. 23, II e IX), concorrente (art. 24, XII), suplementar municipal (art. 30, II) e "descentralização '
             'político-administrativa do Sistema de Saúde (art. 198, CF)".'),
    'W2': _s('Súmula Vinculante 5 (página oficial)', 'SV 5', 'https://jurisprudencia.stf.jus.br/pages/search/seq-sumula741/false',
             '54106231d6e2208f5d18537ea0bb47e408d62b777c14011d1801ad6ffc0da3f3',
             'Enunciado; aprovação 07/05/2008; DJe 16/05/2008; "Referência Legislativa: Constituição Federal de 1988, art. 5º, LV".'),
    'W3': _s('Repercussão Geral — Tema 855 (página do tema)', 'Tema 855 / RE 806339', 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=855',
             '0cd1763bf9b2f0538db5140111eb8fd4c7bb8eebc6b2cd92e48573887b694e0f',
             'Título "Definição do alcance do art. 5º, XVI, da Constituição Federal" (aviso prévio e liberdade de reunião); trânsito em julgado '
             '14/06/2022. Tese no corpus oficial arquivado (J4).'),
}
JOINT_3423 = dict(record='ADI 3423 (no mesmo sentido: ADI 3392, 3432, 3520)', relation='SAME_JUDGMENT_SAME_SCOPE (ementa única publicada)',
                  judgment='Pleno, 29/05/2020 (sessão virtual)', scope=['CF88:ART.114:PAR.2', 'CF88:ART.114:PAR.3'],
                  model='registro conjunto com aliases, como ADI 7047/7064 (ex.: "ADI 3392/3423/3432/3520")')
EV_3423 = ('Art. 1º, da Emenda Constitucional nº 45/2004, na parte em que deu nova redação ao art. 114, §§ 2º e 3º, da Constituição Federal. '
           'Necessidade de "mútuo acordo" para ajuizamento do Dissídio Coletivo. Legitimidade do MPT para ajuizar Dissídio Coletivo em caso de greve '
           'em atividade essencial. Ação direta julgada improcedente.')


def _fp(rid_target, ns_evidence, reason):
    return dict(precedents=[P('STF:ADI:3392', 'ADI', '3392', 'Pleno, 29/05/2020 (com ADI 3423)', 'DJe 18/06/2020')],
                namespace='CF88', namespace_evidence=ns_evidence, temporal_version='NOT_APPLICABLE',
                temporal_note='O dispositivo indicado não foi objeto da ação.', target_check='FAIL', recommended_targets=[],
                decision='REJECT_FALSE_POSITIVE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (improcedente)',
                sources=['S1', 'S2', 'P1'], evidence_excerpt=EV_3423, reason=reason)


def _joint(pid, number, targets, decision, reason, check):
    return dict(precedents=[P(pid, 'ADI', number, 'Pleno, 29/05/2020 (julgamento conjunto com a ADI 3423)', 'DJe 2020')],
                namespace='CF88', namespace_evidence='A ementa (ADI 3423, mesmo sentido 3392/3432/3520) cita "art. 114, §§ 2º e 3º, da Constituição Federal".',
                temporal_version='CURRENT', temporal_note='Art. 114, §§ 2º e 3º na redação da EC 45/2004 (vigente).', target_check=check,
                recommended_targets=targets, decision=decision, confidence='HIGH', status_processual='mérito julgado (improcedente)',
                sources=['S1', 'P1'], evidence_excerpt=EV_3423, joint_judgment=JOINT_3423, reason=reason)


REVIEW = {
    'J0-BL-086': _fp('CF88:ART.102', 'É a CF, mas a ação tratou do art. 114, §§ 2º e 3º; o art. 102 só tem a anotação genérica "Vide ADIN 3392" da EC 45.',
                     'Falso positivo da anotação genérica da EC 45/2004, o mesmo padrão dos arts. 92 e 98 rejeitados no Batch01.'),
    'J0-BL-088': _fp('CF88:ART.102:PAR.2', 'Idem: o § 2º do art. 102 (efeito vinculante, EC 45) só tem a anotação genérica.',
                     'Falso positivo da anotação genérica da EC 45/2004; a ADI 3392 não trata do efeito vinculante.'),
    'J0-BL-102': _joint('STF:ADI:3392', '3392', ['CF88:ART.114:PAR.2', 'CF88:ART.114:PAR.3'], 'REALLOCATE_RECOMMENDED',
                        'A anotação no caput do art. 114 é a genérica da EC 45; o julgado atinge os §§ 2º (comum acordo no dissídio coletivo) e 3º '
                        '(MPT na greve em atividade essencial). Proposta: vincular nesses parágrafos, com registro conjunto do grupo da ADI 3423.',
                        'GRANULARITY'),
    'J0-BL-103': _joint('STF:ADI:3432', '3432', ['CF88:ART.114:PAR.2', 'CF88:ART.114:PAR.3'], 'REALLOCATE_RECOMMENDED',
                        'Mesma situação do J0-BL-102 (mesmo julgamento e mesma ementa): um único registro conjunto cobre os dois.', 'GRANULARITY'),
    'J0-BL-111': dict(
        precedents=[P('STF:ADI:3432', 'ADI', '3432', 'Pleno, 29/05/2020 (com ADI 3423)', 'DJe 26/06/2020')],
        namespace='CF88', namespace_evidence='O Planalto não anota nenhuma ADI no § 1º do art. 114; a ementa trata só dos §§ 2º e 3º.',
        temporal_version='NOT_APPLICABLE', temporal_note='O § 1º (arbitragem) não foi objeto da ação.', target_check='FAIL', recommended_targets=[],
        decision='REJECT_FALSE_POSITIVE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (improcedente)', sources=['S1', 'P1'],
        evidence_excerpt=EV_3423,
        reason='A ADI 3432 não tratou do § 1º do art. 114; o vínculo foi gerado pela proximidade com os §§ 2º e 3º.'),
    'J0-BL-116': _joint('STF:ADI:3392', '3392', ['CF88:ART.114:PAR.3'], 'PROMOTE_RECOMMENDED',
                        'O § 3º (legitimidade do MPT para o dissídio na greve em atividade essencial) foi objeto expresso e foi declarado constitucional. '
                        'Usar o registro conjunto do grupo da ADI 3423.', 'PASS'),
    'J0-BL-117': _joint('STF:ADI:3432', '3432', ['CF88:ART.114:PAR.3'], 'PROMOTE_RECOMMENDED',
                        'Mesmo julgamento e mesmo escopo do J0-BL-116: um único vínculo pelo registro conjunto.', 'PASS'),
    'J0-BL-144': dict(
        precedents=[P('STF:ADPF:672', 'ADPF', '672', 'Pleno, 13/10/2020 (MC-Ref convertido em mérito)', 'DJe 29/10/2020',
                      rapporteur='Min. Alexandre de Moraes')],
        namespace='CF88', namespace_evidence='A ementa cita a "descentralização político-administrativa do Sistema de Saúde (art. 198, CF, e art. 7º da Lei '
                                             '8.080/1990)"; a lei é complemento, o art. 198 é o parâmetro.',
        temporal_version='CURRENT', temporal_note='Art. 198 (caput e diretrizes) vigente.', target_check='PASS', recommended_targets=['CF88:ART.198'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (conversão do referendo)', sources=['W1', 'P1'],
        evidence_excerpt='prescrevendo ainda a descentralização político-administrativa do Sistema de Saúde (art. 198, CF, e art. 7º da Lei 8.080/1990). '
                         'Proposta de conversão de referendo de medida cautelar em julgamento definitivo de mérito.',
        reason='Julgado de mérito (o referendo foi convertido) sobre o federalismo sanitário: a União coordena, mas não afasta medidas de Estados e '
               'Municípios. Contexto da Covid-19. ADPF não está validada no aparelho.'),
    'J0-BL-002': dict(
        precedents=[P('STF:RG:855', 'RG', '855', 'RE 806339 (Rel. Min. Marco Aurélio); tese 2020', 'trânsito em julgado 14/06/2022')],
        namespace='CF88', namespace_evidence='O título oficial do tema é "Definição do alcance do art. 5º, XVI, da Constituição Federal".',
        temporal_version='CURRENT', temporal_note='Art. 5º, XVI na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.5:INC.XVI'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='tese fixada; trânsito em julgado', sources=['W3'],
        evidence_excerpt='A exigência constitucional de aviso prévio relativamente ao direito de reunião é satisfeita com a veiculação de informação que permita '
                         'ao poder público zelar para que seu exercício se dê de forma pacífica. (art. 5º, XVI, da Constituição Federal)',
        reason='Tese vinculante sobre o aviso prévio da liberdade de reunião, exatamente o objeto do art. 5º, XVI. Tese disponível no corpus oficial '
               'arquivado (formato J4).'),
    'J0-BL-004': dict(
        precedents=[P('STF:SV:5', 'SV', '5', 'aprovação 07/05/2008', 'DJe e DOU 16/05/2008')],
        namespace='CF88', namespace_evidence='A referência legislativa oficial é "Constituição Federal de 1988, art. 5º, LV".',
        temporal_version='CURRENT', temporal_note='Art. 5º, LV na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.5:INC.LV'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='súmula vinculante vigente', sources=['W2'],
        evidence_excerpt='A falta de defesa técnica por advogado no processo administrativo disciplinar não ofende a Constituição. Referência Legislativa: '
                         'Constituição Federal de 1988, art. 5º, LV.',
        reason='SV cuja referência legislativa oficial é o art. 5º, LV (ampla defesa). Tipo SV validado; texto no corpus oficial arquivado.'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
