"""MARIA2006_SOURCE_REPAIR: rebuild the operational TXT of Lei 11.340/2006 from the OFFICIAL source bytes, index it with the approved
full-corpus pipeline and stage a mini-deploy (nothing is written to the SD card here).

Authority = the Planalto page archived in source_evidence/MARIA2006/ (raw bytes + provenance: URL, HTTP status, Content-Type,
Last-Modified, ETag, SHA-256). The TXT is produced ONLY by the Updater backend (updater/main.py): validar_resposta_fonte ->
candidato_mestre_de_bytes (encoding detection, extraction, fail-closed checks, identity of the act) -> _montar_conteudo_mestre ->
_validar_conteudo_gravado_mestre. The header date is fixed to the download date, so the same bytes rebuild the same TXT.
The corrupted card file is used only as a DIAGNOSTIC (never as source of truth).

Outputs (staging_maria2006_source_repair/):
  SD/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt          REPLACE (same path as on the card)
  SD/99_LEX_V1/10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX    ADD
  SD/99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX      REPLACE (71 -> 72 entries)
  _host/full_corpus/   complete full-corpus regeneration (72 indexes + catalog + manifest), previous = approved full-corpus staging
  _host/MARIA2006_REPAIR_MANIFEST.json                     deploy plan data, hashes, audits
Usage: python tools/repair_maria2006_source.py [--out DIR]
"""
import argparse
import bisect
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import article_index_corpus as C  # noqa: E402
import build_article_search_index as AI  # noqa: E402
import structure_parser as SP  # noqa: E402

NORMA = 'MARIA2006'
EVIDENCE = DI / 'source_evidence/MARIA2006'
RAW = EVIDENCE / 'l11340_planalto_20261004.htm'
PROVENANCE = EVIDENCE / 'l11340_planalto_20261004.provenance.json'
CORPUS = DI / 'backups/sd_20260929T163407Z/data'                    # host copy of the card (byte-identical to the physical SD)
PHYSICAL = DI / 'backups/full_corpus_physical_deploy_20261003/sd_manifest_post_full.json'
APPROVED_FULL = DI / 'staging_article_indexes_full_corpus_candidate'  # physically approved full-corpus staging (71 + catalog)
OUT = DI / 'staging_maria2006_source_repair'
ATUALIZADO_EM = '04/10/2026 01:31'                                    # download date (provenance fetched_at, -03:00)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def updater():
    import importlib.util
    sys.path.insert(0, str(ROOT / 'updater'))
    spec = importlib.util.spec_from_file_location('lex_updater_main_repair', ROOT / 'updater/main.py')
    U = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(U)
    U.ARQUIVO_CATALOGO_MESTRE = C.CATALOG_JSON
    return U


def build_txt(U, item, raw, prov, local_text):
    """Official bytes -> operational TXT (str), through the Updater backend only."""
    if sha(raw) != prov['sha256'] or len(raw) != prov['bytes']:
        raise SystemExit('EVIDENCE_HASH_MISMATCH')
    U.validar_resposta_fonte(prov['source_url'], prov['final_url'], prov['http_status'], prov['content_type'], raw)
    cand = U.candidato_mestre_de_bytes(item, raw, dict(sha256=prov['sha256'], bytes=prov['bytes']), texto_local=local_text)
    conteudo = U._montar_conteudo_mestre(item, U.normalizar_texto(cand['texto']), cand['codificacao'], cand['fonte_nome'], cand['url_fonte'],
                                         cand['metodo'], atualizado_em=ATUALIZADO_EM)
    U._validar_conteudo_gravado_mestre(item, conteudo)
    return conteudo, cand


def diagnose_corrupted(corrupt_text, new_body):
    """Diagnostic only. Every non-empty line of the new body is MATCHABLE_TEXT when its characters (whitespace removed) occur in the
    corrupted file with whitespace removed (the UTF-16 NULs became spaces), else MISSING_TEXT. HTML_NOISE = markup characters in the
    corrupted body; ENCODING_CORRUPTION = spaced-letter runs + the mis-decoded BOM."""
    body = corrupt_text.split('========================================\n\n', 1)[-1]
    flat = re.sub(r'\s+', '', body)
    lines = [l for l in new_body.splitlines() if l.strip()]
    matchable = [l for l in lines if re.sub(r'\s+', '', l) in flat]
    tags = re.findall(r'<[^>]{0,400}>', body)
    return dict(
        corrupted_body_chars=len(body), corrupted_has_bom_mojibake=body.lstrip().startswith('ÿþ'),
        HTML_NOISE_chars=sum(len(t) for t in tags), HTML_NOISE_tags=len(tags),
        ENCODING_CORRUPTION_spaced_runs=len(re.findall(r'(?:\b\w \b){12}', body)),
        new_lines=len(lines), MATCHABLE_TEXT_lines=len(matchable), MISSING_TEXT_lines=len(lines) - len(matchable),
        missing_examples=[l[:80] for l in lines if l not in matchable][:5])


