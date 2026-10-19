"""CC MASS AUDIT — host-only quality gate over the 932 qualified candidate relations of the CC mass discovery (no ratification, no deploy).

Reads only what the night operation produced (CC_MASS_DISCOVERY/*.jsonl, the source indexes and their hashes) and writes the audit layer:
one structured audit row per relation (identity, target, namespace, temporality, merits, pertinence, duplication, conflicts, authority),
an authority classification independent of extraction confidence, the Turma corroboration / best-representative study, the deterministic
deep-audit sample (reviewed by hand in cc_mass_deep_audit_review.py), the editorial states for ratification (never a human decision) and
the ratification packets. Idempotent; `--check` compares every output byte for byte.
Usage: python build_cc_mass_audit.py [--check] [--print-sample]
"""
import collections
import hashlib
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import build_cc_mass_discovery as B  # noqa: E402
import batch_engine as E  # noqa: E402
from cc_mass_deep_audit_review import DEEP_REVIEW, SYSTEMIC_FINDINGS  # noqa: E402

D = B.OUT
RUN_DATE = '2026-10-19'
INPUT_COUNT = 932
TURMA = 'STJ_ESPELHOS_TURMAS'
OFFICIAL_HOSTS = ('stj.jus.br', 'stf.jus.br', 'planalto.gov.br')
QUALIFIED_KINDS = {'REPETITIVO', 'IAC', 'SIRDR', 'RG', 'ADI', 'ADC', 'ADPF', 'ADO'}
SECAO = ('SEGUNDA SEÇÃO', 'PRIMEIRA SEÇÃO', 'TERCEIRA SEÇÃO', 'CORTE ESPECIAL')
TURMAS = ('TERCEIRA TURMA', 'QUARTA TURMA')
STOP = set('a o os as de da do das dos e em no na nos nas um uma por para com sem que se ao aos à às ou é são ser foi pelo pela pelos pelas '
           'art arts artigo código civil cc lei não sua seu suas seus como mais sobre entre deve está esta este essa esse isso caso'.split())
NEG = re.compile(r'\bn[ãa]o\s+(?:se\s+)?(?:aplica|incide|incid|se\s+aplica)|\binaplic[áa]vel|\binaplicabilidade|\bafast(?:a|ou|ada|ado|ar)\b|'
                 r'\bn[ãa]o\s+(?:h[áa]|configura|se\s+configura)\b', re.I)


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding='utf-8').splitlines() if l.strip()]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def num_of(target):
    art = E.T.parse_target_id(target)['article']
    m = re.match(r'(\d+)(.*)', art)
    return f"{int(m.group(1)):,}".replace(',', '.') + m.group(2)


def num_pattern(target):
    """'1.597' or '1597' (ementas write both); the suffix ('-B') kept."""
    n = num_of(target)
    m = re.match(r'([\d.]+)(.*)', n)
    digits = m.group(1).replace('.', '')
    core = digits if len(digits) < 4 else digits[:-3] + r'\.?' + digits[-3:]
    return r'(?<![\d.])' + core + re.escape(m.group(2)) + r'(?![\d])(?!\.\d)'


def mentions(text, target):
    return [h.start() for h in re.finditer(num_pattern(target), text or '')]


def sentence_at(text, h, back=260, fwd=200):
    """The sentence around a mention (abbreviation dots are not sentence ends)."""
    a = max(0, h - back)
    pre = re.sub(r'\b(arts?|n|fls?|inc|par|al|min|rel)\.', lambda m: m.group(1) + '․', text[a:h], flags=re.I)
    cut = max(pre.rfind('. '), pre.rfind('; '))
    start = a + cut + 2 if cut >= 0 else a
    post = re.sub(r'\b(arts?|n|fls?|inc|par|al|min|rel)\.', lambda m: m.group(1) + '․', text[h:h + fwd], flags=re.I)
    ends = [i for i in (post.find('. '), post.find('; ')) if i >= 0]
    end = min(ends) if ends else -1
    return text[start:h + (end if end >= 0 else len(post))].strip()


def tokens(s):
    return {w for w in re.findall(r'[a-záéíóúâêôãõçà]{4,}', s.lower()) if w not in STOP}


# ------------------------------------------------------------------ sources (reused, hash-checked)
def sources():
    inv = B.load(D / 'CC_MASS_SOURCE_INVENTORY.json')['completed']
    for k, v in inv.items():                     # the indexes the discovery used, unchanged
        p = HERE / v['path']
        assert p.is_file() and B.sha_file(p) == v['sha256'], f'fonte alterada ou ausente: {k}'
    esp = {}
    for k in B.ESPELHO_SOURCES:
        for e in B.load(B.SOURCES[k])['entries']:
            esp[(k, e['espelho_id'])] = e
    stf = collections.defaultdict(list)
    for e in B.load(B.SOURCES['STF_JURISPRUDENCIA'])['entries']:
        stf[e['source_document_id']].append(e)
    prec = {e['id']: e for e in B.load(B.SOURCES['STJ_PRECEDENTES_QUALIFICADOS'])['entries']}
    sums = {str(e['number']): e for e in B.load(B.SOURCES['STJ_SUMULAS_PDF'])['entries']}
    return inv, esp, stf, prec, sums


def docs_of(x, raw, esp, stf, prec, sums):
    """Official documents behind a relation: list of dict(kind, id, orgao, date, text fields, url, hash)."""
    out = []
    for rid in x['raw_ids']:
        r = raw[rid]
        src = r['source']
        if src in B.ESPELHO_SOURCES:
            eid = re.match(r'espelho (\S+)', r['source_document_id']).group(1)
            e = esp[(src, eid)]
            out.append(dict(src=src, kind='ESPELHO', doc_id=e['id'], espelho=eid, registro=e['registro'], sigla=e['sigla'], number=e['number'],
                            orgao=e['orgao'], relator=e['relator'], date=B.iso_date(e['julgamento']), pub=e['publicacao'], ementa=e['ementa'],
                            tese=e['tese'], temas=e['temas'], url=r['source_url'], file_sha=e['file_sha256'], field=r['evidence_field'],
                            method=r['discovery_method'], leading=r.get('leading_case')))
        elif src == 'STF_JURISPRUDENCIA':
            sid = re.search(r'\(([^()]+)\)\s*$', r['source_document_id']).group(1)      # sjurNNNN or repercussao-geralNNNN
            for e in stf[sid]:
                out.append(dict(src=src, kind='STF', doc_id=e['id'], titulo=e['titulo'], orgao=e['orgao'], date=e['julgamento'], tese=e['tese'],
                                ementa=e['ementa'], url=e['url'], rg_merito=e['rg_merito'], incidente=e['incidente'], tema=e['tema'],
                                obs=e['observacao'], field=r['evidence_field'], method=r['discovery_method']))
        elif src == 'STJ_PRECEDENTES_QUALIFICADOS':
            e = prec[r['precedent_id']]
            out.append(dict(src=src, kind='PRECEDENTE', doc_id=e['id'], orgao=e['orgao'], date=B.iso_date(e['data_julgamento']), tese=e['tese'],
                            questao=e['questao'], situacao=e['situacao'], url=r['source_url'], field=r['evidence_field'], method=r['discovery_method']))
        elif src == 'STJ_SUMULAS_PDF':
            e = sums[x['precedent_number']]
            out.append(dict(src=src, kind='SUMULA', doc_id=x['precedent_id'], orgao=e['orgao'], date=B.iso_date(e['data_decisao']),
                            enunciado=e['enunciado'], status=e['status'], url=r['source_url'], field=r['evidence_field'], method=r['discovery_method']))
        else:
            out.append(dict(src=src, kind='PLANALTO', doc_id=x['precedent_id'], url=r['source_url'], field=r['evidence_field'], method=r['discovery_method']))
    seen, uniq = set(), []
    for d in out:
        k = (d['src'], d['doc_id'], d.get('espelho'))
        if k not in seen:
            seen.add(k)
            uniq.append(d)
    return uniq


# ------------------------------------------------------------------ evidence location (where in the official text the article is named)
CC_MARK = re.compile(r'C[óo]digo\s+Civil|\bCCB?\s*(?:1\.?916|16)\b|\bCCB?\b|\bCCB?\s*/|CC-0?2|\bmesmo\s+(?:diploma|c[óo]digo|codex)|desse\s+[úu]ltimo\s+diploma|novo\s+C[óo]digo', re.I)
OTHER_MARK = re.compile(r'\bCPC\b|\bCDC\b|\bCLT\b|\bCF\b|Constitui[çc][ãa]o|\bLei\b|\bLei\s+n|Decreto|\bLINDB\b|\bLICC\b|\bECA\b|Estatuto|RISTJ|'
                        r'S[úu]mula|C[óo]digo\s+(?:de\s+Processo|Tribut|Penal|Comercial|de\s+Defesa|Florestal|Brasileiro\s+de\s+Aeron)|CTN|CCo', re.I)
ADMISS_SENT = re.compile(r's[úu]mulas?\s*(?:n[º°.]*\s*)?(?:5|7|211|282|283|284|356|518)\b|prequestion|n[ãa]o\s+(?:foi|foram)\s+(?:apreciad|examinad|debatid|enfrentad)|'
                         r'n[ãa]o\s+se\s+manifestou|reexame|revolvimento|acervo\s+f[áa]tico|carece\s+de\s+pertin[êe]ncia|defici[êe]ncia\s+(?:de\s+)?fundamenta|'
                         r'dispositivos?\s+invocad|alegad[oa]s?\s+(?:viola|ofens|contrar)|[óo]bices?\b|premissas?\s+f[áa]tic|sem\s+altera[çc][ãa]o\s+d[ao]|'
                         r'\baleg(?:a|ou|am|aram|ando)\b|\bsustent(?:a|ou|am|aram|ando)\b|\bargument(?:a|ou|am)\b|\bpretende\b|\bpostula|'
                         r'\bprejudicad[oa]|\bpleite(?:a|ou|am|aram|ando)\b|\brequere(?:u|ram)\b|\bformul(?:ou|aram)\s+(?:pedido|peti)', re.I)
QUESTION_SENT = re.compile(r'saber\s+se\b|(?:prop[óo]sito|objetivo)\s+recursal|cinge-se|controv[ée]rsia(?:\s+\w+){0,2}\s+(?:resume-se|consiste|reside|cinge)|'
                           r'(?:definir|decidir|determinar|perquirir|examinar|verificar)\s+se\b|discute-se\s+(?:se|a)|quest[ãa]o\s+(?:controvertida|em\s+discuss)|'
                           r'\b(?:o|a)\s+(?:ac[óo]rd[ãa]o\s+(?:recorrido|de\s+apela[çc][ãa]o|estadual|local|embargado)|Tribunal\s+(?:de\s+origem|a\s+quo|local|estadual)|'
                           r'Corte\s+(?:de\s+origem|local|estadual)|decisum|senten[çc]a|inst[âa]ncias?\s+ordin[áa]rias)\b[^.;]{0,120}?\b(?:reconhec|mant|entend|conclu|'
                           r'aplic|julg|consign|fix|determin|conden|deferiu|indeferiu|afastou)', re.I)
ENUM_CLAIM = re.compile(r'\b(?:contraria[m]?|viola[m]?|violou|ofende[m]?|afronta[m]?|houve\s+viola|h[áa]\s+viola|incid(?:e|iria)\s+o\s+art)', re.I)
ENUM_INTRO = re.compile(r'quest(?:[ãa]o|[õo]es)\s+em\s+discuss|consiste[m]?\s+em|saber\s+se|\baleg|sustent|tese[s]?\s+(?:do|da)\s+recorrente|recorrente\s+(?:defende|aponta)', re.I)
TESE_MARK = re.compile(r'Tese\s+de\s+julgamento|Teses?\s+fixadas?|Para\s+os\s+fins\s+do\s+art\.\s*(?:543-C|1\.03[69])|tese\s+jur[íi]dica', re.I)


