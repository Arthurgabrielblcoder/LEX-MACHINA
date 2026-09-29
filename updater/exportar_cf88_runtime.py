"""Exportador determinístico do CF88_RUNTIME (texto operacional único exibido pelo dispositivo).

Entrada: SOMENTE as fontes travadas em fontes_oficiais_senado/SOURCES_LOCK.json (CF 579494 + ADCT 604119, Compilação
Monovigente do Senado), conferidas por sha256 (bruto e normalizado). Nenhuma rede, nenhum relógio, nenhuma edição manual.

Saída: CF88_RUNTIME.txt (UTF-8 sem BOM, LF, termina com LF) + CF88_RUNTIME.provenance.json.
  1. Constituição (corpo monovigente, como extraído pelo pipeline);
  2. marcador inequívoco: a própria linha-título oficial do ADCT, "ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS",
     que deve ocorrer exatamente uma vez no runtime (é o source_marker do namespace ADCT em LEGAL_TARGET_ID/namespaces.json);
  3. ADCT (corpo monovigente).

HEADER_NORMALIZATION_RULE v1 (mecânica; não altera palavras): a fonte do Senado quebra o cabeçalho de artigo em duas linhas
("Art." / "37. A administração..."). Uma linha que é EXATAMENTE "Art." (maiúsculo, sem mais nada) é unida à linha seguinte
com um espaço SE e SOMENTE SE a seguinte começar pelo rótulo do artigo: ^\\d{1,4}(º|°|o)?(-[A-Z])? seguido de ".", espaço
ou fim de linha. Qualquer "Art." isolado que não satisfaça a condição faz o export FALHAR (fail closed). Linhas que começam
com "art." minúsculo (citações que quebraram linha no meio de uma frase) nunca são tocadas.

Uso: python exportar_cf88_runtime.py --out <dir>
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'fontes_oficiais_senado'
EXPORTER_VERSION = 1
NORMALIZATION_VERSION = 'HEADER_NORMALIZATION_RULE_V1'
ADCT_MARKER = 'ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS'
CF_TITLE = 'CONSTITUIÇÃO DA REPÚBLICA FEDERATIVA DO BRASIL'
ART_LABEL_RE = re.compile(r'^\d{1,4}(?:º|°|o)?(?:-[A-Z])?(?=[.\s]|$)')
ART_DOT_LABEL_RE = re.compile(r'^\. \d{1,4}(?:º|°|o)?(?:-[A-Z])?\.\s')
# Caso C: parágrafo colado ao anterior na própria fonte oficial ("...décimos).§ 4º O financiamento..."). Em texto normativo, uma
# remissão a parágrafo é sempre precedida de espaço ("o § 3º"); pontuação final seguida IMEDIATAMENTE de "§ N<ordinal> <Maiúscula>"
# é fronteira de dispositivo. Só se insere uma quebra de linha; nenhum caractere é alterado.
GLUED_PAR_RE = re.compile(r'(?<=[.;:)])(?=§ ?\d{1,3}(?:º|°)(?:-[A-Z])?\.? [A-ZÁÉÍÓÚÂÊÔÃÕÇ])')
# marcas de redação anterior/compilação multivigente (bloqueiam o export)
HISTORICAL_MARKERS = ('Redação dada pel', 'Incluído pel', 'Incluída pel', 'Texto original')
# notas oficiais de remissão da própria compilação monovigente (não são redação histórica; apenas contadas)
EDITORIAL_NOTES = ('(Vide ',)


class ExportError(RuntimeError):
    pass


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def normalize_headers(text):
    """Returns (normalized_text, stats). Pure function.

    Caso A: "Art." + linha que começa pelo rótulo -> "Art. " + linha (um espaço).
    Caso C: ver GLUED_PAR_RE (apenas insere quebra de linha antes de um parágrafo colado).
    Caso B: "Art"  + linha que começa por ". <rótulo>." -> concatenação exata "Art" + linha (nenhum caractere inserido);
            é o mesmo cabeçalho quebrado numa fronteira de tag HTML (ex.: ADCT arts. 76-B e 101).
    """
    split_c = len(GLUED_PAR_RE.findall(text))
    text = GLUED_PAR_RE.sub('\n', text)
    lines = text.split('\n')
    out, joined, joined_b, i = [], 0, 0, 0
    while i < len(lines):
        line = lines[i]
        if line == 'Art':
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if not ART_DOT_LABEL_RE.match(nxt):
                raise ExportError(f'HEADER_NORMALIZATION_UNSAFE linha {i + 1}: "Art" seguido de {nxt[:40]!r}')
            out.append('Art' + nxt)
            joined_b += 1
            i += 2
            continue
        if line == 'Art.':
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if not ART_LABEL_RE.match(nxt):
                raise ExportError(f'HEADER_NORMALIZATION_UNSAFE linha {i + 1}: "Art." seguido de {nxt[:40]!r}')
            out.append('Art. ' + nxt)
            joined += 1
            i += 2
            continue
        out.append(line)
        i += 1
    return '\n'.join(out), dict(joined_headers=joined, joined_headers_case_b=joined_b, split_glued_paragraphs_case_c=split_c,
                                lines_in=len(lines), lines_out=len(out))


CORRECTIONS = SRC / 'SOURCE_TEXT_CORRECTIONS.json'


def apply_source_corrections(ident, text, lock_entry, corrections=None):
    """Correções documentais EXATAS (SOURCE_TEXT_CORRECTIONS.json). Fail closed: se a publicação desta norma tem correção
    registrada e qualquer hash, a linha exata ou a contagem de ocorrências divergir, o export falha e exige revisão humana."""
    doc = corrections if corrections is not None else (json.loads(CORRECTIONS.read_text(encoding='utf-8')) if CORRECTIONS.is_file() else {'corrections': []})
    pub = lock_entry['publicacao_url'].rstrip('/').rsplit('/', 1)[1]
    applied = []
    for c in doc['corrections']:
        if c['norm_id'] != ident:
            continue
        cid = c['correction_id']
        if c.get('status') != 'APPROVED' or not c.get('reviewed') or c.get('correction_type') != 'SOURCE_TRANSCRIPTION_NORMALIZATION':
            raise ExportError(f'SOURCE_CORRECTION_NOT_VERIFIED {cid}: correcao nao aprovada/revisada')
        if (c['norma_id_senado'], c['publication_id'], c['raw_source_sha256'], c['normalized_source_sha256']) != \
                (lock_entry['norma_id_senado'], pub, lock_entry['raw_sha256'], lock_entry['normalizado_sha256']):
            raise ExportError(f'SOURCE_CORRECTION_NOT_VERIFIED {cid}: publicacao/hash mudou; revisar a correcao')
        ref = c['verification_reference']
        vp = HERE.parent / ref['stored_copy']
        if not vp.is_file() or _sha(vp.read_bytes()) != ref['stored_copy_sha256']:
            raise ExportError(f'SOURCE_CORRECTION_NOT_VERIFIED {cid}: copia da fonte de verificacao ausente ou alterada')
        lines = text.split('\n')
        hits = [i for i, l in enumerate(lines) if l == c['exact_raw_text']]
        if len(hits) != c['expected_occurrences']:
            raise ExportError(f"SOURCE_CORRECTION_NOT_VERIFIED {cid}: {len(hits)} ocorrencias exatas (esperado {c['expected_occurrences']})")
        for i in hits:
            lines[i] = c['normalized_text']
        text = '\n'.join(lines)
        applied.append(dict(correction_id=cid, correction_type=c['correction_type'], target_hint=c['target_hint'], occurrences=len(hits),
                            before_sha256=_sha(c['exact_raw_text'].encode('utf-8')), after_sha256=_sha(c['normalized_text'].encode('utf-8'))))
    return text, applied


def load_locked(ident, lock):
    s = lock['sources'][ident]
    d = SRC / s['dir']
    raw, norm = (d / 'raw.html').read_bytes(), (d / 'normalizado.txt').read_bytes()
    meta = json.loads((d / 'metadata.json').read_text(encoding='utf-8'))
    if _sha(raw) != s['raw_sha256'] or _sha(raw) != meta['raw_sha256']:
        raise ExportError(f'{ident}: RAW_SHA256_MISMATCH')
    if _sha(norm) != s['normalizado_sha256'] or _sha(norm) != meta['normalizado_sha256']:
        raise ExportError(f'{ident}: NORMALIZED_SHA256_MISMATCH')
    text = norm.decode('utf-8')
    if '\r' in text or text.startswith('﻿'):
        raise ExportError(f'{ident}: UNEXPECTED_CR_OR_BOM')
    return text, meta


def build_runtime(lock=None):
    lock = lock or json.loads((SRC / 'SOURCES_LOCK.json').read_text(encoding='utf-8'))
    cf, cf_meta = load_locked('CF88', lock)
    adct, adct_meta = load_locked('ADCT', lock)
    cf, cf_corr = apply_source_corrections('CF88', cf, lock['sources']['CF88'])
    adct, adct_corr = apply_source_corrections('ADCT', adct, lock['sources']['ADCT'])
    if not cf.startswith(CF_TITLE):
        raise ExportError('CF_TITLE_NOT_FIRST_LINE')
    if not adct.startswith(ADCT_MARKER + '\n'):
        raise ExportError('ADCT_MARKER_NOT_FIRST_LINE')
    if ADCT_MARKER in cf.split('\n'):
        raise ExportError('ADCT_MARKER_INSIDE_CF')
    cf_n, cf_st = normalize_headers(cf.rstrip('\n'))
    adct_n, adct_st = normalize_headers(adct.rstrip('\n'))
    runtime = cf_n + '\n' + adct_n + '\n'
    lines = runtime.split('\n')
    if lines.count(ADCT_MARKER) != 1:
        raise ExportError('ADCT_MARKER_NOT_UNIQUE')
    if any(l in ('Art.', 'Art') for l in lines):
        raise ExportError('UNJOINED_ART_HEADER')
    hist = {m: runtime.count(m) for m in HISTORICAL_MARKERS}
    if any(hist.values()):
        raise ExportError(f'HISTORICAL_MARKERS_PRESENT {hist}')
    data = runtime.encode('utf-8')
    adct_offset = len((cf_n + '\n').encode('utf-8'))
    prov = dict(
        schema_version=1, exporter='updater/exportar_cf88_runtime.py', exporter_version=EXPORTER_VERSION,
        normalization_version=NORMALIZATION_VERSION, editorial_notes={m: runtime.count(m) for m in EDITORIAL_NOTES}, encoding='UTF-8 sem BOM', line_endings='LF', final_newline=True,
        bytes=len(data), lines=runtime.count('\n'), sha256=_sha(data), adct_marker=ADCT_MARKER, adct_offset=adct_offset,
        composition=['CF88 (Senado 579494, Compilação Monovigente)', 'ADCT (Senado 604119, Compilação Monovigente)'],
        header_normalization=dict(CF88=cf_st, ADCT=adct_st), historical_markers=hist,
        sources={k: dict(norma_id_senado=m['norma_id_senado'], publicacao_url=m['publicacao_url'], raw_sha256=m['raw_sha256'],
                         normalizado_sha256=m['normalizado_sha256'], adquirido_em_utc=m['adquirido_em_utc'], tipo_compilacao=m['tipo_compilacao'])
                 for k, m in (('CF88', cf_meta), ('ADCT', adct_meta))},
        source_text_corrections=cf_corr + adct_corr,
        manual_edits=False)
    return data, prov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    data, prov = build_runtime()
    (out / 'CF88_RUNTIME.txt').write_bytes(data)
    (out / 'CF88_RUNTIME.provenance.json').write_bytes((json.dumps(prov, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: prov[k] for k in ('bytes', 'lines', 'sha256', 'adct_offset', 'header_normalization', 'historical_markers')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
