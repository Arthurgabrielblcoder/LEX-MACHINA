"""J2B.1 — J2B_PREDEPLOY_TEMPORAL_FIX: Tema 558 leaves the CURRENT CF art. 100, § 9º (EC 113/2021 wording) and is linked to CF art. 100
(structural level) with an explicit temporal note (EC 62/2009). Editorial decision ratified by the user on 2026-10-16. Deterministic.

Same mechanism as J1.4 (CF88_LINK_EXCLUSIONS_* + CF88_JURIS_RELOCATIONS_*). The link key STF:RG:558:CF88:100:-:-:- is kept, so the device opens
the same legacy record and ficha (STF_RG_558.TXT, untouched). Scope: ONLY the § 9º link. The § 10 link of Tema 558 is not touched (the § 10
in force is still the EC 62/2009 text the thesis judged), and the 256 are not re-audited.
Writes:
  LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J2B_1.json   1 record MATERIAL_MISMATCH_EXCLUDED
  LEGAL_TARGET_ID/derived/CF88_JURIS_RELOCATIONS_J2B_1.json 1 relocated link (same precedent, same key, CF art. 100, temporal note)
Usage: python apply_j2b_1_tema558.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_X = ROOT / 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J2B_1.json'
OUT_R = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_RELOCATIONS_J2B_1.json'
J2A = HERE / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json'
KEY = 'STF:RG:558:CF88:100:-:-:-'
OLD = f'JURISPRUDENCE:{KEY}@CF88:ART.100:PAR.9'
NEW_TARGET = 'CF88:ART.100'
NOTE = ('Tema referente aos antigos §§ 9º e 10 do art. 100, incluídos pela EC 62/2009 (compensação de precatórios). Não corresponde ao texto '
        'atual do § 9º, dado pela EC 113/2021.')
RATIFICATION = dict(by='ARTHUR', on='2026-10-16', statement='TEMA_558_CURRENT_TARGET = CF art. 100', label='J2B_PREDEPLOY_TEMPORAL_FIX',
                    directives='Remover CF art. 100, § 9º ← Tema 558; criar CF art. 100 ← Tema 558 com TEMPORAL_VERSION = EC 62/2009 e nota de '
                               'redação histórica. Não alterar a tese; não retirar o tema do acervo; não reabrir a J1.')
LEGACY_FICHA = dict(path='99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_558.TXT',
                    sha256_on_card='(ver J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json)',
                    states='A tese do Tema 558 (RE 678360) trata da compensação "prevista nos §§ 9º e 10 do art. 100 da Constituição Federal, '
                           'incluídos pela EC nº 62/09".')


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def build():
    j2a = json.loads(J2A.read_text(encoding='utf-8'))
    src = j2a['sources']
    card = json.loads((HERE / 'J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json').read_text(encoding='utf-8'))['entries']
    ficha = dict(LEGACY_FICHA, sha256_on_card=card[LEGACY_FICHA['path']]['sha256'])
    evidence = dict(
        official_source=src['P1']['title'], official_source_url=src['P1']['url'],
        sources=[dict(id=s, url=src[s]['url'], sha256=src[s].get('dom_text_sha256') or src[s].get('snapshot_sha256')) for s in ('P1', 'S4', 'S3')],
        legacy_ficha=ficha, verified_on='2026-10-16',
        verified_by='J2B (observação) ratificada por Arthur em 2026-10-16 como J2B_PREDEPLOY_TEMPORAL_FIX',
        findings=['P1 (Planalto): o § 9º tem duas redações; a vigente é a da EC 113/2021 ("Sem que haja interrupção no pagamento…"); a da EC 62/2009 '
                  '(compensação no momento da expedição) não está mais em vigor.',
                  'Ficha do Tema 558 no cartão: a tese trata dos §§ 9º e 10 incluídos pela EC 62/2009.',
                  'S4 (ementa da ADI 7064, item 28): a redação do § 9º dada pela EC 113/2021 é "sensivelmente diferente" da declarada '
                  'inconstitucional nas ADIs 4425/4357.'])
    excl = [dict(reference_id=OLD, target_id='CF88:ART.100:PAR.9', source_id='STF:RG:558', source_reference_id=KEY, status='MATERIAL_MISMATCH_EXCLUDED',
                 verified_subject='Compensação de precatórios dos §§ 9º e 10 na redação da EC 62/2009.',
                 expected_subject='CF88:ART.100:PAR.9 (conteúdo atual, EC 113/2021)',
                 reason='ALVO_HISTORICO_INCORRETO: a tese julgou o § 9º da EC 62/2009; o § 9º exibido hoje é o da EC 113/2021.',
                 evidence=evidence, relocated_to=NEW_TARGET, decided_in='J2B.1 (J2B_PREDEPLOY_TEMPORAL_FIX), ratificado em 2026-10-16')]
    reloc = [dict(relocation_id=f'J2B.1-RELOC:{KEY}@{NEW_TARGET}', reference_id=f'JURISPRUDENCE:{KEY}@{NEW_TARGET}', target_id=NEW_TARGET,
                  source_id='STF:RG:558', source_reference_id=KEY, relocated_from=[OLD], temporal_note=NOTE, temporal_version='EC 62/2009',
                  review_status='HUMAN_APPROVED_RELOCATION', decision_refs=['J2B_PREDEPLOY_TEMPORAL_FIX'], main_source='P1',
                  sources=evidence['sources'], untouched=[f'JURISPRUDENCE:{KEY}@CF88:ART.100:PAR.10'])]
    base = dict(schema_version=1, norma_id='CF88', round='J2B.1', ratification=RATIFICATION, decisions_file=J2A.relative_to(ROOT).as_posix(),
                decisions_sha256=sha_lf(J2A))
    x_doc = dict(base, policy='Overlay de exclusão J2B.1: vínculo de jurisprudência num dispositivo cuja redação atual não é a que o precedente '
                              'julgou. Mesmo mecanismo de CF88_LINK_EXCLUSIONS*.json. Fail closed.', total=len(excl), records=excl)
    r_doc = dict(base, policy='Overlay de realocação J2B.1: mesmo precedente e mesma chave, no art. 100 (nível estrutural), com nota temporal. '
                              'Aplicado pelo build RUN9 depois da exclusão. Fail closed.', total=len(reloc), records=reloc)
    return [(p, (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')) for p, doc in ((OUT_X, x_doc), (OUT_R, r_doc))]


if __name__ == '__main__':
    outs = build()
    if '--check' in sys.argv:
        ok = all(p.is_file() and p.read_bytes() == b for p, b in outs)
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for p, b in outs:
        p.write_bytes(b)
        print(p.name, hashlib.sha256(b).hexdigest(), json.loads(b)['total'])