def audit_index(blob, data):
    """100% of the records: inside the file, at a line start, the line (joined like the parser) is a structural heading of exactly
    that key, never a remission; collective 'Arts. X a Y' ranges are not indexed; oracle equivalence."""
    ai = AI.ArticleIndex(blob, data)
    starts = AI.line_starts(data)
    txt = data.decode('utf-8')
    lines = [txt.encode('utf-8')[starts[i]:(starts[i + 1] - 1 if i + 1 < len(starts) else len(data))].decode('utf-8').strip()
             for i in range(len(starts))]
    bad = []
    for num, suf, ns, off, occ, _ in ai.recs:
        if off >= len(data) or (off and data[off - 1:off] != b'\n'):
            bad.append((num, suf, off, 'NOT_LINE_START'))
            continue
        k = bisect.bisect_right(starts, off) - 1
        s = lines[k]
        after = [l for l in lines[k + 1:k + 9] if l]
        if SP.ART_ALONE_RE_CS.match(s):
            s, after = 'Art. ' + (after[0] if after else ''), after[1:]
        s, used = SP.join_split_heading(SP.heading_variant(s), after[:2])
        m = SP.ART_RE_CS.match(s)
        if not m:
            bad.append((num, suf, off, 'NOT_A_HEADING'))
            continue
        key = (int(m.group(1).replace('.', '')), ord(m.group(2)) - 64 if m.group(2) else 0)
        if key != (num, suf):
            bad.append((num, suf, off, f'KEY_MISMATCH {key}'))
        prev = next((l for l in reversed(lines[:k]) if l), '')
        if SP.remission_heading(m, prev, after[used] if len(after) > used else ''):
            bad.append((num, suf, off, 'REMISSION'))
        if ns != 0 or ai.ns[ns] != NORMA:
            bad.append((num, suf, off, 'NAMESPACE'))
    ranges = [l for l in lines if C.RANGE_RE.match(l)]
    eq = C.equivalence(blob, data)
    keys = sorted({(r[0], r[1]) for r in ai.recs})
    return dict(records=len(ai.recs), audited=len(ai.recs), bad=bad, collective_ranges=ranges, oracle_equivalence=eq['ok'],
                oracle_keys=eq['keys'], distinct_keys=len(keys), suffix_records=sum(1 for r in ai.recs if r[1]),
                suffixed=[f'{n}-{chr(64 + s)}' for n, s in keys if s], max_article=max(k[0] for k in keys),
                repeated_keys=[f'{n}' + (f'-{chr(64 + s)}' if s else '') for n, s in keys if sum(1 for r in ai.recs if (r[0], r[1]) == (n, s)) > 1],
                source_bytes=ai.source_bytes, source_sha256=ai.source_sha256, namespaces=ai.ns)


def structure_summary(data):
    text = data.decode('utf-8')
    tops = SP.parse_structure(text, NORMA, article_case_sensitive=True, remission_guard=True, heading_variants=True)[0]
    kinds = {}
    for t in tops:
        kinds[t['kind']] = kinds.get(t['kind'], 0) + 1
    revog = sum(1 for t in tops if t['kind'] == 'ARTIGO' and False)
    body = text.split('========================================\n\n', 1)[-1]
    return dict(kinds=kinds, title_line=next((l for l in body.splitlines() if 'LEI Nº 11.340' in l), None),
                has_date='DE 7 DE AGOSTO DE 2006' in body, revoked_mentions=len(re.findall(r'\(Revogad[oa]', body)),
                vetoed_mentions=len(re.findall(r'\(VETADO\)', body)), redacao_dada=len(re.findall(r'Redação dada', body)),
                incluido=len(re.findall(r'Incluído pela', body)), signature='LUIZ INÁCIO LULA DA SILVA' in body)


