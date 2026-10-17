"""J2 — lightweight, reusable ALERT detectors for jurisprudence review (Fase D). They never decide: they flag what the official evidence must
confirm or reject. Pure functions over text (recommendation, ementa, tese, decision excerpt). Deterministic; no network.

  namespace_alerts(text)   -> norms other than the CF body that a citation may belong to (ADCT, EC, lei, LC, decreto, CE, LO, regimento, ...)
  temporal_alerts(text)    -> signs that the precedent judged a historical wording (redação originária / anterior / EC x / renumerado / revogado)
  status_signals(text)     -> procedural status signals (mérito, trânsito, embargos, cautelar, referendo, mérito pendente, modulação, perda de objeto)
  joint_scope(decisions)   -> SAME_JUDGMENT vs SAME_SCOPE between processes judged together (by the provisions each decision reached)
  review_flags(...)        -> all of the above, for one candidate, as the record stored in a batch decision file
The J0 priority rule is NOT changed here (selection keeps using build_j0_diagnostic_audit's rule).
"""
import re

_NS = [  # (category, pattern) — order matters only for readability
    ('ADCT', r'\bADCT\b|Ato das Disposi[cç][oõ]es Constitucionais Transit[oó]rias'),
    ('EMENDA_CONSTITUCIONAL', r'\bEmenda Constitucional\b|\bEC\s*(n[ºo°.]\s*)?\d+'),
    ('LEI_COMPLEMENTAR', r'\bLei Complementar\b|\bLC\s*(n[ºo°.]\s*)?\d+'),
    ('LEI', r'\bLei\s*(Federal\s*)?(n[ºo°.]\s*)?\d[\d.]*(/\d+)?'),
    ('CODIGO', r'\bC[oó]digo (Civil|Penal|de Processo|Tribut[aá]rio|Eleitoral)|\b(CTN|CPC|CPP|CLT|CC)\b'),
    ('DECRETO', r'\bDecreto(-Lei)?\b'),
    ('CONSTITUICAO_ESTADUAL', r'Constitui[cç][aã]o (do Estado|Estadual)|\bCE[-/ ][A-Z]{2}\b'),
    ('LEI_ORGANICA', r'\bLei Org[aâ]nica\b'),
    ('REGIMENTO_RESOLUCAO', r'\bRegimento Interno\b|\bRISTF\b|\bResolu[cç][aã]o\b'),
    ('CONVENCAO_TRATADO', r'\bConven[cç][aã]o\b|\bTratado\b|\bPacto\b'),
    ('NORMA_MUNICIPAL', r'\blei municipal\b|\bMunic[ií]pio de [A-Z]'),
]
_CF = r'\bConstitui[cç][aã]o (Federal|da Rep[uú]blica)\b|\bCF(/88|/1988|88)?\b|\bCRFB\b|\bCarta (da Rep[uú]blica|Magna)\b'
_TEMPORAL = [
    ('REDACAO_ORIGINARIA', r'reda[cç][aã]o origin[aá]ria|reda[cç][aã]o original\b|texto origin[aá]rio'),
    ('REDACAO_ANTERIOR', r'reda[cç][aã]o anterior|antes da (EC|Emenda)|anterior [àa] (EC|Emenda)'),
    ('REDACAO_DADA_POR_EC', r'(reda[cç][aã]o dada|inclu[ií]d[oa]s?) pel[ao] (EC|Emenda Constitucional)\s*(n[ºo°.]\s*)?\d+'),
    ('RENUMERADO', r'renumerad[oa]'),
    ('REVOGADO', r'revogad[oa]'),
]
_STATUS = [
    ('MERITO_JULGADO', r'julg(ou|ada?|ado) (parcialmente )?(procedente|improcedente)|m[eé]rito (julgado|da a[cç][aã]o)|converteu o julgamento'),
    ('TRANSITO_EM_JULGADO', r'tr[aâ]nsit(o|ado) em julgado'),
    ('EMBARGOS', r'\bembargos de declara[cç][aã]o\b|\bED\b'),
    ('CAUTELAR', r'\bcautelar\b|\bliminar\b|\bMC\b'),
    ('REFERENDO', r'\breferend(o|ou|ada)\b'),
    ('MERITO_PENDENTE', r'm[eé]rito pendente|conclusos ao relator|aguardando julgamento'),
    ('MODULACAO', r'\bmodula[cç][aã]o\b|\bmodul(am|ou|ar)(-se)?\b|efic[aá]cia prospectiva|efeitos ex nunc'),
    ('PERDA_DE_OBJETO', r'perda (superveniente )?(do|de) objeto|prejudicad[ao]'),
    ('TESE_FIXADA', r'\btese\b'),
]


def _hits(text, table):
    t = text or ''
    return sorted({cat for cat, pat in table if re.search(pat, t, re.I)})


def namespace_alerts(text):
    """Categories of non-CF norms mentioned. 'CF' is reported in cf_mentioned. An alert is not a rejection."""
    t = text or ''
    others = _hits(t, _NS)
    return dict(cf_mentioned=bool(re.search(_CF, t)), other_norms=others,
                alert=bool(others) and not re.search(_CF, t) or 'CONSTITUICAO_ESTADUAL' in others)


def temporal_alerts(text):
    hits = _hits(text, _TEMPORAL)
    ecs = sorted({int(m.group(2)) for m in re.finditer(r'\b(EC|Emenda Constitucional)\s*(?:n[ºo°.]\s*)?(\d+)', text or '', re.I)})
    return dict(signals=hits, ecs_cited=ecs, alert=bool(set(hits) & {'REDACAO_ORIGINARIA', 'REDACAO_ANTERIOR', 'RENUMERADO', 'REVOGADO'}))


def status_signals(text):
    s = _hits(text, _STATUS)
    provisional = bool({'CAUTELAR', 'REFERENDO', 'MERITO_PENDENTE'} & set(s)) and 'MERITO_JULGADO' not in s
    return dict(signals=s, provisional=provisional)


def joint_scope(decisions):
    """decisions: {process: set(provisions reached)} for processes judged together. Pairwise SAME_SCOPE only if the sets are equal."""
    procs = sorted(decisions)
    out = {}
    for i, a in enumerate(procs):
        for b in procs[i + 1:]:
            sa, sb = set(decisions[a]), set(decisions[b])
            out[f'{a}|{b}'] = dict(relation='SAME_JUDGMENT_SAME_SCOPE' if sa == sb else 'SAME_JUDGMENT_NOT_SAME_SCOPE',
                                  only_in={a: sorted(sa - sb), b: sorted(sb - sa)}, common=sorted(sa & sb))
    return out


def scope_allows(decisions, process, provision):
    """True if `process` itself reached `provision` (a joint record may only be shown where every alias reached it)."""
    return provision in set(decisions.get(process, ()))


def review_flags(recommendation_text, evidence_text):
    return dict(namespace=namespace_alerts(evidence_text), namespace_in_recommendation=namespace_alerts(recommendation_text),
                temporal=temporal_alerts(evidence_text), status=status_signals(evidence_text))