OLD_CODE = re.compile(r'^\s*(?:de\s+|/\s*|-\s*)?(?:1\.?916|16\b)|^\s*(?:antigo|anterior|revogado|velho|de\s+Bevil[áa]qua)|^\s*Bevil', re.I)
OLD_BEFORE = re.compile(r'(?:antigo|anterior|revogado|velho)\s+$', re.I)
FOREIGN = re.compile(r'^\s*(?:franc[êe]s|alem[ãa]o|portugu[êe]s|italian[oa]|argentin[oa]|espanhol|su[íi][çc]o|chileno|uruguai[oa]|japon[êe]s|'
                     r'quebequense|de\s+Napole[ãa]o|da\s+(?:Fran[çc]a|Alemanha|It[áa]lia|Argentina|Espanha|Su[íi][çc]a)|de\s+Portugal)', re.I)
AMENDING = re.compile(r'(?:introduzid|acrescentad|acrescid|inclu[íi]d|alterad|reda[çc][ãa]o\s+dada)[oa]s?\s+(?:pela|pelo)\s*$', re.I)
SEP = re.compile(r';|\)|\.\s')


def attribution(text, h, num, others=()):
    """Which law the article number at h belongs to: 'CC', 'CC1916', 'FOREIGN', 'OTHER_LAW' or 'UNATTRIBUTED'.
    - forward, inside the same clause (up to ';' or sentence end, abbreviation dots excluded): the first law mark decides; the amending law
      ('introduzido pela Lei 10.931') is not another law;
    - backward (list / parenthetical form 'CC/2002, art. 1.619; Lei 8.069, art. 45', 'CÓDIGO CIVIL, ARTS. 334 A 339. CPC'): a code mark before
      the number in the same sentence with no other law mark between decides, when the forward mark only comes after a separator;
    - no mark either way (header 'INAPLICABILIDADE DO ART. 618'): CC only when the same number is attributed to the CC elsewhere in the text."""
    end = h + len(re.match(r'[\d.]+[-A-Z]*', text[h:]).group(0))
    fwd = text[end:end + 120]
    norm = re.sub(r'\b(arts?|incs?|par|al|n|fls?|c/c)\.', lambda m: m.group(1) + ' ', fwd, flags=re.I)
    stop = re.search(r';|\.\s|\.$|\(', norm)
    clause = fwd[:stop.start()] if stop else fwd
    mc = CC_MARK.search(clause)
    mo = next((m for m in OTHER_MARK.finditer(clause) if not AMENDING.search(clause[:m.start()])), None)
    if mc and (not mo or mc.start() < mo.start()):
        return code_identity(text, end + mc.start(), end + mc.end())
    back = text[max(0, h - 140):h]
    cut = max(back.rfind('. '), back.rfind('; '))
    back = back[cut + 1:] if cut >= 0 and not re.search(r'arts?\.\s*$', back[:cut + 2], re.I) else back
    cs = list(CC_MARK.finditer(back))
    if cs and not OTHER_MARK.search(back[cs[-1].end():]):
        code = code_identity(text, h - len(back) + cs[-1].start(), h - len(back) + cs[-1].end())
        if not mo:
            return code
    if mo:
        return 'OTHER_LAW'
    return 'CC' if 'CC' in others else 'UNATTRIBUTED'


def cc_attributed(text, h, num, others=()):
    return attribution(text, h, num, others) == 'CC'


def code_identity(text, a, b):
    """Which civil code a CC mark at text[a:b] names: 'CC', 'CC1916' ('antigo/anterior/revogado Código Civil', 'Código Civil de 1.916',
    'CC/16'), 'FOREIGN' ('Código Civil Francês', 'BGB'), or the code a 'mesmo diploma/codex' points back to."""
    mark, after, before = text[a:b], text[b:b + 30], text[max(0, a - 25):a]
    if re.search(r'mesmo|desse|deste', mark, re.I):
        o = max(0, a - 400)
        prev = [m for m in CC_MARK.finditer(text[o:a]) if not re.search(r'mesmo|desse|deste', m.group(0), re.I)]
        other = list(OTHER_MARK.finditer(text[o:a]))
        if other and (not prev or other[-1].start() > prev[-1].start()):
            return 'OTHER_LAW'                                  # 'art. 56 do mesmo diploma' after 'Decreto n. 2.044/1908'
        if prev:
            return code_identity(text, o + prev[-1].start(), o + prev[-1].end())
        return 'CC'
    if re.search(r'/\s*1\.?916|/\s*16\b|-16\b|^CCB?\s*(?:1\.?916|16)\b', mark + after[:8]) or OLD_CODE.search(after) or OLD_BEFORE.search(before):
        return 'CC1916'
    if FOREIGN.search(after) or re.search(r'\bBGB\b|Code\s+civil', mark + after[:12], re.I):
        return 'FOREIGN'
    return 'CC'


def locate(text, target, header_end=None, discards=None):
    """Zones of the CC mentions of the target's article in one text: TESE, HOLDING, HEADER, CLAIM, LIST. Mentions that belong to another law,
    to the CC/1916 or to a foreign code are left out and counted in `discards` (the systemic-error ledger)."""
    num = num_of(target)
    zones = [(z.start(1), z.end(1)) for z in B.CLAIM_ZONE.finditer(text)]
    hl = B.HOLDING_LIST.search(text)
    tm = TESE_MARK.search(text)
    first_item = re.search(r'(?:^|\s)(?:1\s*[.\-–)]|I\.?\s*[-–]?\s*CASO EM EXAME)\s', text)
    head_end = header_end if header_end is not None else (first_item.start() if first_item else 0)
    out = []
    hits = mentions(text, target)
    attr = {h: attribution(text, h, num) for h in hits}
    anycc = any(v == 'CC' for v in attr.values())
    old_elsewhere = any(v == 'CC1916' for v in attr.values())          # F11
    for h in hits:
        code = attr[h] if attr[h] != 'UNATTRIBUTED' or not anycc else 'CC'
        if code == 'CC' and old_elsewhere and not EXPLICIT_2002.search(text[h:h + 60]):
            code = 'CC1916'                                     # the same number is the CC/1916's elsewhere in the text ('art. 1178 do CC16')
        if code != 'CC':
            if discards is not None:
                discards[code] += 1
            continue
        if hl and h > hl.start():
            out.append(('LIST', h))
            continue
        window = re.sub(r'\b(arts?|n|fls?|inc|par|al)\.', r'\1', text[max(0, h - 160):h], flags=re.I)
        window = window[max(window.rfind('. '), window.rfind('; ')) + 1:]
        if any(a <= h < b for a, b in zones) or B.CLAIM_CUE.search(window):
            out.append(('CLAIM', h))
        elif ADMISS_SENT.search(sentence_at(text, h)):                 # the bar may come after the mention in the same sentence
            out.append(('CLAIM', h))
            if discards is not None:
                discards['ADMISSIBILITY_IN_SENTENCE'] += 1
        elif QUESTION_SENT.search(sentence_at(text, h)) or (re.match(r'\(?\s*(?:i{1,3}|iv|v|vi{1,3})\s*\)', sentence_at(text, h), re.I) and
                                                            (ENUM_INTRO.search(text[max(0, h - 1500):h]) or ENUM_CLAIM.search(sentence_at(text, h)))):
            out.append(('QUESTION', h))                                 # the question / the decision under appeal, not this court's holding
            if discards is not None:
                discards['QUESTION_OR_NARRATIVE'] += 1
        elif tm and h > tm.start():
            out.append(('TESE', h))
        elif h < head_end:
            out.append(('HEADER', h))
        else:
            out.append(('HOLDING', h))
    return out


def evidence(x, docs):
    """Best evidence of the relation across its documents: level, zone list, the quoted sentence and the doc it comes from."""
    best, rank = None, {'TESE': 5, 'ENUNCIADO': 5, 'HOLDING': 4, 'HEADER': 3, 'QUESTAO': 2, 'QUESTION': 2, 'LIST': 1, 'CLAIM': 0}
    zones_all, discards = [], collections.Counter()
    for d in docs:
        texts = []
        if d['kind'] == 'ESPELHO':
            texts = [('ementa', d['ementa']), ('tese', d['tese'])]
        elif d['kind'] == 'STF':
            texts = [('tese', d['tese']), ('ementa', d['ementa'])]
        elif d['kind'] == 'PRECEDENTE':
            texts = [('tese', d['tese']), ('questao', d['questao'])]
        elif d['kind'] == 'SUMULA':
            texts = [('enunciado', d['enunciado'])]
        for field, t in texts:
            if not t:
                continue
            t = re.sub(r'\s+', ' ', t)
            for z, h in locate(t, x['target_id'], header_end=0 if field != 'ementa' else None, discards=discards):
                z = 'QUESTAO' if field == 'questao' else ({'tese': 'TESE', 'enunciado': 'ENUNCIADO'}.get(field, z) if z not in ('CLAIM', 'LIST') else z)
                if d['kind'] == 'STF' and field == 'ementa' and z == 'HOLDING' and d.get('tese'):
                    z = 'HOLDING'
                zones_all.append(z)
                cand = (rank[z], d.get('date') or '', field, sentence_at(t, h), d)
                if best is None or cand[:2] > best[:2]:
                    best = cand
    if best is None:
        return dict(level='STRUCTURED_ONLY' if any('STRUCTURED' in d['method'] for d in docs) else 'NOT_FOUND', zones=[], quote='', doc=None, field=None,
                    discards=dict(discards))
    lvl = {5: 'DIRECT_THESIS', 4: 'DIRECT_HOLDING', 3: 'HEADER', 2: 'QUESTION_ONLY', 1: 'LIST_ONLY', 0: 'CLAIM_ONLY'}[best[0]]
    letters = re.sub(r'[^A-Za-zÀ-ÿ]', '', best[3])
    bare = re.sub(r'(?i)\b(?:arts?\.?|artigos?|d[oa]s?|e|c/c|§+|par[áa]grafo|[úu]nico|inc(?:iso)?\.?|caput|C[óo]digo\s+Civil|CC(?:/0?2|/2002|-02)?|de\s+2002)\b'
                  r'|[\d.º°ª,;:()\-–IVXL]', '', best[3]).strip()
    if lvl == 'DIRECT_HOLDING' and ((letters and letters == letters.upper() and len(best[3]) < 120) or (len(best[3]) < 60 and not bare)):
        lvl = 'HEADER'                                                  # 'ART. 157 DO CC/02' / 'Art. 522 do Código Civil': a heading
    return dict(level=lvl, zones=sorted(set(zones_all)), quote=best[3][:420], doc=best[4], field=best[2], discards=dict(discards))


# ------------------------------------------------------------------ merits, temporality, authority
FINAL_STJ = re.compile(r'Tr[âa]nsito|Ac[óo]rd[ãa]o\s+Publicado|Julgado|Mérito\s+Julgado', re.I)
PENDING = re.compile(r'Afetado|Pendente|Sobrestado|Em\s+Julgamento|RE\s+Pendente', re.I)


def merits(x, docs):
    """MERITS / NO_MERIT / PENDING / UNKNOWN with the reason."""
    k = x['classe']
    if k == 'SUMULA':
        st = ' '.join(d.get('status') or '' for d in docs)
        return ('MERITS', 'súmula ' + (st or 'vigente')) if 'CANCEL' not in st.upper() else ('NO_MERIT', 'súmula cancelada')
    if k in ('REPETITIVO', 'IAC', 'SIRDR'):
        st = x['status_text']
        if PENDING.search(st) and not FINAL_STJ.search(st):
            return ('PENDING', f'tema {st.strip()[:60]}')
        tese = any((d.get('tese') or '').strip() for d in docs if d['kind'] == 'PRECEDENTE')
        lead = [d for d in docs if d['kind'] == 'ESPELHO']
        if tese or lead:
            return ('MERITS', 'tese firmada' if tese else 'acórdão paradigma com mérito')
        return ('UNKNOWN', 'sem tese nem acórdão paradigma capturados')
    if x['tribunal'] == 'STF':
        if k == 'RG':
            return ('MERITS', 'mérito de repercussão geral') if any(str(d.get('rg_merito')) == 'True' for d in docs) else ('UNKNOWN', 'RG sem mérito confirmado')
        txt = ' '.join((d.get('ementa') or '')[-600:] for d in docs)
        if re.search(r'n[ãa]o\s+conhecid|prejudicad|extin[çc][ãa]o\s+sem', txt, re.I) and not re.search(r'procedente|improcedente|interpreta[çc][ãa]o\s+conforme', txt, re.I):
            return ('NO_MERIT', 'ação não conhecida/prejudicada')
        return ('MERITS', 'controle concentrado julgado')
    txt = ' '.join(d.get('ementa') or '' for d in docs)
    if B.NOT_KNOWN.search(txt) and not B.MERIT_VERB.search(txt):
        return ('NO_MERIT', 'recurso não conhecido sem provimento/desprovimento')
    if B.NOT_KNOWN.search(txt) and B.ADMISSIBILITY.search(txt):
        return ('MERITS', 'conhecido em parte; mérito em parte')
    return ('MERITS', 'recurso conhecido e julgado')


