"""JURISPRUDENCE_ENGINE — discovery adapter #6: STJ "espelhos de acórdãos" from the OFFICIAL STJ open-data portal (CKAN), any catalog norm.

The STJ's Secretaria de Jurisprudência publishes, per órgão julgador, the structured "espelho" of the acórdãos that bring novelty
(datasets espelhos-de-acordaos-<órgão>: one historical ZIP of JSON + monthly JSON updates; the same acórdão may appear twice — the id
deduplicates, the latest file wins). Each espelho carries siglaClasse, numeroProcesso, nomeOrgaoJulgador, dataDecisao, dataPublicacao,
ementa, teseJuridica, tema ("Tema Repetitivo N / Situação do tema"), and referenciasLegislativas in the STJ's structured format
("LEG:FED LEI:010406 ANO:2002 ***** CC-02 ... ART:00186 INC:00001"), parsed with adapter #3's grammar-checked reader.
Output per acórdão citing the norm: identity, incident flags, tema links, the norm's targets from (a) the structured references and (b) the
ementa / tese text (adapter #4 citation rules), each tagged with where it was found. Fail closed: grammar rejects are reported, never invented.
Usage: python discovery_stj_espelhos.py --dir <downloads> [--dir ...] --norm CC2002 --out STJ_ESPELHOS_CC2002_INDEX.json
"""
import argparse
import collections
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'LEGAL_TARGET_ID')]
import discovery_stj_precedentes as TXT  # noqa: E402
import discovery_stj_sumulas as SUM  # noqa: E402

TEMAS = re.compile(r'Temas?\s+Repetitivos?\s+([\d,\se]+)', re.I)
SITU = re.compile(r'Situa[çc][ãa]o d[oa]s?\s+temas?:\s*([^\n]+)', re.I)
IAC = re.compile(r'Incidente de Assun[çc][ãa]o de Compet[êe]ncia|\bIAC\b', re.I)


def themes(x):
    """'Tema(s) Repetitivo(s) N[, N...]' + 'Situação do(s) tema(s): A / B'. The STJ records IAC judgments in the same field; the nature comes
    from the notes or the ementa ('Incidente de Assunção de Competência')."""
    t = x.get('tema') or ''
    m = TEMAS.search(t)
    if not m:
        return []
    nums = re.findall(r'\d+', m.group(1))
    sm = SITU.search(t)
    sit = [s.strip() for s in sm.group(1).split('/')] if sm else []
    kind = 'IAC' if IAC.search((x.get('notas') or '') + ' ' + (x.get('ementa') or '')[:300]) else 'REPETITIVO'
    return [dict(numero=n, situacao=sit[i] if i < len(sit) else (sit[-1] if sit else ''), kind=kind) for i, n in enumerate(nums)]
INCIDENTAL = ('EDcl', 'AgRg', 'AgInt', 'ProAfR', 'QO')
PORTAL = 'https://dadosabertos.web.stj.jus.br/dataset/'


def iter_files(dirs):
    """(file name, sha256, list of espelhos) for every JSON and ZIP-of-JSON in the download dirs, oldest first (names are AAAAMMDD)."""
    for d in dirs:
        for p in sorted(Path(d).iterdir()):
            raw = p.read_bytes() if p.suffix.lower() in ('.json', '.zip') else None
            if raw is None:
                continue
            h = hashlib.sha256(raw).hexdigest()
            if p.suffix.lower() == '.zip':
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    for n in sorted(z.namelist()):
                        if n.lower().endswith('.json'):
                            yield f'{Path(d).name}/{p.name}!{n}', h, json.loads(z.read(n).decode('utf-8'))
            else:
                try:
                    docs = json.loads(raw.decode('utf-8'))
                except ValueError as e:     # official file not valid JSON (e.g. 20240229 'Sem lançamentos' placeholder): recorded, never repaired
                    yield f'{Path(d).name}/{p.name}', h, dict(malformed=str(e), head=raw[:200].decode('utf-8', 'replace'))
                    continue
                yield f'{Path(d).name}/{p.name}', h, docs


def refs(raw_list, norm, laws):
    out, bad = [], []
    for r in raw_list or []:
        m = SUM.LEG.search(r)
        if not m:
            continue
        key = (m.group(2), 0 if '*' in m.group(3) else int(m.group(3)), int(m.group(4)))
        if laws.get(key) != norm:
            continue
        try:
            t, b = SUM.ref_targets(norm, r[m.end():])
        except ValueError:                       # malformed official field (e.g. 'PAR:000P3'): rejected whole, never guessed
            bad.append(r.strip()[:200])
            continue
        out += t
        bad += b
    return list(dict.fromkeys(out)), bad


