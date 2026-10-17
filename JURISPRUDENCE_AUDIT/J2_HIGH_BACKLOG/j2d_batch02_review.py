"""J2D BATCH02 — legal review of the 10 selected HIGH candidates (official sources; consulted 2026-10-17, J2A sources reused where the same
official pages already prove the point). Data module imported by ../build_j2d_batch02.py. Claude's review, AWAITING_USER_RATIFICATION.
Nothing here is materialized.

STF pages were read in the built-in browser (portal.stf.jus.br answers 403 to automated clients; J1.3 "fotografia por navegador" precedent);
sha256 = rendered innerText. J2A sources (P1, S4, S5, S6) are copied from J2A_BATCH01_DECISIONS.json with their original hashes and dates.
"""
import json
from pathlib import Path

ACCESSED = '2026-10-17'
_J2A = json.loads((Path(__file__).resolve().parent / 'J2A_BATCH01_DECISIONS.json').read_text(encoding='utf-8'))['sources']
SOURCES = {k: dict(_J2A[k], reused_from='J2A') for k in ('P1', 'S4', 'S5', 'S6')}
SOURCES.update({
    'T1': dict(tier='A', org='STF', title='Repercussão Geral — Tema 793 (página do tema)', identifier='Tema 793 / RE 855178',
               url='https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=793', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='e9c3a924d5fbb63de14a09fff3206f547bbd6832a5b10c3f1ddef748cc2b0fe9',
               proves='Título "Responsabilidade solidária dos entes federados pelo dever de prestar assistência à saúde"; leading case RE 855178; '
                      'Rel. Min. Luiz Fux; trânsito em julgado em 13/05/2020.'),
    'T2': dict(tier='A', org='STF', title='Jurisprudência — RE 855178 ED (Tema 793, mérito)', identifier='RE 855178 ED',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22RE%20855178%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='c286582bebc98ef5cf34ab67aaf6068754963031d4a43b5f9d38399b4eb4cfba',
               proves='Pleno, j. 23/05/2019, DJe 16/04/2020, red. p/ acórdão Min. Edson Fachin. Tese: os entes da federação, "em decorrência da '
                      'competência comum", são solidariamente responsáveis nas demandas prestacionais na área da saúde.'),
    'T3': dict(tier='A', org='STF', title='Súmula Vinculante 46 (página oficial)', identifier='SV 46',
               url='https://jurisprudencia.stf.jus.br/pages/search/seq-sumula805/false', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='18f8caf4d55d5b81910b6e8cdd56a27eb7d95168af6c081cb927afd52f5e6480',
               proves='Enunciado (competência legislativa privativa da União para crimes de responsabilidade e respectivo processo); aprovação '
                      '09/04/2015; DJe 17/04/2015; "Referência Legislativa: Constituição Federal de 1988, art. 22, I; e art. 85, parágrafo único".'),
    'T4': dict(tier='A', org='STF', title='Jurisprudência — ADI 2167 (mérito e MC)', identifier='ADI 2167',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22ADI%202167%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='e340485a85d88b04ffefa6e1e8a6a2c0170382d0fd11f0cd7a2361f63cbb6bc5',
               proves='Objeto: arts. 33, XVIII; 46, § 3º; 62, parágrafo único, e 103 da Constituição do Estado de Roraima (arguição/aprovação '
                      'prévia pela Assembleia de nomeações, inclusive interventores). Mérito j. 03/06/2020 (DJe 07/12/2020); MC j. 01/06/2000. '
                      'Parâmetros: CF arts. 2º, 25, 84 e, na MC, o procedimento do § 1º do art. 36. Nada sobre vinculação da intervenção (art. 36, I).'),
    'T5': dict(tier='A', org='STF', title='Repercussão Geral — Tema 950 (página do tema)', identifier='Tema 950 / RE 632115',
               url='https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=950', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='61f651facf32cc5db326d837f4c0e901c0a20870a3a8e9a917a439c370d129cd',
               proves='Título "Responsabilidade civil objetiva do Estado por atos protegidos por imunidade parlamentar"; discussão com fundamento '
                      'nos arts. 37, § 6º, e 53 da CF; Rel. Min. Luís Roberto Barroso; trânsito em julgado em 10/12/2025.'),
    'T6': dict(tier='A', org='STF', title='Jurisprudência — RE 632115 (Tema 950, mérito)', identifier='RE 632115',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22RE%20632115%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='06e36da8ff5514f5ea74a1bd9f86720a594799bdea66256d40f30cf269a79b3d',
               proves='Pleno, j. 29/09/2025, DJe 01/12/2025. Tese: a imunidade material parlamentar "(art. 53, caput, c/c art. 27, § 1º, e art. 29, '
                      'VIII, CF/1988)" exclui a responsabilidade civil objetiva do Estado (art. 37, § 6º); excesso = responsabilidade pessoal subjetiva.'),
    'T7': dict(tier='A', org='STF', title='Jurisprudência — HC 232627 e HC 232627 ED', identifier='HC 232627',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22HC%20232627%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='310ca610e6f0fd53275ab4519d90f7d555fcc7d0d5d2124c4881fd2b181c638b',
               proves='Pleno, Rel. Min. Gilmar Mendes, j. 12/03/2025, DJe 16/07/2025. Tese: o foro por prerrogativa para crimes praticados no cargo e '
                      'em razão das funções subsiste após o afastamento. "Dispositivos relevantes citados: CF/1988, art. 53, §1º". ED (PGR) acolhidos '
                      'com efeitos integrativos em 25/05/2026 (DJe 08/06/2026) para fixar balizas.'),
})