EXPLICIT_2002 = re.compile(r'CC\s*/?\s*(?:2002|02)\b|CC-02|C[óo]digo\s+Civil\s+(?:de\s+|/\s*)?2002|novo\s+C[óo]digo|atual\s+C[óo]digo|C[óo]digo\s+(?:Civil\s+)?(?:atual|vigente)|10\.406|CCB\s*/\s*2002', re.I)


def temporal(x, docs, amend, ev=None, arts=None):
    f = set(x['flags'])
    jd = B.iso_date(x['judgment_date']) or next((d['date'] for d in docs if d.get('date')), None)
    if jd and jd < '2003-01-11':
        return 'PRE_CC2002', jd
    if ev and arts is not None and jd and jd < '2011-01-01' and ev['level'] not in ('NOT_FOUND', 'STRUCTURED_ONLY') and \
            not EXPLICIT_2002.search(ev['quote']) and subject_overlap(ev['quote'], x['target_id'], arts)[0] == 0:
        return 'AMBIGUOUS_CODE_NAMESPACE', jd                           # 'do Código Civil' in a 2003-2010 judgment, subject foreign to the CC/2002 article
    if 'CORRESPONDENCIA_CC1916' in f:
        return 'CC1916_CORRESPONDENCE', jd
    if 'POSSIVEL_REGIME_CC1916' in f or 'PRECEDENTE_ANTERIOR_AO_CC2002' in f:
        return 'POSSIBLE_CC1916', jd
    art = E.T.format_target_id(B.NORM, E.T.parse_target_id(x['target_id'])['article'])
    notes = amend.get(x['target_id'], []) + (amend.get(art, []) if art != x['target_id'] else [])
    if 'REDACAO_ALTERADA_APOS_JULGAMENTO' in f or (jd and any(a['year'] > int(jd[:4]) for a in notes)):
        return 'ALTERED_AFTER_JUDGMENT', jd
    return 'COMPATIBLE', jd


def authority(x, docs, mer):
    """Authority category, independent of extraction confidence, with the normative basis in plain words (no inflation)."""
    k, org = x['classe'], (x['orgao'] or '').upper()
    if k in ('REPETITIVO', 'IAC', 'SIRDR'):
        if mer[0] == 'PENDING':
            return 'QUALIFIED_PRECEDENT_PENDING', 'tema afetado/pendente: ainda sem tese firmada'
        return 'QUALIFIED_PRECEDENT', {'REPETITIVO': 'recurso especial repetitivo (CPC, art. 927, III)', 'IAC': 'incidente de assunção de competência (CPC, art. 927, III)',
                                       'SIRDR': 'suspensão em IRDR'}[k]
    if k == 'RG':
        return 'QUALIFIED_PRECEDENT', 'repercussão geral com mérito (CPC, art. 927, III)'
    if k in ('ADI', 'ADC', 'ADPF', 'ADO'):
        return 'CONCENTRATED_REVIEW', 'controle concentrado do STF (CPC, art. 927, I): a eficácia vinculante recai sobre o objeto da ação'
    if k == 'SUMULA':
        return 'SUMULA_STJ', 'súmula do STJ em matéria infraconstitucional (CPC, art. 927, IV); não é súmula vinculante'
    if k.split('_')[-1] in B.HOMOLOGATORY:
        return 'HOMOLOGATION_DECISION', 'homologação de decisão estrangeira (Corte Especial): juízo de delibação, não tese de direito civil'
    if 'CORTE ESPECIAL' in org:
        return 'CORTE_ESPECIAL_ACORDAO', 'acórdão da Corte Especial (orientação do órgão especial, CPC, art. 927, V); não é tese repetitiva'
    if 'SEÇÃO' in org or 'SECAO' in org:
        return 'SECAO_ACORDAO', 'acórdão de Seção (uniformização entre Turmas); relevância institucional, não é precedente obrigatório'
    if any(t in org for t in TURMAS):
        return 'TURMA_ACORDAO', 'acórdão de Turma: jurisprudência persuasiva, não vinculante; não representa orientação pacificada'
    return 'OTHER', org


# ------------------------------------------------------------------ global audit (every one of the 932)
PROCESSOS = HERE / 'stj/STJ_PRECEDENTES_PROCESSOS_INDEX.json'


def build_processos_index(csv_path, out=PROCESSOS):
    '''Compact index of the official 'processos.csv' (precedentes qualificados dataset, CKAN): process -> themes it was judged under.'''
    import csv
    raw = Path(csv_path).read_bytes()
    idx = collections.defaultdict(list)
    for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))):
        if r['tipoPrecedente'].strip() not in ('Tema', 'IAC'):
            continue
        m = re.match(r'\s*([A-Za-z]+)\s+(\d+)', r['Processo'] or '')
        if m:
            idx[f"{m.group(1).upper()}:{m.group(2)}"].append(dict(kind='REPETITIVO' if r['tipoPrecedente'].strip() == 'Tema' else 'IAC',
                                                                    numero=r['numeroPrecedente'].strip(), leading=r['leadingCase'].strip() == 'S'))
    doc = dict(schema_version=1, source=dict(dataset='precedentes-qualificados (STJ, dados abertos, CC-BY)', file='processos.csv',
                                             sha256=sha(raw), rows=raw.count(b'\n')), processes=dict(sorted(idx.items())))
    out.write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return doc


def official(url):
    return bool(url) and any(h in url for h in OFFICIAL_HOSTS)


def audit_all():
    q = jl(D / 'CC_MASS_DISCOVERY_QUALIFIED.jsonl')
    raw = {r['raw_id']: r for r in jl(D / B.LOCAL_RAW)} if (D / B.LOCAL_RAW).is_file() else {r['raw_id']: r for r in jl(D / 'CC_MASS_DISCOVERY_RAW.jsonl')}
    inv, esp, stf, prec, sums = sources()
    index = {t['target_id'] for t in B.load(B.CC_INDEX)['targets']}
    amend = B.load(B.PLANALTO)['amendments']
    _, _, rows = E.physical_layer(B.PHYSICAL_SD)
    phys = {(r['target_id'], r['precedent_id']) for r in rows}
    pairs = collections.Counter((x['target_id'], x['precedent_id']) for x in q)
    arts = article_texts()
    procs = B.load(PROCESSOS)['processes'] if PROCESSOS.is_file() else {}
    theme_pairs = {(x['target_id'], x['precedent_id']) for x in q if x['classe'] in ('REPETITIVO', 'IAC')} | \
        {(r['target_id'], r['precedent_id']) for r in rows}
    out = []
    for x in q:
        docs = docs_of(x, raw, esp, stf, prec, sums)
        ev = evidence(x, docs)
        mer = merits(x, docs)
        tmp, jd = temporal(x, docs, amend, ev, arts)
        auth, basis = authority(x, docs, mer)
        lead = next((d for d in docs if d['kind'] == 'ESPELHO'), None)
        ident = dict(tribunal=x['tribunal'], orgao=x['orgao'], classe=x['classe'], numero=x['precedent_number'], data=jd,
                     publicacao=x['publication_date'], registro=lead['registro'] if lead else None, espelho=lead['espelho'] if lead else None,
                     relator=lead['relator'] if lead else None, url=sorted({d['url'] for d in docs if d.get('url')}),
                     source_hashes=x['source_hashes'])
        checks = dict(
            IDENTITY='OK' if x['tribunal'] in ('STJ', 'STF') and x['orgao'] and x['precedent_number'] and jd and all(official(u) for u in ident['url'])
            else 'INCOMPLETE',
            TARGET='OK' if x['target_id'] in index else 'INVALID', NAMESPACE='OK' if x['target_id'].startswith('CC2002:') else 'WRONG',
            TEMPORAL=tmp, MERITS=mer[0], PERTINENCE=ev['level'], DUPLICATE='OK' if pairs[(x['target_id'], x['precedent_id'])] == 1 and
            (x['target_id'], x['precedent_id']) not in phys else 'DUPLICATE',
            TURMA_LABEL_OK=(auth == 'TURMA_ACORDAO') == (x['sources'] == [TURMA]) if x['sources'] == [TURMA] or auth == 'TURMA_ACORDAO' else True,
            NOT_REPETITIVE_BY_MISTAKE=not (auth == 'TURMA_ACORDAO' and x['classe'] in QUALIFIED_KINDS))
        out.append(dict(id=x['id'], target=x['target_id'], precedent=x['precedent_id'], tier=x['tier'], sources=x['sources'], area=x['area'],
                        flags=x['flags'], identity=ident, authority=auth, authority_basis=basis, merits_reason=mer[1], checks=checks,
                        evidence=dict(level=ev['level'], zones=ev['zones'], field=ev['field'], quote=ev['quote'],
                                      doc=ev['doc']['doc_id'] if ev['doc'] else None, discards=ev.get('discards') or {}),
                        admissibility_bar=bool(B.ADMISSIBILITY.search(' '.join(d.get('ementa') or '' for d in docs))),
                        leading_case_of=sorted({f"{t['kind']} {t['numero']}" for t in lead_themes(x, procs)}),
                        leading_case_duplicate=any((x['target_id'], f"STJ:{t['kind']}:{t['numero']}") in theme_pairs for t in lead_themes(x, procs)),
                        subject=dict(zip(('shared', 'quote_terms'), subject_overlap(ev['quote'], x['target_id'], arts))),
                        unit_in_text=unit_in(ev['quote'], x['target_id']) if ev['quote'] else None,
                        correspondence=bool(ev['quote'] and CORRESP_Q.search(ev['quote'])),
                        official_text=next((re.sub(r'\s+', ' ', d.get('enunciado') or d.get('tese') or '')[:400] for d in docs
                                            if (d.get('enunciado') or d.get('tese'))), ''),
                        official_text_overlap=max([subject_overlap(' '.join(filter(None, [d.get('enunciado'), d.get('tese'), (d.get('ementa') or '')[:600]])),
                                                                   x['target_id'], arts)[0] for d in docs] or [0]),
                        corroborating_precedents=x.get('corroborating_precedents', []), new_target=x['new_target'],
                        human_decision='PENDING', human_approved=False))
    return q, out, raw, (inv, esp, stf, prec, sums), index, phys


def lead_themes(x, procs):
    '''Themes whose judgment this STJ acórdão is (official processos.csv), for non-qualified acórdão relations.'''
    if x['tribunal'] != 'STJ' or x['classe'] in QUALIFIED_KINDS | {'SUMULA'}:
        return []
    k = x['classe'].split('_')[-1]
    return procs.get(f"{k}:{x['precedent_number']}", [])


def crosstabs(q, rows):
    r = {x['id']: x for x in rows}
    ct = lambda f: dict(sorted(collections.Counter(f(x) for x in q).items()))  # noqa: E731
    per_prec = collections.Counter(x['precedent_id'] for x in q)
    per_target = collections.Counter(x['target_id'] for x in q)
    return dict(TOTAL_UNIQUE_RELATIONS=len({x['id'] for x in q}), TOTAL_UNIQUE_PAIRS=len({(x['target_id'], x['precedent_id']) for x in q}),
                SOURCE_X_TIER=ct(lambda x: f"{'+'.join(x['sources'])} | {x['tier']}"),
                ORGAO_X_TIER=ct(lambda x: f"{x['orgao']} | {x['tier']}"),
                CLASS_X_AUTHORITY=ct(lambda x: f"{x['classe']} | {r[x['id']]['authority']}"),
                ORIGIN=dict(NON_TURMA=sum(1 for x in q if x['sources'] != [TURMA]), STJ_3RD_4TH_TURMA=sum(1 for x in q if x['sources'] == [TURMA])),
                TIER_A_ALL_NON_TURMA=all(x['sources'] != [TURMA] for x in q if x['tier'] == 'A'),
                PRECEDENT_X_TARGETS=dict(sorted(collections.Counter(per_prec.values()).items())),
                PRECEDENTS_WITH_MOST_TARGETS=per_prec.most_common(10),
                TARGET_X_DECISIONS=dict(sorted(collections.Counter(per_target.values()).items())),
                TARGETS_WITH_MOST_DECISIONS=per_target.most_common(10))


