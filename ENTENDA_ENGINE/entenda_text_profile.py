"""Text profiles of a norm for ENTENDA: the current text of chosen namespaces read from the approved official runtime, deterministic.

Why: entenda_config.json reads the ADCT from the legacy multi-version structural source (cf.txt), so every ADCT target is
UNKNOWN_VALIDITY and its text may be an old wording (ADCT art. 2: "7 de setembro de 1993" in cf.txt, "21 de abril de 1993" in the
official monovigente compilation). The Lei Seca of the device (DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt, built by
updater/exportar_cf88_runtime.py from the locked Senado sources) already contains the ADCT, and it is segmented by the approved
parser in strict mode (DEVICE_INTEGRATION/tools/runtime_targets.py). The default ENTENDA reader (entenda_engine.NormContext) parses
text sources with the non-strict parser, which misreads that runtime (hyperlinked cross-references on their own lines become
article/namespace headers). Shared modules are hash-pinned by the Batch06/Macro07 manifests, so nothing is changed in them.

A profile is a full, generated ENTENDA config for the norm (same limits, corpus, exports) whose namespaces listed in the profile take
structure, status and text from the runtime:
  TARGET_INDEX.json   the norm's target index: other namespaces byte-for-byte as in the configured index (same entries, same order);
                      each profiled namespace replaced by the strict runtime index of that namespace, plus the targets that exist only
                      in the legacy structural source (kept as HISTORICAL_ONLY rows, so the selection report records their exclusion)
  TARGET_STATUS.json  other namespaces as configured; profiled namespaces: CURRENT (present in the official monovigente runtime),
                      revoked_marker for "(Revogado)/(Suprimido)" texts (runtime_targets.runtime_status), STRUCTURAL for
                      namespace/article units, HISTORICAL_ONLY for legacy-only targets (with the legacy-vs-runtime diff evidence)
  RUNTIME_TEXT.txt    ENTENDA reading of the runtime: one line per device, canonical label + the device text exactly as the
                      strict parser reads it from the runtime (no word added, removed or changed). It is NOT the Lei Seca; the build
                      fails closed unless the default ENTENDA reader, applied to it, returns for every target exactly the strict runtime
                      text (ROUND_TRIP) and the runtime sha256 matches its provenance
  entenda_config.json the profile config (paths of the three files above; everything else copied from the base config)
  PROFILE_MANIFEST.json sources and sha256, parser options, counts, round-trip evidence
Usage: python entenda_text_profile.py [PROFILE_ID ...] [--check]   (profiles: editorial/TEXT_PROFILES.json)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(REPO / 'DEVICE_INTEGRATION/tools'))
import entenda_engine as E  # noqa: E402
import runtime_targets as RT  # noqa: E402
import structure_parser as SP  # noqa: E402
import target_id as T  # noqa: E402

PROFILES = HERE / 'editorial/TEXT_PROFILES.json'
ROMAN_RE = re.compile(r'^[IVXLCDM]+(?:-[A-Z])?$')


class ProfileError(RuntimeError):
    pass


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _json_bytes(doc):
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def load_profiles(path=PROFILES):
    return json.loads(Path(path).read_text(encoding='utf-8'))['profiles']


def _ordinal(num):
    """'1' -> '1º' (1 to 9 take the ordinal sign in the constitutional style), '10' -> '10.'; '18-A' -> '18-A.'."""
    base, _, suf = num.partition('-')
    if suf:
        return f"{base}{'º' if base.isdigit() and int(base) < 10 else ''}-{suf}."
    return f'{base}º' if base.isdigit() and int(base) < 10 else f'{base}.'


def label(t):
    """Canonical heading of a device, from its target id (the grammar of target_id.py), so that the default parser reads it back."""
    last = t['target_id'].split(':')[-1]
    k = t['kind']
    if k == 'CAPUT':
        return f"Art. {_ordinal(t['article'])}"
    if k == 'PARAGRAFO_UNICO':
        return 'Parágrafo único.'
    if k == 'PARAGRAFO':
        return f"§ {_ordinal(last.split('.', 1)[1])}"
    if k == 'INCISO':
        num = last.split('.', 1)[1]
        if not ROMAN_RE.match(num):
            raise ProfileError(f'INCISO_LABEL {t["target_id"]}')
        return f'{num} -'
    if k == 'ALINEA':
        return f"{last.split('.', 1)[1]})"
    raise ProfileError(f'NO_LABEL {t["target_id"]} {k}')


def strict_parse(runtime_bytes, norma, parser):
    targets, anomalies, _ = SP.parse_structure(runtime_bytes.decode('utf-8-sig'), norma, end_markers=tuple(parser['end_markers']),
                                               article_case_sensitive=parser['article_case_sensitive'], preview_len=10 ** 7)
    bad = [a for a in anomalies if a['code'] != 'CLOSING_MARKER']
    if bad:
        raise ProfileError(f'RUNTIME_PARSER_ANOMALIES {bad[:5]}')
    # canonical position = last occurrence (line_start), as in the runtime target map: a repeated label (e.g. a hyperlink fragment that
    # starts with "§ 6º" inside the previous paragraph) keeps its text and children at the real heading, never at the fragment
    return sorted(targets, key=lambda t: t['line_start'])


def render_runtime(parsed, reg):
    """The whole runtime, one line per device: canonical label + strict text, namespace titles where the runtime has them. Articles are
    rendered through their caput line. The root norm must be present (the parser requires it), so every namespace is rendered; the
    profile config reads only the profiled namespaces from this file."""
    lines = []
    for t in parsed:
        if t['kind'] == 'NAMESPACE':
            lines.append(reg.sub[t['namespace']]['source_marker'])
            continue
        if t['kind'] in ('NORMA', 'ARTIGO'):
            continue
        text = E.norm_text(t['preview'] or '')
        if not text:
            raise ProfileError(f'DEVICE_WITHOUT_TEXT {t["target_id"]}')
        lines.append(f'{label(t)} {text}')
    return '\n'.join(lines) + '\n'


def _merge_legacy_only(runtime_rows, legacy_ns, runtime_ids):
    """Runtime order as backbone; each legacy-only target is placed right after the target that precedes it in the legacy order
    (already placed), so the legacy sequence is kept around it. Deterministic."""
    out = list(runtime_rows)
    prev = None
    for t in legacy_ns:
        tid = t['target_id']
        if tid not in runtime_ids:
            i = next(j for j, x in enumerate(out) if x['target_id'] == prev) + 1 if prev is not None else 0
            out.insert(i, dict(t, profile_origin='LEGACY_STRUCTURAL_ONLY'))
        prev = tid
    return out


def build(profile_id, write=True, base=REPO):
    p = load_profiles()[profile_id]
    base = Path(base)
    cfg = json.loads((base / p['base_config']).read_text(encoding='utf-8'))
    norma = p['norma_id']
    ncfg = cfg['norms'][norma]
    rt_path = base / p['runtime']
    raw = rt_path.read_bytes()
    prov = json.loads((base / p['runtime_provenance']).read_text(encoding='utf-8'))
    if _sha(raw) != p['runtime_sha256'] or prov['sha256'] != p['runtime_sha256']:
        raise ProfileError('RUNTIME_SHA256_MISMATCH')
    legacy = json.loads((base / ncfg['target_index']).read_text(encoding='utf-8'))
    legacy_status = json.loads((base / ncfg['target_status']).read_text(encoding='utf-8'))
    parsed = strict_parse(raw, norma, p['parser'])
    reg = T.registry()
    ids = [t['target_id'] for t in parsed]
    if len(ids) != len(set(ids)):
        raise ProfileError('RUNTIME_TARGET_ID_DUPLICATES')
    rt_index = {t['target_id']: t for t in parsed}
    rstatus = RT.runtime_status(dict(targets=[dict(t, preview=t['preview']) for t in parsed]))
    out_dir = base / p['out_dir']
    targets, status, ns_counts = [], {}, {}
    legacy_by_ns = {}
    for t in legacy['targets']:
        legacy_by_ns.setdefault(t['namespace'], []).append(t)
    diff_rows, _ = RT.classify(legacy, dict(targets=[dict(t, preview=E.norm_text(t['preview'] or '')[:100] or None) for t in parsed]),
                               raw.decode('utf-8'), lambda tid: legacy_status['targets'].get(tid, {}).get('status', 'UNKNOWN_VALIDITY'),
                               RT.load_reviewed())
    diff = {r['target_id']: r for r in diff_rows}
    for ns in dict.fromkeys(t['namespace'] for t in legacy['targets']):
        if ns not in p['namespaces']:
            for t in legacy_by_ns[ns]:
                targets.append(t)
                if t['target_id'] in legacy_status['targets']:
                    status[t['target_id']] = legacy_status['targets'][t['target_id']]
            continue
        rns = [t for t in parsed if t['namespace'] == ns]
        if not rns:
            raise ProfileError(f'NAMESPACE_NOT_IN_RUNTIME {ns}')
        rows = []
        for t in rns:
            tid = t['target_id']
            full = E.norm_text(t['preview'] or '')
            row = {k: t[k] for k in ('target_id', 'parent_id', 'kind', 'namespace', 'norma_id', 'article', 'paragraph', 'inciso', 'alinea',
                                     'occurrences', 'line_start', 'repeated_label_occurrences')}
            row.update(preview=full[:100] or None, text_sha256_current=t.get('text_sha256_current'), profile_origin='OFFICIAL_RUNTIME')
            rows.append(row)
            if t['kind'] in ('NORMA', 'NAMESPACE', 'ARTIGO'):
                status[tid] = dict(status='STRUCTURAL', reason='estrutura (norma, namespace ou artigo-unidade)', revoked_marker=False,
                                   present_in_operational_text=True, profile_source='OFFICIAL_RUNTIME')
            else:
                rev = rstatus[tid] == 'REVOKED'
                status[tid] = dict(status='CURRENT', reason='rotulo presente na compilacao monovigente oficial (runtime da Lei Seca)'
                                   + (' com marca de revogacao' if rev else ''), revoked_marker=rev, present_in_operational_text=True,
                                   profile_source='OFFICIAL_RUNTIME')
        legacy_only = [t for t in legacy_by_ns.get(ns, []) if t['target_id'] not in rt_index]
        for t in legacy_only:
            if t['parent_id'] not in rt_index and t['parent_id'] not in {x['target_id'] for x in legacy_only}:
                raise ProfileError(f"LEGACY_ONLY_PARENT_MISSING {t['target_id']}")
            d = diff.get(t['target_id'], {})
            if d.get('classification') in RT.BLOCKING:
                raise ProfileError(f"LEGACY_VS_RUNTIME_BLOCKING {t['target_id']} {d}")
            status[t['target_id']] = dict(status='HISTORICAL_ONLY', reason='rotulo ausente da compilacao monovigente oficial; existe so na fonte '
                                          f"estrutural legada ({d.get('classification', 'SEM_CLASSIFICACAO')}: {d.get('evidence', '')})",
                                          revoked_marker=False, present_in_operational_text=False, profile_source='LEGACY_STRUCTURAL_ONLY')
        merged = _merge_legacy_only(rows, legacy_by_ns.get(ns, []), set(rt_index))
        targets += merged
        ns_counts[ns] = dict(runtime_targets=len(rows), legacy_targets=len(legacy_by_ns.get(ns, [])), legacy_only_historical=len(legacy_only),
                             runtime_only=sorted(t['target_id'] for t in rows if t['target_id'] not in {x['target_id'] for x in legacy_by_ns.get(ns, [])}),
                             text_file=f"{p['out_dir']}/RUNTIME_TEXT.txt")
    tids = [t['target_id'] for t in targets]
    if len(tids) != len(set(tids)):
        raise ProfileError('PROFILE_TARGET_ID_DUPLICATES')
    for t in targets:
        if t['parent_id'] and t['parent_id'] not in set(tids):
            raise ProfileError(f"PARENT_MISSING {t['target_id']}")
    index = dict(schema_version=1, norma_id=norma, profile=profile_id, grammar=legacy['grammar'],
                 sources=dict(legacy_index=ncfg['target_index'], legacy_index_sha256=legacy['target_index_sha256'],
                              runtime=p['runtime'], runtime_sha256=p['runtime_sha256'], parser=p['parser']),
                 total_targets=len(targets), target_index_sha256=_sha('\n'.join(sorted(tids)).encode('ascii')), targets=targets)
    st_doc = dict(schema_version=1, profile=profile_id, index_sha256=index['target_index_sha256'],
                  counts=dict(sorted({s: sum(1 for v in status.values() if v['status'] == s) for s in {v['status'] for v in status.values()}}.items())),
                  targets=dict(sorted(status.items(), key=lambda kv: tids.index(kv[0]) if kv[0] in tids else -1)))
    pcfg = json.loads(json.dumps(cfg))
    pcfg['note'] = (f"GERADO por ENTENDA_ENGINE/entenda_text_profile.py (perfil {profile_id}); nao editar. Igual a {p['base_config']} exceto: "
                    f"indice, status e fonte de texto dos namespaces {', '.join(p['namespaces'])} lidos do runtime oficial ({p['runtime']}).")
    pn = pcfg['norms'][norma]
    pn['target_index'] = f"{p['out_dir']}/TARGET_INDEX.json"
    pn['target_status'] = f"{p['out_dir']}/TARGET_STATUS.json"
    pn['text_sources'] = [s for s in pn['text_sources'] if not set(s['namespaces']) & set(p['namespaces'])] + [
        dict(namespaces=list(p['namespaces']), path=f"{p['out_dir']}/RUNTIME_TEXT.txt", role='OFFICIAL_RUNTIME_PROFILE_TEXT',
             note=f"leitura ENTENDA do runtime oficial {p['runtime']} (sha256 {p['runtime_sha256'][:12]}...), um dispositivo por linha; "
                  'texto de cada dispositivo identico ao do parser estrito (PROFILE_MANIFEST.json, ROUND_TRIP); so os namespaces listados sao lidos daqui')]
    files = {'TARGET_INDEX.json': _json_bytes(index), 'TARGET_STATUS.json': _json_bytes(st_doc), 'entenda_config.json': _json_bytes(pcfg)}
    files['RUNTIME_TEXT.txt'] = render_runtime(parsed, reg).encode('utf-8')
    if write:
        out_dir.mkdir(parents=True, exist_ok=True)
        for n, b in files.items():
            (out_dir / n).write_bytes(b)
    rt = round_trip(profile_id, parsed, p, base) if write else None
    manifest = dict(schema_version=1, profile=profile_id, norma_id=norma, builder='ENTENDA_ENGINE/entenda_text_profile.py',
                    builder_sha256_lf=_sha((HERE / 'entenda_text_profile.py').read_bytes().replace(b'\r\n', b'\n')),
                    base_config=p['base_config'], runtime=p['runtime'], runtime_sha256=p['runtime_sha256'], runtime_provenance=p['runtime_provenance'],
                    runtime_composition=prov.get('composition'), parser=p['parser'], namespaces=p['namespaces'], counts=ns_counts,
                    status_counts=st_doc['counts'], round_trip=rt, files={n: _sha(b) for n, b in sorted(files.items())},
                    policy='Nenhuma palavra da lei e editada. O texto de cada dispositivo e o do runtime oficial lido pelo parser estrito aprovado. '
                           'O perfil nao altera o indice, o status nem a config globais; e usado por lotes que o declaram (MACRO_SPEC.entenda_config).')
    if write:
        (out_dir / 'PROFILE_MANIFEST.json').write_bytes(_json_bytes(manifest))
    return manifest, files


def round_trip(profile_id, parsed, p, base=REPO):
    """Default ENTENDA reader on the profile == strict runtime text for every profiled target; other namespaces == default config."""
    pcfg = base / p['out_dir'] / 'entenda_config.json'
    ctx = E.NormContext(p['norma_id'], pcfg, base=base)
    strict = {t['target_id']: E.norm_text(t['preview'] or '') for t in parsed if t['namespace'] in p['namespaces']}
    bad = [tid for tid, txt in strict.items() if txt and ctx.text.get(tid) != txt]
    extra = sorted(t for t in ctx.text if t.split(':')[0] in p['namespaces'] and t not in strict)
    dflt = E.NormContext(p['norma_id'], base / p['base_config'], base=base)
    other = [t for t in dflt.text if t.split(':')[0] not in p['namespaces'] and dflt.text[t] != ctx.text.get(t)]
    status_other = [t for t in dflt.targets if t.split(':')[0] not in p['namespaces'] and dflt.effective_status(t) != ctx.effective_status(t)]
    res = dict(profiled_targets_with_text=sum(1 for v in strict.values() if v), mismatched=bad[:20], mismatched_count=len(bad),
               extra_targets=extra[:20], other_namespaces_text_mismatch=len(other), other_namespaces_status_mismatch=len(status_other),
               status='PASS' if not (bad or extra or other or status_other) else 'FAIL')
    if res['status'] != 'PASS':
        raise ProfileError(f'ROUND_TRIP_FAIL {json.dumps(res, ensure_ascii=False)[:800]}')
    return res


def check(profile_id, base=REPO):
    """Rebuild in memory and compare with the versioned files (byte-identical)."""
    p = load_profiles()[profile_id]
    _, files = build(profile_id, write=False, base=base)
    out = Path(base) / p['out_dir']
    return {n: (out / n).is_file() and (out / n).read_bytes() == b for n, b in files.items()}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ids = [a for a in sys.argv[1:] if not a.startswith('--')] or sorted(load_profiles())
    for pid in ids:
        if '--check' in sys.argv:
            print(pid, json.dumps(check(pid), indent=1))
        else:
            m, _ = build(pid)
            print(json.dumps({k: m[k] for k in ('profile', 'counts', 'status_counts', 'round_trip')}, ensure_ascii=False, indent=1))
