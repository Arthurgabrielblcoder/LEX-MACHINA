"""J2B.1: HOST-ONLY SD candidate that SUPERSEDES the J2B package before any physical deploy = current physical card (J1.4 installed, J1.5 11/11)
+ RUN9 (5 ADI links of BATCH01 + J2B_PREDEPLOY_TEMPORAL_FIX of Tema 558) + the same legacy ADI rows/fichas as J2B (append-only).
Same builder and gates as build_j2b_candidate.py (physical card reproduced first, official generator, R-only divergence, legacy append-only),
pointed at RUN9. Tema 558 keeps its legacy key, record and ficha (STF_RG_558.TXT) byte for byte.
Outputs: DEVICE_INTEGRATION/staging_sd_v1_juris_j2b_1_candidate/ (gitignored) and JURISPRUDENCE_AUDIT/J2B_1_CANDIDATE_HOST_ONLY/.
Usage: python build_j2b_1_candidate.py --commit <sha> [--runs N]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2b_candidate as B  # noqa: E402

B.RUN8_DEV = B.ROOT / 'LEGAL_TARGET_ID/derived/export_test/run9_juris_j2b_1_candidate/device_ready'
B.OUT = B.DI / 'staging_sd_v1_juris_j2b_1_candidate'
B.TMP = B.DI / '_tmp_juris_j2b_1_rebuild'
B.TMP_BASE = B.DI / '_tmp_juris_j2b_1_physical_reproduction'
B.PKG = HERE / 'J2B_1_CANDIDATE_HOST_ONLY'
B.PACKAGE = 'JURIS_J2B_1'
B.MANIFEST_NAME = 'J2B_1_PACKAGE_MANIFEST.json'
B.ENGINE_VERSION = dict(tag='cf-reference-engine-run9-juris-j2b-1', run='run9', status='RUN9_JURIS_J2B_1_CANDIDATE_HOST_ONLY',
                        derived_from='run8 (J2B: 256 + 5 ADI links) with J2B_PREDEPLOY_TEMPORAL_FIX (Tema 558: art. 100 § 9º -> art. 100)',
                        supersedes='J2B_CANDIDATE_HOST_ONLY (SUPERSEDED_BEFORE_PHYSICAL_DEPLOY)')

if __name__ == '__main__':
    B.main()