# ------------------------------------------------------------------ subject check (does the passage talk about what the CC/2002 article says?)
CC_TEXT = ROOT / 'DEVICE_INTEGRATION/backups/sd_20260929T163407Z/data/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'


def article_texts():
    """Article -> its text (caput + parágrafos + incisos), cut from the official corpus the CC index was built on (hash-pinned in the index)."""
    idx = B.load(B.CC_INDEX)
    assert CC_TEXT.is_file() and B.sha_file(CC_TEXT) == idx['source']['sha256'], 'corpus do CC ausente ou alterado'
    lines = CC_TEXT.read_text(encoding='utf-8').splitlines()
    starts = sorted((int(t['line_start']), t['target_id']) for t in idx['targets'] if t['kind'] == 'ARTIGO')
    out = {}
    for i, (ln, tid) in enumerate(starts):
        nxt = starts[i + 1][0] if i + 1 < len(starts) else len(lines) + 1
        out[tid] = ' '.join(lines[ln - 1:nxt - 1])
    return out


ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50}
CORRESP_Q = re.compile(r'correspond|reproduzid|atual\s+art|atualmente\s+(?:regid|previst|disciplinad)|equivalente\s+ao|mesma\s+reda|agora\s+disp|'
                       r'CC\s*/\s*16\s*[-–]\s*art', re.I)


def unit_in(quote, target):
    '''Does the passage name the target paragraph / inciso / alínea (or is the target the article itself)?'''
    p = E.T.parse_target_id(target)
    q = re.sub(r'\s+', ' ', quote or '')
    ok = True
    if p['paragraph']:
        par = p['paragraph']
        ok &= bool(re.search(r'par[áa]grafo\s+[úu]nico|p(?:ar)?\.\s*[úu]n|§\s*[úu]nico', q, re.I)) if par == 'UNICO' else \
            bool(re.search(r'§{1,2}\s*(?:\d+[º°]?\s*(?:,|e)\s*)*' + par + r'\s*[º°o]?(?!\d)|' + par + r'[º°]\s*,?\s*§|par[áa]grafo\s+' + par + r'(?!\d)', q, re.I))
    if p['inciso']:
        r = p['inciso']
        ok &= bool(re.search(r'(?<![A-Za-z])' + r + r'(?![A-Za-z])', q)) or bool(re.search(r'inciso\s+' + r + r'\b', q, re.I))
    if p['alinea']:
        ok &= bool(re.search(r'al[íi]nea\s+["“]?' + p['alinea'] + r'\b|,\s*' + p['alinea'] + r'\s*[,)]', q, re.I))
    return ok


def stems(s):
    return {w[:6] for w in tokens(s) if len(w) >= 5}


def subject_overlap(quote, target, arts):
    art = E.T.format_target_id(B.NORM, E.T.parse_target_id(target)['article'])
    a, b = stems(arts.get(art, '')), stems(re.sub(r'\d', ' ', quote))
    return len(a & b), len(b)


# ------------------------------------------------------------------ Turma: corroboration, divergence, higher authority, best representative
PERT_RANK = {'DIRECT_THESIS': 5, 'DIRECT_HOLDING': 4, 'HEADER': 3, 'QUESTION_ONLY': 2, 'LIST_ONLY': 1, 'CLAIM_ONLY': 0, 'STRUCTURED_ONLY': 0, 'NOT_FOUND': 0}


def judge(x, raw, srcs, amend, arts):
    """The audit view of one candidate (any relation-shaped record): evidence, merits, temporality and READY eligibility of the evidence."""
    docs = docs_of(x, raw, *srcs)
    ev = evidence(x, docs)
    mer = merits(x, docs)
    tmp, jd = temporal(x, docs, amend, ev, arts)
    ok = mer[0] == 'MERITS' and PERT_RANK[ev['level']] >= 3 and tmp in ('COMPATIBLE', 'CC1916_CORRESPONDENCE')
    return dict(id=x['id'], precedent=x['precedent_id'], date=jd, evidence=ev, merits=mer, temporal=tmp, eligible=ok,
                polarity='NEGATIVE' if ev['quote'] and NEG.search(ev['quote']) else 'POSITIVE', toks=tokens(ev['quote']))


def sentence_window_for_neg(q):
    return q


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def turma_study(q, rows, raw, srcs, amend, arts):
    """Per Turma relation: the representative vs every corroborating acórdão the discovery set aside for the same target."""
    rej = jl(D / B.LOCAL_REJ)
    by_rep = collections.defaultdict(list)
    for c in rej:
        if c.get('representative'):
            by_rep[c['representative']].append(c)
    allraw = jl(D / B.LOCAL_RAW)
    higher = collections.defaultdict(set)              # article -> qualified precedents of any tier (not old code / invalid) naming it
    for r in allraw:
        if r['classe'] in QUALIFIED_KINDS | {'SUMULA'} and r['source'] != TURMA:
            art = E.T.format_target_id(B.NORM, E.T.parse_target_id(r['candidate_target'])['article'])
            higher[art].add(r['precedent_id'])
    excluded_old = {x['precedent_id'] for x in rej if x['tier_code'] == 'NAMESPACE_CC1916_BY_DATE'}
    higher_text = collections.defaultdict(list)        # article -> (precedent, tese/enunciado sentence) of qualified precedents
    for r in allraw:
        if r['classe'] in QUALIFIED_KINDS | {'SUMULA'} and r['source'] != TURMA and r['evidence_field'] in ('tese', 'enunciado') and                 r['discovery_method'].replace('LEADING_CASE_', '').startswith('TEXT_'):
            art = E.T.format_target_id(B.NORM, E.T.parse_target_id(r['candidate_target'])['article'])
            higher_text[art].append((r['precedent_id'], r['citation_context']))
    _, _, prow = E.physical_layer(B.PHYSICAL_SD)
    for r in prow:
        art = E.T.format_target_id(B.NORM, E.T.parse_target_id(r['target_id'])['article']) if r['target_id'].startswith('CC2002:') else None
        if art:
            higher[art].add(r['precedent_id'] + ' (no cartão)')
    rowmap = {x['id']: x for x in rows}
    out = {}
    for x in q:
        if x['sources'] != [TURMA]:
            continue
        rep = judge(x, raw, srcs, amend, arts)
        cands = [judge(c, raw, srcs, amend, arts) for c in by_rep.get(x['id'], [])]
        merits_c = [c for c in cands if c['merits'][0] == 'MERITS' and PERT_RANK[c['evidence']['level']] >= 3]
        support = [c for c in merits_c if c['polarity'] == rep['polarity'] and jaccard(c['toks'], rep['toks']) >= 0.12]
        conflict = [c for c in merits_c if c['polarity'] != rep['polarity'] and jaccard(c['toks'], rep['toks']) >= 0.12]
        art = E.T.format_target_id(B.NORM, E.T.parse_target_id(x['target_id'])['article'])
        sup = sorted(p for p in higher.get(art, set()) - excluded_old if p != x['precedent_id'])
        hconf = sorted({p for p, t in higher_text.get(art, []) if p not in excluded_old and jaccard(tokens(t), rep['toks']) >= 0.12 and
                        ('NEGATIVE' if NEG.search(t) else 'POSITIVE') != rep['polarity']})
        okc = [c for c in cands if c['eligible'] and PERT_RANK[c['evidence']['level']] >= 4 and unit_in(c['evidence']['quote'], x['target_id'])
               and subject_overlap(c['evidence']['quote'], x['target_id'], arts)[0] >= 1 and not re.search(r'S[úu]mula\s*(?:n[º°.]*\s*)?83', c['evidence']['quote'])]
        best = max(okc, key=lambda c: (PERT_RANK[c['evidence']['level']], ':RESP:' in c['precedent'], c['date'] or '', c['id'])) if okc else rep
        rep_good = rep['eligible'] and PERT_RANK[rep['evidence']['level']] >= 4 and unit_in(rep['evidence']['quote'], x['target_id'])
        subst = best is not rep and not rep_good
        if not rep['eligible'] and not subst:
            status = 'INSUFFICIENT_EVIDENCE'
        elif hconf:
            status = 'SUPERIOR_AUTHORITY_CONFLICT'
        elif conflict:
            status = 'POTENTIAL_DIVERGENCE'
        elif support:
            status = 'CORROBORATED_TURMA_CASELAW'
        else:
            status = 'ISOLATED_MERITS_DECISION'
        out[x['id']] = dict(target=x['target_id'], representative=x['precedent_id'], representative_eligible=rep['eligible'],
                            CANDIDATES_COMPARED=len(cands) + 1, MERITS_EVIDENCE=rep['merits'][0], TEMPORAL_STATUS=rep['temporal'],
                            CO_CITING_MERITS_DECISIONS=len(merits_c), SUPPORTING_DECISIONS_COUNT=len(support),
                            POTENTIALLY_CONFLICTING_DECISIONS_COUNT=len(conflict),
                            supporting=[c['precedent'] for c in support][:8], conflicting=[c['precedent'] for c in conflict][:8],
                            HIGHER_AUTHORITY_SAME_ARTICLE=sup[:8], HIGHER_AUTHORITY_CONFLICT=bool(hconf), higher_conflicting=hconf[:5],
                            classification=status,
                            substitution=dict(proposed=best['precedent'], proposed_relation=best['id'], ready=True,
                                              proposed_orgao=(best['evidence']['doc'] or {}).get('orgao'),
                                              proposed_espelho=(best['evidence']['doc'] or {}).get('espelho'),
                                              proposed_registro=(best['evidence']['doc'] or {}).get('registro'),
                                              proposed_temporal=best['temporal'], proposed_merits=best['merits'][0], reason=f"evidência {best['evidence']['level']} "
                                              f"({'apta' if best['eligible'] else 'não apta'}) contra {rep['evidence']['level']} do representante atual",
                                              proposed_quote=best['evidence']['quote'][:300], proposed_date=best['date']) if subst else None,
                            method='suporte e divergência por proxy textual: mesma conclusão (polaridade) e vocabulário comum (Jaccard ≥ 0,12) no '
                                   'trecho que nomeia o artigo; não equivale a jurisprudência consolidada')
    return out


# ------------------------------------------------------------------ editorial states (never a human decision)
STATES = ('READY_FOR_BLOCK_DECISION', 'READY_WITH_QUALIFICATION', 'INDIVIDUAL_REVIEW_REQUIRED', 'NEEDS_MORE_EVIDENCE', 'REJECT_RECOMMENDED',
          'BLOCKED_BY_SYSTEMIC_AUDIT')
NOTE = dict(
    TURMA='Acórdão de Turma do STJ: jurisprudência persuasiva, não vinculante; não representa tese repetitiva nem orientação pacificada.',
    TURMA_ISOLATED='Decisão localizada isoladamente nas fontes oficiais consultadas.',
    TURMA_CORROBORATED='Outros acórdãos de Turma nas fontes oficiais aplicam o dispositivo no mesmo sentido (indício textual, não consolidação).',
    SECAO='Acórdão de Seção do STJ (uniformização entre Turmas): relevância institucional, não é tese repetitiva.',
    CORTE='Acórdão da Corte Especial do STJ (orientação do órgão especial): não é tese repetitiva.',
    LEADING='O artigo aparece na fundamentação do acórdão paradigma do tema, não no texto da tese.',
    HISTORICA='Decisão proferida sob o Código Civil de 1916; o artigo do CC/2002 é citado como correspondente da regra aplicada.',
    SUBST='Representante substituído por acórdão com fundamentação mais direta sobre o artigo (substituição proposta pela auditoria).',
    OFFICIAL_REF='Vínculo indicado pela referência legislativa oficial do próprio tribunal; o texto da súmula/tese trata do mesmo objeto do artigo.',
    CORRESP='A decisão aplica norma anterior (CC/1916 ou Código Comercial) e cita o artigo do CC/2002 como seu correspondente.',
    NEGATIVE='A decisão delimita o alcance do artigo: afasta sua aplicação à hipótese julgada.',
    LEADING_OF='Acórdão paradigma de tema repetitivo do STJ ({}); a tese do tema prevalece sobre a fundamentação do acórdão.')


