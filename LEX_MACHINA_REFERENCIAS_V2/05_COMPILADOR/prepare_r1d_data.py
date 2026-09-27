"""Editorial policy data overlay, independent of evaluation labels.

No evaluation is performed here. Existing R1C inputs and output are immutable.
"""
import copy
import sys
from collections import Counter
from pathlib import Path
from canonical_input_r1c import load_canonical
from proof_compiler_r1 import load, require, digest, file_hash, source_hash
from r1d_support import ROOT, POLICY, DATE, now, write, key, contract, dependent_contracts, apply_overlay

RULES = {
 'A': ('PRINCIPIO_OU_OBJETIVO_AMPLO', 'Pode ilustrar problema social, violação ou consequência diretamente nomeados ou materialmente representados pelo dispositivo. Não exige representação do mecanismo estatal de solução.'),
 'B': ('MECANISMO_INSTITUTO_REGIME_ESPECIFICO', 'Exige evidência do mecanismo, instituto, sujeito, condição ou contexto essencial. Tema ancestral não basta.'),
 'C': ('GARANTIA_AUTONOMA', 'Garantia que constitui núcleo autônomo pode ser ilustrada diretamente.'),
 'D': ('GARANTIA_DEPENDENTE', 'Garantia em regime funcional, procedimento específico, mecanismo institucional ou hipótese delimitada não se desprende do contexto hospedeiro. Exige ao menos uma âncora essencial.'),
 'E': ('OBRA_ACADEMICA_DOCUMENTAL', 'Permite CONTEXTUALIZACAO_HISTORICA quando a obra explicitamente ANALISA o mesmo objeto jurídico/social. Não exige que o autor PRATIQUE o evento.'),
 'F': ('ANALOGIA_CONTROLADA', 'Pode atravessar país, época e instituição preservando o núcleo pedagógico. Não apaga objeto, sujeito, subtipo ou mecanismo essencial.'),
 'G': ('CONDICAO_SOCIAL', 'Pode ilustrar o problema combatido por política constitucional. Não significa representar implementação, competência, programa ou instrumento.')}

# These are authoritative ledger entries, never passed to the compiler.
HUMAN = [
 ('REF-DOC-0001','CF88:ART.14','CONDICIONAL','ANALOGIA_CONTROLADA','EVIDENCIA_INSUFICIENTE', 'Efeito explícito sobre escolha, comportamento ou autonomia eleitoral. Exploração de dados isolada não basta; a ficha congelada não valida essa ponte.'),
 ('REF-DOC-0004','CF88:ART.170:INC.VII','APROVAR','ILUSTRACAO_DE_CONSEQUENCIA','APROVAR','Privação/desigualdade concretas ilustram o problema social a reduzir; não um instrumento econômico.'),
 ('REF-JOG-0001','CF88:ART.1:INC.III','CONDICIONAL','ANALOGIA_CONTROLADA','EVIDENCIA_INSUFICIENTE','Exige tratamento degradante, desumanização, coerção, instrumentalização ou lesão equivalente documentada. Controle documental sozinho não basta.'),
 ('REF-LIV-0004','CF88:ART.1:INC.III','APROVAR','ILUSTRACAO_DE_CONSEQUENCIA','APROVAR','Fome/privação/desproteção documentadas ilustram comprometimento da dignidade; não exigir NEGAR_ACESSO ativo.'),
 ('EXP-DOC-003','CF88:ART.1:INC.IV','CONDICIONAL','ANALOGIA_CONTROLADA','EVIDENCIA_INSUFICIENTE','Exige ponte específica com trabalho, renda, estrutura econômica ou valor social do trabalho. A ficha sobre distância genérica de rendas não discrimina essa ponte laboral.'),
 ('REF-LIV-0006','CF88:ART.1:PAR.UNICO','CONDICIONAL','ANALOGIA_CONTROLADA','EVIDENCIA_INSUFICIENTE','Exige concentração/usurpação de poder mais supressão/exclusão da participação dos governados. A afirmação tipada atual não valida conjuntamente a ponte; democracia não é ancestral de toda regra eleitoral.'),
 ('REF-DOC-0004','CF88:ART.203:INC.VI','APROVAR','ILUSTRACAO_DE_CONSEQUENCIA','APROVAR','Vulnerabilidade socioeconômica de famílias/pessoas pobres ilustra PROBLEMA_SOCIAL, sem afirmar execução da política assistencial.'),
 ('REF-LIV-0004','CF88:ART.203:INC.VI','APROVAR','ILUSTRACAO_DE_CONSEQUENCIA','APROVAR','Mesma política do caso 07: privação familiar ilustra problema-alvo; não programa estatal.'),
 ('REF-LIV-0004','CF88:ART.3:INC.III','APROVAR','ILUSTRACAO_DE_CONSEQUENCIA','APROVAR','Pobreza/marginalização documentadas ilustram o objetivo de erradicação; não exigir negativa ativa.'),
 ('REF-LIV-0005','CF88:ART.5:INC.III','APROVAR','CONTEXTUALIZACAO_HISTORICA','APROVAR','Análise histórico-acadêmica explicitamente relacionada à tortura/tratamento degradante sustenta a referência. Não transformar ANALISAR em PRATICAR.'),
 ('REF-FIL-0001','CF88:ART.5:INC.LV','REJEITAR',None,'REJEITAR','Reexame de prova e dúvida probatória não demonstram contraditório/ampla defesa; revisão humana expressa do APROVAR histórico.'),
 ('REF-LIV-0005','CF88:ART.5:INC.XLIX','CONDICIONAL','CONTEXTUALIZACAO_HISTORICA','EVIDENCIA_INSUFICIENTE','Exige passagem específica de integridade física/moral do preso ou tratamento penitenciário nessa dimensão. A ficha editorial geral não valida uma passagem delimitada; análise geral da prisão não basta.')]

