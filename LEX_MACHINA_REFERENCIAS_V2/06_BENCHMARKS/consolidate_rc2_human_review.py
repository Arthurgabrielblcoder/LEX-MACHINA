"""Editorial publication only: immutable RC1 + explicit human decisions.

No import, execution or modification of any proof engine, ontology or pipeline.
Explanations and partial scopes are reference metadata, never new legal data.
"""
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
RC1=ROOT/'08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1'
RC2=ROOT/'08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED'
LEDGER=ROOT/'06_BENCHMARKS/REVISAO_HUMANA_RC1_FINAL_V1.json'
VERSION='REVISAO_HUMANA_RC1_FINAL_V1'
DATE='2026-09-26'
SOURCE=Path('C:/Users/arthu/.codex/attachments/f96c07cd-713a-4500-88de-ac0e938359f3/Texto colado.txt')
HOLDOUT_SHA='b71a87a8292ac621a209201e2082935813563f8002f9203430af3b781414adf1'


def serialized(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(serialized(x).encode('utf-8')).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def write(p,x):
    require(not p.exists(),'Refusing overwrite: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes((x if isinstance(x,str) else serialized(x)).encode('utf-8'))
def key(r):return r['device_id'],r['work_id']


# Explicit decisions keyed by IDs reconciled against the frozen RC1 titles.
REJECTS=[
 ('REF-LIV-0007','CF88:ART.170','Ensaio sobre a Cegueira','Privação pontual/distópica não sustenta ordem econômica/justiça social do caput.'),
 ('REF-LIV-0007','CF88:ART.3:INC.III','Ensaio sobre a Cegueira','Privação alimentar causada pela dinâmica do confinamento não representa pobreza/marginalização social constitucional.'),
 ('EXP-SER-006','CF88:ART.5:INC.XLII','Show Me a Hero','Discriminação racial é demonstrada, mas não a criminalização constitucional específica do racismo.'),
 ('REF-FIL-0004','CF88:ART.170','Filadélfia','Discriminação trabalhista individual não representa a ordem econômica constitucional em geral.'),
 ('REF-FIL-0004','CF88:ART.170:INC.VIII','Filadélfia','Acesso/manutenção de emprego individual não equivale à finalidade macroeconômica de busca do pleno emprego.'),
 ('REF-FIL-0004','CF88:ART.186:INC.III','Filadélfia','Relação trabalhista em escritório não possui âncora em propriedade rural/função social da propriedade rural.'),
 ('REF-FIL-0004','CF88:ART.193','Filadélfia','Problema individual de discriminação no trabalho não basta para representar primado do trabalho + bem-estar + justiça social.'),
 ('EXP-FIL-006','CF88:ART.196','Eu, Daniel Blake','O enredo documentado trata de benefício por incapacidade; não há recusa/negação de acesso a serviço de saúde.'),
 ('REF-FIL-0004','CF88:ART.1:INC.IV','Filadélfia','Problema individual de discriminação laboral não basta para representar o fundamento constitucional dos valores sociais do trabalho e da livre iniciativa.'),
 ('REF-FIL-0006','CF88:ART.220:PAR.1','The Post: A Guerra Secreta','Tentativa de repressão jornalística não demonstra especificamente o mecanismo normativo “lei contendo dispositivo que embarace informação jornalística”.'),
 ('REF-FIL-0002','CF88:ART.5:INC.IX','V de Vingança','Evidência demonstra manifestação política/dissenso; não prova especificamente atividade intelectual, artística, científica ou de comunicação.'),
 ('REF-SER-0001','CF88:ART.5:INC.LV','Olhos que Condenam','Coação/confissão e injustiça processual não demonstram especificamente contraditório e ampla defesa.'),
 ('REF-LIV-0003','CF88:ART.5:INC.LVII','O Sol É para Todos','Condenação injusta de inocente não equivale automaticamente à violação da presunção de inocência até trânsito em julgado.'),
 ('REF-SER-0001','CF88:ART.5:INC.LVII','Olhos que Condenam','Condenação errada não basta para demonstrar especificamente violação do marco constitucional da presunção de inocência.'),
 ('REF-LIV-0001','CF88:ART.5:INC.XII','1984','Vigilância doméstica/teletela sustenta intimidade e vida privada, mas não demonstra interceptação de correspondência/comunicação entre pessoas.'),
 ('REF-FIL-0006','CF88:ART.5:INC.XIV','The Post: A Guerra Secreta','Publicação jornalística não demonstra por si só direito geral de acesso à informação nem sigilo da fonte.'),
 ('REF-LIV-0003','CF88:ART.5:INC.XLII','O Sol É para Todos','Racismo é central, mas a obra não ajuda especificamente a compreender o mecanismo constitucional de criminalização do racismo.'),
 ('REF-FIL-0007','CF88:ART.225:PAR.3','O Preço da Verdade','Busca por responsabilização/reparação ambiental não demonstra o regime constitucional específico de sanções penais e administrativas independentemente da reparação.'),
 ('EXP-DOC-010','CF88:ART.23:INC.IX','Citizen Jane: Battle for the City','Urbanismo/renovação urbana genérica não prova programa de construção de moradias, melhoria habitacional ou saneamento básico.')]
SPECIAL=('CF88:ART.6','EXP-FIL-006')
MULTI_KEEP={('CF88:ART.227','REF-LIV-0004'),('CF88:ART.5:INC.IX','REF-FIL-0006'),('CF88:ART.5:INC.X','REF-FIL-0003'),('CF88:ART.6','REF-LIV-0004')}


# Reference-level partial scope, grounded in the frozen text and evidence.
# Values are display prose and editorial limits, not matcher requirements.
SCOPES={
 'CF88:ART.14':('o direito ao voto como forma de participação popular',['Não demonstra as modalidades e os requisitos eleitorais brasileiros.']),
 'CF88:ART.1:PAR.UNICO':('a participação dos governados no exercício do poder político',['Não descreve todas as formas constitucionais de representação e participação direta.']),
 'CF88:ART.170':('a justiça social e a existência digna como finalidades da ordem econômica',['Não representa a organização integral da economia nem os instrumentos econômicos previstos nos incisos.']),
 'CF88:ART.170:INC.II':('a proteção da propriedade privada',['Não demonstra todos os requisitos de intervenção estatal ou de desapropriação no Brasil.']),
 'CF88:ART.170:INC.VI':('a defesa do meio ambiente diante de atividades econômicas',['Não demonstra o tratamento normativo diferenciado de produtos e processos segundo seu impacto ambiental.']),
 'CF88:ART.170:INC.VII':('a redução das desigualdades sociais',['Não demonstra desigualdade regional específica nem um instrumento estatal de redução da desigualdade.']),
 'CF88:ART.193':('a justiça social como objetivo da ordem social',['Não representa conjuntamente todas as dimensões do primado do trabalho, do bem-estar e da organização da ordem social.']),
 'CF88:ART.194':('a proteção social diante da incapacidade para o trabalho, no âmbito da seguridade social',['Não demonstra recusa de serviço de saúde nem a organização integrada do sistema brasileiro de seguridade.']),
 'CF88:ART.1:INC.III':('a dignidade humana diante de condições que comprometem a autonomia ou a subsistência',['Não atribui à obra cobertura de todas as dimensões da dignidade humana.']),
 'CF88:ART.2':('a separação dos poderes e seus controles recíprocos',['Não equipara a organização institucional estrangeira à Constituição brasileira.']),
 'CF88:ART.203:INC.VI':('a vulnerabilidade socioeconômica de famílias pobres que a assistência social busca reduzir',['Não retrata implementação, competência ou funcionamento de programa assistencial brasileiro.']),
 'CF88:ART.205':('o direito à educação e sua função na formação da cidadania',['Não demonstra realização de todas as finalidades de desenvolvimento pessoal, preparo para cidadania e qualificação profissional.']),
 'CF88:ART.220':('a liberdade de informação e de comunicação',['Não demonstra todas as condições e responsabilidades constitucionais da comunicação social.']),
 'CF88:ART.220:PAR.2':('a proteção contra a censura política ou ideológica',['Não afirma que a evidência alcance também censura artística.']),
 'CF88:ART.225':('o direito ao meio ambiente equilibrado e a necessidade de protegê-lo',['Não demonstra todas as obrigações dos Poderes Públicos nem os instrumentos e sanções dos parágrafos.']),
 'CF88:ART.226:PAR.7':('a liberdade de decisão reprodutiva e a vedação à coerção no planejamento familiar',['Não demonstra a oferta estatal de recursos educacionais e científicos nem todo o regime brasileiro de planejamento familiar.']),
 'CF88:ART.23:INC.IX':('a construção de moradias por meio de programa habitacional',['Não demonstra saneamento básico nem a distribuição constitucional brasileira de competências.']),
 'CF88:ART.3:INC.III':('o enfrentamento da pobreza e da marginalização social',['Não demonstra execução de política pública ou erradicação efetiva desses problemas.']),
 'CF88:ART.4:INC.VIII':('o repúdio ao racismo',['Não afirma terrorismo nem descreve integralmente a política externa brasileira.']),
 'CF88:ART.5':('a igualdade de tratamento, sem distinções arbitrárias',['Não demonstra todas as garantias e condições enumeradas no art. 5º.']),
 'CF88:ART.5:INC.I':('a igualdade de direitos entre homens e mulheres',['Não representa todos os direitos e obrigações constitucionais relativos à igualdade de gênero.']),
 'CF88:ART.5:INC.III':('a proibição da tortura',['A relação se limita à análise histórica da punição; não abrange todas as formas de tratamento desumano ou degradante.']),
 'CF88:ART.5:INC.IV':('a liberdade de manifestação do pensamento',['Não demonstra a regra constitucional de vedação ao anonimato.']),
 'CF88:ART.5:INC.IX':('a liberdade de expressão intelectual ou de comunicação, sem censura',['Não afirma exercício de todas as modalidades de atividade artística, científica e intelectual nem regime de licenciamento.']),
 'CF88:ART.5:INC.LIV':('a proteção contra a privação arbitrária de liberdade e a exigência de um processo justo',['Não prova o cumprimento ou a violação de cada etapa do devido processo legal brasileiro.']),
 'CF88:ART.5:INC.LV':('a possibilidade de conhecer a acusação e exercer defesa efetiva',['Não representa todos os meios e recursos do contraditório e da ampla defesa no sistema brasileiro.']),
 'CF88:ART.5:INC.LVII':('a cautela em atribuir culpa ao acusado diante de dúvida probatória',['A comparação é pedagógica; não reproduz a estrutura recursal nem demonstra o trânsito em julgado brasileiro.']),
 'CF88:ART.5:INC.LXXIX':('a proteção dos dados pessoais contra usos invasivos ou abusivos',['Não demonstra todo o regime legal de tratamento de dados nem depende de que a informação esteja em meio digital.']),
 'CF88:ART.5:INC.VI':('a liberdade de crença e de prática religiosa',['Não demonstra todas as garantias legais de locais de culto e liturgias.']),
 'CF88:ART.5:INC.VIII':('a proteção contra a privação de direitos por motivo de crença',['Não afirma recusa de obrigação legal geral nem de prestação alternativa fixada em lei.']),
 'CF88:ART.5:INC.X':('a proteção da intimidade e da vida privada',['Não demonstra, por si, violação da honra ou da imagem nem indenização por dano material ou moral.']),
 'CF88:ART.5:INC.XII':('o sigilo das comunicações privadas diante de escutas',['Não demonstra todos os meios de comunicação enumerados nem as condições brasileiras de autorização judicial de interceptação.']),
 'CF88:ART.5:INC.XIII':('a liberdade de exercer uma profissão sem discriminação',['Não afirma cumprimento, dispensa ou violação das qualificações profissionais que a lei estabelecer.']),
 'CF88:ART.5:INC.XIV':('o acesso à informação diante de sua ocultação por autoridades',['Não afirma sigilo da fonte no exercício profissional.']),
 'CF88:ART.5:INC.XLII':('o contexto social e histórico do racismo que a Constituição criminaliza',['A contextualização não demonstra o regime brasileiro de inafiançabilidade, imprescritibilidade ou aplicação da pena de reclusão.']),
 'CF88:ART.5:INC.XLIX':('o respeito à integridade física e moral da pessoa presa',['Não descreve integralmente o regime penitenciário brasileiro.']),
 'CF88:ART.5:INC.XV':('a liberdade de circulação e de ingresso no território',['A fronteira fictícia permite comparação; não comprova os requisitos brasileiros de ingresso, permanência, saída ou circulação de bens.']),
 'CF88:ART.5:INC.XXII':('a proteção do direito de propriedade',['Não demonstra todos os limites constitucionais da propriedade nem o regime brasileiro de desapropriação.']),
 'CF88:ART.5:INC.XXXV':('o acesso à Justiça para buscar proteção diante de lesão ou ameaça a direito',['Não demonstra a existência de lei brasileira que exclua a apreciação judicial.']),
 'CF88:ART.7:INC.IV':('a formação histórica do direito ao salário mínimo',['Não demonstra o atendimento de todas as necessidades enumeradas, os critérios atuais de reajuste ou a vedação de vinculação.'])}


def scope_for(r):
    did=r['device_id'];objects=r['escopo_afirmado']['proposicao']['objetos'];wid=r['work_id']
    if did=='CF88:ART.6':
        obj=objects[0]
        parts={'ALIMENTACAO':'o direito social à alimentação','MORADIA':'o direito social à moradia','ACESSO_EMPREGO':'o direito social ao trabalho'}
        require(obj in parts,'Unexpected retained art.6 route')
        part=parts[obj];limits=['Não demonstra os demais direitos sociais enumerados no art. 6º.']
    elif did=='CF88:ART.227':
        part='a proteção prioritária da alimentação de crianças' if r['nucleo_id'].endswith('#N1') else 'o direito de crianças à alimentação entre os direitos protegidos pelo art. 227'
        limits=['A evidência é a fome dos filhos; não demonstra violação autônoma dos demais direitos enumerados, como saúde, educação e convivência familiar.']
    elif did=='CF88:ART.3:INC.IV':
        if 'DISCRIMINACAO_RACIAL' in objects:part='o combate ao preconceito e à discriminação racial'
        elif 'DISCRIMINACAO_ETNICA' in objects:part='o combate à discriminação por origem étnica'
        else:part='o combate a distinções arbitrárias no tratamento dos integrantes de uma comunidade'
        limits=['Não demonstra todas as espécies de discriminação enumeradas no dispositivo.']
        if wid=='REF-LIV-0006':limits=['A distinção entre animais é alegórica; não é apresentada como discriminação racial ou étnica humana.']
    else:part,limits=copy.deepcopy(SCOPES[did])
    if did=='CF88:ART.3:INC.III' and 'DESIGUALDADE_ECONOMICA' in objects:
        part='a redução das desigualdades sociais';limits=['Não demonstra especificamente desigualdades regionais nem a execução de medidas brasileiras.']
    if did=='CF88:ART.5:INC.IX' and wid=='REF-LIV-0001':
        part='a liberdade de expressão intelectual diante da repressão a pensamentos e escritos dissidentes'
        limits=['Não demonstra atividade artística ou científica específica nem todas as modalidades de comunicação.']
    if did=='CF88:ART.5:INC.IX' and wid=='REF-FIL-0006':part='a liberdade de comunicação jornalística sem censura'
    if did=='CF88:ART.1:INC.III':
        part='a dignidade humana diante da servidão reprodutiva' if wid=='REF-SER-0002' else 'a dignidade humana diante da privação de condições materiais básicas'
    if did=='CF88:ART.4:INC.VIII':
        evidence_objects={o for e in r['evidencias'] for o in e['claim']['objects']}
        require('DISCRIMINACAO_RACIAL' in evidence_objects and 'TERRORISMO' not in evidence_objects,'Unexpected art.4 evidence; stop for explicit reconciliation')
    return part,limits


def display_fact(r):
    # Source paraphrases remain the authoritative factual boundary.
    texts=list(dict.fromkeys(e['source']['paraphrase'] for e in r['evidencias']))
    return ' '.join(texts)


def route_text(r,part,limits):
    fact=display_fact(r)
    if r['device_id']=='CF88:ART.4:INC.VIII':
        bridge='A obra ajuda a compreender por que o racismo é objeto de repúdio constitucional.'
    elif r['device_id']=='CF88:ART.5:INC.XLII':
        bridge='Essa análise contextualiza o racismo, problema social que a Constituição trata como crime.'
    else:bridge='A referência ajuda a compreender '+part+'.'
    # Limit in every explanation, kept concise; full inherited limits stay internal.
    return fact+' '+bridge+' '+limits[0]


def prepare_ledger():
    source=load(RC1/'REFERENCIAS_RC1.json');rows=source['references'];groups=defaultdict(list)
    for r in rows:groups[key(r)].append(r)
    require(len(rows)==125 and len(groups)==120,'RC1 counts differ; no silent reconciliation')
    rejects={}
    for wid,did,title,reason in REJECTS:
        k=(did,wid);require(k in groups,'Missing rejected pair: '+title+' '+did)
        require(all(r['obra']==title for r in groups[k]),'Title/ID mismatch: '+title)
        rejects[k]=reason
    require(len(rejects)==19,'Rejected count differs')
    entries=[]
    for k,rs in sorted(groups.items()):
        kept=[];removed=[];adjustments=[];editorial=[]
        for r in rs:
            rid=r['reference_id']
            if k in rejects:removed.append(rid);continue
            if k==SPECIAL and r['nucleo_id']=='CF88:ART.6#N2':
                require(r['escopo_afirmado']['proposicao']['objetos']==['SAUDE'],'Wrong special route')
                removed.append(rid);continue
            kept.append(rid)
            part,limits=scope_for(r)
            adjustments.append(dict(reference_id=rid,PARTE_ALCANCADA=part,PARTE_NAO_AFIRMADA=limits,
                nature='AJUSTE_DA_REFERENCIA_NAO_DA_REPRESENTACAO_JURIDICA',
                rationale='Regra humana de escopo parcial; proposição original da engine preservada apenas como proveniência.'))
            editorial.append(dict(reference_id=rid,POR_QUE_ESTA_OBRA_SE_RELACIONA=route_text(r,part,limits),
                source_evidence_ids=[e['evidence_id'] for e in r['evidencias']]))
        decision='REJEITAR' if k in rejects else 'APROVAR'
        if k in rejects:reason=rejects[k]
        elif k==SPECIAL:reason='Manter somente alimentação: falta de sustento e recurso a banco alimentar constituem evidência direta de privação alimentar. Rejeitar saúde: infarto + benefício por incapacidade não demonstram violação ou acesso ao direito social à saúde.'
        elif k in MULTI_KEEP:reason='Aprovação humana expressa das duas rotas. Preservar separadamente suas evidências e seus alcances, sem fundir justificativas.'
        else:reason='Aprovação humana final deste vínculo entre os 101 aprovados, com alcance limitado à parte demonstrada pelas evidências RC1. A redação pedagógica abaixo explicita o alcance, sem acrescentar nova decisão humana.'
        entries.append(dict(work_id=k[1],obra=rs[0]['obra'],device_id=k[0],decisao_humana=decision,
            rotas_RC1=[r['reference_id'] for r in rs],rotas_mantidas=kept,rotas_rejeitadas=removed,
            justificativa_editorial=reason,ajustes_de_escopo=adjustments,explicacoes_por_rota=editorial,versao=VERSION,
            authority='MENSAGEM_HUMANA_EXPLICITA',decision_scope='REJEICAO_INTEGRAL' if decision=='REJEITAR' else 'APROVACAO_PARCIAL_DE_ROTAS' if removed else 'APROVACAO_INTEGRAL_DAS_ROTAS',
            justificativa_authority='Motivos dos rejeitados e do caso especial: fornecidos pelo usuário. Demais explicações: redação editorial assistida limitada à prova, sem nova adjudicação.'))
    counts=Counter(e['decisao_humana'] for e in entries)
    require(counts==Counter(APROVAR=101,REJEITAR=19),'Human totals differ')
    require(sum(len(e['rotas_mantidas']) for e in entries)==105,'Expected route total differs')
    ledger=dict(schema=VERSION,versao=VERSION,data=DATE,total_pairs=120,counts=dict(counts),rc1_routes=125,kept_routes=105,rejected_routes=20,
        authority='Todos os 120 vínculos foram revisados pelo humano: 101 aprovar e 19 rejeitar, com uma rota adicional rejeitada no vínculo art.6 aprovado.',
        source_message=dict(path=str(SOURCE),sha256=sha(SOURCE)),rc1_sha256=sha(RC1/'REFERENCIAS_RC1.json'),
        scope_policy='Decisão de publicação editorial; não altera nem reavalia engine, contratos, evidências ou rótulos históricos.',pairs=entries)
    write(LEDGER,ledger)
    md=['# Revisão humana final do RC1 — V1','', '120 vínculos: 101 APROVAR e 19 REJEITAR. Rotas: 125 originais, 105 mantidas, 20 removidas.','',
        'Autoridade: mensagem humana fornecida na retomada. Motivos dos rejeitados e do caso especial preservados. Explicações aprovadas são redação editorial apoiada nas evidências congeladas, não novos rótulos.','']
    for e in entries:
        md += [f"## {e['obra']} → {e['device_id']}",'',f"Decisão: **{e['decisao_humana']}**. Obra: `{e['work_id']}`.",'',e['justificativa_editorial'],'',
            'Rotas RC1: '+', '.join(e['rotas_RC1'])+'.','', 'Mantidas: '+(', '.join(e['rotas_mantidas']) or 'nenhuma')+'.','',
            'Rejeitadas: '+(', '.join(e['rotas_rejeitadas']) or 'nenhuma')+'.','']
        for a,x in zip(e['ajustes_de_escopo'],e['explicacoes_por_rota']):md += [f"Rota `{a['reference_id']}`: {x['POR_QUE_ESTA_OBRA_SE_RELACIONA']}",'',f"Parte alcançada: {a['PARTE_ALCANCADA']}. Parte não afirmada: {' '.join(a['PARTE_NAO_AFIRMADA'])}",'']
    write(LEDGER.with_suffix('.md'),'\n'.join(md)+'\n')
    # Freeze the sole human input and the immutable RC1. Generator hashes make
    # reconstruction auditable; time does not enter generated output bytes.
    inputs=[LEDGER,LEDGER.with_suffix('.md'),Path(__file__),RC1/'REFERENCIAS_RC1.json',RC1/'MANIFEST.json']
    write(ROOT/'00_CHECKPOINTS/RC2_HUMAN_LEDGER_FREEZE.json',dict(version=VERSION,date=DATE,self_excluded=True,
        source_message_sha256=sha(SOURCE),files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in inputs]))
    print('Ledger frozen',dict(counts),'105 kept / 20 removed',flush=True)


def metadata(references,links):
    counts=Counter(l['work_id'] for l in links);total=len(links);order=sorted(counts.items(),key=lambda x:(-x[1],x[0]));hhi=sum((n/total)**2 for _,n in order)
    media_links=Counter(l['tipo'] for l in links)
    work_media={l['work_id']:l['tipo'] for l in links};media_works=Counter(work_media.values())
    nature_links=Counter();objects_links=Counter()
    for l in links:
        for n in {r['relacao_pedagogica'] for r in l['rotas']}:nature_links[n]+=1
        for o in {r['objeto_alcancado'] for r in l['rotas']}:objects_links[o]+=1
    return dict(schema='CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED',date=DATE,review_version=VERSION,
        unique_links=total,proof_routes=len(references),devices_covered=len({l['device_id'] for l in links}),works_used=len(counts),
        media_links=dict(media_links),media_distinct_works=dict(media_works),
        concentration=dict(unit='vínculos únicos por obra; não duplica rotas',top1=sum(n for _,n in order[:1])/total,
            top5=sum(n for _,n in order[:5])/total,top10=sum(n for _,n in order[:10])/total,HHI=hhi,HHI_10000=hhi*10000,effective_works=1/hhi,counts_by_work=dict(order)),
        relations_by_route=dict(Counter(r['relacao_pedagogica'] for r in references)),objects_by_route=dict(Counter(r['objeto_alcancado'] for r in references)),
        relations_by_link=dict(nature_links),objects_by_link=dict(objects_links),distribution_note='Por rota é exclusiva; por vínculo é inclusiva quando há múltiplas rotas.',
        historical_scores='Copiados sem ajuste; null continua null. Seleção histórica é proveniência, não novo ranking editorial.',
        human_approvals=101,human_rejections=19,route_rejections=20,engine_evaluations=0,holdout_opened=False,
        engine_input_hash=load(RC1/'REFERENCIAS_RC1.json')['input_hash'],rc1_sha256=sha(RC1/'REFERENCIAS_RC1.json'),human_ledger_sha256=sha(LEDGER),
        status='CONSOLIDADO_HUMANAMENTE_SEM_INTEGRACAO',limitations='Aprovação humana deste conjunto fechado; não mede precisão global nem resolve cobertura de outros dispositivos.')


def build():
    freeze=load(ROOT/'00_CHECKPOINTS/RC2_HUMAN_LEDGER_FREEZE.json')
    for r in freeze['files']:require(sha(ROOT/r['path'])==r['sha256'],'Frozen editorial input changed: '+r['path'])
    src=load(RC1/'REFERENCIAS_RC1.json');ledger=load(LEDGER);original={r['reference_id']:r for r in src['references']}
    refs=[];links=[];edits=[]
    for e in ledger['pairs']:
        for rid in e['rotas_rejeitadas']:edits.append(dict(action='REMOVE_ROUTE',reference_id=rid,work_id=e['work_id'],device_id=e['device_id'],reason=e['justificativa_editorial']))
        if e['decisao_humana']=='REJEITAR':continue
        routes=[]
        by_adj={a['reference_id']:a for a in e['ajustes_de_escopo']};by_text={a['reference_id']:a for a in e['explicacoes_por_rota']}
        for rid in e['rotas_mantidas']:
            old=original[rid];r=copy.deepcopy(old);a=by_adj[rid];x=by_text[rid]
            # Keep the engine's compound proposition as historical evidence of
            # its output, never as the claim made by the reviewed reference.
            r['prova_original_rc1']=dict(nao_e_escopo_editorial_rc2=True,reference_sha256=digest(old),
                escopo_afirmado=old['escopo_afirmado'],escopo_nao_afirmado=old['escopo_nao_afirmado'],
                explicacao=old['POR_QUE_ESTA_OBRA_SE_RELACIONA'],proveniencia=old['proveniencia'],versions_hashes=old['versions_hashes'])
            r['PARTE_ALCANCADA']=a['PARTE_ALCANCADA'];r['PARTE_NAO_AFIRMADA']=a['PARTE_NAO_AFIRMADA']
            r['escopo_afirmado']=dict(PARTE_ALCANCADA=a['PARTE_ALCANCADA'],evidence_ids=[ev['evidence_id'] for ev in r['evidencias']],
                natureza=r['relacao_pedagogica'],objeto_alcancado=r['objeto_alcancado'],
                contrato=copy.deepcopy(old['escopo_afirmado']['contrato']),ancoras=old['escopo_afirmado']['ancoras'],
                nota='A proposição jurídica original composta permanece somente em prova_original_rc1. Este campo delimita o alcance editorial aprovado, não altera contratos da engine.')
            r['escopo_nao_afirmado']=list(dict.fromkeys(a['PARTE_NAO_AFIRMADA']+old['escopo_nao_afirmado']))
            r['POR_QUE_ESTA_OBRA_SE_RELACIONA']=x['POR_QUE_ESTA_OBRA_SE_RELACIONA']
            r['decisao_humana']='APROVAR';r['versao_revisao']=VERSION
            r['proveniencia']['status']='APROVADO_HUMANAMENTE_COM_ESCOPO_PARCIAL'
            r['proveniencia']['editorial_review']=dict(version=VERSION,authority='MENSAGEM_HUMANA_EXPLICITA',ledger_sha256=sha(LEDGER),
                evidence_annotations_unchanged=True,engine_state_not_overwritten=True)
            r['versions_hashes']['rc1_reference_hash']=digest(old);r['versions_hashes']['human_review_ledger_sha256']=sha(LEDGER)
            refs.append(r);routes.append(r)
            edits.append(dict(action='NARROW_DISPLAY_SCOPE_AND_REWRITE_EXPLANATION',reference_id=rid,work_id=e['work_id'],device_id=e['device_id'],
                before=dict(scope=old['escopo_afirmado'],explanation=old['POR_QUE_ESTA_OBRA_SE_RELACIONA']),
                after=dict(scope=r['escopo_afirmado'],explanation=r['POR_QUE_ESTA_OBRA_SE_RELACIONA'],not_affirmed=r['PARTE_NAO_AFIRMADA']),
                evidence_changed=False,constitutional_text_changed=False))
        # Each different assertion remains individually visible. Do not merge
        # separate episodes into a new invented fact at the link level.
        explanations=list(dict.fromkeys(r['POR_QUE_ESTA_OBRA_SE_RELACIONA'] for r in routes))
        display=' '.join(explanations) if len(explanations)==1 else ' '.join(f"{i+1}. {text}" for i,text in enumerate(explanations))
        if key(e)==('CF88:ART.227','REF-LIV-0004'):
            display='O diário descreve a fome vivida por Carolina e seus filhos na favela do Canindé. A situação ajuda a compreender a proteção prioritária da alimentação das crianças. Não demonstra, por si, violação de todos os demais direitos enumerados no art. 227.'
        if key(e)==('CF88:ART.6','REF-LIV-0004'):
            display='O diário relata a fome de Carolina e seus filhos e, em outra evidência, a precariedade da moradia da família no Canindé. As duas situações ajudam a compreender os direitos sociais à alimentação e à moradia, sem afirmar os demais direitos enumerados no art. 6º.'
        if key(e)==('CF88:ART.5:INC.IX','REF-FIL-0006'):
            display='O filme mostra a publicação dos Pentagon Papers e a tentativa do governo de restringir sua divulgação. As duas evidências ajudam a compreender a liberdade de comunicação jornalística sem censura, sem afirmar todas as modalidades de expressão previstas no inciso.'
        if key(e)==('CF88:ART.5:INC.X','REF-FIL-0003'):
            display='O filme mostra escutas no apartamento de um dramaturgo e, em outra situação, o uso de informação sobre a dependência química de Christa-Maria para pressioná-la. Essas evidências ajudam a compreender a proteção da intimidade e da vida privada, sem demonstrar indenização ou todas as demais dimensões do inciso.'
        links.append(dict(work_id=e['work_id'],obra=e['obra'],device_id=e['device_id'],tipo=routes[0]['tipo'],ano=routes[0]['ano'],decisao_humana='APROVAR',
            rotas_RC2=[r['reference_id'] for r in routes],rotas=[dict(reference_id=r['reference_id'],nucleo_id=r['nucleo_id'],relacao_pedagogica=r['relacao_pedagogica'],objeto_alcancado=r['objeto_alcancado'],
                PARTE_ALCANCADA=r['PARTE_ALCANCADA'],PARTE_NAO_AFIRMADA=r['PARTE_NAO_AFIRMADA'],evidence_ids=[v['evidence_id'] for v in r['evidencias']],
                POR_QUE_ESTA_OBRA_SE_RELACIONA=r['POR_QUE_ESTA_OBRA_SE_RELACIONA']) for r in routes],
            POR_QUE_ESTA_OBRA_SE_RELACIONA=display,justificativa_editorial=e['justificativa_editorial']))
    refs.sort(key=lambda r:(r['device_id'],r['work_id'],r['reference_id']));links.sort(key=key)
    meta=metadata(refs,links)
    changed=dict(schema='ALTERACOES_RC1_PARA_RC2',rc1_pairs=120,rc2_pairs=len(links),rc1_routes=125,rc2_routes=len(refs),
        human_rejected_pairs=19,removed_routes=20,kept_routes=105,scope_adjusted_routes=len(refs),
        art4_viii_adjusted_routes=sum(r['device_id']=='CF88:ART.4:INC.VIII' for r in refs),
        before_multi_pairs=5,after_multi_pairs=sum(len(l['rotas'])>1 for l in links),
        no_new_links=True,engine_unchanged=True,edits=edits)
    decisions=copy.deepcopy(ledger)
    readme=f'''# CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED

Consolidação editorial da revisão humana final: **101 vínculos aprovados**, **105 rotas de prova**. As 19 rejeições integrais e uma rejeição de rota de saúde foram aplicadas ao RC1 de 120 vínculos/125 rotas.

`REFERENCIAS_RC2.json` contém os vínculos com explicação pedagógica final e as referências completas por rota. Quatro vínculos mantêm duas rotas; evidências e fontes não foram fundidas. O vínculo Eu, Daniel Blake → art.6 mantém somente alimentação.

Todas as referências separam PARTE_ALCANCADA de PARTE_NAO_AFIRMADA. Seis rotas do art.4 VIII alcançam somente racismo, sem afirmar terrorismo ou toda a política externa brasileira. Outros dispositivos compostos também recebem limites explícitos. O texto integral dos dispositivos e as provas originais permanecem preservados. A prova original da engine é proveniência, não o alcance editorial afirmado no RC2.

Os rótulos decorrem exclusivamente das decisões humanas fornecidas. As explicações são redação assistida com base nas evidências RC1, sem pesquisa nova, fatos novos ou reavaliação da engine. Scores e evidências foram copiados sem alteração.

Arquivos: REFERENCIAS_RC2.json; METADADOS_RC2.json; DECISOES_HUMANAS.json; ALTERACOES_RC1_PARA_RC2.json; README.md; MANIFEST.json. O ledger canônico está em `06_BENCHMARKS/REVISAO_HUMANA_RC1_FINAL_V1.json` e no relatório MD correspondente.

Mídia por vínculo: {meta['media_links']}. Dispositivos cobertos: {meta['devices_covered']}; obras utilizadas: {meta['works_used']}. As distribuições por rota e por vínculo estão separadas nos metadados.

RC2 é seleção editorial humana do conjunto RC1; não é R1D2 nem mudança de engine. Não há execução de benchmark ou pipeline integral nesta missão. O holdout permanece fechado. Sem firmware, IDX, SD, catálogo ou DNA oficial.

Próximo passo: usar este pacote como candidato editorial aprovado e conservar o ledger como referência para futura avaliação da Engine V3, sem alterar agora o pipeline R1D1.
'''
    payloads={'REFERENCIAS_RC2.json':serialized(dict(schema='CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED',versao=VERSION,
        rc1_sha256=sha(RC1/'REFERENCIAS_RC1.json'),ledger_sha256=sha(LEDGER),unique_links=len(links),total_references=len(refs),
        reference_unit='Uma rota de prova preservada por reference_id; vínculos únicos estão em links.',references=refs,links=links)),
        'METADADOS_RC2.json':serialized(meta),'DECISOES_HUMANAS.json':serialized(decisions),
        'ALTERACOES_RC1_PARA_RC2.json':serialized(changed),'README.md':readme}
    manifest=dict(schema='RC2_HUMAN_REVIEWED_MANIFEST',date=DATE,self_excluded=True,inputs=dict(rc1_sha256=sha(RC1/'REFERENCIAS_RC1.json'),ledger_sha256=sha(LEDGER),
        freeze_sha256=sha(ROOT/'00_CHECKPOINTS/RC2_HUMAN_LEDGER_FREEZE.json')),
        files=[dict(path=name,sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),bytes=len(text.encode('utf-8'))) for name,text in sorted(payloads.items())])
    payloads['MANIFEST.json']=serialized(manifest)
    return payloads