def editorial(x, row, ts, deep):
    """(state, reason, notes) for one relation; deep-audit verdicts override the rules for the sampled ids (auditor finding, not ratification)."""
    c, ev, auth = row['checks'], row['evidence'], row['authority']
    notes = []
    d = deep.get(x['id'])
    if d and d['verdict'] in STATES:
        if d.get('reader_note'):
            notes.append(d['reader_note'])
        return d['verdict'], 'auditoria aprofundada: ' + d['note'], notes
    if c['TARGET'] != 'OK' or c['DUPLICATE'] != 'OK' or c['NAMESPACE'] != 'OK':
        return 'REJECT_RECOMMENDED', 'target inválido ou relação duplicada', notes
    if row.get('leading_case_duplicate'):
        return 'REJECT_RECOMMENDED', 'acórdão paradigma de tema repetitivo já vinculado ao mesmo artigo (duplicaria o tema)', notes
    if c['MERITS'] == 'PENDING':
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'tema afetado ainda sem tese firmada', notes
    sub0 = ts.get(x['id'], {}).get('substitution') if auth == 'TURMA_ACORDAO' else None
    if sub0 and sub0.get('ready'):
        notes += [NOTE['SUBST'], NOTE['TURMA'], NOTE['TURMA_ISOLATED'] if ts[x['id']]['SUPPORTING_DECISIONS_COUNT'] == 0 else NOTE['TURMA_CORROBORATED']]
        if ts[x['id']]['classification'] in ('POTENTIAL_DIVERGENCE', 'SUPERIOR_AUTHORITY_CONFLICT'):
            return 'INDIVIDUAL_REVIEW_REQUIRED', 'possível divergência sobre o artigo (substituto proposto)', notes
        return 'READY_WITH_QUALIFICATION', 'representante substituído por acórdão de Turma com fundamento direto, mérito e regime conferidos', notes
    if ev['level'] == 'NOT_FOUND':
        dis = {k: v for k, v in (ev.get('discards') or {}).items() if k not in ('UNATTRIBUTED', 'ADMISSIBILITY_IN_SENTENCE')}
        if dis:
            return 'REJECT_RECOMMENDED', 'o número citado pertence a outra norma (' + ', '.join(sorted(dis)) + '), não ao CC/2002', notes
        return 'NEEDS_MORE_EVIDENCE', 'artigo não localizado no texto oficial capturado', notes
    if c['MERITS'] == 'NO_MERIT':
        if row['admissibility_bar'] or 'cancelada' in row['merits_reason'] or 'prejudicada' in row['merits_reason']:
            return 'REJECT_RECOMMENDED', 'sem julgamento de mérito sobre o dispositivo', notes
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'recurso não conhecido após exame da questão (prática antiga): verificar se houve pronunciamento de mérito', notes
    if ev['level'] == 'CLAIM_ONLY':
        return 'REJECT_RECOMMENDED', 'dispositivo citado só na alegação, na questão ou no óbice de admissibilidade', notes
    if c['TEMPORAL'] == 'AMBIGUOUS_CODE_NAMESPACE':
        return 'NEEDS_MORE_EVIDENCE', 'julgado de 2003-2010 que cita "Código Civil" sem indicar 2002 e trata de matéria alheia ao artigo do CC/2002', notes
    if c['TEMPORAL'] in ('PRE_CC2002', 'POSSIBLE_CC1916'):
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'regime temporal incerto (CC/1916 x CC/2002)', notes
    sub = ts.get(x['id'], {}).get('substitution') if auth == 'TURMA_ACORDAO' else None
    if sub and sub.get('ready'):
        notes += [NOTE['SUBST'], NOTE['TURMA'], NOTE['TURMA_ISOLATED'] if ts[x['id']]['SUPPORTING_DECISIONS_COUNT'] == 0 else NOTE['TURMA_CORROBORATED']]
        if ts[x['id']]['classification'] in ('POTENTIAL_DIVERGENCE', 'SUPERIOR_AUTHORITY_CONFLICT'):
            return 'INDIVIDUAL_REVIEW_REQUIRED', 'possível divergência sobre o artigo (substituto proposto)', notes
        return 'READY_WITH_QUALIFICATION', 'representante substituído por acórdão de Turma com fundamento direto, mérito e regime conferidos', notes
    if row['subject']['shared'] == 0 and row['subject']['quote_terms'] >= 8 and not EXPLICIT_2002.search(ev['quote'] or '') and \
            auth not in ('QUALIFIED_PRECEDENT', 'SUMULA_STJ'):
        return 'NEEDS_MORE_EVIDENCE', 'o trecho trata de matéria alheia ao texto do artigo do CC/2002 (possível numeração do CC/1916 ou erro de citação)', notes
    if row['unit_in_text'] is False and ev['level'] not in ('STRUCTURED_ONLY', 'NOT_FOUND'):
        return 'NEEDS_MORE_EVIDENCE', 'o trecho cita o artigo, mas não o parágrafo/inciso do target', notes
    if c['MERITS'] == 'PENDING':
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'tema afetado ainda sem tese firmada', notes
    if c['MERITS'] != 'MERITS':
        return 'NEEDS_MORE_EVIDENCE', row['merits_reason'], notes
    if auth in ('QUALIFIED_PRECEDENT', 'SUMULA_STJ') and ev['level'] in ('STRUCTURED_ONLY', 'HEADER') and row.get('official_text_overlap', 0) >= 2:
        notes.append(NOTE['OFFICIAL_REF'] if ev['level'] == 'STRUCTURED_ONLY' else NOTE['LEADING'])
        return 'READY_WITH_QUALIFICATION', 'precedente qualificado ligado ao artigo pela referência oficial/verbetação, com o mesmo objeto do artigo', notes
    if ev['level'] in ('STRUCTURED_ONLY', 'LIST_ONLY', 'QUESTION_ONLY'):
        return 'NEEDS_MORE_EVIDENCE', {'STRUCTURED_ONLY': 'só referência legislativa indexada, sem o artigo no texto',
                                       'LIST_ONLY': 'só na lista de dispositivos citados',
                                       'QUESTION_ONLY': 'só na questão submetida ou na narrativa da decisão recorrida'}[ev['level']], notes
    if 'USO_CONTEXTUAL_POSSIVEL' in x['flags'] and not (d and d['verdict'] in ('READY_FOR_BLOCK_DECISION', 'READY_WITH_QUALIFICATION')):
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'uso possivelmente contextual do CC em julgado do STF', notes
    if auth == 'HOMOLOGATION_DECISION':
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'homologação de decisão estrangeira: juízo de delibação', notes
    if c['TEMPORAL'] == 'ALTERED_AFTER_JUDGMENT':
        return 'INDIVIDUAL_REVIEW_REQUIRED', 'redação do dispositivo alterada depois do julgamento', notes
    if row.get('leading_case_of'):
        notes.append(NOTE['LEADING_OF'].format(', '.join(row['leading_case_of'])))
    if ev['quote'] and NEG.search(sentence_window_for_neg(ev['quote'])):
        notes.append(NOTE['NEGATIVE'])
    if c['TEMPORAL'] == 'CC1916_CORRESPONDENCE':
        notes.append(NOTE['HISTORICA'])
    elif row['correspondence']:
        notes.append(NOTE['CORRESP'])
    if auth == 'TURMA_ACORDAO':
        t = ts[x['id']]
        if t['classification'] in ('POTENTIAL_DIVERGENCE', 'SUPERIOR_AUTHORITY_CONFLICT'):
            return 'INDIVIDUAL_REVIEW_REQUIRED', {'POTENTIAL_DIVERGENCE': 'possível divergência entre acórdãos de Turma sobre o artigo',
                                                  'SUPERIOR_AUTHORITY_CONFLICT': 'possível conflito com precedente de maior autoridade'}[t['classification']], notes
        if t['substitution']:
            notes.append(NOTE['SUBST'])
        elif not t['representative_eligible'] or ev['level'] == 'HEADER':
            return 'NEEDS_MORE_EVIDENCE', 'fundamento só na verbetação ou insuficiente; nenhum acórdão alternativo melhor', notes
        notes += [NOTE['TURMA'], NOTE['TURMA_CORROBORATED'] if t['classification'] == 'CORROBORATED_TURMA_CASELAW' else NOTE['TURMA_ISOLATED']]
        return 'READY_WITH_QUALIFICATION', 'acórdão de Turma de mérito, fundamento verificável, dispositivo e regime conferidos', notes
    if ev['level'] == 'HEADER':
        return 'NEEDS_MORE_EVIDENCE', 'artigo só na verbetação da ementa', notes
    if auth in ('SECAO_ACORDAO', 'CORTE_ESPECIAL_ACORDAO'):
        notes.append(NOTE['SECAO'] if auth == 'SECAO_ACORDAO' else NOTE['CORTE'])
        return 'READY_WITH_QUALIFICATION', 'acórdão colegiado de uniformização, fundamento verificável', notes
    if auth in ('QUALIFIED_PRECEDENT', 'SUMULA_STJ', 'CONCENTRATED_REVIEW'):
        if ev['field'] == 'ementa' and auth == 'QUALIFIED_PRECEDENT' and x['tribunal'] == 'STJ':
            notes.append(NOTE['LEADING'])
        if notes:
            return 'READY_WITH_QUALIFICATION', 'precedente qualificado com nota obrigatória', notes
        return 'READY_FOR_BLOCK_DECISION', 'precedente qualificado/súmula com o artigo no texto da tese/enunciado, mérito e regime conferidos', notes
    return 'INDIVIDUAL_REVIEW_REQUIRED', f'categoria de autoridade {auth}', notes


# ------------------------------------------------------------------ deep-audit sample (deterministic, stratified, >= 200)
def deep_sample(q, rows):
    """Deterministic, stratified, >= 200, drawn only from attributes the audit rules cannot change (so a rule fix never reshuffles it):
    every TIER A; every STF relation; non-Turma up to 80 in round-robin over authority categories; 120 Turma: 15 judged before 2011,
    20 the discovery found corroborated, every flagged one, then round-robin over the CC books. Order inside a stratum: sha256 of the id."""
    R = {r['id']: r for r in rows}
    order = sorted(q, key=lambda x: sha(('deep|' + x['id']).encode()))
    pick, seen = [], set()
    n_non = lambda: sum(1 for x in pick if x['sources'] != [TURMA])  # noqa: E731
    n_tur = lambda: sum(1 for x in pick if x['sources'] == [TURMA])  # noqa: E731

    def take(cands, n):
        k = 0
        for x in cands:
            if k >= n:
                break
            if x['id'] not in seen:
                seen.add(x['id'])
                pick.append(x)
                k += 1
        return k
    take([x for x in order if x['tier'] == 'A'], 10 ** 6)
    non = [x for x in order if x['sources'] != [TURMA]]
    take([x for x in non if x['tribunal'] == 'STF'], 10 ** 6)
    cats = sorted({R[x['id']]['authority'] for x in non})
    while n_non() < 80:
        got = 0
        for c in cats:
            if n_non() < 80:
                got += take([x for x in non if R[x['id']]['authority'] == c], 1)
        if not got:
            break
    tur = [x for x in order if x['sources'] == [TURMA]]
    take([x for x in tur if (B.iso_date(x['judgment_date']) or '9') < '2011'], 15)
    take([x for x in tur if x.get('corroborating_precedents')], 20)
    take([x for x in tur if x['flags']], 10)
    books = sorted({x['area'] for x in tur})
    while n_tur() < 120:
        got = 0
        for bk in books:
            if n_tur() < 120:
                got += take([x for x in tur if x['area'] == bk], 1)
        if not got:
            break
    return sorted(pick, key=lambda x: x['id'])


