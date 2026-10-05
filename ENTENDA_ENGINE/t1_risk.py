"""ENTENDA-T1 risk classifier (LOW / MEDIUM / HIGH) for draft explanations of a production batch.

Deterministic, rule-based and conservative: any escalation rule sends the explanation to HIGH. HIGH never means "wrong"; it means
the explanation needs full human review (queue D). The classifier reads the official snapshot (whole article subtree for OVERVIEW,
device plus covered siblings for BLOCK), the draft body and notes, and a per-target vigency map (amendment/"Vide" annotations of the
canonical source). It never changes content or review_status.

Escalation to HIGH (mission ENTENDA_CF_PRODUCTION_BATCH_06):
  EC_WORDING            the target or a covered/subdivision target has wording given or included by a constitutional amendment
  EXTERNAL_LAW_STATE    a "Vide" annotation, EXTERNAL_VERIFICATION_REQUIRED note, or recent wording to be verified
  TRANSITION_RULE       the snapshot or the draft deals with transition rules
  JURISPRUDENCE         a JURISPRUDENCIA note, or "sumula"/"tema" in the draft
  QUORUM                qualified or special majorities
  DEADLINE              a deadline (prazo, dias, horas, meses, anos with a number)
  NUMBER_OR_PERCENTAGE  numbers or percentages written in the snapshot
  SENSITIVE_THEME       loss of mandate, immunity, incompatibility, sanction, crime, rights or prerogatives
  EXCEPTION             "salvo", "exceto", "ressalvado"
  COMPLEX_REMISSION     two or more references to other articles
  BLOCK_MULTI_DEPENDENCY BLOCK spanning three or more targets (covered siblings plus subdivisions)
  LAW_DEPENDENCY        lei complementar, regulation or "na forma da lei"
  INTERPRETIVE_CONTROVERSY the draft itself flags an interpretive question
MEDIUM: a single remission or a list structure (subdivisions). LOW: none of the above.
"""
import re

import entenda_engine as E

NUM_WORDS = (r'dois|duas|tr[êe]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|quinze|vinte|trinta|quarenta|cinquenta|sessenta|'
             r'setenta|oitenta|noventa|cem|cento|duzentos|mil')
RULES = (
    ('TRANSITION_RULE', re.compile(r'\btransi[çc][ãa]o\b', re.I), 'snapshot+draft'),
    ('QUORUM', re.compile(r'\bmaioria\b|\bdois ter[çc]os\b|\btr[êe]s quintos\b|\bum ter[çc]o\b|\bqu[óo]rum\b|\bter[çc]a parte\b', re.I), 'snapshot'),
    ('DEADLINE', re.compile(r'\bprazo\b|\b(?:' + NUM_WORDS + r'|\d+)\s+(?:dias?|horas?|meses|anos)\b', re.I), 'snapshot'),
    ('NUMBER_OR_PERCENTAGE', re.compile(r'\bpor cento\b|%|\b(?:' + NUM_WORDS + r')\b|\bd[ée]cimos?\b|\bquintos?\b', re.I), 'snapshot'),
    ('SENSITIVE_THEME', re.compile(r'perd(?:a|er[áa]) (?:do|o) mandato|\bimunidade|\binviol[áa]v|\bincompat[íi]v|\bsan[çc][ãa]o|\bsan[çc][õo]es|'
                                   r'\bmulta\b|\bcrimes?\b|\bprerrogativ|\bdireitos?\b|\bgarantias?\b|\bcassa|\bsob pena\b|responsabilidade solid', re.I), 'snapshot'),
    ('EXCEPTION', re.compile(r'\bsalvo\b|\bexceto\b|\bressalvad[oa]s?\b|\bressalva\b|\bexcetuad', re.I), 'snapshot'),
    ('LAW_DEPENDENCY', re.compile(r'\blei complementar\b|\bregulament|\bna forma da lei\b|\bnos termos da lei\b|\blei dispor[áa]\b|'
                                  r'\blei estabelecer[áa]\b|\bprevist[oa]s? em lei\b|\blei espec[íi]fica\b', re.I), 'snapshot'),
)
ID_PREFIX_RE = re.compile(r'^[A-Z0-9]+:[^\t\n]*\t', re.M)
REMISSION_RE = re.compile(r'\barts?\.\s*(\d+)', re.I)
JURIS_NOTE_RE = re.compile(r'JURISPRUD', re.I)
JURIS_BODY_RE = re.compile(r'\bs[úu]mula\b|\btema\s+(?:n[ºo.]*\s*)?\d', re.I)
CONTROVERSY_RE = re.compile(r'interpreta[çc][ãa]o constitucional|quest[ãa]o de interpreta[çc][ãa]o|controv[ée]rs', re.I)
EXTERNAL_NOTE_RE = re.compile(r'EXTERNAL_VERIFICATION_REQUIRED|\bVide\b', re.I)