# Direct application of A-G, no invented human approval.
ADDITIONAL = {
 ('CF88:ART.19:INC.I','EXP-FIL-009'): ('PENDENTE_HUMANO','B,F','Coação religiosa documentada; decidir se poder de facto configura o contexto institucional de estabelecimento/embaraço de culto. Não equiparar automaticamente coação individual e aliança estatal.'),
 ('CF88:ART.19:INC.I','REF-SER-0002'): ('EVIDENCIA_INSUFICIENTE_SEGUNDO_POLITICA','B,F','Subordinação reprodutiva não documenta a relação institucional Estado/culto exigida. Fonte nova do caso art.5 VI permaneceu insuficiente.'),
 ('CF88:ART.1:INC.III','REF-FIL-0008'): ('PENDENTE_HUMANO','A,F','Proteção de vida de grupo étnico está documentada, mas a passagem de proteção da vida à consequência sobre dignidade requer explicitação editorial; não é mera equivalência entre direitos.'),
 ('CF88:ART.1:INC.III','REF-JOG-0002'): ('APROVAR_SEGUNDO_POLITICA','A,G','Falta de comida/remédios para civis em cerco documenta privação material. Mesma política humana da dignidade por consequência; não exigir agente que negue acesso.'),
 ('CF88:ART.1:PAR.UNICO','REF-DOC-0003'): ('EVIDENCIA_INSUFICIENTE_SEGUNDO_POLITICA','A,F','Documentar impeachment não valida concentração de poder mais exclusão da participação popular.'),
 ('CF88:ART.2','REF-DOC-0003'): ('EVIDENCIA_INSUFICIENTE_SEGUNDO_POLITICA','B,F','Impeachment não demonstra por si só defesa ou violação da separação dos Poderes.'),
 ('CF88:ART.205','EXP-LIV-004'): ('APROVAR_SEGUNDO_POLITICA','A,E','A fonte R1C p.11 historia explicitamente educação como condição da cidadania. CONTEXTUALIZACAO_HISTORICA não exige prática EDUCAR.'),
 ('CF88:ART.220:PAR.1','REF-SER-0003'): ('EVIDENCIA_INSUFICIENTE_SEGUNDO_POLITICA','B,F','Ocultar risco ambiental não documenta obstáculo à informação jornalística em veículo de comunicação social.'),
 ('CF88:ART.55:PAR.3','REF-LIV-0002'): ('REJEITAR_SEGUNDO_POLITICA','B,D,F','Defesa em persecução opaca não traz âncora de mandato parlamentar ou declaração pela Mesa. Rejeição editorial desse suporte, não prova negativa sobre toda a obra.'),
 ('CF88:ART.5:INC.III','REF-JOG-0002'): ('EVIDENCIA_INSUFICIENTE_SEGUNDO_POLITICA','C,F','Escassez e busca de sobrevivência não documentam por si tortura ou tratamento degradante concreto.'),
 ('CF88:ART.5:INC.III','REF-LIV-0007'): ('PENDENTE_HUMANO','C,F','A privação de rações por internos é documentada, mas permanece ambiguidade da natureza degradante e revisão já exigida. Não generalizar a política de dignidade para toda tortura/tratamento.'),
 ('CF88:ART.5:INC.LVII','REF-LIV-0002'): ('EVIDENCIA_INSUFICIENTE_SEGUNDO_POLITICA','C,F','Execução sem julgamento não prova condenação judicial; eventual analogia não pode apagar o mecanismo da garantia.'),
 ('CF88:ART.5:INC.XII','REF-DOC-0001'): ('REJEITAR_SEGUNDO_POLITICA','B,F','Exploração de dados pessoais não demonstra violação de sigilo de comunicação/interceptação. Não confundir objeto protegido com o art.5 LXXIX.'),
 ('CF88:ART.5:INC.XIV','REF-SER-0003'): ('APROVAR_SEGUNDO_POLITICA','C','Ocultação estatal de informação de risco à população ilustra diretamente acesso à informação, núcleo autônomo. Não afirma sigilo da fonte profissional nem prática de publicação jornalística.')}