# ------------------------------------------------------------------ projections, device capacity
READY = ('READY_FOR_BLOCK_DECISION', 'READY_WITH_QUALIFICATION')
DEVICE_TIPO = {'SUMULA': 'sumula', 'REPETITIVO': 'repetitivo_stj', 'IAC': 'iac', 'RG': 'repercussao_geral', 'ADI': 'adi', 'ADC': 'adc', 'ADPF': 'adpf'}
LOOKUP_STRUCT_BYTES = 68        # LookupJurisCFCache with norma[16] (multinorm.patch): 16+12+12+16+4 chars, uint32 at 60, uint8, padded to 4
FW = dict(MAX_JUR_LOOKUPS_SEGURANCA=4096, MAX_RECORDS_BYTES=16 * 1024 * 1024, MAX_RELACOES_ARTIGO=32,
          source='firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE + JURISPRUDENCE_ENGINE/firmware_multinorm/multinorm.patch (aparelho: app 38c4d71f…)')


def effective(x, st, ts):
    """(target, precedent) the relation would publish: the proposed substitute when the audit replaced a Turma representative."""
    sub = ts.get(x['id'], {}).get('substitution')
    if sub and st[x['id']][0] in READY and 'substituído' in st[x['id']][1]:
        return x['target_id'], sub['proposed']
    return x['target_id'], x['precedent_id']


def projections(q, st, ts, phys):
    base = {(t, p_) for t, p_ in phys if t.startswith('CC2002:')}
    out = {}
    for name, states in (('READY_ONLY', ('READY_FOR_BLOCK_DECISION',)), ('READY_WITH_QUALIFICATIONS', READY),
                         ('CEILING_ALL_NOT_REJECTED', READY + ('INDIVIDUAL_REVIEW_REQUIRED', 'NEEDS_MORE_EVIDENCE', 'BLOCKED_BY_SYSTEMIC_AUDIT'))):
        pairs = base | {effective(x, st, ts) for x in q if st[x['id']][0] in states}
        out[name] = dict(relations=len(pairs), targets=len({t for t, _ in pairs}), added_relations=len(pairs - base),
                         new_targets=len({t for t, _ in pairs} - {t for t, _ in base}))
    out['BASELINE'] = dict(relations=len(base), targets=len({t for t, _ in base}))
    return out


def capacity(q, st, ts):
    """SIMULATION_ONLY: the largest technically qualified set (every relation not rejected) packaged by generic_packager over the physical
    layer. Measures what the firmware limits care about; no physical timing is invented."""
    card = {k.split('/')[-1] for k in B.load(HERE / 'CC_J2_PHYSICAL_DEPLOY/sd_manifest_post_full.json')['entries'] if k.startswith(E.P.CONTENT + '/')}
    recs, fichas, rels = {}, {}, []
    for x in q:
        if st[x['id']][0] == 'REJECT_RECOMMENDED':
            continue
        t, pid = effective(x, st, ts)
        trib, klass, num = pid.split(':')[:3]
        tipo = DEVICE_TIPO.get(klass, 'acordao')
        n = num.replace('-', '/')
        lab = E.JT.label(tipo, trib, n)
        recs.setdefault(pid, dict(tipo=tipo, tribunal=trib, numero=n, status='simulacao', titulo=lab, fonte=''))
        fichas.setdefault(E.JT.ficha(pid), f'{lab} ({trib})\nSIMULAÇÃO — NÃO PUBLICADO\n')
        rels.append(dict(norm=B.NORM, target_id=t, precedent_id=pid, origin='CC_MASS_AUDIT (SIMULATION_ONLY)'))
    rels = list({(r['target_id'], r['precedent_id']): r for r in rels}.values())
    files, rep = E.simulate(B.PHYSICAL_SD, card, rels, recs, fichas, E.P.provisional_ids(), E.P.known_targets(), B.PROBE, B.NORM)
    look = files[E.P.LAYER + '/JUR_LOOKUP.IDX'].decode('utf-8').splitlines()
    look_n = sum(1 for l in look if l.strip() and not l.startswith('#'))
    rec_b = len(files[E.P.LAYER + '/JURISPRUDENCIA.IDX'])
    look0, recs0, _ = E.physical_layer(B.PHYSICAL_SD)
    base_look_n = sum(1 for l in look0.decode('utf-8').splitlines() if l.strip() and not l.startswith('#'))
    per_key = collections.Counter(E.P.query_key(r['target_id']) for r in rels)
    new_fichas = [k for k in files if k.startswith(E.P.CONTENT)]
    cf_reg = rep['OTHER_NORM_KEYS_CHANGED'] + sum(v for k, v in rep['lost_by_namespace'].items() if k != B.NORM)
    cc_reg = rep['lost_by_namespace'].get(B.NORM, 0) + rep['BASELINE_RECORD_LINES_MISSING']
    return dict(status='SIMULATION_ONLY', deployable=False, simulated_relations=len(rels), simulated_precedents=len(recs),
                LOOKUP_ENTRIES=look_n, LOOKUP_ENTRIES_BASELINE=base_look_n, LOOKUP_LIMIT=FW['MAX_JUR_LOOKUPS_SEGURANCA'],
                LOOKUP_PSRAM_BYTES=look_n * LOOKUP_STRUCT_BYTES, LOOKUP_PSRAM_BYTES_BASELINE=base_look_n * LOOKUP_STRUCT_BYTES,
                RECORDS_IDX_BYTES=rec_b, RECORDS_IDX_BYTES_BASELINE=len(recs0), RECORDS_LIMIT_BYTES=FW['MAX_RECORDS_BYTES'],
                PSRAM_TOTAL_BYTES=look_n * LOOKUP_STRUCT_BYTES + rec_b + 1, NEW_FICHAS=len(new_fichas),
                NEW_FICHAS_BYTES=sum(len(files[k]) for k in new_fichas), MAX_RELATIONS_PER_KEY=max(per_key.values()) if per_key else 0,
                MAX_RELACOES_ARTIGO=FW['MAX_RELACOES_ARTIGO'], DUPLICATE_QUERY_KEYS=rep['DUPLICATE_QUERY_KEYS'], CF_REGRESSION=cf_reg,
                CC_J1_J2_REGRESSION=cc_reg, VISIBLE=rep['NEW_VISIBLE'], FICHA_OPEN=rep['NEW_FICHA_OPEN'], BACK=rep['NEW_BACK'],
                labels=rep['labels'], OUTRO_LABELS=rep['OUTRO_LABELS'],
                LOOKUP_COMPARISONS_PER_QUERY=dict(baseline=base_look_n, simulated=look_n, ratio=round(look_n / base_look_n, 2) if base_look_n else None,
                                                  note='busca linear sobre o cache (for i < totalJurLookupCFCache): custo proporcional ao número de '
                                                       'entradas; razão em relação ao baseline físico, sem medição de tempo'),
                TYPE_COMPATIBILITY=dict(acordao='rótulo "ACORDAO n" existe no firmware, sem validação física; não distingue REsp/AREsp nem Turma',
                                        others='SÚMULA, REPETITIVO STJ e IAC validados fisicamente; RG/ADI/ADC/ADPF com rótulos legados'),
                firmware=FW)


# ------------------------------------------------------------------ packets
RISK = {'READY_FOR_BLOCK_DECISION': 'BAIXO', 'QUALIFIED': 'MODERADO (nota obrigatória)', 'SECAO': 'MODERADO (acórdão colegiado, nota)',
        'TURMA': 'MODERADO (acórdão persuasivo de Turma, nota)'}
TYPE_PT = {'QUALIFIED_PRECEDENT': 'Precedente qualificado', 'SUMULA_STJ': 'Súmula do STJ', 'CONCENTRATED_REVIEW': 'Controle concentrado (STF)',
           'SECAO_ACORDAO': 'Acórdão de Seção (STJ)', 'CORTE_ESPECIAL_ACORDAO': 'Acórdão da Corte Especial (STJ)', 'TURMA_ACORDAO': 'Acórdão de Turma (STJ)',
           'HOMOLOGATION_DECISION': 'Homologação (Corte Especial)', 'QUALIFIED_PRECEDENT_PENDING': 'Tema pendente'}


def source_pt(row):
    i = row['identity']
    if i.get('espelho'):
        return f"STJ, dados abertos — espelho {i['espelho']} (registro {i['registro']})"
    return (i['url'] or ['—'])[0]


def item_of(x, row, st, ts):
    state, reason, notes = st[x['id']]
    t, pid = effective(x, st, ts)
    sub = ts.get(x['id'], {}).get('substitution') if pid != x['precedent_id'] else None
    quote = (sub['proposed_quote'] if sub else row['evidence']['quote']) or row.get('official_text') or ''
    a = row['authority']
    risk = RISK['READY_FOR_BLOCK_DECISION'] if state == 'READY_FOR_BLOCK_DECISION' else RISK['TURMA'] if a == 'TURMA_ACORDAO' else \
        RISK['SECAO'] if a in ('SECAO_ACORDAO', 'CORTE_ESPECIAL_ACORDAO') else RISK['QUALIFIED']
    return dict(ID=x['id'], ARTIGO=t, PRECEDENTE=pid, ORGAO_JULGADOR=(row['identity']['orgao'] if not sub else sub.get('proposed_orgao')),
                TIPO=TYPE_PT.get(a, a), FUNDAMENTO_MATERIAL_RESUMIDO=quote[:240], FONTE_OFICIAL=source_pt(row) if not sub else
                f"STJ, dados abertos — espelho {sub.get('proposed_espelho')} (registro {sub.get('proposed_registro')})", RISCO=risk,
                RECOMENDACAO='APROVAR EM BLOCO' if state == 'READY_FOR_BLOCK_DECISION' else 'APROVAR COM A NOTA', NOTA_NECESSARIA=' '.join(dict.fromkeys(notes)),
                DECISAO_HUMANA='PENDING', substituted_from=x['precedent_id'] if sub else None, area=x['area'], authority=a, state=state)


def packets(items):
    """Packets of about 100-200 relations, never mixing persuasive Turma acórdãos with qualified precedents."""
    non = [i for i in items if i['authority'] != 'TURMA_ACORDAO']
    tur = [i for i in items if i['authority'] == 'TURMA_ACORDAO']
    out = [('PRECEDENTES QUALIFICADOS, SÚMULAS, STF E ACÓRDÃOS DE SEÇÃO/CORTE ESPECIAL', non)] if non else []
    order = [b for b, _, _ in B.AREAS]
    tur.sort(key=lambda i: (order.index(i['area']) if i['area'] in order else 99, E.T.parse_target_id(i['ARTIGO'])['article'].zfill(6), i['ID']))
    cur, label = [], []
    for b in order + [None]:
        grp = [i for i in tur if i['area'] == b] if b else []
        if cur and (b is None or len(cur) + len(grp) > 200):
            out.append(('ACÓRDÃOS DE TURMA DO STJ (PERSUASIVOS) — ' + ' + '.join(label), cur))
            cur, label = [], []
        while len(grp) > 200:
            out.append((f'ACÓRDÃOS DE TURMA DO STJ (PERSUASIVOS) — {b} (parte)', grp[:150]))
            grp = grp[150:]
        if grp:
            cur += grp
            label.append(b)
    return out


