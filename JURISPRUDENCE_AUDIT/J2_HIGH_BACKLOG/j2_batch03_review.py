"""J2 BATCH03 (HIGH) — review of the 10 selected recommendations. Official sources consulted on 2026-10-17 in the built-in browser (STF
portal answers 403 to automated clients; sha256 = rendered innerText) + the archived official RG corpus (J4, 2026-09-21) + the Planalto
compiled CF snapshot of J2A (P1). PROPOSALS ONLY (AWAITING_USER_RATIFICATION). Short excerpts = official text, quoted for the detectors.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from j2_review_common import make_decisions  # noqa: E402

D = '2026-10-17'
_J2A = json.loads((Path(__file__).resolve().parent / 'J2A_BATCH01_DECISIONS.json').read_text(encoding='utf-8'))['sources']
_J2D = json.loads((Path(__file__).resolve().parent / 'J2D_BATCH02_DECISIONS.json').read_text(encoding='utf-8'))['sources']
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'


def _s(title, ident, url, sha, proves, method='navegador embutido (innerText)'):
    return dict(tier='A', org='STF', title=title, identifier=ident, url=url, accessed_on=D, method=method, dom_text_sha256=sha, proves=proves)


SOURCES = {
    'P1': dict(_J2A['P1'], reused_from='J2A'), 'S4': dict(_J2A['S4'], reused_from='J2A'), 'S6': dict(_J2A['S6'], reused_from='J2A'),
    'T7': dict(_J2D['T7'], reused_from='J2D'),
    'U1': _s('Súmula 702 (página oficial)', 'Súmula 702', 'https://jurisprudencia.stf.jus.br/pages/search/seq-sumula702/false',
             '4921c31b1c8f9967168e099eaf65f6633c0b595731c1dc4399672df1c333603f',
             'Enunciado; aprovação 24/09/2003; DJ 09-13/10/2003; "Referência Legislativa: Constituição Federal de 1988, art. 29, X".'),
    'U2': _s('Jurisprudência — MS 34379 (mesmo sentido: MS 34384 e MS 34418)', 'MS 34418', JUR.format('MS%2034418'),
             '8c5b0e99a884960a38855bfd62eaca60e1262d946d97b044de2a47780185899d',
             'Pleno, Rel. Min. Rosa Weber, j. 25/09/2023, DJe 06/10/2023: cisão das votações do impeachment (art. 52, p.u.); mandado de '
             'segurança PREJUDICADO (perda do mandato do impetrante) ou não conhecido; sem tese sobre a validade da cisão.'),
    'U3': _s('Jurisprudência — MS 21689', 'MS 21689', JUR.format('MS%2021689'), 'daecc0462c29f6b2a4cfa78c686001bcad3f2b1562676c4dc5d2bc40aea2e12b',
             'Pleno, Rel. Min. Carlos Velloso, j. 16/12/1993, DJ 07/04/1995: art. 52, p.u.: duas penas (perda do cargo e inabilitação por oito '
             'anos), a inabilitação não é acessória; a renúncia apresentada na sessão de julgamento não paralisa o impeachment.'),
    'U4': _s('Jurisprudência — AP 694', 'AP 694', JUR.format('AP%20694'), '3d2084172b6bf00ca8e21e0cce3042baa53c349eae3219cbfa06f4122d18856d',
             '1ª Turma, Rel. Min. Rosa Weber, j. 02/05/2017, DJe 31/08/2017, item 7: perda do mandato do congressista condenado cabe à Casa '
             '(art. 55, VI e § 2º), salvo regime fechado incompatível com o mandato: perda automática declarada pela Mesa (art. 55, III, § 3º).'),
    'U5': _s('Jurisprudência — ADI 1616', 'ADI 1616', JUR.format('ADI%201616'), '900c18ebf98caa497ac6ce8af7b1e9f9084488ac2e65955caf4b9aa5602fdd95',
             'Pleno, Rel. Min. Maurício Corrêa, j. 24/05/2001, DJ 24/08/2001, item 4: o múnus do AGU (CF, art. 103, § 3º) deve ser entendido com '
             'temperamentos; o AGU não está obrigado a defender tese já declarada inconstitucional pelo STF.'),
    'U6': _s('Jurisprudência — ADI 1254 (AgR)', 'ADI 1254', JUR.format('ADI%201254'), '0fa9d7236c23e97c1545c56c647918dad44824ce91d4d9458097f1fe4330adcc',
             'Pleno: "A função processual do Advogado-Geral da União, nos processos de controle de constitucionalidade por via de ação, é '
             'eminentemente defensiva".'),
    'U7': _s('Jurisprudência — ADI 789', 'ADI 789', JUR.format('ADI%20789'), 'df485ceea2cd806ae3532e8d894fef29e064a8c4b82788b075c219777abce59b',
             'Pleno, Rel. Min. Celso de Mello, j. 26/05/1994, DJ 19/12/1994: "inteligência da norma inscrita no art. 130": o MP junto ao TCU é '
             'órgão de extração constitucional, sem fisionomia institucional própria, na intimidade estrutural da Corte de Contas.'),
    'U8': _s('Portal — ADI 5017, aba Decisões', 'ADI 5017 (incidente 4437805)', 'https://portal.stf.jus.br/processos/abaDecisoes.asp?incidente=4437805',
             '43f9db70b1bd9d6e28ab3cabc78c0236bf085a391fdd896b441e07c181d8684a',
             'Liminar deferida pela Presidência em 17/07/2013, "sujeito ao referendo do Colegiado", para suspender os efeitos da EC 73/2013; '
             'não há referendo nem mérito registrados; autos conclusos ao relator (Min. Luiz Fux) em 18/06/2025.'),
    'U9': _s('Jurisprudência — Inq 4787 AgR-QO', 'Inq 4787', JUR.format('Inq%204787'), '54ba687b866dba99abaa4bd11d064e81b2d49773e05d0c1376c10690769927d4',
             'Pleno, Rel. Min. Gilmar Mendes, j. 12/03/2025 (mesma sessão do HC 232627), DJe 27/05/2025: mesma tese; "Dispositivos relevantes '
             'citados: CF/1988, art. 53, §1º"; ex-parlamentar.'),
    'U10': _s('Repercussão Geral — Tema 157 (página do tema)', 'Tema 157 / RE 729744', 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=157',
              '732326315c7f3c1977425a7faaf590f41667350f33b390585ac8f8343129c7bf',
              'Título "Competência exclusiva da Câmara Municipal para o julgamento das contas de Prefeito"; discussão "à luz do art. 31"; '
              'parecer prévio meramente opinativo; trânsito em julgado 15/10/2019. Tese no corpus oficial arquivado (J4, 2026-09-21).'),
}


def P(pid, court, klass, number, judgment, publication, **kw):
    return dict(id=pid, court=court, klass=klass, number=number, judgment=judgment, publication=publication, **kw)


REVIEW = {
    'J0-BL-047': dict(
        precedents=[P('STF:SUMULA:702', 'STF', 'SUMULA', '702', 'aprovação 24/09/2003', 'DJ 09, 10 e 13/10/2003')],
        namespace='CF88', namespace_evidence='Referência legislativa oficial: "Constituição Federal de 1988, art. 29, X".',
        temporal_version='CURRENT', temporal_note='Art. 29, X (redação dada pela EC 1/1992 ao antigo VIII, mantida).',
        target_check='PASS', recommended_targets=['CF88:ART.29:INC.X'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='súmula vigente', sources=['U1'],
        evidence_excerpt='A competência do Tribunal de Justiça para julgar prefeitos restringe-se aos crimes de competência da Justiça comum '
                         'estadual. Referência Legislativa: Constituição Federal de 1988, art. 29, X.',
        reason='Súmula do STF cuja referência legislativa oficial é exatamente o art. 29, X. Súmula comum: o firmware tem o rótulo "SUMULA STF", '
               'mas o tipo nunca foi validado fisicamente.'),
    'J0-BL-053': dict(
        precedents=[P('STF:MS:34418', 'STF', 'MS', '34418', 'Pleno, 25/09/2023 (com MS 34379 e 34384)', 'DJe 06/10/2023',
                      rapporteur='Min. Rosa Weber', result='prejudicado / não conhecido')],
        namespace='CF88', namespace_evidence='A ementa cita o "ART. 52, Parágrafo Único, Da Constituição Federal".',
        temporal_version='CURRENT', temporal_note='Art. 52, p.u. sem alteração.', target_check='FAIL_MATERIALITY', recommended_targets=[],
        decision='REJECT_NOT_MATERIAL_RECOMMENDED', confidence='HIGH', status_processual='mérito não apreciado (prejudicado)', sources=['U2'],
        evidence_excerpt='Mandado de segurança prejudicado ou, se assim não se entender, não conhecido. Cisão de votações referentes à perda do '
                         'cargo e à inabilitação (art. 52, parágrafo único, da Constituição Federal).',
        reason='O STF não decidiu se a votação separada (perda do cargo × inabilitação) é válida: o mandado foi julgado prejudicado ou não '
               'conhecido. Vincular ao art. 52, p.u. sugeriria uma tese que o tribunal não fixou.'),
    'J0-BL-054': dict(
        precedents=[P('STF:MS:21689', 'STF', 'MS', '21689', 'Pleno, 16/12/1993', 'DJ 07/04/1995', rapporteur='Min. Carlos Velloso')],
        namespace='CF88', namespace_evidence='A ementa cita "C.F., art. 52, parágrafo único" e "C.F., 1988, art. 52, parag. único".',
        temporal_version='CURRENT', temporal_note='Art. 52, p.u. vigente; a ementa compara com as Constituições anteriores (contexto histórico, '
                                                   'não versão do target).',
        target_check='PASS', recommended_targets=['CF88:ART.52:PAR.UNICO'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='mérito julgado (1993)', sources=['U3'],
        evidence_excerpt='A existência, no impeachment brasileiro, segundo a Constituição (C.F., 1988, art. 52, parag. único), de duas penas: a) perda '
                         'do cargo; b) inabilitação, por oito anos. A renúncia ao cargo, apresentada na sessão de julgamento, não paralisa o processo.',
        reason='Precedente do Pleno que interpreta diretamente o art. 52, p.u.: inabilitação autônoma e efeito da renúncia (caso Collor). MS é um '
               'tipo novo no aparelho (NEW_JURIS_TYPE_REQUIRES_DESIGN).'),
    'J0-BL-061': dict(
        precedents=[P('STF:AP:694', 'STF', 'AP', '694', '1ª Turma, 02/05/2017', 'DJe 31/08/2017', rapporteur='Min. Rosa Weber',
                      organ='Turma (não Plenário)')],
        namespace='CF88', namespace_evidence='O item 7 da ementa cita "artigo 55, VI e § 2º, da CF" e "artigo 55, III, § 3º, da CF".',
        temporal_version='CURRENT', temporal_note='Art. 55 vigente (EC 76/2013 no § 2º: votação aberta).', target_check='PASS',
        recommended_targets=['CF88:ART.55:INC.VI'], decision='PROMOTE_RECOMMENDED', confidence='MEDIUM',
        status_processual='mérito julgado (Turma); orientação do STF oscilante (AP 470 × AP 565 × AP 694)', sources=['U4'],
        evidence_excerpt='Perda do mandato parlamentar: É da competência das Casas Legislativas decidir sobre a perda do mandato do Congressista '
                         'condenado criminalmente (artigo 55, VI e § 2º, da CF). Regra excepcionada quando a condenação impõe regime fechado.',
        reason='Interpreta diretamente o art. 55, VI. A confiança é MEDIUM porque é precedente de Turma num tema em que a orientação do STF oscilou; '
               'a ficha precisa dizer isso. AP é um tipo novo no aparelho.'),
    'J0-BL-134': dict(
        precedents=[P('STF:ADI:7047-7064', 'STF', 'ADI', '7047/7064', 'Pleno, 30/11/2023', 'DJe 19/12/2023 (ADI 7064)')],
        namespace='CF88', namespace_evidence='O art. 165, § 18 é da CF, mas foi incluído pela EC 136/2025 (P1), depois do julgamento.',
        temporal_version='NOT_APPLICABLE', temporal_note='O precedente (2023) é anterior ao dispositivo (EC 136/2025); não há "Vide ADI" no § 18.',
        target_check='FAIL_TEMPORAL', recommended_targets=[], decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', confidence='HIGH',
        status_processual='mérito julgado', sources=['P1', 'S6', 'S4'],
        evidence_excerpt='§ 18. A partir do exercício financeiro de 2026, serão excluídas do limite individualizado do Poder Executivo as despesas '
                         'com precatórios e requisições de pequeno valor. (Incluído pela Emenda Constitucional nº 136, de 2025)',
        reason='Uma decisão de 2023 não pode ter interpretado um parágrafo criado em 2025. A nota do backlog descreve o art. 107-A do ADCT, que já '
               'foi decidido no Batch02 (ADI 7064).'),
    'J0-BL-090': dict(
        precedents=[P('STF:ADI:1616', 'STF', 'ADI', '1616', 'Pleno, 24/05/2001', 'DJ 24/08/2001', rapporteur='Min. Maurício Corrêa'),
                    P('STF:ADI:1254', 'STF', 'ADI', '1254', 'Pleno (AgR)', 'DJ 17/03/2000 (acórdão do processo)')],
        namespace='CF88', namespace_evidence='A ADI 1616 cita "CF, artigo 103, § 3º"; a ADI 1254 trata da "função processual do Advogado-Geral da '
                                             'União" (art. 103, § 3º).',
        temporal_version='CURRENT', temporal_note='Art. 103, § 3º vigente (redação originária).', target_check='FAIL_TARGET',
        recommended_targets=['CF88:ART.103:PAR.3'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado',
        sources=['U5', 'U6'],
        evidence_excerpt='O munus a que se refere o imperativo constitucional (CF, artigo 103, § 3º) deve ser entendido com temperamentos. A função '
                         'processual do Advogado-Geral da União é eminentemente defensiva.',
        reason='A nota do backlog cita "art. 103, § 3º", mas o target ficou no § 1º (oitiva do PGR). Os precedentes verificados tratam do AGU, '
               '§ 3º. A ADI 4983 não foi verificada para esse ponto e não entra na proposta.'),
    'J0-BL-122': dict(
        precedents=[P('STF:ADI:789', 'STF', 'ADI', '789', 'Pleno, 26/05/1994', 'DJ 19/12/1994', rapporteur='Min. Celso de Mello')],
        namespace='CF88', namespace_evidence='A ementa traz "INTELIGÊNCIA DA NORMA INSCRITA NO ART. 130 DA CONSTITUIÇÃO" (o objeto era a Lei '
                                             '8.443/92, interpretada à luz do art. 130).',
        temporal_version='CURRENT', temporal_note='Art. 130 na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.130'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (improcedente)', sources=['U7'],
        evidence_excerpt='MINISTÉRIO PÚBLICO JUNTO AO TCU - INSTITUIÇÃO QUE NÃO INTEGRA O MINISTÉRIO PÚBLICO DA UNIÃO - INTELIGÊNCIA DA NORMA INSCRITA '
                         'NO ART. 130 DA CONSTITUIÇÃO. Lei n. 8.443/92.',
        reason='Precedente-base do STF sobre o art. 130. As ADIs 3315, 3804 e 4427 da nota não foram verificadas nesta rodada; a proposta cobre só '
               'a ADI 789. O alerta de namespace (Lei 8.443/92) foi conferido: a lei era o objeto, e o art. 130 o parâmetro interpretado.'),
    'J0-BL-165': dict(
        precedents=[P('STF:ADI:5017', 'STF', 'ADI', '5017', 'liminar monocrática da Presidência, 17/07/2013 (sujeita a referendo)',
                      'DJe 2013', rapporteur='Min. Luiz Fux (relator atual)')],
        namespace='ADCT', namespace_evidence='A decisão suspende os efeitos da EC 73/2013, que incluiu o § 11 no art. 27 do ADCT (anotação oficial '
                                             '"Vide ADI 5017").',
        temporal_version='CURRENT', temporal_note='ADCT art. 27, § 11 (EC 73/2013) continua no texto compilado, com efeitos suspensos.',
        target_check='GRANULARITY', recommended_targets=['ADCT:ART.27:PAR.11'], decision='PROMOTE_PROVISIONAL_RECOMMENDED', confidence='MEDIUM',
        status_processual='cautelar monocrática não referendada; mérito pendente (conclusos em 18/06/2025)', sources=['U8', 'P1'],
        revalidation=dict(trigger='REFERENDO_OU_JULGAMENTO_DE_MERITO', max_age_days=90, last_verified_on=D,
                          check='https://portal.stf.jus.br/processos/detalhe.asp?incidente=4437805'),
        evidence_excerpt='em caráter excepcional, e sujeito ao referendo do Colegiado, defiro a medida cautelar pleiteada, para suspender os efeitos '
                         'da EC 73/2013.',
        reason='Informação essencial para quem lê o § 11 (a criação dos TRFs pela EC 73/2013 está suspensa desde 2013). Mas é cautelar monocrática '
               'nunca referendada, por isso a proposta é provisória, com gatilho de revalidação. O alvo vai do artigo para o § 11.'),
    'J0-BL-048': dict(
        precedents=[P('STF:HC:232627', 'STF', 'HC', '232627', 'Pleno, 12/03/2025', 'DJe 16/07/2025'),
                    P('STF:INQ:4787', 'STF', 'INQ', '4787', 'Pleno, 12/03/2025 (AgR-QO; mesma sessão)', 'DJe 27/05/2025')],
        namespace='CF88', namespace_evidence='Os dois acórdãos citam só "CF/1988, art. 53, §1º" e tratam de ex-parlamentares; nada sobre o art. 29, X.',
        temporal_version='CURRENT', temporal_note='—', target_check='FAIL_MATERIALITY', recommended_targets=[],
        decision='REJECT_NOT_MATERIAL_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado; ED do HC em 2026', sources=['T7', 'U9'],
        evidence_excerpt='Dispositivos relevantes citados: CF/1988, art. 53, §1º. Inquérito instaurado para apurar envolvimento de ex-parlamentar.',
        reason='A tese é geral sobre foro após o fim do cargo, mas os acórdãos interpretam só o art. 53, § 1º (já aprovado no Batch02 para o HC). '
               'Aplicá-la ao foro do prefeito (art. 29, X) seria extensão, não interpretação do dispositivo. O Inq 4787 é o mesmo julgamento '
               'do HC 232627 (SAME_JUDGMENT_SAME_SCOPE), relevante para a recomendação J0-BL-059 (MEDIUM).'),
    'J0-BL-045': dict(
        precedents=[P('STF:RG:157', 'STF', 'RG', '157', 'RE 729744 (Rel. Min. Gilmar Mendes); tese de 2016', 'trânsito em julgado 15/10/2019')],
        namespace='CF88', namespace_evidence='A página do tema diz que a discussão é "à luz do art. 31 da Constituição Federal".',
        temporal_version='CURRENT', temporal_note='Art. 31, § 2º na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.31:PAR.2'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='tese fixada; trânsito em julgado', sources=['U10'],
        evidence_excerpt='O parecer técnico elaborado pelo Tribunal de Contas tem natureza meramente opinativa, competindo exclusivamente à Câmara de '
                         'Vereadores o julgamento das contas anuais do Chefe do Poder Executivo local (art. 31 da Constituição Federal).',
        reason='Tese vinculante que define a natureza do parecer prévio do § 2º do art. 31. A tese está no corpus oficial arquivado (formato J4 de '
               'ficha disponível).'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
