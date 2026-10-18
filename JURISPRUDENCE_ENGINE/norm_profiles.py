"""JURISPRUDENCE_ENGINE — norm profiles + thin adapters over the CF tools (wrappers; the CF modules are NOT modified).

A profile carries only what varies between norms: target namespaces, the "home norm" markers used by the namespace audit, the
amendment vocabulary used by the temporal audit, the official compiled text, the expected courts and the discovery adapters.
CF88 is described here for backward compatibility (it mirrors the constants already hard-coded in the J2 pipeline); CC2002 is the
first non-CF profile (portability pilot). Target ids keep the existing grammar (LEGAL_TARGET_ID/target_id.py): CF88:ART.5 stays valid.
"""
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / 'LEGAL_TARGET_ID'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import citation_parser as CP  # noqa: E402
import j2_auditors as AUD  # noqa: E402
import target_id as T  # noqa: E402


@dataclass(frozen=True)
class NormProfile:
    norm_id: str
    namespaces: tuple
    home_markers: str                    # regex: the evidence names THIS norm
    amendment_markers: str               # regex: the evidence speaks of a historical wording of THIS norm
    official_text_url: str
    expected_courts: tuple               # in order of expected weight for this norm
    discovery_adapters: tuple
    intentional_rules: tuple = field(default=())


PROFILES = {
    'CF88': NormProfile(
        'CF88', ('CF88', 'ADCT'), AUD._CF, r'\b(EC|Emenda Constitucional)\s*(n[ºo°.]\s*)?\d+|reda[cç][aã]o origin[aá]ria',
        'https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm', ('STF',),
        ('ENTENDA_RECOMMENDATIONS (J0)', 'PLANALTO_VIDE_ANNOTATIONS', 'STF_CONSTITUICAO_E_O_SUPREMO'),
        ('ADCT sub-namespace (parent CF88)', 'historical wording linked only at article level (J1.4/J2B.1)', 'device files CF88_TARGETS.IDX')),
    'CC2002': NormProfile(
        'CC2002', ('CC2002',), r'C[óo]digo Civil|\bCC(/2002|/02)?\b|Lei\s*(n[ºo°.]\s*)?10\.?406',
        r'(reda[cç][aã]o dada|inclu[ií]d[oa]|revogad[oa])\s+pel[ao]\s+Lei|reda[cç][aã]o (anterior|origin[aá]ria)|C[óo]digo Civil de 1916|\bCC/1916\b',
        'https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm', ('STJ', 'STF'),
        ('PLANALTO_VIDE_ANNOTATIONS', 'STF_SEARCH_RG_MERIT_CITING_NORM'), ()),
}


def namespace_check(profile, evidence):
    """Profile-aware namespace audit: the CF auditor treats any non-CF norm as an alert; here the home norm is the profile's."""
    t = evidence or ''
    home = bool(re.search(profile.home_markers, t, re.I))
    cf_view = AUD.namespace_alerts(t)
    others = [o for o in cf_view['other_norms'] if not (profile.norm_id != 'CF88' and o == 'CODIGO' and home)]
    return dict(home_norm_mentioned=home, other_norms=others, cf_auditor_alert=cf_view['alert'], result='PASS' if home else 'ALERT')


def temporal_check(profile, amendments, judgment_year):
    """Amendment notes of the dispositivo (Planalto, current wording) vs the judgment year: a wording given AFTER the judgment means
    the precedent may have judged a historical text (fail closed -> human)."""
    later = [a for a in amendments if a['year'] > judgment_year]
    return dict(amendments=amendments, later_than_judgment=later, result='TEMPORAL_ALERT' if later else 'CURRENT')


def citation_granularity(profile, text, article):
    """citation_parser is norm-agnostic in grammar but CF-centred in norm detection: a CC citation comes back as norm OTHER with
    label 'Código Civil'. Accept it as the home norm when the label matches the profile."""
    p = CP.parse_for_article(text, article)
    if p['status'] != 'OK':
        return dict(status=p['status'], reason=p.get('reason'), targets=[])
    home = p['norm'] == 'CF' if profile.norm_id == 'CF88' else bool(re.search(profile.home_markers, p.get('norm_label') or '', re.I))
    if not home:
        return dict(status='OTHER_NORM', norm_label=p.get('norm_label'), targets=[])
    targets = []
    for comp in p['components']:
        kind, val = comp
        if kind == 'PAR':
            targets.append(T.format_target_id(profile.norm_id, article, paragraph=val))
        elif kind == 'INC':
            targets.append(T.format_target_id(profile.norm_id, article, inciso=val))
    return dict(status='OK', targets=targets)
