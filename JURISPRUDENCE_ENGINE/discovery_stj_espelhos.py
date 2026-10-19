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

TEMA = re.compile(r'Tema\s+Repetitivo\s+(\d+)(?:.*?Situa[çc][ãa]o do tema:\s*([^\n]+))?', re.I | re.S)
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
                yield f'{Path(d).name}/{p.name}', h, json.loads(raw.decode('utf-8'))


def refs(raw_list, norm, laws):
    out, bad = [], []
    for r in raw_list or []:
        m = SUM.LEG.search(r)
        if not m:
            continue
        key = (m.group(2), 0 if '*' in m.group(3) else int(m.group(3)), int(m.group(4)))
        if laws.get(key) != norm:
            continue
        t, b = SUM.ref_targets(norm, r[m.end():])
        out += t
        bad += b
    return list(dict.fromkeys(out)), bad


def parse(dirs, norm):
    laws = SUM.catalog_laws()
    latest, files, st = {}, [], collections.Counter()
    for name, h, docs in iter_files(dirs):
        files.append(dict(file=name, sha256=h, espelhos=len(docs)))
        for x in docs:
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
        temas = [dict(numero=m.group(1), situacao=(m.group(2) or '').strip()) for m in TEMA.finditer(x.get('tema') or '')]
        full = re.sub(r'[^A-Za-z0-9]+', '_', sigla).strip('_').upper() or 'ACORDAO'          # 'AgInt nos EREsp' -> AGINT_NOS_ERESP (incident kept)
        entries.append(dict(id=f"STJ:{full}:{x.get('numeroProcesso')}", klass=main.upper(), sigla=sigla, number=str(x.get('numeroProcesso')),
                            incidental=any(sigla.startswith(i) for i in INCIDENTAL), espelho_id=eid, registro=x.get('numeroRegistro'),
                            orgao=x.get('nomeOrgaoJulgador'), relator=x.get('ministroRelator'), julgamento=x.get('dataDecisao'),
                            publicacao=re.sub(r'\s+', ' ', x.get('dataPublicacao') or '').strip(), ementa=re.sub(r'\s+', ' ', x.get('ementa') or '').strip(),
                            tese=re.sub(r'\s+', ' ', x.get('teseJuridica') or '').strip(), temas=temas, targets=hits, grammar_rejects=bad,
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
                          WITH_TEMA=sum(1 for e in entries if e['temas']), GRAMMAR_REJECTS=sum(len(e['grammar_rejects']) for e in entries)),
               entries=entries)
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(doc['stats'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
