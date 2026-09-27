from editorial import *
facts='''1|M|O jogador atua como detetive, interroga personagens, investiga homicídios e pode aceitar subornos.|investigação;corrupção
2|M|O jogador assume a defesa de clientes em quatorze episódios dos três primeiros jogos da série.|defesa;prova
3|M|O jogador examina pistas, entrevista e interroga testemunhas e apresenta provas em julgamentos ambientados no Japão e na Inglaterra do século XIX.|defesa;prova
4|M|Na função do promotor Miles Edgeworth, o jogador examina locais de crime, reúne pistas e conversa com pessoas para solucionar casos.|investigação;prova
5|N|O detetive Cole Phelps investiga incêndios criminosos, conspirações e homicídios, enfrentando também integrantes do próprio departamento.|investigação;polícia
6|N|Androides conscientes buscam emancipação em uma narrativa ramificada pelas escolhas do jogador.|inteligência artificial;discriminação
7|N|Adam Jensen protege uma empresa de biotecnologia; aprimoramentos mecânicos dividem a sociedade entre quem pode e quem não pode pagá-los.|biotecnologia;desigualdade
8|N|Adam Jensen trabalha como agente clandestino em uma sociedade hostil a humanos com aprimoramentos.|discriminação;biotecnologia
9|N|A aventura ocorre em Night City, metrópole marcada pela disputa de poder e pela modificação constante dos corpos.|personalidade;biotecnologia
10|N|Arthur Morgan e seu grupo fogem de agentes federais e caçadores de recompensas, recorrendo a roubos e confrontos.|polícia;criminalidade
11|N|O taxista Tommy Angelo ingressa na família Salieri após um encontro com o crime organizado.|criminalidade;organizações criminosas
12|N|Lincoln Clay organiza uma nova rede de aliados para se vingar da máfia que matou sua família substituta.|criminalidade;violência
13|M|O jogador conduz um esquadrão em uma Dubai ficcional devastada pela guerra e por tempestades de areia.|guerra;decisões militares
14|N|A apresentação oficial situa o tema na transmissão de memórias e modos de vida às gerações futuras em um mundo digitalizado.|informação;tecnologia
15|N|Em 1984, Snake forma um novo exército privado e retorna ao combate por vingança, em um cenário de Guerra Fria e crise nuclear.|guerra;forças privadas
16|M|O administrador designado pelo Estado instala escutas e invade apartamentos de inquilinos para reportar suspeitos de oposição.|privacidade;vigilância
17|M|Um funcionário do ministério pode espionar superiores, tramar contra colegas, cumprir tarefas burocráticas ou expor corrupção.|administração pública;corrupção
18|M|O jogador consulta informações da internet, comunicações pessoais e arquivos privados e transmite dados que afetam cidadãos investigados.|proteção de dados;investigação
19|M|Um funcionário de um programa estatal de vigilância pode descobrir e fabricar informações apresentadas como verdade.|informação;vigilância
20|M|O jogador seleciona imagens e anúncios e censura conteúdos de um telejornal, influenciando a percepção pública dos acontecimentos.|imprensa;publicidade
21|M|O jogador ocupa a editoria de um jornal e deve selecionar artigos favoráveis à imagem da nação fictícia de Republia.|imprensa;propaganda
22|M|O jogador preside casos como juiz do Tribunal Revolucionário de Paris, toma decisões e participa de intrigas políticas.|jurisdição;imparcialidade
23|N|O nascimento define a posição social no império fictício; as escolhas do protagonista podem levá-lo à magistratura, à inquisição ou à revolução.|estratificação social;instituições
24|M|O jogador recebe petições no trono e decide a quem destinar recursos limitados, negociando alianças entre governantes.|orçamento;administração
25|M|O jogador administra uma dinastia medieval, concede títulos e territórios e continua a partida por meio de herdeiros.|sucessões;propriedade'''
extra={2:(2014,'https://www.nintendo.com/en-gb/Games/Nintendo-3DS-download-software/Phoenix-Wright-Ace-Attorney-Trilogy-942989.html'),6:(2018,'https://www.quanticdream.com/en/our-story'),7:(2011,'https://blog.playstation.com/archive/2011/03/09/deus-ex-human-revolution-is-coming-on-26-august/'),10:(2018,'https://store.rockstargames.com/game/buy-red-dead-redemption-2?drm=PlayStation'),12:(2016,'https://support.2k.com/hc/en-us/articles/229711387-Mafia-III-FAQ'),14:(2001,'https://www.konami.com/mg/archive/mgs2/english/topic/topic_index.html')}
rows=[]
for line in facts.splitlines():
 n,ct,fact,areas=line.split('|');n=int(n);s=load(ROOT/'03_FONTES'/f'STEAM_{n:03}.json')
 if n in [13,21]:
  year,creator,publisher,url=(2012,['Yager'],['2K'],'https://www.2k.com/en-US/game/spec-ops-the-line/') if n==13 else (2012,['Lucas Pope'],['Lucas Pope'],'https://www.dukope.com/')
 else:year=int(re.search(r'\d{4}',s['release_date']['date']).group());creator=s['developers'];publisher=s['publishers'];url=s['source_url']
 sources=[dict(url=url,tier='A',accessed_on='2026-09-26',locator='Apresentação oficial / About this game',supports=['identidade','fato_central'],paraphrase=fact)]
 if n in extra:
  year,other=extra[n];sources.append(dict(url=other,tier='A',accessed_on='2026-09-26',locator='Data de lançamento original / histórico oficial',supports=['ano_original']))
 if n==7:sources.append(dict(url='https://www.eidosmontreal.com/games/deus-ex-human-revolution/',tier='A',supports=['fato_central'],paraphrase=fact))
 if n==14:sources.append(dict(url='https://www.konami.com/mg/archive/mgs2/english/intro/introduction.html',tier='A',supports=['fato_central'],paraphrase=fact))
 row=dict(number=n,ano=year,criador_principal=creator,publisher_distribuidor_editora=publisher,status_triagem='APTA_COM_RESSALVA',fontes=sources,facts=[dict(text=fact,content_type='MECANICA_INTERATIVA' if ct=='M' else 'EVENTO_NARRATIVO',source_index=len(sources)-1 if n in [6,7,14] else 0)],areas_potenciais=areas.split(';'),objetos_juridicos_potenciais=areas.split(';'),riscos=['Ficção, abstração interativa ou reconstrução histórica; decisões variam conforme a partida.'],transposition_limits=['Não equivale a procedimento ou instituição brasileira.','A mecânica documentada descreve possibilidades do jogo, sem afirmar que toda partida contém o mesmo evento.'])
 if n in [1,2,4,7,11,12,14]:row['nota_edicao']='Edição, remake ou coletânea identificada; não cria registros adicionais para remaster, tradução ou jogos contidos na coletânea. Ano da obra separado da edição de plataforma.'
 if n==9:row['status_triagem']='REJEITADA_EVIDENCIA_FRACA';row['motivo']='A descrição oficial consultada é ampla e promocional: disputa de poder e modificação corporal não delimitam uma prática institucional ou um fato suficientemente específico.'
 rows.append(row)
process(1,rows)
