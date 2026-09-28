"""Read-only diagnostic: how many existing CF references map automatically to canonical target_ids.

Classes per reference:
  AUTO_SUBDIVISION         maps to an existing paragraph/inciso/alinea target (no rule needed)
  ARTICLE_LEVEL_NEEDS_RULE legacy article-level key (V2 'CF88:ART.N' carried the CAPUT text): a migration rule must
                           decide ARTIGO (unit) vs CAPUT; not auto-mapped
  AMBIGUOUS_V2_COLLISION   legacy key whose V2 text came from a different device collapsed by the old parser
                           (e.g. 'CF88:ART.40:PAR.4' stored the text of '§ 4º-C')
  NOT_FOUND / INVALID      converted id absent from the index / not convertible
Usage: python analyze_reference_coverage.py <CF88_TARGET_INDEX.json> <output.json>
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import target_id as T  # noqa: E402

V2 = REPO / 'LEX_MACHINA_REFERENCIAS_V2'
ART_ONLY = re.compile(r'^[A-Z0-9]+:ART\.[0-9A-Z-]+$')


def norm(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def main(index_path, out_path):
    idx = json.loads(Path(index_path).read_text(encoding='utf-8'))
    tg = {t['target_id']: t for t in idx['targets']}
    v2dev = json.loads((REPO / 'CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json').read_text(encoding='utf-8'))['dispositivos']
    # V2 keys whose stored text is not the text of that label in the source (collapsed suffix siblings)
    collided = set()
    for d in v2dev:
        k = d['chave_dispositivo']
        tid = k + ':CAPUT' if ART_ONLY.match(k) else k
        cur = tg.get(tid)
        sib = [x for x in tg if x.startswith(tid + '-')]
        if cur and sib and hashlib.sha256(norm(d['texto']).encode()).hexdigest() != cur['text_sha256_current']:
            collided.add(k)

    unmarked = set()
    for a in idx['anomalies']:
        if a['code'] == 'POSSIBLE_INCISO_WITHOUT_SEPARATOR' and a.get('context'):
            ctx = a['context']
            base = T.parent_target_id(ctx) if ':INC.' in ctx else ctx
            unmarked.add((base, a['label']))

    def classify_legacy(key, v2_text_based):
        ok, err = T.validate_target_id(key)
        if not ok:
            return 'INVALID', None, err
        if v2_text_based and key in collided:
            return 'AMBIGUOUS_V2_COLLISION', key, None
        if ART_ONLY.match(key):
            return ('ARTICLE_LEVEL_NEEDS_RULE' if key in tg else 'NOT_FOUND'), key, None
        if key in tg:
            return 'AUTO_SUBDIVISION', key, None
        t = T.parse_target_id(key)
        par = T.parent_target_id(key)
        if t['inciso'] and not t['alinea'] and (par, t['inciso']) in unmarked:
            return 'NOT_FOUND_UNMARKED_INCISO_IN_SOURCE', key, None
        return 'NOT_FOUND_NO_SUCH_DEVICE', key, None

    datasets = {}

    def record(name, source, items, v2_text_based=False):
        c = collections.Counter()
        ex = collections.defaultdict(list)
        for raw, key_fn in items:
            try:
                key = key_fn()
                cls, tid, err = classify_legacy(key, v2_text_based)
            except T.TargetIdError as e:
                cls, tid, err = 'INVALID', None, e.code
            c[cls] += 1
            if len(ex[cls]) < 5:
                ex[cls].append(dict(raw=raw, target_id=tid, error=err))
        datasets[name] = dict(source=source, total=sum(c.values()), counts=dict(sorted(c.items())), examples=dict(ex))

    # 1-2. V2 release candidates (device_id)
    for rc, rel in (('V2_RC2_REFERENCES', '08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/REFERENCIAS_RC2.json'),
                    ('V2_RC1_REFERENCES', '08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/REFERENCIAS_RC1.json')):
        p = V2 / rel
        refs = json.loads(p.read_text(encoding='utf-8'))['references']
        record(rc, 'LEX_MACHINA_REFERENCIAS_V2/' + rel, [(r['device_id'], (lambda k=r['device_id']: k)) for r in refs], True)
    # 3. every distinct device_id mentioned in V2 JSON artifacts (frozen history, schema inputs, benchmarks)
    ids = set()
    for p in V2.rglob('*.json'):
        if '09_CATALOGO_EXPANSAO_200' in p.parts:
            continue
        ids.update(re.findall(r'"device_id"\s*:\s*"([^"]+)"', p.read_text(encoding='utf-8', errors='ignore')))
    record('V2_ALL_DISTINCT_DEVICE_IDS', 'LEX_MACHINA_REFERENCIAS_V2/**/*.json (exceto 09_CATALOGO_EXPANSAO_200)',
           [(k, (lambda k=k: k)) for k in sorted(ids)], True)
    # 4. SD relations lookup (pipe fields)
    rel = REPO / 'LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/SD_PRONTO/99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX'
    rows = [l.split('|') for l in rel.read_text(encoding='utf-8-sig').splitlines() if l and not l.startswith('#')]
    record('SD_RELATIONS_REL_LOOKUP', str(rel.relative_to(REPO)).replace('\\', '/'),
           [('|'.join(r[:5]), (lambda r=r: T.from_pipe_fields(*r[:5]))) for r in rows])
    # 5-6. jurisprudence J4_6 (read-only from the relocation archive)
    jroot = Path(r'C:\LMA\p545e\20260928\LEX_MACHINA_JURIS_CF_J4_6\SD_JURIS_J4_TESTE\99_JURISPRUDENCIA_V2\05_INDICES_ESP32')
    if jroot.is_dir():
        rows = [l.split('|') for l in (jroot / 'JUR_LOOKUP.IDX').read_text(encoding='utf-8-sig').splitlines() if l and not l.startswith('#')]
        record('SD_JURIS_J4_6_JUR_LOOKUP', 'archive(read-only):LEX_MACHINA_JURIS_CF_J4_6/.../JUR_LOOKUP.IDX',
               [('|'.join(r[:5]), (lambda r=r: T.from_pipe_fields(*r[:5]))) for r in rows])
        jids = [l.split('|')[0] for l in (jroot / 'JURISPRUDENCIA.IDX').read_text(encoding='utf-8-sig').splitlines() if l and not l.startswith('#')]
        record('SD_JURIS_J4_6_IDS', 'archive(read-only):LEX_MACHINA_JURIS_CF_J4_6/.../JURISPRUDENCIA.IDX (sufixo norma:art:par:inc:ali)',
               [(j, (lambda j=j: T.from_colon_fields(':'.join(j.split(':')[3:])))) for j in jids])
    total = collections.Counter()
    for d in datasets.values():
        total.update(d['counts'])
    out = dict(index_sha256=idx['target_index_sha256'], v2_collided_keys=sorted(collided), v2_collided_count=len(collided),
               datasets=datasets, totals=dict(sorted(total.items())), total_references=sum(total.values()))
    Path(out_path).write_bytes((json.dumps(out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps(dict(v2_collided=sorted(collided), totals=out['totals'], per_dataset={k: v['counts'] for k, v in datasets.items()}), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
