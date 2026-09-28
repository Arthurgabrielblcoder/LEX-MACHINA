"""Generic reference engine: canonical catalogs -> validated operational links -> deterministic export -> lookup.

Norm-agnostic: every dataset comes from engine_config.json (norm -> target index, status, catalog, quarantine
resolution). No norm id is hardcoded here. Every link must pass validate_link() (fail closed):
  validate_target_id(target_id)  +  target_exists_for_norm(norma_id, target_id)  +  required fields.

Operational link (one per target; a source reference may fan out to several targets with the same source_reference_id):
  norma_id, target_id, reference_id, reference_type, source_id, source_reference_id, provenance, status, visibility,
  label, payload, validation_status, routes (WORK_REFERENCE: distinct proof routes of the same work x target link)

Export (derived, never the SD):
  <NORM>_REFERENCES_EXPORT.json   {target_id: [links]} in structural order
  REF_LOOKUP.IDX / REF_PAYLOAD.IDX  ESP32-style pair: sorted target_id -> byte offset + count into the payload file
Usage: python reference_engine.py <out_dir> [--norm CF88] [--config engine_config.json]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import target_id as T  # noqa: E402

REQUIRED = ('norma_id', 'target_id', 'reference_id', 'reference_type', 'source_id', 'status', 'visibility', 'label', 'validation_status')
TYPE_ORDER = {'WORK_REFERENCE': 0, 'JURISPRUDENCE': 1, 'CORRELATA': 2}


class EngineError(ValueError):
    def __init__(self, code, detail=''):
        super().__init__(f'{code}: {detail}')
        self.code = code


class TargetRegistry:
    """Per-norm target sets and status, loaded from configuration."""

    def __init__(self, config_path=HERE / 'engine_config.json', base=HERE):
        self.cfg = json.loads(Path(config_path).read_text(encoding='utf-8'))
        self.base = Path(base)
        self._targets, self._order, self._status = {}, {}, {}

    def load(self, norma_id):
        if norma_id not in self.cfg['norms']:
            raise EngineError('NORM_NOT_CONFIGURED', norma_id)
        if norma_id not in self._targets:
            c = self.cfg['norms'][norma_id]
            idx = json.loads((self.base / c['target_index']).read_text(encoding='utf-8'))
            if idx['norma_id'] != norma_id:
                raise EngineError('INDEX_NORM_MISMATCH', norma_id)
            self._targets[norma_id] = {t['target_id']: t for t in idx['targets']}
            self._order[norma_id] = {t['target_id']: i for i, t in enumerate(idx['targets'])}
            st = self.base / c['target_status'] if c.get('target_status') else None
            self._status[norma_id] = json.loads(st.read_text(encoding='utf-8'))['targets'] if st and st.is_file() else {}
        return self

    def target_exists_for_norm(self, norma_id, target_id):
        ok, _ = T.validate_target_id(target_id)
        if not ok:
            return False
        self.load(norma_id)
        return T.parse_target_id(target_id)['norma_id'] == norma_id and target_id in self._targets[norma_id]

    def status(self, norma_id, target_id):
        return self._status[norma_id].get(target_id, {}).get('status', 'UNKNOWN_VALIDITY')

    def order(self, norma_id, target_id):
        return self._order[norma_id][target_id]


def validate_link(link, reg):
    for f in REQUIRED:
        if link.get(f) in (None, ''):
            raise EngineError('LINK_MISSING_FIELD', f'{link.get("reference_id")}: {f}')
    ok, err = T.validate_target_id(link['target_id'])
    if not ok:
        raise EngineError('LINK_INVALID_TARGET_ID', f'{link["reference_id"]}: {err}')
    if not reg.target_exists_for_norm(link['norma_id'], link['target_id']):
        raise EngineError('LINK_TARGET_NOT_IN_NORM', f'{link["reference_id"]}: {link["norma_id"]} {link["target_id"]}')
    return True


def _visibility(cfg, status):
    return cfg['export']['visibility'].get(status, cfg['export']['visibility']['default'])


def _clean(s):
    return ' '.join(str(s or '').replace('|', '/').split())


def build_links(norma_id, reg):
    """Catalog records (exported layers) + quarantine resolutions -> validated operational links."""
    reg.load(norma_id)
    c = reg.cfg['norms'][norma_id]
    layers = reg.cfg['export']['layers']
    cat = json.loads((reg.base / c['references_catalog']).read_text(encoding='utf-8'))['records']
    links = []

    def add(target, rtype, source_id, source_ref, label, provenance, payload, migration, route=None):
        status = reg.status(norma_id, target)
        link = dict(norma_id=norma_id, target_id=target, reference_id=f'{rtype}:{source_ref}@{target}', reference_type=rtype,
                    source_id=source_id, source_reference_id=source_ref, provenance=provenance, status=status,
                    visibility=_visibility(reg.cfg, status), label=_clean(label), payload=payload, migration=migration,
                    validation_status='VALIDATED', routes=[route] if route else [])
        validate_link(link, reg)
        links.append(link)

    for r in cat:
        rtype = layers.get(r['source_layer'])
        if not rtype:
            continue
        prov = r['provenance']
        if rtype == 'WORK_REFERENCE':
            lf = r.get('legal_fields_preserved', {})
            add(r['target_id'], rtype, prov['work_id'], prov['work_id'], prov['obra'], dict(system=prov['system'], work_id=prov['work_id'], tipo=prov['tipo']),
                dict(obra=prov['obra'], tipo=prov['tipo'], ano=lf.get('ano'), relacao=(lf.get('escopo_afirmado') or {}).get('natureza')),
                r['migration_status'], route=dict(reference_id=r['source_record_id'], nucleo_id=lf.get('nucleo_id'),
                                                  evidence_ids=[e.get('evidence_id') for e in lf.get('evidencias', [])]))
        elif rtype == 'JURISPRUDENCE':
            base = ':'.join(r['source_record_id'].split(':')[:3])
            add(r['target_id'], rtype, base, r['source_record_id'], r['label'], dict(system=prov['system'], tribunal=prov.get('tribunal'), tipo=prov.get('tipo'),
                numero=prov.get('numero'), metodo=prov.get('metodo')), dict(tribunal=prov.get('tribunal'), tipo=prov.get('tipo'), numero=prov.get('numero'),
                titulo=r['label'], fonte=prov.get('fonte')), r['migration_status'])
        elif rtype == 'CORRELATA':
            for rel, dest in zip(prov.get('relacoes', []), prov.get('destinos', [])):
                add(r['target_id'], rtype, dest, rel, dest, dict(system=prov['system'], relacao_id=rel, index_row=r['source_record_id']),
                    dict(destino=dest, relacao_id=rel), r['migration_status'])
    res_path = reg.base / c['quarantine_resolution'] if c.get('quarantine_resolution') else None
    if res_path and res_path.is_file():
        for q in json.loads(res_path.read_text(encoding='utf-8'))['records']:
            if q['klass'] != 'MIXED_RESOLVED_BY_SPLIT':
                continue
            rtype = layers.get(q['source_layer'])
            if rtype != 'JURISPRUDENCE':
                raise EngineError('RESOLUTION_LAYER_NOT_EXPORTABLE', q['source_layer'])
            j = q.get('jurisprudence', {})
            base = ':'.join(q['original_record_id'].split(':')[:3])
            for t in q['targets']:
                add(t, rtype, base, q['original_record_id'], j.get('titulo'), dict(system='Jurisprudencia CF J4 (VINCULOS_EXPLICITOS)', tribunal=j.get('tribunal'),
                    tipo=j.get('tipo'), numero=j.get('numero'), split_from=q['original_device_key'], citation=q.get('citation', '')[:200],
                    wording_note=q.get('wording_note')), dict(tribunal=j.get('tribunal'), tipo=j.get('tipo'), numero=j.get('numero'), titulo=j.get('titulo'),
                    fonte=j.get('fonte')), 'SPLIT_FROM_LITERAL_CITATION')
    # WORK_REFERENCE: distinct proof routes of the same (target, work) become one link with several routes (provenance kept)
    merged, out = {}, []
    for l in links:
        if l['reference_type'] == 'WORK_REFERENCE':
            k = (l['target_id'], l['source_id'])
            if k in merged:
                merged[k]['routes'] += l['routes']
                merged[k]['duplicate_class'] = 'MULTI_ROUTE_DISTINCT_PROVENANCE'
                continue
            merged[k] = l
        out.append(l)
    ids = [l['reference_id'] for l in out]
    if len(ids) != len(set(ids)):
        raise EngineError('DUPLICATE_REFERENCE_ID', str(len(ids) - len(set(ids))))
    for l in out:
        l.setdefault('duplicate_class', 'DISTINCT')
        l['routes'].sort(key=lambda r: r['reference_id'])
    out.sort(key=lambda l: (reg.order(norma_id, l['target_id']), TYPE_ORDER.get(l['reference_type'], 9), l['label'], l['reference_id']))
    return out


def export(norma_id, links, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    grouped = {}
    for l in links:
        grouped.setdefault(l['target_id'], []).append(l)
    doc = dict(schema_version=1, norma_id=norma_id, grouping='target_id', order='estrutural (indice) ; tipo ; label ; reference_id',
               targets_with_references=len(grouped), total_links=len(links), references=grouped)
    j = out_dir / f'{norma_id}_REFERENCES_EXPORT.json'
    j.write_bytes((json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False) + '\n').encode('utf-8'))
    # ESP32-style pair (UTF-8, LF): payload lines grouped by target, lookup sorted by target_id (ASCII) for binary search
    payload_lines, lookup = ['#LEXMACHINA|REF_PAYLOAD|1', '#TARGET_ID|TIPO|VISIBILIDADE|STATUS|REFERENCE_ID|SOURCE_ID|LABEL'], []
    head = ('\n'.join(payload_lines) + '\n').encode('utf-8')
    offset = len(head)
    body = []
    for tid in sorted(grouped):
        lines = [f"{tid}|{l['reference_type']}|{l['visibility']}|{l['status']}|{_clean(l['reference_id'])}|{_clean(l['source_id'])}|{l['label']}"
                 for l in grouped[tid]]
        blob = ('\n'.join(lines) + '\n').encode('utf-8')
        lookup.append(f'{tid}|{offset}|{len(lines)}')
        body.append(blob)
        offset += len(blob)
    (out_dir / 'REF_PAYLOAD.IDX').write_bytes(head + b''.join(body))
    (out_dir / 'REF_LOOKUP.IDX').write_bytes(('#LEXMACHINA|REF_LOOKUP|1\n#TARGET_ID|OFFSET|QUANTIDADE\n' + '\n'.join(lookup) + '\n').encode('utf-8'))
    return {p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
            for p in (j, out_dir / 'REF_LOOKUP.IDX', out_dir / 'REF_PAYLOAD.IDX')}


def get_references(target_id, export_doc, include_historical=False):
    """Valid links of one target (default: hides HISTORICAL_HIDDEN_BY_DEFAULT)."""
    ok, err = T.validate_target_id(target_id)
    if not ok:
        raise EngineError('LOOKUP_INVALID_TARGET_ID', f'{target_id}: {err}')
    links = export_doc['references'].get(target_id, [])
    return [l for l in links if include_historical or l['visibility'] != 'HISTORICAL_HIDDEN_BY_DEFAULT']


def lookup_idx(target_id, lookup_path, payload_path):
    """Firmware-style lookup: binary search in REF_LOOKUP.IDX, then read `count` lines at `offset` in REF_PAYLOAD.IDX."""
    rows = [l.split('|') for l in Path(lookup_path).read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    lo, hi = 0, len(rows) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if rows[mid][0] == target_id:
            off, n = int(rows[mid][1]), int(rows[mid][2])
            with open(payload_path, 'rb') as fh:
                fh.seek(off)
                return [fh.readline().decode('utf-8').rstrip('\n').split('|') for _ in range(n)]
        if rows[mid][0] < target_id:
            lo = mid + 1
        else:
            hi = mid - 1
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('--norm', default=None, help='norm id from engine_config.json (default: every configured norm)')
    ap.add_argument('--config', default=str(HERE / 'engine_config.json'))
    a = ap.parse_args()
    reg = TargetRegistry(a.config)
    for norm in ([a.norm] if a.norm else sorted(reg.cfg['norms'])):
        links = build_links(norm, reg)
        files = export(norm, links, a.out_dir)
        print(json.dumps(dict(norm=norm, links=len(links), files=files), indent=1))


if __name__ == '__main__':
    main()
