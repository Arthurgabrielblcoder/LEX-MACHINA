"""Prepared canonical path, blocked until explicit audited development gate passes."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input_r1b import load_canonical
from proof_compiler_v2 import iter_exhaustive
from proof_compiler_r1 import load, require


def iter_full():
    gate=load(ROOT/'00_CHECKPOINTS/FINAL_DEVELOPMENT_GATE.json')
    inp=load_canonical()
    require(gate['input_hash']==inp.hash and gate['passed'], 'Gate de desenvolvimento não satisfeito: execução final bloqueada')
    yield from iter_exhaustive(inp)


if __name__=='__main__':
    raise SystemExit('Runner preparado, não executado. Consulte FINAL_DEVELOPMENT_GATE.json; nenhum desbloqueio automático.')
