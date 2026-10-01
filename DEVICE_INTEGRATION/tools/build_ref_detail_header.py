"""Generate firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h from the APPROVED reference catalog (fast track).

Source of truth: LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json, records of type WORK_REFERENCE from
V2_RC2_REFERENCES (human-reviewed RC2), whose `legal_fields_preserved` carry the approved editorial fields per link
(work <-> legal target): obra, tipo, ano, score_editorial, fontes[].paraphrase (documented synopsis), POR_QUE_ESTA_OBRA_SE_RELACIONA,
PARTE_ALCANCADA, relacao_pedagogica. Nothing is written or rewritten: only transported. Only links present as CURRENT_VISIBLE
WORK_REFERENCE rows of the approved device REF_PAYLOAD are emitted (the REF_PAYLOAD itself stays a byte copy).
There is NO approved "temas" field in the catalog: it is reported as REFERENCE_DETAIL_INCOMPLETE, never invented.

Deterministic: sorted by key "TARGET_ID|WORK_ID"; the header records the sha256 of both inputs.
Usage: python build_ref_detail_header.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
CANON = ROOT / 'LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json'
PAYLOAD = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1/REF_PAYLOAD.IDX'
OUT = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h'
SCHEMA = 1
RELACAO = {                                   # display names of the approved relacao_pedagogica codes (formatting only)
    'ILUSTRACAO_DE_VIOLACAO': 'Ilustração de violação',
    'ILUSTRACAO_DE_CONSEQUENCIA': 'Ilustração de consequência',
    'ANALOGIA_CONTROLADA': 'Analogia controlada',
    'CONTEXTUALIZACAO_HISTORICA': 'Contextualização histórica',
    'REPRESENTACAO': 'Representação',
}
FIELDS = ('tipo', 'ano', 'nota', 'sobre', 'por_que', 'temas')


def c_str(s):
    b = s.encode('utf-8')
    out = []
    for ch in b:
        if ch in (0x22, 0x5C):
            out.append('\\' + chr(ch))
        elif 32 <= ch < 127:
            out.append(chr(ch))
        else:
            out.append('\\x%02x' % ch)
    # break hex escapes that could swallow following hex digits
    txt, res = ''.join(out), []
    i = 0
    while i < len(txt):
        res.append(txt[i])
        if txt[i] == '\\' and txt[i + 1] == 'x' and i + 4 < len(txt) + 1:
            res.append(txt[i + 1:i + 4])
            i += 4
            if i < len(txt) and txt[i] in '0123456789abcdefABCDEF':
                res.append('""')
            continue
        i += 1
    return '"' + ''.join(res) + '"'


def records():
    canon = json.loads(CANON.read_text(encoding='utf-8'))
    visible = set()
    for l in PAYLOAD.read_text(encoding='utf-8').splitlines():
        if l and not l.startswith('#'):
            p = l.split('|')
            if p[1] == 'WORK_REFERENCE' and p[2] == 'CURRENT_VISIBLE':
                visible.add((p[0], p[5]))
    out, incomplete = {}, {f: 0 for f in FIELDS}
    for r in canon['records']:
        if r['reference_type'] != 'WORK_REFERENCE' or r['source_layer'] != 'V2_RC2_REFERENCES':
            continue
        key = (r['target_id'], r['subject_id'])
        if key not in visible:
            continue
        lf = r['legal_fields_preserved']
        sobre = next((f['paraphrase'] for f in lf.get('fontes', []) if f.get('paraphrase')), '')
        score = lf.get('score_editorial')
        rec = dict(key=f'{key[0]}|{key[1]}', titulo=lf['obra'], tipo=lf.get('tipo') or '', ano=int(lf.get('ano') or 0),
                   nota=-1 if score is None else int(round(float(score) * 10)), sobre=sobre,
                   por_que=lf.get('POR_QUE_ESTA_OBRA_SE_RELACIONA') or '', alcance=lf.get('PARTE_ALCANCADA') or '',
                   relacao=RELACAO.get(lf.get('relacao_pedagogica'), lf.get('relacao_pedagogica') or ''), fonte=lf['work_id'])
        prev = out.get(rec['key'])
        if prev:
            # same work <-> target link approved for more than one nucleus: keep every approved text (paragraphs), best nota
            for f, sep in (('por_que', '\n'), ('alcance', '; '), ('sobre', '\n')):
                if rec[f] and rec[f] not in prev[f].split(sep):
                    prev[f] = prev[f] + sep + rec[f] if prev[f] else rec[f]
            prev['nota'] = max(prev['nota'], rec['nota'])
            continue
        out[rec['key']] = rec
    for rec in out.values():
        incomplete['tipo'] += not rec['tipo']
        incomplete['ano'] += not rec['ano']
        incomplete['nota'] += rec['nota'] < 0
        incomplete['sobre'] += not rec['sobre']
        incomplete['por_que'] += not rec['por_que']
        incomplete['temas'] += 1                      # no approved field exists
    return [out[k] for k in sorted(out, key=lambda k: k.encode('utf-8'))], incomplete, len(visible)


def render():
    recs, incomplete, n_visible = records()
    src = hashlib.sha256(CANON.read_bytes()).hexdigest()
    pay = hashlib.sha256(PAYLOAD.read_bytes()).hexdigest()
    L = ['#pragma once',
         '// GERADO por DEVICE_INTEGRATION/tools/build_ref_detail_header.py - NAO EDITAR.',
         '// Metadados editoriais APROVADOS (RC2 revisado) dos vinculos obra <-> dispositivo, transportados sem reescrita.',
         f'// Fonte: LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json sha256 {src}',
         f'// Filtro: linhas WORK_REFERENCE CURRENT_VISIBLE do REF_PAYLOAD aprovado sha256 {pay}',
         f'// Vinculos: {len(recs)} de {n_visible} visiveis. REFERENCE_DETAIL_INCOMPLETE (campos ausentes): '
         + ', '.join(f'{k}={v}' for k, v in incomplete.items()),
         '// nota = score_editorial do VINCULO x 10 (-1 = ausente). Ordenado por chave "TARGET_ID|WORK_ID" (bytewise).',
         f'#define LEXV1_REF_DETAIL_SCHEMA {SCHEMA}',
         f'#define LEXV1_REF_DETAIL_COUNT {len(recs)}',
         f'#define LEXV1_REF_DETAIL_SOURCE_SHA256 "{src}"',
         'struct LexV1RefDetalhe { const char *chave, *titulo, *tipo; uint16_t ano; int16_t nota10;',
         '                        const char *sobre, *porQue, *alcance, *relacao, *fonte; };',
         'static const LexV1RefDetalhe LEXV1_REF_DETALHES[LEXV1_REF_DETAIL_COUNT] = {']
    for r in recs:
        L.append('  {%s, %s, %s, %d, %d,\n   %s,\n   %s,\n   %s, %s, %s},' % (
            c_str(r['key']), c_str(r['titulo']), c_str(r['tipo']), r['ano'], r['nota'], c_str(r['sobre']), c_str(r['por_que']),
            c_str(r['alcance']), c_str(r['relacao']), c_str(r['fonte'])))
    L.append('};')
    return '\n'.join(L) + '\n', recs, incomplete


if __name__ == '__main__':
    txt, recs, inc = render()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_text(encoding='utf-8') == txt
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(txt.encode('utf-8'))
    print(len(recs), inc, OUT.stat().st_size)
