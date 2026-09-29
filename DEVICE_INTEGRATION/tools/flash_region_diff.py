"""Region-by-region comparison of ESP32 full-flash dumps under FLASH_INTEGRITY_POLICY.md (read-only, host side).

The partition table is re-parsed from the CURRENT dump (never taken from an older report). Every byte of the flash belongs to
exactly one region; each region gets a policy class. Verdict is fail closed:
  - any difference in an IMMUTABLE_CRITICAL or UNPARTITIONED region -> BLOCK;
  - a difference in a MUTABLE_PERSISTENT region (NVS) -> ALLOWED_EXPLAINED only if every changed NVS entry is decoded and
    belongs to an explicitly allow-listed namespace/key; otherwise BLOCK;
  - DIAGNOSTIC_CONDITIONAL (coredump) -> REVIEW (reported, not silently accepted).
Usage: python flash_region_diff.py <reference_dump> <current_dump> [<out_json>]
"""
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

FLASH_SIZE = 16 * 1024 * 1024
BOOTLOADER = (0x0, 0x8000)
PTABLE = (0x8000, 0x1000)
# NVS changes that are explained and allowed (namespace, key). phy/cal_data = RF calibration rewritten by ESP-IDF at radio init.
NVS_ALLOWED = {('phy', 'cal_data'), ('phy', 'cal_mac'), ('phy', 'cal_version')}
TYPES = {0x01: 'u8', 0x11: 'i8', 0x02: 'u16', 0x12: 'i16', 0x04: 'u32', 0x14: 'i32', 0x08: 'u64', 0x18: 'i64',
         0x21: 'str', 0x41: 'blob_data', 0x42: 'blob_idx'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def parse_partitions(img):
    out, md5 = [], None
    for i in range(PTABLE[0], PTABLE[0] + PTABLE[1], 32):
        e = img[i:i + 32]
        if e[:2] == b'\xeb\xeb':
            md5 = e[16:32].hex()
            break
        if e[:2] != b'\xaa\x50':
            break
        off, size = struct.unpack('<II', e[4:12])
        out.append(dict(name=e[12:28].split(b'\0')[0].decode('ascii'), type=e[2], subtype=e[3], offset=off, size=size))
    if md5 is not None:
        calc = hashlib.md5(img[PTABLE[0]:PTABLE[0] + 32 * len(out)]).hexdigest()
        if calc != md5:
            raise SystemExit(f'PARTITION_TABLE_MD5_MISMATCH {calc} != {md5}')
    return out, md5


def active_app(img, parts):
    """otadata: two 32-byte records (seq u32 ... crc u32 over seq). Highest valid seq selects ota_(seq-1) % n_ota."""
    ota = next((p for p in parts if p['type'] == 1 and p['subtype'] == 0x00), None)
    apps = sorted([p for p in parts if p['type'] == 0 and 0x10 <= p['subtype'] < 0x20], key=lambda p: p['subtype'])
    best = None
    if ota:
        for s in (0, 1):
            rec = img[ota['offset'] + s * 0x1000: ota['offset'] + s * 0x1000 + 32]
            seq, crc = struct.unpack('<I', rec[:4])[0], struct.unpack('<I', rec[28:32])[0]
            if seq not in (0, 0xFFFFFFFF) and zlib.crc32(rec[:4], 0xFFFFFFFF) == crc:   # esp_rom_crc32_le(UINT32_MAX, &seq, 4)
                best = max(best or 0, seq)
    if best and apps:
        return apps[(best - 1) % len(apps)]['name'], best
    factory = next((p for p in parts if p['type'] == 0 and p['subtype'] == 0x00), None)
    return (factory or (apps[0] if apps else {'name': None}))['name'], best


def nvs_entries(img, off, size):
    """Decoded NVS entries -> {(namespace, key, type, chunk): sha256(entry+span data)}."""
    ns_names, raw = {0: ''}, []
    for page in range(off, off + size, 0x1000):
        state = struct.unpack('<I', img[page:page + 4])[0]
        if state in (0xFFFFFFFF,):
            continue
        k = 0
        while k < 126:
            bm = (img[page + 32 + k // 4] >> ((k % 4) * 2)) & 3
            e = img[page + 64 + 32 * k: page + 64 + 32 * (k + 1)]
            if bm != 2:
                k += 1
                continue
            ns, typ, span, chunk = e[0], e[1], max(e[2], 1), e[3]
            key = e[8:24].split(b'\0')[0].decode('latin-1')
            data = img[page + 64 + 32 * k: page + 64 + 32 * (k + span)]
            if ns == 0 and typ == 0x01:
                ns_names[e[24]] = key
            raw.append((ns, key, typ, chunk, sha(data)))
            k += span
    out = {}
    for ns, key, typ, chunk, h in raw:
        out[(ns_names.get(ns, f'#{ns}'), key, TYPES.get(typ, hex(typ)), chunk)] = h
    return out


def regions(parts):
    regs = [dict(name='bootloader', offset=BOOTLOADER[0], size=BOOTLOADER[1], cls='IMMUTABLE_CRITICAL'),
            dict(name='partition_table', offset=PTABLE[0], size=PTABLE[1], cls='IMMUTABLE_CRITICAL')]
    for p in parts:
        if p['type'] == 1 and p['subtype'] == 0x02:
            c = 'MUTABLE_PERSISTENT'
        elif p['type'] == 1 and p['subtype'] == 0x03:
            c = 'DIAGNOSTIC_CONDITIONAL'
        else:
            c = 'IMMUTABLE_CRITICAL'          # app (active/secondary), otadata, filesystem
        regs.append(dict(name=p['name'], offset=p['offset'], size=p['size'], cls=c))
    regs.sort(key=lambda r: r['offset'])
    full, pos = [], 0
    for r in regs:
        if r['offset'] > pos:
            full.append(dict(name=f'unpartitioned_{pos:#x}', offset=pos, size=r['offset'] - pos, cls='UNPARTITIONED'))
        full.append(r)
        pos = r['offset'] + r['size']
    if pos < FLASH_SIZE:
        full.append(dict(name=f'unpartitioned_{pos:#x}', offset=pos, size=FLASH_SIZE - pos, cls='UNPARTITIONED'))
    return full


def compare(ref_path, cur_path):
    res = compare_images(Path(ref_path).read_bytes(), Path(cur_path).read_bytes())
    res.update(reference_dump=Path(ref_path).name, current_dump=Path(cur_path).name)
    return res


def compare_images(a, b, nvs_allowed=NVS_ALLOWED):
    if len(a) != FLASH_SIZE or len(b) != FLASH_SIZE:
        raise SystemExit('DUMP_SIZE_NOT_16MB')
    parts, md5 = parse_partitions(b)
    parts_ref, _ = parse_partitions(a)
    app, seq = active_app(b, parts)
    rows, verdict = [], 'PASS'
    for r in regions(parts):
        s, e = r['offset'], r['offset'] + r['size']
        ra, rb = a[s:e], b[s:e]
        changed = 0 if ra == rb else sum(x != y for x, y in zip(ra, rb))
        row = dict(name=r['name'], offset=hex(s), size=hex(r['size']), sha256_original=sha(ra), sha256_current=sha(rb),
                   equal=ra == rb, changed_bytes=changed, classification=r['cls'])
        if r['name'] == app:
            row['role'] = 'ACTIVE_APP'
        if changed:
            if r['cls'] == 'MUTABLE_PERSISTENT':
                ea, eb = nvs_entries(a, s, r['size']), nvs_entries(b, s, r['size'])
                diff = sorted({k[:2] for k in set(ea) ^ set(eb)} | {k[:2] for k in set(ea) & set(eb) if ea[k] != eb[k]})
                row['changed_nvs_keys'] = [dict(namespace=n, key=k) for n, k in diff]
                unexplained = [d for d in diff if d not in nvs_allowed]
                row['nvs_verdict'] = 'ALLOWED_EXPLAINED' if diff and not unexplained else 'BLOCK_UNEXPLAINED_NVS_CHANGE'
                row['unexplained'] = [dict(namespace=n, key=k) for n, k in unexplained]
                if row['nvs_verdict'] != 'ALLOWED_EXPLAINED':
                    verdict = 'BLOCK'
            elif r['cls'] == 'DIAGNOSTIC_CONDITIONAL':
                verdict = 'BLOCK' if verdict == 'BLOCK' else 'REVIEW'
            else:
                verdict = 'BLOCK'
        rows.append(row)
    return dict(policy='FLASH_INTEGRITY_POLICY.md', reference_sha256=sha(a), current_sha256=sha(b), partition_table_md5=md5,
                partition_table_equal=parts == parts_ref,
                partitions=[dict(p, offset=hex(p['offset']), size=hex(p['size'])) for p in parts],
                active_app=app, otadata_seq=seq, regions=rows, verdict=verdict)


if __name__ == '__main__':
    res = compare(sys.argv[1], sys.argv[2])
    txt = json.dumps(res, indent=1) + '\n'
    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(txt, encoding='utf-8')
    print(res['verdict'], [(r['name'], r['changed_bytes']) for r in res['regions'] if r['changed_bytes']])
