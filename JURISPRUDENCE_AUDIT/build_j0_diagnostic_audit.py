"""J0 — diagnostic audit of the CF jurisprudence layer (READ-ONLY, host-only, deterministic, no network).

Reads (never writes):
  DEVICE (published bytes = physically approved baseline lex-device-v1-references4-physical-approved-2026-10-16):
    REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX, REF_LOOKUP.IDX
    .../10_TARGETS/CF88_TARGETS.IDX
    REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json (hashes of the legacy 99_JURISPRUDENCIA_V2 files on the card)
  ENGINE (device-ready export, structural order): LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_ready/CF88_REFERENCES_EXPORT.json
  CATALOG: LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json, CF88_QUARANTINE_RESOLUTION.json, CROSS_NORM_PENDING.json,
           CF88_LINK_EXCLUSIONS.json, CF88_TARGET_INDEX.json
  EDITORIAL ORIGIN (outside Git, protected archive, sha-pinned): C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4/{VINCULOS_EXPLICITOS,
           VINCULOS_REVISAO,RESUMO_J4}.json and LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/*.IDX
  BACKLOG: ENTENDA_ENGINE/derived/production_batch_*/JURISPRUDENCE_LINK_RECOMMENDATIONS.json (final version of each batch)
Writes: JURISPRUDENCE_AUDIT/J0_DIAGNOSTIC_AUDIT.json.  No legal merit is decided: flags are objective/structural (NEEDS_HUMAN_REVIEW).
Usage: python build_j0_diagnostic_audit.py [--check]
"""
import collections
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEV = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
POST = ROOT / 'REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
EXPORT = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_ready/CF88_REFERENCES_EXPORT.json'
D = ROOT / 'LEGAL_TARGET_ID/derived'
ARCH = Path('C:/LMA/p545e/20260928')
J4 = ARCH / 'LEX_MACHINA_JURIS_CF_J4'
J46 = ARCH / 'LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/05_INDICES_ESP32'
PIN = {  # protected archive inputs (sha256 of the bytes read)
    'J4/VINCULOS_EXPLICITOS.json': None, 'J4/VINCULOS_REVISAO.json': None, 'J4/RESUMO_J4.json': None,
    'J4_6/JURISPRUDENCIA.IDX': 'f85108baf4ee', 'J4_6/JUR_LOOKUP.IDX': '7931e28e7a05'}
BATCHES = ('production_batch_01_final', 'production_batch_02_final', 'production_batch_03_final', 'production_batch_04', 'production_batch_05',
           'production_batch_06', 'production_batch_07_macro', 'production_batch_08_macro')
OUT = HERE / 'J0_DIAGNOSTIC_AUDIT.json'
SEV_HIGH = {'LIKELY_OTHER_NORM_ARTICLE', 'ORPHAN_TARGET', 'NO_DETAIL_RECORD_IN_LEGACY_IDX', 'NO_CONTENT_FILE_ON_CARD', 'DUPLICATE_SAME_SOURCE_SAME_TARGET',
            'NO_J4_ORIGIN_RECORD', 'SOURCE_NOT_VERIFIABLE', 'IDENTIFIER_INCOMPLETE'}
SEV_MEDIUM = {'PARENT_CHILD_SAME_SOURCE'}
CF_MARK = re.compile(r'(constitui[cç][aã]o|\bCF\b|\bCF/88\b|carta (magna|federal|da rep)|constitucional)', re.I)
OTHER_NORM = re.compile(r'(\blei\b|decreto|c[oó]digo|\bLC\b|\bCLT\b|\bCPC\b|\bCPP\b|\bCTN\b|regimento|resolu[cç][aã]o|portaria|medida provis[oó]ria|emenda constitucional|\bADCT\b|estatuto)', re.I)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def rows(p):
    return [l.split('|') for l in Path(p).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]


def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()).strip()


