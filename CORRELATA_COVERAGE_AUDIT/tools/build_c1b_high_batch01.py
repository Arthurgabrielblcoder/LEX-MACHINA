"""CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH01 — human-assisted legal review of the C0 HIGH candidates of arts. 5 to 43 (CF88).

Selection (derived, not listed): every candidate of the C0 queue section HIGH whose target is CF88 art. 5..43, in the structural order of
the queue. Limit rule of the mission: > 35 -> first 30 (rest to Batch02); <= 35 -> all. Each decision was taken against the official
text (Planalto, downloaded on VERIFIED_ON, sha256 recorded; HTML not versioned). LEGAL_DECISION is kept apart from the device route
(MAIN_CORPUS_ROUTE_REQUIRED / INGESTION_REQUIRED / DEVICE_RESOLVABLE_NOW): a route problem never invalidates a legal link.
NOTHING IS APPLIED (no additions overlay, no exclusions, no RUN4, no SD/firmware).

Writes CF88_CORRELATA_C1B_HIGH_BATCH01_{INPUT.json, DECISIONS.json, REPORT.md} (deterministic). Usage: python build_c1b_high_batch01.py [--check]
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import target_id as T  # noqa: E402

MISSION = 'CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH01'
BASE = dict(branch='cf-correlata-coverage-audit', head='281b2e6e101c54f1e4349c3dce6a5169058f3527')
QUEUE = AUDIT / 'CF88_CORRELATA_REVIEW_QUEUE.json'
CANDS = AUDIT / 'CF88_CORRELATA_CANDIDATES.json'
OUT_IN = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH01_INPUT.json'
OUT_DEC = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH01_DECISIONS.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH01_REPORT.md'
VERIFIED_ON = '2026-10-11'
ART_RANGE = (5, 43)
LIMIT_ALL, LIMIT_TAKE = 35, 30
DECISIONS = ('APPROVE', 'ADJUST', 'REJECT', 'HOLD', 'NEEDS_SOURCE')
RELATION_TYPES = ('REGULAMENTA', 'COMPLEMENTA', 'IMPLEMENTA', 'PROCEDIMENTO', 'CONDIÇÃO_OU_EXCEÇÃO', 'ORGANIZA_INSTITUIÇÃO',
                  'EXECUTA_POLÍTICA_CONSTITUCIONAL')
P = 'https://www.planalto.gov.br/ccivil_03/'


def S(norm, path, sha, size):
    return dict(norm=norm, url=P + path, sha256=sha, bytes=size, verified_on=VERIFIED_ON)


SOURCES = {
    'CF88': S('Constituição Federal (compilada)', 'constituicao/constituicao.htm', 'd22db6b86fe90c8626e26753adf5b34d127272959b280e7955df0a9eb0b946cf', 1840587),
    'EC103': S('Emenda Constitucional nº 103/2019', 'constituicao/emendas/emc/emc103.htm', '418ea85a5c34fa39670635d5a09b455278cf6d2d41fe8eb964478b241cfffea6', 171194),
    'L9296': S('Lei nº 9.296/1996', 'leis/l9296.htm', 'f0482c0fb3cc57b52b65c26262b286462bc40d570afd01c84d388b759c2ed326', 21359),
    'L8078': S('Lei nº 8.078/1990 (CDC)', 'leis/l8078compilado.htm', '2b27ba8ee10835bc31343f4d4f25e37aac92d060b69cbd5657201c09e2d96dfc', 170425),
    'L12527': S('Lei nº 12.527/2011 (LAI)', '_ato2011-2014/2011/lei/l12527.htm', '763c95e3090fa0bdf238e64e876f37c927a98563104aad0df1d9cfacf38bdb33', 109489),
    'L8072': S('Lei nº 8.072/1990', 'leis/l8072.htm', 'fc35cfaeb2d1010d77791b9126fb126ae2efa1031fea0a60198ce1021d32c060', 50432),
    'L13709': S('Lei nº 13.709/2018 (LGPD)', '_ato2015-2018/2018/lei/l13709.htm', 'a142ec0976619bc435147c402c1ae14db3deec5f105759b592ba7cadd335ac93', 310252),
    'LC150': S('Lei Complementar nº 150/2015', 'leis/lcp/lcp150.htm', '682fad0f9dd3851f07c7616583df46bb3b074c29e8c74dc8df011fa5cc836ba5', 99114),
    'L7783': S('Lei nº 7.783/1989', 'leis/l7783.htm', '4327a3c1b59c8d666d5219adbfd99e8baf6022c2b7409e70103ed0e11352cba1', 20526),
    'LC135': S('Lei Complementar nº 135/2010', 'leis/lcp/lcp135.htm', '33a08ef890a0aa6ad15342be63395cb740252bc2d7de3f2a0fc806caa7c94949', 29020),
    'LC64': S('Lei Complementar nº 64/1990', 'leis/lcp/lcp64.htm', '5d95b330f1849077f3d9361cb7cef4845b8b8f9a57ae8aeaf5e360fd6841f3af', 95850),
    'L9096': S('Lei nº 9.096/1995', 'leis/l9096.htm', '2ef73d9c48f0a24760572819d69e6e90674b29070057569d82833843eaafaac2', 245700),
    'LC230': S('Lei Complementar nº 230/2026', 'leis/lcp/lcp230.htm', 'f3398ffa583af68f52210447b516c526b23822fc8672da558af010fda61c3f3a', 16646),
    'LC90': S('Lei Complementar nº 90/1997', 'leis/lcp/lcp90.htm', 'ec4488af5c7a7e0c243c9e037d0205fb4de5c6dea4c7ab9667fc025ccf11e0db', 12886),
    'L13848': S('Lei nº 13.848/2019', '_ato2019-2022/2019/lei/l13848.htm', '23c776273f8113c033afff9bdc80828994d457450fb17dd4f0c0b4e6c85a3d72', 140991),
    'L15352': S('Lei nº 15.352/2026', '_ato2023-2026/2026/lei/l15352.htm', 'feac5bc35076d39da33287911dc74186db6a4495fbafd81aef2edaa8704d63dd', 164468),
    'MP1317': S('Medida Provisória nº 1.317/2025', '_ato2023-2026/2025/mpv/mpv1317.htm', 'f4b950d2b0dacae9c8d49075168b1467f861e9461f911559fca6d9492b3a5db3', 129893),
    'L13303': S('Lei nº 13.303/2016', '_ato2015-2018/2016/lei/l13303.htm', '009d9edb46088b87c9ffcbf97fe6f6fda5758f2c7cad6dc5153697d4c241ab2a', 248652),
    'L14133': S('Lei nº 14.133/2021', '_ato2019-2022/2021/lei/l14133.htm', 'e33c9e649f18c56a119ae38e607724c2eabd9baa2866514d1edbe8d0032f2ce3', 649705),
    'LC103': S('Lei Complementar nº 103/2000', 'leis/lcp/lcp103.htm', '2fa5c71d0a62a8da2a692e37bc89eb87e8fdcb86526c3cc7ff1e38c95ffbd78b', 5584),
    'LC140': S('Lei Complementar nº 140/2011', 'leis/lcp/lcp140.htm', '3c8ce10c9068d9890e17ed77d1e70494668605e645371f2d6e6c69f149b983d8', 54123),
    'L8112': S('Lei nº 8.112/1990 (compilada)', 'leis/l8112cons.htm', 'd46060504696ce68f461d7f25604b0f4e873ec6c24a8f530df62464331c43728', 563961),
    'L8429': S('Lei nº 8.429/1992', 'leis/l8429.htm', 'c3a7b4cb31489d4d2d52154dbba3224f69a2dbdb2b73b7caff98eb57bb2aa012', 210250),
    'L12813': S('Lei nº 12.813/2013', '_ato2011-2014/2013/lei/l12813.htm', 'a920bd6ba29e5775569299ed9704adc2a3f87eef934deec0100b7089b5613090', 28347),
    'LC152': S('Lei Complementar nº 152/2015', 'leis/lcp/lcp152.htm', '8ead015814de148f8bd24999eb4b2382d2b5f7c1b3ae7c9bf43fac399f1677ba', 9116),
    'L9717': S('Lei nº 9.717/1998', 'leis/l9717.htm', '89fb9083cdb5b5ccf3b7018ee93e26b9bcd5ea259142982e9b912db75d30118b', 68251),
}


def D(decision, confidence, relation, sources, provisions, analysis, route=None, target=None, notes=None):
    return dict(decision=decision, confidence=confidence, relation_type_final=relation, sources=sources, provisions=provisions,
                analysis=analysis, route=route, target_final=target, notes=notes)


# candidate_id -> decision (one per candidate of the batch; nothing applied)
REVIEW = {
    'CORRC0-BDB0C3B6A45D': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L9296'],
                             'Ementa: "Regulamenta o inciso XII, parte final, do art. 5°". O art. 1º trata da interceptação de comunicações '
                             'telefônicas por ordem judicial, para investigação criminal e instrução processual penal.',
                             'A lei é a regulamentadora expressa da parte final do inciso XII. O target está correto. A natureza muda de '
                             'COMPLEMENTA para REGULAMENTA.', route='art. 1º'),
    'CORRC0-ABBD129F7E41': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L8078'],
                             'Art. 1º: "O presente código estabelece normas de proteção e defesa do consumidor ... nos termos dos arts. 5°, '
                             'inciso XXXII, 170, inciso V".',
                             'O inciso XXXII manda o Estado promover, na forma da lei, a defesa do consumidor, e o CDC se declara a lei '
                             'desse comando. A natureza muda de COMPLEMENTA para REGULAMENTA. A rota de aparelho é um problema separado e '
                             'não invalida o vínculo.', route='art. 1º'),
    'CORRC0-514534A6E80F': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L12527'],
                             'Ementa: "Regula o acesso a informações previsto no inciso XXXIII do art. 5º, no inciso II do § 3º do art. 37 '
                             'e no § 2º do art. 216". O art. 1º diz o mesmo.',
                             'Regulamentação expressa do inciso XXXIII. A natureza muda para REGULAMENTA. Sem fan-out: o vínculo fica só '
                             'neste inciso, e o art. 37, § 3º, II foi tratado na C1A.', route='art. 1º'),
    'CORRC0-06D0375C4D5A': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L8072'],
                             'Ementa: "Dispõe sobre os crimes hediondos, nos termos do art. 5º, inciso XLIII". O art. 1º traz o rol dos '
                             'crimes hediondos e o art. 2º as vedações (anistia, graça, indulto e fiança).',
                             'É a lei que concretiza a parte "crimes hediondos" do inciso XLIII. A natureza muda para REGULAMENTA. Não '
                             'exclui as leis de tortura, drogas e terrorismo (a Lei 13.260/2016 já está vinculada).',
                             route='arts. 1º e 2º', notes='NON_EXCLUSIVE: o inciso XLIII é regulado por várias leis, cada uma na sua parte.'),
    'CORRC0-A809DD115D5A': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L13709'],
                             'Art. 1º: "dispõe sobre o tratamento de dados pessoais, inclusive nos meios digitais ... com o objetivo de '
                             'proteger os direitos fundamentais".',
                             'O inciso LXXIX, incluído pela EC 115/2022, assegura a proteção de dados "nos termos da lei". A LGPD é '
                             'essa lei, mesmo sendo anterior à emenda. A natureza muda para REGULAMENTA.', route='art. 1º'),
    'CORRC0-AFD5D339090B': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC150'],
                             'Ementa: "Dispõe sobre o contrato de trabalho doméstico". O art. 1º define o empregado doméstico e o âmbito '
                             'de aplicação.',
                             'O parágrafo único condiciona direitos dos domésticos às "condições estabelecidas em lei", e a LC 150/2015 é '
                             'essa disciplina legal. A classificação da C0 está correta.', route='art. 1º'),
    'CORRC0-142570A4C40E': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L7783'],
                             'Art. 14: "Constitui abuso do direito de greve a inobservância das normas contidas na presente Lei..."; o art. '
                             '15 trata da responsabilidade pelos atos praticados.',
                             'O § 2º sujeita os abusos às penas da lei, e a Lei 7.783/1989 define o abuso (art. 14) e a responsabilidade '
                             '(art. 15). O target e a natureza estão corretos.', route='arts. 14 e 15',
                             notes='A mesma lei também regula o caput (art. 1º) e o § 1º (atividades essenciais, arts. 10 a 13). Esses vínculos não '
                                   'são herdados; ficam como sugestão para candidatos próprios.'),
    'CORRC0-EE675AD3A3EF': D('REJECT', 'ALTA', None, ['LC135', 'LC64'],
                             'Ementa: "Altera a Lei Complementar nº 64, de 18 de maio de 1990, que estabelece, de acordo com o § 9º do '
                             'art. 14 ... casos de inelegibilidade".',
                             'A LC 135/2010 (Ficha Limpa) é lei alteradora. Seu conteúdo normativo vigente está incorporado ao texto '
                             'compilado da LC 64/1990, que é a correlata do § 9º e foi aprovada neste lote. Como vínculo independente no '
                             'botão 1, só duplicaria o mesmo conteúdo.',
                             notes='ALTERADORA_INCORPORADA: o nome "Lei da Ficha Limpa" pode entrar como rótulo/explicação da LC 64, não como vínculo.'),
    'CORRC0-FFA7F8C1F500': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC64'],
                             'Ementa: "Estabelece, de acordo com o art. 14, § 9º da Constituição Federal, casos de inelegibilidade, prazos de '
                             'cessação". O art. 1º traz o rol de inelegibilidades.',
                             'É a lei complementar exigida pelo § 9º, com remissão expressa. A classificação da C0 está correta.',
                             route='art. 1º'),
    'CORRC0-23FDAA617AC7': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L9096'],
                             'Ementa: "regulamenta os arts. 17 e 14, § 3º, inciso V". Art. 7º: "O partido político, após adquirir '
                             'personalidade jurídica na forma da lei civil, registra seu estatuto no Tribunal Superior Eleitoral."',
                             'O art. 7º reproduz e disciplina exatamente o § 2º (registro do estatuto no TSE). O target específico está sustentado.',
                             route='art. 7º'),
    'CORRC0-EC2800C205A0': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L9096'],
                             'Capítulo II "Do Fundo Partidário" (arts. 38 a 44; art. 41-A trata da distribuição). O art. 50-B trata da '
                             'propaganda partidária gratuita no rádio e na TV para partido com estatuto registrado.',
                             'O § 3º condiciona fundo partidário e acesso gratuito a rádio e TV "na forma da lei". A Lei 9.096 é essa forma '
                             '(fundo: arts. 38 a 44; propaganda: art. 50-B, incluído pela Lei 14.291/2022).', route='art. 41-A (e art. 50-B)'),
    'CORRC0-7C51431603DB': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC230'],
                             'Ementa e art. 1º: "normas gerais aplicáveis ao desmembramento de parte de um Município para incorporação a '
                             'outro, limítrofe, nos termos do § 4º do art. 18".',
                             'É a lei complementar federal do § 4º, com remissão expressa, mas com escopo parcial: só o desmembramento '
                             'para incorporação a Município limítrofe.', route='art. 1º',
                             notes='ESCOPO_PARCIAL: criação, fusão e demais hipóteses do § 4º não estão cobertas por esta LC (confirmado pela ementa oficial).'),
    'CORRC0-643E8D275C20': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC90'],
                             'Ementa: "Determina os casos em que forças estrangeiras possam transitar pelo território nacional ou nele '
                             'permanecer temporariamente". O art. 1º lista as hipóteses.',
                             'É exatamente a lei complementar exigida pelo inciso IV ("nos casos previstos em lei complementar"): o art. 1º '
                             'lista os casos em que o Presidente pode permitir o trânsito ou a permanência sem autorização do Congresso.',
                             route='art. 1º'),
    'CORRC0-0ACA5FF28F47': D('REJECT', 'ALTA', None, ['L13848', 'L13709'],
                             'Ementa: "Dispõe sobre a gestão, a organização, o processo decisório e o controle social das agências '
                             'reguladoras...".',
                             'É a lei geral das agências reguladoras. A ligação com o inciso XXVI (organizar e fiscalizar a proteção de '
                             'dados) é só reflexa, porque a ANPD passou a integrar o rol de agências. A organização da proteção de dados está '
                             'na LGPD (arts. 55-A e seguintes, ANPD).',
                             notes='Sugestão fora do lote: candidato LGPD × art. 21, XXVI (arts. 55-A e ss.), a avaliar em rodada própria.'),
    'CORRC0-1FA33FCCC066': D('REJECT', 'ALTA', None, ['L15352', 'L13709'],
                             'Ementa: "Transforma cargos ...; altera a Lei nº 13.709 (LGPD), para dispor sobre a Agência Nacional de '
                             'Proteção de Dados (ANPD)...".',
                             'Lei alteradora: as regras sobre a ANPD foram incorporadas ao texto da LGPD. Como correlata independente '
                             'só duplicaria conteúdo; a utilidade jurídica atual está na LGPD.', notes='ALTERADORA_INCORPORADA.'),
    'CORRC0-5F7CFBD5912A': D('REJECT', 'ALTA', None, ['MP1317'],
                             'Cabeçalho oficial: "Convertida na Lei nº 15.352, de 2026".',
                             'Medida provisória já convertida em lei: é ato histórico, sem utilidade como correlata vigente.',
                             notes='HISTORICA_CONVERTIDA.'),
    'CORRC0-9C3FB3B95B9B': D('APPROVE', 'MEDIA', 'COMPLEMENTA', ['L13303', 'CF88'],
                             'Ementa: "Dispõe sobre o estatuto jurídico da empresa pública, da sociedade de economia mista e de suas '
                             'subsidiárias". Título II, Capítulo I, "Das Licitações" (art. 28 e seguintes).',
                             'O inciso XXVII inclui as normas gerais de licitação das empresas públicas e sociedades de economia mista '
                             '"nos termos do art. 173, § 1º, III", e a Lei 13.303 traz esse regime. COMPLEMENTA é a natureza correta: a '
                             'regulamentação primária é do art. 173, § 1º.', route='art. 28',
                             notes='Sugestão fora do lote: vínculo primário Lei 13.303 × art. 173, § 1º (III).'),
    'CORRC0-C6956D31D6B7': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L14133'],
                             'Art. 1º: "Esta Lei estabelece normas gerais de licitação e contratação para as Administrações Públicas '
                             'diretas, autárquicas e fundacionais da União, dos Estados, do Distrito Federal e dos Municípios".',
                             'São as normas gerais do inciso XXVII para a administração direta, autárquica e fundacional. A natureza muda para '
                             'REGULAMENTA.', route='art. 1º'),
    'CORRC0-7387F1A2A033': D('ADJUST', 'ALTA', 'IMPLEMENTA', ['LC103'],
                             'Ementa: "Autoriza os Estados e o Distrito Federal a instituir o piso salarial a que se refere o inciso V do '
                             'art. 7º ... por aplicação do disposto no parágrafo único do seu art. 22".',
                             'A LC 103/2000 é um exercício concreto da autorização do parágrafo único. A natureza muda de REGULAMENTA '
                             'para IMPLEMENTA.', route='art. 1º',
                             notes='NON_EXCLUSIVE: outras leis complementares podem usar a mesma autorização.'),
    'CORRC0-6B89F3FB8FD7': D('ADJUST', 'ALTA', 'REGULAMENTA', ['LC140'],
                             'Ementa: "Fixa normas, nos termos dos incisos III, VI e VII do caput e do parágrafo único do art. 23 ... para a '
                             'cooperação ... relativas à proteção do meio ambiente, ao combate à poluição...".',
                             'Remissão expressa ao inciso VI. A LC disciplina o exercício cooperativo dessa competência comum. A natureza muda '
                             'para REGULAMENTA.', route='art. 1º'),
    'CORRC0-2E98C1949CA4': D('ADJUST', 'ALTA', 'REGULAMENTA', ['LC140'],
                             'Ementa: as normas são fixadas "nos termos ... do parágrafo único do art. 23".',
                             'É uma das leis complementares de cooperação do parágrafo único, para a matéria ambiental. A natureza muda '
                             'para REGULAMENTA.', route='art. 1º',
                             notes='NON_EXCLUSIVE / ESCOPO_PARCIAL: o parágrafo único fala em "leis complementares"; a LC 140 cobre só o meio ambiente.'),
    'CORRC0-9F2A47C4A756': D('REJECT', 'ALTA', None, ['L8112'],
                             'Lei 8.112/1990: regime jurídico dos servidores civis federais. Não há dispositivo específico sobre nulidade de '
                             'investidura sem concurso nem sobre punição da autoridade nos termos do § 2º.',
                             'O § 2º trata da nulidade e da punição da autoridade quando os incisos II e III do art. 37 não são observados, '
                             'para todos os entes. O estatuto federal é genérico para esse comando e restrito à União. O vínculo legado é '
                             'apenas temático.'),
    'CORRC0-75E9432F8BCD': D('REJECT', 'ALTA', None, ['L8112', 'L8429'],
                             'Lei 8.112/1990: a demissão por improbidade (art. 132, IV) é consequência disciplinar federal. A Lei 8.429/1992, '
                             'pela ementa, é a lei "de que trata o § 4º do art. 37".',
                             'A lei da forma e gradação das sanções de improbidade é a LIA, aprovada neste lote. O estatuto federal é '
                             'incidental e restrito à União.'),
    'CORRC0-9CC6494851BB': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L8429'],
                             'Ementa (redação da Lei 14.230/2021): "Dispõe sobre as sanções aplicáveis em virtude da prática de atos de '
                             'improbidade administrativa, de que trata o § 4º do art. 37".',
                             'Remissão expressa: é a lei do § 4º. A natureza muda para REGULAMENTA.', route='art. 1º'),
    'CORRC0-D961094C030C': D('REJECT', 'MEDIA', None, ['L8112', 'L8429'],
                             'Lei 8.112/1990, art. 142: prescrição da ação disciplinar (5 anos, 2 anos, 180 dias), só para servidores '
                             'federais. Lei 8.429/1992, art. 23: prescrição das ações de improbidade.',
                             'O § 5º trata dos prazos de prescrição de ilícitos que causem prejuízo ao erário, praticados por "qualquer '
                             'agente, servidor ou não". O art. 142 da Lei 8.112 é prescrição disciplinar interna da União, sem relação direta '
                             'e geral com o comando.',
                             notes='Sugestão fora do lote: LIA (Lei 8.429/1992, art. 23) × art. 37, § 5º, a avaliar como candidato próprio.'),
    'CORRC0-E1D20570E8DC': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L12813'],
                             'Ementa: "Dispõe sobre o conflito de interesses no exercício de cargo ou emprego do Poder Executivo federal e '
                             'impedimentos posteriores...". O art. 1º e os arts. 5º e 6º tratam de informação privilegiada.',
                             'O § 7º pede lei sobre requisitos e restrições para quem tem acesso a informações privilegiadas. A Lei 12.813 é '
                             'essa lei no Executivo federal. A natureza está correta, com escopo federal.', route='art. 1º (arts. 5º e 6º)',
                             notes='ESCOPO_FEDERAL: não é regulamentação universal do § 7º (T1_EXTERNAL_CATALOG, LEI_12813_2013).'),
    'CORRC0-F3505EF9129C': D('ADJUST', 'ALTA', 'REGULAMENTA', ['LC152'],
                             'Ementa: "Dispõe sobre a aposentadoria compulsória por idade, com proventos proporcionais, nos termos do inciso '
                             'II do § 1º do art. 40". O art. 2º fixa os 75 anos.',
                             'É a lei complementar exigida pelo inciso II, com remissão expressa. A natureza muda para REGULAMENTA.', route='arts. 1º e 2º'),
    'CORRC0-78E258F9B624': D('HOLD', 'BAIXA', None, ['L8112', 'CF88'],
                             'Lei 8.112/1990: Seção VII "Da Pensão" (art. 215 e seguintes), regime dos servidores federais.',
                             'O § 7º, na redação da EC 103/2019, remete a pensão à "lei do respectivo ente federativo" e exige tratamento '
                             'diferenciado da morte dos servidores do § 4º-B decorrente de agressão. A Lei 8.112 é a lei da União, mas não '
                             'verifiquei se ela, ou outra lei federal, implementa esse tratamento diferenciado. Também não verifiquei como as '
                             'regras transitórias da EC 103 sobre pensão interagem com a Seção VII. Sem isso, não é seguro aprovar nem '
                             'rejeitar.',
                             notes='Revisão independente: confirmar a lei federal que implementa o § 7º (policiais do § 4º-B) e o alcance '
                                   'atual da Seção VII.'),
    'CORRC0-DAD68D5F75A2': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L9717', 'EC103'],
                             'EC 103/2019, art. 9º: "Até que entre em vigor lei complementar que discipline o § 22 do art. 40 ..., aplicam-se '
                             'aos regimes próprios de previdência social o disposto na Lei nº 9.717". A Lei 9.717/1998 traz as regras '
                             'gerais de organização e funcionamento dos RPPS.',
                             'Por determinação constitucional transitória, a Lei 9.717 faz hoje o papel da LC do § 22. O vínculo é '
                             'direto e útil.', route='art. 1º',
                             notes='TRANSITORIA: vale até a lei complementar do § 22 (EC 103/2019, art. 9º). Reavaliar quando ela for editada.'),
}


INDEPENDENT_REVIEW = dict(
    verdict='APPROVED_WITH_ONE_ADJUSTMENT', accepted=21, reject=7, hold=1, relation_type_changes=1, decisions_materially_changed='NO',
    new_candidate_backlog=[dict(norm='Lei nº 13.709/2018 (LGPD)', norm_key='LEI:13709/2018', target_id='CF88:ART.21:INC.XXVI',
                                reason='o regime vigente da ANPD e da proteção de dados está consolidado na LGPD (arts. 55-A e ss.), inclusive '
                                       'após as alterações de 2026; entra em fila própria, sem herança automática',
                                status='BACKLOG_NOT_DECIDED')])
INDEPENDENT_ITEMS = {
    'CORRC0-E1D20570E8DC': dict(verdict='APPROVED_WITH_ADJUSTMENT', relation_type_final='IMPLEMENTA',
                                note='natureza REGULAMENTA → IMPLEMENTA, SCOPE = FEDERAL_EXECUTIVE. A Lei 12.813/2013 concretiza o § 7º só no '
                                     'Poder Executivo federal; não é regulamentação geral para União, Estados, DF e Municípios. ESCOPO_FEDERAL '
                                     'preservado e vínculo mantido.'),
}
ITEM_SCOPE = {
    'CORRC0-E1D20570E8DC': dict(scope='FEDERAL_EXECUTIVE', flags=['ESCOPO_FEDERAL']),
    'CORRC0-7C51431603DB': dict(scope='PARTIAL', flags=['ESCOPO_PARCIAL'],
                                covers='desmembramento de parte de Município para incorporação a outro limítrofe',
                                not_covered='criação, fusão e as demais hipóteses do § 4º'),
    'CORRC0-DAD68D5F75A2': dict(scope='TRANSITORY', flags=['TRANSITORIA'], basis='EC 103/2019, art. 9º',
                                REVALIDATE_ON_NEW_COMPLEMENTARY_LAW=True,
                                note='não é a solução constitucional definitiva do art. 40, § 22'),
}


def jdump(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def select():
    q = json.loads(QUEUE.read_text(encoding='utf-8'))
    pool = []
    for x in q['HIGH']:
        m = re.match(r'^CF88:ART\.(\d+)(?:-[A-Z])?(?::|$)', x['target_id'])
        if m and ART_RANGE[0] <= int(m.group(1)) <= ART_RANGE[1]:
            pool.append(x)
    idx = {t['target_id']: i for i, t in enumerate(json.loads((ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets'])}
    pool.sort(key=lambda x: (idx.get(x['target_id'], 10 ** 6), x['norm_key'], x['candidate_id']))
    batch = pool if len(pool) <= LIMIT_ALL else pool[:LIMIT_TAKE]
    return q, pool, batch


def build():
    q, pool, batch = select()
    cands = {c['candidate_id']: c for c in json.loads(CANDS.read_text(encoding='utf-8'))['candidates']}
    ids = [x['candidate_id'] for x in batch]
    if set(ids) != set(REVIEW) or len(ids) != len(set(ids)):
        raise SystemExit(f'BATCH_DECISION_MISMATCH {sorted(set(ids) ^ set(REVIEW))}')
    inp = []
    for x in batch:
        c = cands[x['candidate_id']]
        inp.append(dict(candidate_id=c['candidate_id'], target_id=c['canonical_target_id'], display_target=c['display_target'], norm_key=c['norm_key'],
                        norm_name=c['norm_name'], c0_relation_type=c['relation_type'], c0_confidence=c['confidence'], c0_priority=c['review_priority'],
                        c0_signal_families=c['signal_families'], c0_acervo_status=c['acervo_status'], c0_device_status=c['device_status'],
                        c0_external_verification_required=c['external_verification_required'], c0_flags=c['flags'],
                        c0_signals=[dict(family=s['family'], source=s['source'], evidence=s['evidence']) for s in c['signals'][:6]]))
    dec = []
    for i in inp:
        r = REVIEW[i['candidate_id']]
        accepted = r['decision'] in ('APPROVE', 'ADJUST')
        dev = i['c0_device_status']
        dec.append(dict(candidate_id=i['candidate_id'], target=i['target_id'], display_target=i['display_target'], norm_key=i['norm_key'],
                        norm_name=i['norm_name'], c0_signals=i['c0_signal_families'], c0_relation_type=i['c0_relation_type'],
                        legal_decision=r['decision'], confidence=r['confidence'],
                        relation_type_final=INDEPENDENT_ITEMS.get(i['candidate_id'], {}).get('relation_type_final', r['relation_type_final']),
                        relation_type_final_initial=r['relation_type_final'],
                        scope=ITEM_SCOPE.get(i['candidate_id']), target_final=(r['target_final'] or i['target_id']) if accepted else None,
                        route=r['route'], device_route_status=dev if accepted else None,
                        ingestion_status=('INGESTION_REQUIRED' if dev == 'INGESTION_REQUIRED' else 'NOT_REQUIRED') if accepted else None,
                        official_sources=[dict(source_id=k, **SOURCES[k]) for k in r['sources']], relevant_provisions=r['provisions'],
                        legal_analysis=r['analysis'], notes=r['notes'], applied=False,
                        independent_review=INDEPENDENT_ITEMS.get(i['candidate_id'], dict(verdict='CONFIRMED'))))
    cnt = Counter(d['legal_decision'] for d in dec)
    acc = [d for d in dec if d['legal_decision'] in ('APPROVE', 'ADJUST')]
    dcnt = Counter(d['device_route_status'] for d in acc)
    summary = dict(batch_candidates=len(dec), pool_high_arts_5_43=len(pool), limit_rule=f'<= {LIMIT_ALL}: todos; > {LIMIT_ALL}: primeiros {LIMIT_TAKE}',
                   left_for_batch02=[x['candidate_id'] for x in pool if x['candidate_id'] not in set(ids)],
                   decisions={k: cnt.get(k, 0) for k in DECISIONS},
                   accepted_device_route={k: dcnt.get(k, 0) for k in ('MAIN_CORPUS_ROUTE_REQUIRED', 'INGESTION_REQUIRED', 'DEVICE_RESOLVABLE_NOW')},
                   all_batch_device_status=dict(sorted(Counter(i['c0_device_status'] for i in inp).items())),
                   relation_type_changed=sum(1 for d in acc if d['relation_type_final_initial'] != d['c0_relation_type']),
                   independent_review_relation_changes=sum(1 for d in acc if d['relation_type_final'] != d['relation_type_final_initial']))
    common = dict(schema_version=1, mission=MISSION, baseline=BASE, applied=False, verified_on=VERIFIED_ON)
    j_in = jdump(dict(common, artifact='CF88_CORRELATA_C1B_HIGH_BATCH01_INPUT',
                      selection=dict(source=f'{QUEUE.relative_to(ROOT).as_posix()} :: HIGH', rule='target CF88 art. 5 a 43; ordem estrutural do Target Index',
                                     pool=len(pool), taken=len(batch), limit_rule=summary['limit_rule'], candidate_ids=ids),
                      candidates=inp))
    j_dec = jdump(dict(common, artifact='CF88_CORRELATA_C1B_HIGH_BATCH01_DECISIONS', decision_values=list(DECISIONS),
                       independent_review=INDEPENDENT_REVIEW,
                       relation_types=list(RELATION_TYPES), source_policy='Somente Planalto (fonte oficial); HTML identificado por sha256, nao versionado.',
                       summary=summary, decisions=dec))
    return j_in, j_dec, report(summary, dec).encode('utf-8')


def report(s, dec):
    L = []
    a = L.append
    a('# CF88_CORRELATA_C1B — HIGH Batch01 (arts. 5º a 43)')
    a('')
    a('**Revisão jurídica assistida. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração no SD ou no firmware.')
    a('')
    a('## Lote')
    a('')
    a(f"- **Seleção:** fila HIGH da C0 com target entre os arts. {ART_RANGE[0]} e {ART_RANGE[1]} da CF, em ordem estrutural.")
    rest = 'nenhum ficou para o Batch02' if not s['left_for_batch02'] else f"{len(s['left_for_batch02'])} ficaram para o Batch02"
    a(f"- **Tamanho:** o pool tem {s['pool_high_arts_5_43']} candidatos. Regra: {s['limit_rule']}. Entraram {s['batch_candidates']}; {rest}.")
    a(f"- **Fontes:** só oficiais (Planalto), verificadas em {VERIFIED_ON}, com sha256 de cada página.")
    a('- **Decisão jurídica e rota de aparelho ficam separadas.** MAIN_CORPUS_ROUTE_REQUIRED e INGESTION_REQUIRED não impedem a aprovação.')
    a('')
    a('## Contabilidade')
    a('')
    a('| Decisão | n |')
    a('|---|---:|')
    for k in DECISIONS:
        a(f"| {k} | {s['decisions'][k]} |")
    a(f"| **Total** | **{s['batch_candidates']}** |")
    a('')
    a('**Rota de aparelho dos aceitos (APPROVE + ADJUST)**')
    a('')
    a('| Rota | n |')
    a('|---|---:|')
    for k, v in s['accepted_device_route'].items():
        a(f'| {k} | {v} |')
    a('')
    a(f"- **Natureza da relação:** reclassificada em {s['relation_type_changed']} dos aceitos. É o motivo da maioria dos ADJUST, porque a "
      'C0 tinha atribuído COMPLEMENTA a leis que se declaram regulamentadoras.')
    a('')
    a('## Decisões')
    a('')
    a('| # | Target | Norma | Decisão | Natureza final | Rota | Aparelho |')
    a('|---:|---|---|---|---|---|---|')
    for i, d in enumerate(dec, 1):
        a(f"| {i} | {d['display_target']} | {d['norm_name']} | **{d['legal_decision']}** | {d['relation_type_final'] or '—'} | {d['route'] or '—'} | "
          f"{d['device_route_status'] or '—'} |")
    a('')
    for i, d in enumerate(dec, 1):
        a(f"### {i}. {d['display_target']} × {d['norm_name']}: **{d['legal_decision']}** ({d['confidence']})")
        a('')
        a(f"- **candidate_id:** `{d['candidate_id']}`")
        a(f"- **Target:** `{d['target']}`; target final `{d['target_final']}`.")
        a(f"- **Sinais C0:** {', '.join(d['c0_signals'])}; natureza C0 {d['c0_relation_type']}.")
        a('- **Fonte oficial:**')
        for f in d['official_sources']:
            a(f"  - {f['norm']}: {f['url']} ({f['verified_on']}, sha256 `{f['sha256'][:16]}…`)")
        a(f"- **Dispositivos relevantes:** {d['relevant_provisions']}")
        a(f"- **Análise:** {d['legal_analysis']}")
        if d['notes']:
            a(f"- **Observações:** {d['notes']}")
        a('')
    ir = INDEPENDENT_REVIEW
    a('## Revisão independente do Batch01')
    a('')
    a(f"- `BATCH01_INDEPENDENT_REVIEW = {ir['verdict']}`")
    a(f"- **Contagem:** inclusões e exclusões inalteradas: aceitos {ir['accepted']}, REJECT {ir['reject']}, HOLD {ir['hold']}.")
    a(f"- **Ajuste:** só {ir['relation_type_changes']} aceito muda de natureza.")
    for k, v in INDEPENDENT_ITEMS.items():
        d = next(x for x in dec if x['candidate_id'] == k)
        a(f"- **{d['display_target']} × {d['norm_name']}:** {v['note']}")
    for k, v in ITEM_SCOPE.items():
        d = next(x for x in dec if x['candidate_id'] == k)
        a(f"- **{d['display_target']} × {d['norm_name']}:** escopo `{json.dumps(v, ensure_ascii=False)}`.")
    a('- **NEW_CANDIDATE_BACKLOG** (não é decisão deste lote):')
    for b in ir['new_candidate_backlog']:
        a(f"  - {b['norm']} × `{b['target_id']}`: {b['reason']}")
    a('')
    a('## Fora deste lote')
    a('')
    a('- **Candidatos sugeridos nas observações** (decididos aqui só como sugestão, não como vínculo):')
    a('  - LGPD × art. 21, XXVI;')
    a('  - LIA, art. 23 × art. 37, § 5º;')
    a('  - Lei 13.303 × art. 173, § 1º;')
    a('  - Lei 7.783 × art. 9º, caput e § 1º.')
    a('- **Não revisados:** os candidatos MEDIUM e LOW, e os HIGH fora dos arts. 5º a 43.')
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('C1B_NOT_DETERMINISTIC')
    paths = (OUT_IN, OUT_DEC, OUT_MD)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[1])['summary'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
