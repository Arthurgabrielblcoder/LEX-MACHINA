"""CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH02 — next HIGH candidates after Batch01, in structural Target Index order (max 30).

Selection (derived): C0 queue HIGH, minus every Batch01 candidate, minus pairs (target x norm) already decided in C1A (current links
and their replacements), minus duplicates of target x norm; sorted by the Target Index; first 30. Decisions were taken against the
official text (Planalto, downloaded on VERIFIED_ON, sha256 recorded, HTML not versioned). LEGAL_DECISION is kept apart from the
device route. New relations found while reviewing go to NEW_CANDIDATE_BACKLOG (never decided here). NOTHING IS APPLIED.

Writes CF88_CORRELATA_C1B_HIGH_BATCH02_{INPUT.json, DECISIONS.json, REPORT.md}. Usage: python build_c1b_high_batch02.py [--check]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_c1b_high_batch01 as B1  # noqa: E402

AUDIT, ROOT = B1.AUDIT, B1.ROOT
MISSION = 'CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH02'
BASE = dict(branch='cf-correlata-coverage-audit', head='95791c4b7eb4588bb012fe89ff6a1ba44099cdcf')
C1A_DECISIONS = AUDIT / 'CF88_CORRELATA_C1A_DECISIONS.json'
OUT_IN = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH02_INPUT.json'
OUT_DEC = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH02_DECISIONS.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH02_REPORT.md'
LIMIT = 30
S, D = B1.S, B1.D

SOURCES = {
    'CF88': B1.SOURCES['CF88'],
    'LC78': S('Lei Complementar nº 78/1993', 'leis/lcp/lcp78.htm', '17443dd7b87849063c30e20397f526dbe83163cb07d995890a93f3a9911bb27b', 5756),
    'LC90': S('Lei Complementar nº 90/1997', 'leis/lcp/lcp90.htm', '5406ba9a656983eec0ddd347023cdc70d5f8fa971d271105460c50ee60149057', 12886),
    'LC107': S('Lei Complementar nº 107/2001', 'leis/lcp/lcp107.htm', 'f562a1be8dd160a44c9577c8a18b8279837e4ced2fed2f173b7a806283560eac', 16578),
    'LC95': S('Lei Complementar nº 95/1998', 'leis/lcp/lcp95.htm', '3507b83cec6b50f7b6572bc7fdc7ea1625c714e7a531bd64865323680df353b3', 39852),
    'L4320': S('Lei nº 4.320/1964', 'leis/l4320.htm', '28d03d38a72e9f4e5ec2e80454ff74354bbcae31891b86213119422c26943799', 141445),
    'L9868': S('Lei nº 9.868/1999', 'leis/l9868.htm', 'dda0ebaeb9c708d38b43a769c8f7316e7f4926776d35363d7f224038c47ec8a5', 42059),
    'L11417': S('Lei nº 11.417/2006', '_ato2004-2006/2006/lei/l11417.htm', '2d358cb867abd0a930858735bc586c0991be9ed7d54e6d3f257b8ec573f63493', 17830),
    'L15484': S('Lei nº 15.484/2026', '_ato2023-2026/2026/lei/l15484.htm', '4a0e49e374a8899456590b3da62b117cd4d89a07f5a64869617093e263d76166', 42458),
    'LC75': S('Lei Complementar nº 75/1993 (MPU)', 'leis/lcp/lcp75.htm', 'e52cd3f20f45fbbf23bbd4bcf58d7128b34bc77282a7c0bf8181f5fcc7951ef9', 353952),
    'L14965': S('Lei nº 14.965/2024', '_ato2023-2026/2024/lei/l14965.htm', '48c23ae7efc4f8d7d895170c5b59202c9635f3585326cd54a2b6b5f304678ce3', 55968),
    'LC80': S('Lei Complementar nº 80/1994', 'leis/lcp/lcp80.htm', '9379b747c3a763b1c87849a4eb3af9a3d2d37308831b07c3219a543b77356d61', 303697),
    'LC83': S('Lei Complementar nº 83/1995', 'leis/lcp/lcp83.htm', '5f830bd1be9c89e47bd8fb5c10eb28113e552a5d5879486b64a62bab2852aca9', 6706),
    'LC69': S('Lei Complementar nº 69/1991 (revogada)', 'leis/lcp/lcp69.htm', '90aef067a2bb755b0c29ac6a018ba6d2c0925d51e905ca50d3a6b32ce8204a67', 18358),
    'LC97': S('Lei Complementar nº 97/1999', 'leis/lcp/lcp97.htm', 'c5867ecc923b4b57f31a04cd6a42fa7f6fbe9cce4cd8c29802f7399168f1631e', 61355),
    'L6880': S('Lei nº 6.880/1980 (Estatuto dos Militares)', 'leis/l6880.htm', 'a9c01802819cb3d31c7d087d073c13340afbdfb4bf8ce2f2e86ba9ffbd5422ef', 381830),
    'L13022': S('Lei nº 13.022/2014', '_ato2011-2014/2014/lei/l13022.htm', '53d8b731a8a033619dd9fa0dd86a46e594ce75fadd7960212d16b12758b7b5a2', 38582),
    'LC214': S('Lei Complementar nº 214/2025', 'leis/lcp/lcp214.htm', '56324955fe0d7644fda1adc5475f1a06edac77801606fbac03ce9204ebe84e2b', 5403613),
    'LC199': S('Lei Complementar nº 199/2023', 'leis/lcp/lcp199.htm', 'f99a6c41aa0b22d5d2f523a15255b16f103feb992b69588db09a60dc2541ec55', 38182),
    'LC123': S('Lei Complementar nº 123/2006', 'leis/lcp/lcp123.htm', '5c4ab2706186613e8cefe40434202b72936d9fb495ca8eb41493879511fb0af9', 1622252),
    'LC227': S('Lei Complementar nº 227/2026', 'leis/lcp/lcp227.htm', '39503f69ea3ce721199b712536fdcee0609f128dbe9c25228ae510baae23b83b', 1334008),
    'LC102': S('Lei Complementar nº 102/2000', 'leis/lcp/lcp102.htm', '9320865d69ec2ed729d9fce32b45a1df9753e5711b7182a42a25542c836f9061', 51664),
    'LC99': S('Lei Complementar nº 99/1999', 'leis/lcp/lcp99.htm', 'a502da9c0cc58468bac6163ef3d99795136a78adf3bd3c4224feedad7a2f8693', 6615),
}

REVIEW = {
    'CORRC0-EF96FA80B154': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC78'],
                             'Ementa: "Disciplina a fixação do número de Deputados, nos termos do art. 45, § 1º". O art. 1º trata do limite de '
                             '513 e da base populacional fornecida pelo IBGE.',
                             'É a lei complementar exigida pelo § 1º, com remissão expressa.', route='art. 1º'),
    'CORRC0-9AB7A934F0B2': D('ADJUST', 'ALTA', 'CONDIÇÃO_OU_EXCEÇÃO', ['LC90'],
                             'Art. 1º: o Presidente pode permitir o trânsito ou a permanência de forças estrangeiras "independente da '
                             'autorização do Congresso Nacional", nos casos listados.',
                             'O inciso II atribui ao Congresso autorizar a permissão a forças estrangeiras, "ressalvados os casos previstos em '
                             'lei complementar". A LC 90 define exatamente essa ressalva. A natureza é exceção à competência do Congresso '
                             '(CONDIÇÃO_OU_EXCEÇÃO), não regulamentação.', route='art. 1º'),
    'CORRC0-DB7354F1B905': D('REJECT', 'ALTA', None, ['LC107', 'LC95'],
                             'Ementa: "Altera a Lei Complementar nº 95, de 26 de fevereiro de 1998"; o art. 1º dá nova redação aos arts. 8º, 9º, 11 '
                             'a 14 da LC 95.',
                             'Lei alteradora sem conteúdo autônomo relevante: as novas redações estão incorporadas ao texto compilado da LC 95, '
                             'aprovada neste lote.', notes='ALTERADORA_INCORPORADA.'),
    'CORRC0-C6DD33BDB4E1': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC95'],
                             'Ementa: "Dispõe sobre a elaboração, a redação, a alteração e a consolidação das leis, conforme determina o '
                             'parágrafo único do art. 59".',
                             'É a lei complementar do parágrafo único, com remissão expressa.', route='art. 1º'),
    'CORRC0-245CA29208BF': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC90'],
                             'Art. 1º: "Poderá o Presidente da República permitir que forças estrangeiras transitem ... nos seguintes casos".',
                             'O inciso XXII atribui ao Presidente a permissão "nos casos previstos em lei complementar", e a LC 90 enumera esses '
                             'casos. Do lado do Presidente, ela regulamenta diretamente a competência.', route='art. 1º'),
    'CORRC0-690721F4196B': D('REJECT', 'MEDIA', None, ['L4320'],
                             'Lei 4.320/1964, art. 34: "O exercício financeiro coincidirá com o ano civil."',
                             'O § 5º trata da inclusão orçamentária obrigatória e do prazo de pagamento dos precatórios. A Lei 4.320 só fornece '
                             'o conceito auxiliar de exercício financeiro e não disciplina precatórios. A relação é definitória e incidental.'),
    'CORRC0-35E96F1CA181': D('ADJUST', 'ALTA', 'PROCEDIMENTO', ['L9868'],
                             'Ementa: "Dispõe sobre o processo e julgamento da ADI e da ADC perante o STF". Art. 28, parágrafo único: a '
                             'declaração tem "eficácia contra todos e efeito vinculante". O art. 27 trata da modulação de efeitos.',
                             'A lei disciplina o processo em que se produzem os efeitos do § 2º e os detalha (arts. 27 e 28). A natureza '
                             'muda de COMPLEMENTA para PROCEDIMENTO.', route='art. 28'),
    'CORRC0-420E49E80EF9': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L11417'],
                             'Ementa: "Regulamenta o art. 103-A ... disciplinando a edição, a revisão e o cancelamento de enunciado de súmula '
                             'vinculante". O art. 3º lista os legitimados a propor.',
                             'O § 2º ressalva "o que vier a ser estabelecido em lei" sobre quem pode provocar a súmula, e o art. 3º da Lei '
                             '11.417 é essa lei.', route='art. 3º',
                             notes='A mesma lei também regula o caput do art. 103-A (art. 2º). Não há herança automática: fica para candidato próprio.'),
    'CORRC0-8E5A28F8F96F': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L11417'],
                             'Art. 7º: cabe reclamação ao STF da decisão ou do ato que contrariar a súmula vinculante. O § 1º exige o '
                             'esgotamento das vias administrativas contra ato ou omissão da administração.',
                             'O art. 7º disciplina diretamente a reclamação do § 3º, inclusive com condição de cabimento. A natureza muda de '
                             'COMPLEMENTA para REGULAMENTA.', route='art. 7º'),
    'CORRC0-312A79978F0C': D('APPROVE', 'ALTA', 'REGULAMENTA', ['L15484'],
                             'Ementa e art. 1º: "Regulamenta o regime de relevância das questões de direito federal infraconstitucional para '
                             'admissão dos recursos especiais no STJ".',
                             'O § 2º exige a demonstração da relevância "nos termos da lei", e a Lei 15.484/2026 é essa lei.', route='art. 1º',
                             notes='Norma recente (2026): ingestão necessária; a vigência deve ser reconferida na ingestão.'),
    'CORRC0-3A3521E4F0DB': D('ADJUST', 'ALTA', 'IMPLEMENTA', ['LC75'],
                             'LC 75/1993, art. 156: o Procurador-Geral de Justiça do DF e Territórios é nomeado pelo Presidente da '
                             'República dentre integrantes de lista tríplice, para mandato de dois anos, permitida uma recondução.',
                             'O § 3º remete à "lei respectiva" de cada MP. A LC 75 concretiza o comando só para o MPDFT; os Ministérios '
                             'Públicos estaduais seguem suas próprias leis. A natureza muda para IMPLEMENTA, com escopo restrito.',
                             route='art. 156', notes='ESCOPO_MPDFT; NON_EXCLUSIVE (leis orgânicas estaduais e Lei 8.625/1993).'),
    'CORRC0-FB380CBD6CBF': D('ADJUST', 'ALTA', 'IMPLEMENTA', ['LC75'],
                             'LC 75/1993, art. 156, § 2º: o Procurador-Geral pode ser destituído antes do término do mandato por deliberação '
                             'da maioria absoluta do Senado Federal.',
                             'O § 4º remete à "lei complementar respectiva". Para o MPDFT, a LC 75 é essa lei, com o Senado no papel de '
                             'Poder Legislativo. Nos Estados valem as leis complementares estaduais. A natureza muda para IMPLEMENTA, com '
                             'escopo MPDFT.', route='art. 156, § 2º', notes='ESCOPO_MPDFT; NON_EXCLUSIVE.'),
    'CORRC0-E0CCCEFB92EC': D('ADJUST', 'ALTA', 'IMPLEMENTA', ['LC75'],
                             'LC 75/1993, art. 8º: nos procedimentos de sua competência, o MPU pode notificar testemunhas e requisitar '
                             'informações, exames, perícias e documentos.',
                             'O inciso VI remete à "lei complementar respectiva". A LC 75 implementa o poder de notificação e requisição para o '
                             'MPU; os MPs estaduais seguem as leis complementares estaduais. A natureza muda para IMPLEMENTA.',
                             route='art. 8º', notes='ESCOPO_MPU; NON_EXCLUSIVE.'),
    'CORRC0-02E5634C2228': D('ADJUST', 'ALTA', 'IMPLEMENTA', ['LC75'],
                             'LC 75/1993, Capítulo III, "Do Controle Externo da Atividade Policial", art. 9º: o MPU exerce o controle externo '
                             'por medidas judiciais e extrajudiciais, com livre ingresso em estabelecimentos policiais e acesso a documentos.',
                             'O inciso VII remete à lei complementar do art. 128, § 5º. A LC 75 implementa o controle externo no âmbito do MPU. '
                             'A natureza muda para IMPLEMENTA.', route='art. 9º', notes='ESCOPO_MPU; NON_EXCLUSIVE.'),
    'CORRC0-29C48A0D5DA7': D('APPROVE', 'ALTA', 'COMPLEMENTA', ['L14965'],
                             'Lei 14.965/2024, art. 1º, § 2º: "Esta Lei aplica-se subsidiariamente aos concursos públicos previstos no § 2º do '
                             'art. 131 e no art. 132 ..., naquilo que não contrariar normas específicas ... e das leis orgânicas".',
                             'Remissão expressa ao § 2º. A aplicação é subsidiária: as normas gerais de concurso complementam a lei orgânica '
                             'da AGU. COMPLEMENTA está correto.', route='art. 1º, § 2º',
                             notes='SUBSIDIARIA; NON_EXCLUSIVE: a disciplina principal da carreira está na lei orgânica da AGU (LC 73/1993), '
                                   'não avaliada neste lote.'),
    'CORRC0-08F347BF86E6': D('APPROVE', 'ALTA', 'COMPLEMENTA', ['L14965'],
                             'Lei 14.965/2024, art. 1º, § 2º: aplicação subsidiária "aos concursos públicos previstos ... no art. 132".',
                             'O caput do art. 132 exige concurso público de provas e títulos para os Procuradores dos Estados e do DF, e a lei '
                             'o alcança de forma expressa e subsidiária. O target é ART.132, a unidade de apresentação do caput.',
                             route='art. 1º, § 2º', notes='SUBSIDIARIA; NON_EXCLUSIVE (leis orgânicas estaduais).'),
    'CORRC0-0232EB5B26DB': D('ADJUST', 'ALTA', 'ORGANIZA_INSTITUIÇÃO', ['LC80'],
                             'Ementa: "Organiza a Defensoria Pública da União, do Distrito Federal e dos Territórios e prescreve normas gerais '
                             'para sua organização nos Estados".',
                             'A ementa reproduz o comando do § 1º. É a lei orgânica da instituição. A natureza muda de REGULAMENTA para '
                             'ORGANIZA_INSTITUIÇÃO.', route='art. 1º'),
    'CORRC0-4EEAA9F57A2A': D('REJECT', 'ALTA', None, ['LC83', 'LC69'],
                             'LC 83/1995, ementa: "Altera dispositivo da Lei Complementar nº 69, de 23 de julho de 1991". A página oficial da '
                             'LC 69/1991 indica "Revogada pela Lei Complementar nº 97, de 1999".',
                             'É alteração de uma lei complementar revogada: ato histórico, sem utilidade como correlata vigente. A correlata '
                             'atual do § 1º é a LC 97/1999, aprovada neste lote.', notes='HISTORICA_ALTERADORA_DE_LEI_REVOGADA.'),
    'CORRC0-7A1757A796C5': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC97'],
                             'Ementa: "Dispõe sobre as normas gerais para a organização, o preparo e o emprego das Forças Armadas".',
                             'A ementa reproduz exatamente o comando do § 1º. É a lei complementar exigida.', route='art. 1º'),
    'CORRC0-4A61114D26A5': D('REJECT', 'ALTA', None, ['LC97', 'L6880'],
                             'LC 97/1999: normas gerais de organização, preparo e emprego das Forças Armadas. Lei 6.880/1980, art. 1º: "O '
                             'presente Estatuto regula a situação, obrigações, deveres, direitos e prerrogativas" dos militares.',
                             'O § 3º trata do estatuto pessoal dos militares, além das disposições "que vierem a ser fixadas em lei". Essa '
                             'matéria é do Estatuto dos Militares, não da LC 97. A ligação com a LC 97 é só temática: é fan-out do § 1º para o § 3º.',
                             notes='NEW_CANDIDATE_BACKLOG: Lei 6.880/1980 × art. 142, § 3º.'),
    'CORRC0-B603B2579A60': D('ADJUST', 'ALTA', 'REGULAMENTA', ['L13022'],
                             'Art. 1º: "Esta Lei institui normas gerais para as guardas municipais, disciplinando o § 8º do art. 144".',
                             'Regulamentação expressa do § 8º. A natureza muda de COMPLEMENTA para REGULAMENTA.', route='art. 1º'),
    'CORRC0-E6E419F28886': D('REJECT', 'MEDIA', None, ['LC214', 'CF88'],
                             'Ementa: "Institui o IBS, a CBS e o Imposto Seletivo; cria o Comitê Gestor do IBS e altera a legislação tributária".',
                             'O inciso III reserva à lei complementar as normas gerais em matéria tributária. A LC 214 institui tributos '
                             'específicos (arts. 156-A, 195, V, e 153, VIII), não é a lei geral do inciso. Ela só toca as alíneas c e d '
                             'reflexamente. O vínculo útil está nos dispositivos dos novos tributos.',
                             notes='NEW_CANDIDATE_BACKLOG: LC 214/2025 × art. 156-A e art. 195, V (dispositivos instituidores).'),
    'CORRC0-8CF6938B096C': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC199'],
                             'Art. 1º: institui o Estatuto Nacional de Simplificação de Obrigações Tributárias Acessórias "em observância ao '
                             'disposto na alínea b do inciso III do caput do art. 146".',
                             'Remissão expressa à alínea b. A LC 199 é uma lei complementar de normas gerais sobre obrigação tributária '
                             '(acessória). O escopo é parcial: não cobre lançamento, crédito, prescrição nem decadência, que estão no CTN.',
                             route='art. 1º',
                             notes='ESCOPO_PARCIAL; NON_EXCLUSIVE (CTN). O vínculo atual LC 199 × ART.146, no nível do artigo, deve ser '
                                   'reavaliado em C2 como retarget para esta alínea.'),
    'CORRC0-781D2FD631FD': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC123'],
                             'LC 123/2006, art. 12: "Fica instituído o Regime Especial Unificado de Arrecadação de Tributos e Contribuições '
                             'devidos pelas Microempresas e Empresas de Pequeno Porte - Simples Nacional". O art. 1º, IV remete ao cadastro do '
                             '"inciso IV do § 1º do art. 146".',
                             'O § 1º prevê o regime único de arrecadação por lei complementar, e o Simples Nacional da LC 123 é esse regime.',
                             route='art. 12'),
    'CORRC0-2C927C32607D': D('APPROVE', 'MEDIA', 'COMPLEMENTA', ['LC214', 'LC123'],
                             'LC 214/2025, art. 41, §§ 1º a 3º: os optantes pelo Simples Nacional ficam sujeitos às regras desse regime e podem '
                             'optar por apurar e recolher IBS e CBS pelo regime regular.',
                             'O § 1º, após a EC 132, admite o IBS e a CBS no regime único. A LC 214 também alterou a LC 123 (essas alterações '
                             'estão incorporadas lá), mas o art. 41 tem conteúdo autônomo vigente sobre a convivência Simples × IBS/CBS que '
                             'não está representado na LC 123. Pela exceção da política de leis alteradoras, aprovo como COMPLEMENTA.',
                             route='art. 41', notes='ESCOPO_PARCIAL; NON_EXCLUSIVE (LC 123 é a principal).'),
    'CORRC0-83C4D0DE51F8': D('REJECT', 'MEDIA', None, ['LC214'],
                             'LC 214/2025, art. 454: a partir de 2027, as alíquotas do IPI ficam reduzidas a zero para certos produtos não '
                             'industrializados na Zona Franca de Manaus.',
                             'O § 3º fixa as características constitucionais do IPI (seletividade, não cumulatividade, imunidade na exportação '
                             'etc.). O art. 454 é regra de transição ligada à Zona Franca (reforma tributária), não disciplina esses '
                             'atributos. A relação com o § 3º é temática.',
                             notes='NEW_CANDIDATE_BACKLOG: LC 214/2025, art. 454 × ADCT, regras de transição da Zona Franca (EC 132/2023).'),
    'CORRC0-4A80B12218AA': D('ADJUST', 'ALTA', 'REGULAMENTA', ['LC214'],
                             'LC 214/2025, art. 409: "Fica instituído o Imposto Seletivo, de que trata o inciso VIII do art. 153..."; o Livro '
                             'II disciplina o imposto, inclusive a incidência única.',
                             'A remissão expressa da LC 214 é ao inciso VIII, que cria a competência. O § 6º só lista características do imposto. '
                             'Pela regra do target mais específico sustentado pela fonte, o vínculo vai para o inciso VIII; a relação com o § 6º '
                             'é reflexa. O ajuste é de target.',
                             route='art. 409', target='CF88:ART.153:INC.VIII',
                             notes='O § 6º deixa de ser target deste candidato; um vínculo próprio no § 6º exigiria fundamento individual.'),
    'CORRC0-A97DCCBA85CF': D('APPROVE', 'ALTA', 'REGULAMENTA', ['LC227'],
                             'LC 227/2026: a ementa "institui normas gerais relativas ao ITCMD". O Livro II (art. 146: "de que trata o inciso I '
                             'do caput do art. 155") regula competência, base e regras de domicílio, e o art. 158 trata dos casos com elemento no '
                             'exterior.',
                             'O § 1º disciplina o imposto do inciso I (ITCMD): competência por situação do bem e domicílio, progressividade e '
                             'demais regras. A LC 227 é a lei complementar de normas gerais que concretiza esses comandos.', route='art. 146',
                             notes='NON_EXCLUSIVE. NEW_CANDIDATE_BACKLOG: LC 227/2026 (art. 158) × art. 155, § 1º, III, alvo que ficou sem '
                                   'correlata após a remoção da LC 87 na C1A.'),
    'CORRC0-E1EE9B658B50': D('REJECT', 'ALTA', None, ['LC102'],
                             'Ementa: "Altera dispositivos da Lei Complementar nº 87, de 13 de setembro de 1996", que é a lei do ICMS.',
                             'O § 1º, III é ITCMD. A LC 102 é alteradora da lei do ICMS. Não há relação com o target e o conteúdo está '
                             'incorporado à LC 87.', notes='ALTERADORA_INCORPORADA; FAN_OUT_LEGADO.'),
    'CORRC0-ED873A7A92E9': D('REJECT', 'ALTA', None, ['LC99'],
                             'Ementa: "Dá nova redação ao inciso I do art. 33 da Lei Complementar nº 87, de 13 de setembro de 1996" (ICMS).',
                             'Alteradora pontual da lei do ICMS, sem relação com o ITCMD do § 1º, III.', notes='ALTERADORA_INCORPORADA; FAN_OUT_LEGADO.'),
}

NEW_CANDIDATE_BACKLOG = [
    dict(norm='Lei nº 6.880/1980 (Estatuto dos Militares)', norm_key='LEI:6880/1980', target_id='CF88:ART.142:PAR.3', origin='CORRC0-4A61114D26A5'),
    dict(norm='Lei Complementar nº 214/2025', norm_key='LC:214/2025', target_id='CF88:ART.156-A', origin='CORRC0-E6E419F28886'),
    dict(norm='Lei Complementar nº 214/2025', norm_key='LC:214/2025', target_id='CF88:ART.195:INC.V', origin='CORRC0-E6E419F28886'),
    dict(norm='Lei Complementar nº 214/2025 (art. 454)', norm_key='LC:214/2025', target_id='ADCT (transição Zona Franca, EC 132/2023)', origin='CORRC0-83C4D0DE51F8'),
    dict(norm='Lei Complementar nº 227/2026 (art. 158)', norm_key='LC:227/2026', target_id='CF88:ART.155:PAR.1:INC.III', origin='CORRC0-A97DCCBA85CF'),
    dict(norm='Lei nº 11.417/2006 (art. 2º)', norm_key='LEI:11417/2006', target_id='CF88:ART.103-A', origin='CORRC0-420E49E80EF9'),
]


def select():
    q = json.loads(B1.QUEUE.read_text(encoding='utf-8'))
    b1 = set(json.loads(B1.OUT_IN.read_text(encoding='utf-8'))['selection']['candidate_ids'])
    c1a = json.loads(C1A_DECISIONS.read_text(encoding='utf-8'))
    decided = {(d['current_target'], d['current_norm_id']) for d in c1a['decisions']}
    decided_keys = {(n['target_id'], n['norm_key']) for d in c1a['decisions'] for n in d['replacement_norms']}
    cands = {c['candidate_id']: c for c in json.loads(B1.CANDS.read_text(encoding='utf-8'))['candidates']}
    idx = {t['target_id']: i for i, t in enumerate(json.loads((ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets'])}
    seen, pool, excluded = set(), [], []
    for x in sorted(q['HIGH'], key=lambda x: (idx.get(x['target_id'], 10 ** 6), x['norm_key'], x['candidate_id'])):
        key = (x['target_id'], x['norm_key'])
        if x['candidate_id'] in b1:
            excluded.append(dict(candidate_id=x['candidate_id'], reason='BATCH01'))
        elif key in decided_keys or (x['target_id'], cands[x['candidate_id']].get('acervo_id')) in decided:
            excluded.append(dict(candidate_id=x['candidate_id'], reason='C1A'))
        elif key in seen:
            excluded.append(dict(candidate_id=x['candidate_id'], reason='DUPLICATE_TARGET_NORM'))
        else:
            seen.add(key)
            pool.append(x)
    return q, pool, pool[:LIMIT], excluded, cands


def build():
    q, pool, batch, excluded, cands = select()
    ids = [x['candidate_id'] for x in batch]
    if set(ids) != set(REVIEW):
        raise SystemExit(f'BATCH02_DECISION_MISMATCH {sorted(set(ids) ^ set(REVIEW))}')
    inp, dec = [], []
    for x in batch:
        c = cands[x['candidate_id']]
        inp.append(dict(candidate_id=c['candidate_id'], target_id=c['canonical_target_id'], display_target=c['display_target'], norm_key=c['norm_key'],
                        norm_name=c['norm_name'], c0_relation_type=c['relation_type'], c0_confidence=c['confidence'], c0_priority=c['review_priority'],
                        c0_signal_families=c['signal_families'], c0_device_status=c['device_status'], c0_flags=c['flags'],
                        c0_signals=[dict(family=s['family'], source=s['source'], evidence=s['evidence']) for s in c['signals'][:6]]))
    for i in inp:
        r = REVIEW[i['candidate_id']]
        ok = r['decision'] in ('APPROVE', 'ADJUST')
        dev = i['c0_device_status']
        dec.append(dict(candidate_id=i['candidate_id'], target=i['target_id'], display_target=i['display_target'], norm_key=i['norm_key'],
                        norm_name=i['norm_name'], c0_signals=i['c0_signal_families'], c0_relation_type=i['c0_relation_type'],
                        legal_decision=r['decision'], confidence=r['confidence'], relation_type_final=r['relation_type_final'],
                        target_final=(r['target_final'] or i['target_id']) if ok else None, route=r['route'],
                        device_route_status=dev if ok else None,
                        ingestion_status=('INGESTION_REQUIRED' if dev == 'INGESTION_REQUIRED' else 'NOT_REQUIRED') if ok else None,
                        scope_flags=sorted(set(re.findall(r'\b[A-Z]{2,}(?:_[A-Z0-9]+)+\b', r['notes'] or ''))),
                        official_sources=[dict(source_id=k, **SOURCES[k]) for k in r['sources']], relevant_provisions=r['provisions'],
                        legal_analysis=r['analysis'], notes=r['notes'], applied=False))
    cnt = Counter(d['legal_decision'] for d in dec)
    acc = [d for d in dec if d['legal_decision'] in ('APPROVE', 'ADJUST')]
    dcnt = Counter(d['device_route_status'] for d in acc)
    remaining = len(pool) - len(batch)
    summary = dict(batch_candidates=len(dec), high_total=len(q['HIGH']), excluded_from_pool=dict(sorted(Counter(e['reason'] for e in excluded).items())),
                   eligible_pool=len(pool), limit=LIMIT, high_remaining_after_batch02=remaining,
                   decisions={k: cnt.get(k, 0) for k in B1.DECISIONS},
                   accepted_device_route={k: dcnt.get(k, 0) for k in ('MAIN_CORPUS_ROUTE_REQUIRED', 'INGESTION_REQUIRED', 'DEVICE_RESOLVABLE_NOW')},
                   all_batch_device_status=dict(sorted(Counter(i['c0_device_status'] for i in inp).items())),
                   relation_type_changed=sum(1 for d in acc if d['relation_type_final'] != d['c0_relation_type']),
                   target_changed=sum(1 for d in acc if d['target_final'] != d['target']), new_candidate_backlog=len(NEW_CANDIDATE_BACKLOG))
    common = dict(schema_version=1, mission=MISSION, baseline=BASE, applied=False, verified_on=B1.VERIFIED_ON)
    j_in = B1.jdump(dict(common, artifact='CF88_CORRELATA_C1B_HIGH_BATCH02_INPUT',
                         selection=dict(source='CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_REVIEW_QUEUE.json :: HIGH',
                                        rule='HIGH - Batch01 - C1A - duplicatas target x norma; ordem estrutural do Target Index; maximo 30',
                                        excluded=excluded, eligible_pool=len(pool), taken=len(batch), candidate_ids=ids,
                                        remaining_after=[x['candidate_id'] for x in pool[LIMIT:]]),
                         candidates=inp))
    j_dec = B1.jdump(dict(common, artifact='CF88_CORRELATA_C1B_HIGH_BATCH02_DECISIONS', decision_values=list(B1.DECISIONS),
                          relation_types=list(B1.RELATION_TYPES), source_policy='Somente Planalto (fonte oficial); HTML identificado por sha256, nao versionado.',
                          summary=summary, decisions=dec, NEW_CANDIDATE_BACKLOG=[dict(b, status='BACKLOG_NOT_DECIDED') for b in NEW_CANDIDATE_BACKLOG]))
    return j_in, j_dec, report(summary, dec).encode('utf-8')


def report(s, dec):
    L = []
    a = L.append
    a('# CF88_CORRELATA_C1B — HIGH Batch02')
    a('')
    a('**Revisão jurídica assistida. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração no SD ou no firmware.')
    a('')
    a('## Lote')
    a('')
    a(f"- **Seleção:** fila HIGH da C0 ({s['high_total']} candidatos) menos os excluídos {s['excluded_from_pool']}.")
    a(f"  - Sobram {s['eligible_pool']} elegíveis, em ordem estrutural do Target Index.")
    a(f"  - Entraram os primeiros {s['batch_candidates']} (limite {s['limit']}).")
    a(f"- **HIGH restantes após o Batch02:** {s['high_remaining_after_batch02']}.")
    a(f"- **Fontes:** só oficiais (Planalto), verificadas em {B1.VERIFIED_ON}, com sha256 de cada página.")
    a('- **Decisão jurídica e rota de aparelho ficam separadas.**')
    a('')
    a('## Contabilidade')
    a('')
    a('| Decisão | n |')
    a('|---|---:|')
    for k in B1.DECISIONS:
        a(f"| {k} | {s['decisions'][k]} |")
    a(f"| **Total** | **{s['batch_candidates']}** |")
    a('')
    a('| Rota de aparelho dos aceitos (APPROVE + ADJUST) | n |')
    a('|---|---:|')
    for k, v in s['accepted_device_route'].items():
        a(f'| {k} | {v} |')
    a('')
    a(f"- **Natureza da relação:** reclassificada em {s['relation_type_changed']} aceitos.")
    a(f"- **Target:** ajustado em {s['target_changed']}.")
    a(f"- **NEW_CANDIDATE_BACKLOG:** {s['new_candidate_backlog']} sugestões, não decididas.")
    a('')
    a('## Decisões')
    a('')
    a('| # | Target | Norma | Decisão | Natureza final | Target final | Rota | Aparelho |')
    a('|---:|---|---|---|---|---|---|---|')
    for i, d in enumerate(dec, 1):
        tf = d['target_final'] if d['target_final'] and d['target_final'] != d['target'] else ('=' if d['target_final'] else '—')
        a(f"| {i} | {d['display_target']} | {d['norm_name']} | **{d['legal_decision']}** | {d['relation_type_final'] or '—'} | {tf} | {d['route'] or '—'} | "
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
    a('## NEW_CANDIDATE_BACKLOG (não decidido; exige rodada própria)')
    a('')
    for b in NEW_CANDIDATE_BACKLOG:
        a(f"- {b['norm']} × `{b['target_id']}` (origem `{b['origin']}`)")
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('C1B_BATCH02_NOT_DETERMINISTIC')
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