def scope_targets(rec, ctx):
    """Targets whose official text the explanation speaks for."""
    g, tid = rec['granularity'], rec['target_id']
    if g['role'] == 'OVERVIEW':
        return [t for t in ctx.subtree(tid) if ctx.effective_status(t) == 'CURRENT']
    out = [tid] + list(g.get('covered_targets', []))
    if g['role'] == 'BLOCK':
        out += [s for t in list(out) for s in ctx.subtree(t) if s != t and ctx.effective_status(s) == 'CURRENT']
    return sorted(set(out), key=out.index)


def classify(rec, ctx, vigency=None):
    """Returns dict(level, reasons=[...], rules=[...]) for one stamped record. vigency: {target_id: [annotation, ...]}."""
    vigency = vigency or {}
    targets = scope_targets(rec, ctx)
    snap = rec['source']['source_text_snapshot'] + '\n' + '\n'.join(ctx.text.get(t, '') or '' for t in targets if t != rec['target_id'])
    snap = ID_PREFIX_RE.sub('', snap)  # snapshot lines carry target ids ("CF88:ART.49:INC.IX<tab>"): never read them as remissions
    c = rec['content']
    draft = ' '.join([c[k] for k in E.REQUIRED_TEXT] + [c.get('atencao') or ''])
    notes = ' '.join(rec.get('external_layer_notes') or [])
    hits = []

    def hit(code, detail):
        hits.append((code, detail))

    ann = [(t, a) for t in targets for a in vigency.get(t, [])]
    ec = [f"{t.split(':', 1)[1]}: {a}" for t, a in ann if re.search(r'Emenda Constitucional', a, re.I)]
    if ec:
        hit('EC_WORDING', '; '.join(ec[:3]) + (f' (+{len(ec) - 3})' if len(ec) > 3 else ''))
    vide = [f"{t.split(':', 1)[1]}: {a}" for t, a in ann if re.search(r'\bVide\b', a)]
    if vide or EXTERNAL_NOTE_RE.search(notes):
        hit('EXTERNAL_LAW_STATE', '; '.join(vide) or 'nota de verificacao externa')
    for code, rx, where in RULES:
        m = rx.search(snap) or (rx.search(draft) if where == 'snapshot+draft' else None)
        if m:
            hit(code, m.group(0))
    if JURIS_NOTE_RE.search(notes) or JURIS_BODY_RE.search(draft):
        hit('JURISPRUDENCE', 'nota da camada JURISPRUDENCIA' if JURIS_NOTE_RE.search(notes) else JURIS_BODY_RE.search(draft).group(0))
    refs = sorted({m.group(1) for m in REMISSION_RE.finditer(snap)}, key=int)
    if len(refs) >= 2:
        hit('COMPLEX_REMISSION', 'arts. ' + ', '.join(refs[:6]))
    if rec['granularity']['role'] == 'BLOCK' and len(targets) >= 3:
        hit('BLOCK_MULTI_DEPENDENCY', f'{len(targets)} dispositivos')
    if CONTROVERSY_RE.search(c.get('atencao') or '') or CONTROVERSY_RE.search(notes):
        hit('INTERPRETIVE_CONTROVERSY', (CONTROVERSY_RE.search(c.get('atencao') or '') or CONTROVERSY_RE.search(notes)).group(0))
    if hits:
        return dict(level='HIGH', rules=[h[0] for h in hits], reasons=[f'{a}: {b}' for a, b in hits])
    medium = []
    if refs:
        medium.append(f'remissao: art. {refs[0]}')
    if len(targets) > 1:
        medium.append(f'estrutura de lista/bloco: {len(targets)} dispositivos')
    if medium:
        return dict(level='MEDIUM', rules=['REMISSION_OR_LIST'], reasons=medium)
    return dict(level='LOW', rules=[], reasons=['regra simples, sem remissao, numero, prazo, excecao ou tema sensivel'])