def target_level(tid):
    if tid.startswith('ADCT:'):
        return 'ADCT'
    last = tid.split(':')[-1]
    return {'CAPUT': 'CAPUT'}.get(last, 'ALINEA' if last.startswith('ALI') else 'INCISO' if last.startswith('INC') else
                                  'PARAGRAFO' if last.startswith('PAR') else 'ARTIGO')


def ancestors(tid, parent):
    out, p = [], parent.get(tid)
    while p:
        out.append(p)
        p = parent.get(p)
    if tid.endswith(':CAPUT'):                       # ART.n and ART.n:CAPUT are the device equivalence pair
        out.append(tid[:-len(':CAPUT')])
    return out


OTHER_NORM_ARTICLE = r'art(?:igo)?s?\.?\s*{n}\s*(?:º|o|°)?(?:,\s*[^,;]{{0,40}})?\s*,?\s*d[aoe]s?\s+(?:lei|decreto|c[oó]digo|LC|CLT|CPC|CPP|CTN|regimento|resolu|portaria|medida provis|emenda|estatuto|ADCT)'


def other_norm_article(evidence, artigo):
    """Objective false-positive pattern (class of Tema 113 x art. 25): the matched excerpt names 'art. N' OF ANOTHER NORM, N = target article."""
    ref = (evidence or {}).get('referencia_detectada') or ''
    return bool(artigo) and re.search(OTHER_NORM_ARTICLE.format(n=re.escape(str(artigo))), ref, re.I) is not None


def norm_context(evidence):
    """Objective check of the literal citation: does the matched excerpt name the CF, another norm, or neither?"""
    ref = (evidence or {}).get('referencia_detectada') or ''
    if CF_MARK.search(ref) and not OTHER_NORM.search(ref):
        return 'CF_EXPLICIT'
    if CF_MARK.search(ref) and OTHER_NORM.search(ref):
        return 'CF_AND_OTHER_NORM_IN_SAME_CITATION'
    if OTHER_NORM.search(ref):
        return 'OTHER_NORM_ONLY'
    return 'NO_NORM_MARKER'


