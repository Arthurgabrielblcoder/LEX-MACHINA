"""PÓS-NOTURNA Parte D — single source for the firmware/ guards after the header-debt fix.

- The ONLY authorized change in firmware/ since the frozen points is lex_ref_detail_data.h replaced by the 124-ficha R1 header (sha-pinned).
  firmware_changes(commit) lists every other changed path under firmware/ (committed, commit..HEAD); guards assert it is empty.
- The pre-R1 header (122 fichas) that the Referências nº 4 R1 audits compare against is read from Git at the pinned commit 10e199f, never
  from the working tree (sha-checked, fail closed).
"""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER = 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h'
HEADER_R1_SHA_LF = 'e420f4dec7923036448b4cf1129c6092a9489b8c36c8cef4921a5d534b6f55f8'     # 124 fichas (R1, b5ccf96) — approved app
PRE_R1_COMMIT = '10e199f'
PRE_R1_SHA_LF = '2ca5820a170a3b08ecfa869685d319d65eee5bc94ddf0bfa5854282acce9710b'        # 122 fichas


def _sha_lf(b):
    return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()


def authorized(path):
    return path == HEADER and _sha_lf((ROOT / path).read_bytes()) == HEADER_R1_SHA_LF


def firmware_changes(commit, ref='HEAD'):
    out = subprocess.run(['git', 'diff', '--name-only', commit, ref, '--', 'firmware'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.split() if not authorized(p)]


def pre_r1_header_bytes():
    b = subprocess.run(['git', 'show', f'{PRE_R1_COMMIT}:{HEADER}'], cwd=ROOT, capture_output=True, check=True).stdout
    if _sha_lf(b) != PRE_R1_SHA_LF:
        raise SystemExit('PRE_R1_HEADER_MISMATCH')
    return b