def packet_md(n, title, items, total_packets):
    L = [f'# CC MASS — pacote de ratificação {n:02d}/{total_packets:02d}: {title}', '', '```',
         f'RELAÇÕES = {len(items)} · DECISAO_HUMANA = PENDING em todas · nada aqui foi aprovado · nada será publicado sem a decisão do usuário', '```', '',
         'Cada linha é um candidato para decisão humana. O trecho é da fonte oficial (ementa/tese/enunciado); a evidência completa, o hash e a '
         'trilha de auditoria estão em `CC_MASS_AUDIT_ALL_932.jsonl` e `CC_MASS_RATIFICATION_READY.json` (pela ID).', '']
    groups = collections.OrderedDict()
    for i in items:
        groups.setdefault(i['TIPO'], []).append(i)
    for tipo, its in groups.items():
        L += [f'## {tipo} ({len(its)})', '', '| ID | ARTIGO | PRECEDENTE | ÓRGÃO | FUNDAMENTO MATERIAL (trecho oficial) | FONTE | RISCO | RECOMENDAÇÃO | NOTA NECESSÁRIA | DECISÃO |',
              '|---|---|---|---|---|---|---|---|---|---|']
        for i in its:
            cell = lambda v: str(v or '—').replace('|', '/').replace('\n', ' ')  # noqa: E731
            L.append(f"| {i['ID']} | {i['ARTIGO'].replace('CC2002:', '')} | {i['PRECEDENTE']}{' (subst.)' if i['substituted_from'] else ''} | "
                     f"{cell(i['ORGAO_JULGADOR'])} | {cell(i['FUNDAMENTO_MATERIAL_RESUMIDO'][:180])} | {cell(i['FONTE_OFICIAL'])} | {i['RISCO']} | "
                     f"{i['RECOMENDACAO']} | {cell(i['NOTA_NECESSARIA'][:220])} | PENDING |")
        L.append('')
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------ systemic-error ledger
def systemic_impact(q, rows, st, ts, deep):
    R = {r['id']: r for r in rows}
    notready = {x['id'] for x in q if st[x['id']][0] not in READY}
    imp = collections.Counter()
    for x in q:
        r, (state, reason, _) = R[x['id']], st[x['id']]
        dis = r['evidence'].get('discards') or {}
        codes = set()
        d = deep.get(x['id'])
        if dis.get('CC1916') or r['checks']['TEMPORAL'] == 'AMBIGUOUS_CODE_NAMESPACE' or 'CC/1916 ou erro' in reason or \
                (d and 'CC/1916' in d.get('temporal', '')):
            codes.add('S01_CC1916_NUMBERING')
        if r['evidence']['level'] == 'NOT_FOUND' and (dis.get('OTHER_LAW') or dis.get('FOREIGN')) or (d and 'CPC' in d.get('target', '')):
            codes.add('S02_OTHER_LAW')
        if r['evidence']['level'] == 'CLAIM_ONLY':
            codes.add('S03_ADMISSIBILITY')
        if r['evidence']['level'] == 'QUESTION_ONLY' and r['checks']['MERITS'] != 'PENDING':
            codes.add('S04_QUESTION_NARRATIVE')
        if r['evidence']['level'] == 'HEADER' and state == 'NEEDS_MORE_EVIDENCE':
            codes.add('S05_HEADING_ONLY')
        if 'parágrafo/inciso' in reason:
            codes.add('S06_UNIT_NOT_IN_TEXT')
        if x['tribunal'] == 'STF' and state == 'REJECT_RECOMMENDED':
            codes.add('S07_STF_CONTEXTUAL')
        if r.get('leading_case_duplicate') or (d and d.get('duplicate', 'OK') != 'OK'):
            codes.add('S08_DUPLICATES')
        for c in codes:
            if x['id'] in notready:
                imp[c] += 1
        if ts.get(x['id'], {}).get('substitution') and state in READY and 'substituído' in reason:
            imp['S09_REPRESENTATIVE'] += 1
    return dict(sorted(imp.items()))


def systemic_md(findings, impact, n_notready):
    L = ['# CC MASS AUDIT — erros sistemáticos (regra corrigida e grupo inteiro reprocessado)', '',
         'Cada padrão foi achado na auditoria aprofundada (amostra de 200) ou na validação independente, corrigido na regra do construtor e '
         'reaplicado às 932 relações. A coluna "relações afetadas" conta quantas das 932 deixaram o estado favorável por causa do padrão '
         '(uma relação pode cair em mais de um); para S09 conta os representantes de Turma substituídos.', '',
         f'Relações que deixaram o estado favorável (todas eram TIER A/B na descoberta): {n_notready}.', '',
         '| Código | Padrão | Exemplos | Correção | Relações afetadas |', '|---|---|---|---|---:|']
    for f in findings:
        L.append(f"| {f['code']} | {f['title']} | {'; '.join(f['examples'])} | {f['fix']} | {impact.get(f['code'], 0)} |")
    L += ['', 'Recomendação em bloco suspensa para cada grupo afetado até a correção; depois dela, nenhum grupo ficou BLOCKED_BY_SYSTEMIC_AUDIT: '
          'os casos que a regra não resolve com segurança vão para NEEDS_MORE_EVIDENCE ou INDIVIDUAL_REVIEW_REQUIRED, nunca para READY.', '',
          'Limites conhecidos (não corrigíveis por regra sem perder casos válidos): o validador de assunto produz falsos positivos (2 na amostra), '
          'só rebaixa para NEEDS_MORE_EVIDENCE; a corroboração entre acórdãos de Turma é um indício textual (polaridade + vocabulário), '
          'não prova de jurisprudência consolidada.']
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------ assembly
from cc_mass_deep_audit_review import VALIDATION_ROUNDS  # noqa: E402

STAGES = ['RECONCILE_932', 'GLOBAL_VALIDATORS', 'AUTHORITY', 'TURMA_CORROBORATION', 'DEEP_SAMPLE_200', 'VALIDATION_ROUNDS', 'EDITORIAL_STATES',
          'PACKETS', 'PROJECTIONS', 'DEVICE_CAPACITY', 'REPORTS']


def dumpb(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def jsonl(rows):
    return ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows).encode('utf-8')


def deep_metrics(sam, rule_st, st, deep):
    dims = ('identity', 'target', 'temporal', 'merits', 'pertinence', 'duplicate', 'authority')
    err = {d: sum(1 for x in sam if deep[x['id']][d] != 'OK') for d in dims}
    strata = collections.defaultdict(lambda: collections.Counter())
    for x in sam:
        k = 'TIER_A' if x['tier'] == 'A' else 'STF' if x['tribunal'] == 'STF' else 'TURMA' if x['sources'] == [TURMA] else 'OUTROS_NAO_TURMA'
        strata[k]['n'] += 1
        strata[k]['with_error'] += any(deep[x['id']][d] != 'OK' for d in dims)
    overrides = [x['id'] for x in sam if deep[x['id']]['verdict'] != 'CONFIRMA']
    agree = sum(1 for x in sam if rule_st[x['id']][0] == st[x['id']][0])
    return dict(DEEP_AUDIT_SAMPLE=len(sam), RELATIONS_WITH_ERROR=sum(1 for x in sam if any(deep[x['id']][d] != 'OK' for d in dims)),
                ERRORS_BY_DIMENSION=err, ERRORS_BY_STRATUM={k: dict(v) for k, v in sorted(strata.items())}, AUDITOR_OVERRIDES=len(overrides),
                RULE_STATE_AGREES_WITH_AUDITOR=f'{agree}/{len(sam)}',
                design='estratificada e deliberadamente enriquecida de casos de risco (todo o TIER A, todo o STF, julgados antigos, corroborados, '
                       'sinalizados); a taxa de erro da amostra NÃO é estimativa da taxa da população')


def outputs():
    q, rows, raw, srcs, index, phys = audit_all()
    assert len(q) == INPUT_COUNT and len({x['id'] for x in q}) == INPUT_COUNT, 'divergência: as 932 relações não reconciliam'
    arts = article_texts()
    amend = B.load(B.PLANALTO)['amendments']
    ts = turma_study(q, rows, raw, srcs[1:], amend, arts)
    R = {r['id']: r for r in rows}
    st = {x['id']: editorial(x, R[x['id']], ts, DEEP_REVIEW) for x in q}
    rule_st = {x['id']: editorial(x, R[x['id']], ts, {}) for x in q}
    sam = deep_sample(q, rows)
    assert {x['id'] for x in sam} == set(DEEP_REVIEW), 'amostra e revisão divergentes'
    # per-relation audit (all 932)
    all_rows = []
    for x in q:
        r = dict(R[x['id']])
        state, reason, notes = st[x['id']]
        t, pid = effective(x, st, ts)
        r.update(editorial_state=state, editorial_reason=reason, reader_notes=list(dict.fromkeys(notes)), published_pair=dict(target=t, precedent=pid),
                 turma=ts.get(x['id']), deep_audit=DEEP_REVIEW.get(x['id']), rule_state_without_deep_audit=rule_st[x['id']][0],
                 discovery=dict(tier=x['tier'], tier_reason=x['tier_reason'], evidence_strength=x['evidence_strength']))
        all_rows.append(r)
    items = [item_of(x, R[x['id']], st, ts) for x in q if st[x['id']][0] in READY]
    pk = packets(items)
    impact = systemic_impact(q, rows, st, ts, DEEP_REVIEW)
    cnt = collections.Counter(v[0] for v in st.values())
    proj = projections(q, st, ts, phys)
    cap = capacity(q, st, ts)
    dm = deep_metrics(sam, rule_st, st, DEEP_REVIEW)
    val = [dict(round=v['round'], rules_frozen=v['rules_frozen'], n=len(v['ids']), errors=len(v['errors'])) for v in VALIDATION_ROUNDS]
    tur = [x for x in q if x['sources'] == [TURMA]]
    ready_pairs = {effective(x, st, ts) for x in q if st[x['id']][0] in READY}
    phys_t = {t for t, _ in phys}
    metrics = dict(
        MASS_AUDIT_STATUS='PASS', INPUT_RELATIONS=INPUT_COUNT, RECONCILED_RELATIONS=len(all_rows),
        TIER_A_REASSESSED=sum(1 for x in q if x['tier'] == 'A'), TIER_B_REASSESSED=sum(1 for x in q if x['tier'] == 'B'),
        DEEP_AUDIT_SAMPLE=len(sam), **{k: cnt.get(k, 0) for k in STATES}, READY_TOTAL=cnt['READY_FOR_BLOCK_DECISION'] + cnt['READY_WITH_QUALIFICATION'],
        TARGET_200_READY_REACHED='YES' if cnt['READY_FOR_BLOCK_DECISION'] + cnt['READY_WITH_QUALIFICATION'] >= 200 else 'NO',
        STJ_TURMA_READY=sum(1 for x in tur if st[x['id']][0] in READY),
        STJ_TURMA_REVIEW=sum(1 for x in tur if st[x['id']][0] in ('INDIVIDUAL_REVIEW_REQUIRED', 'NEEDS_MORE_EVIDENCE', 'BLOCKED_BY_SYSTEMIC_AUDIT')),
        STJ_TURMA_REJECTED=sum(1 for x in tur if st[x['id']][0] == 'REJECT_RECOMMENDED'),
        NEW_CC_TARGETS_READY=len({t for t, _ in ready_pairs} - phys_t),
        PROJECTED_CC_READY_ONLY=f"{proj['READY_ONLY']['relations']}/{proj['READY_ONLY']['targets']}",
        PROJECTED_CC_WITH_QUALIFICATIONS=f"{proj['READY_WITH_QUALIFICATIONS']['relations']}/{proj['READY_WITH_QUALIFICATIONS']['targets']}",
        PROJECTED_CC_CEILING=f"{proj['CEILING_ALL_NOT_REJECTED']['relations']}/{proj['CEILING_ALL_NOT_REJECTED']['targets']}",
        CURRENT_CC_PHYSICAL='49/39', CURRENT_CF_PHYSICAL='315/198', NEW_CORE_ENGINE_CODE_LINES=0, REPRODUCIBILITY='PASS',
        CF_REGRESSION=cap['CF_REGRESSION'], CC_J1_J2_REGRESSION=cap['CC_J1_J2_REGRESSION'], FROZEN_LAYER_CHANGES=0,
        SD_CHANGED='NO', FIRMWARE_CHANGED='NO', RATIFIED_NEW_RELATIONS=0, DEPLOYED_NEW_RELATIONS=0, RATIFICATION_PACKET_COUNT=len(pk),
        AUTHORITY=dict(sorted(collections.Counter(r['authority'] for r in rows).items())),
        AUTHORITY_X_STATE={f'{a} | {s_}': n for (a, s_), n in sorted(collections.Counter((R[k]['authority'], v[0]) for k, v in st.items()).items())},
        TURMA_CLASSIFICATION=dict(sorted(collections.Counter(v['classification'] for v in ts.values()).items())),
        TURMA_SUBSTITUTIONS_PROPOSED=sum(1 for v in ts.values() if v['substitution']),
        TURMA_SUBSTITUTIONS_IN_READY=sum(1 for x in tur if st[x['id']][0] in READY and 'substituído' in st[x['id']][1]),
        TIER_A_STATES=dict(sorted(collections.Counter(st[x['id']][0] for x in q if x['tier'] == 'A').items())),
        CHANGED_FROM_QUALIFIED=sum(1 for x in q if st[x['id']][0] not in READY), SYSTEMIC_IMPACT=impact, DEEP_AUDIT=dm, VALIDATION=val,
        PROJECTIONS=proj, DEVICE_CAPACITY={k: v for k, v in cap.items() if k not in ('firmware',)}, CROSSTABS=crosstabs(q, rows))
    files = {
        'CC_MASS_AUDIT_ALL_932.jsonl': jsonl(all_rows),
        'CC_MASS_AUTHORITY_CLASSIFICATION.json': dumpb(dict(schema_version=1, note='autoridade jurídica, independente da confiança da extração',
                                                            summary=metrics['AUTHORITY'], items={r['id']: dict(authority=r['authority'],
                                                            basis=r['authority_basis'], tribunal=r['identity']['tribunal'], orgao=r['identity']['orgao'],
                                                            classe=r['identity']['classe'], leading_case_of=r['leading_case_of']) for r in rows})),
        'CC_MASS_TURMA_CORROBORATION.json': dumpb(dict(schema_version=1, summary=metrics['TURMA_CLASSIFICATION'], items=ts)),
        'CC_MASS_DEEP_AUDIT_SAMPLE.json': dumpb(dict(schema_version=1, metrics=dm, validation_rounds=VALIDATION_ROUNDS, systemic_findings=SYSTEMIC_FINDINGS,
                                                    sample=[dict(id=x['id'], relation_precedent=x['precedent_id'], relation_target=x['target_id'],
                                                                 rule_state=rule_st[x['id']][0], final_state=st[x['id']][0], **DEEP_REVIEW[x['id']])
                                                            for x in sam])),
        'CC_MASS_SYSTEMIC_ERRORS.md': systemic_md(SYSTEMIC_FINDINGS, impact, metrics['CHANGED_FROM_QUALIFIED']).encode('utf-8'),
        'CC_MASS_RATIFICATION_READY.json': dumpb(dict(schema_version=1, status='AWAITING_USER_RATIFICATION', human_approved=0, items=items,
                                                     evidence={x['id']: dict(quote=R[x['id']]['evidence']['quote'], field=R[x['id']]['evidence']['field'],
                                                                             identity=R[x['id']]['identity'], turma=ts.get(x['id']))
                                                               for x in q if st[x['id']][0] in READY})),
        'CC_MASS_RATIFICATION_HOLD.json': dumpb(dict(schema_version=1, items=[dict(id=x['id'], target=x['target_id'], precedent=x['precedent_id'],
                                                                                 state=st[x['id']][0], reason=st[x['id']][1], DECISAO_HUMANA='PENDING')
                                                                            for x in q if st[x['id']][0] in ('INDIVIDUAL_REVIEW_REQUIRED', 'NEEDS_MORE_EVIDENCE',
                                                                                                             'BLOCKED_BY_SYSTEMIC_AUDIT')])),
        'CC_MASS_RATIFICATION_REJECT.json': dumpb(dict(schema_version=1, items=[dict(id=x['id'], target=x['target_id'], precedent=x['precedent_id'],
                                                                                   reason=st[x['id']][1]) for x in q if st[x['id']][0] == 'REJECT_RECOMMENDED'])),
    }
    for n, (title, its) in enumerate(pk, 1):
        files[f'CC_MASS_RATIFICATION_PACKET_{n:02d}.md'] = packet_md(n, title, its, len(pk)).encode('utf-8')
    files['CC_MASS_AUDIT_METRICS.json'] = dumpb(metrics)
    files['CC_MASS_AUDIT_REPORT.md'] = report_md(metrics, pk, cap, proj).encode('utf-8')
    files['CC_MASS_AUDIT_SHA256.json'] = dumpb(dict(outputs={k: sha(v) for k, v in sorted(files.items())},
                                                    inputs={k: v['sha256'] for k, v in srcs[0].items()} | dict(
                                                        CC_MASS_DISCOVERY_QUALIFIED=sha((D / 'CC_MASS_DISCOVERY_QUALIFIED.jsonl').read_bytes().replace(b'\r\n', b'\n')),
                                                        CC_CORPUS=B.sha_file(CC_TEXT), PROCESSOS_INDEX=B.sha_file(PROCESSOS))))
    files['CC_MASS_AUDIT_CHECKPOINT.json'] = dumpb(dict(stages_completed=STAGES, stages_pending=[], errors=[], totals={k: cnt.get(k, 0) for k in STATES},
                                                       resume='python build_cc_mass_audit.py (idempotente; --check confere byte a byte)',
                                                       output_hashes={k: sha(v) for k, v in sorted(files.items())}))
    return files, metrics