def audit():
    inputs = {}
    for k in PIN:
        p = (J4 / k.split('/', 1)[1]) if k.startswith('J4/') else (J46 / k.split('/', 1)[1])
        b = p.read_bytes()
        inputs[k] = dict(path=str(p).replace('\\', '/'), sha256=sha(b))
        if PIN[k] and not inputs[k]['sha256'].startswith(PIN[k]):
            raise SystemExit(f'ARCHIVE_INPUT_CHANGED {k}')
    for p in (DEV / '20_REFERENCES/REF_PAYLOAD.IDX', DEV / '20_REFERENCES/REF_LOOKUP.IDX', DEV / '10_TARGETS/CF88_TARGETS.IDX', EXPORT,
              D / 'CF88_REFERENCES_CANONICAL.json', D / 'CF88_LINK_EXCLUSIONS.json', D / 'CF88_QUARANTINE_RESOLUTION.json', D / 'CROSS_NORM_PENDING.json'):
        inputs[p.relative_to(ROOT).as_posix()] = dict(sha256=sha(p.read_bytes().replace(b'\r\n', b'\n')))

    # ---------------- device layer
    pay = rows(DEV / '20_REFERENCES/REF_PAYLOAD.IDX')
    tgt = {r[0]: r for r in rows(DEV / '10_TARGETS/CF88_TARGETS.IDX')}
    jur = [r for r in pay if r[1] == 'JURISPRUDENCE']
    vis = [r for r in jur if r[2] == 'CURRENT_VISIBLE']
    hidden = [r for r in jur if r[2] != 'CURRENT_VISIBLE']
    j_flag = {t for t, r in tgt.items() if r[3][2] == 'J'}
    vis_targets = {r[0] for r in vis}
    post = load(POST)['entries']
    card_jur = {k: v['sha256'] for k, v in post.items() if k.startswith('99_JURISPRUDENCIA_V2/')}
    legacy_idx = {r[0]: r for r in rows(J46 / 'JURISPRUDENCIA.IDX')}
    contents = {Path(k).stem for k in card_jur if '/03_CONTEUDO/' in k}
    device = dict(
        key='2 JURIS. (rodapé do leitor; lexV1FlagCamada flags[2]==J; tipo JURISPRUDENCE de REF_PAYLOAD; detalhe aberto pela chave do vínculo no '
            'JURISPRUDENCIA.IDX legado e no texto 99_JURISPRUDENCIA_V2/03_CONTEUDO/<ID>.TXT)',
        ref_payload_rows=len(jur), visible=len(vis), hidden_historical=len(hidden),
        legacy_card_files=len(card_jur), legacy_content_files=len(contents),
        legacy_jurisprudencia_idx_on_card=card_jur.get('99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'),
        legacy_idx_equals_J4_6=card_jur.get('99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX') == inputs['J4_6/JURISPRUDENCIA.IDX']['sha256'],
        legacy_lookup_equals_J4_6=card_jur.get('99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX') == inputs['J4_6/JUR_LOOKUP.IDX']['sha256'],
        J_FLAGS=len(j_flag), J_FLAGS_WITHOUT_RELATION=len(j_flag - vis_targets), J_RELATIONS_WITHOUT_FLAG=len(vis_targets - j_flag),
        j_flags_without_relation=sorted(j_flag - vis_targets), j_relations_without_flag=sorted(vis_targets - j_flag),
        ref_lookup_rows_for_juris_targets=len(vis_targets & {r[0] for r in rows(DEV / '20_REFERENCES/REF_LOOKUP.IDX')}),
        firmware_list_limit='lexV1LerRegistrosChave → regs[LEXV1_REL_REGS_MAX=32] por chave (camadas 1/2); detalhe via JURISPRUDENCIA.IDX legado')

    # ---------------- editorial origin (J4)
    j4 = load(J4 / 'VINCULOS_EXPLICITOS.json')
    j4_by_key = {x['vinculo_id']: x for x in j4}
    rev = load(J4 / 'VINCULOS_REVISAO.json')
    resumo = load(J4 / 'RESUMO_J4.json')
    excl = load(D / 'CF88_LINK_EXCLUSIONS.json')['records']
    quar = load(D / 'CF88_QUARANTINE_RESOLUTION.json')['records']
    cross = load(D / 'CROSS_NORM_PENDING.json')['records']
    split_src = {q['original_record_id']: q for q in quar if q['klass'] == 'MIXED_RESOLVED_BY_SPLIT' and q['source_layer'] == 'SD_JURIS_J4_6_IDS'}
    exp = load(EXPORT)
    links = {l['reference_id']: l for ls in exp['references'].values() for l in ls if l['reference_type'] == 'JURISPRUDENCE'}
    idx = load(D / 'CF88_TARGET_INDEX.json')['targets']
    parent = {t['target_id']: t.get('parent_id') for t in idx}

    # ---------------- per-link inventory and structural checks
    inv, nhr = [], []
    by_target_source = collections.defaultdict(list)
    for r in vis:
        by_target_source[(r[0], r[5])].append(r[4])
    vis_by_source = collections.defaultdict(set)
    for r in vis:
        vis_by_source[r[5]].add(r[0])
    for r in jur:
        rid = r[4]
        key = rid.split(':', 1)[1].rsplit('@', 1)[0]
        l = links.get(rid, {})
        j = j4_by_key.get(key)
        prov = l.get('provenance', {})
        reasons = []
        if r[2] == 'CURRENT_VISIBLE':
            if len(by_target_source[(r[0], r[5])]) > 1:
                reasons.append('DUPLICATE_SAME_SOURCE_SAME_TARGET')
            anc = [a for a in ancestors(r[0], parent) if a in vis_by_source[r[5]]]
            if anc:
                reasons.append('PARENT_CHILD_SAME_SOURCE:' + ','.join(anc))
            if not all(prov.get(f) for f in ('tribunal', 'tipo', 'numero')) and not all(l.get('payload', {}).get(f) for f in ('tribunal', 'tipo', 'numero')):
                reasons.append('IDENTIFIER_INCOMPLETE')
            if key not in legacy_idx:
                reasons.append('NO_DETAIL_RECORD_IN_LEGACY_IDX')
            if f"STF_{r[5].split(':')[1]}_{r[5].split(':')[2]}" not in contents:
                reasons.append('NO_CONTENT_FILE_ON_CARD')
            if r[0] not in tgt:
                reasons.append('ORPHAN_TARGET')
            if not j:
                reasons.append('NO_J4_ORIGIN_RECORD')
            else:
                if other_norm_article(j.get('evidencia_vinculo'), j.get('origem_artigo')):
                    reasons.append('LIKELY_OTHER_NORM_ARTICLE')
                nc = norm_context(j.get('evidencia_vinculo'))
                if nc != 'CF_EXPLICIT':
                    reasons.append('NORM_CONTEXT_' + nc)
                if not (j.get('fonte_oficial') or {}).get('sha256_conteudo') or not (j.get('evidencia_vinculo') or {}).get('trecho'):
                    reasons.append('SOURCE_NOT_VERIFIABLE')
                if j.get('status_atual') not in ('tese_fixada', 'vigente'):
                    reasons.append('STATUS_' + str(j.get('status_atual')).upper())
            if l.get('migration') in ('KEPT_AS_ARTICLE',) and target_level(r[0]) == 'ARTIGO' and any(
                    t.get('parent_id') in (r[0], r[0] + ':CAPUT') for t in idx if t['target_id'].startswith(r[0] + ':')):
                reasons.append('BROAD_ARTICLE_TARGET_WITH_SUBDIVISIONS')
            if key in split_src:
                reasons.append('SPLIT_FROM_MIXED_CITATION' + (':WORDING_NOTE' if split_src[key].get('wording_note') else ''))
            if r[3] not in ('CURRENT', 'STRUCTURAL'):
                reasons.append('TARGET_STATUS_' + r[3])
        item = dict(target_id=r[0], target_level=target_level(r[0]), visibility=r[2], target_status=r[3], reference_id=rid, link_key=key,
                    source_id=r[5], label=r[6], tribunal=prov.get('tribunal'), tipo=prov.get('tipo'), numero=prov.get('numero'),
                    processo=(j or {}).get('processo_principal'), status_atual=(j or {}).get('status_atual'), migration=l.get('migration'),
                    origin='J4 VINCULOS_EXPLICITOS (citacao_literal, classe EXPLICITO)' if j else None,
                    origin_confidence=((j or {}).get('confianca') or {}).get('nivel'), human_review=((j or {}).get('revisao_manual') or {}).get('estado'),
                    norm_context=norm_context((j or {}).get('evidencia_vinculo')) if j else None, structural_flags=reasons)
        inv.append(item)
        if r[2] == 'CURRENT_VISIBLE' and reasons:
            sev = 'HIGH' if any(x.split(':')[0] in SEV_HIGH or x.startswith('TARGET_STATUS_') for x in reasons) else                 'MEDIUM' if any(x.split(':')[0] in SEV_MEDIUM or x.startswith('NORM_CONTEXT_') for x in reasons) else 'LOW'
            nhr.append(dict(reference_id=rid, target_id=r[0], source_id=r[5], severity=sev, reasons=reasons))

    # human decisions that exist for this layer
    human = dict(
        link_exclusions=[dict(reference_id=e['reference_id'], status=e['status']) for e in excl],
        j4_manual_review_states=dict(collections.Counter(x['revisao_manual']['estado'] for x in j4)),
        j4_structural_strong_in_review=[dict(id=x['id'], candidate=x['candidato'], motivo=x.get('motivo')) for x in rev],
        note='Nenhum dos vínculos publicados passou por revisão humana individual: J4 marca revisao_manual=nao_requerida (extração automática por '
             'citação literal). Decisões humanas existentes: 2 exclusões MATERIAL_MISMATCH (revisão do ENTENDA Batch04) e a revisão J2.5 de SV 28/SV 29 '
             '(ESTRUTURAL_FORTE), concluída sem promoção (REVISAO_SV_28_29.md); nenhuma decisão humana formal está aberta.')

    # ---------------- types and coverage
    types = collections.Counter(r[5].split(':')[1] for r in vis)
    lvl = collections.Counter(target_level(t) for t in sorted(vis_targets))
    art_with = {':'.join(t.split(':')[:2]) for t in vis_targets}
    per_target = collections.Counter(r[0] for r in vis)
    per_article = collections.Counter(':'.join(r[0].split(':')[:2]) for r in vis)

    # ---------------- backlog (ENTENDA recommendations, final version of each batch)
    recs = []
    for b in BATCHES:
        for x in load(ROOT / f'ENTENDA_ENGINE/derived/{b}/JURISPRUDENCE_LINK_RECOMMENDATIONS.json')['recommendations']:
            recs.append(dict(x, batch=b))
    linked_pairs = {(r[0], r[5]) for r in vis}
    groups = collections.OrderedDict()
    for x in recs:
        k = (x['target_id'], norm(x.get('desired_reference')))
        groups.setdefault(k, []).append(x)
    backlog = []
    for (t, dref), xs in groups.items():
        x = xs[-1]
        src = (x.get('local_identity_searched') or '')
        if x['status'] == 'MATERIAL_MISMATCH_EXCLUDED':
            cat = 'EXCLUDED_MATERIAL_DIVERGENCE'
        elif x['status'] == 'READY_TO_LINK' or x.get('already_linked_to_target') or (t, src) in linked_pairs:
            cat = 'ALREADY_LINKED'
        else:
            cat = 'NEEDS_EXTERNAL_INGESTION'
        backlog.append(dict(target_id=t, desired_reference=x.get('desired_reference'), purpose=(x.get('purpose') or '')[:300], category=cat,
                            occurrences=len(xs), batches=sorted({y['batch'] for y in xs}), local_identity_searched=src or None))
    pending = [b for b in backlog if b['category'] == 'NEEDS_EXTERNAL_INGESTION']
    # identifiers named in the recommendation text (objective; no merit)
    ident_re = re.compile(r'\b(ADI|ADC|ADPF|ADO|RE|ARE|MS|HC|RHC|MI|Rcl|AI|ACO|AP|Inq|Pet)\s*\d[\d.]*|\bTema\s*\d+|\bS[uú]mula\s+(Vinculante\s+)?\d+|\bSV\s*\d+', re.I)
    dup_desired = collections.Counter(norm(b['desired_reference']) for b in pending)
    for b in pending:
        text = f"{b['desired_reference']} {b['purpose']}"
        ids = sorted({m.group(0).strip() for m in ident_re.finditer(text)})
        b['named_identifiers'] = ids
        b['target_has_juris'] = any(k in vis_targets for k in (b['target_id'], b['target_id'] + ':CAPUT', b['target_id'].removesuffix(':CAPUT')))
        b['article_has_juris'] = ':'.join(b['target_id'].split(':')[:2]) in art_with
        score = (1 if ids else 0) + (1 if b['occurrences'] > 1 or dup_desired[norm(b['desired_reference'])] > 1 else 0) + (0 if b['article_has_juris'] else 1) \
            + (1 if b['desired_reference'] and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE' else 0)
        b['priority'] = 'HIGH' if score >= 3 else 'MEDIUM' if score == 2 else 'LOW'
        b['priority_basis'] = dict(named_identifier=bool(ids), recurrent=b['occurrences'] > 1 or dup_desired[norm(b['desired_reference'])] > 1,
                                   article_without_juris=not b['article_has_juris'],
                                   reference_described=bool(b['desired_reference'] and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE'))
    bl = dict(raw_recommendations=len(recs), unique=len(backlog), duplicate_recommendations=len(recs) - len(backlog),
              by_category=dict(collections.Counter(b['category'] for b in backlog)),
              pending_targets=len({b['target_id'] for b in pending}), pending_by_priority=dict(collections.Counter(b['priority'] for b in pending)),
              pending_by_batch=dict(collections.Counter(b['batches'][-1] for b in pending)), items=backlog)

    # ---------------- gaps (objective signals only; no external knowledge)
    cf_articles = {t['target_id'] for t in idx if t['kind'] == 'ARTIGO'}
    current_articles = {a for a in cf_articles if tgt.get(a, ['', '', 'CURRENT'])[2] == 'CURRENT' or tgt.get(a, ['', '', ''])[2] == 'STRUCTURAL'}
    rec_by_article = collections.Counter(':'.join(b['target_id'].split(':')[:2]) for b in pending)
    gaps = []
    for a in sorted(current_articles):
        if a in art_with:
            continue
        n = rec_by_article.get(a, 0)
        gaps.append(dict(article=a, pending_recommendations=n, classification='HIGH_VALUE_GAP' if n >= 2 else 'POTENTIAL_GAP' if n == 1 else 'NO_LOCAL_GAP_SIGNAL'))
    gap_counts = collections.Counter(g['classification'] for g in gaps)

    reason_counts = collections.Counter(r.split(':')[0] for n in nhr for r in n['reasons'])
    return dict(
        artifact='J0_DIAGNOSTIC_AUDIT', mode='READ_ONLY', inputs=inputs,
        authoritative=dict(device='REF_PAYLOAD/REF_LOOKUP (linhas JURISPRUDENCE) + CF88_TARGETS flag J do baseline físico 2026-10-16 + '
                                  '99_JURISPRUDENCIA_V2 legado do cartão (J4.6) para o detalhe',
                           editorial='C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4/VINCULOS_EXPLICITOS.json (296 vínculos EXPLICITO) + '
                                     'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json (overlay de exclusões) via CF88_REFERENCES_CANONICAL.json'),
        j4_summary=resumo, device=device, human_decisions=human,
        counts=dict(JURIS_RELATIONS=len(vis), hidden_historical=len(hidden), JURIS_TARGETS=len(vis_targets), distinct_sources=len({r[5] for r in vis}),
                    articles_with_juris=len(art_with), by_type=dict(types), by_target_level=dict(lvl),
                    max_links_per_target=per_target.most_common(5), max_links_per_article=per_article.most_common(10),
                    j4_explicit=len(j4), canonical_ids=263, excluded=len(excl), quarantine=dict(collections.Counter(q['klass'] for q in quar)),
                    cross_norm_pending=len(cross)),
        structural_audit=dict(NEEDS_HUMAN_REVIEW=len(nhr), by_severity=dict(collections.Counter(n['severity'] for n in nhr)), by_reason=dict(sorted(reason_counts.items())),
                              duplicates_same_target=sum(1 for v in by_target_source.values() if len(v) > 1),
                              orphans=sum('ORPHAN_TARGET' in n['reasons'] for n in nhr), items=nhr),
        backlog=bl, gaps=dict(counts=dict(gap_counts), articles_considered=len(current_articles), items=gaps),
        inventory=inv)


def render():
    return (json.dumps(audit(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = render()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    a = json.loads(b)
    print(json.dumps(dict(counts=a['counts'], device={k: v for k, v in a['device'].items() if not isinstance(v, list)},
                          structural=a['structural_audit']['by_reason'], severity=a['structural_audit']['by_severity'], NHR=a['structural_audit']['NEEDS_HUMAN_REVIEW'],
                          backlog={k: v for k, v in a['backlog'].items() if k != 'items'}, gaps=a['gaps']['counts']), ensure_ascii=False, indent=1))