def evidence(base, wid, suffix, predicate, objects, participants, source, limits, context=()):
    template = copy.deepcopy(base.works[wid]['evidences'][0])
    template.update(evidence_id=wid+suffix,state='VALIDADA',content_type='EVENTO_NARRATIVO',polarity='AFIRMADA',
        source=source,claim=dict(predicate=predicate,objects=list(objects),participants=[dict(concept=c,role=r) for c,r in participants],
        subjects=[c for c,r in participants if r=='ACTOR'],context=list(context),effects=[]),transposition_limits=limits,
        provenance=dict(version='R1D_ADJUDICADA',method='curadoria_dirigida_oito_casos',human_validated=False,source_checked=True))
    template['source']['hash']=source_hash(template['source'])
    return template


def card(url, locator, text, tier):
    return dict(identifier=url,locator=locator,paraphrase=text,tier=tier,consulted_at=DATE,
                hash_scope='SHA256 da ficha documental; não bytes da página remota')


def prepare():
    require(not (ROOT/'03_OBRAS/CURADORIA_EDITORIAL_R1D.json').exists(), 'R1D already prepared')
    sim=load(ROOT/'06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json')
    require(sim['implementation_applied'] is False, 'Simulation must precede implementation')
    base=load_canonical(); data=copy.deepcopy(base.data)
    ds={d['device_id']:d for d in data['devices']}
    master=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
    prior={key(p):p for p in master['pairs']}
    policy=dict(id=POLICY,date=DATE,created_at=now(),authority='Decisões editoriais humanas na mensagem de retomada R1C',
        rules={k:dict(name=v[0],rule=v[1]) for k,v in RULES.items()},
        constraints=['R1C imutável','Sem R2, novo matcher, score ou threshold','Garantia dependente simulada antes de aplicada','Histórico nunca sobrescrito'],
        label_semantics='Rótulo adjudicado separa decisões humanas diretas, aplicação da política e pendências. Insuficientes/pendentes não entram na matriz binária; matriz histórica paralela obrigatória.',
        gate_protocol=dict(new_structural_failure=False,max_known_fp=4,recent35_max_fp=0,recent20_negative_min=18,
            recent25_admissible_min=17,mechanisms15_admissible_min=12,negative_mechanisms10_min=10,
            require_all_contracts_disposed=True,require_all_eight_closed=True,
            explanation='Critérios de preservação derivados dos controles R1C; não são thresholds do compilador. Não exige recuperar todos os positivos históricos.'))
    write('01_SCHEMA/POLITICA_EDITORIAL_REFERENCIAS_V2_V1.json',policy)
    write('01_SCHEMA/POLITICA_EDITORIAL_REFERENCIAS_V2_V1.md','# Política editorial de referências V2 V1\n\nAutoridade: mensagem humana de retomada. Data: '+DATE+'\n\n'+'\n\n'.join(f'**{k}. {v[0]}** — {v[1]}' for k,v in RULES.items())+'\n\nInsuficiência factual não equivale a incompatibilidade. As aplicações inequívocas são identificadas como aplicação de política, nunca como nova decisão humana.\n')
    human=[]
    for i,(wid,did,decision,nature,label,reason) in enumerate(HUMAN,1):
        human.append(dict(caso=f'{i:02}',work_id=wid,device_id=did,obra=base.works[wid]['nome'],
            decisao='ROTA_EDITORIAL_AUTORIZADA_CONDICIONALMENTE' if decision=='CONDICIONAL' else decision,
            natureza=nature,objeto='PROBLEMA_SOCIAL' if i in [2,7,8,9] else None,
            rotulo_historico=prior[(did,wid)]['label'],rotulo_adjudicado_v1=label,justificativa=reason,
            autoridade='HUMANA_EXPLICITA',policy=POLICY,date=DATE,
            condicao_validada=False if decision=='CONDICIONAL' else None))
    fp=[dict(device_id=c['device_id'],work_id=c['work_id'],obra=c['obra'],rotulo_historico='REJEITAR',rotulo_adjudicado_v1='REJEITAR',
        justificativa='Obstrução da defesa penal não basta para regime funcional específico.',autoridade='HUMANA_EXPLICITA') for c in sim['cases'] if c['impacto']=='FP_ELIMINADO']
    write('06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.json',dict(policy=POLICY,date=DATE,total=12,cases=human,fp_confirmados=fp))
    md=['# Adjudicação humana R1C V1','',f'Política: {POLICY}; data: {DATE}. Decisão condicional não é aprovação do par enquanto a ponte não for validada.','']
    for r in human:md += [f"## {r['caso']}. {r['obra']} → {r['device_id']}",'',f"Decisão: {r['decisao']}. Histórico: {r['rotulo_historico']}; adjudicado V1: {r['rotulo_adjudicado_v1']}. Natureza: {r['natureza']}.",'',r['justificativa'],'']
    md += ['Quatro FP: REJEITAR mantido, pela exigência de âncora funcional.','', 'Política geral: [regras A–G](../01_SCHEMA/POLITICA_EDITORIAL_REFERENCIAS_V2_V1.md).']
    write('06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.md','\n'.join(md)+'\n')

    residual=load(ROOT/'06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1C.json')['cases']
    original={key(r) for r in human}
    extras=[r for r in residual if r['primary_cause']=='CONTRATO_REQUER_ADJUDICACAO' and key(r) not in original]
    require(len(extras)==14 and {key(r) for r in extras}==set(ADDITIONAL), 'Unexpected additional scope')
    extra_rows=[]
    for c in extras:
        decision,rules,reason=ADDITIONAL[key(c)]
        label=decision.replace('_SEGUNDO_POLITICA','')
        extra_rows.append(dict(device_id=c['device_id'],work_id=c['work_id'],obra=c['obra'],pair_id=c['pair_id'],
            decisao=decision,rotulo_historico=prior[key(c)]['label'],rotulo_adjudicado_v1=label,
            regras=rules.split(','),justificativa=reason,existing_claims=c['existing_claims'],
            fonte_causal='DECOMPOSICAO_CAUSAL_FN_R1C.json',authority='APLICACAO_DA_POLITICA_HUMANA' if label!='PENDENTE_HUMANO' else 'REQUER_HUMANO',policy=POLICY,date=DATE))
    extra_counts=dict(Counter(r['rotulo_adjudicado_v1'] for r in extra_rows))
    write('06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.json',dict(total=14,policy=POLICY,source_sha256=file_hash(ROOT/'06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1C.json'),counts=extra_counts,cases=extra_rows))
    write('06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.md','# 14 contratos adicionais após política\n\n'+str(extra_counts)+'\n\n'+'\n\n'.join(f"**{r['obra']} → {r['device_id']}**: {r['decisao']} (regras {','.join(r['regras'])}). {r['justificativa']}" for r in extra_rows)+'\n')

    changes=[]
    def add(did,index,c,reason):
        n=ds[did]['nuclei'][index]
        n['contracts_by_relation'].append(c)
        changes.append(dict(device_id=did,nucleus_id=n['nucleus_id'],action='APPEND_CONTRACT',reason=reason,contract=c))
    def c(relation,obj,pred,objects,reason,**kw):
        return contract(relation,obj,pred,objects,reason=reason,**kw)
    for d in ds.values():
        for n in d['nuclei']:
            if n['role']=='GARANTIA_TRANSVERSAL':
                old=copy.deepcopy(n['contracts_by_relation']);n['contracts_by_relation']=dependent_contracts(d,n)
                changes.append(dict(device_id=d['device_id'],nucleus_id=n['nucleus_id'],action='ANCHOR_CONTRACTS',before=old,after=n['contracts_by_relation'],reason='Política D aplicada após simulação de todos os 12 conhecidos.'))
    # Social condition remains a specific contractual route, never predicate equivalence.
    for did,idx,obj in [('CF88:ART.1:INC.III',0,'VALOR_DIREITO'),('CF88:ART.3:INC.III',0,'PROBLEMA_SOCIAL'),('CF88:ART.170',1,'VALOR_DIREITO')]:
        add(did,idx,c('ILUSTRACAO_DE_CONSEQUENCIA',obj,['DESPROTEGER'],['ALIMENTACAO'],'A/G: privação alimentar documentada como consequência; não exige negativa ativa.'),'A/G e decisão humana 04/09')
    add('CF88:ART.1:INC.III',0,c('ILUSTRACAO_DE_CONSEQUENCIA','VALOR_DIREITO',['BUSCAR_SOBREVIVENCIA'],['ALIMENTACAO','SAUDE'],'A/G: escassez material documentada para civis.',subjects=['CIVIL'],role='AFFECTED'),'Aplicação 14: This War of Mine; rota generalizável')
    for did,idx in [('CF88:ART.170:INC.VII',0),('CF88:ART.203:INC.VI',0)]:
        add(did,idx,c('ILUSTRACAO_DE_CONSEQUENCIA','PROBLEMA_SOCIAL',['NEGAR_ACESSO','DESPROTEGER'],['ALIMENTACAO'],'A/G: privação de pessoas/famílias vulneráveis; não implementa política ou instrumento.',subjects=['CRIANCA','MAE','MULHER','FAMILIA'],role='AFFECTED'),'Decisões humanas 02/07/08')
    add('CF88:ART.205',2,c('CONTEXTUALIZACAO_HISTORICA','VALOR_DIREITO',['HISTORIAR','ANALISAR'],['EDUCACAO','CIDADANIA'],'E: análise explícita de educação como condição da cidadania; não equivale a prática EDUCAR.'),'Aplicação adicional E')
    add('CF88:ART.5:INC.XIV',0,c('ILUSTRACAO_DE_VIOLACAO','VALOR_DIREITO',['OCULTAR'],['INFORMACAO_RISCO_AMBIENTAL'],'C: acesso à informação de risco ocultada; não prova sigilo da fonte.',subjects=['POPULACAO'],role='AFFECTED'),'Aplicação adicional C')
    add('CF88:ART.5:INC.III',0,c('CONTEXTUALIZACAO_HISTORICA','GARANTIA',['ANALISAR','HISTORIAR'],['TORTURA'],'E/decisão 10: analisar tortura explicitamente; não PRATICAR.'),'Decisão humana 10')
    # Minimal semantic correction grounded in the already validated human-10 card.
    # It adds only the literally named object; no new source, event or predicate.
    vig=copy.deepcopy(base.works['REF-LIV-0005']['evidences'][0])
    require('tortura' in vig['source']['paraphrase'], 'Human 10 factual object missing')
    vig['claim']['objects']=sorted(set(vig['claim']['objects']+['TORTURA']))
    vig['provenance']['r1d']=dict(policy=POLICY,human_case='10',method='Anotação mínima do objeto tortura já literal na ficha validada; ANALISAR permanece ANALISAR.',prior_sha256=digest(base.works['REF-LIV-0005']['evidences'][0]))

    # Four technical representation gaps: patch the frozen data, never recreate it.
    add('CF88:ART.170',1,c('CONTEXTUALIZACAO_HISTORICA','PROBLEMA_SOCIAL',['ANALISAR'],['DESIGUALDADE_ECONOMICA'],'A/E: desigualdade de rendas como problema da justiça social na ordem econômica, sem afirmar instrumento específico.'),'Lacuna técnica 01: mesmo objeto amplo da finalidade literal')
    def nucleus(did,span,contracts,objects):
        d=ds[did];start=d['text'].index(span);nid=did+'#R1D_N'+str(len(d['nuclei'])+1)
        n=dict(nucleus_id=nid,source_spans=[dict(device_id=did,start=start,end=start+len(span),text=span)],
            template=d['family'],proposition=dict(modalidade='GARANTIA',sujeitos=['PESSOA'],predicado='GARANTIR',objetos=objects,condicoes=[],excecoes=[],finalidades=[]),
            role='AUTONOMO',depends_on=[],contracts_by_relation=contracts,state='CURADA_EXPERIMENTAL',
            provenance=dict(version='R1D_ADJUDICADA',human_validated=False,policy=POLICY,method='Complemento restrito às quatro lacunas autorizadas; preserva núcleos anteriores.'))
        d['nuclei'].append(n);d['annotation_status']='CURADA_PARCIAL'
        changes.append(dict(device_id=did,nucleus_id=nid,action='TECHNICAL_LITERAL_COMPLEMENT',reason='Lacuna técnica autorizada; igualdade genérica não se converte em espécie racial/étnica.',nucleus=n))
    unequal=c('ANALOGIA_CONTROLADA','VALOR_DIREITO',['DISCRIMINAR'],['IGUALDADE_GENERICA'],'A/F: desigualdade de tratamento explicitamente normatizada na fábula; não afirma discriminação racial/étnica.',context=['FABULA'])
    nucleus('CF88:ART.3:INC.IV','quaisquer outras formas de discriminação',[copy.deepcopy(unequal)],['IGUALDADE_GENERICA'])
    employment=c('ILUSTRACAO_DE_VIOLACAO','VALOR_DIREITO',['DISCRIMINAR'],['ACESSO_EMPREGO'],'C: discriminação concreta no emprego ilustra igualdade; não prova todos os incisos.',subjects=['TRABALHADOR'],role='AFFECTED')
    nucleus('CF88:ART.5','Todos são iguais perante a lei, sem distinção de qualquer natureza',[copy.deepcopy(unequal),employment],['IGUALDADE_GENERICA'])
    animal_url='https://www.marxists.org/subject/art/literature/children/texts/orwell/animal-farm/ch10.htm'
    animal=evidence(base,'REF-LIV-0006','#R1D01','DISCRIMINAR',['IGUALDADE_GENERICA'],[('ELITE','ACTOR')],
        card(animal_url,'Capítulo X: leitura por Benjamin do mandamento único; privilégios dos porcos e rações/trabalho dos demais.',
             'A regra escrita passa a conceder igualdade maior a alguns animais; os porcos mantêm privilégios e os demais trabalham mais com rações inferiores.','TEXTO_PRIMARIO_REPRODUZIDO'),
        ['Animais e elite são papéis alegóricos; não classificar a distinção como raça, etnia ou sexo humanos.','Não prova exercício de voto ou supressão de participação eleitoral.'],['FABULA'])
    v_url='https://web.archive.org/web/20060315180047/http://vforvendetta.warnerbros.com/cmp/prod_notes_ch_02.html'
    ve=evidence(base,'REF-FIL-0002','#R1D01','REPRIMIR',['DISSENSO_POLITICO'],[('ESTADO','ACTOR'),('OPOSITOR','AFFECTED')],
        card(v_url,'Production Notes, capítulo 2, parágrafo iniciado Evey is orphaned: pais mortos por falar contra o regime.',
             'As notas de produção do filme descrevem a morte dos pais de Evey por se manifestarem contra o regime repressivo.','PRIMARIA_PRODUTORA_ARQUIVADA'),
        ['Fonte sobre o filme, não o quadrinho. Ilustra repressão à manifestação de ideias, sem provar todas as modalidades de expressão do inciso IX.'])
    changed_devices=[d for d in data['devices'] if d!=base.devices[d['device_id']]]
    overlay=dict(schema='R1D_ADJUDICADA_DATA_OVERLAY',policy=POLICY,created_at=now(),base_input_hash=base.hash,
        simulation_sha256=file_hash(ROOT/'06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json'),devices=changed_devices,
        evidence_replacements=[vig],evidence_additions=[animal,ve],changes=changes,
        exclusions=['Nenhum rótulo ou lookup de pares no input','Sem score/threshold novos','As únicas fontes novas são para lacunas técnicas autorizadas'])
    inp=apply_overlay(base,overlay)
    require(len(inp.works)==69 and len(inp.devices)==3461,'Universe changed')
    require(inp.data['ontology']==base.data['ontology'],'Ontology changed')
    write('03_OBRAS/CURADORIA_EDITORIAL_R1D.json',overlay)
    write('01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D.json',dict(schema='R1D_ADJUDICADA_DESCRIPTOR',base_input_hash=base.hash,canonical_input_hash=inp.hash,
        overlay='03_OBRAS/CURADORIA_EDITORIAL_R1D.json',overlay_sha256=file_hash(ROOT/'03_OBRAS/CURADORIA_EDITORIAL_R1D.json'),
        policy=POLICY,works=69,devices=3461,nuclei=sum(len(d['nuclei']) for d in inp.devices.values()),
        compiler='proof_compiler_r1.py via proof_compiler_v2.py',new_matcher=False,new_score=False,new_threshold=False))

    technical=[]
    causes=load(ROOT/'00_CHECKPOINTS/R1C_GATE_DECISION.json')['curation_blocking_cases']
    queries={
        ('CF88:ART.5:INC.IV','REF-FIL-0002'):'V for Vendetta 2006 Gordon Deitrich television show arrested satire government',
        ('CF88:ART.5:INC.IX','REF-FIL-0002'):'V for Vendetta 2006 banned music art Gordon secret collection',
        ('CF88:ART.5:INC.LXXIX','REF-LIV-0001'):'1984 novel personal information records surveillance diary telescreen Winston',
        ('CF88:ART.5:INC.VI','REF-SER-0002'):"The Handmaids Tale season 1 priest executed religion church Gilead"}
    for row in causes:
        r=copy.deepcopy(row);k=key(r)
        r.update(policy=POLICY,research_closed=True,research_rounds=1 if k in queries or r['work_id']=='REF-LIV-0006' else 0)
        if k in queries:r['query']=queries[k]
        elif r['work_id']=='REF-LIV-0006':r.update(query='site.orwellfoundation.com Animal Farm "All animals are equal" "pigs"',shared_research_id='ANIMAL_EQUALITY_ONE_ROUND_FOR_TWO_CASES')
        if r['work_id']=='REF-LIV-0001':
            r.update(resolution='EVIDENCIA_INSUFICIENTE',evidence_ids=[],sources=['https://www.open.edu/openlearn/mod/oucontent/view.php?id=126526&section=6.1','https://assets.cambridge.org/97811084/83605/excerpt/9781108483605_excerpt.pdf'],
                reason='OpenLearn descreve vigilância; os dados pessoais detalhados são analogias contemporâneas, não eventos do romance. PDF Cambridge não abriu. Não converter VIGIAR em EXPLORAR dados. Uma pesquisa encerrada.')
        elif r['work_id']=='REF-SER-0002':
            r.update(resolution='EVIDENCIA_INSUFICIENTE',evidence_ids=[],sources=['https://the-handmaids-tale.fandom.com/wiki/Republic_of_Gilead_(Series)','https://en.wikipedia.org/wiki/The_Handmaid%27s_Tale'],
                reason='Resultados misturam romance e série; wiki de fãs não valida causalidade específica em fonte primária/reputada. Não atribuir automaticamente a execução do padre à crença. Uma pesquisa encerrada.')
        else:
            eid=animal['evidence_id'] if r['work_id']=='REF-LIV-0006' else ve['evidence_id'] if r['work_id']=='REF-FIL-0002' else r['work_id']+'#E01'
            r.update(resolution='RESOLVIDA',evidence_ids=[eid],sources=[animal_url] if r['work_id']=='REF-LIV-0006' else [v_url] if r['work_id']=='REF-FIL-0002' else [base.works[r['work_id']]['evidences'][0]['source']['identifier']],
                reason='Complemento contratual/literal segundo política A/C/E/F com evidência específica preservada.' if r['cause'].startswith('REPRESENTACAO') else 'Evento de repressão à expressão de ideias validado em notas oficiais; reutiliza a rota R1C REPRIMIR DISSENSO_POLITICO dos dois incisos. Não afirma todas as modalidades do IX.')
        technical.append(r)
    write('06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.json',dict(total=8,counts=dict(Counter(r['resolution'] for r in technical)),cases=technical,
        stop_rule='No máximo uma pesquisa dirigida por caso; buscas conjuntas não duplicadas. Pesquisa encerrada antes de avaliar.',
        source_rejections=['V: enciclopédia localizou pistas; validação usa nota oficial do filme.','1984: não importar exemplos contemporâneos como fato ficcional.','Handmaid: não misturar adaptação com romance.']))
    write('06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.md','# Oito lacunas técnicas R1D\n\n'+'\n\n'.join(f"**{r['obra']} → {r['device_id']}**: {r['resolution']}. {r['reason']} Fontes: "+', '.join(f'[fonte]({u})' for u in r['sources']) for r in technical)+'\n')

    ledger=copy.deepcopy(master)
    decisions={key(r):r for r in human+extra_rows}
    pending={key(r):r for r in sim['cases'] if r['impacto']=='TP_HISTORICO_PARA_READJUDICACAO'}
    for p in ledger['pairs']:
        k=key(p);p['rotulo_historico']=p['label'];p['policy']=POLICY;p['policy_date']=DATE
        if k in decisions:
            r=decisions[k];p.update(rotulo_adjudicado_v1=r['rotulo_adjudicado_v1'],motivo=r['justificativa'],authority=r.get('autoridade',r.get('authority')))
        elif k in pending:
            p.update(rotulo_adjudicado_v1='PENDENTE_HUMANO',motivo='TP histórico sem âncora essencial na simulação. Readjudicação obrigatória, sem proteção por desempenho passado.',authority='READJUDICACAO_REQUERIDA_PELA_POLITICA_D')
        else:
            p.update(rotulo_adjudicado_v1=p['label'],motivo='Histórico preservado; nenhuma nova decisão nesse par.',authority='HISTORICO_PRESERVADO')
        p['label']=p['rotulo_adjudicado_v1']
    mapping={key(p):p for p in ledger['pairs']}
    for name,items in ledger['groups'].items():
        for p in items:
            p['rotulo_historico']=p['label']
            # Preserve historical source-specific conflict labels unless adjudicated.
            if key(p) in decisions or key(p) in pending:p['label']=mapping[key(p)]['label']
            p['rotulo_adjudicado_v1']=p['label']
    ledger.update(schema='HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1',created_at=now(),policy=POLICY,
        historical_master_sha256=file_hash(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json'),
        adjudicated_counts=dict(Counter(p['label'] for p in ledger['pairs'])),
        changed_labels=[{k:p[k] for k in ['device_id','work_id','rotulo_historico','rotulo_adjudicado_v1','motivo','authority']} for p in ledger['pairs'] if p['rotulo_historico']!=p['rotulo_adjudicado_v1']],
        warning='Known development labels; not blind. Nonbinary labels excluded explicitly; historical-label sensitivity matrix required.')
    write('06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json',ledger)
    write('00_CHECKPOINTS/R1D_CURATION_COMPLETE.json',dict(status='R1D_CURATION_COMPLETE',at=now(),input_hash=inp.hash,
        human=12,additional=extra_counts,technical=dict(Counter(r['resolution'] for r in technical)),
        simulation_first=True,conditional_human_routes_still_insufficient=5,readjudication_required=len(pending),research_closed=True))
    print('R1D data prepared',inp.hash,extra_counts,ledger['adjudicated_counts'])


if __name__=='__main__':prepare()
