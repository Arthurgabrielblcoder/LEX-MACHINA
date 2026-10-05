"""Critic pass (PASSO 2) of an ENTENDA macro batch: applies the adversarial critic's (target, section, before, after) edits, in order,
to the pass-1 drafts (DRAFTER) and writes the versioned sub-block drafts + critic log. Each "before" must occur exactly once.
Usage: python macro_critic_pass.py <batch_dir> <sub_block> <edits.json> [--second-pass <second_pass_edits.json>] <pass1 part files...>
--second-pass: edits of the second pass (risk compression and source sanity), applied after the critic edits with the same contract
("before" exactly once); they may also edit article_notes (section "article_notes", target = the article). Separate log:
drafts/<P>_<X>_SECOND_PASS_LOG.json.
Reproduce sub-block A of batch 07:
  python macro_critic_pass.py derived/production_batch_07_macro A derived/production_batch_07_macro/drafts/pass1/MACRO07_A_CRITIC_EDITS.json \
         derived/production_batch_07_macro/drafts/pass1/MACRO07_A_PASS1_*.json"""
import json,sys
from pathlib import Path
BD=Path(sys.argv[1])
args=sys.argv[4:]
second=None
if args and args[0]=='--second-pass':
    second,args=args[1],args[2:]
x,editsf,parts=sys.argv[2],sys.argv[3],sorted(args)
notes,exps,jr={},[],[]
for f in parts:
    d=json.load(open(f)); notes.update(d['article_notes']); exps+=d['explanations']; jr+=d.get('jurisprudence_recommendations',[])
by={e['target_id']:e for e in exps}
assert len(by)==len(exps),'duplicate target'
def apply(edits):
  log=[]
  for ed in edits:
      if ed.get('action')=='DROP_EXPLANATION':   # critic removes a draft (e.g. the target already has an approved explanation to reuse)
          exps.remove(by.pop(ed['target']))
          log.append(dict(target_id=ed['target'],section='*',category=ed['category'],detector=ed.get('detector','CRITIC_REVIEW'),reason=ed['reason'],before='(rascunho removido)',after=''))
          continue
      sec=ed['section']
      if sec=='article_notes':
        txt=notes[ed['target']]
        assert txt.count(ed['before'])==1,(ed['target'],sec,ed['before'][:60],txt.count(ed['before']))
        notes[ed['target']]=txt.replace(ed['before'],ed['after'])
        log.append(dict(target_id=ed['target'],section=sec,category=ed['category'],detector=ed.get('detector','CRITIC_REVIEW'),reason=ed['reason'],before=ed['before'],after=ed['after']))
        continue
      e=by[ed['target']]
      if sec=='external_layer_notes':
          txt='\n'.join(e['external_layer_notes'])
      elif sec=='palavras_dificeis':
          txt=json.dumps(e['content']['palavras_dificeis'],ensure_ascii=False)
      else:
          txt=e['content'][sec] or ''
      assert txt.count(ed['before'])==1,(ed['target'],sec,ed['before'][:60],txt.count(ed['before']))
      new=txt.replace(ed['before'],ed['after'])
      if sec=='external_layer_notes':
          e['external_layer_notes']=[n for n in new.split('\n') if n.strip()]
      elif sec=='palavras_dificeis':
          e['content']['palavras_dificeis']=json.loads(new)
      else:
          e['content'][sec]=new
      log.append(dict(target_id=ed['target'],section=sec,category=ed['category'],detector=ed.get('detector','CRITIC_REVIEW'),reason=ed['reason'],before=ed['before'],after=ed['after']))
  return log
log=apply(json.load(open(editsf)))
log2=apply(json.load(open(second))) if second else None
out=dict(sub_block=x,article_notes=dict(sorted(notes.items())),explanations=exps)
if jr: out['jurisprudence_recommendations']=jr
(BD/'drafts').mkdir(parents=True,exist_ok=True)
(BD/'drafts'/f"{json.loads((BD/'MACRO_SPEC.json').read_text())['packet_prefix']}_{x}_DRAFTS.json").write_bytes((json.dumps(out,ensure_ascii=False,indent=1)+'\n').encode())
cl=dict(schema_version=1,batch_id=json.loads((BD/'MACRO_SPEC.json').read_text())['batch_id'],sub_block=x,
        policy='PASSO 2 (CRITIC): revisao adversarial do rascunho antes da triagem: regra inventada, excecao perdida, numero/quorum/prazo, lista incompleta, teleologia, condicao fora do texto, jurisprudencia velada, generalizacao, historico tratado como vigente, dependencia externa sem proveniencia, copia da Lei Seca e contrato do motor. Cada correcao registra antes/depois e motivo.',
        corrections=log)
(BD/'drafts'/f"{json.loads((BD/'MACRO_SPEC.json').read_text())['packet_prefix']}_{x}_CRITIC_LOG.json").write_bytes((json.dumps(cl,ensure_ascii=False,indent=1)+'\n').encode())
if log2 is not None:
    sl=dict(schema_version=1,batch_id=cl['batch_id'],sub_block=x,
            policy='SEGUNDO PASSE: revisao critica adicional (teleologia, regra inventada, absolutos, pai x filho, numero ilustrativo, enumeracao incompleta, remissao errada, lei infraconstitucional como CF, jurisprudencia velada, emenda recente, transicao ativa, exemplo que cria requisito) e saneamento de fonte. Correcao automatica so quando segura; o que exige interpretacao juridica externa vai para C/D. Cada correcao registra antes/depois e motivo.',
            corrections=log2)
    (BD/'drafts'/f"{json.loads((BD/'MACRO_SPEC.json').read_text())['packet_prefix']}_{x}_SECOND_PASS_LOG.json").write_bytes((json.dumps(sl,ensure_ascii=False,indent=1)+'\n').encode())
print(len(exps),'explanations;',len(log),'critic corrections'+(f'; {len(log2)} second-pass corrections' if log2 is not None else ''))
