from editorial import *
facts='''26|M|O jogador governa entre 1836 e 1936, reforma instituições, tributa lucros e administra indústria, comércio e interesses de grupos populacionais.|tributação;trabalho;economia
27|M|O jogador controla uma nação durante quatro séculos e administra território, riqueza, diplomacia e conflitos religiosos.|relações internacionais;território
28|M|O jogador organiza produção industrial, alianças diplomáticas e estratégias militares de países na Segunda Guerra Mundial, incluindo caminhos históricos alternativos.|guerra;indústria
29|M|O jogador expande assentamentos, desenvolve tecnologia e escolhe entre cooperação e conquista ao conduzir civilizações por diferentes eras.|território;cooperação internacional
30|M|O jogador disputa cargos políticos, redige legislação e equilibra orçamentos durante uma carreira política simulada.|eleições;orçamento;processo legislativo
31|M|O jogador atua em diferentes sistemas eleitorais, aprova ou rejeita projetos e governa um país simulado.|eleições;processo legislativo
32|M|Em uma Grã-Bretanha alternativa, o jogador trabalha como segurança por aplicativo, verifica documentos e listas de convidados.|trabalho;documentação;migração
33|N|Após uma prisão por agentes migratórios, amigos precisam atravessar os Estados Unidos e recuperar documentos de identificação.|migração;documentação
34|M|O jogador decide quais notícias publicar; suas escolhas alteram relações sociais, sua carreira e os desfechos.|imprensa;informação
35|M|O jogador observa pessoas por câmeras de vigilância e acessa momentos privados, sob a regra de não interagir com elas.|privacidade;vigilância
36|M|O jogador pesquisa conversas em vídeo gravadas secretamente para reconstruir uma história que envolve quatro vidas privadas.|privacidade;prova
37|M|O jogador consulta um banco de vídeos de sete entrevistas policiais de uma mulher e cruza informações entre os registros.|prova;investigação
38|M|Um investigador de seguros embarca em um navio que reapareceu sem tripulação para avaliar danos por exploração e dedução.|seguros;prova;responsabilidade
39|M|O jogador reúne pistas sobre doze mortes, formula hipóteses e identifica suspeitos e motivos.|prova;investigação
40|N|Andreas Maler se envolve em homicídios, escândalos e intrigas nos Alpes bávaros durante mudanças religiosas e políticas.|investigação;conflitos religiosos
41|N|A sinopse apresenta a aventura de Henry na Europa medieval do século XV.|história
42|M|O administrador de uma cidade distribui recursos e calor e negocia interesses de facções representadas em um conselho.|orçamento;recursos;participação política
43|M|O jogador atua como autoridade que aplica leis em um território conquistado por um déspota e pode sustentar ou desafiar a ordem imposta.|jurisdição;ocupação
44|M|O chefe de polícia administra agentes, atende emergências e reúne provas, sob pressão da prefeitura e de organizações criminosas.|administração pública;polícia;corrupção
45|M|O jogador organiza documentos de investigação policial e emite conclusões sobre oito casos que vão de furto a homicídio.|prova;investigação;decisão institucional
46|M|O guarda de fronteira verifica documentos, recusa entradas com inconsistências e inspeciona veículos para localizar contrabando.|migração;fiscalização;contrabando
47|M|O jogador analisa visões de mundo dos cidadãos, realiza diagnósticos e opera aparelhos de tratamento em uma metrópole distópica.|saúde mental;autonomia
48|N|Uma corporação anuncia um sistema para eliminar emoções negativas; um bartender e um hacker tentam impedir o programa por considerá-lo manipulação mental.|autonomia;tecnologia
49|M|Um jornalista reúne evidências em áreas restritas e entrevista pessoas enquanto o tempo da investigação corre continuamente.|imprensa;investigação
50|N|O jogador acompanha Reza, aspirante a fotojornalista, e toma decisões durante a revolução iraniana no final dos anos 1970.|imprensa;conflito político'''
rows=[]
for line in facts.splitlines():
 n,ct,fact,areas=line.split('|');n=int(n);s=load(ROOT/'03_FONTES'/f'STEAM_{n:03}.json');year=int(re.search(r'\d{4}',s['release_date']['date']).group())
 rows.append(dict(number=n,ano=year,criador_principal=s['developers'],publisher_distribuidor_editora=s['publishers'],status_triagem='FONTE_EM_REVISAO' if n==41 else 'APTA_COM_RESSALVA',motivo='Identidade consultada; descrição disponível insuficiente para delimitar evidência central. Solicitar press kit/manual antes de aproveitamento.' if n==41 else 'Prática ou evento central documentado; simulação não equivale a regime jurídico real.',fontes=[dict(url=s['source_url'],tier='A',accessed_on='2026-09-26',locator='About this game / ficha do produto',supports=['identidade','fato_central'],paraphrase=fact)],facts=[dict(text=fact,content_type='MECANICA_INTERATIVA' if ct=='M' else 'EVENTO_NARRATIVO')],areas_potenciais=areas.split(';'),objetos_juridicos_potenciais=areas.split(';'),riscos=['Abstração, ficção ou reconstrução histórica; recursos variam conforme versão e escolhas.'],transposition_limits=['Não equiparar a simulação a normas ou procedimentos brasileiros.','A descrição oficial prova a possibilidade mecânica, não a ocorrência em toda partida.']))
process(2,rows)
