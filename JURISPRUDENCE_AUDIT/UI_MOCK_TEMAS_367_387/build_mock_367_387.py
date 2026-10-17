"""PÓS-NOTURNA Parte K — HOST-ONLY presentation mock for Temas 367 × 387 (identical thesis, distinct themes; J1.3 KEEP_BOTH).
Data-only: the two links (STF:RG:367 / STF:RG:387 → CF88:ART.16), the JURISPRUDENCIA.IDX rows, the labels ("RG TEMA 367/387") and the ficha
NAMES stay exactly as installed. Only the ficha TEXT gains a "TEMA (OBJETO)" block and a "NOTA" telling the reader the thesis is shared and
why the themes differ (facts from the official J1.3 sources S6/S7). Nothing is applied to any package or card.
Writes PROPOSED/STF_RG_367.TXT, PROPOSED/STF_RG_387.TXT and UI_MOCK_TEMAS_367_387.md (12-line screens, ~38 columns on the 3.2" 320×240 TFT).
"""
import hashlib
import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUD = HERE.parent
J13 = json.loads((AUD / 'J1_3_DECISIONS.json').read_text(encoding='utf-8'))['sources']
COLS, ROWS = 38, 12
TESE = ('A Lei Complementar 135/2010 não é aplicável às eleições gerais de 2010, em face do princípio da anterioridade eleitoral (art. 16 da '
        'Constituição Federal).')
FONTE = 'https://portal.stf.jus.br/repercussaogeral/retornartesesrepercussaogeral.asp'
TEMAS = {
    '367': dict(re='RE 631102 (paradigma substituído pelo RE 630147)', objeto='Inelegibilidade por renúncia a mandato: constitucionalidade '
                'da alínea k do art. 1º, I, da LC 64/90, discutida também à luz do art. 16.', outro='387', src='S7'),
    '387': dict(re='RE 633703', objeto='Aplicação da LC 135/2010 às eleições de 2010 à luz do art. 16.', outro='367', src='S6'),
}


def ficha(n):
    t = TEMAS[n]
    return (f'REPERCUSSÃO GERAL {n}\nTRIBUNAL: STF\nSTATUS: tese_fixada\nPROCESSO: {t["re"]}\n\n'
            f'TEMA (OBJETO)\n{t["objeto"]}\n\n'
            f'TESE/ENUNCIADO\n{TESE}\n\n'
            f'NOTA\nTese idêntica à do Tema {t["outro"]}. Os temas são distintos (leading cases e objetos diferentes; sem julgamento conjunto) '
            f'e por isso ambos aparecem no art. 16.\n\n'
            f'FONTE OFICIAL\n{FONTE}\n')


def screens(text):
    lines = []
    for par in text.split('\n'):
        lines += textwrap.wrap(par, COLS) or ['']
    return [lines[i:i + ROWS] for i in range(0, len(lines), ROWS)]


def main():
    out = HERE / 'PROPOSED'
    out.mkdir(exist_ok=True)
    md = ['# Mock de apresentação — Temas 367 × 387 (CF art. 16)', '', '```',
          'HOST-ONLY · NADA APLICADO · VÍNCULOS, IDX, RÓTULOS E NOMES DE FICHA INALTERADOS · aguarda decisão do usuário', '```', '',
          '**Problema.** As duas fichas instaladas são idênticas, exceto número e processo, e o leitor não vê por que há dois temas.',
          '',
          '**Proposta (só dados).** Nas duas fichas entram:', '',
          '- **TEMA (OBJETO):** o objeto de cada tema;',
          '- **NOTA:** curta, avisando que a tese é compartilhada.',
          '',
          'As fontes oficiais são as da J1.3: S6 (Tema 387) e S7 (Tema 367).', '',
          '## Lista no aparelho (inalterada)', '', '```', '+--------------------------------------+', '| CF ART. 16 - JURISPRUDÊNCIA (2)      |',
          '| 1 RG TEMA 367                        |', '| 2 RG TEMA 387                        |', '+--------------------------------------+', '```', '']
    rep = {}
    for n in TEMAS:
        txt = ficha(n)
        (out / f'STF_RG_{n}.TXT').write_bytes(txt.encode('utf-8'))
        sc = screens(txt)
        rep[n] = dict(bytes=len(txt.encode('utf-8')), sha256=hashlib.sha256(txt.encode('utf-8')).hexdigest(), screens=len(sc),
                      source=J13[TEMAS[n]['src']]['url'])
        md += [f'## Ficha proposta — Tema {n} (título "STF RG TEMA {n}"; {len(sc)} telas de {ROWS} linhas)', '']
        for i, s in enumerate(sc, 1):
            md += [f'Tela {i}:', '', '```'] + [f'|{l.ljust(COLS)}|' for l in s] + ['```', '']
    md += ['## Garantias', '',
           '- **Vínculos:** `STF:RG:367:CF88:16:-:-:-` e `STF:RG:387:CF88:16:-:-:-` inalterados.',
           '- **Índices e rótulos:** linhas do `JURISPRUDENCIA.IDX`, `JUR_LOOKUP.IDX`, `REF_PAYLOAD` e rótulos inalterados.',
           '- **Fichas:** os nomes (`STF_RG_367.TXT` e `STF_RG_387.TXT`) também não mudam; só o texto.',
           '- **Firmware:** nenhuma mudança. O leitor já quebra linhas e rola 12 linhas por tela.',
           f'- **Tamanho:** {rep["367"]["bytes"]} B e {rep["387"]["bytes"]} B, contra 349 B cada hoje.',
           '- **Aplicação:** a mudança só entra num pacote após aprovação do usuário. É um ajuste de conteúdo de ficha legada e exige regenerar o '
           'manifesto do pacote SD.', '']
    (HERE / 'UI_MOCK_TEMAS_367_387.md').write_text('\n'.join(md), encoding='utf-8', newline='\n')
    (HERE / 'UI_MOCK_BUILD.json').write_text(json.dumps(dict(phase='K', host_only=True, applied=False, links_changed=False, fichas=rep),
                                                        ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
