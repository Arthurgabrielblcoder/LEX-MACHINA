"""Deterministic compiler of the candidate catalog (no engine, no device links).

Inputs (frozen after editorial decisions):
  02_TRIAGEM/LOTE_01..08.json, 04_DOSSIERS/*.json, 00_ENTRADA/REFERENCIA_CATALOGO_69.json
Outputs (to the directory given as argv[1], default 07_CATALOGO_CANDIDATO):
  CATALOGO_EXPANSAO_200.json, CATALOGO_TOTAL_69_MAIS_APTAS.json
No timestamps or environment-dependent values are written, so two runs over the
same inputs must produce byte-identical files.
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USABLE = ('APTA', 'APTA_COM_RESSALVA')
STATUS_CATALOGO = 'CANDIDATO_NAO_INTEGRADO'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(out_dir):
    triage = []
    for i in range(1, 9):
        triage += load(ROOT / '02_TRIAGEM' / f'LOTE_{i:02}.json')
    assert len(triage) == 200 and len({e['number'] for e in triage}) == 200
    works = []
    for e in sorted(triage, key=lambda x: x['work_id']):
        if e['status_triagem'] not in USABLE:
            continue
        d = load(ROOT / '04_DOSSIERS' / f"{e['work_id']}.json")
        assert d['status_triagem'] == e['status_triagem'] and d['evidencias']
        assert all(c['not_targeted_to_device'] is True for c in d['evidencias'])
        works.append({
            'work_id': d['work_id'], 'candidate_id': d['candidate_id'], 'candidate_number': d['number'],
            'titulo': d['titulo'], 'titulo_informado': d['titulo_informado'], 'titulo_original': d.get('titulo_original'),
            'titulo_ptbr': d.get('titulo_ptbr'), 'tipo': d['tipo'], 'subtipo': d.get('subtipo'), 'franquia': d.get('franquia'),
            'ano': d['ano'], 'pais': d.get('pais'), 'criadores': d['criadores'],
            'publisher_distribuidor_editora': d.get('publisher_distribuidor_editora', []),
            'status_triagem': d['status_triagem'], 'status_catalogo': STATUS_CATALOGO, 'not_targeted_to_device': True,
            'resumo_factual_curto': d['resumo_factual_curto'], 'evidencias': d['evidencias'], 'fontes': d['fontes'],
            'areas_potenciais': d.get('areas_potenciais', []), 'objetos_juridicos_potenciais': d.get('objetos_juridicos_potenciais', []),
            'riscos': d.get('riscos', []), 'transposition_limits': d.get('transposition_limits', []),
            'notas': {k: d[k] for k in ('nota_edicao', 'nota_correcao', 'motivo', 'duplicate_of') if d.get(k)},
            'metadata_pendente': d.get('metadata_pendente', []),
            'provenance': d['provenance']})
    counts = {}
    for w in works:
        counts.setdefault(w['tipo'], {}).setdefault(w['status_triagem'], 0)
        counts[w['tipo']][w['status_triagem']] += 1
    expansao = {
        'catalogo': 'CATALOGO_EXPANSAO_200', 'status_catalogo': STATUS_CATALOGO,
        'aviso': 'Catálogo candidato. NÃO é o catálogo oficial; sem vínculos obra↔dispositivo; Engine não executada.',
        'criterio_inclusao': list(USABLE), 'total_obras': len(works), 'por_tipo_status': counts,
        'total_evidence_cards': sum(len(w['evidencias']) for w in works), 'obras': works}
    ref = load(ROOT / '00_ENTRADA' / 'REFERENCIA_CATALOGO_69.json')
    existing = [{'id': w['id'], 'titulo': w['titulo'], 'titulo_original': w.get('titulo_original'), 'tipo': w['tipo'],
                 'ano': w.get('ano'), 'origem': 'CATALOGO_69_CONGELADO', 'status_catalogo': 'OFICIAL_EXISTENTE'}
                for w in sorted(ref['obras'], key=lambda x: x['id'])]
    novas = [{'id': w['work_id'], 'titulo': w['titulo'], 'titulo_original': w['titulo_original'], 'tipo': w['tipo'],
              'ano': w['ano'], 'origem': 'EXPANSAO_200', 'status_triagem': w['status_triagem'],
              'status_catalogo': STATUS_CATALOGO} for w in works]
    total = {
        'catalogo': 'CATALOGO_TOTAL_69_MAIS_APTAS', 'status_catalogo': STATUS_CATALOGO,
        'aviso': 'União editorial para planejamento. As 69 obras são referência congelada (não alteradas); as novas não estão integradas.',
        'referencia_69': {'path': ref['path'], 'sha256_declarado': ref['sha256'], 'total': len(existing)},
        'total_existentes': len(existing), 'total_novas_utilizaveis': len(novas),
        'total_novas_apta': sum(1 for w in novas if w['status_triagem'] == 'APTA'),
        'total_potencial_69_mais_apta': len(existing) + sum(1 for w in novas if w['status_triagem'] == 'APTA'),
        'total_potencial_69_mais_apta_e_ressalva': len(existing) + len(novas),
        'obras': existing + novas}
    out = Path(out_dir)
    dump(out / 'CATALOGO_EXPANSAO_200.json', expansao)
    dump(out / 'CATALOGO_TOTAL_69_MAIS_APTAS.json', total)
    for name in ('CATALOGO_EXPANSAO_200.json', 'CATALOGO_TOTAL_69_MAIS_APTAS.json'):
        print(name, sha(out / name))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / '07_CATALOGO_CANDIDATO')
