"""Deterministic compiler of the ENRIQUECIDO_V1 package (no engine, no device links).

Inputs (frozen): base catalog CATALOGO_EXPANSAO_200.json, Codex overlays in
04_DOSSIERS/ENRIQUECIMENTO_V1/, revision layer 06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json,
queue in 06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json, reference 69.
Writes to argv[1] (default 07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1). No timestamps.
The base catalog is read, never rewritten.
"""
import copy, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / '07_CATALOGO_CANDIDATO'
STATUS = 'CANDIDATO_NAO_INTEGRADO'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(out):
    out = Path(out)
    base_p = CAT / 'CATALOGO_EXPANSAO_200.json'
    base = load(base_p)
    revs = {r['evidence_id']: r for r in load(ROOT / '06_RELATORIOS' / 'REVISOES_ENRIQUECIMENTO_V1.json')['revisoes']}
    state = load(ROOT / '06_RELATORIOS' / 'CHECKPOINT_ENRIQUECIMENTO.json')
    queue = {x['work_id']: x for x in state['fila']}
    ov_dir = ROOT / '04_DOSSIERS' / 'ENRIQUECIMENTO_V1'
    works, cards_flat, decisions, applied = [], [], [], []
    for w in sorted(base['obras'], key=lambda x: x['work_id']):
        w = copy.deepcopy(w)
        base_cards = w['evidencias']
        for c in base_cards:
            c['origem_card'] = 'BASE_199'
        ovp = ov_dir / f"{w['work_id']}.json"
        new = []
        if ovp.exists():
            ov = load(ovp)
            d = ov['decisao']
            for c in ov['evidencias_adicionais']:
                c = copy.deepcopy(c)
                c['origem_card'] = 'ENRIQUECIMENTO_V1_CODEX'
                if c['evidence_id'] in revs:
                    patch = revs[c['evidence_id']]['patch']
                    c['unidade_documental'] = patch['unidade_documental']
                    c['escopo_centralidade'] = patch['escopo_centralidade']
                    c['claim']['context'] = patch['claim_context']
                    c['revisao_pos_codex'] = revs[c['evidence_id']]['motivo']
                    applied.append(c['evidence_id'])
                new.append(c)
            decisions.append(dict(work_id=w['work_id'], candidate_number=w['candidate_number'], titulo=w['titulo'], tipo=w['tipo'],
                                  examinada=True, examinada_por='CODEX', estado=d['estado'], cards_antes=d['cards_antes'],
                                  cards_adicionados=d['cards_adicionados'], evidence_ids=d['evidence_ids'], justificativa=d.get('justificativa'),
                                  rejeitados=d.get('rejeitados', []), overlay=ovp.relative_to(ROOT).as_posix(), overlay_sha256=sha(ovp)))
        else:
            assert w['work_id'] not in queue, w['work_id']
            decisions.append(dict(work_id=w['work_id'], candidate_number=w['candidate_number'], titulo=w['titulo'], tipo=w['tipo'],
                                  examinada=False, estado='NAO_ENFILEIRADA_COMPLETA_PROVAVEL', cards_antes=len(base_cards), cards_adicionados=0,
                                  evidence_ids=[], justificativa='Fora da fila de enriquecimento (estimativa COMPLETA_PROVAVEL em ESTIMATIVA_ENRIQUECIMENTO.json).'))
        w['evidencias'] = base_cards + new
        w['resumo_factual_curto'] = w['resumo_factual_curto']
        w['enriquecimento_v1'] = dict(cards_base=len(base_cards), cards_adicionados=len(new))
        assert all(c['not_targeted_to_device'] is True for c in w['evidencias'])
        assert len({c['evidence_id'] for c in w['evidencias']}) == len(w['evidencias'])
        works.append(w)
        for c in w['evidencias']:
            cards_flat.append(dict(c, titulo_obra=w['titulo'], tipo_obra=w['tipo']))
    assert sorted(applied) == sorted(revs), (applied, list(revs))
    assert len(works) == 199 and len(queue) == sum(1 for d in decisions if d['examinada'])
    n_base = sum(1 for c in cards_flat if c['origem_card'] == 'BASE_199')
    n_new = len(cards_flat) - n_base
    dist = {}
    for d in decisions:
        if d['examinada']:
            k = '+0' if d['cards_adicionados'] == 0 else '+1' if d['cards_adicionados'] == 1 else '+2' if d['cards_adicionados'] == 2 else '+3_OU_MAIS'
            dist[k] = dist.get(k, 0) + 1
    by_type = {}
    for c in cards_flat:
        if c['origem_card'] != 'BASE_199':
            by_type[c['content_type']] = by_type.get(c['content_type'], 0) + 1
    exp = dict(catalogo='CATALOGO_EXPANSAO_ENRIQUECIDO_V1', status_catalogo=STATUS,
               aviso='Catálogo candidato enriquecido. NÃO é catálogo oficial; sem vínculos obra↔dispositivo; Engine não executada; ontologia não mapeada (ONTOLOGY_GAP preservado).',
               base=dict(path='07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json', sha256=sha(base_p)),
               total_obras=len(works), total_evidence_cards=len(cards_flat), cards_base=n_base, cards_novos=n_new, obras=works)
    ref = load(ROOT / '00_ENTRADA' / 'REFERENCIA_CATALOGO_69.json')
    total = dict(catalogo='CATALOGO_TOTAL_ENRIQUECIDO_V1', status_catalogo=STATUS,
                 aviso='União editorial para planejamento; as 69 obras são referência congelada e não foram alteradas.',
                 referencia_69=dict(path=ref['path'], sha256_declarado=ref['sha256'], total=len(ref['obras'])),
                 total_existentes=len(ref['obras']), total_novas_utilizaveis=len(works), total_potencial=len(ref['obras']) + len(works),
                 obras=[dict(id=w['id'], titulo=w['titulo'], tipo=w['tipo'], ano=w.get('ano'), origem='CATALOGO_69_CONGELADO', status_catalogo='OFICIAL_EXISTENTE')
                        for w in sorted(ref['obras'], key=lambda x: x['id'])]
                       + [dict(id=w['work_id'], titulo=w['titulo'], tipo=w['tipo'], ano=w['ano'], origem='EXPANSAO_200', status_triagem=w['status_triagem'],
                               evidence_cards=len(w['evidencias']), status_catalogo=STATUS) for w in works])
    cards = dict(catalogo='EVIDENCE_CARDS_ENRIQUECIDOS_V1', total=len(cards_flat), base=n_base, novos=n_new,
                 todos_not_targeted_to_device=all(c['not_targeted_to_device'] is True for c in cards_flat), cards=cards_flat)
    decs = dict(total_obras=len(decisions), examinadas=sum(d['examinada'] for d in decisions), distribuicao_examinadas=dist,
                revisoes_pos_codex=sorted(applied), decisoes=decisions)
    files = {'CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json': exp, 'CATALOGO_TOTAL_ENRIQUECIDO_V1.json': total,
             'EVIDENCE_CARDS_ENRIQUECIDOS_V1.json': cards, 'DECISOES_ENRIQUECIMENTO.json': decs}
    for name, obj in files.items():
        dump(out / name, obj)
    meta = dict(pacote='ENRIQUECIDO_V1', status_catalogo=STATUS, obras_utilizaveis=len(works), candidatas_totais=200,
                cards_antes=n_base, cards_novos=n_new, cards_finais=len(cards_flat), cards_novos_por_content_type=by_type,
                obras_examinadas=decs['examinadas'], distribuicao_examinadas=dist, revisoes_pos_codex=sorted(applied),
                entradas=dict(catalogo_base=sha(base_p), checkpoint_enriquecimento=sha(ROOT / '06_RELATORIOS' / 'CHECKPOINT_ENRIQUECIMENTO.json'),
                              revisoes=sha(ROOT / '06_RELATORIOS' / 'REVISOES_ENRIQUECIMENTO_V1.json'),
                              overlays={p.name: sha(p) for p in sorted(ov_dir.glob('*.json'))}),
                engine_executada=False, vinculos_juridicos_gerados=False, ontologia_mapeada=False)
    dump(out / 'METADADOS_ENRIQUECIDO_V1.json', meta)
    readme = '\n'.join([
        '# ENRIQUECIDO_V1 — pacote congelado', '',
        'Catálogo candidato enriquecido da expansão de 200 candidatas (`status_catalogo = CANDIDATO_NAO_INTEGRADO`).', '',
        f'- Obras utilizáveis: {len(works)} (28 APTA + 171 APTA_COM_RESSALVA).',
        f'- Evidence cards: {len(cards_flat)} ({n_base} da base + {n_new} do enriquecimento V1).',
        '- Todos os cards: `not_targeted_to_device: true`; `ONTOLOGY_GAP` preservado (sem mapeamento ontológico).',
        '- Engine não executada; nenhum vínculo jurídico; catálogo base (`../CATALOGO_EXPANSAO_200.json`) não foi substituído.', '',
        '## Arquivos', '',
        '- `CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json`: 199 obras com cards base + novos.',
        '- `CATALOGO_TOTAL_ENRIQUECIDO_V1.json`: 69 obras congeladas + 199 candidatas (visão resumida).',
        '- `EVIDENCE_CARDS_ENRIQUECIDOS_V1.json`: lista plana de todos os cards, com `origem_card`.',
        '- `DECISOES_ENRIQUECIMENTO.json`: decisão por obra (examinada, cards adicionados, rejeitados, justificativa).',
        '- `METADADOS_ENRIQUECIDO_V1.json`: contagens e hashes das entradas.',
        '- `MANIFEST.json`: SHA-256 de cada arquivo do pacote.', '',
        'Reproduzir: `python 07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py <pasta>`; saída determinística (sem timestamps).',
        'Política: `06_RELATORIOS/POLITICA_ENRIQUECIMENTO_EVIDENCE_CARDS_V1.md`. Relatório: `06_RELATORIOS/RELATORIO_ENRIQUECIMENTO_V1.md`.', ''])
    (out / 'README.md').write_bytes(readme.encode('utf-8'))
    names = sorted(p.name for p in out.glob('*') if p.is_file() and p.name != 'MANIFEST.json')
    dump(out / 'MANIFEST.json', dict(pacote='ENRIQUECIDO_V1', arquivos=[dict(path=n, sha256=sha(out / n), bytes=(out / n).stat().st_size) for n in names]))
    for n in names + ['MANIFEST.json']:
        print(n, sha(out / n))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else CAT / 'ENRIQUECIDO_V1')
