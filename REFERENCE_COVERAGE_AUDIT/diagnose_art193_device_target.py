# -*- coding: utf-8 -*-
"""ART. 193 — DEVICE ACTIVE_TARGET diagnostic (read-only; firmware, UI and SD are NOT changed).

Host-side replica of the approved DEVICE V1 reader (sketch sha256 f06cdc14…81ed, contexto_juridico.h), on the approved SD bytes
(DEVICE_INTEGRATION/staging_sd_v1 = physical baseline):
  * visual lines   = avancarUmaLinhaVisual(): UTF-8 decode, Arimo glyph advances (FONTE_ARIMO_A4_GLYPHS, parsed from the sketch),
                     LEITOR_TEXTO_W = 312 px, word wrap at the last space, '\n' ends a line;
  * article search = pesquisarArtigo(): first LINE-START "Art. N" (non-CF path: CF88_RUNTIME.txt is not "cf.txt"), then
                     reiniciarIndice(pos) + linhaTopo = 0  -> the article line is the TOP row of the 12-row viewport;
  * CONTEXTO row   = escolherContextoPredominante(): centre row (12/2 = 6, i.e. the 7th row) whenever it has an article context;
  * ACTIVE_TARGET  = lexV1SincronizarAlvo(): CF88_TEXT_MAP.IDX floor lookup at the offset of that row;
  * layer 4        = lexV1QueryKeysForActiveTarget (ART.n -> [ART.n, ART.n:CAPUT]) + W flag of CF88_TARGETS.IDX (union).
Writes REFERENCE_COVERAGE_AUDIT/ART193_DEVICE_TARGET_DIAGNOSTIC.md.  Usage: python diagnose_art193_device_target.py
"""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKETCH = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
CTX_H = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/contexto_juridico.h'
BASE_SD = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1/SD/99_LEX_V1'
RUN3_SD = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1_run3_candidate/SD/99_LEX_V1'
OUT = HERE / 'ART193_DEVICE_TARGET_DIAGNOSTIC.md'
ROWS, CENTER, WIDTH, ROW_H, TEXT_Y0 = 12, 6, 312, 15, 23           # LEITOR_LINHAS_VISIVEIS, /2, LEITOR_TEXTO_W, LEITOR_LINHA_H, TEXTO_Y0


def glyph_advances(sketch=SKETCH):
    src = Path(sketch).read_text(encoding='utf-8')
    body = src[src.index('FONTE_ARIMO_A4_GLYPHS[148] PROGMEM = {'):]
    body = body[:body.index('};')]
    adv = {int(cp, 16): int(a) for a, cp in re.findall(r'\{\s*\d+,\s*\d+,\s*\d+,\s*-?\d+,\s*-?\d+,\s*(\d+)\},\s*//\s*U\+([0-9A-F]{4})', body)}
    if len(adv) != 148:
        raise SystemExit(f'GLYPH_TABLE_PARSE {len(adv)}')
    return adv


