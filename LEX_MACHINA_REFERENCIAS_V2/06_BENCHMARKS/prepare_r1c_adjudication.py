"""Diagnostic-only reports. No evaluation, curation or contract mutation."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'05_COMPILADOR'))
from canonical_input_r1b import load_canonical
from proof_compiler_r1 import load, serialized, digest

PROPOSALS = {
('REF-DOC-0001','CF88:ART.14'): ('ILUSTRACAO_DE_CONSEQUENCIA', 'Delimitar efeitos da exploração de dados na autonomia eleitoral; obter também evidência do efeito. Não confundir uso de dados e exercício do voto.', 'Pode atingir obras sobre comunicação e eleições; risco de converter toda persuasão em lesão eleitoral.'),
('REF-DOC-0004','CF88:ART.170:INC.VII'): ('ILUSTRACAO_DE_CONSEQUENCIA', 'Avaliar se privação alimentar pode ilustrar desigualdade social sem exigir argumento analítico; não tornar ANALISAR sinônimo de NEGAR_ACESSO.', 'Atingiria outras narrativas de carência; risco de admitir pobreza para qualquer instrumento econômico.'),
('REF-JOG-0001','CF88:ART.1:INC.III'): ('ANALOGIA_CONTROLADA', 'Definir tensão entre controle fronteiriço e tratamento digno; exigir evento adicional de tratamento da pessoa, não apenas CONTROLAR INGRESSO.', 'Atingiria jogos/filmes migratórios; risco de classificar qualquer recusa legítima como indignidade.'),
('REF-LIV-0004','CF88:ART.1:INC.III'): ('ILUSTRACAO_DE_CONSEQUENCIA', 'Avaliar desproteção alimentar documentada como consequência de vulnerabilidade; não equiparar a negativa ativa universalmente.', 'Atingiria fome em outras obras; risco de inflar dignidade sem delimitação causal.'),
('EXP-DOC-003','CF88:ART.1:INC.IV'): ('ANALOGIA_CONTROLADA', 'Delimitar argumento sobre trabalho, renda e ordem econômica, sem exigir discriminação no emprego não demonstrada.', 'Atingiria ensaios econômicos; risco de tratar distribuição genérica como fundamento laboral específico.'),
('REF-LIV-0006','CF88:ART.1:PAR.UNICO'): ('ANALOGIA_CONTROLADA', 'Avaliar contraste entre concentração de poder da fábula e soberania popular; não inventar reivindicação de voto.', 'Atingiria distopias políticas; risco de democracia virar ancestral universal de mecanismos eleitorais.'),
('REF-DOC-0004','CF88:ART.203:INC.VI'): ('ILUSTRACAO_DE_CONSEQUENCIA', 'Distinguir população vulnerável representada da implementação de programa assistencial; manter âncora da política se necessária.', 'Atingiria outras obras de pobreza; risco de finalidade sem execução da política.'),
('REF-LIV-0004','CF88:ART.203:INC.VI'): ('ILUSTRACAO_DE_CONSEQUENCIA', 'Distinguir privação autobiográfica da implementação de programa; não afirmar que o Estado presta o benefício no diário.', 'Mesmo problema das demais narrativas de vulnerabilidade e de finalidades de políticas.'),
('REF-LIV-0004','CF88:ART.3:INC.III'): ('ILUSTRACAO_DE_CONSEQUENCIA', 'Adjudicar desproteção alimentar como ilustração da pobreza a erradicar; conservar distinção factual de negativa ativa.', 'Atingiria fontes de carência material; risco de apagamento das modalidades de conduta.'),
('REF-LIV-0005','CF88:ART.5:INC.III'): ('CONTEXTUALIZACAO_HISTORICA', 'Delimitar argumento histórico sobre tortura/punição, sem atribuir ao autor a prática da tortura.', 'Atingiria outras obras acadêmicas; risco de converter qualquer menção em ocorrência factual.'),
('REF-FIL-0001','CF88:ART.5:INC.LV'): ('ANALOGIA_CONTROLADA', 'Avaliar reexame de prova pelos jurados como apoio pedagógico à garantia; não confundir dúvida probatória com obstrução de defesa.', 'Atingiria histórias de julgamento e garantias transversais; pode ampliar os quatro FP funcionais.'),
('REF-LIV-0005','CF88:ART.5:INC.XLIX'): ('CONTEXTUALIZACAO_HISTORICA', 'Exigir passagem histórica delimitada sobre integridade do preso; análise da penitenciária não é evento de violação praticado pelo autor.', 'Atingiria livros sobre punição e outros mecanismos penais; risco de apagar distinção entre analisar e praticar.')}

def prepare():
    inp=load_canonical()
    inv=load(ROOT/'06_BENCHMARKS/INVENTARIO_OPERACIONAL_105_R1C.json')['rows']
    known=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')['pairs']
    signature_devices={}
    for d in inp.devices.values():
        for n in d['nuclei']:
            for c in n['contracts_by_relation']:
                signature_devices.setdefault(digest(c),set()).add(d['device_id'])
    rows=[]
    for r in inv:
        if r['causa_principal']!='CONTRATO_DE_NATUREZA_INADEQUADO': continue
        nature,change,risk=PROPOSALS[(r['work_id'],r['dispositivo'])]
        same={r['dispositivo']}
        for group in r['contratos_existentes']:
            for c in group['contratos']:same |= signature_devices.get(digest(c),set())
        impacted=[dict(device_id=p['device_id'],work_id=p['work_id']) for p in known if p['device_id'] in same or p['work_id']==r['work_id']]
        rows.append(dict(pair_id=r['pair_id'],obra=r['obra'],work_id=r['work_id'],dispositivo=r['dispositivo'],rotulo_humano=r['rotulo_humano'],contrato_atual=r['contratos_existentes'],natureza_atual=r['natureza_pedagogica_existente'],motivo_da_perda=r['dimensao_ausente'],natureza_humana_implicita_hipotese=nature,natureza_ja_existe=True,mudanca_necessaria=change,alcance='Critério de relação generalizável; não correção por título/endereço. Nenhuma mudança implementada.',outros_casos_potencialmente_afetados=impacted,definicao_impacto='Candidatos à auditoria: mesmo contrato literal, mesmo dispositivo ou mesma obra entre os 398. Não são resultados de simulação.',risco_fp=risk,adjudicacao='PENDENTE_HUMANA'))
    assert len(rows)==12
    md=['# Doze contratos — adjudicação humana R1C','','Somente hipóteses editoriais. As naturezas propostas já existem, mas as rotas e seus limites não estão autorizados a mudar. Lista de impacto é estática, não simulação. Nenhum contrato alterado.','']
    for i,r in enumerate(rows,1):
        md += [f"## {i}. {r['obra']} → {r['dispositivo']}",'',f"Par: `{r['pair_id']}`. Rótulo: {r['rotulo_humano']}. Natureza atual: {', '.join(r['natureza_atual'])}.",'','Contrato literal:','```json',json.dumps(r['contrato_atual'],ensure_ascii=False,indent=2),'```','',f"Perda: {r['motivo_da_perda']}",'',f"Natureza humana implícita — hipótese, não decisão: {r['natureza_humana_implicita_hipotese']} (já existe).",'',f"Mudança a adjudicar: {r['mudanca_necessaria']}",'',f"Alcance: {r['alcance']}",'',f"Risco: {r['risco_fp']}",'','Outros casos a conferir (escopo estático): '+ '; '.join(x['work_id']+' → '+x['device_id'] for x in r['outros_casos_potencialmente_afetados'])+'.','','Decisão humana: PENDENTE.','']
    fps=load(ROOT/'06_BENCHMARKS/DIAGNOSTICO_FP_REMANESCENTES.json')['cases']
    proofs=load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1B.json')['rows']
    fp_rows=[]
    for f in fps:
        p=next(p for p in proofs if (p['device_id'],p['work_id'])==(f['device_id'],f['work_id']))
        d,w=inp.devices[f['device_id']],inp.works[f['work_id']]
        ids={e for q in p['proofs'] for e in q['evidence_ids']}
        fp_rows.append(dict(work_id=f['work_id'],obra=w['nome'],dispositivo=f['device_id'],prova_usada=p['proofs'],evidencias=[e for e in w['evidences'] if e['evidence_id'] in ids],nucleos=d['nuclei'],natureza=f['nature'],motivo_da_admissao=f['reason'],decisao_humana='REJEITAR',motivo_humano_documentado='O diagnóstico consolidado informa rejeição; sua explicação causal é auditoria técnica, não nova fala do revisor.',hipotese_causal='Contrato de garantia transversal autônoma admite obstrução da defesa fora do regime funcional específico. Evidência penal pode ser verdadeira e ainda assim inadequada à transposição.',tipo='CONTRATO_REQUER_ADJUDICACAO',impacto_correcao='Exigir âncora funcional pode conter esses FP, mas também perder analogias legítimas de defesa. Não restringir por par; avaliar todas as garantias transversais em nova autorização.',alteracao_implementada=False))
    fpmd=['# Quatro FP — diagnóstico para adjudicação','','Provas R1B reais reutilizadas; nenhuma nova avaliação e nenhuma correção automática.','']
    for i,r in enumerate(fp_rows,1):
        fpmd += [f"## {i}. {r['obra']} → {r['dispositivo']}",'','Decisão humana: REJEITAR. Natureza: '+', '.join(r['natureza'])+'.','',r['motivo_humano_documentado'],'',r['motivo_da_admissao'],'',r['hipotese_causal'],'','Prova e evidência literal:','```json',json.dumps({'proofs':r['prova_usada'],'evidences':r['evidencias']},ensure_ascii=False,indent=2),'```','',r['impacto_correcao'],'']
    return {'06_BENCHMARKS/CONTRATOS_12_PARA_ADJUDICACAO.json':serialized({'total':12,'cases':rows}), '06_BENCHMARKS/CONTRATOS_12_PARA_ADJUDICACAO.md':'\n'.join(md)+'\n','06_BENCHMARKS/DIAGNOSTICO_FP_4_PARA_ADJUDICACAO.json':serialized({'total':4,'cases':fp_rows}), '06_BENCHMARKS/DIAGNOSTICO_FP_4_PARA_ADJUDICACAO.md':'\n'.join(fpmd)+'\n'}

if __name__=='__main__':print(json.dumps({'files':prepare()},ensure_ascii=False))
