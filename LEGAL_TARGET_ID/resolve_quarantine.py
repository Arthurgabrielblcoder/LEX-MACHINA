"""CF-REF-A3: resolve the A2 quarantine only with literal evidence (derived output; A2 files untouched).

Classes:
  MIXED_RESOLVED_BY_SPLIT              literal citation names the device(s): one source reference -> 1..n target links
  MIXED_RESOLVED_VIA_CONSTITUENT_LINKS derived index row (lookup) whose constituent links are each resolved/pending;
                                       the index is rebuilt from links by the export, the row itself carries no link
  MIXED_STILL_AMBIGUOUS                citation not decomposable by the fail-closed grammar
  CROSS_NORM_REFERENCE_PENDING         citation belongs to another norm; preserved outside the CF catalog
  OTHER_QUARANTINE                     anything else
Usage: python resolve_quarantine.py <out_json> <cross_norm_json>
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import citation_parser as C  # noqa: E402
import reference_canonicalization as R  # noqa: E402
import target_id as T  # noqa: E402

JUR_FIELDS = ['id', 'tipo', 'tribunal', 'numero', 'status', 'titulo', 'identificador', 'fonte']


def main(out_path, cross_path):
    idx = json.loads((HERE / 'derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))
    tg = {t['target_id'] for t in idx['targets']}
    q = json.loads((HERE / 'derived/CF88_REFERENCES_QUARANTINE.json').read_text(encoding='utf-8'))['records']
    vinc = {v['vinculo_id']: v for v in json.loads(R.JUR_VINCULOS.read_text(encoding='utf-8'))}
    jur_lines = R.lines_at_offsets(R.JUR_IDX_DIR / 'JURISPRUDENCIA.IDX')
    out, cross, by_vinculo = [], [], {}

    def resolve_vinculo(vid, record_key):
        v = vinc[vid]
        ev = v['evidencia_vinculo']
        art = v['origem_artigo']
        parsed = C.parse_for_article(ev.get('referencia_detectada') or '', art)
        used = 'referencia_detectada'
        if parsed['status'] != 'OK':
            p2 = C.parse_for_article(ev.get('trecho') or '', art)
            if p2['status'] == 'OK':
                parsed, used = p2, 'trecho'
        res = dict(parsed=dict((k, v2) for k, v2 in parsed.items() if k != 'hits'), evidence_field=used,
                   citation=(ev.get(used) or '')[:400])
        if parsed['status'] == 'OK' and parsed['norm'] in ('CF', 'ADCT'):
            ns = 'ADCT' if parsed['norm'] == 'ADCT' else 'CF88'
            try:
                targets = C.to_targets(ns, T.normalize_number_label(art), parsed, T.format_target_id)
            except T.TargetIdError as e:
                return dict(res, klass='MIXED_STILL_AMBIGUOUS', reason='TARGET_FORMAT_ERROR:' + e.code)
            missing = [t for t in targets if t not in tg]
            if missing:
                return dict(res, klass='MIXED_STILL_AMBIGUOUS', reason='SPLIT_TARGET_NOT_IN_INDEX', candidate_targets=targets)
            note = 'CITES_PRIOR_WORDING' if re.search(r'reda[çc][ãa]o\s+(?:anterior|original)', ev.get('trecho') or '', re.I) else None
            return dict(res, klass='MIXED_RESOLVED_BY_SPLIT', targets=targets, fan_out=len(targets), wording_note=note,
                        reason='LITERAL_CITATION_NAMES_DEVICES')
        if parsed.get('norm') == 'OTHER':
            # the norm is determined as another one; device granularity (e.g. an alínea) is irrelevant for the CF catalog
            label = parsed['norm_label']
            if label and label.startswith('norma referida por'):
                trecho = ev.get('trecho') or ''
                cut = trecho.find('seu art')
                prev = list(re.finditer(r'(?:EC|Emenda Constitucional)\s*(?:n[ºo°.]\s*)?\d+/\d+', trecho[:cut if cut >= 0 else len(trecho)]))
                if prev:
                    label = prev[-1].group(0) + ' (antecedente de "seu art." no trecho)'
            return dict(res, klass='CROSS_NORM_REFERENCE_PENDING', cited_norm_label=label, cited_device_text=parsed.get('unit_text'),
                        reason='CITATION_BELONGS_TO_ANOTHER_NORM')
        # fallback for citations not parseable for the article: another norm explicitly named in the evidence
        m = C.OTHER_MARK.search(ev.get('trecho') or '')
        if m and not C.CF_ANY.search(ev.get('referencia_detectada') or ''):
            unit = re.search(r'[^;]{0,45}' + re.escape(m.group(0)), ev.get('trecho') or '')
            return dict(res, klass='CROSS_NORM_REFERENCE_PENDING', cited_norm_label=re.sub(r'\s+(?:e|do|da|de)$', '', m.group('label')),
                        cited_device_text=(unit.group(0).strip() if unit else None), reason='TRECHO_NAMES_ANOTHER_NORM')
        return dict(res, klass='MIXED_STILL_AMBIGUOUS', reason=parsed.get('reason', 'NOT_DECOMPOSABLE'))

    for x in q:
        ro = x['record_original']
        base = dict(original_source=ro['source_file'], original_record_id=ro['source_record_id'], source_layer=ro['source_layer'],
                    original_device_key=ro['original_device_key'], a2_classification=x['classification'], a2_reason=x['reason_code'])
        if ro['source_layer'] == 'SD_JURIS_J4_6_IDS':
            r = resolve_vinculo(ro['source_record_id'], ro['original_device_key'])
            raw = dict(zip(JUR_FIELDS, ro['raw'].split('|'))) if isinstance(ro['raw'], str) else {}
            rec = dict(base, **r, jurisprudence=raw)
            by_vinculo[ro['source_record_id']] = rec
        elif ro['source_layer'] == 'SD_JURIS_J4_6_JUR_LOOKUP':
            p = ro['raw'].split('|')
            off, qty = int(p[5]), int(p[6])
            pos = sorted(k for k in jur_lines if k >= off)
            constituents = [jur_lines[k].split('|')[0] for k in pos[:qty]]
            rec = dict(base, constituents=constituents)
        else:
            rec = dict(base, klass='OTHER_QUARANTINE', reason='LAYER_NOT_HANDLED')
        out.append(rec)
    # lookup rows: resolved through their constituent links (each constituent is either in the A2 catalog or resolved/pending here)
    cat = json.loads((HERE / 'derived/CF88_REFERENCES_CANONICAL.json').read_text(encoding='utf-8'))['records']
    in_catalog = {r['source_record_id'] for r in cat if r['source_layer'] == 'SD_JURIS_J4_6_IDS'}
    for rec in out:
        if rec['source_layer'] != 'SD_JURIS_J4_6_JUR_LOOKUP':
            continue
        states = {}
        for vid in rec['constituents']:
            states[vid] = 'IN_A2_CATALOG' if vid in in_catalog else by_vinculo.get(vid, {}).get('klass', 'UNKNOWN')
        rec['constituent_states'] = states
        if any(s in ('UNKNOWN', 'MIXED_STILL_AMBIGUOUS', 'OTHER_QUARANTINE') for s in states.values()):
            rec.update(klass='MIXED_STILL_AMBIGUOUS', reason='CONSTITUENT_UNRESOLVED')
        elif all(s == 'CROSS_NORM_REFERENCE_PENDING' for s in states.values()):
            rec.update(klass='CROSS_NORM_REFERENCE_PENDING', reason='DERIVED_INDEX_ROW_OF_CROSS_NORM_LINKS',
                       cited_norm_label='; '.join(sorted({by_vinculo[v].get('cited_norm_label') for v in states})), cited_device_text=None)
        else:
            rec.update(klass='MIXED_RESOLVED_VIA_CONSTITUENT_LINKS' if rec['a2_classification'] == 'ARTICLE_VS_CAPUT_RESOLVABLE' else 'CROSS_NORM_REFERENCE_PENDING',
                       reason='DERIVED_INDEX_ROW_REBUILT_FROM_LINKS')
    for rec in out:
        if rec['klass'] == 'CROSS_NORM_REFERENCE_PENDING':
            cross.append(dict(original_source=rec['original_source'], original_record_id=rec['original_record_id'], source_layer=rec['source_layer'],
                              original_device_key=rec['original_device_key'], cited_norm_label=rec.get('cited_norm_label'),
                              cited_device_text=rec.get('cited_device_text'), citation=rec.get('citation'), reason=rec['reason'],
                              wrongly_attached_to=rec['original_device_key'], target_norm_canonicalized=False,
                              note='Preservado: pertence a outra norma; sera mapeado quando a norma citada for canonicalizada.'))
    counts = {}
    for rec in out:
        counts[rec['klass']] = counts.get(rec['klass'], 0) + 1
    doc = dict(schema_version=1, source='LEGAL_TARGET_ID/derived/CF88_REFERENCES_QUARANTINE.json', total=len(out), counts=dict(sorted(counts.items())),
               fan_out_links=sum(r.get('fan_out', 0) for r in out), records=out)
    Path(out_path).write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    Path(cross_path).write_bytes((json.dumps(dict(schema_version=1, scope='referencias a outras normas encontradas no acervo da CF; nao entram no catalogo da CF',
                                                   total=len(cross), records=cross), ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps(dict(total=len(out), counts=doc['counts'], fan_out_links=doc['fan_out_links'], cross_norm=len(cross)), indent=1))
    for r in out:
        if r['source_layer'] == 'SD_JURIS_J4_6_IDS':
            print(' ', r['original_record_id'], r['klass'], r.get('targets') or r.get('cited_norm_label') or r.get('reason'))
    return doc


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
