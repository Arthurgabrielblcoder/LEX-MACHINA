"""J2 BATCH08 (MEDIUM, 3rd) — review of the 10 selected recommendations. Official sources consulted on 2026-10-17 in the built-in browser:
STF jurisprudence, TSE (súmulas page), STJ (BLOCKED by an anti-bot challenge — not bypassed). Reused: J2D T7, Batch03 U9. PROPOSALS ONLY.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from j2_review_common import make_decisions  # noqa: E402

D = '2026-10-17'
_J2D = json.loads((HERE.parent / 'J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json').read_text(encoding='utf-8'))['sources']
_B03 = json.loads((HERE.parent / 'J2_HIGH_BACKLOG/J2_BATCH03_DECISIONS.json').read_text(encoding='utf-8'))['sources']
JUR = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22{}%22&base=acordaos'


def _s(title, ident, url, sha, proves, org='STF', tier='A'):
    return dict(tier=tier, org=org, title=title, identifier=ident, url=url, accessed_on=D, method='navegador embutido (innerText)',
                dom_text_sha256=sha, proves=proves)


def P(pid, klass, number, judgment, publication, court='STF', **kw):
    return dict(id=pid, court=court, klass=klass, number=number, judgment=judgment, publication=publication, **kw)


SOURCES = {
    'T7': dict(_J2D['T7'], reused_from='J2D'), 'U9': dict(_B03['U9'], reused_from='BATCH03'),
    'Y1': _s('Súmula-TSE n. 9 (página oficial)', 'Súmula TSE 9', 'https://www.tse.jus.br/legislacao/codigo-eleitoral/sumulas/sumulas-do-tse/sumula-nb0-9',
             '1f4b62a53dd070705a8dcd4ab4cacf0bc275b41849a94779f86020045055fbfd',
             'Enunciado: a suspensão de direitos políticos por condenação criminal transitada em julgado cessa com o cumprimento ou a extinção da pena; '
             '"Referências: CF, art. 15, III"; publicada nos DJs de 28 a 30/10/1992.', org='TSE'),
    'Y2': _s('Jurisprudência — MS 27931', 'MS 27931', JUR.format('MS%2027931'), 'bb990605db280414caa48c8d7e38fb53835975546ed3f8a2f84465d45d261be3',
             'Pleno, Rel. Min. Celso de Mello, j. 29/06/2017, DJe 28/10/2020: interpretação restritiva do § 6º do art. 62: o sobrestamento só '
             'afeta matérias passíveis de regramento por medida provisória; segurança indeferida.'),
    'Y3': _s('STJ — pesquisa de súmulas (Súmula 403)', 'Súmula STJ 403', 'https://scon.stj.jus.br/SCON/pesquisar.jsp?b=SUMU&livre=%40NUM%3D403',
             '9423587ec676b6a067963519a36e7078a9ebf61065c211bae1a442f6d4face8f',
             'BLOQUEADO: a página exibiu "Verificação automática em andamento ... responda ao desafio abaixo" (anti-robô). O desafio NÃO foi '
             'contornado; o conteúdo da súmula não foi acessado. O hash é da página de bloqueio.', org='STJ'),
    'Y4': _s('Jurisprudência — Inq 4781 (Ref e AgRs)', 'Inq 4781', JUR.format('Inq%204781'), 'f3c015962df2e5f04ee0cc20e2e7805be2401307df82ab6b0ef20876d683262e',
             'Ref: Pleno, Rel. Min. Alexandre de Moraes, j. 17/02/2021, DJe 14/05/2021: "Não incidência da imunidade parlamentar prevista no caput, do '
             'art. 53"; a imunidade material só incide com conexão com o desempenho da função; flagrante de crime inafiançável (art. 53, § 2º).'),
    'Y5': _s('Jurisprudência — Pet 7174', 'Pet 7174', JUR.format('Pet%207174'), '93a4c5a3840ae1bb64522bfc5d044d6a984f82d69f0faee18f5818a8ab6b614a',
             '1ª Turma, red. p/ acórdão Min. Marco Aurélio, j. 10/03/2020, DJe 28/09/2020: "IMUNIDADE PARLAMENTAR – ARTIGO 53": pressupõe nexo de '
             'causalidade com o exercício do mandato.'),
    'Y6': _s('Jurisprudência — ADI 3395', 'ADI 3395', JUR.format('ADI%203395'), 'a57846742cfdeb29dec6957e5c7b02f257e9987c4771cfbf3d63bc44fa05c3db',
             'Pleno, Rel. Min. Alexandre de Moraes, j. 15/04/2020, DJe 01/07/2020: "ART.114, I"; interpretação conforme: a competência da Justiça do '
             'Trabalho não alcança as ações entre o Poder Público e seus servidores estatutários.'),
    'Y7': _s('Jurisprudência — ADI 3684', 'ADI 3684', JUR.format('ADI%203684'), '56e7246184fed1b4591c15336df3cad1c7c5ebb6a28df1f75887534fab389c67',
             'Pleno, Rel. Min. Gilmar Mendes, j. 11/05/2020, DJe 01/06/2020: interpretação conforme ao "art. 114, I, IV e IX" para afastar a '
             'competência da Justiça do Trabalho para ações penais.'),
    'Y8': _s('Jurisprudência — ADI 3085', 'ADI 3085', JUR.format('ADI%203085'), '5c56a381dd52d8e4a90aba17423af7aaad6543e017546085b9b458c4efdab2f0',
             'Pleno, QO, Rel. Min. Eros Grau, j. 17/02/2005, DJ 28/04/2006: a EC 45/04, ao vedar as férias coletivas, revogou os atos normativos '
             'inferiores; pedido PREJUDICADO.'),
    'Y9': _s('Jurisprudência — ADI 6457', 'ADI 6457', JUR.format('ADI%206457'), 'bb0fd915990d3be428cc188aea43df548d2fedd244d94f69080f5030cc3dc3ea',
             'Pleno, Rel. Min. Luiz Fux, j. 09/04/2024, DJe 04/06/2024: "ART. 142 DA CONSTITUIÇÃO"; LC 97/1999 com interpretação conforme; '
             'inexistência de poder moderador na CF/1988.'),
}

REVIEW = {
    'J0-BL-020': dict(
        precedents=[P('TSE:SUMULA:9', 'SUMULA_TSE', '9', 'edição 1992 (Rel. Min. Paulo Brossard)', 'DJs de 28-30/10/1992', court='TSE')],
        namespace='CF88', namespace_evidence='Referências oficiais: "CF, art. 15, III".', temporal_version='CURRENT', temporal_note='Art. 15, III na redação originária.',
        target_check='GRANULARITY', recommended_targets=['CF88:ART.15:INC.III'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
        status_processual='súmula vigente (TSE)', sources=['Y1'],
        evidence_excerpt='A suspensão de direitos políticos decorrente de condenação criminal transitada em julgado cessa com o cumprimento ou a extinção da '
                         'pena, independendo de reabilitação ou de prova de reparação dos danos. Referências: CF, art. 15, III.',
        reason='Súmula do TSE cuja referência é o inciso III do art. 15 (condenação criminal), e não o artigo inteiro. É o primeiro precedente de outro '
               'tribunal: o firmware exige ID "STF:" e rotula súmula como "SUMULA STF", por isso exige desenho de tipo e tribunal antes de materializar.'),
    'J0-BL-062': dict(
        precedents=[P('STF:MS:27931', 'MS', '27931', 'Pleno, 29/06/2017', 'DJe 28/10/2020', rapporteur='Min. Celso de Mello')],
        namespace='CF88', namespace_evidence='A ementa dá "INTERPRETAÇÃO RESTRITIVA CONFERIDA AO § 6º DO ART. 62 DA CONSTITUIÇÃO DA REPÚBLICA".',
        temporal_version='CURRENT', temporal_note='§ 6º do art. 62 na redação da EC 32/2001 (vigente).', target_check='PASS',
        recommended_targets=['CF88:ART.62:PAR.6'], decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='mérito julgado (Pleno)',
        sources=['Y2'],
        evidence_excerpt='INTERPRETAÇÃO RESTRITIVA CONFERIDA AO § 6º DO ART. 62 DA CONSTITUIÇÃO DA REPÚBLICA, NO SENTIDO DE QUE O REGIME DE URGÊNCIA SOMENTE '
                         'AFETA AQUELAS MATÉRIAS QUE SE MOSTREM PASSÍVEIS DE REGRAMENTO POR MEDIDA PROVISÓRIA.',
        reason='Precedente do Plenário que define o alcance do trancamento de pauta por MP (art. 62, § 6º). MS é tipo novo no aparelho.'),
    'J0-BL-001': dict(
        precedents=[P('STJ:SUMULA:403', 'SUMULA_STJ', '403', 'não verificado (fonte oficial bloqueada)', 'não verificado', court='STJ')],
        namespace='CF88', namespace_evidence='Não confirmado: a página oficial do STJ não foi acessada (desafio anti-robô).', temporal_version='NOT_APPLICABLE',
        temporal_note='Não avaliável sem a fonte oficial.', target_check='UNVERIFIED', recommended_targets=[], decision='UNRESOLVED_EXTERNAL',
        confidence='N/A', status_processual='não verificado', sources=['Y3'],
        evidence_excerpt='Verificação automática em andamento. Aguarde a verificação automática. Caso não seja redirecionado, responda ao desafio abaixo.',
        reason='A fonte oficial do STJ bloqueou o acesso com um desafio anti-robô, que não foi contornado (regra de segurança). Nenhum conteúdo foi '
               'presumido. Além disso, súmula do STJ é tribunal e tipo novos no aparelho. Retomar quando houver acesso (ou com a página fornecida pelo usuário).'),
    'J0-BL-055': dict(
        precedents=[P('STF:INQ:4781', 'INQ', '4781', 'Pleno, Ref 17/02/2021', 'DJe 14/05/2021', rapporteur='Min. Alexandre de Moraes')],
        namespace='CF88', namespace_evidence='A ementa traz "Não incidência da imunidade parlamentar prevista no caput, do art. 53, da Constituição Federal".',
        temporal_version='CURRENT', temporal_note='Art. 53, caput na redação da EC 35/2001.', target_check='PASS', recommended_targets=['CF88:ART.53:CAPUT'],
        decision='PROMOTE_RECOMMENDED', confidence='HIGH', status_processual='referendo de prisão em flagrante pelo Pleno (decisão definitiva do incidente)',
        sources=['Y4'],
        evidence_excerpt='Não incidência da imunidade parlamentar prevista no caput, do art. 53, da Constituição Federal. A garantia constitucional da imunidade '
                         'parlamentar material somente incide no caso de as manifestações guardarem conexão com o desempenho da função legislativa.',
        reason='Precedente do Plenário sobre o limite da imunidade material (nexo com a função). Complementa o Tema 950 (Batch02, aprovado) no caput. Inq é '
               'tipo novo no aparelho. O mesmo acórdão trata do § 2º (flagrante), o que pode virar uma proposta separada.'),
    'J0-BL-056': dict(
        precedents=[P('STF:PET:7174', 'PET', '7174', '1ª Turma, 10/03/2020', 'DJe 28/09/2020', rapporteur='Min. Marco Aurélio (redator)')],
        namespace='CF88', namespace_evidence='A ementa cita "IMUNIDADE PARLAMENTAR – ARTIGO 53 DA CONSTITUIÇÃO FEDERAL".', temporal_version='CURRENT', temporal_note='—',
        target_check='PASS', recommended_targets=[], decision='DUPLICATE_RECOMMENDATION', confidence='HIGH', status_processual='mérito julgado (Turma)',
        sources=['Y5', 'Y4'],
        evidence_excerpt='A imunidade parlamentar pressupõe nexo de causalidade com o exercício do mandato. Declarações proferidas em contexto desvinculado das '
                         'funções parlamentares não se encontram cobertas pela imunidade material.',
        reason='Mesma tese do Inq 4781 Ref (item anterior), que é do Plenário. Para não multiplicar vínculos iguais no caput do art. 53, prefere-se o '
               'precedente do Plenário. Não é rejeição de mérito: a Pet 7174 é correta, mas redundante.'),
    'J0-BL-059': dict(
        precedents=[P('STF:INQ:4787', 'INQ', '4787', 'Pleno, 12/03/2025 (AgR-QO; mesma sessão do HC 232627)', 'DJe 27/05/2025')],
        namespace='CF88', namespace_evidence='A ementa cita "Dispositivos relevantes citados: CF/1988, art. 53, §1º", a mesma tese do HC 232627.',
        temporal_version='CURRENT', temporal_note='—', target_check='COVERED', recommended_targets=[], decision='DUPLICATE_RECOMMENDATION',
        confidence='HIGH', status_processual='mérito julgado (Pleno)', sources=['U9', 'T7'],
        evidence_excerpt='Fixação do entendimento de que a prerrogativa de foro para julgamento de crimes praticados durante o exercício do cargo e em razão das '
                         'funções subsiste mesmo após o afastamento do cargo. Dispositivos relevantes citados: CF/1988, art. 53, §1º.',
        reason='Mesmo julgamento e mesmo escopo do HC 232627, já ratificado no Batch02 (SAME_JUDGMENT_SAME_SCOPE). Proposta: incluir "Inq 4787" como '
               'alias no registro do HC quando o tipo HC for materializado, sem nova ficha.'),
    'J0-BL-104': dict(
        precedents=[P('STF:ADI:3395', 'ADI', '3395', 'Pleno, 15/04/2020', 'DJe 01/07/2020', target='CF88:ART.114:INC.I'),
                    P('STF:ADI:3684', 'ADI', '3684', 'Pleno, 11/05/2020', 'DJe 01/06/2020', target='CF88:ART.114:INC.I|IV|IX')],
        namespace='CF88', namespace_evidence='As ementas citam "ART.114, I" e "art. 114, I, IV e IX" (redação da EC 45/2004).', temporal_version='CURRENT',
        temporal_note='Art. 114, I, IV e IX na redação da EC 45/2004.', target_check='GRANULARITY',
        recommended_targets=['CF88:ART.114:INC.I', 'CF88:ART.114:INC.IV', 'CF88:ART.114:INC.IX'], decision='REALLOCATE_RECOMMENDED', confidence='HIGH',
        status_processual='mérito julgado (interpretação conforme)', sources=['Y6', 'Y7'],
        evidence_excerpt='Interpretação conforme ao disposto no art. 114, I, IV e IX, da Constituição da República, de modo a afastar a competência da Justiça do '
                         'Trabalho para processar e julgar ações penais. ART.114, I: exclusão das ações entre o Poder Público e seus servidores.',
        reason='Do caput para os incisos que os julgados interpretam: ADI 3395 no inciso I (estatutários); ADI 3684 nos incisos I, IV e IX (sem competência '
               'penal).'),
    'J0-BL-105': dict(
        precedents=[P('STF:ADI:3395', 'ADI', '3395', 'Pleno, 15/04/2020', 'DJe 01/07/2020')],
        namespace='CF88', namespace_evidence='A ementa cita "ART.114, I, DA CONSTITUIÇÃO FEDERAL".', temporal_version='CURRENT', temporal_note='—',
        target_check='PASS', recommended_targets=['CF88:ART.114:INC.I'], decision='PROMOTE_RECOMMENDED', confidence='HIGH',
        status_processual='mérito julgado (MC confirmada)', sources=['Y6'],
        evidence_excerpt='A interpretação adequadamente constitucional da expressão relação do trabalho deve excluir os vínculos de natureza jurídico-estatutária.',
        reason='Interpretação conforme do inciso I: a Justiça do Trabalho não julga causas estatutárias. É o mesmo vínculo proposto no item anterior; '
               'materializado uma única vez.'),
    'J0-BL-071': dict(
        precedents=[P('STF:ADI:3085', 'ADI', '3085', 'Pleno, QO 17/02/2005', 'DJ 28/04/2006', result='prejudicada')],
        namespace='CF88', namespace_evidence='A ementa menciona a vedação de férias coletivas da EC 45/04 (art. 93, XII), mas julga a ação prejudicada.',
        temporal_version='CURRENT', temporal_note='Art. 93, XII (EC 45/2004).', target_check='FAIL_MATERIALITY', recommended_targets=[],
        decision='REJECT_NOT_MATERIAL_RECOMMENDED', confidence='MEDIUM', status_processual='prejudicada (sem mérito)', sources=['Y8'],
        evidence_excerpt='A EC 45/04, ao vedar as férias coletivas nos juízos e tribunais de segundo grau, revogou os atos normativos inferiores que a elas se '
                         'referiam. Pedido de declaração de inconstitucionalidade prejudicado.',
        reason='Questão de ordem que julgou a ação prejudicada; não há tese de mérito sobre o art. 93, XII (mesma lógica do MS 34418). A ADI 3823 MC, '
               'também citada na nota, não foi verificada nesta rodada e pode ser reexaminada.'),
    'J0-BL-123': dict(
        precedents=[P('STF:ADI:6457', 'ADI', '6457', 'Pleno, 09/04/2024', 'DJe 04/06/2024', rapporteur='Min. Luiz Fux')],
        namespace='CF88', namespace_evidence='A ementa abre com "ART. 142 DA CONSTITUIÇÃO" (o objeto é a LC 97/1999, com interpretação conforme).',
        temporal_version='CURRENT', temporal_note='Art. 142 vigente.', target_check='PASS', recommended_targets=['CF88:ART.142'], decision='PROMOTE_RECOMMENDED',
        confidence='HIGH', status_processual='mérito julgado', sources=['Y9'],
        evidence_excerpt='ART. 142 DA CONSTITUIÇÃO. ATRIBUIÇÕES DAS FORÇAS ARMADAS. LEI COMPLEMENTAR FEDERAL 97/1999. PODER MODERADOR. CONSTITUIÇÃO FEDERAL DE '
                         '1988. INEXISTÊNCIA. INTERPRETAÇÃO CONFORME.',
        reason='Julgado de 2024 que interpreta diretamente o art. 142: as Forças Armadas não exercem poder moderador e sua missão é limitada. O alerta '
               'de namespace (LC 97/99) foi conferido: a lei era o objeto, e o art. 142 o parâmetro.'),
}


def decisions(doc):
    return make_decisions(doc, REVIEW, SOURCES)
