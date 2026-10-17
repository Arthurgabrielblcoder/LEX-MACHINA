"""J2 BATCH07 (MEDIUM, 2nd) — review of the 10 selected recommendations. Official STF sources consulted on 2026-10-17 (built-in browser;
tema pages fetched in-page from portal.stf.jus.br; sha256 = rendered text), archived official corpus (J4), J2A S3 (ADI 4425). PROPOSALS ONLY.
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
TEMA = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={}'


def _s(title, ident, url, sha, proves, method='navegador embutido (innerText)'):
    return dict(tier='A', org='STF', title=title, identifier=ident, url=url, accessed_on=D, method=method, dom_text_sha256=sha, proves=proves)


def P(pid, klass, number, judgment, publication, **kw):
    return dict(id=pid, court='STF', klass=klass, number=number, judgment=judgment, publication=publication, **kw)


FETCH = 'navegador embutido (fetch na página do portal; texto do DOM)'
SOURCES = {
    'P1': dict(_J2A['P1'], reused_from='J2A'), 'S3': dict(_J2A['S3'], reused_from='J2A'),
    'X1': _s('Repercussão Geral — Tema 1046', 'Tema 1046 / ARE 1121633', TEMA.format(1046), '3a6f389f973c3a65bafcd8adb815387b6ba3a7ea24b72350c5491a41cebff95c',
             'Título: validade de norma coletiva que limita direito trabalhista não assegurado constitucionalmente; discussão "à luz dos arts. 5º, '
             'incisos II, LV e XXXV; e 7º, incisos XIII e XXVI"; trânsito em julgado 09/05/2023.', FETCH),
    'X2': _s('Jurisprudência — ADI 2404', 'ADI 2404', JUR.format('ADI%202404'), '8ec3defdc5691dd489d2f8b9b884e27dc41f356973258e35d43283b65837fdf3',
             'Pleno, Rel. Min. Dias Toffoli, j. 31/08/2016, DJe 01/08/2017: art. 254 do ECA ("em horário diverso do autorizado") inconstitucional; '
             'a CF conferiu à União, no art. 21, XVI, a classificação "para efeito indicativo"; classificação não é autorização prévia.'),
    'X3': _s('Jurisprudência — ADI 3114', 'ADI 3114', JUR.format('ADI%203114'), 'ab59b1496679569b13d373261212234617cb924171fe30908663b8830975d6a9',
             'Pleno, Rel. Min. Carlos Britto, j. 24/08/2005, DJ 07/04/2006: emendas parlamentares a projeto de iniciativa reservada: limites da '
             'pertinência temática e da vedação de aumento de despesa "(inciso I do art. 63 da CF)"; LC 836/97-SP.'),
    'X4': _s('Jurisprudência — ADI 2681 (mérito e MC)', 'ADI 2681', JUR.format('ADI%202681'), '469317debab4330ed3effde30c2097719a640cc24638fc01e0b833c17d0df5ad',
             'Mérito: Pleno, Rel. Min. Celso de Mello, j. 01/08/2018, DJe 28/08/2018 (MC 2002 superada): aumento de despesa por emenda '
             'parlamentar; "INCIDÊNCIA DA RESTRIÇÃO PREVISTA NO ART. 63, I, DA CONSTITUIÇÃO DA REPÚBLICA"; procedente.'),
    'X5': _s('Repercussão Geral — Tema 686', 'Tema 686 / RE 745811', TEMA.format(686), 'feb96f9f056efa1a8d01959cd27d6052f965f03b3a3b948b52baeda3ee471f12',
             'Título: emenda parlamentar que implica aumento de despesa em projeto de iniciativa privativa; discussão "à luz dos arts. 2º; 61, § 1º, '
             'II, a; e 63". Tese (corpus J4) cita "art. 63, I, da CF". JÁ INSTALADO em CF88:ART.63:INC.I.', FETCH),
    'X6': _s('Repercussão Geral — Tema 1068', 'Tema 1068 / RE 1235340', TEMA.format(1068), '425be9b47c6aa71fabfb1f6efa07c7496d9aebfd552dbe472550e9cd4cc7f28c',
             'Título: constitucionalidade da execução imediata de pena aplicada pelo Tribunal do Júri; discussão "à luz do art. 5º, inciso XXXVIII, '
             'alínea c"; trânsito em julgado 26/09/2025.', FETCH),
    'X7': _s('Súmula Vinculante 25 (página oficial)', 'SV 25', 'https://jurisprudencia.stf.jus.br/pages/search/seq-sumula774/false',
             '18e25eda1ac82fc464e59c83c02250105d4aeae088396867d77f241d4c9e26c1',
             'Enunciado ("qualquer que seja a modalidade do depósito"); aprovação 16/12/2009; "Referência Legislativa: Constituição Federal de 1988, '
             'art. 5º, LXVII e § 2º. Convenção Americana sobre Direitos Humanos, art. 7º, § 7º. Pacto Internacional sobre Direitos Civis e '
             'Políticos, art. 11".'),
    'X8': _s('Repercussão Geral — Tema 935', 'Tema 935 / ARE 1018459', TEMA.format(935), '2f34046b64b022ed6b45283d550dcbe2aca4a89274b248b7ebbcc560c1ca3130',
             'Discussão "com base nos arts. 5º, incs. II, XXXVI e LV, 7º, inc. XXVI, e 93, inc. IX" (não o art. 8º, IV); contribuição assistencial; '
             'situação: acórdão de mérito publicado (sem trânsito registrado na página).', FETCH),
    'X9': _s('Repercussão Geral — Tema 1229', 'Tema 1229 / RE 1355228', TEMA.format(1229), 'bfc776c2f9c0647e465bf95e1383b665172f40a0e4202dfc55dfdb8e85bcb248',
             'Título: substituição na chefia do Executivo por decisão judicial e a irreelegibilidade "da qual trata o art. 14, § 5º, da Constituição '
             'Federal, na redação dada pela Emenda de n. 16/1997".', FETCH),
}

REVIEW = {
    'J0-BL-011': dict(
        precedents=[P('STF:RG:1046', 'RG', '1046', 'ARE 1121633 (Rel. Min. Gilmar Mendes); tese 2022', 'trânsito em julgado 09/05/2023')],
        namespace='CF88', namespace_evidence='Discussão "à luz dos arts. 5º ... e 7º, incisos XIII e XXVI".', temporal_version='CURRENT',
        temporal_note='Art. 7º, XXVI na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.7:INC.XXVI'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='tese fixada; trânsito em julgado', sources=['X1'],
        evidence_excerpt='São constitucionais os acordos e as convenções coletivos que pactuam limitações ou afastamentos de direitos trabalhistas, desde que '
                         'respeitados os direitos absolutamente indisponíveis. (art. 7º, XXVI, da Constituição Federal)',
        reason='Tese central sobre o reconhecimento das convenções e acordos coletivos (art. 7º, XXVI): o negociado prevalece, respeitados os direitos '
               'absolutamente indisponíveis.'),
    'J0-BL-031': dict(
        precedents=[P('STF:ADI:2404', 'ADI', '2404', 'Pleno, 31/08/2016', 'DJe 01/08/2017', rapporteur='Min. Dias Toffoli')],
        namespace='CF88', namespace_evidence='O objeto é o art. 254 da Lei 8.069/90 (ECA); o parâmetro expresso é o "art. 21, inciso XVI" da CF.',
        temporal_version='CURRENT', temporal_note='Art. 21, XVI na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.21:INC.XVI'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (procedente)', sources=['X2'],
        evidence_excerpt='a própria Carta de 1988 conferiu à União, com exclusividade, no art. 21, inciso XVI, o desempenho da atividade material de exercer a '
                         'classificação, para efeito indicativo. Expressão contida no art. 254 da Lei nº 8.069/90.',
        reason='Interpreta diretamente o art. 21, XVI: a classificação indicativa é informativa e não autoriza censura nem condiciona a exibição. O alerta '
               'de namespace (Lei 8.069) foi conferido: a lei era o objeto e o parâmetro é a CF.'),
    'J0-BL-063': dict(
        precedents=[P('STF:ADI:3114', 'ADI', '3114', 'Pleno, 24/08/2005', 'DJ 07/04/2006', rapporteur='Min. Carlos Britto')],
        namespace='CF88', namespace_evidence='O objeto é a LC 836/97-SP; o parâmetro é o art. 63, I, mais o limite da pertinência temática das emendas.',
        temporal_version='CURRENT', temporal_note='Art. 63 na redação originária.', target_check='PASS', recommended_targets=['CF88:ART.63'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (improcedente)', sources=['X3'],
        evidence_excerpt='duas limitações: a) a impossibilidade de o parlamento veicular matérias diferentes das versadas no projeto de lei; e b) a '
                         'impossibilidade de as emendas implicarem aumento de despesa pública (inciso I do art. 63 da CF).',
        reason='Firma os dois limites do poder de emenda: pertinência temática e não aumento de despesa. Como a pertinência não está só no inciso I, '
               'o alvo em nível de artigo (art. 63) é o adequado.'),
    'J0-BL-064': dict(
        precedents=[P('STF:ADI:2681', 'ADI', '2681', 'Pleno, mérito 01/08/2018 (MC de 2002 superada)', 'DJe 28/08/2018', rapporteur='Min. Celso de Mello')],
        namespace='CF88', namespace_evidence='A ementa cita a "RESTRIÇÃO PREVISTA NO ART. 63, I, DA CONSTITUIÇÃO DA REPÚBLICA" (o objeto era lei estadual).',
        temporal_version='CURRENT', temporal_note='—', target_check='GRANULARITY', recommended_targets=['CF88:ART.63:INC.I'],
        decision='REALLOCATE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (procedente)', sources=['X4'],
        evidence_excerpt='CONSEQUENTE AUMENTO DA DESPESA GLOBAL PREVISTA NO PROJETO DE LEI – IMPOSSIBILIDADE CONSTITUCIONAL – INCIDÊNCIA DA RESTRIÇÃO PREVISTA '
                         'NO ART. 63, I, DA CONSTITUIÇÃO DA REPÚBLICA – AÇÃO DIRETA JULGADA PROCEDENTE.',
        reason='A recomendação citava a MC; o mérito (2018) a substituiu e decide especificamente o inciso I do art. 63, onde o Tema 686 já está instalado.'),
    'J0-BL-065': dict(
        precedents=[P('STF:RG:686', 'RG', '686', 'RE 745811', 'tese fixada (trânsito na página: 18/11/2013)')],
        namespace='CF88', namespace_evidence='A tese cita "(art. 63, I, da CF)".', temporal_version='CURRENT', temporal_note='—', target_check='COVERED',
        recommended_targets=[], decision='ALREADY_COVERED', confidence='HIGH', status_processual='tese fixada', sources=['X5'],
        evidence_excerpt='São formalmente inconstitucionais emendas parlamentares que impliquem aumento de despesa em projeto de lei de iniciativa reservada do '
                         'Chefe do Poder Executivo (art. 63, I, da CF).',
        reason='O Tema 686 já está instalado no dispositivo exato (CF88:ART.63:INC.I, base de 261). Vincular de novo no art. 63 duplicaria a ficha.'),
    'J0-BL-075': dict(
        precedents=[P('STF:ADI:4425', 'ADI', '4425', 'Pleno, mérito 14/03/2013; QO 25/03/2015', 'DJe 19/12/2013; DJe 04/08/2015')],
        namespace='CF88', namespace_evidence='A ementa cita os §§ 2º, 9º, 10 e 12 do art. 100 (EC 62/2009) e o regime especial do ADCT.',
        temporal_version='MIXED', temporal_note='Julgou a redação da EC 62/2009: o § 12 continua vigente (ADI 4425 já ratificada e instalada no § 12); a '
                                                 'expressão do § 2º e os §§ 9º e 10 foram substituídos depois (EC 94/2016 e EC 113/2021).',
        target_check='PASS_ARTICLE_WITH_TEMPORAL_NOTE', recommended_targets=['CF88:ART.100'], decision='PROMOTE_RECOMMENDED', confidence='MEDIUM',
        status_processual='mérito julgado com modulação', sources=['S3', 'P1'],
        evidence_excerpt='O regime de compensação dos débitos da Fazenda Pública inscritos em precatórios, previsto nos §§ 9º e 10 do art. 100, incluídos pela '
                         'EC nº 62/09. A expressão "na data de expedição do precatório", contida no art. 100, §2º, com redação dada pela EC nº 62/09.',
        reason='Mesma política do Tema 558 (J2B.1) e do Tema 594: as partes históricas do julgado ficam no art. 100, com nota temporal. Confiança MEDIUM '
               'porque é decisão editorial: o essencial vigente (§ 12) já está coberto, e o vínculo no artigo serve à história do regime de '
               'precatórios. Sem a nota, recomenda-se não vincular.'),
    'J0-BL-005': dict(
        precedents=[P('STF:RG:1068', 'RG', '1068', 'RE 1235340 (Rel. Min. Luís Roberto Barroso); tese 2024', 'trânsito em julgado 26/09/2025')],
        namespace='CF88', namespace_evidence='A página oficial discute o tema "à luz do art. 5º, inciso XXXVIII, alínea c" (soberania dos veredictos), não '
                                             'do inciso LVII.',
        temporal_version='CURRENT', temporal_note='Art. 5º, XXXVIII na redação originária; o target de alínea não existe, então vincula no inciso.',
        target_check='FAIL_TARGET', recommended_targets=['CF88:ART.5:INC.XXXVIII'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
        status_processual='tese fixada; trânsito em julgado', sources=['X6'],
        evidence_excerpt='A soberania dos veredictos do Tribunal do Júri autoriza a imediata execução de condenação imposta pelo corpo de jurados, '
                         'independentemente do total da pena aplicada. (art. 5º, XXXVIII, c)',
        reason='A tese se apoia na soberania dos veredictos (art. 5º, XXXVIII, c). Pôr no inciso LVII sugeriria uma tese sobre presunção de inocência '
               'que o tema não fixa diretamente. Realocar para o inciso XXXVIII, que já tem o Tema 154.'),
    'J0-BL-006': dict(
        precedents=[P('STF:SV:25', 'SV', '25', 'aprovação 16/12/2009', 'DJe e DOU 23/12/2009')],
        namespace='CF88', namespace_evidence='A referência legislativa traz a CF (art. 5º, LXVII e § 2º) e convenções internacionais; a CF é o dispositivo-alvo.',
        temporal_version='CURRENT', temporal_note='Art. 5º, LXVII vigente: a exceção do depositário infiel continua no texto, mas é ilícita (SV 25).',
        target_check='PASS', recommended_targets=['CF88:ART.5:INC.LXVII'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='súmula vinculante vigente', sources=['X7'],
        evidence_excerpt='É ilícita a prisão civil de depositário infiel, qualquer que seja a modalidade do depósito. Referência Legislativa: Constituição '
                         'Federal de 1988, art. 5º, LXVII e § 2º. Convenção Americana sobre Direitos Humanos, art. 7º, § 7º.',
        reason='Informação indispensável no próprio inciso LXVII: o texto ainda prevê a prisão do depositário infiel, mas ela é ilícita. Usar o enunciado '
               'oficial atual ("do depósito"); o corpus arquivado dizia "de depósito".'),
    'J0-BL-013': dict(
        precedents=[P('STF:RG:935', 'RG', '935', 'ARE 1018459; tese revista em 2023 (ED)', 'acórdão de mérito publicado; trânsito não registrado na página')],
        namespace='CF88', namespace_evidence='A página oficial discute o tema "com base nos arts. 5º ..., 7º, inc. XXVI, e 93, IX"; o art. 8º, IV '
                                             '(contribuição confederativa) não está entre eles.',
        temporal_version='CURRENT', temporal_note='—', target_check='FAIL_TARGET', recommended_targets=['CF88:ART.7:INC.XXVI'],
        decision='REALLOCATE_RECOMMENDED', confidence='MEDIUM', status_processual='mérito publicado; sem trânsito registrado', sources=['X8'],
        evidence_excerpt='É constitucional a instituição, por acordo ou convenção coletivos, de contribuições assistenciais a serem impostas a todos os '
                         'empregados da categoria, ainda que não sindicalizados, desde que assegurado o direito de oposição.',
        reason='O art. 8º, IV trata da contribuição confederativa (SV 40, já instalada ali). A assistencial do Tema 935 é instituída por acordo ou '
               'convenção coletiva, por isso a base oficial inclui o art. 7º, XXVI. Confiança MEDIUM porque a página não registra trânsito. Revalidar '
               'antes de materializar.'),
    'J0-BL-017': dict(
        precedents=[P('STF:RG:1229', 'RG', '1229', 'RE 1355228', 'tese fixada (corpus J4)')],
        namespace='CF88', namespace_evidence='O título oficial cita "art. 14, § 5º, da Constituição Federal, na redação dada pela Emenda de n. 16/1997".',
        temporal_version='CURRENT', temporal_note='Art. 14, § 5º na redação da EC 16/1997 (vigente).', target_check='PASS', recommended_targets=['CF88:ART.14:PAR.5'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='tese fixada', sources=['X9'],
        evidence_excerpt='O exercício da chefia do Poder Executivo, nos seis meses anteriores ao pleito, em decorrência de decisão judicial não transitada em '
                         'julgado, não conta como exercício de um mandato para efeito de reeleição. (art. 14, § 5º, redação da EC 16/1997)',
        reason='Tese específica sobre a contagem de mandato para a reeleição do art. 14, § 5º. Convive com os Temas 172 e 564 já instalados no parágrafo.'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
