"""J1.1 — writes the editorial exclusion overlay of the 20 jurisprudence links ratified by the user (2026-10-16) as false positives.

Source of the decisions: JURISPRUDENCE_AUDIT/J1_DECISIONS.json (decision REMOVE_FALSE_POSITIVE, 20/20) + user ratification below.
Output: LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1.json, same record schema as CF88_LINK_EXCLUSIONS.json (status
MATERIAL_MISMATCH_EXCLUDED). The previous overlay is NOT edited (RUN3..RUN5 stay reproducible). No relocation to the ADCT, no new link,
EXTERNAL_REVIEW_REQUIRED / DUPLICATE_OR_REDUNDANT untouched, backlog of 148 untouched. Deterministic.
Usage: python apply_j1_exclusions.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DECISIONS = HERE / 'J1_DECISIONS.json'
OUT = ROOT / 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1.json'
RATIFICATION = dict(
    by='ARTHUR', on='2026-10-16', statement='J1_REMOVE_FALSE_POSITIVE_APPROVED = 20/20',
    scope='Remover somente os 20 vínculos errados da CF (15 de outra norma, 5 do ADCT lidos como CF); sem realocação para o ADCT; '
          'preservar todos os demais vínculos; EXTERNAL_REVIEW_REQUIRED (4) e DUPLICATE_OR_REDUNDANT (1) permanecem pendentes; backlog 148 intocado.')
EXPECTED = 20


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def build():
    d = json.loads(DECISIONS.read_text(encoding='utf-8'))
    rem = [x for x in d['decisions'] if x['decision'] == 'REMOVE_FALSE_POSITIVE']
    if len(rem) != EXPECTED:
        raise SystemExit(f'REMOVE_COUNT {len(rem)}')
    recs = []
    for i, x in enumerate(sorted(rem, key=lambda x: x['relation_id']), 1):
        key = x['relation_id'].split(':', 1)[1].rsplit('@', 1)[0]
        recs.append(dict(
            reference_id=x['relation_id'], target_id=x['target_id'], source_id=x['precedent'], source_reference_id=key,
            status='MATERIAL_MISMATCH_EXCLUDED',
            verified_subject=f"{x['precedent']} ({x['processo']}): o dispositivo citado é {x['cited_norm']}.",
            expected_subject=f"{x['target_id']} (dispositivo da Constituição Federal de mesmo número)",
            reason=f"{x['cause']}: {x['comment']}",
            evidence=dict(official_source='STF (texto oficial arquivado no J4)', official_source_url=x['local_evidence']['official_url'],
                          local_thesis_sha256=x['local_evidence']['thesis_sha256'], official_content_sha256=x['local_evidence']['official_sha256'],
                          excerpt=x['local_evidence']['excerpt'], verified_on='2026-10-16',
                          verified_by='revisão de evidência local (J1) ratificada por Arthur em 2026-10-16'),
            relocation_candidate_not_applied=x['relocation_candidate'],
            decided_in=f'J1_RISK_REVIEW (J1-REMOVE-{i:02d}), ratificado em J1.1'))
    doc = dict(schema_version=1, norma_id='CF88', round='J1.1',
               policy='Overlay editorial de vínculos de jurisprudência materialmente incorretos (falsos positivos de numeração: dispositivo de outra '
                      'norma ou do ADCT lido como da CF). Mesmo mecanismo de CF88_LINK_EXCLUSIONS.json: cada registro retira exatamente um vínculo '
                      '(reference_id) do export visível; o corpus J4 e o catálogo canônico não são editados. Fail closed.',
               ratification=RATIFICATION, decisions_file=DECISIONS.relative_to(ROOT).as_posix(), decisions_sha256=sha_lf(DECISIONS),
               total=len(recs), records=recs)
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(OUT.name, hashlib.sha256(b).hexdigest(), json.loads(b)['total'])
