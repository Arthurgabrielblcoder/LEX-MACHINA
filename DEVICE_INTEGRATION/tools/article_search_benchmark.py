"""ARTICLE_SEARCH performance benchmark (host): old linear search vs ARTICLE_SEARCH.IDX, CF runtime + synthetic 2.500-article norm.

OLD (physical, measured): Arthur's DEVICE session serial (backups/search_ux_flash/session_serial.bin, not versioned):
  PERF BUSCA_ARTIGO = text scan (pesquisarArtigo) ; PERF CONTEXTO_UP = reconstruirContextoAntesOffset after the centered landing.
OLD (model, when not measured): scan = offset x 1.135 us/B, context = min(top, 256 KiB) x 17.2 us/B (rates fitted on the same log).
NEW: lookup measured on the host with the firmware algorithm (lower_bound + contiguous occurrences; comparisons counted), no text scan.
     landing/render are ESTIMATES from physical rates until the [ARTSEARCH] serial line is captured on the device:
       landing = bytes of the visual lines above the occurrence x 17.2 us/B (indexarAntesDaJanela)
       render  = [TEXT_MAP lookup for the context seed (50 ms), only when > 2 KiB would be re-read] + re-read x 17.2 us/B + 139 ms
                 (PERF SCROLL mean: 12-line cache, ACTIVE_TARGET sync, full TFT redraw)
Usage: python article_search_benchmark.py [--out ../ARTICLE_SEARCH_PERFORMANCE_BENCHMARK.md]
"""
import argparse
import json
import math
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
sys.path.insert(0, str(HERE))
import build_article_search_index as AI  # noqa: E402
import reader_viewport as V  # noqa: E402

SESSION = DI / 'backups/search_ux_flash/session_serial.bin'
SCAN_US_PER_B, CTX_US_PER_B, TEXTMAP_MS, REDRAW_MS = 1.135, 17.2, 50.0, 139.0
ARTICLES = (1, 5, 15, 37, 100, 150, 193, 230, 250)


def physical_old():
    """offset -> (scan_ms, context_ms) from the device serial of the previous candidate (centered landing, linear search)."""
    if not SESSION.is_file():
        return {}
    t = SESSION.read_bytes().decode('utf-8', 'replace').splitlines()
    out = {}
    for i, l in enumerate(t):
        m = re.search(r'PERF BUSCA_ARTIGO: (\d+) ms \(offset=(\d+)', l)
        if not m:
            continue
        for k in t[i + 1:i + 6]:
            c = re.search(r'PERF CONTEXTO_UP: (\d+) us \(checkpoint=\w+, bytes=(\d+)\)', k)
            if c:
                out.setdefault(int(m.group(2)), (int(m.group(1)), int(c.group(1)) / 1000.0))
                break
    return out


def time_lookup(idx, num, start=0, reps=20000):
    idx.comparisons = 0
    hit = idx.find(num, 0, start)
    cmp = idx.comparisons
    t0 = time.perf_counter()
    for _ in range(reps):
        idx.find(num, 0, start)
    return hit, cmp, (time.perf_counter() - t0) / reps * 1e6


def cf_rows():
    r = V.Reader(artidx=V.ARTIDX)
    phys = physical_old()
    rows = []
    for a in ARTICLES:
        hit, cmp, us = time_lookup(r.index, a)
        off = hit[0]
        top = r.land_top(off)
        above = off - top
        old_scan, old_ctx = phys.get(off, (None, None))
        src = 'FISICO'
        if old_scan is None:
            old_scan, old_ctx, src = off * SCAN_US_PER_B / 1000, min(top, 262144) * CTX_US_PER_B / 1000, 'MODELO'
        landing = above * CTX_US_PER_B / 1000
        reread, seeded = r.context_reread(top)
        render = (TEXTMAP_MS if seeded else 0) + reread * CTX_US_PER_B / 1000 + REDRAW_MS
        total = us / 1000 + landing + render
        old_total = old_scan + old_ctx + REDRAW_MS
        rows.append(dict(article=a, target=r.map_row_at(off), offset=off, cmp=cmp, new_lookup_us=round(us, 2), old_lookup_ms=round(old_scan, 1),
                         old_context_ms=round(old_ctx, 1), old_source=src, reread_bytes=reread, seeded=seeded, landing_ms=round(landing, 1),
                         render_ms=round(render, 1), total_ms=round(total, 1), old_total_ms=round(old_total, 1),
                         speedup=round(old_total / total, 1)))
    return r, rows


