# -*- coding: utf-8 -*-
"""SCROLL performance benchmark (host): OLD reader scroll vs BIDIRECTIONAL_SCROLL_PERFORMANCE_FIX, on a Codigo-Civil-like fixture.

Physical evidence of the OLD stall (backups/indexed_bench/bench_serial.bin, not versioned): ARTICLE_SEARCH art. 2000 on a legacy
large norm -> landing in 102 ms; the FIRST scroll UP above the landing logged
  PERF CONTEXTO_UP: 11293148 us (checkpoint=sim, bytes=647150)     PERF SCROLL: ... max=11380644 us
i.e. reconstruirContextoAntesOffset re-read 647.150 B byte by byte from the checkpoint left near offset 0 when the file was opened.

Model: tools/scroll_model.py (exact bytes / seeks / opens / lines for each firmware path; times = ESTIMATES from device rates).
Fixture: >= 2.500 articles, several MB, caput/paragraphs/incisos/alineas, headings, long paragraphs (single physical lines of
3-6 KiB) and a few very long articles, UTF-8 accents (exercises the TFT width wrap).
Usage: python scroll_performance_benchmark.py [--out ../SCROLL_PERFORMANCE_BENCHMARK.json] [--quick]
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reader_viewport as V  # noqa: E402
import scroll_model as M  # noqa: E402

WORDS = ('contrato obrigação pessoa jurídica direito herança cônjuge sucessão posse propriedade usufruto servidão '
         'condomínio sociedade empresário título crédito prescrição decadência negócio nulidade anulação boa-fé '
         'responsabilidade dano indenização garantia fiança penhor hipoteca alienação fiduciária locação comodato '
         'mútuo depósito mandato comissão corretagem transporte seguro constituição renda jogo aposta tutela curatela '
         'ausência domicílio bens públicos particulares fungíveis consumíveis divisíveis acessórios benfeitorias '
         'útil necessária voluptuária ação execução cláusula penal arras juros correção monetária').split()
ROMAN = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII')


def _sentence(rng, lo, hi):
    out, n = [], rng.randint(lo, hi)
    while sum(len(w) + 1 for w in out) < n:
        out.append(rng.choice(WORDS))
    s = ' '.join(out)
    return s[0].upper() + s[1:] + '.'


def art_label(k, thousands=True):
    """Article number as printed in the norm: 'Art. 2.000.' (Codigo Civil / CPC / CLT style) or plain 'Art. 2000.'."""
    return f'{k:,}'.replace(',', '.') if thousands else str(k)


def civil_like_norm(n=2500, seed=7, thousands=True):
    """Deterministic legacy norm like the Codigo Civil TXT on the SD ('Art. 1.000.' thousands separator by default)."""
    return civil_like_norm_with_map(n, seed, thousands)[0]


def civil_like_norm_with_map(n=2500, seed=7, thousands=True):
    """-> (bytes, structural map [(offset, 'F1:ART.k')]) built by the GENERATOR (independent of any parser)."""
    rng = random.Random(seed)
    L = ['CÓDIGO SINTÉTICO DE TESTE — DOCUMENTO GRANDE', '']
    art_lines = {}
    for k in range(1, n + 1):
        if k % 500 == 1:
            L.append(f'LIVRO {k // 500 + 1}')
        if k % 100 == 1:
            L.append(f'TÍTULO {k // 100 + 1} — DISPOSIÇÕES GERAIS')
        if k % 25 == 1:
            L.append(f'CAPÍTULO {k // 25 + 1}')
        art_lines[len(L)] = k
        L.append(f'Art. {art_label(k, thousands)}. ' + _sentence(rng, 220, 760))
        if k % 97 == 0:                                       # long paragraph: one physical line of 3-6 KiB
            L.append(_sentence(rng, 3000, 6000))
        if k % 400 == 0:                                      # very long article (~20 KiB of incisos)
            for i in range(60):
                L.append(f'{ROMAN[i % 12]} - ' + _sentence(rng, 200, 400) + ';')
        r = rng.random()
        if r < 0.55:
            for j in range(1, rng.randint(2, 5)):
                L.append(f'§ {j}º ' + _sentence(rng, 120, 520))
        elif r < 0.75:
            L.append('Parágrafo único. ' + _sentence(rng, 120, 480))
        if rng.random() < 0.3:
            for i in range(rng.randint(2, 7)):
                L.append(f'{ROMAN[i]} - ' + _sentence(rng, 60, 260) + ';')
                if rng.random() < 0.2:
                    for a in 'abc':
                        L.append(f'{a}) ' + _sentence(rng, 40, 160) + ';')
    data = ('\n'.join(L) + '\n').encode('utf-8')
    smap, off = [], 0
    for i, line in enumerate(L):
        if i in art_lines:
            smap.append((off, f'F1:ART.{art_lines[i]}'))
        off += len(line.encode('utf-8')) + 1
    return data, smap


def _steps(r, d, n):
    return [r.scroll(d) for _ in range(n)]


def _ms(us):
    return round(us / 1000.0, 2)


def landing_case(data, art, mode, landing='top', pre_down=4, kind='legacy', text_map=None, cf=False):
    """Arthur's sequence: open the norm (offset 0), search -> landing, a few DOWN steps, then the first UP above the landing."""
    r = M.Reader(data, mode, kind=kind, text_map=text_map, cf_compat=cf)
    r.open_file()
    pos = M.article_offset(data, art)
    t0 = time.perf_counter()
    lnd = r.land_top(pos) if landing == 'top' else r.land_centered(pos)
    for _ in range(pre_down):
        r.scroll(1)
    for _ in range(pre_down):
        r.scroll(-1)
    first = r.scroll(-1)
    host_s = time.perf_counter() - t0
    return r, dict(art=art, offset=pos, landing=lnd, first_up=first, host_s=round(host_s, 3))