def validate(payload):
    src=load(RC1/'REFERENCIAS_RC1.json');old={r['reference_id']:r for r in src['references']};ledger=load(LEDGER)
    data=json.loads(payload['REFERENCIAS_RC2.json']);refs=data['references'];links=data['links'];actual={key(l) for l in links}
    expected={key(e) for e in ledger['pairs'] if e['decisao_humana']=='APROVAR'}
    approved_ids={rid for e in ledger['pairs'] for rid in e['rotas_mantidas']}
    rejected_ids={rid for e in ledger['pairs'] for rid in e['rotas_rejeitadas']}
    checks=dict(expected_101_links=len(links)==101,expected_105_routes=len(refs)==105,
        unique_pairs=len(actual)==len(links),unique_routes=len({r['reference_id'] for r in refs})==len(refs),
        exact_approved_pairs=actual==expected,no_new_links=actual<={key(r) for r in src['references']},
        rejected19_absent=not actual & {(did,wid) for wid,did,_,_ in REJECTS},
        exact_retained_routes={r['reference_id'] for r in refs}==approved_ids,
        rejected_routes_absent=not {r['reference_id'] for r in refs}&rejected_ids,
        special_health_absent=not any(key(r)==SPECIAL and r['nucleo_id']=='CF88:ART.6#N2' for r in refs),
        special_food_preserved=sum(key(r)==SPECIAL and r['nucleo_id']=='CF88:ART.6#N3' for r in refs)==1,
        four_multiroute_pairs_preserved=all(sum(key(r)==k for r in refs)==2 for k in MULTI_KEEP),
        constitutional_text_unchanged=all(r['texto_dispositivo']==old[r['reference_id']]['texto_dispositivo'] for r in refs),
        evidence_sources_score_unchanged=all(all(r[f]==old[r['reference_id']][f] for f in ['evidencias','fontes','score_editorial','nucleo_id','relacao_pedagogica','objeto_alcancado']) for r in refs),
        contracts_unchanged=all(r['escopo_afirmado']['contrato']==old[r['reference_id']]['escopo_afirmado']['contrato'] for r in refs),
        art4_scopes_racism_only=all('racismo' in r['PARTE_ALCANCADA'] and 'terrorismo' not in r['PARTE_ALCANCADA'].lower() and any('terrorismo' in s for s in r['PARTE_NAO_AFIRMADA']) for r in refs if r['device_id']=='CF88:ART.4:INC.VIII'),
        art4_all_six_preserved=sum(r['device_id']=='CF88:ART.4:INC.VIII' for r in refs)==6,
        partial_scope_fields_complete=all(r['PARTE_ALCANCADA'] and r['PARTE_NAO_AFIRMADA'] for r in refs),
        natural_display_no_internal_jargon=all(not any(word in r['POR_QUE_ESTA_OBRA_SE_RELACIONA'] for word in ['matched_requirements','predicate','objects_all','N1','N2','N3','CONTEXTUALIZACAO','ILUSTRACAO','ANALOGIA']) for r in refs+links),
        all_ledger_routes_partitioned=all(set(e['rotas_RC1'])==set(e['rotas_mantidas'])|set(e['rotas_rejeitadas']) and not set(e['rotas_mantidas'])&set(e['rotas_rejeitadas']) for e in ledger['pairs']))
    require(all(checks.values()),'RC2 validation failed: '+str({k:v for k,v in checks.items() if not v}))
    return checks


