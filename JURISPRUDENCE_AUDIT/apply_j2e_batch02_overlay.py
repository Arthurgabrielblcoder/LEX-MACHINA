"""J2E — overlay of the BATCH02 decisions ratified by the user (J2D, ratified 2026-10-17). Deterministic, host-only, no network.

Device model = the one validated in J2B/J2C (legacy JURISPRUDENCIA.IDX 8 columns, append-only; ficha 03_CONTEUDO/<IDENTIFICADOR>.TXT):
  * ADI 7047/7064 joint record (STF:ADI:7047-7064, already on the card) on ADCT art. 101, § 5º and CF art. 100, § 11 (no new ficha);
  * ADI 7064 ALONE on ADCT art. 107-A: own record STF:ADI:7064, label "ADI 7064", own ficha (SAME_JUDGMENT as ADI 7047, NOT SAME_SCOPE);
  * Tema 793 (archived official corpus, J4 2026-09-21; same text as RE 855178 ED), Tema 950 (official page 2026-10-17) and SV 46
    (official page 2026-10-17, one ficha for CF art. 22, I and art. 85, parágrafo único): fichas in the exact J4.6 format (texto_detalhe);
  * HC 232627: editorially approved, NOT physically approved; type "hc" is not shown correctly by the current firmware ("OUTRO 232627"),
    so it goes ONLY into variant B (requires a firmware candidate). Variant A = everything the current firmware shows correctly.
Legacy key convention kept: ADCT articles use the CF88 prefix in the legacy key/lookup (as STF:RG:231:CF88:78:4:-:- for ADCT art. 78 § 4º);
the logical target (ADCT:ART.101:PAR.5) is what REF_PAYLOAD and the device use. Paragraph único -> UNICO.
Writes LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2E.json.   Usage: python apply_j2e_batch02_overlay.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEC = HERE / 'J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json'
CORPUS = Path('C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4/CORPUS_JURIS_CF_COMPLETO_PARCIAL.json')   # protected archive, read only
CORPUS_SHA = None   # recorded in the output (sha of the bytes read)
OUT = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2E.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-17', statement='Batch02 (J2D) ratificado integralmente',
                    decisions={'J0-BL-166': 'REALLOCATE -> ADCT art. 101, § 5º (registro conjunto ADI 7047/7064)',
                               'J0-BL-167': 'REALLOCATE -> ADCT art. 101, § 5º (registro conjunto ADI 7047/7064)',
                               'J0-BL-169': 'PROMOTE (rótulo "ADI 7064", não "ADI 7047/7064")',
                               'J0-BL-039': 'PROMOTE', 'J0-BL-049': 'REALLOCATE -> CF art. 22, I e art. 85, parágrafo único (ficha única)',
                               'J0-BL-052': 'REJECT_FALSE_POSITIVE (sem vínculo alternativo)', 'J0-BL-057': 'PROMOTE',
                               'J0-BL-076': 'REALLOCATE -> CF art. 100, § 11 (registro conjunto)',
                               'J0-BL-077': 'REALLOCATE -> CF art. 100, § 11 (registro conjunto)',
                               'J0-BL-058': 'PROMOTE editorial (HC232627_EDITORIAL_APPROVAL = YES; HC232627_PHYSICAL_APPROVAL = NO; tipo HC próprio)'})
URL_7064 = 'https://portal.stf.jus.br/processos/detalhe.asp?incidente=6330822'
URL_7697_UNUSED = None
URL_950 = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=950'
URL_SV46 = 'https://jurisprudencia.stf.jus.br/pages/search/seq-sumula805/false'
URL_HC = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22HC%20232627%22&base=acordaos'


def texto_detalhe(doc):
    """Exact copy of preparar_staging_j4_6.texto_detalhe (J4.6 pack on the card); fidelity proven by regenerating card fichas in the tests."""
    tipo = {"sumula_vinculante": "SÚMULA VINCULANTE", "repercussao_geral": "REPERCUSSÃO GERAL"}[doc["tipo"]]
    processo = doc.get("processo_principal") or "Não disponível na fonte."
    return (f"{tipo} {doc['numero']}\n"
            f"TRIBUNAL: {doc['tribunal']}\n"
            f"STATUS: {doc['status']}\n"
            f"PROCESSO: {processo}\n\n"
            "TESE/ENUNCIADO\n"
            f"{doc['tese_ou_enunciado']}\n\n"
            "FONTE OFICIAL\n"
            f"{doc['fonte_url']}\n")


def corpus():
    b = CORPUS.read_bytes()
    return {d['id']: d for d in json.loads(b.decode('utf-8'))['documentos']}, hashlib.sha256(b).hexdigest()


def docs():
    c, csha = corpus()
    rg793 = dict(c['STF:RG:793'])                                         # reused as archived (official endpoint capture 2026-09-21)
    sv46 = dict(c['STF:SV:46'], tese_ou_enunciado='A definição dos crimes de responsabilidade e o estabelecimento das respectivas normas de '
                                                   'processo e julgamento são da competência legislativa privativa da União.', fonte_url=URL_SV46)
    rg950 = dict(id='STF:RG:950', numero=950, processo_principal='RE 632115', status='tese_fixada', tipo='repercussao_geral',
                 titulo='Tema de Repercussão Geral 950', tribunal='STF', fonte_url=URL_950,
                 tese_ou_enunciado='1. A imunidade material parlamentar (art. 53, caput, c/c art. 27, § 1º, e art. 29, VIII, CF/1988) configura '
                                   'excludente da responsabilidade civil objetiva do Estado (art. 37, § 6º, CF/1988), afastando qualquer pretensão '
                                   'indenizatória em face do ente público por opiniões, palavras e votos cobertos por essa garantia. 2. Nas '
                                   'hipóteses em que a conduta do parlamentar extrapolar os limites da imunidade material, eventual '
                                   'responsabilização recairá de forma pessoal, direta e exclusiva sobre o próprio parlamentar, sob o regime de '
                                   'responsabilidade civil subjetiva.')
    notes = dict(rg793='Corpus J4 arquivado (endpoint oficial de teses, 2026-09-21); tese idêntica à do RE 855178 ED conferida em 2026-10-17 (T2).',
                 sv46='Corpus J4 arquivado trazia "são de competência"; a página oficial consultada em 2026-10-17 (T3) traz "são da competência": '
                      'usado o texto oficial atual.',
                 rg950='Não consta do corpus J4 (captura de 2026-09-21). Tese copiada da página oficial do acórdão (T6, 2026-10-17).')
    return dict(rg793=rg793, sv46=sv46, rg950=rg950), notes, csha


FICHA_7064 = '\n'.join([
    'AÇÃO DIRETA DE INCONSTITUCIONALIDADE 7064',
    'TRIBUNAL: STF',
    'STATUS: mérito julgado',
    'PROCESSO: ADI 7064 (Rel. Min. Luiz Fux)',
    '',
    'ART. 107-A DO ADCT (TETO DE PRECATÓRIOS, EC 114/2021)',
    'Em 30/11/2023 o Plenário julgou a ação parcialmente procedente e:',
    '- deu interpretação conforme ao caput do art. 107-A do ADCT, para que seus efeitos operem somente no exercício de 2022;',
    '- declarou inconstitucionais os incisos II e III do art. 107-A e, por arrastamento, os §§ 3º, 5º e 6º;',
    '- deferiu a abertura de créditos extraordinários para quitar os precatórios dos exercícios de 2022 a 2026 que excederam o subteto, '
    'reconhecendo que o pagamento se insere nas exceções do art. 3º, § 2º, da LC 200/2023.',
    '',
    'JULGAMENTO CONJUNTO',
    'Julgada em conjunto com a ADI 7047. Os pontos sobre o art. 107-A são somente da ADI 7064. Os pontos comuns às duas ações '
    '(art. 100, §§ 9º e 11, da CF e art. 101, § 5º, do ADCT) estão na ficha ADI 7047/7064.',
    '',
    'ACÓRDÃO',
    'Julgamento em 01/12/2023, DJe de 19/12/2023.',
    '',
    'FONTE OFICIAL',
    URL_7064]) + '\n'

FICHA_HC = '\n'.join([
    'HABEAS CORPUS 232627',
    'TRIBUNAL: STF',
    'STATUS: mérito julgado (Plenário)',
    'PROCESSO: HC 232627 (Rel. Min. Gilmar Mendes)',
    '',
    'TESE',
    'A prerrogativa de foro para julgamento de crimes praticados no cargo e em razão das funções subsiste mesmo após o afastamento do cargo, '
    'ainda que o inquérito ou a ação penal sejam iniciados depois de cessado seu exercício.',
    '',
    'JULGAMENTO',
    'Plenário, 12/03/2025; DJe de 16/07/2025. Dispositivo constitucional citado: art. 53, § 1º. Revê em parte a orientação da AP 937-QO.',
    '',
    'EMBARGOS DE DECLARAÇÃO',
    'Em 25/05/2026 (DJe de 08/06/2026) o Plenário acolheu embargos da PGR, com efeitos integrativos, para fixar balizas de aplicação da tese.',
    '',
    'FONTE OFICIAL',
    URL_HC]) + '\n'


def build():
    j2d = json.loads(DEC.read_text(encoding='utf-8'))
    dec = {d['recommendation_id']: d for d in j2d['decisions']}
    if sorted(dec) != sorted(RATIFICATION['decisions']):
        raise SystemExit('RATIFICATION_DOES_NOT_COVER_BATCH02')
    d, notes, csha = docs()
    url_joint = 'https://portal.stf.jus.br/processos/detalhe.asp?incidente=6330822'
    # (variant, target, source_id, legacy key, legacy row fields, lookup tuple, ficha identificador, ratified recs, label, payload extra)
    R = [
        ('A', 'ADCT:ART.101:PAR.5', 'STF:ADI:7047-7064', 'STF:ADI:7047-7064:CF88:101:5:-:-',
         ('adi', 'STF', '7047/7064', 'merito_julgado', 'ADI 7047/7064 (julgamento conjunto)', 'STF:ADI:7047-7064', url_joint),
         ('CF88', '101', '5', '', ''), None, ['J0-BL-166', 'J0-BL-167'], dict(aliases=['ADI 7047', 'ADI 7064'], joint='SAME_JUDGMENT_SAME_SCOPE')),
        ('A', 'ADCT:ART.107-A', 'STF:ADI:7064', 'STF:ADI:7064:CF88:107-A:-:-:-',
         ('adi', 'STF', '7064', 'merito_julgado', 'ADI 7064', 'STF:ADI:7064', URL_7064),
         ('CF88', '107-A', '', '', ''), 'STF:ADI:7064', ['J0-BL-169'],
         dict(aliases=['ADI 7064'], joint='SAME_JUDGMENT_NOT_SAME_SCOPE', joint_with='STF:ADI:7047 (não tratou do art. 107-A)')),
        ('A', 'CF88:ART.100:PAR.11', 'STF:ADI:7047-7064', 'STF:ADI:7047-7064:CF88:100:11:-:-',
         ('adi', 'STF', '7047/7064', 'merito_julgado', 'ADI 7047/7064 (julgamento conjunto)', 'STF:ADI:7047-7064', url_joint),
         ('CF88', '100', '11', '', ''), None, ['J0-BL-076', 'J0-BL-077'], dict(aliases=['ADI 7047', 'ADI 7064'], joint='SAME_JUDGMENT_SAME_SCOPE')),
        ('A', 'CF88:ART.23:INC.II', 'STF:RG:793', 'STF:RG:793:CF88:23:-:II:-',
         ('repercussao_geral', 'STF', '793', 'tese_fixada', 'Tema de Repercussão Geral 793', 'STF:RG:793', d['rg793']['fonte_url']),
         ('CF88', '23', '', 'II', ''), 'STF:RG:793', ['J0-BL-039'], {}),
        ('A', 'CF88:ART.22:INC.I', 'STF:SV:46', 'STF:SV:46:CF88:22:-:I:-',
         ('sumula_vinculante', 'STF', '46', 'vigente', 'Súmula Vinculante 46', 'STF:SV:46', URL_SV46),
         ('CF88', '22', '', 'I', ''), 'STF:SV:46', ['J0-BL-049'], {}),
        ('A', 'CF88:ART.85:PAR.UNICO', 'STF:SV:46', 'STF:SV:46:CF88:85:UNICO:-:-',
         ('sumula_vinculante', 'STF', '46', 'vigente', 'Súmula Vinculante 46', 'STF:SV:46', URL_SV46),
         ('CF88', '85', 'UNICO', '', ''), None, ['J0-BL-049'], {}),
        ('A', 'CF88:ART.53:CAPUT', 'STF:RG:950', 'STF:RG:950:CF88:53:-:-:-',
         ('repercussao_geral', 'STF', '950', 'tese_fixada', 'Tema de Repercussão Geral 950', 'STF:RG:950', URL_950),
         ('CF88', '53', '', '', ''), 'STF:RG:950', ['J0-BL-057'], {}),
        ('B', 'CF88:ART.53:PAR.1', 'STF:HC:232627', 'STF:HC:232627:CF88:53:1:-:-',
         ('hc', 'STF', '232627', 'merito_julgado', 'HC 232627', 'STF:HC:232627', URL_HC),
         ('CF88', '53', '1', '', ''), 'STF:HC:232627', ['J0-BL-058'], dict(requires_firmware='JTIPO_HC (rótulo "HC <NUMERO>")')),
    ]
    fichas = {'STF:ADI:7064': FICHA_7064, 'STF:RG:793': texto_detalhe(d['rg793']), 'STF:SV:46': texto_detalhe(d['sv46']),
              'STF:RG:950': texto_detalhe(d['rg950']), 'STF:HC:232627': FICHA_HC}
    records = []
    for variant, target, src, key, row, lookup, ficha, recs, extra in R:
        for r in recs:
            x = dec[r]
            want = {x['recommended_target']} | set(x.get('additional_targets') or [])
            if target not in want or x['decision'] not in ('PROMOTE', 'REALLOCATE_RECOMMENDED'):
                raise SystemExit(f'RATIFIED_TARGET_MISMATCH {r} {target}')
        records.append(dict(variant=variant, target_id=target, source_id=src, source_reference_id=key, label=row[4],
                            legacy_idx_row='|'.join((key,) + row), legacy_lookup=list(lookup), new_ficha=ficha,
                            ratified_decisions=recs, ratification=[RATIFICATION['decisions'][r] for r in recs],
                            sources=sorted({s for r in recs for s in dec[r]['sources']}),
                            temporal_version=sorted({dec[r]['temporal_version'] for r in recs}),
                            payload=dict(tribunal='STF', tipo=row[0], numero=row[2], titulo=row[4], fonte=row[6], status_processual=row[3],
                                         **{k: v for k, v in extra.items() if k in ('aliases',)}),
                            joint=extra.get('joint'), joint_with=extra.get('joint_with'), requires_firmware=extra.get('requires_firmware')))
    doc = dict(schema_version=1, norma_id='CF88', round='J2E', ratification=RATIFICATION, decisions_file=DEC.relative_to(ROOT).as_posix(),
               decisions_sha256=hashlib.sha256(DEC.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
               archive_corpus=dict(path=CORPUS.as_posix(), sha256=csha), text_notes=notes,
               variants=dict(A='Batch02 compatível com o firmware físico atual (sem HC)', B='A + HC 232627 (exige firmware candidato com JTIPO_HC)'),
               legacy_key_convention='ADCT usa o prefixo CF88 na chave e no lookup legado (STF:RG:231:CF88:78:4:-:- = ADCT art. 78, § 4º); '
                                     'o target lógico (ADCT:ART.x) é o do REF_PAYLOAD.',
               rejected=dict(recommendation_id='J0-BL-052', precedent='STF:ADI:2167', decision='REJECT_FALSE_POSITIVE', alternative_link=None),
               total=len(records), records=records, fichas=fichas)
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(OUT.name, hashlib.sha256(b).hexdigest())
