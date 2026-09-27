"""Resume driver for lots 5-8 after the Codex interruption.

Reuses editorial.process unchanged. Unlike from_table.py, nothing is decided by
candidate-number ranges: status, content_type, centrality and sources are explicit
per candidate in 02_TRIAGEM/CURADORIA_RETOMADA_<lote>.json. Does not run the engine.
"""
import sys
from editorial import ROOT, load, process

ALLOWED = {'APTA', 'APTA_COM_RESSALVA', 'FONTE_EM_REVISAO', 'REJEITADA_DUPLICATA_EXISTENTE',
           'REJEITADA_REDUNDANCIA_EXTREMA', 'REJEITADA_EVIDENCIA_FRACA',
           'REJEITADA_FONTE_INSUFICIENTE', 'REJEITADA_INCOMPATIBILIDADE'}
TIERS = {'A', 'B', 'C'}

batch = int(sys.argv[1])
rows = load(ROOT / '02_TRIAGEM' / f'CURADORIA_RETOMADA_{batch:02}.json')
for r in rows:
    assert r['status_triagem'] in ALLOWED, r['number']
    for f in r.get('fontes', []):
        assert f['tier'] in TIERS and f['url'].startswith('http'), (r['number'], f)
        f.setdefault('accessed_on', '2026-09-26')
    if r['status_triagem'] in ('APTA', 'APTA_COM_RESSALVA'):
        for fact in r['facts']:
            assert fact['content_type'] and fact.get('centrality') in ('CENTRAL', 'FORTE', 'PONTUAL'), (r['number'], fact)
    else:
        assert r.get('motivo'), r['number']
process(batch, rows)
