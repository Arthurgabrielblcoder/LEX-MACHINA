"""J2B — revalidation gate for provisional jurisprudence (cautelar / mérito pendente). MANDATORY before any deploy of these links.

Reads JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json. For each item: FAIL when last_verified_on is older than max_age_days
relative to --as-of (explicit date, never the clock, so the result is reproducible), or when the registry records the trigger as fired
(merit_judged=true) without a new review. Exit 0 = PASS, 2 = REVALIDATION_REQUIRED.
Usage: python check_j2b_provisional.py --as-of YYYY-MM-DD
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REG = Path(__file__).resolve().parent / 'J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json'


def check(as_of, reg=REG):
    d = json.loads(Path(reg).read_text(encoding='utf-8'))
    out = []
    for x in d['items']:
        age = (as_of - dt.date.fromisoformat(x['last_verified_on'])).days
        due = age > x['max_age_days'] or age < 0 or x.get('merit_judged') is True
        out.append(dict(source_id=x['source_id'], targets=x['targets'], last_verified_on=x['last_verified_on'], age_days=age,
                        max_age_days=x['max_age_days'], trigger=x['trigger'], result='REVALIDATION_REQUIRED' if due else 'PASS'))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--as-of', required=True)
    res = check(dt.date.fromisoformat(ap.parse_args().as_of))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(0 if all(r['result'] == 'PASS' for r in res) else 2)
