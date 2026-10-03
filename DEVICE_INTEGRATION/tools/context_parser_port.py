"""Faithful Python port of aplicarLinhaContextoJuridico() from firmware v7.12.0 (contexto_juridico.h), used only on the PC to
check that the runtime tuple (artigo, paragrafo, inciso, alinea) of the physically validated parser maps to the same canonical
target_id as CF88_TEXT_MAP.IDX (derived from the approved structural index). Read-only; never touches the firmware.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROMAN = set('IVXLCDM')
THOUSANDS = True                                            # False = parser before the fix (bug reproduction)
THOUSANDS_MAX = 999999999                                   # LEX_NUMERO_DISPOSITIVO_MAX (contexto_juridico.h)


def _skip(b, i):
    while i < len(b):
        if b[i] in (0x20, 0x09):
            i += 1
        elif b[i] == 0xC2 and i + 1 < len(b) and b[i + 1] == 0xA0:
            i += 2
        else:
            break
    return i


def _prefix(b, i, pre):
    pre = pre.encode('latin-1') if isinstance(pre, str) else pre
    if i + len(pre) > len(b):
        return False
    return all((b[i + k] | 0x20 if 65 <= b[i + k] <= 90 else b[i + k]) == (c | 0x20 if 65 <= c <= 90 else c) for k, c in enumerate(pre))


def _delim(b, i):
    i = _skip(b, i)
    if i >= len(b) or b[i] in (ord('-'), ord(':'), ord('.'), 0x0D):
        return True
    return b[i] == 0xE2 and i + 2 < len(b) and b[i + 1] == 0x80 and b[i + 2] in (0x93, 0x94)


def _number(b, i):
    s = ''
    while i < len(b) and 48 <= b[i] <= 57:
        s += chr(b[i])
        i += 1
    if not s:
        return None, i
    # THOUSANDS_PARSER_FIX (DEVICE V1 build): '.' + exactly 3 digits after a 1-3 digit block is a thousands separator.
    if THOUSANDS and len(s) <= 3:
        value = int(s)
        while (i + 3 < len(b) and b[i] == ord('.') and all(48 <= b[i + k] <= 57 for k in (1, 2, 3))
               and not (i + 4 < len(b) and 48 <= b[i + 4] <= 57)):
            group = int(b[i + 1:i + 4])
            if value > (THOUSANDS_MAX - group) // 1000 or len(s) + 3 >= 16:
                return None, i                                   # overflow / capacity: fail safe (context untouched)
            value = value * 1000 + group
            s += b[i + 1:i + 4].decode()
            i += 4
    if i + 1 < len(b) and b[i] in (ord('-'), ord('.')) and chr(b[i + 1]).isalpha():
        s += chr(b[i]) + chr(b[i + 1]).upper()
        i += 2
    if i + 1 < len(b) and b[i] == 0xC2 and b[i + 1] in (0xBA, 0xAA):
        i += 2
    return s, i


def apply_line(c, line):
    """Mutates context dict c exactly like aplicarLinhaContextoJuridico (line = raw bytes of one physical line)."""
    i = _skip(line, 0)
    if _prefix(line, i, 'Art'):
        i += 6 if _prefix(line, i, 'Artigo') else 3
        if i < len(line) and line[i] == ord('.'):
            i += 1
        if i >= len(line) or line[i] not in (0x20, 0x09):
            return False
        v, i = _number(line, _skip(line, i))
        if v is None:
            return False
        c.update(artigo=v, paragrafo='', inciso='', alinea='')
        return True
    if i + 1 < len(line) and line[i] == 0xC2 and line[i + 1] == 0xA7:
        v, i = _number(line, _skip(line, i + 2))
        if v is None:
            return False
        c.update(paragrafo=v, inciso='', alinea='')
        return True
    after = None
    if _prefix(line, i, 'Paragrafo'):
        after = i + 9
    elif _prefix(line, i, b'Par\xc3\xa1grafo'):
        after = i + 10
    if after is not None:
        a = _skip(line, after)
        if _prefix(line, a, 'unico') or _prefix(line, a, b'\xc3\xbanico'):
            c.update(paragrafo='unico', inciso='', alinea='')
            return True
    if i + 1 < len(line) and 97 <= line[i] <= 122 and line[i + 1] == ord(')'):
        c.update(alinea=chr(line[i]))
        return True
    j, v = i, ''
    while j < len(line) and chr(line[j]).upper() in ROMAN and len(v) + 1 < 16:
        v += chr(line[j]).upper()
        j += 1
    if v and _delim(line, j):
        c.update(inciso=v, alinea='')
        return True
    return False


def to_target(c, namespace):
    if not c['artigo']:
        return None
    out = [namespace, f"ART.{c['artigo']}"]
    if c['paragrafo']:
        out.append('PAR.UNICO' if c['paragrafo'] == 'unico' else f"PAR.{c['paragrafo']}")
    if c['inciso']:
        out.append(f"INC.{c['inciso']}")
    if c['alinea']:
        out.append(f"AL.{c['alinea']}")
    return ':'.join(out)


def compare(text_map_path):
    """Replays the whole structural text through the ported parser and compares, on every mapped line, with CF88_TEXT_MAP.IDX."""
    header, rows = {}, []
    for l in Path(text_map_path).read_text(encoding='utf-8').splitlines():
        if l.startswith('#'):
            p = l[1:].split('|')
            header[p[0]] = p[1:]
        elif l:
            off, ln, tid = l.split('|')
            rows.append((int(off), int(ln), tid))
    if header.get('SOURCE_NAME', [''])[0] == 'CF88_RUNTIME.txt':
        # runtime map (A2B): the text is the overlay's own runtime file, checked against the header hash
        raw = (Path(text_map_path).parent.parent / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        import hashlib
        if hashlib.sha256(raw).hexdigest() != header['SOURCE_SHA256'][0]:
            raise ValueError('RUNTIME_TEXT_SHA256_MISMATCH')
    else:
        idx = json.loads((ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))
        raw = (ROOT / idx['source']['path']).read_bytes()
    ns_start = {k: int(v[0]) for k, v in ((k[len('NAMESPACE_START_'):], v) for k, v in header.items() if k.startswith('NAMESPACE_START_'))}
    lines = raw.split(b'\n')
    want = {ln: tid for _, ln, tid in rows}
    c = dict(artigo='', paragrafo='', inciso='', alinea='')
    agree, differ, namespace, pos = 0, [], 'CF88', 0
    for n, line in enumerate(lines, start=1):
        for ns, off in ns_start.items():
            if pos == off:
                namespace = ns
                c = dict(artigo='', paragrafo='', inciso='', alinea='')
        apply_line(c, line.rstrip(b'\r'))
        pos += len(line) + 1
        if n in want:
            got = to_target(c, namespace)
            exp = want[n]
            exp_cmp = exp[:-len(':CAPUT')] if exp.endswith(':CAPUT') else exp
            if got == exp_cmp:
                agree += 1
            else:
                differ.append(dict(line=n, text_map=exp, runtime_parser=got, text=line[:50].decode('utf-8', 'replace').strip()))
    cats = {}
    for d in differ:
        cats.setdefault(_category(d), []).append(d['line'])
    return dict(mapped_lines=len(want), agree=agree, differ=len(differ), agreement=round(agree / max(1, len(want)), 4),
                categories={k: len(v) for k, v in sorted(cats.items())}, examples=differ[:25])


def _category(d):
    tm, rp, tx = d['text_map'], d['runtime_parser'] or '', d['text']
    last = tm.split(':')[-1]
    if re.search(r'-[A-Z]$', last) and not rp.endswith(last):
        return 'SUFIXO_LETRA_NAO_LIDO (ex.: § 4º-A, I-A)'
    if re.match(r'^§\s*\d+\.º', tx) or rp.endswith('.Â'):
        return 'ORDINAL_COM_PONTO (ex.: § 2.º)'
    if re.match(r'^[IVXLCDM]+\s+[a-zà-ú]', tx):
        return 'INCISO_SEM_SEPARADOR (ex.: "I portadores")'
    if tm.startswith('ADCT') or rp.startswith('ADCT'):
        return 'ADCT'
    return 'OUTROS'


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p = sys.argv[1] if len(sys.argv) > 1 else HERE.parent / 'staging_sd_v1/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX'
    print(json.dumps(compare(p), ensure_ascii=False, indent=1))