def parse(dirs, norm):
    laws = SUM.catalog_laws()
    latest, files, st = {}, [], collections.Counter()
    for name, h, docs in iter_files(dirs):
        if isinstance(docs, dict):
            files.append(dict(file=name, sha256=h, espelhos=0, malformed_json=docs['malformed'],
                              sem_lancamentos='Sem lan' in docs['head']))
            st['MALFORMED_FILES'] += 1
            continue
        files.append(dict(file=name, sha256=h, espelhos=len(docs)))
        for x in docs:
            if not x.get('id'):
                st['EMPTY_PLACEHOLDERS'] += 1
                continue
            st['ESPELHOS_READ'] += 1
            latest[x['id']] = (x, name, h)
    entries = []
    for eid, (x, name, h) in sorted(latest.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
        st['ACORDAOS'] += 1
        tg, bad = refs(x.get('referenciasLegislativas'), norm, laws)
        hits = {t: ['referencias_legislativas:STRUCTURED'] for t in tg}
        for field, txt in (('ementa', x.get('ementa')), ('tese', x.get('teseJuridica'))):
            found, _, b2 = TXT.cites_extended(re.sub(r'\s+', ' ', txt or ''), norm)
            bad += b2
            for t, m in found.items():
                hits.setdefault(t, []).append(f'{field}:{m}')
        if not hits:
            continue
        st['WITH_TARGETS'] += 1
        sigla = re.sub(r'\s+', ' ', x.get('siglaClasse') or '').strip()
        main = sigla.split(' ')[-1] if sigla else 'ACORDAO'
        temas = themes(x)
        full = re.sub(r'[^A-Za-z0-9]+', '_', sigla).strip('_').upper() or 'ACORDAO'          # 'AgInt nos EREsp' -> AGINT_NOS_ERESP (incident kept)
        entries.append(dict(id=f"STJ:{full}:{x.get('numeroProcesso')}", klass=main.upper(), sigla=sigla, number=str(x.get('numeroProcesso')),
                            incidental=any(sigla.startswith(i) for i in INCIDENTAL), espelho_id=eid, registro=x.get('numeroRegistro'),
                            orgao=x.get('nomeOrgaoJulgador'), relator=x.get('ministroRelator'), julgamento=x.get('dataDecisao'),
                            publicacao=re.sub(r'\s+', ' ', x.get('dataPublicacao') or '').strip(), ementa=re.sub(r'\s+', ' ', x.get('ementa') or '').strip(),
                            tese=re.sub(r'\s+', ' ', x.get('teseJuridica') or '').strip(), notas=re.sub(r'\s+', ' ', x.get('notas') or '').strip()[:300],
                            temas=temas, targets=hits, grammar_rejects=bad,
                            source_document_id=f'espelho {eid} ({name})', source_url=PORTAL, file_sha256=h))
    return entries, files, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', action='append', required=True)
    ap.add_argument('--norm', default='CC2002')
    ap.add_argument('--accessed-on', default='2026-10-19')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    entries, files, st = parse(a.dir, a.norm)
    doc = dict(schema_version=1, adapter='discovery_stj_espelhos', court='STJ', norm=a.norm,
               source=dict(portal=PORTAL, datasets=[Path(d).name.replace('dl_', '') for d in a.dir], licence='CC-BY', tier='A', org='STJ',
                           accessed_on=a.accessed_on, files=files,
                           method='download direto dos recursos públicos do portal de dados abertos (CKAN); nenhum desafio anti-robô contornado'),
               stats=dict(ESPELHOS_READ=st['ESPELHOS_READ'], ACORDAOS=st['ACORDAOS'], WITH_TARGETS=st['WITH_TARGETS'],
                          PAIRS=sum(len(e['targets']) for e in entries),
                          BY_EVIDENCE=dict(sorted(collections.Counter(m.split(':')[0] for e in entries for ms in e['targets'].values() for m in ms).items())),
                          WITH_TEMA=sum(1 for e in entries if e['temas']), MALFORMED_FILES=st['MALFORMED_FILES'], EMPTY_PLACEHOLDERS=st['EMPTY_PLACEHOLDERS'], GRAMMAR_REJECTS=sum(len(e['grammar_rejects']) for e in entries)),
               entries=entries)
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(doc['stats'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
