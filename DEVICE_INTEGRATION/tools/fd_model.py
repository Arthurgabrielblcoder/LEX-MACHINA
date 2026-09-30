"""Host-side model of the SD file-handle lifecycle of the DEVICE V1 boot diagnostic (FILE_DESCRIPTOR_POLICY.md).

Not a FAT simulation: it replays the OPEN/CLOSE sequence of the firmware (the same sequence the firmware prints as
"LEXV1: OPEN ... OPEN_COUNT=n" / "LEXV1: CLOSE ...") against a VFS limit (max_files) that already has `legacy_open`
handles taken by the legacy firmware. A3B-FLASH (max_files=5) logged 5 successful DEVICE V1 opens (VER, TARGETS,
TEXT_MAP, ENTENDA_LOOKUP, REF_LOOKUP) -> the legacy held 0 handles at boot; LEGACY_RESERVE covers the legacy UI later.

OLD_FLOW = candidate 04cb218a (A3B-FLASH, rolled back). NEW_FLOW = A3B-PREP2 candidate. Each step is (op, name) with
op in {'open', 'close'}; queries are expanded from the diagnostic case table with the simulator's real data (a payload is
opened only if the lookup row exists / the reference count is > 0).
"""
import sys
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DI / 'tools'))

LEGACY_OPEN_OBSERVED = 0          # at boot, when the diagnostic runs (A3B-FLASH serial log)
LEGACY_RESERVE = 2                # reader file + one legacy index/directory while DEVICE V1 is in use (policy assumption)
SD_MAX_FILES_LEGACY = 5
SD_MAX_FILES_DEVICE_V1 = 12
FD_STEADY_MAX = 3
FD_PEAK_MAX = 6
FD_HEADROOM_MIN = 4

QUERIES = ('CF88:ART.5:INC.V', 'CF88:ART.21:INC.XXIV', 'CF88:ART.22:INC.XXIX', 'CF88:ART.24:PAR.4', 'CF88:ART.37:PAR.6',
           'CF88:ART.60:PAR.4:INC.IV', 'ADCT:ART.10:INC.II', 'CF88:ART.114:INC.VIII', 'CF88:ART.25', 'CF88:ART.999')
BLOCK_ANCHORS = {'CF88:ART.5:INC.V': 'CF88:ART.5:INC.IV', 'CF88:ART.24:PAR.4': 'CF88:ART.24:PAR.3'}
REF_CASES = ('CF88:ART.21:INC.XXIV', 'CF88:ART.25', 'CF88:ART.37:PAR.6')

OLD_FLOW = [('open', 'LEXV1_VER'), ('open', 'TARGETS'), ('open', 'TEXT_MAP'), ('open', 'ENTENDA_LOOKUP'), ('open', 'REF_LOOKUP'),
            ('open', 'ENTENDA_PAYLOAD'), ('open', 'REF_PAYLOAD'),
            ('open', 'CF88_RUNTIME'), ('close', 'CF88_RUNTIME'),            # runtime sha256 while 7 were open
            ('open', 'TEXT_MAP#sha'), ('close', 'TEXT_MAP#sha'),
            ('open', 'CF88_RUNTIME'), ('close', 'CF88_RUNTIME')]            # text position search


def new_flow(dev):
    """dev: device_lookup_simulator.Device over the staged overlay (decides which payloads are actually opened)."""
    f = [('open', 'LEXV1_VER'), ('close', 'LEXV1_VER'),
         ('open', 'CF88_RUNTIME'), ('close', 'CF88_RUNTIME'),               # sha256
         ('open', 'TEXT_MAP'), ('close', 'TEXT_MAP'),                       # sha256
         ('open', 'CF88_RUNTIME'), ('close', 'CF88_RUNTIME'),               # structural position of art. 114, VIII
         ('open', 'TEXT_MAP'), ('close', 'TEXT_MAP'),                       # index: guards + TEXT -> TARGET
         ('open', 'TARGETS'), ('open', 'ENTENDA_LOOKUP'), ('open', 'REF_LOOKUP')]
    for tid in QUERIES:
        exists = dev.targets.find(tid) is not None
        if exists and dev.ent.find(tid) is not None:
            f += [('open', 'ENTENDA_PAYLOAD'), ('close', 'ENTENDA_PAYLOAD')]
        if exists and len(dev.references(tid)) > 0:
            f += [('open', 'REF_PAYLOAD'), ('close', 'REF_PAYLOAD')]
        if tid in BLOCK_ANCHORS and dev.ent.find(tid) is not None:
            f += [('open', 'ENTENDA_PAYLOAD'), ('close', 'ENTENDA_PAYLOAD')]
    for tid in REF_CASES:
        if len(dev.references(tid)) > 0:
            f += [('open', 'REF_PAYLOAD'), ('close', 'REF_PAYLOAD')]
    f += [('close', 'TARGETS'), ('close', 'ENTENDA_LOOKUP'), ('close', 'REF_LOOKUP')]
    return f


def replay(flow, max_files, legacy_open=LEGACY_OPEN_OBSERVED):
    """Returns dict(ok, peak, failed=[names that could not open], steady, final_open, dup)."""
    open_set, peak, failed, dup = [], 0, [], []
    for op, name in flow:
        base = name.split('#')[0]
        if op == 'open':
            if base in [n.split('#')[0] for n in open_set]:
                dup.append(base)
            if legacy_open + len(open_set) >= max_files:
                failed.append(name)
                continue
            open_set.append(name)
            peak = max(peak, len(open_set))
        else:
            if name in open_set:
                open_set.remove(name)
    return dict(ok=not failed, peak=peak, failed=failed, final_open=len(open_set), duplicates=dup,
                headroom=max_files - legacy_open - peak)


def steady_set(flow):
    """Handles open right before the first query payload (the steady-state set)."""
    open_set = []
    for op, name in flow:
        if op == 'open' and name in ('ENTENDA_PAYLOAD', 'REF_PAYLOAD'):
            return list(open_set)
        if op == 'open':
            open_set.append(name)
        elif name in open_set:
            open_set.remove(name)
    return open_set