def synthetic_norm(n=2500, second_ns=200, remission_every=50):
    """Synthetic text + structural target index: n articles (namespace F1), a second namespace re-using numbers 1..second_ns (F2),
    paragraphs, and line-start remissions 'art. k da Lei ...' that are NOT targets (must never be indexed)."""
    lines, targets = ['NORMA SINTETICA DE TESTE'], []

    def art(ns, k):
        lines.append(f'Art. {k}. Texto sintético do artigo {k} da {ns}, com redação neutra para medir o índice.')
        targets.append(dict(target_id=f'{ns}:ART.{k}', kind='ARTIGO', line_start=len(lines)))
        lines.append(f'§ 1º Parágrafo sintético do artigo {k}.')
        lines.append('I - inciso sintético;')
        if k % remission_every == 0:
            lines.append(f'art. {k + 1} da Lei nº 1.000, de 2000, citado como remissão.')
    for k in range(1, n + 1):
        art('F1', k)
    lines.append('DISPOSICOES TRANSITORIAS')
    for k in range(1, second_ns + 1):
        art('F2', k)
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    import hashlib
    idx = dict(source=dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()), targets=targets, target_index_sha256='synthetic')
    return data, idx


def fixture_rows(n=2500):
    data, idx = synthetic_norm(n)
    with tempfile.TemporaryDirectory() as t:
        (Path(t) / 'T.txt').write_bytes(data)
        (Path(t) / 'I.json').write_text(json.dumps(idx), encoding='utf-8')
        blob, man = AI.build(Path(t) / 'T.txt', Path(t) / 'I.json')
    ai = AI.ArticleIndex(blob, data)
    rows = []
    for k in (10, 100, 1000, 2400, 2500):
        hit, cmp, us = time_lookup(ai, k)
        rx = re.compile(rb'(?m)^[ \t]*[Aa][Rr][Tt]\.?[ \t]*' + str(k).encode() + rb'(?![0-9]|\.[0-9])')
        t0 = time.perf_counter()
        m = rx.search(data)
        lin_us = (time.perf_counter() - t0) * 1e6
        rows.append(dict(article=k, offset=hit[0], cmp=cmp, lookup_us=round(us, 2), linear_scan_bytes=m.start(), linear_host_us=round(lin_us, 1),
                         linear_device_ms_est=round(m.start() * SCAN_US_PER_B / 1000, 1)))
    second, cmp2, _ = time_lookup(ai, 10, hit_start(ai, 10))
    return dict(records=man['records'], bytes=man['bytes'], text_bytes=len(data), rows=rows, log2=math.ceil(math.log2(man['records'])),
                second_occurrence_10=dict(namespace=second[1], occurrence=second[2], cmp=cmp2),
                max_cmp=max(r['cmp'] for r in rows))


def hit_start(ai, k):
    return ai.find(k)[0] + 1


