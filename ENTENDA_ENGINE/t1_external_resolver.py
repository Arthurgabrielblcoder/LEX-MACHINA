"""ENTENDA-T1 A6: resolver of external dependencies (law, regulation, jurisprudence) before declaring EXTERNAL_VERIFICATION_REQUIRED.

Order (stops at the first source that gives validated evidence):
  1. T1_EXTERNAL_CATALOG.json (entry linked in the text, or catalogued target)
  2. validated relations of the Relations Engine (A_EXPRESSA / B_REGULAMENTACAO_OFICIAL with EXIBIR; global catalog status ATUAL)
  3. local legal corpus (relation says the destination text is available locally)
  4. provenance already registered in the ENTENDA record (human_review.content_provenance)
  5. otherwise: EXTERNAL_EVIDENCE_LOCAL_PENDING if only pending/weak relations exist, else EXTERNAL_VERIFICATION_REQUIRED

A relation is evidence, never truth for the T1 core: it does not approve anything and does not replace the provenance rule of A6.
ENTENDA and the Relations Engine have independent editorial processes: an ENTENDA approved with HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE
provenance does not promote a relation that stays EXTERNAL_EVIDENCE_LOCAL_PENDING (see standard A6.11).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

AVAILABLE = 'EXTERNAL_EVIDENCE_AVAILABLE'
PENDING = 'EXTERNAL_EVIDENCE_LOCAL_PENDING'
REQUIRED = 'EXTERNAL_VERIFICATION_REQUIRED'
VALIDATED_CLASSES = {'A_EXPRESSA', 'B_REGULAMENTACAO_OFICIAL'}
EXTERNAL_CODES = {'EXTERNAL_FACT_NEEDS_PROVENANCE', 'EXTERNAL_FACT_NO_PROVENANCE', 'LAW_STATUS_CLAIM', 'CATALOG_LINK_MISSING', 'CATALOG_CONTRADICTION'}


def _tid(rel):
    """Relations Engine origin -> CF88 target id (article / paragraph level; inner paths fall back to the article)."""
    if rel.get('origem_norma') != 'CF88':
        return []
    if 'origem_artigo' in rel:
        art, par = str(rel['origem_artigo']), rel.get('origem_paragrafo')
        base = f'CF88:ART.{art}'
        if par:
            p = str(par).upper()
            return [f"{base}:PAR.{'UNICO' if p in ('UNICO', 'ÚNICO', 'PU') else p}"]
        return [base]
    out = []
    for c in rel.get('origem_caminhos', []):
        m = re.match(r'^(\d+(?:-[A-Z])?)', str(c))
        if m:
            out.append(f'CF88:ART.{m.group(1)}')
    return sorted(set(out))


def relation_status(rel):
    if rel.get('status') == 'ATUAL' and 'classe' not in rel:
        return 'VALIDATED'
    if rel.get('classe') in VALIDATED_CLASSES and rel.get('decisao') == 'EXIBIR':
        return 'VALIDATED'
    if rel.get('classe') == 'C_EXTERNA_PENDENTE_VALIDACAO':
        return 'PENDING'
    return 'WEAK'


def _evidence(rel, source):
    return dict(norma=rel.get('destino_norma'), tipo=(rel.get('tipos') or [rel.get('tipo')])[0], fonte=(rel.get('fontes') or ['?'])[0]
                if isinstance(rel.get('fontes'), list) else 'relacao_oficial', status=relation_status(rel),
                classe=rel.get('classe'), decisao=rel.get('decisao') or rel.get('status'), vigencia=rel.get('vigencia_status'),
                url=(rel.get('urls') or [None])[0] if isinstance(rel.get('urls'), list) else (rel.get('fontes') or {}).get('relacao_oficial'),
                texto_local=bool(rel.get('texto_local_disponivel')), evidencia=(rel.get('evidencias') or [None])[0], source=source)


class RelationsIndex:
    def __init__(self, sources):
        """sources: [{"path": ..., "role": "VALIDATED"|"POOL"}] or already-loaded [{"relations": [...], "source": name}]."""
        self.by_target, self.loaded = {}, []
        for s in sources:
            rels = s.get('relations')
            name = s.get('source') or s.get('path')
            if rels is None:
                p = ROOT / s['path']
                if not p.is_file():
                    self.loaded.append(dict(source=name, available=False))
                    continue
                rels = json.loads(p.read_text(encoding='utf-8')).get('relacoes', [])
            self.loaded.append(dict(source=name, available=True, relations=len(rels)))
            for r in rels:
                for t in _tid(r):
                    self.by_target.setdefault(t, []).append(_evidence(r, name))

    @classmethod
    def from_config(cls, cfg):
        return cls(cfg.get('external_resolver', {}).get('relations_sources', []))

    def for_target(self, tid):
        return list(self.by_target.get(tid, []))


def resolve(rec, catalog, relations, provenance):
    """Returns dict(status, via, evidence) for the external dependency of an ENTENDA record."""
    tid = rec['target_id']
    text = '\n'.join([rec['content'].get(k) or '' for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')]
                     + list(rec.get('external_layer_notes', []))).lower()
    ev = []
    for e in catalog.get('entries', []):                                                    # 1. T1 catalog
        if tid in e['applies_to_targets'] or any(r in text for r in e['refs']):
            ev.append(dict(source='T1_EXTERNAL_CATALOG', entry=e['id'], provenance_required=e['provenance_required']))
            if not e['provenance_required']:
                return dict(status=AVAILABLE, via='T1_EXTERNAL_CATALOG', evidence=ev)
    rels = relations.for_target(tid) if relations else []
    ev += rels
    if any(r['status'] == 'VALIDATED' for r in rels):                                       # 2. validated relations
        return dict(status=AVAILABLE, via='RELATIONS_ENGINE_VALIDATED', evidence=ev)
    if any(r['texto_local'] and r['status'] != 'WEAK' for r in rels):                       # 3. local legal corpus
        return dict(status=AVAILABLE, via='LOCAL_LEGAL_CORPUS', evidence=ev)
    if provenance:                                                                          # 4. ENTENDA provenance
        return dict(status=AVAILABLE, via='ENTENDA_CONTENT_PROVENANCE', evidence=ev + [dict(source='content_provenance', items=len(provenance))])
    if any(r['status'] == 'PENDING' for r in rels):                                         # 5. pending only
        return dict(status=PENDING, via='RELATIONS_ENGINE_PENDING', evidence=ev)
    return dict(status=REQUIRED, via=None, evidence=ev)
