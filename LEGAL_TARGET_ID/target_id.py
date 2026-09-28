"""Canonical legal target_id grammar for LEX MACHINA (single source of truth).

Extends, without changing, the existing V2 `chave_dispositivo`/`device_id` format
(`CF88:ART.37:PAR.6:INC.I:AL.a`, `ADCT:ART.5`, `CF88:ART.40:PAR.UNICO`) used by thousands of frozen records.

Grammar (ASCII, no spaces, ':' separates levels, '.' separates label and value):

    target_id := NS
               | NS ":ART." ART [ ":CAPUT" | [":PAR." PAR] [":INC." INC [":AL." AL]] ]
    NS   := registered namespace   [A-Z][A-Z0-9]{1,15}          e.g. CF88, ADCT, CC2002
    ART  := [1-9][0-9]{0,3} ("-" [A-Z])?                          e.g. 5, 103-A
    PAR  := [1-9][0-9]{0,2} ("-" [A-Z])? | "UNICO"               e.g. 6, 4-A, UNICO
    INC  := canonical roman numeral ("-" [A-Z])?                  e.g. XXI, II-A
    AL   := [a-z] ("-" [A-Z])?                                    e.g. a

Semantics:
  * `CF88:ART.37` is the ARTICLE AS A UNIT; `CF88:ART.37:CAPUT` is only its caput. They are different targets.
  * Incisos without a paragraph belong to the caput. Their id keeps the V2 form (`CF88:ART.37:INC.XXI`, no CAPUT
    segment) and their structural parent is `CF88:ART.37:CAPUT`. `...:CAPUT:INC.I` is rejected as NON_CANONICAL.
  * A namespace may belong to a parent norm (ADCT -> CF88): `ADCT` and `CF88` are different targets and
    `parent("ADCT") == "CF88"`, so ADCT art. 5 (`ADCT:ART.5`) never collides with CF art. 5 (`CF88:ART.5`).
  * Parent is purely structural (breadcrumbs, aggregation). No legal inheritance is implied.
All functions fail closed with TargetIdError(code, detail).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
NAMESPACES_FILE = HERE / 'namespaces.json'

NS_RE = re.compile(r'[A-Z][A-Z0-9]{1,15}')
ART_RE = re.compile(r'[1-9][0-9]{0,3}(?:-[A-Z])?')
PAR_RE = re.compile(r'(?:[1-9][0-9]{0,2}(?:-[A-Z])?|UNICO)')
ROMAN_RE = re.compile(r'(?=[MDCLXVI])M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})')
INC_RE = re.compile(ROMAN_RE.pattern + r'(?:-[A-Z])?')
AL_RE = re.compile(r'[a-z](?:-[A-Z])?')
MAX_LEN = 64

KINDS = ('NORMA', 'NAMESPACE', 'ARTIGO', 'CAPUT', 'PARAGRAFO', 'PARAGRAFO_UNICO', 'INCISO', 'ALINEA')


class TargetIdError(ValueError):
    def __init__(self, code, detail=''):
        super().__init__(f'{code}: {detail}' if detail else code)
        self.code = code
        self.detail = detail


class NamespaceRegistry:
    """Namespaces = norm ids from the master catalog + explicit sub-namespaces (e.g. ADCT inside CF88)."""

    def __init__(self, norms, subnamespaces):
        self.norms = set(norms)
        self.sub = dict(subnamespaces)
        clash = self.norms & set(self.sub)
        if clash:
            raise TargetIdError('NAMESPACE_CONFLICT', ','.join(sorted(clash)))
        for ns, cfg in self.sub.items():
            if cfg['parent'] not in self.norms:
                raise TargetIdError('NAMESPACE_PARENT_UNKNOWN', ns)
        for ns in self.norms | set(self.sub):
            if not NS_RE.fullmatch(ns):
                raise TargetIdError('NAMESPACE_MALFORMED', ns)

    @classmethod
    def load(cls, path=NAMESPACES_FILE):
        cfg = json.loads(Path(path).read_text(encoding='utf-8'))
        catalog = REPO / cfg['norm_catalog']
        norms = [item['id'] for item in json.loads(catalog.read_text(encoding='utf-8'))['itens']]
        return cls(norms, cfg['subnamespaces'])

    def known(self, ns):
        return ns in self.norms or ns in self.sub

    def parent(self, ns):
        return self.sub[ns]['parent'] if ns in self.sub else None

    def norm_of(self, ns):
        return self.sub[ns]['parent'] if ns in self.sub else ns


_DEFAULT = None


def registry():
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = NamespaceRegistry.load()
    return _DEFAULT


def parse_target_id(target_id, reg=None):
    """Parse a canonical target_id into its components. Raises TargetIdError (fail closed)."""
    reg = reg or registry()
    if not isinstance(target_id, str) or not target_id:
        raise TargetIdError('EMPTY')
    if len(target_id) > MAX_LEN:
        raise TargetIdError('TOO_LONG', str(len(target_id)))
    if not target_id.isascii():
        raise TargetIdError('NON_ASCII', target_id)
    if any(c in target_id for c in ' /\\\t\r\n') or target_id.lower().endswith(('.txt', '.json', '.idx')):
        raise TargetIdError('PATH_OR_WHITESPACE', target_id)
    parts = target_id.split(':')
    if any(p == '' for p in parts):
        raise TargetIdError('EMPTY_SEGMENT', target_id)
    ns = parts[0]
    if not NS_RE.fullmatch(ns):
        raise TargetIdError('NAMESPACE_MALFORMED', ns)
    if not reg.known(ns):
        raise TargetIdError('UNKNOWN_NAMESPACE', ns)
    out = dict(namespace=ns, norma_id=reg.norm_of(ns), article=None, caput=False, paragraph=None, inciso=None, alinea=None)
    order = ['ART', 'CAPUT', 'PAR', 'INC', 'AL']
    last = -1
    for seg in parts[1:]:
        label, dot, value = seg.partition('.')
        if seg == 'CAPUT':
            label, value = 'CAPUT', None
        elif reg.known(seg):
            raise TargetIdError('NESTED_NAMESPACE', f'{seg} is a root namespace (e.g. ADCT:ART.5, parent CF88): {target_id}')
        elif not dot or not value:
            raise TargetIdError('MALFORMED_SEGMENT', seg)
        if label not in order:
            raise TargetIdError('UNKNOWN_LEVEL', seg)
        pos = order.index(label)
        if pos <= last:
            raise TargetIdError('LEVEL_ORDER', target_id)
        if label != 'ART' and out['article'] is None:
            raise TargetIdError('MISSING_ARTICLE', target_id)
        if label == 'ART':
            if not ART_RE.fullmatch(value):
                raise TargetIdError('INVALID_ARTICLE', value)
            out['article'] = value
        elif label == 'CAPUT':
            out['caput'] = True
        elif label == 'PAR':
            if not PAR_RE.fullmatch(value):
                raise TargetIdError('INVALID_PARAGRAPH', value)
            out['paragraph'] = value
        elif label == 'INC':
            if not INC_RE.fullmatch(value):
                raise TargetIdError('INVALID_INCISO', value)
            out['inciso'] = value
        elif label == 'AL':
            if out['inciso'] is None:
                raise TargetIdError('ALINEA_WITHOUT_INCISO', target_id)
            if not AL_RE.fullmatch(value):
                raise TargetIdError('INVALID_ALINEA', value)
            out['alinea'] = value
        last = pos
    if out['caput'] and (out['paragraph'] or out['inciso']):
        raise TargetIdError('NON_CANONICAL', 'CAPUT is terminal; caput incisos are written without CAPUT: ' + target_id)
    out['kind'] = kind_of(out, reg)
    return out


def kind_of(t, reg=None):
    reg = reg or registry()
    if t['article'] is None:
        return 'NAMESPACE' if reg.parent(t['namespace']) else 'NORMA'
    if t['alinea']:
        return 'ALINEA'
    if t['inciso']:
        return 'INCISO'
    if t['paragraph']:
        return 'PARAGRAFO_UNICO' if t['paragraph'] == 'UNICO' else 'PARAGRAFO'
    if t['caput']:
        return 'CAPUT'
    return 'ARTIGO'


def format_target_id(namespace, article=None, caput=False, paragraph=None, inciso=None, alinea=None, reg=None):
    """Build a canonical target_id from already-normalized components and validate it."""
    parts = [namespace]
    if article is not None:
        parts.append('ART.' + str(article))
    if caput:
        parts.append('CAPUT')
    if paragraph is not None:
        parts.append('PAR.' + str(paragraph))
    if inciso is not None:
        parts.append('INC.' + str(inciso))
    if alinea is not None:
        parts.append('AL.' + str(alinea))
    tid = ':'.join(parts)
    parse_target_id(tid, reg)
    return tid


def parent_target_id(target_id, reg=None):
    """Structural parent (None for a root norm)."""
    reg = reg or registry()
    t = parse_target_id(target_id, reg)
    ns = t['namespace']
    if t['alinea']:
        return format_target_id(ns, t['article'], paragraph=t['paragraph'], inciso=t['inciso'], reg=reg)
    if t['inciso']:
        if t['paragraph']:
            return format_target_id(ns, t['article'], paragraph=t['paragraph'], reg=reg)
        return format_target_id(ns, t['article'], caput=True, reg=reg)
    if t['paragraph'] or t['caput']:
        return format_target_id(ns, t['article'], reg=reg)
    if t['article']:
        return ns
    return reg.parent(ns)


def ancestors(target_id, reg=None):
    chain, cur = [], parent_target_id(target_id, reg)
    while cur:
        chain.append(cur)
        cur = parent_target_id(cur, reg)
    return chain


def validate_target_id(target_id, reg=None):
    """Return (True, None) or (False, error_code). Never raises."""
    try:
        parse_target_id(target_id, reg)
        return True, None
    except TargetIdError as exc:
        return False, exc.code


ROMAN_VALUES = dict(M=1000, D=500, C=100, L=50, X=10, V=5, I=1)


def roman_to_int(roman):
    """Canonical roman numeral (optionally with '-A' suffix ignored) -> int. Fails closed."""
    base = roman.split('-')[0]
    if not ROMAN_RE.fullmatch(base):
        raise TargetIdError('INVALID_ROMAN', roman)
    total = 0
    for i, ch in enumerate(base):
        v = ROMAN_VALUES[ch]
        total += -v if i + 1 < len(base) and ROMAN_VALUES[base[i + 1]] > v else v
    return total


# ---------------------------------------------------------------- source-label normalization
ORD_RE = re.compile(r'^\s*(\d{1,4})\s*(?:º|°|o|ª)?\s*(?:-\s*([A-Za-z]))?\s*$')


def normalize_number_label(label):
    """'1º', '1o', '1', '4º-A', '103-A' -> '1', '4-A', '103-A'. Fails closed on anything else."""
    m = ORD_RE.match(label or '')
    if not m or m.group(1).startswith('0'):
        raise TargetIdError('UNRECOGNIZED_NUMBER_LABEL', repr(label))
    return m.group(1) + ('-' + m.group(2).upper() if m.group(2) else '')


def normalize_paragraph_label(label):
    s = (label or '').strip().rstrip('.').strip()
    if re.fullmatch(r'(?i)par[aá]grafo\s+[uú]nico', s) or s.upper() == 'UNICO':
        return 'UNICO'
    s = re.sub(r'^§\s*', '', s)
    return normalize_number_label(s)


def normalize_inciso_label(label):
    s = (label or '').strip().upper().replace(' ', '')
    if not INC_RE.fullmatch(s):
        raise TargetIdError('UNRECOGNIZED_INCISO_LABEL', repr(label))
    return s


def normalize_alinea_label(label):
    s = (label or '').strip().rstrip(')').strip()
    if not AL_RE.fullmatch(s):
        raise TargetIdError('UNRECOGNIZED_ALINEA_LABEL', repr(label))
    return s


# ---------------------------------------------------------------- converters from other existing serializations
def from_pipe_fields(norma, artigo, paragrafo='', inciso='', alinea='', reg=None):
    """SD lookup IDX rows: 'CF88|5||XLIII|' ; paragraph 'unico' accepted as used by the firmware."""
    par = None
    if paragrafo:
        par = 'UNICO' if paragrafo.strip().lower() in ('unico', 'único') else normalize_number_label(paragrafo)
    return format_target_id(norma, normalize_number_label(artigo), paragraph=par, inciso=normalize_inciso_label(inciso) if inciso else None,
                            alinea=normalize_alinea_label(alinea) if alinea else None, reg=reg)


def from_colon_fields(fields, reg=None):
    """Jurisprudence ids tail 'CF88:1:-:III:-' (norma:art:par:inc:ali, '-' = absent)."""
    parts = fields.split(':')
    if len(parts) != 5:
        raise TargetIdError('MALFORMED_COLON_FIELDS', fields)
    norma, art, par, inc, ali = [None if x in ('-', '') else x for x in parts]
    return from_pipe_fields(norma, art, par or '', inc or '', ali or '', reg)


def to_pipe_fields(target_id, reg=None):
    """Inverse view for the ESP32 lookup format (paragraph 'unico' as the firmware expects)."""
    t = parse_target_id(target_id, reg)
    par = 'unico' if t['paragraph'] == 'UNICO' else (t['paragraph'] or '')
    return '|'.join([t['namespace'], t['article'] or '', par, t['inciso'] or '', t['alinea'] or ''])