JOINT = dict(processes=['STF:ADI:7047', 'STF:ADI:7064'], date='2023-11-30', existing_record='STF:ADI:7047-7064 (J2B/J2C)',
             model='mesmo registro conjunto com aliases; uma ficha (que já separa o que vale "SOMENTE NA ADI 7064")')

REVIEW = {
    'J0-BL-166': dict(precedent='STF:ADI:7047', court='STF', klass='ADI', number='7047', process='ADI 7047', theme=None, rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023 (sessão virtual extraordinária), conjunto com a ADI 7064', publication='acórdão de 2023',
                      situation='mérito julgado', namespace='ADCT', namespace_evidence='A decisão declara inconstitucional o "art. 101, § 5º, do ADCT, '
                      'com redação estabelecida pelo art. 1º da EC 113/21". O target do backlog é ADCT:ART.101, o mesmo namespace.',
                      temporal_version='CURRENT', temporal_note='§ 5º incluído pela EC 113/2021; é o texto vigente no compilado, declarado inconstitucional.',
                      target_check='GRANULARITY', recommended_target='ADCT:ART.101:PAR.5', decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
                      provisional=False, new_type=False, joint_judgment=JOINT, sources=['S5', 'S6', 'P1'],
                      reason='A anotação está no § 5º, e a decisão atinge só o § 5º do art. 101 do ADCT; o artigo inteiro seria alvo amplo demais. '
                             'Recomendo o vínculo no ADCT:ART.101:PAR.5 com o registro conjunto ADI 7047/7064 já instalado.'),
    'J0-BL-167': dict(precedent='STF:ADI:7064', court='STF', klass='ADI', number='7064', process='ADI 7064', theme=None, rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023; acórdão j. 01/12/2023', publication='DJe 19/12/2023', situation='mérito julgado', namespace='ADCT',
                      namespace_evidence='A decisão declara inconstitucional o "art. 101, § 5º, do ADCT" (EC 113/21).',
                      temporal_version='CURRENT', temporal_note='Idem ao J0-BL-166.',
                      target_check='GRANULARITY', recommended_target='ADCT:ART.101:PAR.5', decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
                      provisional=False, new_type=False, joint_judgment=JOINT, sources=['S6', 'S4', 'P1'],
                      reason='Mesmo dispositivo e mesmo julgamento conjunto do J0-BL-166: um único vínculo (registro ADI 7047/7064) cobre as duas '
                             'recomendações, como no Batch01 (J0-BL-081/082).'),
    'J0-BL-169': dict(precedent='STF:ADI:7064', court='STF', klass='ADI', number='7064', process='ADI 7064', theme=None, rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023; acórdão j. 01/12/2023', publication='DJe 19/12/2023', situation='mérito julgado', namespace='ADCT',
                      namespace_evidence='A decisão dá interpretação conforme ao "caput do art. 107-A do ADCT, incluído pela EC 114/2021" e invalida '
                                         'incisos II e III e §§ 3º, 5º e 6º do mesmo artigo.',
                      temporal_version='CURRENT', temporal_note='Art. 107-A (EC 114/2021): texto vigente no compilado, regime transitório do teto de '
                                                                 'precatórios; o STF limitou seus efeitos ao exercício de 2022.',
                      target_check='PASS', recommended_target='ADCT:ART.107-A', decision='PROMOTE', confidence='HIGH', provisional=False, new_type=False,
                      joint_judgment=dict(JOINT, note='Só a ADI 7064 tratou do art. 107-A; a ficha conjunta já registra isso em "SOMENTE NA ADI 7064". '
                                                      'Na ratificação, decidir entre o registro conjunto e um registro próprio da ADI 7064.'),
                      sources=['S6', 'S4', 'P1'],
                      reason='A decisão atinge várias partes do art. 107-A (caput, incisos e parágrafos), por isso o alvo em nível de artigo é o '
                             'adequado. É mérito definitivo e de alta utilidade, porque o texto compilado ainda mostra o teto.'),
    'J0-BL-039': dict(precedent='STF:RG:793', court='STF', klass='RE (repercussão geral)', number='793', process='RE 855178', theme='Tema 793',
                      rapporteur='Min. Luiz Fux; red. p/ acórdão dos ED Min. Edson Fachin', judgment='RG 05/03/2015; ED 23/05/2019 (tese)',
                      publication='DJe 16/04/2020 (ED)', situation='tese fixada; trânsito em julgado 13/05/2020', namespace='CF88',
                      namespace_evidence='A tese funda a solidariedade na "competência comum" dos entes, a do art. 23 da CF; o inciso II trata de "cuidar '
                                         'da saúde e assistência pública".',
                      temporal_version='CURRENT', temporal_note='Art. 23, II na redação originária, sem alteração relevante.',
                      target_check='PASS', recommended_target='CF88:ART.23:INC.II', decision='PROMOTE', confidence='HIGH', provisional=False, new_type=False,
                      sources=['T1', 'T2'],
                      reason='Tese com efeito vinculante, sobre o núcleo do art. 23, II (competência comum em saúde). O tema ainda não está na base nem '
                             'no índice legado: precisa de registro RG e ficha nova, no formato RG já validado.'),
    'J0-BL-049': dict(precedent='STF:SV:46', court='STF', klass='Súmula Vinculante', number='46', process='PSV 106', theme='SV 46', rapporteur=None,
                      judgment='aprovação em 09/04/2015', publication='DJe nº 72 e DOU de 17/04/2015', situation='vigente', namespace='CF88',
                      namespace_evidence='A referência legislativa oficial é "CF/1988, art. 22, I; e art. 85, parágrafo único"; não cita o art. 29-A.',
                      temporal_version='CURRENT', temporal_note='Arts. 22, I e 85, parágrafo único vigentes.',
                      target_check='FAIL_TARGET', recommended_target='CF88:ART.22:INC.I',
                      additional_targets=['CF88:ART.85:PAR.UNICO'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH', provisional=False,
                      new_type=False, sources=['T3'],
                      reason='A SV 46 interpreta a competência legislativa da União (art. 22, I e art. 85, parágrafo único), não o § 2º do art. 29-A, '
                             'que só lista crimes de responsabilidade do Prefeito. Recomendo vincular nos dispositivos da referência oficial. O art. 22, I '
                             'já tem o Tema 1246; o art. 85, parágrafo único não tem jurisprudência.'),
    'J0-BL-052': dict(precedent='STF:ADI:2167', court='STF', klass='ADI', number='2167', process='ADI 2167',
                      theme=None, rapporteur='Min. Ricardo Lewandowski; red. p/ acórdão Min. Alexandre de Moraes (mérito); Min. Marco Aurélio (MC)',
                      judgment='mérito 03/06/2020; MC 01/06/2000', publication='DJe 07/12/2020; DJ 01/09/2000', situation='mérito julgado',
                      namespace='CE-RR', namespace_evidence='O objeto são os arts. 33, XVIII; 46, § 3º; 62, parágrafo único e 103 da Constituição do '
                                                            'Estado de Roraima. O art. 36 da CF só aparece (na MC) pelo procedimento do § 1º, não pelo inciso I.',
                      temporal_version='NOT_APPLICABLE', temporal_note='O dispositivo federal indicado (art. 36, I) não foi objeto da decisão.',
                      target_check='FAIL', recommended_target=None, decision='REJECT_FALSE_POSITIVE', confidence='HIGH', provisional=False,
                      new_type=False, sources=['T4'],
                      reason='A recomendação atribui à ADI 2167 a tese de que a intervenção é "vinculada ou discricionária conforme a hipótese", mas a '
                             'ação trata da Constituição de Roraima (arguição prévia de nomeações pela Assembleia) e não interpreta o art. 36, I. '
                             'É o mesmo tipo de erro da J1: o objeto é de outra norma.'),
    'J0-BL-057': dict(precedent='STF:RG:950', court='STF', klass='RE (repercussão geral)', number='950', process='RE 632115', theme='Tema 950',
                      rapporteur='Min. Luís Roberto Barroso', judgment='29/09/2025', publication='DJe 01/12/2025',
                      situation='tese fixada; trânsito em julgado 10/12/2025', namespace='CF88',
                      namespace_evidence='A tese cita textualmente "art. 53, caput, c/c art. 27, § 1º, e art. 29, VIII, CF/1988".',
                      temporal_version='CURRENT', temporal_note='Art. 53, caput, na redação da EC 35/2001 (vigente).',
                      target_check='PASS', recommended_target='CF88:ART.53:CAPUT', decision='PROMOTE', confidence='HIGH', provisional=False, new_type=False,
                      sources=['T5', 'T6'],
                      reason='Tese definitiva e recente sobre a imunidade material do caput do art. 53: o Estado não responde objetivamente por atos '
                             'cobertos pela imunidade, e o excesso é responsabilidade pessoal do parlamentar. Precisa de registro RG e ficha nova.'),
    'J0-BL-076': dict(precedent='STF:ADI:7047', court='STF', klass='ADI', number='7047', process='ADI 7047', theme=None, rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023, conjunto com a ADI 7064', publication='acórdão de 2023', situation='mérito julgado', namespace='CF88',
                      namespace_evidence='A decisão trata do art. 100, § 9º (já vinculado) e dá interpretação conforme ao "art. 100, § 11, da '
                                         'Constituição, com redação da EC 113/21".',
                      temporal_version='CURRENT', temporal_note='§ 11 na redação da EC 113/2021, que é o texto vigente.',
                      target_check='GRANULARITY', recommended_target='CF88:ART.100:PAR.11', decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
                      provisional=False, new_type=False, joint_judgment=JOINT, sources=['S5', 'S4', 'P1'],
                      reason='No art. 100 a decisão atinge o § 9º (já instalado) e o § 11 (interpretação conforme, para excluir "com auto aplicabilidade '
                             'para a União"). O artigo inteiro seria alvo amplo, e o § 11 ainda não tem esse vínculo. Recomendo o § 11 com o registro conjunto.'),
    'J0-BL-077': dict(precedent='STF:ADI:7064', court='STF', klass='ADI', number='7064', process='ADI 7064', theme=None, rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023; acórdão j. 01/12/2023', publication='DJe 19/12/2023', situation='mérito julgado', namespace='CF88',
                      namespace_evidence='A decisão dá interpretação conforme ao "art. 100, § 11, da Constituição, com redação da EC 113/21".',
                      temporal_version='CURRENT', temporal_note='Idem ao J0-BL-076.',
                      target_check='GRANULARITY', recommended_target='CF88:ART.100:PAR.11', decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
                      provisional=False, new_type=False, joint_judgment=JOINT, sources=['S6', 'S4', 'P1'],
                      reason='Mesmo julgamento conjunto do J0-BL-076: um único vínculo (registro ADI 7047/7064) no § 11 cobre as duas recomendações.'),
    'J0-BL-058': dict(precedent='STF:HC:232627', court='STF', klass='HC', number='232627', process='HC 232627', theme=None,
                      rapporteur='Min. Gilmar Mendes', judgment='Pleno, 12/03/2025; ED 25/05/2026 (efeitos integrativos)',
                      publication='DJe 16/07/2025; ED DJe 08/06/2026', situation='mérito julgado (tese de Plenário)', namespace='CF88',
                      namespace_evidence='A ementa indica "Dispositivos relevantes citados: CF/1988, art. 53, §1º".',
                      temporal_version='CURRENT', temporal_note='Art. 53, § 1º na redação da EC 35/2001 (vigente). Supera em parte a orientação da AP 937-QO.',
                      target_check='PASS', recommended_target='CF88:ART.53:PAR.1', decision='PROMOTE', confidence='HIGH', provisional=False,
                      new_type=True, sources=['T7'],
                      reason='Tese do Plenário diretamente sobre o § 1º do art. 53: o foro por prerrogativa para crimes funcionais subsiste após o fim '
                             'do mandato. HC ainda não é um tipo validado no aparelho (NEW_JURIS_TYPE_REQUIRES_DESIGN = YES); não materializar antes '
                             'desse desenho. Os ED de 2026 (J0-BL-060, fora do lote) entram como complemento do mesmo registro.'),
}

FIELDS = ('precedent', 'court', 'klass', 'number', 'process', 'theme', 'rapporteur', 'judgment', 'publication', 'situation', 'namespace',
          'namespace_evidence', 'temporal_version', 'temporal_note', 'target_check', 'recommended_target', 'decision', 'confidence', 'provisional',
          'new_type', 'sources', 'reason')
DECISIONS = ('PROMOTE', 'PROMOTE_PROVISIONAL', 'REJECT_FALSE_POSITIVE', 'REJECT_TEMPORAL_MISMATCH', 'REJECT_NOT_MATERIAL', 'ALREADY_COVERED',
             'DUPLICATE', 'REALLOCATE_RECOMMENDED', 'UNRESOLVED_EXTERNAL')
TEMPORAL = ('CURRENT', 'HISTORICAL', 'MIXED', 'NOT_APPLICABLE')
VALIDATED_TYPES = ('RE (repercussão geral)', 'Súmula Vinculante', 'ADI')


def decisions(doc):
    if sorted(REVIEW) != sorted(doc['selected']):
        raise SystemExit('REVIEW_DOES_NOT_MATCH_SELECTION')
    q = {x['recommendation_id']: x for x in doc['high_queue']}
    out = []
    for rid in doc['selected']:
        r = REVIEW[rid]
        if any(f not in r for f in FIELDS) or r['decision'] not in DECISIONS or r['temporal_version'] not in TEMPORAL \
                or any(s not in SOURCES for s in r['sources']):
            raise SystemExit('INCOMPLETE_REVIEW ' + rid)
        if r['new_type'] != (r['klass'] not in VALIDATED_TYPES):
            raise SystemExit('NEW_TYPE_FLAG_INCONSISTENT ' + rid)
        ns_ok = r['namespace'] in ('CF88', 'ADCT') and r['recommended_target'] is not None and r['recommended_target'].startswith(
            'ADCT:' if r['namespace'] == 'ADCT' else 'CF88:')
        if r['decision'] in ('PROMOTE', 'PROMOTE_PROVISIONAL', 'REALLOCATE_RECOMMENDED') and not (ns_ok and r['temporal_version'] == 'CURRENT'):
            raise SystemExit('PROMOTION_WITHOUT_NAMESPACE_OR_CURRENT_TEXT ' + rid)
        out.append(dict(recommendation_id=rid, rank=q[rid]['rank'], recommended_by_backlog=q[rid]['target_id'],
                        suggested_identifiers=q[rid]['suggested_identifiers'], **r,
                        NAMESPACE_CHECK='PASS' if ns_ok else 'FAIL', TEMPORAL_CHECK='DONE', OFFICIAL_SOURCE_REVIEWED=True,
                        NEW_JURIS_TYPE_REQUIRES_DESIGN='YES' if r['new_type'] else 'NO', status='AWAITING_USER_RATIFICATION'))
    return out
