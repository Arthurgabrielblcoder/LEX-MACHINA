# -*- coding: utf-8 -*-
"""REFERENCE_EXPANSION_CANDIDATES.json + REFERENCE_EXPANSION_REVIEW.md + REFERENCE_EXPANSION_PLAN_CF88.md (read-only for every corpus).

Editorial proposals only: status PENDING_HUMAN_REVIEW. Nothing here enters run1/run2, the catalog or the registry.
SOURCE = EXISTING_CATALOG (work already in the 69-work registry: EXISTING_WORK_REUSE) or NEW_CANDIDATE (NEW_WORK_CANDIDATE; when
the work already appears in the non-integrated 199-work candidate catalog, its candidate id is recorded).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REG = {o['id']: o for o in json.loads((ROOT / 'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json').read_text(encoding='utf-8'))['obras']}
IDX = {t['target_id']: t for t in json.loads((ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets']}
MAPPED = {l.split('|')[2] for l in (ROOT / 'DEVICE_INTEGRATION/staging_sd_v1/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX').read_text(encoding='utf-8').splitlines()
          if l and l[0] != '#'}
S = json.loads((HERE / 'REFERENCE_COVERAGE_AUDIT_SUMMARY.json').read_text(encoding='utf-8'))


def P(target, work, obra, tipo, ano, conexao, por_que, alcance, score, score_just, confidence, cand=None, limites=None, priority=False):
    src = 'EXISTING_CATALOG' if work in REG else 'NEW_CANDIDATE'
    if src == 'EXISTING_CATALOG':
        assert REG[work]['titulo'] == obra and REG[work]['tipo'] == tipo, work
    assert target in IDX, target
    disp = target if target in MAPPED else (target[:-len(':CAPUT')] if target.endswith(':CAPUT') and target[:-len(':CAPUT')] in MAPPED else None)
    return dict(target_id=target, target_kind=IDX[target]['kind'], work_id=work if src == 'EXISTING_CATALOG' else None, obra=obra, tipo=tipo, ano=ano,
                source=src, work_status='EXISTING_WORK_REUSE' if src == 'EXISTING_CATALOG' else 'NEW_WORK_CANDIDATE',
                candidate_catalog_id=cand, conexao_juridica=conexao, por_que_esta_aqui=por_que, alcance_neste_dispositivo=alcance,
                limites_de_transposicao=limites, score_proposto=score, score_justificativa=score_just, confidence=confidence,
                priority_article=priority, device_display_target=disp, device_layer4_after_ingestion='YES' if disp else 'NO (target fora do TEXT_MAP)',
                status='PENDING_HUMAN_REVIEW')


PRIORITY = [
    P('CF88:ART.37:CAPUT', 'EXP-LIV-002', 'Os Donos do Poder', 'LIVRO', 1958,
      'Princípios da impessoalidade e da moralidade administrativa (art. 37, caput).',
      'Faoro descreve o patrimonialismo: o Estado tratado como extensão dos interesses de um estamento que o controla. O caput do art. 37 é a resposta normativa a isso: a administração deve agir para todos, sem favorecimentos pessoais.',
      'Ajuda a compreender por que impessoalidade e moralidade são princípios expressos: o leitor visualiza o problema histórico (confusão entre público e privado) que eles combatem. Não explica o regime jurídico de cada princípio nem a legalidade, a publicidade e a eficiência.',
      8.6, 'Conexão central e duradoura com o caput; obra clássica do pensamento brasileiro. Não chega a 9 porque é ensaio histórico-sociológico denso, não ilustração direta.', 'HIGH', priority=True),
    P('CF88:ART.37:CAPUT', 'EXP-LIV-001', 'Raízes do Brasil', 'LIVRO', 1936,
      'Impessoalidade administrativa (art. 37, caput).',
      'Sérgio Buarque descreve o "homem cordial" e a dificuldade de separar relações pessoais e função pública. A impessoalidade do art. 37 exige justamente essa separação.',
      'Facilita lembrar o sentido da impessoalidade (agir pelo cargo, não por afeto ou parentesco). Não aborda os demais princípios nem as regras de concurso, nepotismo ou improbidade.',
      8.0, 'Boa ponte didática com a impessoalidade; segunda obra do mesmo target, com alcance mais estreito que Os Donos do Poder.', 'HIGH',
      limites='A expressão "homem cordial" costuma ser mal lida como "gentil"; a ficha deve evitar esse equívoco.', priority=True),
    P('CF88:ART.43:CAPUT', 'EXP-LIV-003', 'Formação Econômica do Brasil', 'LIVRO', 1959,
      'Regiões de desenvolvimento e redução das desigualdades regionais (art. 43, caput).',
      'Furtado explica a formação histórica das desigualdades entre as regiões brasileiras. O art. 43 autoriza a União a articular sua ação em complexos regionais para reduzir essas desigualdades.',
      'Ajuda a compreender o problema que o art. 43 enfrenta e por que a Constituição trata região como unidade de planejamento. Não descreve os instrumentos do § 2º nem a organização dos órgãos regionais.',
      8.6, 'Vínculo direto entre o diagnóstico da obra e a finalidade do dispositivo; autor clássico do desenvolvimento regional.', 'HIGH', priority=True),
    P('CF88:ART.43:PAR.2:INC.IV', None, 'Vidas Secas', 'LIVRO', 1938,
      'Prioridade ao aproveitamento de rios e massas de água represadas nas regiões de baixa renda sujeitas a secas periódicas (art. 43, § 2º, IV).',
      'O romance acompanha uma família de retirantes expulsa pela seca do sertão. O inciso IV escolhe exatamente esse cenário como prioridade de incentivo regional.',
      'Facilita visualizar e lembrar o que são "regiões de baixa renda sujeitas a secas periódicas" e por que o aproveitamento da água é prioridade. Não trata dos demais incentivos regionais.',
      8.4, 'Imagem literária forte e precisa do cenário descrito no inciso; obra clássica brasileira.', 'HIGH', cand='CAND200-200 (EXP2-LIV-040, APTA_COM_RESSALVA)', priority=True),
    P('CF88:ART.62:CAPUT', 'EXP-JOG-002', 'Suzerain', 'JOGO', 2020,
      'Ato normativo de urgência do chefe do Executivo e controle pelo Legislativo (art. 62, medida provisória).',
      'O jogador governa como presidente de um país fictício e precisa negociar reformas com o parlamento e os tribunais, sentindo o conflito entre agir rápido e obter aprovação legislativa.',
      'Pode ajudar a problematizar a tensão que o art. 62 regula (urgência do Executivo x controle do Congresso). Não reproduz o rito brasileiro da medida provisória: prazos, trancamento de pauta, vedações materiais e conversão em lei.',
      6.8, 'Conexão real, mas indireta: o jogo trata da relação Executivo-Legislativo em geral. Abaixo de 7 por exigir confirmação da mecânica específica de decretos do jogo antes da aprovação.', 'MEDIUM',
      limites='Sistema político fictício; verificar a mecânica de decretos no jogo antes de aprovar.', priority=True),
    P('CF88:ART.201:INC.I', 'EXP-FIL-006', 'Eu, Daniel Blake', 'FILME', 2016,
      'Cobertura previdenciária dos eventos de incapacidade temporária ou permanente para o trabalho (art. 201, I).',
      'Daniel, impedido de trabalhar após um infarto, enfrenta a perícia e a burocracia para obter o benefício por incapacidade. O inciso I põe a incapacidade para o trabalho entre os riscos cobertos pela previdência.',
      'Ajuda a visualizar o que é o risco social "incapacidade para o trabalho" e por que a previdência existe para cobri-lo. Não demonstra os requisitos do RGPS brasileiro (carência, qualidade de segurado, perícia do INSS).',
      8.4, 'O tema central do filme é exatamente o evento coberto pelo inciso; a obra já é aprovada no acervo para os arts. 6, 170 e 194.', 'HIGH',
      limites='Sistema britânico de benefícios; não equivale ao RGPS.', priority=True),
]

EXTRA = [
    P('CF88:ART.86:CAPUT', 'EXP-DOC-006', 'Excelentíssimos', 'DOCUMENTÁRIO', 2018,
      'Processo por crime de responsabilidade do Presidente: admissão pela Câmara por dois terços e julgamento pelo Senado (art. 86).',
      'O documentário acompanha a Câmara dos Deputados durante o processo de impeachment de 2015–2016, mostrando votação, articulação e discursos.',
      'Ajuda a visualizar a etapa de admissão na Câmara. Não explica o julgamento pelo Senado em detalhe nem o regime dos crimes comuns.',
      7.6, 'Registro documental do procedimento real do art. 86 no Brasil; perde pontos por perspectiva autoral sobre evento politicamente sensível.', 'HIGH',
      limites='Evento politicamente sensível; a ficha deve tratar só do procedimento constitucional.'),
    P('CF88:ART.52:INC.I', 'EXP-DOC-005', 'O Processo', 'DOCUMENTÁRIO', 2018,
      'Competência privativa do Senado para processar e julgar o Presidente nos crimes de responsabilidade (art. 52, I).',
      'O filme acompanha a defesa no processo de impeachment de 2016, incluindo a fase de julgamento no Senado.',
      'Ajuda a visualizar o Senado funcionando como órgão julgador. Não demonstra o quórum e o rito completo previstos no parágrafo único.',
      7.4, 'Mostra a fase senatorial do procedimento; perspectiva declaradamente da defesa reduz o score.', 'MEDIUM',
      limites='Perspectiva de uma das partes; evitar leitura de mérito político.'),
    P('CF88:ART.58:PAR.3', None, 'Tropa de Elite 2: O Inimigo Agora É Outro', 'FILME', 2010,
      'Comissões parlamentares de inquérito: poderes de investigação e encaminhamento das conclusões ao Ministério Público (art. 58, § 3º).',
      'Na trama, uma CPI da Assembleia Legislativa investiga milícias ligadas a agentes públicos e políticos.',
      'Facilita lembrar o que uma CPI faz (investigar fato determinado e remeter conclusões ao Ministério Público). A CPI do filme é estadual e ficcionalizada; não mostra os limites jurídicos (reserva de jurisdição).',
      7.6, 'A CPI é elemento narrativo central; obra brasileira de grande alcance. Ficção e CPI estadual limitam a nota.', 'MEDIUM',
      cand='CAND200-089 (EXP2-FIL-039, APTA_COM_RESSALVA)', limites='CPI estadual em obra de ficção; violência explícita.'),
    P('CF88:ART.76', 'EXP-SER-001', 'Borgen', 'SÉRIE', 2010,
      'Sistema presidencialista: o Executivo é exercido pelo Presidente, auxiliado pelos Ministros (art. 76).',
      'A série mostra uma primeira-ministra que depende de coalizão parlamentar para governar, isto é, um sistema parlamentarista.',
      'Serve para problematizar por contraste: no Brasil o chefe de governo é eleito diretamente e não depende de confiança do Parlamento. Não ilustra o presidencialismo brasileiro diretamente.',
      7.0, 'Vínculo por contraste, útil para memorização; nota moderada por não retratar o modelo do dispositivo.', 'MEDIUM',
      limites='Parlamentarismo dinamarquês; usar apenas como contraste.'),
    P('CF88:ART.134:CAPUT', None, 'Luta por Justiça (Just Mercy)', 'FILME', 2019,
      'Defensoria Pública: orientação jurídica e defesa dos necessitados (art. 134).',
      'O filme acompanha Bryan Stevenson defendendo gratuitamente condenados pobres, incluindo um homem inocente no corredor da morte.',
      'Ajuda a compreender por que a defesa técnica dos necessitados é função essencial à Justiça. A organização é privada e o sistema é norte-americano; não demonstra a estrutura da Defensoria brasileira.',
      7.8, 'Tema central da obra é a defesa dos necessitados; contexto estrangeiro limita a nota.', 'HIGH',
      cand='CAND200-056 (EXP2-FIL-006, APTA_COM_RESSALVA)', limites='Organização privada norte-americana, não Defensoria Pública.'),
    P('CF88:ART.142:CAPUT', 'EXP-FIL-003', 'Argentina, 1985', 'FILME', 2022,
      'Forças Armadas sob a autoridade suprema do Presidente e destinadas à defesa da Pátria e à garantia dos poderes constitucionais (art. 142).',
      'O filme reconstitui o julgamento civil dos chefes das juntas militares argentinas.',
      'Ajuda a problematizar a subordinação das Forças Armadas à ordem constitucional e ao poder civil. Não trata do regime jurídico dos militares brasileiros nem da GLO.',
      7.2, 'Conexão temática relevante, mas por contraste histórico estrangeiro.', 'MEDIUM', limites='Contexto argentino.'),
    P('CF88:ART.144:PAR.5', None, 'Tropa de Elite', 'FILME', 2007,
      'Polícia militar: polícia ostensiva e preservação da ordem pública (art. 144, § 5º).',
      'O filme acompanha o batalhão de operações especiais da Polícia Militar do Rio de Janeiro.',
      'Ajuda a visualizar o papel da polícia militar e a problematizar os limites constitucionais da atuação policial. Não ensina a repartição de competências das demais polícias.',
      7.4, 'Obra brasileira central sobre polícia militar; a abordagem violenta e controversa exige cuidado editorial.', 'MEDIUM',
      cand='CAND200-088 (EXP2-FIL-038, APTA_COM_RESSALVA)', limites='Retrata tortura e violência policial sem endossá-las juridicamente; a ficha deve deixar isso claro.'),
    P('CF88:ART.144:PAR.7', 'EXP-SER-002', 'A Escuta', 'SÉRIE', 2002,
      'Organização e funcionamento dos órgãos de segurança pública para garantir a eficiência de suas atividades (art. 144, § 7º).',
      'A série mostra como metas, estatísticas e disputas internas distorcem o trabalho policial em Baltimore.',
      'Ajuda a problematizar o que significa eficiência na segurança pública. Sistema estrangeiro; não descreve a lei brasileira que organiza o setor.',
      7.2, 'Retrato institucional profundo, mas norte-americano e indireto quanto ao texto do § 7º.', 'MEDIUM', limites='Contexto norte-americano.'),
    P('CF88:ART.145:PAR.1', 'EXP-LIV-009', 'O Triunfo da Injustiça', 'LIVRO', 2019,
      'Capacidade contributiva: impostos graduados segundo a capacidade econômica do contribuinte (art. 145, § 1º).',
      'Saez e Zucman mostram que, nos Estados Unidos, os mais ricos chegaram a pagar alíquota efetiva menor que a da média da população.',
      'Ajuda a compreender e problematizar a capacidade contributiva e a progressividade. Dados norte-americanos; não descreve os tributos brasileiros.',
      8.2, 'Tema central da obra coincide com o princípio do § 1º; obra já aprovada no acervo (arts. 170 e 193).', 'HIGH', limites='Dados dos EUA.'),
    P('CF88:ART.182:CAPUT', 'EXP-DOC-010', 'Citizen Jane: Battle for the City', 'DOCUMENTÁRIO', 2016,
      'Política de desenvolvimento urbano: funções sociais da cidade e bem-estar dos habitantes (art. 182).',
      'O documentário mostra Jane Jacobs enfrentando projetos viários que destruiriam bairros de Nova York.',
      'Ajuda a compreender o que são as "funções sociais da cidade" e a participação dos moradores no planejamento. Não trata do plano diretor nem dos instrumentos do Estatuto da Cidade.',
      8.2, 'Debate urbanístico central da obra coincide com a finalidade do art. 182.', 'HIGH', limites='Contexto norte-americano.'),
    P('CF88:ART.182:PAR.1', 'EXP-JOG-004', 'Cities: Skylines', 'JOGO', 2015,
      'Plano diretor como instrumento básico da política urbana (art. 182, § 1º).',
      'O jogador planeja uma cidade inteira: zoneamento, transporte, serviços e expansão.',
      'Facilita visualizar o que um plano urbano organiza. Não reproduz exigências jurídicas (obrigatoriedade para cidades com mais de 20 mil habitantes, aprovação pela Câmara).',
      7.6, 'Mecânica central do jogo é planejamento urbano; sem dimensão jurídica própria.', 'HIGH'),
    P('CF88:ART.184:CAPUT', 'EXP-DOC-008', 'Cabra Marcado para Morrer', 'DOCUMENTÁRIO', 1984,
      'Desapropriação para fins de reforma agrária do imóvel rural que não cumpre sua função social (art. 184).',
      'O filme retoma a história de João Pedro Teixeira, líder das Ligas Camponesas, e da luta por terra no Nordeste antes e depois de 1964.',
      'Ajuda a compreender a origem histórica da reforma agrária como tema constitucional. Não explica o procedimento de desapropriação nem a indenização em títulos.',
      7.8, 'Obra brasileira fundamental sobre a questão agrária; o vínculo é histórico, não procedimental.', 'HIGH'),
    P('CF88:ART.192', 'EXP-FIL-007', 'A Grande Aposta', 'FILME', 2015,
      'Sistema financeiro nacional estruturado para promover o desenvolvimento equilibrado e servir aos interesses da coletividade (art. 192).',
      'O filme mostra como produtos financeiros de risco levaram à crise de 2008 e prejudicaram milhões de pessoas.',
      'Ajuda a problematizar por que o sistema financeiro deve servir à coletividade e ser regulado. Contexto norte-americano; não descreve o Banco Central nem as leis complementares do setor.',
      7.8, 'Ilustra com clareza o risco que justifica o art. 192; contexto estrangeiro limita a nota.', 'HIGH', limites='Mercado norte-americano.'),
    P('CF88:ART.196', None, 'SOS Saúde (Sicko)', 'DOCUMENTÁRIO', 2007,
      'Saúde como direito de todos e dever do Estado, com acesso universal e igualitário (art. 196).',
      'Michael Moore compara o sistema de saúde baseado em seguros privados dos Estados Unidos com sistemas universais.',
      'Ajuda a compreender por contraste o que significa acesso universal e igualitário. Documentário opinativo; não descreve o SUS.',
      7.4, 'Contraste forte e memorável com o art. 196; tom opinativo reduz a nota.', 'MEDIUM', limites='Documentário de autor, opinativo.'),
    P('CF88:ART.206:INC.I', None, 'Pro Dia Nascer Feliz', 'DOCUMENTÁRIO', 2006,
      'Igualdade de condições para o acesso e permanência na escola (art. 206, I).',
      'O documentário acompanha estudantes de escolas públicas e privadas em diferentes estados brasileiros.',
      'Ajuda a visualizar a desigualdade de condições que o inciso I quer enfrentar. Não trata dos demais princípios do ensino.',
      8.0, 'Retrato brasileiro direto do problema do inciso.', 'HIGH'),
    P('CF88:ART.215:PAR.1', 'EXP-JOG-006', 'Never Alone (Kisima Inŋitchuŋa)', 'JOGO', 2014,
      'Proteção das manifestações das culturas populares e indígenas (art. 215, § 1º).',
      'O jogo foi criado com a comunidade Iñupiat e transmite suas histórias tradicionais.',
      'Ajuda a compreender o que é proteger manifestação cultural de um povo indígena. Contexto do Alasca; não trata de políticas culturais brasileiras.',
      7.4, 'Conexão cultural autêntica (coautoria comunitária); contexto estrangeiro.', 'MEDIUM', limites='Povo indígena do Alasca, não brasileiro.'),
    P('CF88:ART.231:CAPUT', 'EXP-DOC-007', 'Martírio', 'DOCUMENTÁRIO', 2016,
      'Direitos originários dos índios sobre as terras que tradicionalmente ocupam e dever da União de demarcá-las (art. 231).',
      'O documentário acompanha a luta dos Guarani-Kaiowá pela retomada de terras tradicionais no Mato Grosso do Sul.',
      'Ajuda a compreender o que são terras tradicionalmente ocupadas e por que a demarcação é central. Não trata do regime jurídico detalhado da demarcação.',
      8.6, 'Obra brasileira diretamente sobre o objeto do dispositivo.', 'HIGH'),
    P('ADCT:ART.68', 'EXP-LIV-005', 'Torto Arado', 'LIVRO', 2019,
      'Propriedade definitiva das terras ocupadas por remanescentes das comunidades dos quilombos (ADCT, art. 68).',
      'O romance narra a vida de descendentes de escravizados que trabalham em uma fazenda na Bahia e lutam pela terra onde vivem.',
      'Ajuda a compreender o sentido de reconhecer a terra das comunidades quilombolas. É ficção; não descreve o procedimento de titulação.',
      8.4, 'Romance brasileiro diretamente ligado ao tema do artigo; primeira obra do ADCT.', 'HIGH'),
    P('CF88:ART.7:INC.XXXIII', 'EXP-JOG-003', 'Frostpunk', 'JOGO', 2018,
      'Proibição de trabalho noturno, perigoso ou insalubre a menores de dezoito anos e de qualquer trabalho a menores de dezesseis, salvo aprendiz (art. 7º, XXXIII).',
      'Em uma cidade em crise, o jogador pode aprovar uma lei que coloca crianças para trabalhar e sente as consequências da escolha.',
      'Ajuda a problematizar por que a Constituição proíbe o trabalho infantil, mesmo em situações de crise. Mundo fictício; não demonstra o contrato de aprendizagem.',
      7.2, 'A escolha sobre trabalho infantil é mecânica explícita do jogo; contexto fictício.', 'MEDIUM', limites='Mundo fictício; ficha sem mecânica de jogo detalhada.'),
]

REJECTED = [
    dict(article='CF88:ART.98', reason='Nenhuma obra do registry ou do catálogo candidato trata de juizados especiais ou justiça de paz com conexão real. Lacuna mantida (CONFIRMED_REFERENCE_GAP).'),
    dict(article='CF88:ART.202', reason='Nenhuma obra adequada sobre previdência complementar privada. Inside Job (catálogo candidato) trata da crise financeira em geral; a conexão seria forçada. Lacuna mantida.'),
    dict(article='CF88:ART.193', reason='Já possui 3 obras no caput (Capital no Século XXI, Desigualdade para Todos, O Triunfo da Injustiça), adequadas ao primado do trabalho e à justiça social. Sem proposta; a ausência no aparelho deve ser retestada (provável seleção de CONTEXTO).'),
    dict(article='O Mecanismo (EXP-SER-004)', reason='Rejeitada para o art. 37, § 4º: dramatização controversa e com imprecisões de investigação real.'),
    dict(article='Democracy 4 (EXP-JOG-001) / O Mito do Déficit (EXP-LIV-007)', reason='Rejeitadas para orçamento (arts. 165 a 167): a conexão seria "a obra fala de dinheiro, então serve para orçamento".'),
    dict(article='Democracia em Vertigem (REF-DOC-0003)', reason='Não proposta: redundante com Excelentíssimos e O Processo para o mesmo procedimento.'),
]

allp = PRIORITY + EXTRA
assert len({(p['target_id'], p['obra']) for p in allp}) == len(allp)
doc = dict(schema_version=1, status='PENDING_HUMAN_REVIEW', as_of='2026-10-01', scope='CF88 + ADCT', layer='4 REFERENCIAS (WORK_REFERENCE)',
           policy='Propostas editoriais; nenhuma entra no run1/run2, no catálogo canônico ou no registry sem revisão humana e ingestão própria. Qualidade > quantidade.',
           score_scale='0 a 10, mesma escala do score_editorial do RC2 (atual: mínimo 3,8, mediana 8,3, máximo 9,2)',
           counts=dict(priority=len(PRIORITY), additional=len(EXTRA), total=len(allp),
                       existing_work_reuse=sum(1 for p in allp if p['source'] == 'EXISTING_CATALOG'), new_work_candidate=sum(1 for p in allp if p['source'] == 'NEW_CANDIDATE'),
                       high=sum(1 for p in allp if p['confidence'] == 'HIGH'), medium=sum(1 for p in allp if p['confidence'] == 'MEDIUM')),
           priority_articles={'CF88:ART.37': 'ZERO_COVERAGE → 2 propostas', 'CF88:ART.43': 'ZERO_COVERAGE → 2 propostas', 'CF88:ART.62': 'ZERO_COVERAGE → 1 proposta (MEDIUM)',
                              'CF88:ART.98': 'ZERO_COVERAGE → nenhuma obra adequada', 'CF88:ART.193': 'COVERED (3 obras no caput) → sem proposta',
                              'CF88:ART.201': 'ZERO_COVERAGE → 1 proposta', 'CF88:ART.202': 'ZERO_COVERAGE → nenhuma obra adequada'},
           priority=PRIORITY, additional=EXTRA, not_proposed=REJECTED)
(HERE / 'REFERENCE_EXPANSION_CANDIDATES.json').write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def card(p, i):
    return [f"### {i}. `{p['target_id']}` — {p['obra']} ({p['tipo']}, {p['ano']})", '',
            f"- **SOURCE:** {p['source']} · {p['work_status']}" + (f" · `{p['work_id']}`" if p['work_id'] else '') +
            (f" · catálogo candidato {p['candidate_catalog_id']}" if p['candidate_catalog_id'] else ''),
            f"- **CONEXÃO JURÍDICA:** {p['conexao_juridica']}", f"- **POR QUE ESTÁ AQUI:** {p['por_que_esta_aqui']}",
            f"- **ALCANCE NESTE DISPOSITIVO:** {p['alcance_neste_dispositivo']}"] + \
           ([f"- **LIMITES:** {p['limites_de_transposicao']}"] if p['limites_de_transposicao'] else []) + \
           [f"- **SCORE PROPOSTO:** {p['score_proposto']} — {p['score_justificativa']}", f"- **CONFIDENCE:** {p['confidence']}",
            f"- **DEVICE (após ingestão):** botão 4 em `{p['device_display_target']}`", '', '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR', '']


R = ['# REFERÊNCIAS — candidatos de expansão (PENDING_HUMAN_REVIEW)', '',
     f"{doc['counts']['total']} propostas ({doc['counts']['priority']} prioritárias + {doc['counts']['additional']} adicionais); "
     f"{doc['counts']['existing_work_reuse']} reutilizam obras do registry e {doc['counts']['new_work_candidate']} são obras novas (NEW_WORK_CANDIDATE). "
     f"Confiança: HIGH {doc['counts']['high']}, MEDIUM {doc['counts']['medium']}. Nenhuma entrou no run2.", '',
     'O limite era de até 50 vínculos adicionais. Foram propostos só os que ajudam de verdade a compreender, lembrar, problematizar ou visualizar o dispositivo.', '',
     '## Artigos prioritários (verificação física de Arthur)', '']
for i, p in enumerate(PRIORITY, 1):
    R += card(p, i)
R += ['## Candidatos adicionais (maiores vazios)', '']
for i, p in enumerate(EXTRA, len(PRIORITY) + 1):
    R += card(p, i)
R += ['## Não propostos', ''] + [f"- **{x['article']}:** {x['reason']}" for x in REJECTED]
(HERE / 'REFERENCE_EXPANSION_REVIEW.md').write_bytes(('\n'.join(R) + '\n').encode('utf-8'))

gaps = S['largest_gaps']
blocks = S['blocks']
PL = ['# Plano de expansão da camada 4 REFERÊNCIAS — CF88', '',
      '**Objetivo:** corrigir os grandes vazios sem forçar uma referência em todo artigo. Status: **PENDING_HUMAN_REVIEW**; nada foi inserido no corpus.', '',
      '## Ponto de partida (auditoria de 2026-10-01)', '',
      f"- {S['work_reference_links']} vínculos WORK_REFERENCE em {S['distinct_targets_with_work']} targets e {S['distinct_articles_with_work_cf']} artigos da CF "
      f"({S['cf_article_coverage_pct']}% dos {S['cf_articles_existing']} artigos estruturais); ADCT sem nenhuma obra.",
      f"- Maior vazio: {gaps[0]['first']} a {gaps[0]['last']} ({gaps[0]['count']} artigos consecutivos sem obra), cobrindo Organização do Estado (a partir do art. 24), "
      'Organização dos Poderes, Defesa do Estado e Tributação e Orçamento.',
      f"- Registry: {S['registry']['works']} obras, {S['registry']['unused']} sem uso na CF; catálogo de expansão com {S['candidate_catalog']['works']} obras ainda não integradas.", '',
      '## Prioridades', '',
      '1. Dispositivos constitucionalmente importantes (art. 37; separação de Poderes; tributação; ordem social).',
      '2. Artigos de grande utilidade didática.',
      '3. Temas em que uma obra realmente facilita compreender, lembrar, problematizar ou visualizar.',
      '4. Partes quase sem cobertura (blocos com 0%: Organização dos Poderes, Defesa do Estado, Tributação e Orçamento, Disposições Gerais, ADCT).',
      '5. Artigos testados por Arthur e confirmados vazios (37, 43, 62, 98, 201, 202).', '',
      '## Efeito das propostas se aprovadas', '',
      f"- Prioritárias: arts. 37, 43, 62 e 201 deixam de ser lacuna; 98 e 202 continuam lacuna por falta de obra adequada; 193 já tem obra (retestar no aparelho).",
      f"- Adicionais: {len(EXTRA)} vínculos em blocos hoje vazios (Poderes, Defesa do Estado, Tributação, Ordem Econômica, Ordem Social, ADCT).",
      '- Total: ' + str(len(allp)) + ' vínculos propostos; ' + str(len({p['target_id'].split(':')[0] + ':' + p['target_id'].split(':')[1] for p in allp})) + ' artigos distintos.', '',
      '## Regras de qualidade aplicadas', '',
      '- Rejeitadas conexões genéricas ("a obra tem governo, então serve para Administração Pública"; "fala de dinheiro, então serve para orçamento").',
      '- Score na mesma escala do RC2, com justificativa; nenhuma nota alta para preencher lacuna.',
      '- Obras fora do registry ficam como NEW_WORK_CANDIDATE e exigem ingestão própria (identidade, evidências, ficha) antes de qualquer vínculo.',
      '- Sistemas estrangeiros e ficção sempre com limites de transposição explícitos.', '',
      '## Próximos passos (fora desta missão)', '',
      '1. Revisão humana de `REFERENCE_EXPANSION_REVIEW.md`.',
      '2. Ingestão das obras novas aprovadas no registry (pipeline do catálogo).',
      '3. Geração dos vínculos aprovados pelo pipeline editorial atual e novo export (run3), com regressão contra o run2.',
      '4. Reteste físico do art. 193 com `CONTEXTO: ART. 193` no rodapé.']
(HERE / 'REFERENCE_EXPANSION_PLAN_CF88.md').write_bytes(('\n'.join(PL) + '\n').encode('utf-8'))
print(json.dumps(doc['counts']))
