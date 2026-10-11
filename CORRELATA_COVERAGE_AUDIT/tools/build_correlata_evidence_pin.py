"""CF88_CORRELATA_COVERAGE_AUDIT_C0 — evidence pin (diagnostic only; reads local evidence, writes ONE versioned JSON).

Several evidence sources of the correlata audit exist only as local, unversioned folders of the main checkout (Relations V2 legacy
stages 2D4..2E6, the read-only SD backup with the 72 main-corpus texts, the physical SD manifests). This tool reads them READ ONLY and
freezes what the audit needs into CORRELATA_COVERAGE_AUDIT/inputs/CORRELATA_EVIDENCE_PIN.json (sha256 of every source file), so that
the audit itself (correlata_coverage_audit.py) runs only on versioned files + this pin and is reproducible on any checkout.

Pinned:
  physical_sd              sha256 of the /99_LEX_V1 and /99_RELATIONS_V2 files on the card (post FULL_ENTENDA_810 manifest)
  relations_v2_package     EXT_NORMAS / RELACOES / REL_LOOKUP / EXT_ARTIGOS of the 2E6 package, checked byte by byte against the card
  main_corpus              72 catalog norms located by the Updater locator in the SD backup, with presence on the card (same sha256)
  legacy_relations         normalized records of the Relations V2 legacy stages (evidence/candidates, never authority)
  reverse_remissions       literal citations of CF88/ADCT devices found in the main-corpus and external-norm texts (citation_parser,
                           fail closed: only status OK citations become targets; the rest is counted as UNRESOLVED)
Nothing is written outside the pin; no SD, firmware, ENTENDA, Lei Seca or Reference Engine file is touched.
Usage: python build_correlata_evidence_pin.py [--legacy-root C:/GitHub/LEX-MACHINA]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(ROOT / 'DEVICE_INTEGRATION/tools'))
import citation_parser as CP  # noqa: E402
import target_id as T  # noqa: E402

PIN = AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json'
SD_BACKUP = 'DEVICE_INTEGRATION/backups/sd_20260929T163407Z/data'
PHYSICAL_MANIFEST = 'DEVICE_INTEGRATION/backups/full_entenda_810_physical_deploy/sd_manifest_post_full.json'
REL_PKG = 'LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/SD_PRONTO'
LEGACY_SETS = (  # (set id, stage, relative path, role)
    ('2E4_RELACOES_CF88', '2E4.1', 'LEX-MACHINAETAPA_2E41/etapa2e4_work/saida/PACOTE_FUSAO_CF_2E4/99_RELATIONS_V2/01_RELACOES_GLOBAIS/RELACOES_CF88.json',
     'ORIGEM_DAS_CORRELATAS_ATUAIS'),
    ('2D4_EXIBIVEIS', '2D4', 'LEX-MACHINAETAPA_2D4/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D4/RELACOES_CF88_EXIBIVEIS_2D4.json', 'CANDIDATO_LEGADO'),
    ('2D4_QUARENTENA', '2D4', 'LEX-MACHINAETAPA_2D4/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D4/QUARENTENA_2D3_PRESERVADA.json', 'CANDIDATO_LEGADO'),
    ('2D4_HISTORICO_REVOGADAS', '2D4', 'LEX-MACHINAETAPA_2D4/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D4/HISTORICO_REVOGADAS_PRESERVADO.json',
     'HISTORICO_LEGADO'),
    ('2D4_P3_DECRETOS_OU_AMPLAS', '2D4', 'LEX-MACHINAETAPA_2D4/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D4/CANDIDATAS_P3_DECRETOS_OU_AMPLAS.json',
     'CANDIDATO_LEGADO'),
    ('2D6_4_P1_CONSOLIDADAS', '2D6.4', 'LEX-MACHINAETAPA_2D6_4/etapa2d6_4_work/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D6_4/P1_CONSOLIDADAS_FINAIS_2D6_4.json',
     'CANDIDATO_LEGADO'),
    ('2D8_P2_A', '2D8', 'LEX-MACHINAETAPA_2D8/etapa2d8_work/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D8/P2_A_REMISSAO_EXPRESSA_2D8.json', 'CANDIDATO_LEGADO'),
    ('2D8_P2_B', '2D8', 'LEX-MACHINAETAPA_2D8/etapa2d8_work/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D8/P2_B_REGULAMENTACAO_OFICIAL_2D8.json', 'CANDIDATO_LEGADO'),
    ('2D8_P2_D_HISTORICO', '2D8', 'LEX-MACHINAETAPA_2D8/etapa2d8_work/saida/99_RELATIONS_V2/99_AUDITORIA_QUALIDADE_2D8/P2_D_HISTORICO_2D8.json', 'HISTORICO_LEGADO'),
)
SNIP = 280


class PinError(RuntimeError):
    pass


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def rows(text):
    return [l.split('|') for l in text.splitlines() if l and not l.startswith('#')]


def decode(b):
    try:
        return b.decode('utf-8-sig')
    except UnicodeDecodeError:
        return b.decode('cp1252')


def clip(s, n=SNIP):
    s = ' '.join(str(s or '').split())
    return s if len(s) <= n else s[:n - 1] + '…'


# ------------------------------------------------------------------ physical card + Relations V2 package
def physical_sd(lr, sources):
    p = lr / PHYSICAL_MANIFEST
    m = json.loads(p.read_text(encoding='utf-8'))
    sources.append(dict(path=PHYSICAL_MANIFEST, sha256=sha_b(p.read_bytes()), role='MANIFESTO_FISICO_POS_FULL_ENTENDA_810'))
    keep = {k: v for k, v in m['entries'].items() if k.startswith(('99_LEX_V1/', '99_RELATIONS_V2/'))}
    return m, dict(manifest=PHYSICAL_MANIFEST, drive=m['drive'], file_count=m['file_count'], files=dict(sorted(keep.items())))


DEVICE_STAGING = 'DEVICE_INTEGRATION/staging_sd_v1_full_entenda_810_candidate/SD'
DEVICE_TABLES = ('99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', '99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX', '99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX',
                 '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')


def device_tables(lr, manifest, sources):
    """Device tables of the physically approved FULL_ENTENDA_810 package, read from its staging and accepted only when every file is
    byte-identical (sha256) to the file on the card."""
    out = {}
    for rel in DEVICE_TABLES:
        p = lr / DEVICE_STAGING / rel
        b = p.read_bytes()
        card = manifest['entries'].get(rel)
        if not card or card['sha256'] != sha_b(b):
            raise PinError(f'DEVICE_TABLE_NOT_EQUAL_TO_CARD {rel}')
        sources.append(dict(path=f'{DEVICE_STAGING}/{rel}', sha256=sha_b(b), role='PACOTE_FISICO_FULL_ENTENDA_810 (= cartao)'))
        out[rel] = b.decode('utf-8')
    targets = {r[0]: dict(kind=r[1], legal_status=r[2], flags=r[3]) for r in rows(out[DEVICE_TABLES[0]])}
    text_map = [r[2] for r in rows(out[DEVICE_TABLES[1]])]
    ent = {r[0]: dict(explanation_id=r[3], resolution=r[7]) for r in rows(out[DEVICE_TABLES[2]])}
    return dict(staging=DEVICE_STAGING, sha256={rel: sha_b(out[rel].encode('utf-8')) for rel in DEVICE_TABLES},
                targets_header=[l for l in out[DEVICE_TABLES[0]].splitlines() if l.startswith('#')][:5],
                targets=dict(sorted(targets.items())), text_map_targets=text_map, entenda_lookup=dict(sorted(ent.items())))


def relations_package(lr, manifest, sources):
    base = lr / REL_PKG
    idx = base / '99_RELATIONS_V2/05_INDICES_ESP32_V2'
    files = sorted(p for p in (base / '99_RELATIONS_V2').rglob('*') if p.is_file())
    check = {}
    for p in files:
        rel = p.relative_to(base).as_posix()
        b = p.read_bytes()
        card = manifest['entries'].get(rel)
        check[rel] = dict(sha256=sha_b(b), bytes=len(b), on_card=bool(card), card_identical=bool(card and card['sha256'] == sha_b(b)))
        sources.append(dict(path=f'{REL_PKG}/{rel}', sha256=sha_b(b), role='PACOTE_RELATIONS_V2_2E6'))
    card_only = sorted(k for k in manifest['entries'] if k.startswith('99_RELATIONS_V2/') and k not in check)
    if card_only or not all(c['card_identical'] for c in check.values()):
        raise PinError(f'RELATIONS_V2_PACKAGE_NOT_EQUAL_TO_CARD card_only={card_only}')
    ext_normas = [dict(id=r[0], nome=r[1], caminho=r[2], artigos=int(r[3]), bytes=int(r[4])) for r in rows((idx / 'EXT_NORMAS.IDX').read_text(encoding='utf-8'))]
    relacoes = [dict(origem=r[0:5], relacao_id=r[5], destino_id=r[6], destino_nome=r[7], modo=r[8], artigos_destino=[a for a in r[9].split(',') if a],
                     caminho=r[10]) for r in rows((idx / 'RELACOES.IDX').read_text(encoding='utf-8'))]
    lookup = [dict(origem=r[0:5], offset=int(r[5]), quantidade=int(r[6])) for r in rows((idx / 'REL_LOOKUP.IDX').read_text(encoding='utf-8'))]
    arts = {}
    for r in rows((idx / 'EXT_ARTIGOS.IDX').read_text(encoding='utf-8')):
        arts.setdefault(r[0], []).append(r[1])
    for n in ext_normas:
        f = base / n['caminho'].lstrip('/')
        n['file_present'] = f.is_file()
        n['file_sha256'] = sha_b(f.read_bytes()) if f.is_file() else None
        n['indexed_articles'] = len(arts.get(n['id'], []))
        n['ementa'] = clip(_ementa(decode(f.read_bytes())), 400) if f.is_file() else None
    return dict(path=REL_PKG, files=check, ext_normas=ext_normas, relacoes=relacoes, rel_lookup=lookup,
                ext_artigos={k: v for k, v in sorted(arts.items())},
                cache_limits_firmware=dict(MAX_LOOKUP_V2_CACHE=64, MAX_NORMAS_V2_CACHE=32,
                                           note='DEVICE_INTEGRATION/RELATIONS_V2_LEGACY_64_LINE_LIMIT.md (truncamento silencioso no cache legado)'))


def _ementa(text):
    t = ' '.join(text.split())
    m = re.search(r'\bArt\.\s*1\s*(?:º|°|o)\b', t)
    return t[:m.start()] if m else t[:600]


# ------------------------------------------------------------------ main corpus (72 catalog norms)
def main_corpus(lr, manifest, sources):
    import article_index_corpus as A
    root = lr / SD_BACKUP
    cat = json.loads((ROOT / 'updater/catalogo_mestre_vademecum.json').read_text(encoding='utf-8'))
    found = {f['norma']: f for f in A.discover(root)}
    out = []
    for it in cat['itens']:
        f = found.get(it['id'])
        rec = dict(id=it['id'], nome=it['nome'], tipo=it['tipo'], located=bool(f and f['status'] == 'LOCATED'))
        if rec['located']:
            b = f['path'].read_bytes()
            card = manifest['entries'].get(f['rel'])
            rec.update(rel=f['rel'], sha256=sha_b(b), bytes=len(b), on_card=bool(card), card_identical=bool(card and card['sha256'] == sha_b(b)))
            if card and not rec['card_identical']:
                rec['card_note'] = ('o cartao tem outra versao do mesmo arquivo (ex.: reparo de fonte MARIA2006); remissoes lidas do backup '
                                    'somente-leitura anterior')
            sources.append(dict(path=f"{SD_BACKUP}/{f['rel']}", sha256=rec['sha256'], role='ACERVO_PRINCIPAL'))
        out.append(rec)
    return out, found


# ------------------------------------------------------------------ legacy Relations V2
def _origin(r):
    def first(*keys):
        for k in keys:
            v = r.get(k)
            if v:
                return [str(x) for x in v] if isinstance(v, list) else [str(v)]
        return []
    pars = first('origem_paragrafos_confirmados_texto_2d8', 'origem_paragrafos_pagina_2d8', 'origem_paragrafos') or first('origem_paragrafo')
    incs = first('origem_incisos_confirmados_texto_2d8', 'origem_incisos_pagina_2d8', 'origem_incisos')
    als = first('origem_alineas_confirmadas_texto_2d8', 'origem_alineas_pagina_2d8', 'origem_alineas')
    return dict(norma=r.get('origem_norma'), artigo=str(r.get('origem_artigo') or ''), paragrafos=pars, incisos=incs, alineas=als,
                caminhos=[str(c) for c in r.get('origem_caminhos', [])])


def legacy_relations(lr, sources):
    out, per_set = [], {}
    for sid, stage, rel, role in LEGACY_SETS:
        p = lr / rel
        b = p.read_bytes()
        sources.append(dict(path=rel, sha256=sha_b(b), role=f'RELATIONS_V2_LEGADO_{stage}'))
        recs = json.loads(b.decode('utf-8'))['relacoes']
        per_set[sid] = len(recs)
        for i, r in enumerate(recs):
            if sid == '2E4_RELACOES_CF88':
                bind = r['navegacao']['bindings']
                out.append(dict(legacy_id=f'{sid}:{r["id"]}', set=sid, stage=stage, role=role, relacao_id=r['id'], origem=_origin(r),
                                destino_norma=r['destino_norma'], destino_artigos=sorted({a for b_ in bind for a in b_['artigos_destino']}),
                                tipos=[r['tipo']], fontes=sorted(r.get('fontes', {}).keys()), urls=sorted(r.get('fontes', {}).values()),
                                classe=None, decisao=r['status'], secao_camara=None, vigencia_status=None, motivos=[],
                                bindings=[dict(origem_caminho=b_['origem_caminho'], modo=b_['modo_abertura'], artigos=b_['artigos_destino']) for b_ in bind],
                                evidencia=clip(r.get('proveniencia', {}).get('regra'))))
                continue
            out.append(dict(legacy_id=f'{sid}:{i:04d}', set=sid, stage=stage, role=role, relacao_id=None, origem=_origin(r),
                            destino_norma=r['destino_norma'], destino_artigos=[str(a) for a in r.get('destino_artigos') or []],
                            tipos=r.get('tipos') or [], fontes=r.get('fontes') or [], urls=(r.get('urls') or [])[:3],
                            classe=r.get('classe'), decisao=r.get('decisao'), secao_camara=r.get('secao_camara_2d8') or r.get('secao_camara'),
                            vigencia_status=r.get('vigencia_status_2d8') or r.get('vigencia_status'), motivos=(r.get('motivos_2d8') or r.get('motivos') or [])[:4],
                            score=r.get('score'), evidencia=clip(' | '.join(r.get('evidencias') or [])),
                            ementa=clip(r.get('vigencia_evidencia'), 400) if r.get('vigencia_evidencia') else None))
    return out, per_set


# ------------------------------------------------------------------ reverse remissions (corpus text -> CF88/ADCT device)
PAREN_NOTE = re.compile(r'\((?:\s*(?:Reda[çc][ãa]o|Inclu[íi]d|Acrescid|Vide|Revogad|Renumerad|Vig[êe]ncia|Regulamento|Produ[çc][ãa]o)[^()]{0,300})\)', re.I)
CF_MARKER = re.compile(r'\b(?:da|do)\s+(?:Constitui[çc][ãa]o(?:\s+Federal|\s+da\s+Rep[úu]blica(?:\s+Federativa\s+do\s+Brasil)?)?(?:\s+de\s+1988)?|CF(?:/88)?\b|Carta\s+Magna)')
ADCT_MARKER = re.compile(r'\b(?:do|da)\s+(?:Ato\s+das\s+Disposi[çc][õo]es\s+Constitucionais\s+Transit[óo]rias|ADCT\b)')
BOUNDARY = re.compile(r'(?:;|:|(?<![Aa]rt)(?<![Aa]rts)(?<!inc)(?<!incs)(?<!\bn)(?<!\bp)\.)\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])')
ART_NUM = re.compile(r'\b(?:art|arts|artigo|artigos)\.?\s*(\d{1,3}(?:-[A-Z])?)')   # citations are lower case; 'Art. n' is a heading
NESTED = re.compile(r'(?:al[íi]nea\s+["“\']?(?P<al>[a-z])["”\']?\s+do\s+)?(?:inciso\s+(?P<inc>[IVXLC]{1,7}(?:-[A-Z])?)\s+do\s+)?'
                    r'(?:(?:§\s*(?P<par>\d{1,3}(?:-[A-Z])?)\s*º?|(?P<unico>par[áa]grafo\s+[úu]nico))\s+do\s+)?(?:(?P<caput>caput)\s+do\s+)?'
                    r'art\.\s*(?P<art>\d{1,3}(?:-[A-Z])?)\s*º?')
HEADING = re.compile(r'\bArt\.\s*(\d{1,4}(?:\.\d{3})?)\s*(?:º|°)?(?:\s*-\s*([A-Z]))?(?=[\s.\-–])')
VERB = (('REGULAMENTA', re.compile(r'\b(?:regulament\w*|regula|regulam|disciplin\w*)\b', re.I)),
        ('IMPLEMENTA', re.compile(r'\b(?:disp[õo]e\s+sobre|institui\w*|cria|estabelece)\b', re.I)),
        ('COMPLEMENTA', re.compile(r'\b(?:nos\s+termos|previst[oa]s?|de\s+que\s+trat\w+|a\s+que\s+se\s+refere\w*|com\s+(?:amparo|fundamento)|em\s+cumprimento|'
                                   r'para\s+(?:os\s+)?(?:fins|efeitos)\s+d[oa]|cumprir\s+o\s+disposto|conforme)\b', re.I)))


def normalize_corpus_text(t):
    t = t.replace('\xa0', ' ').replace('\r', '\n')
    t = ' '.join(t.split())
    t = re.sub(r'(\d)\s+(?:o|º|°)(?=[\s,;.)\-]|$)', r'\1º', t)      # Planalto '§ 1 o' -> '§ 1º'
    t = re.sub(r'\b([Aa]rts?)\.\s+(\d)', r'\1. \2', t)
    return PAREN_NOTE.sub(' ', t)


AMEND_START = re.compile(r'(?:passa(?:m)?\s+a\s+vigorar|fica(?:m)?\s+acrescid\w*|acrescid[oa]s?\s+d[oa]s?\s+seguintes?|com\s+a\s+seguinte\s+reda[çc][ãa]o)'
                         r'[^“"]{0,250}[“"]', re.I)
AMEND_END = re.compile(r'\((?:NR|AC)\)')
UNIT = re.compile(r'(?<![\wÀ-ú])(?:al[íi]neas?|incisos?|§|par[áa]grafos?|caput|arts?\.|artigos?)', re.I)


def amendment_spans(t):
    """Text of OTHER norms quoted by amending clauses ('passa a vigorar com as seguintes alteracoes: “Art. 1º ...” (NR)'): its headings
    and citations belong to the amended norm, never to the source norm."""
    spans, pos = [], 0
    while True:
        m = AMEND_START.search(t, pos)
        if not m:
            return spans
        e = AMEND_END.search(t, m.end())
        end = e.end() if e and e.start() - m.end() < 60000 else min(len(t), m.end() + 2000)
        spans.append((m.end() - 1, end))
        pos = end


def reverse_remissions(norma, text):
    t = normalize_corpus_text(text)
    spans = amendment_spans(t)
    inside = lambda p: any(a <= p < b for a, b in spans)  # noqa: E731
    heads = [(m.start(), m.group(1).replace('.', '') + (('-' + m.group(2)) if m.group(2) else '')) for m in HEADING.finditer(t)
             if not inside(m.start())]
    first_art = heads[0][0] if heads else len(t)
    hits = []
    for marker, ns in ((CF_MARKER, 'CF88'), (ADCT_MARKER, 'ADCT')):
        for m in marker.finditer(t):
            if inside(m.start()):
                hits.append(dict(source_norm=norma, source_article=None, region='AMENDMENT_BLOCK', verb_class='-', namespace=ns, article=None,
                                 status='IN_AMENDMENT_BLOCK', reason='citacao dentro de texto de outra norma alterada', targets=[],
                                 snippet=clip(t[max(0, m.start() - SNIP):m.end()])))
                continue
            lo = max(0, m.start() - 320)
            win = t[lo:m.end()]
            bounds = [b.end() for b in BOUNDARY.finditer(win, 0, len(win) - (m.end() - m.start()))]
            clause = win[bounds[-1]:] if bounds else win
            body = len(clause) - (m.end() - m.start())
            cuts = [h.end() for h in HEADING.finditer(clause, 0, body)]                     # never across a heading of the source norm
            cuts += [x.end() for rx in (CF_MARKER, ADCT_MARKER) for x in rx.finditer(clause, 0, body)]   # nor across a previous citation
            if cuts:
                clause = clause[max(cuts):]
            # nested 'alinea x do inciso Y do § Z do art. N' (outside the citation_parser grammar): literal, CF context checked
            nested, rest = [], clause
            for nm in NESTED.finditer(clause):
                if sum(1 for g in ('al', 'inc', 'par', 'unico', 'caput') if nm.group(g)) < 2 or (nm.group('caput') and not nm.group('inc')):
                    continue
                if CP._norm_after(clause, nm.end())[0] != ('CF' if ns == 'CF88' else 'ADCT'):
                    continue
                par = 'UNICO' if nm.group('unico') else nm.group('par')
                try:
                    tid = T.format_target_id(ns, nm.group('art'), paragraph=par, inciso=nm.group('inc'), alinea=nm.group('al'))
                except Exception:  # noqa: BLE001 - not a valid device id: left to the generic parser (fail closed there)
                    continue
                nested.append((nm.group('art'), tid))
                rest = rest.replace(nm.group(0), ' ' * len(nm.group(0)), 1)
            arts = []
            for a in ART_NUM.finditer(rest):
                if a.group(1) not in arts:
                    arts.append(a.group(1))
            if not arts and not nested:
                continue
            pos = m.start()
            src_art = None
            for hp, ha in heads:
                if hp <= pos:
                    src_art = ha
                else:
                    break
            region = 'EMENTA' if pos < first_art else ('ART1' if src_art == '1' else 'BODY')
            u = UNIT.search(clause)
            near = clause[max(0, (u.start() if u else len(clause)) - 90):(u.start() if u else len(clause))]   # verb glued to the citation
            verb = next((k for k, rx in VERB if rx.search(near)), 'INCIDENTAL')
            for a, tid in nested:
                hits.append(dict(source_norm=norma, source_article=src_art, region=region, verb_class=verb, namespace=ns, article=a,
                                 status='OK', reason='NESTED_LITERAL_CITATION', targets=[tid], snippet=clip(clause[-SNIP:]), marker=m.group(0)))
            for a in arts:
                p = CP.parse_for_article(rest, a)
                st, targets, reason = p['status'], [], p.get('reason')
                want = 'CF' if ns == 'CF88' else 'ADCT'
                if st == 'OK' and p['norm'] == want:
                    try:
                        targets = CP.to_targets(ns, a, p, T.format_target_id)
                    except Exception as e:  # noqa: BLE001 - fail closed, recorded
                        st, reason = 'UNPARSEABLE', f'TARGET_FORMAT_ERROR {e}'
                elif st == 'OK':
                    st, reason = 'OTHER_NORM', f"citacao de {p.get('norm_label') or p['norm']}"
                hits.append(dict(source_norm=norma, source_article=src_art, region=region, verb_class=verb, namespace=ns, article=a,
                                 status=st, reason=reason, targets=targets, snippet=clip(clause[-SNIP:]), marker=m.group(0)))
    # one record per (source article, region, verb, targets) — the same sentence matched twice by overlapping windows counts once
    seen, out = set(), []
    for h in hits:
        k = (h['source_article'], h['region'], h['namespace'], h['article'] or '', tuple(h['targets']), h['status'], h['snippet'])
        if k not in seen:
            seen.add(k)
            out.append(h)
    return out


def build(lr):
    lr = Path(lr)
    sources = []
    manifest, phys = physical_sd(lr, sources)
    rel = relations_package(lr, manifest, sources)
    dev = device_tables(lr, manifest, sources)
    corpus, found = main_corpus(lr, manifest, sources)
    legacy, per_set = legacy_relations(lr, sources)
    rev = []
    for it in corpus:
        if it['id'] == 'CF88' or not it['located']:
            continue
        rev += reverse_remissions(it['id'], decode(found[it['id']]['path'].read_bytes()))
    base = lr / REL_PKG
    for n in rel['ext_normas']:
        f = base / n['caminho'].lstrip('/')
        if f.is_file():
            rev += reverse_remissions(n['id'], f.read_bytes().decode('utf-8', errors='replace'))
    rev.sort(key=lambda h: (h['source_norm'], h['namespace'], h['article'] or '', h['targets'], h['source_article'] or '', h['snippet']))
    sources.sort(key=lambda s: s['path'])
    return dict(schema_version=1, pin_id='CF88_CORRELATA_EVIDENCE_PIN_C0', mission='CF88_CORRELATA_COVERAGE_AUDIT_C0',
                policy='Evidencia congelada (somente leitura). O Relations V2 legado e evidencia/candidato, nunca autoridade juridica. '
                       'Nenhum candidato e promovido por este arquivo.',
                legacy_root_note='caminhos relativos a raiz do checkout principal (pastas locais nao versionadas)',
                sources=sources, physical_sd=phys, device_tables=dev, relations_v2_package=rel, main_corpus=corpus,
                legacy_relations=dict(per_set=per_set, records=legacy),
                reverse_remissions=dict(scanned_norms=sorted({h['source_norm'] for h in rev}), records=rev))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--legacy-root', default=str(ROOT))
    a = ap.parse_args()
    doc = build(a.legacy_root)
    data = (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if build(a.legacy_root) != doc:
        raise PinError('PIN_NOT_DETERMINISTIC')
    PIN.parent.mkdir(parents=True, exist_ok=True)
    PIN.write_bytes(data)
    rr = doc['reverse_remissions']['records']
    print(json.dumps(dict(pin=PIN.relative_to(ROOT).as_posix(), sha256=sha_b(data), bytes=len(data), sources=len(doc['sources']),
                          legacy=doc['legacy_relations']['per_set'], main_corpus=len(doc['main_corpus']),
                          main_on_card=sum(1 for c in doc['main_corpus'] if c.get('card_identical')),
                          ext_normas=len(doc['relations_v2_package']['ext_normas']), reverse_hits=len(rr),
                          reverse_ok=sum(1 for h in rr if h['status'] == 'OK')), indent=1))


if __name__ == '__main__':
    main()
