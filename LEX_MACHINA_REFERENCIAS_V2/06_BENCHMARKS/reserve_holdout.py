"""Reserve human-unlabelled pairs; identities alone exclude known development pairs."""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'05_COMPILADOR'))
from canonical_input_r1 import load_canonical
from proof_compiler_r1 import load, serialized, file_hash


def reserve():
    inp = load_canonical()
    master = load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
    excluded = {(p['device_id'], p['work_id']) for p in master['pairs']}
    pilot = load(ROOT/'06_BENCHMARKS/PROVAS_PILOTO_V2_R1.json')['pairs']
    excluded.update((p['device_id'], p['work_id']) for p in pilot)
    strata = defaultdict(list)
    seed = 'LEX-MACHINA-V2-HOLDOUT-2026-09-24-01'
    for did, d in sorted(inp.devices.items()):
        for wid, w in sorted(inp.works.items()):
            if (did, wid) in excluded:
                continue
            stratum = (did.split(':')[0], w['tipo'], 'REPRESENTADO' if d['nuclei'] else 'NAO_REPRESENTADO')
            key = hashlib.sha256((seed+'|'+did+'|'+wid).encode()).hexdigest()
            strata[stratum].append((key, did, wid))
    selected = []
    for stratum, pool in sorted(strata.items()):
        for key, did, wid in sorted(pool)[:6]:
            selected.append(dict(device_id=did, work_id=wid, stratum=list(stratum), selection_key=key,
                                 human_label=None, human_rationale=None))
    return dict(schema='HOLDOUT_V2_BLIND_1', seed=seed, count=len(selected),
                sampling='6 menores SHA256 por norma × mídia × presença de representação; sem decisões ou scores no seletor.',
                canonical_input_hash_at_reservation=inp.hash,
                excluded_unique_pairs=len(excluded), excluded_master_pairs=len(master['pairs']),
                excluded_identity_sha256=hashlib.sha256(serialized(sorted(excluded)).encode()).hexdigest(),
                label_master_sha256=file_hash(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json'),
                strata={ '|'.join(k):min(6,len(v)) for k,v in sorted(strata.items())}, pairs=selected,
                limitations=['Sem rótulos humanos novos: não mede precisão externa.',
                             'Cegueira relativa aos rótulos, não a obras/dispositivos: representação e provas diagnósticas anteriores já existiam.',
                             'A presença de estratos sem representação permite medir abstenção; não representa amostra de vínculos aprováveis.',
                             'Não executar avaliação/autorrotulação desta reserva antes da adjudicação independente.'])


if __name__ == '__main__':
    print(json.dumps(reserve(), ensure_ascii=False))