def run(quick=False, n=2500):
    data = civil_like_norm(n)
    out = dict(fixture=dict(articles=n, bytes=len(data), lines=data.count(b'\n'),
                            longest_physical_line=max(len(x) for x in data.split(b'\n'))),
               constants=M.C, rates=M.RATES, cases=[], sequences={}, sizing=[])
    arts = (10, 500, 1000, 2000, 2400)
    for art in arts:
        row = dict(art=art)
        for mode in ('old', 'new'):
            if mode == 'old' and quick and art > 1000:
                continue
            r, res = landing_case(data, art, mode)
            f = res['first_up']
            row[mode] = dict(offset=res['offset'], io=f['io'], perbyte=f['perbyte'], seeks=f['seeks'], opens=f['opens'],
                             ctx_lines=f['ctx_lines'], origin=f['origin'], reread=f['reread'], proc_ms=_ms(f['us']),
                             total_ms=round(_ms(f['us']) + M.RATES['render_ms'], 1), landing_ms=_ms(res['landing']['us']),
                             landing_io=res['landing']['io'], contexts=r.contexts(), viewport=r.viewport())
        if 'old' in row:
            row['same_viewport'] = row['old']['viewport'] == row['new']['viewport']
            row['same_contexts'] = row['old']['contexts'] == row['new']['contexts']
        for m in ('old', 'new'):
            if m in row:
                row[m].pop('contexts')
                row[m].pop('viewport')
        out['cases'].append(row)

    # sequences on the NEW reader after landing at art. 2000 (cold first UP already measured above)
    def seq(name, pattern, art=2000, landing='top'):
        r = M.Reader(data, 'new')
        r.open_file()
        (r.land_top if landing == 'top' else r.land_centered)(M.article_offset(data, art))
        recs = [r.scroll(d) for d in pattern]
        recs = [x for x in recs if x and x.get('moved')]
        us = [x['us'] for x in recs]
        out['sequences'][name] = dict(steps=len(recs), max_proc_ms=_ms(max(us)), mean_proc_ms=_ms(sum(us) / len(us)),
                                      max_io=max(x['io'] for x in recs), total_io=sum(x['io'] for x in recs),
                                      refills_prev=sum(1 for x in recs if x['prev_refill']),
                                      refills_next=sum(1 for x in recs if x['next_refill']),
                                      origins=sorted({x['origin'] for x in recs}))
        return r, recs

    seq('10_up', [-1] * 10)
    seq('10_down', [1] * 10)
    seq('alternating', [-1, 1] * 10)
    seq('warm_up_after_10', [-1] * 10 + [-1])
    seq('120_up', [-1] * 120)
    seq('120_down', [1] * 120)
    seq('pageup_x10', [-6] * 10)
    seq('centered_10_up', [-1] * 10, landing='centered')
    seq('20_rapid_up_coalesced', [-2] * 10)
    seq('20_rapid_down_coalesced', [2] * 10)

    # backlog model: wheel events every `gap_ms`; each loop iteration consumes the accumulated delta (clamped +-12) once
    def backlog(mode, direction, events=20, gap_ms=40.0, art=2000):
        r = M.Reader(data, mode)
        r.open_file()
        r.land_top(M.article_offset(data, art))
        t, pend, done, redraws, maxpend, lost, worst = 0.0, 0, 0, 0, 0, 0, 0.0
        arrivals = [i * gap_ms for i in range(events)]
        i = 0
        while i < len(arrivals) or pend:
            while i < len(arrivals) and arrivals[i] <= t:
                pend += 1
                i += 1
            if not pend:
                t = arrivals[i]
                continue
            maxpend = max(maxpend, pend)
            d = direction * pend
            lost += max(0, pend - 12)
            rec = r.scroll(d)
            pend = 0
            step = (_ms(rec['us']) + M.RATES['render_ms']) if rec and rec.get('moved') else 1.0
            worst = max(worst, step)
            done += abs(rec['moved']) if rec else 0
            redraws += 1
            t += step
        return dict(events=events, gap_ms=gap_ms, redraws=redraws, max_pending=maxpend, lines_moved=done, lost_by_clamp=lost,
                    drain_ms=round(t - arrivals[-1], 1), worst_step_ms=round(worst, 1))

    out['backlog'] = {f'{m}_{"UP" if d < 0 else "DOWN"}': backlog(m, d) for m in (('new',) if quick else ('old', 'new'))
                      for d in (-1, 1)}

    # sizing of the PREVIOUS block (lines per refill): cost per refill vs refills per 240 lines up
    for alvo in (16, 32, 48, 64, 96, 128):
        saved = M.C['prev_alvo']
        M.C['prev_alvo'] = alvo
        try:
            r = M.Reader(data, 'new')
            r.open_file()
            r.land_top(M.article_offset(data, 2000))
            recs = [x for x in (r.scroll(-1) for _ in range(240)) if x and x.get('moved')]
            ref = [x for x in recs if x['prev_refill']]
            out['sizing'].append(dict(prev_alvo=alvo, refills=len(ref), max_step_ms=_ms(max(x['us'] for x in recs)),
                                      max_refill_io=max((x['io'] for x in ref), default=0),
                                      mean_step_ms=_ms(sum(x['us'] for x in recs) / len(recs)), ram_bytes=alvo * 4 * 2))
        finally:
            M.C['prev_alvo'] = saved
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    res = run(a.quick)
    txt = json.dumps(res, ensure_ascii=False, indent=1, default=list)
    if a.out:
        Path(a.out).write_text(txt, encoding='utf-8')
    print(txt)


if __name__ == '__main__':
    main()