def generate_twice():
    require(not RC2.exists(),'RC2 already exists; do not overwrite')
    first=build();checks=validate(first)
    for name,text in first.items():write(RC2/name,text)
    # Independent reconstruction reloads frozen RC1/ledger and creates all bytes.
    second=build();validate(second)
    dest=ROOT/'00_CHECKPOINTS/RC2_HUMAN_REVIEW_DETERMINISM_RUN2'
    for name,text in second.items():write(dest/name,text)
    hashes={name:dict(run1=sha(RC2/name),run2=sha(dest/name),equal=sha(RC2/name)==sha(dest/name)) for name in first}
    require(all(v['equal'] for v in hashes.values()),'RC2 generation is not deterministic')
    write(ROOT/'00_CHECKPOINTS/RC2_HUMAN_REVIEW_VALIDATION.json',dict(version=VERSION,passed=True,checks=checks,count_divergences=[],engine_evaluated=False))
    write(ROOT/'00_CHECKPOINTS/RC2_HUMAN_REVIEW_DETERMINISM.json',dict(version=VERSION,runs=2,all_files_identical=True,files=hashes,
        basis='RC1 congelado + ledger humano congelado; nenhuma data variável ou execução da engine nos resultados.'))
    print('RC2 generated twice and validated',load(RC2/'METADADOS_RC2.json'),flush=True)


if __name__=='__main__':
    if sys.argv[1]=='ledger':prepare_ledger()
    elif sys.argv[1]=='generate':generate_twice()
    else:raise ValueError('Unknown command')