def report_md(m, pk, cap, proj):
    L = ['# CC MASS AUDIT — relatório (host-only, nenhuma ratificação)', '', '```']
    for k in ('MASS_AUDIT_STATUS', 'INPUT_RELATIONS', 'RECONCILED_RELATIONS', 'TIER_A_REASSESSED', 'TIER_B_REASSESSED', 'DEEP_AUDIT_SAMPLE',
              'READY_FOR_BLOCK_DECISION', 'READY_WITH_QUALIFICATION', 'INDIVIDUAL_REVIEW_REQUIRED', 'NEEDS_MORE_EVIDENCE', 'REJECT_RECOMMENDED',
              'BLOCKED_BY_SYSTEMIC_AUDIT', 'READY_TOTAL', 'TARGET_200_READY_REACHED', 'STJ_TURMA_READY', 'STJ_TURMA_REVIEW', 'STJ_TURMA_REJECTED',
              'NEW_CC_TARGETS_READY', 'PROJECTED_CC_READY_ONLY', 'PROJECTED_CC_WITH_QUALIFICATIONS', 'PROJECTED_CC_CEILING', 'CURRENT_CC_PHYSICAL',
              'CURRENT_CF_PHYSICAL', 'NEW_CORE_ENGINE_CODE_LINES', 'REPRODUCIBILITY', 'SD_CHANGED', 'FIRMWARE_CHANGED', 'RATIFIED_NEW_RELATIONS',
              'DEPLOYED_NEW_RELATIONS', 'RATIFICATION_PACKET_COUNT'):
        L.append(f'{k} = {m[k]}')
    dm = m['DEEP_AUDIT']
    L += ['```', '', '## Autoridade jurídica (independente da confiança da extração)', '',
          '| Categoria | Relações |', '|---|---:|'] + [f'| {k} | {v} |' for k, v in m['AUTHORITY'].items()] + [
          '', 'Acórdão de Turma não é apresentado como precedente obrigatório, tese repetitiva, orientação pacificada nem posição unânime do STJ; '
          'acórdão de Seção/Corte Especial não é tratado como precedente obrigatório só pela origem colegiada.', '',
          '## Auditoria aprofundada (200) e validação independente', '',
          f"Amostra: {dm['DEEP_AUDIT_SAMPLE']} relações; com erro: {dm['RELATIONS_WITH_ERROR']}; por dimensão: "
          f"{', '.join(f'{k} {v}' for k, v in dm['ERRORS_BY_DIMENSION'].items())}; por estrato: "
          f"{'; '.join(k + ' ' + str(v.get('with_error', 0)) + '/' + str(v['n']) for k, v in dm['ERRORS_BY_STRATUM'].items())}.",
          f"Estado da regra (sem a auditoria) = estado final em {dm['RULE_STATE_AGREES_WITH_AUDITOR']} da amostra; {dm['AUDITOR_OVERRIDES']} decisões "
          'do auditor prevalecem sobre a regra para os próprios casos. ' + dm['design'] + '.',
          'Validação independente de acórdãos de Turma prontos, fora da amostra: ' + '; '.join(
              f"rodada {v['round']} ({'regras congeladas' if v['rules_frozen'] else 'antes das últimas correções'}): {v['n'] - v['errors']}/{v['n']} corretos"
              for v in m['VALIDATION']) + '. Os erros da rodada 1 viraram regra; a rodada 2 mediu a regra final.', '',
          '## Erros sistemáticos', '', 'Ver `CC_MASS_SYSTEMIC_ERRORS.md`. Impacto (relações que deixaram o estado favorável): ' +
          ', '.join(f'{k} {v}' for k, v in sorted(m['SYSTEMIC_IMPACT'].items())) + f". Total fora do estado favorável: {m['CHANGED_FROM_QUALIFIED']} de 932.", '',
          '## Acórdãos de Turma', '',
          f"Prontos (com nota de natureza persuasiva): {m['STJ_TURMA_READY']}; revisão/evidência: {m['STJ_TURMA_REVIEW']}; rejeição recomendada: "
          f"{m['STJ_TURMA_REJECTED']}. Classificação: {m['TURMA_CLASSIFICATION']}. Substituições de representante: {m['TURMA_SUBSTITUTIONS_IN_READY']} "
          f"aplicadas nos prontos ({m['TURMA_SUBSTITUTIONS_PROPOSED']} propostas). 'CORROBORATED' é indício textual entre acórdãos, não consolidação.", '',
          '## Pacotes', ''] + [f'- `CC_MASS_RATIFICATION_PACKET_{n:02d}.md` — {t} ({len(i)})' for n, (t, i) in enumerate(pk, 1)] + [
          '', 'Não pronto: `CC_MASS_RATIFICATION_HOLD.json` (revisão individual / mais evidência) e `CC_MASS_RATIFICATION_REJECT.json`.', '',
          '## Projeção (não é baseline; nada foi ratificado)', '',
          '| Cenário | Relações CC | Targets CC | Relações novas | Targets novos |', '|---|---:|---:|---:|---:|',
          f"| Baseline físico | {proj['BASELINE']['relations']} | {proj['BASELINE']['targets']} | — | — |"] + [
          f"| {n} | {v['relations']} | {v['targets']} | {v['added_relations']} | {v['new_targets']} |" for n, v in proj.items() if n != 'BASELINE'] + [
          '', 'O cenário de teto inclui casos ainda em revisão/sem evidência: limite quantitativo, não recomendação de publicação.', '',
          '## Capacidade do aparelho (SIMULATION_ONLY, maior conjunto não rejeitado)', '',
          f"Lookups {cap['LOOKUP_ENTRIES']} (baseline {cap['LOOKUP_ENTRIES_BASELINE']}; limite de segurança {cap['LOOKUP_LIMIT']}); PSRAM do lookup "
          f"{cap['LOOKUP_PSRAM_BYTES']} B; JURISPRUDENCIA.IDX {cap['RECORDS_IDX_BYTES']} B (limite {cap['RECORDS_LIMIT_BYTES']}); fichas novas "
          f"{cap['NEW_FICHAS']} ({cap['NEW_FICHAS_BYTES']} B no cartão); máximo de relações por dispositivo {cap['MAX_RELATIONS_PER_KEY']} (limite "
          f"{cap['MAX_RELACOES_ARTIGO']}); chaves duplicadas {cap['DUPLICATE_QUERY_KEYS']}; regressão CF {cap['CF_REGRESSION']}, CC-J1/J2 "
          f"{cap['CC_J1_J2_REGRESSION']}; visíveis {cap['VISIBLE']}; rótulos {cap['labels']}.",
          f"Consulta: busca linear no cache — {cap['LOOKUP_COMPARISONS_PER_QUERY']['ratio']}x as comparações do baseline por consulta (sem medir tempo).",
          'Mudança arquitetural NÃO exigida pelos limites; nota de projeto separada: acórdãos aparecem como "ACORDAO n" (rótulo existente, sem '
          'validação física, sem classe nem órgão) — distinguir "REsp n (3ª Turma)" exigiria evolução de firmware, fora desta missão.', '',
          '## Fichas futuras', '', 'As notas para o leitor (`NOTA NECESSÁRIA`) não contêm metadado interno (tier, estado editorial, flags, hashes); '
          'esses ficam no registro de auditoria. Nenhuma ficha definitiva foi produzida.', '',
          '## Próximo passo', '', '`NEXT_STEP = MASS HUMAN RATIFICATION` — não ratificado, não materializado, sem deploy.']
    return '\n'.join(L) + '\n'


def main():
    files, metrics = outputs()
    if '--check' in sys.argv:
        ok = all((D / k).is_file() and (D / k).read_bytes().replace(b'\r\n', b'\n') == v for k, v in files.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for k, v in files.items():
        (D / k).write_bytes(v)
    print(json.dumps({k: v for k, v in metrics.items() if not isinstance(v, (dict, list))}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