def render(out):
    r, rows = cf_rows()
    fx = fixture_rows()
    cc = 96 + 16 * 2 + 2100 * AI.RECORD
    M = ['# ARTICLE_SEARCH — benchmark de desempenho (busca indexada × busca linear)', '',
         'Gerado por `tools/article_search_benchmark.py`. **OLD** físico = log serial da sessão de Arthur com o candidato anterior (busca linear '
         '+ pouso centralizado); **OLD** modelo = taxas ajustadas nesse mesmo log (scan 1,135 µs/B; reconstrução de contexto 17,2 µs/B, '
         'sem checkpoint, janela ≤ 256 KiB). **NEW_LOOKUP** = medido no host com o algoritmo do firmware. **LANDING/RENDER/TOTAL NEW** são '
         '**estimativas** pelas taxas físicas até a medição no aparelho (linha serial `[ARTSEARCH] … total_ms=`).', '',
         f"Índice CF: **{len(r.index.recs)} registros**, **{len(V.ARTIDX.read_bytes())} B** (header 96 + 2 namespaces × 16 + "
         f"{len(r.index.recs)} × 12), ⌈log2 n⌉ = {math.ceil(math.log2(len(r.index.recs)))}.", '',
         '| ARTICLE | TARGET | BYTE_OFFSET | OLD_LOOKUP_MS | OLD_CONTEXT_MS | OLD fonte | NEW_LOOKUP (host) | CMP | LANDING_MS (est.) | '
         'RELIDOS p/ contexto | RENDER_MS (est.) | TOTAL_MS (est.) | OLD_TOTAL_MS | SPEEDUP |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in rows:
        M.append(f"| {x['article']} | `{x['target']}` | {x['offset']} | {x['old_lookup_ms']} | {x['old_context_ms']} | {x['old_source']} | "
                 f"{x['new_lookup_us']} µs | {x['cmp']} | {x['landing_ms']} | {x['reread_bytes']} B{' (semente TEXT_MAP)' if x['seeded'] else ''} | {x['render_ms']} | {x['total_ms']} | "
                 f"{x['old_total_ms']} | {x['speedup']}× |")
    lk = [x['cmp'] for x in rows]
    M += ['', f"- Comparações do lookup: {min(lk)}–{max(lk)} (art. 1 a art. 250): **independe do offset**. Art. 230 (offset "
              f"{next(x['offset'] for x in rows if x['article'] == 230)}): {next(x['cmp'] for x in rows if x['article'] == 230)} comparações.",
          '- Releitura para o contexto após o pouso: só do registro do TEXT_MAP anterior ao topo (dezenas a poucos milhares de bytes), em vez de '
          'centenas de KB desde um checkpoint distante.', '',
          f"## Fixture sintética: {fx['records']} registros ({fx['text_bytes']} B de texto, 2.500 artigos + 200 da 2ª estrutura, remissões "
          f"'art. k da Lei…' em início de linha que **não** entram)", '',
          f"Índice: **{fx['bytes']} B**; ⌈log2 n⌉ = {fx['log2']}.", '',
          '| ARTICLE | BYTE_OFFSET | CMP (índice) | LOOKUP (host) | SCAN LINEAR (bytes) | SCAN LINEAR (host) | SCAN LINEAR no aparelho (est.) |',
          '|---|---|---|---|---|---|---|']
    M += [f"| {x['article']} | {x['offset']} | {x['cmp']} | {x['lookup_us']} µs | {x['linear_scan_bytes']} | {x['linear_host_us']} µs | "
          f"{x['linear_device_ms_est']} ms |" for x in fx['rows']]
    M += ['', f"- Art. 10 e art. 2.400: {fx['rows'][0]['cmp']} e {fx['rows'][3]['cmp']} comparações (máximo {fx['max_cmp']}), mesma ordem de "
              f"grandeza; o scan linear cresce de {fx['rows'][0]['linear_scan_bytes']} B para {fx['rows'][3]['linear_scan_bytes']} B.",
          f"- 2ª ocorrência do art. 10 (outra estrutura): namespace `{fx['second_occurrence_10']['namespace']}`, ocorrência "
          f"{fx['second_occurrence_10']['occurrence']}, {fx['second_occurrence_10']['cmp']} comparações.", '',
          '## Projeção', '',
          f"- Código Civil (~2.046 artigos; ~2.100 registros com sufixos): ≈ **{cc} B** (~{cc // 1024} KiB) em PSRAM; ⌈log2 2100⌉ = 12 comparações.",
          '- 72 normas: um índice por texto indexado (carregado só o da norma aberta); 12 B/ocorrência.']
    Path(out).write_bytes(('\n'.join(M) + '\n').encode('utf-8'))
    return rows, fx


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(DI / 'ARTICLE_SEARCH_PERFORMANCE_BENCHMARK.md'))
    rows, fx = render(ap.parse_args().out)
    print(json.dumps(dict(cf=[{k: x[k] for k in ('article', 'offset', 'cmp', 'new_lookup_us', 'old_total_ms', 'total_ms', 'speedup', 'old_source')} for x in rows],
                          fixture={k: fx[k] for k in ('records', 'bytes', 'max_cmp')}, fixture_rows=fx['rows']), ensure_ascii=False, indent=1))