def run(out=OUT):
    out = Path(out)
    U = updater()
    item = {i['id']: i for i in json.loads(C.CATALOG_JSON.read_text(encoding='utf-8'))['itens']}[NORMA]
    prov = json.loads(PROVENANCE.read_text(encoding='utf-8'))
    raw = RAW.read_bytes()
    found = {d['norma']: d for d in C.discover(CORPUS)}[NORMA]
    card_rel = found['rel']
    corrupt = (CORPUS / card_rel).read_bytes()
    conteudo, cand = build_txt(U, item, raw, prov, corrupt.decode('utf-8'))
    txt = conteudo.encode('utf-8')
    if out.exists():
        shutil.rmtree(out)
    sd = out / 'SD'
    (sd / card_rel).parent.mkdir(parents=True)
    (sd / card_rel).write_bytes(txt)
    host = out / '_host'
    full = host / 'full_corpus'
    man = C.build_corpus(CORPUS, full, previous_dir=APPROVED_FULL, physical_manifest=PHYSICAL, source_overrides={NORMA: sd / card_rel})
    tdir = sd / C.SD_DIR
    tdir.mkdir(parents=True)
    for name in (f'{NORMA}{C.SUFFIX}', C.CATALOG_NAME):
        shutil.copyfile(full / 'SD' / C.SD_DIR / name, tdir / name)
    blob = (tdir / f'{NORMA}{C.SUFFIX}').read_bytes()
    cat_new = C.read_catalog((tdir / C.CATALOG_NAME).read_bytes())
    cat_old = C.read_catalog((APPROVED_FULL / 'SD' / C.SD_DIR / C.CATALOG_NAME).read_bytes())
    phys = json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries']
    files = []
    for p in sorted(x for x in sd.rglob('*') if x.is_file()):
        rel = p.relative_to(sd).as_posix()
        before = phys.get(rel)
        files.append(dict(path='/' + rel, action='REPLACE' if before else 'ADD', bytes=p.stat().st_size, sha256=sha(p.read_bytes()),
                          physical_before=before))
    # every other physical file under the full-corpus staging stays byte-identical (nothing else to copy)
    others = {k: v for k, v in man['files'].items() if not k.endswith((f'{NORMA}{C.SUFFIX}', C.CATALOG_NAME))}
    unchanged = all(phys.get(k) == v for k, v in others.items())
    manifest = dict(
        schema='MARIA2006_REPAIR_MANIFEST', schema_version=1, norma=NORMA, catalog_item=item, provenance=prov,
        source_file='source_evidence/MARIA2006/' + RAW.name, card_path='/' + card_rel,
        corrupted=dict(bytes=len(corrupt), sha256=sha(corrupt), diagnosis=diagnose_corrupted(corrupt.decode('utf-8'), U.normalizar_texto(cand['texto']))),
        txt=dict(path='/' + card_rel, bytes=len(txt), sha256=sha(txt), encoding='UTF-8 (sem BOM), LF', codificacao_origem=cand['codificacao'],
                 header_atualizado_em=ATUALIZADO_EM, structure=structure_summary(txt)),
        index=dict(file=f'/{C.SD_DIR}/{NORMA}{C.SUFFIX}', bytes=len(blob), sha256=sha(blob), audit=audit_index(blob, txt)),
        catalog=dict(file=f'/{C.SD_DIR}/{C.CATALOG_NAME}', entries_before=len(cat_old), entries_after=len(cat_new),
                     bytes=(tdir / C.CATALOG_NAME).stat().st_size, sha256=sha((tdir / C.CATALOG_NAME).read_bytes()),
                     norms_after=sorted(e['norma'] for e in cat_new)),
        full_corpus=dict(summary=man['summary'], blocked=man['blocked'], other_deploy_files_unchanged_vs_physical=unchanged,
                         catalog_covers_catalog_mestre=sorted(e['norma'] for e in cat_new) == sorted(man['norms'])),
        deploy=files)
    (host / 'MARIA2006_REPAIR_MANIFEST.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + '\n').encode('utf-8'))
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    m = run(ap.parse_args().out)
    print(json.dumps(dict(txt=m['txt'], index={k: v for k, v in m['index'].items() if k != 'audit'},
                          audit={k: v for k, v in m['index']['audit'].items() if k not in ('collective_ranges',)}, catalog={k: v for k, v in m['catalog'].items() if k != 'norms_after'},
                          summary=m['full_corpus']['summary'], blocked=m['full_corpus']['blocked'], deploy=m['deploy'],
                          diagnosis=m['corrupted']['diagnosis']), ensure_ascii=False, indent=1))