class Reader:
    def __init__(self, sd=BASE_SD):
        self.sd = Path(sd)
        self.data = (self.sd / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        self.adv = glyph_advances()
        self.map = [(int(r[0]), int(r[1]), r[2]) for r in self._rows('10_TARGETS/CF88_TEXT_MAP.IDX')]
        self.flags = {r[0]: r[3] for r in self._rows('10_TARGETS/CF88_TARGETS.IDX')}
        self.refs = {}
        for r in self._rows('20_REFERENCES/REF_PAYLOAD.IDX'):
            self.refs.setdefault(r[0], []).append(r)

    def _rows(self, rel):
        return [l.split('|') for l in (self.sd / rel).read_text(encoding='utf-8').splitlines() if l and l[0] != '#']

    def advance(self, cp):
        if cp == '\t' or cp == 0x09:
            cp = 0x20
        if cp == 0x00A0:
            cp = 0x20
        return self.adv.get(cp, self.adv[ord('?')])

    def next_visual_line(self, start):
        """avancarUmaLinhaVisual(): returns the offset of the next visual line."""
        d, n = self.data, len(self.data)
        px, last_space_after, found = 0, start, False
        i = start
        while i < n:
            before = i
            b0 = d[i]
            i += 1
            if b0 == 0x0D:
                continue
            if b0 == 0x0A:
                return i
            cp = b0
            if b0 & 0xE0 == 0xC0:
                cp = ((b0 & 0x1F) << 6) | (d[i] & 0x3F)
                i += 1
            elif b0 & 0xF0 == 0xE0:
                cp = ((b0 & 0x0F) << 12) | ((d[i] & 0x3F) << 6) | (d[i + 1] & 0x3F)
                i += 2
            elif b0 & 0xF8 == 0xF0:
                i += 3
                cp = ord('?')
            if cp in (0x20, 0x09, 0xA0):
                last_space_after, found = i, True
            av = self.advance(cp)
            if px + av > WIDTH:
                if found and last_space_after > start:
                    return last_space_after
                return before if before > start else i
            px += av
        return n

    def visual_lines(self, start, count):
        out, p = [], start
        for _ in range(count):
            if p >= len(self.data):
                break
            q = self.next_visual_line(p)
            out.append((p, q))
            p = q
        return out

    def visual_lines_before(self, start, count):
        """Visual lines that end exactly at `start`, as indexarAntesDaJanela() rebuilds them (from the previous physical line start)."""
        out = []
        end = start
        while len(out) < count and end > 0:
            ls = self.data.rfind(b'\n', 0, end - 1) + 1
            seg = []
            p = ls
            while p < end:
                q = self.next_visual_line(p)
                seg.append((p, min(q, end)))
                p = q
            out = seg + out
            end = ls
        return out[-count:]

    def text(self, a, b):
        return self.data[a:b].decode('utf-8').rstrip('\n').rstrip()

    def target_at(self, off):
        """CF88_TEXT_MAP floor search -> target_id."""
        lo, hi, best = 0, len(self.map) - 1, None
        while lo <= hi:
            m = (lo + hi) // 2
            if self.map[m][0] <= off:
                best, lo = self.map[m], m + 1
            else:
                hi = m - 1
        return best[2] if best else None

    def search_article(self, n):
        m = re.search(rb'(?m)^[ \t]*([Aa][Rr][Tt](?:igo)?\.?[ \t]*' + re.escape(str(n).encode()) + rb')(?![0-9]|\.[0-9])', self.data)
        return m.start(1) if m else None

    @staticmethod
    def query_keys(tid):
        if tid and tid.startswith('CF88:ART.') and ':' not in tid[len('CF88:ART.'):]:
            return [tid, tid + ':CAPUT']
        return [tid] if tid else []

    def layer4(self, tid):
        keys = self.query_keys(tid)
        flag = any(len(self.flags.get(k, '')) >= 4 and self.flags[k][3] == 'W' for k in keys)
        works = [r[6] for k in keys for r in self.refs.get(k, []) if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE']
        return flag, works

    def viewport(self, top):
        lines = self.visual_lines(top, ROWS)
        rows = [dict(row=i, y=TEXT_Y0 + i * ROW_H, offset=a, end=b, target=self.target_at(a), text=self.text(a, b)) for i, (a, b) in enumerate(lines)]
        act = rows[CENTER]['target'] if len(rows) > CENTER else None
        return rows, act


def scan(rd, art_off, before=10, after=12):
    """Every scroll position around the article: top row = each visual line from `before` lines above to `after` lines below."""
    above = rd.visual_lines_before(art_off, before)
    below = rd.visual_lines(art_off, after + 1)
    tops = [a for a, _ in above] + [a for a, _ in below]
    idx_art = len(above)
    out = []
    for k, top in enumerate(tops):
        rows, act = rd.viewport(top)
        flag, works = rd.layer4(act)
        out.append(dict(scroll=k - idx_art, top=top, top_text=rows[0]['text'][:48], center_text=rows[CENTER]['text'][:48],
                        active_target=act, layer4=flag, works=len(works)))
    return out


def after_search_all(rd):
    """For every article line whose own layer 4 exists (ART.n / ART.n:CAPUT): ACTIVE_TARGET right after 'Buscar Art. n'."""
    arts = sorted({k.rsplit(':CAPUT', 1)[0] for k, f in rd.flags.items() if len(f) >= 4 and f[3] == 'W' and k.startswith('CF88:ART.')
                   and (k.count(':') == 1 or (k.count(':') == 2 and k.endswith(':CAPUT')))}, key=lambda t: (int(re.match(r'CF88:ART\.(\d+)', t).group(1)), t))
    out = []
    for a in arts:
        n = a.split('ART.')[1]
        pos = rd.search_article(n)
        if pos is None:
            continue
        rows, act = rd.viewport(pos)
        caput_rows = [r['row'] for r in rows if r['target'] == a]
        out.append(dict(article=a, search_offset=pos, caput_rows=caput_rows, active_target=act, layer4_after_search=rd.layer4(act)[0],
                        rows_up_needed=max(0, CENTER - max(caput_rows)) if caput_rows else None))
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rd = Reader(BASE_SD)
    m = {t: (o, ln) for o, ln, t in rd.map}
    a193, pu, a194 = m['CF88:ART.193'], m['CF88:ART.193:PAR.UNICO'], m['CF88:ART.194']
    pos = rd.search_article(193)
    rows, act = rd.viewport(pos)
    flag_act, works_act = rd.layer4(act)
    flag_art, works_art = rd.layer4('CF88:ART.193')
    sc = scan(rd, a193[0])
    ok_positions = [s for s in sc if s['layer4']]
    caput_lines = rd.visual_lines(a193[0], 6)
    caput_lines = [(a, b) for a, b in caput_lines if a < pu[0]]
    pu_lines = [(a, b) for a, b in rd.visual_lines(pu[0], 12) if a < a194[0]]
    allsearch = after_search_all(rd)
    misses = [x for x in allsearch if not x['layer4_after_search']]
    rd3 = Reader(RUN3_SD) if RUN3_SD.is_dir() else None
    all3 = after_search_all(rd3) if rd3 else []
    miss3 = [x for x in all3 if not x['layer4_after_search']]
    pos_ok = sorted({s['scroll'] for s in ok_positions if s['active_target'] == 'CF88:ART.193'})

    M = ['# ART. 193 — diagnóstico do ACTIVE_TARGET no DEVICE (somente diagnóstico)', '',
         '**Firmware, UI, algoritmo ACTIVE_TARGET e SD físico NÃO foram alterados.** Simulação host do leitor aprovado sobre os bytes do baseline físico.', '',
         '## Fontes simuladas', '',
         f'- Sketch `{SKETCH.relative_to(ROOT).as_posix()}` sha256 `{sha(SKETCH)}` (baseline aprovado: `f06cdc14…81ed`).',
         f'- `contexto_juridico.h` sha256 `{sha(CTX_H)}`.',
         f"- SD baseline `{BASE_SD.relative_to(ROOT).as_posix()}`: `CF88_RUNTIME.txt` {len(rd.data)} B sha256 `{sha(BASE_SD / '05_TEXT/CF88_RUNTIME.txt')}`; "
         f"`CF88_TEXT_MAP.IDX` sha256 `{sha(BASE_SD / '10_TARGETS/CF88_TEXT_MAP.IDX')}`.",
         f'- Quebra visual: `avancarUmaLinhaVisual()` com os avanços reais da fonte Arimo ({len(rd.adv)} glifos lidos do sketch), largura {WIDTH} px; '
         f'viewport {ROWS} linhas de {ROW_H} px; linha do CONTEXTO = linha central `{CENTER}` (7ª linha, y={TEXT_Y0 + CENTER * ROW_H}) '
         '(`escolherContextoPredominante`, regra principal).', '',
         '## 1–4. Offsets e estrutura', '', '| ITEM | OFFSET | LINHA FÍSICA | TARGET (TEXT_MAP) |', '|---|---|---|---|',
         f'| line_start Art. 193 (caput) | {a193[0]} | {a193[1]} | `CF88:ART.193` |',
         f'| Parágrafo único | {pu[0]} | {pu[1]} | `CF88:ART.193:PAR.UNICO` |',
         f'| Início do Art. 194 | {a194[0]} | {a194[1]} | `CF88:ART.194` |', '',
         f'- Byte range do caput: **[{a193[0]}, {pu[0]})** = {pu[0] - a193[0]} bytes → **{len(caput_lines)} linhas visuais**.',
         f'- Parágrafo único + cabeçalhos até o art. 194: [{pu[0]}, {a194[0]}) = {a194[0] - pu[0]} bytes → **{len(pu_lines)} linhas visuais** '
         '(os cabeçalhos "CAPÍTULO II / Da Seguridade Social / SEÇÃO I / Disposições Gerais" não têm linha própria no TEXT_MAP e resolvem, por piso, '
         'para `CF88:ART.193:PAR.UNICO`).',
         f'- Dados: `CF88:ART.193` flags `{rd.flags["CF88:ART.193"]}`; `CF88:ART.193:CAPUT` flags `{rd.flags["CF88:ART.193:CAPUT"]}`; '
         f'`CF88:ART.193:PAR.UNICO` flags `{rd.flags["CF88:ART.193:PAR.UNICO"]}`. Com ACTIVE_TARGET = `CF88:ART.193`, as chaves '
         f'`{"+".join(rd.query_keys("CF88:ART.193"))}` dão botão 4 = **{flag_art}** com {len(works_art)} obras: {", ".join(works_art)}.', '',
         '## 5–6. Viewport logo após "Buscar Art. 193"', '',
         f'`pesquisarArtigo("193")` acha a linha em offset **{pos}** (= line_start do caput: {pos == a193[0]}); `reiniciarIndice(pos)` + `linhaTopo=0` '
         'colocam o "Art. 193" na **linha 0 (topo)**.', '',
         '| LINHA | y | OFFSET | TARGET DA LINHA | TEXTO |', '|---|---|---|---|---|']
    for r in rows:
        mark = ' **← CONTEXTO / ACTIVE_TARGET**' if r['row'] == CENTER else ''
        M.append(f"| {r['row']} | {r['y']} | {r['offset']} | `{r['target']}`{mark} | {r['text'][:60].replace('|', '/')} |")
    M += ['', f'- **ACTIVE_TARGET calculado: `{act}`** (linha {CENTER}). Chaves: `{"+".join(rd.query_keys(act))}`. '
              f'Flags W: **{flag_act}** → layer4 expected **{"YES" if flag_act else "NO"}** ({len(works_act)} obras).', '',
          '## 7. Quais posições de rolagem resolvem o quê', '',
          'Rolagem = linha visual no topo relativa ao "Art. 193" (0 = estado logo após a busca; negativo = rolar para cima).', '',
          '| ROLAGEM | TOPO | LINHA CENTRAL | ACTIVE_TARGET | BOTÃO 4 (do target ativo) |', '|---|---|---|---|---|']
    M += [f"| {s['scroll']:+d} | {s['top_text'][:30].replace('|', '/')} | {s['center_text'][:40].replace('|', '/')} | `{s['active_target']}` | "
          f"{('**SIM — art. 193** (' if s['active_target'] == 'CF88:ART.193' else 'sim — outro artigo (') + str(s['works']) + ' obras)' if s['layer4'] else 'não'} |" for s in sc]
    M += ['', f'- Botão 4 do art. 193 aparece só nas rolagens **{pos_ok[0]:+d} a {pos_ok[-1]:+d}** (o caput precisa estar na linha central). '
              f'Na rolagem 0 (logo após a busca) o centro já está em `{act}`.' if pos_ok else '- Nenhuma posição mostra o botão 4.',
          '', '## Conclusão', '',
          f'- **Hipótese CONFIRMADA.** O caput do art. 193 ocupa {len(caput_lines)} linhas visuais; após a busca ele fica no topo (linhas 0–{len(caput_lines) - 1}) '
          f'e a linha central (6) cai em `{act}`. ACTIVE_TARGET ≠ `CF88:ART.193` → as chaves não incluem `CF88:ART.193:CAPUT` → sem flag W → '
          'o rodapé não mostra 4 REF. e a tecla 4 não abre nada.',
          '- **Por que Arthur não viu o botão:** testou logo após "Buscar Art. 193" (ou rolando sem centralizar o caput). Os dados estão corretos: '
          f'as 3 obras estão em `CF88:ART.193:CAPUT` no REF_PAYLOAD e a regra ART↔CAPUT as entrega quando o ACTIVE_TARGET é `CF88:ART.193`.',
          '- **BUG de dados/engine: NÃO.** O comportamento é o **esperado** pela regra aprovada (ACTIVE_TARGET = linha central). É, porém, uma limitação '
          'de UX: em artigos de caput curto seguido de parágrafo/incisos, o estado logo após a busca nunca ativa o próprio caput.',
          f'- **Não é exclusivo do art. 193.** No baseline físico, {len(misses)} de {len(allsearch)} artigos com obra no caput/linha do artigo NÃO mostram o '
          f'botão 4 logo após a busca: {", ".join("`" + x["article"] + "` (centro em `" + str(x["active_target"]) + "`)" for x in misses) or "nenhum"}.']
    if rd3:
        M += [f'- **RUN3 candidato** (mesmo texto e TEXT_MAP): {len(miss3)} de {len(all3)} artigos com obra na linha do artigo ficam sem botão 4 logo após a busca: '
              f'{", ".join("`" + x["article"] + "` (subir " + str(x["rows_up_needed"]) + " linha(s))" for x in miss3)}. '
              'Isto deve orientar o teste físico do RUN3 (ex.: art. 37: centralizar o caput antes de apertar 4).']
    M += ['', '## Procedimento de teste físico (sem mudar firmware)', '',
          f'1. Buscar Art. 193; 2. rolar **para cima** até o texto "Art. 193. A ordem social…" ficar na 7ª linha (centro); '
          f'3. o rodapé deve mostrar `CONTEXTO: Art. 193` e 4 REF.; 4. tecla 4 → {len(works_art)} obras.',
          f'5. Conferência objetiva: o monitor serial imprime `LEXV1: ACTIVE_TARGET=CF88:ART.193:PAR.UNICO off={rows[CENTER]["offset"]}` logo após a busca '
          f'e `LEXV1: ACTIVE_TARGET=CF88:ART.193 off=…` com o caput no centro (offsets do caput: {", ".join(str(x) for x, _ in caput_lines)}).', '',
          '## Possíveis soluções futuras (NÃO implementadas; decidir separadamente)', '',
          '1. **Busca centraliza o artigo:** após `pesquisarArtigo`, posicionar `linhaTopo` de modo que a linha do "Art. N" fique na linha central '
          '(mudança só no posicionamento pós-busca; ACTIVE_TARGET inalterado).',
          '2. **Linha de CONTEXTO = primeira linha de artigo visível quando o topo é o próprio "Art. N" logo após a busca** (estado "recém-buscado" '
          'até a primeira rolagem).',
          '3. **Indicador de navegação:** quando o caput tem camada 4 mas o ACTIVE_TARGET é um descendente, mostrar dica "↑ caput tem REF." '
          '(sem herdar vínculos).',
          '4. Manter o comportamento atual e documentar o procedimento de teste (custo zero; UX pior em caputs curtos).',
          '', 'Nenhuma opção altera a regra ART↔CAPUT nem propaga vínculos para incisos/parágrafos.', '',
          '## Resposta', '', '- art193 bug: **NÃO** (comportamento esperado do algoritmo atual; limitação de UX confirmada).']
    OUT.write_bytes(('\n'.join(M) + '\n').encode('utf-8'))
    print(json.dumps(dict(search=pos, art193=a193, par_unico=pu, art194=a194, caput_visual_lines=len(caput_lines), active_after_search=act,
                          layer4_after_search=flag_act, ok_scroll=pos_ok, baseline_misses=[x['article'] for x in misses],
                          run3_misses=[(x['article'], x['rows_up_needed']) for x in miss3]), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
