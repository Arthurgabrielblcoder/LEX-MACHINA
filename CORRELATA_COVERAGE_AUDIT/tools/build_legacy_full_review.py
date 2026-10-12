"""CF88_CORRELATA_LEGACY_FULL_REVIEW — auditable decision for EVERY one of the 44 visible legacy CORRELATA links.

19 links were decided by C1A (NEEDS_REVIEW queue, independently reviewed); this tool reviews the remaining 25 one by one, reusing evidence
already available: (1) the norm text on the card (sha256 from the C0 evidence pin), (2) the official Planalto pages already downloaded and
hashed in C1A/C1B, (3) the official CF text. No new candidate is researched. The 2 hidden historical links are listed apart and are not
counted among the 44. NOTHING IS APPLIED: no exclusion, no addition, no RUN4.

Writes CF88_CORRELATA_LEGACY_FULL_REVIEW.json and CF88_CORRELATA_LEGACY_FULL_REVIEW.md. Usage: python build_legacy_full_review.py [--check]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_c1a_review as A  # noqa: E402
import build_c1b_high_batch02 as B2  # noqa: E402
import build_c1b_high_batch03 as B3  # noqa: E402
import build_c1b_high_batch04 as B4  # noqa: E402

AUDIT = A.AUDIT
OUT_JSON = AUDIT / 'CF88_CORRELATA_LEGACY_FULL_REVIEW.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_LEGACY_FULL_REVIEW.md'
PIN = AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json'
DECISIONS = A.DECISIONS
BASE = dict(branch='cf-correlata-coverage-audit', head='a597844bc42b0da944b97cc67d428294eff86c2f',
            device_entenda_810='44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef')
TS = B3.TS
OFFICIAL = dict(A.SOURCES, LEI_14965_2024=B2.SOURCES['L14965'], LC_199_2023=B2.SOURCES['LC199'], LC_109_2001=B4.SOURCES['LC109'])
ICMS_T = TS('IN_FORCE', revalidate_on='2033-01-01', note='ADCT, arts. 128 a 133 (EC 132/2023): transição e extinção do ICMS até 2033')
COFINS_T = TS('IN_FORCE', revalidate_on='2027-01-01', note='ADCT, art. 126, II (EC 132/2023): extinção da contribuição do art. 195, I, "b", a partir de 2027')
VACATIO_T = TS('VACATIO_LEGIS', effective_from='2028-01-01', early=True, note='Lei 14.965/2024, art. 13; mesma situação dos HIGH dos arts. 131, § 2º e 132')
PNE_T = TS('IN_FORCE', effective_from='2026-04-14', revalidate_on='2036-04-14', note='PNE decenal (art. 1º da Lei 15.388/2026)')


def L(decision, confidence, official, analysis, provisions, retarget_to=None, route_fix=None, temporal=None, flags=(), scope=(), note=None):
    assert decision in DECISIONS, decision
    return dict(decision=decision, confidence=confidence, official=list(official), analysis=analysis, provisions=provisions,
                retarget_to=retarget_to, route_fix=route_fix, temporal=temporal or B3.IN_FORCE, flags=list(flags), scope=list(scope), note=note)


PNE_FANOUT = ('A Lei 15.388/2026 aprova o PNE "para cumprir o disposto no art. 214" (art. 1º). É a lei exigida pelo caput. Os incisos I a '
              'VI são os fins a que o plano deve conduzir; o art. 4º da lei lista objetivos gerais próprios, que não correspondem um a um aos '
              'incisos. Seis vínculos idênticos (mesma relação, mesmo art. 4º) nos incisos são fan-out sem especificidade.')
# key: (target_id, destination_norm_key)
REVIEW = {
    ('CF88:ART.5:INC.XLIII', 'LEI:13260/2016'): L(
        'KEEP', 'ALTA', [], 'Ementa e art. 1º: "regulamenta o disposto no inciso XLIII do art. 5º", disciplinando o terrorismo. Relação '
        'material direta (crime inafiançável e insuscetível de graça).', 'art. 1º', scope=('NON_EXCLUSIVE',),
        note='A Lei 8.072/1990 (crimes hediondos) também disciplina o inciso; não exclusivo.'),
    ('CF88:ART.20:PAR.1', 'LEI:12734/2012'): L(
        'REMOVE', 'MEDIA', [], 'A Lei 12.734/2012 é lei alteradora: modifica as Leis 9.478/1997 e 12.351/2010 (ementa; arts. 2º e 3º) para '
        'redistribuir royalties e participação especial. O conteúdo está incorporado às leis alteradas; o art. 1º só enuncia o objeto. '
        'Pela regra das leis alteradoras incorporadas, o vínculo não se sustenta. A disciplina direta do § 1º já tem substituição decidida na '
        'C1A (REPLACE do vínculo Lei 9.984/2000 no mesmo target).', 'arts. 1º a 3º', flags=('ALTERADORA_INCORPORADA',),
        note='Risco adicional não usado como fundamento: as novas regras de distribuição foram objeto de cautelar na ADI 4917 (não verificado nesta rodada).'),
    ('CF88:ART.34:INC.V:AL.b', 'LC:63/1990'): L(
        'KEEP', 'ALTA', ['LC_63_1990'], 'Art. 10: a falta de entrega aos Municípios, nos prazos da lei complementar, sujeita o Estado à '
        'intervenção "nos termos do disposto na alínea b do inciso V do art. 34". A LC 63 fixa os prazos a que a alínea b se refere.', 'art. 10'),
    ('CF88:ART.37:INC.II', 'LEI:14965/2024'): L(
        'KEEP', 'ALTA', ['LEI_14965_2024'], 'Art. 1º: normas gerais sobre concurso público "para assegurar ... o disposto no inciso II do '
        'caput do art. 37". Relação jurídica correta. A lei, porém, está em vacatio legis até 2028-01-01: o vínculo visível hoje apresenta '
        'como vigente uma lei futura.', 'art. 1º', temporal=VACATIO_T, flags=('TEMPORAL_DEVICE_BLOCK', 'SUPPRESS_UNTIL_EFFECTIVE'),
        scope=('NON_EXCLUSIVE',), note='Decisão jurídica KEEP; ação de aparelho segue a política C2 de vacatio (DO_NOT_PUBLISH_AS_CURRENT): '
        'neutralizar por exclusão temporária até a vigência.'),
    ('CF88:ART.37:PAR.3:INC.I', 'LEI:13460/2017'): L(
        'KEEP', 'ALTA', ['LEI_13460_2017'], 'Lei de participação, proteção e defesa do usuário de serviços públicos: reclamações (ouvidorias), '
        'manutenção dos serviços e avaliação de qualidade, conteúdo do § 3º, I. O texto cita o inciso I expressamente.', 'art. 1º',
        note='O fan-out da mesma relação nos incisos II e III já foi decidido na C1A (REPLACE e HOLD).'),
    ('CF88:ART.146', 'LC:199/2023'): L(
        'RETARGET', 'ALTA', ['LC_199_2023'], 'Art. 1º: o Estatuto de simplificação de obrigações acessórias é instituído "em observância ao '
        'disposto na alínea b do inciso III do caput do art. 146". O vínculo no artigo inteiro é genérico; o dispositivo específico é a '
        'alínea b do inciso III.', 'art. 1º', retarget_to='CF88:ART.146:INC.III:AL.b',
        note='Converge com o HIGH CORRC0-8CF6938B096C (APPROVE, mesmo target): aplicar uma única relação.'),
    ('CF88:ART.150:PAR.7', 'LC:87/1996'): L(
        'KEEP_WITH_ROUTE_FIX', 'ALTA', ['LC_87_1996', 'CF88'], 'O § 7º autoriza a substituição tributária para frente com "imediata e '
        'preferencial restituição" se o fato gerador presumido não ocorrer. O art. 10 da LC 87 assegura essa restituição no ICMS. Relação '
        'material direta, mas restrita ao ICMS; a rota atual abre a norma sem salto.', 'art. 10', route_fix=dict(mode='ABRIR_ARTIGO_INTERNO',
        articles=['10']), temporal=ICMS_T, scope=('ESCOPO_PARCIAL', 'NON_EXCLUSIVE')),
    ('CF88:ART.153:PAR.4:INC.II', 'LEI:9393/1996'): L(
        'KEEP_WITH_ROUTE_FIX', 'ALTA', ['LEI_9393_1996', 'CF88'], 'Art. 2º: "Nos termos do art. 153, § 4º, in fine", o ITR não incide sobre '
        'pequenas glebas rurais. A lei cita o § 4º pela redação anterior à EC 42/2003; o conteúdo corresponde hoje ao inciso II do § 4º '
        '(renumeração verificada no texto compilado). A rota atual abre a norma sem salto.', 'art. 2º',
        route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['2'])),
    ('CF88:ART.153:PAR.4:INC.III', 'LEI:11250/2005'): L(
        'KEEP', 'ALTA', ['LEI_11250_2005'], 'Ementa: "Regulamenta o inciso III do § 4º do art. 153"; art. 1º disciplina os convênios de '
        'fiscalização e cobrança do ITR com os Municípios que optarem.', 'art. 1º'),
    ('CF88:ART.155:PAR.2:INC.XII', 'LC:87/1996'): L(
        'KEEP', 'ALTA', ['LC_87_1996', 'CF88'], 'O inciso XII reserva à lei complementar contribuintes, substituição tributária, compensação, '
        'local das operações, exclusão nas exportações, manutenção de crédito e base de cálculo do ICMS. A LC 87 é a lei geral do ICMS que '
        'disciplina essas alíneas. Não exclusiva: a alínea g (isenções por deliberação dos Estados) é da LC 24/1975.', 'arts. 1º a 36',
        temporal=ICMS_T, scope=('NON_EXCLUSIVE',)),
    ('CF88:ART.158:PAR.1:INC.II', 'LC:63/1990'): L(
        'RETARGET', 'ALTA', ['LC_63_1990', 'CF88'], 'O inciso II do § 1º remete à lei estadual (até 35%, indicadores de educação); a LC 63 '
        'não disciplina essa parcela. O art. 3º, I, da LC 63 disciplina a parcela "na proporção do valor adicionado", que é o inciso I.',
        'art. 3º', retarget_to='CF88:ART.158:PAR.1:INC.I', route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['3'])),
    ('CF88:ART.161:INC.II', 'LC:62/1989'): L(
        'KEEP', 'ALTA', ['LC_62_1989'], 'Art. 1º: cálculo, entrega e controle das liberações do FPE e do FPM "consoante o disposto nos incisos '
        'II e III do art. 161". O inciso II exige a LC dos critérios de rateio e da entrega.', 'art. 1º'),
    ('CF88:ART.161:INC.III', 'LC:62/1989'): L(
        'KEEP', 'ALTA', ['LC_62_1989'], 'Mesmo art. 1º: o inciso III exige a LC do acompanhamento, pelos beneficiários, do cálculo das quotas '
        'e da liberação; a LC 62 disciplina o controle das liberações.', 'art. 1º'),
    ('CF88:ART.195:INC.I', 'LC:70/1991'): L(
        'RETARGET', 'ALTA', ['LC_70_1991', 'CF88'], 'Art. 1º institui a COFINS "nos termos do inciso I do art. 195", na redação original. '
        'Depois da EC 20/1998 o inciso I se divide em alíneas, e a contribuição sobre faturamento/receita é a alínea b. A EC 132/2023 '
        'extingue essa contribuição a partir de 2027 (ADCT, art. 126, II).', 'arts. 1º e 2º', retarget_to='CF88:ART.195:INC.I:AL.b',
        route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['1']), temporal=COFINS_T, flags=('SCHEDULED_EXTINCTION',)),
    ('CF88:ART.201:INC.III', 'LEI:7998/1990'): L(
        'KEEP_WITH_ROUTE_FIX', 'ALTA', ['LEI_7998_1990', 'CF88'], 'O inciso III vigente trata da proteção ao trabalhador em desemprego '
        'involuntário; a Lei 7.998 regula o seguro-desemprego e cita o "inciso IV do art. 201" pela numeração anterior à EC 20/1998 '
        '(renumeração verificada). A rota atual abre a norma sem salto; o programa está no art. 2º.', 'arts. 1º e 2º',
        route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['2'])),
    ('CF88:ART.202:CAPUT', 'LC:109/2001'): L(
        'KEEP', 'ALTA', ['LC_109_2001'], 'Art. 1º: regime de previdência complementar "nos termos do caput do art. 202". É a lei complementar '
        'geral exigida pelo caput.', 'art. 1º'),
    ('CF88:ART.202:PAR.4', 'LC:108/2001'): L(
        'KEEP', 'ALTA', [], 'Art. 1º: a relação entre entes públicos patrocinadores e suas entidades fechadas, "a que se referem os §§ 3º, '
        '4º, 5º e 6º do art. 202", é disciplinada pela LC 108. O § 4º exige exatamente essa lei complementar.', 'art. 1º'),
    ('CF88:ART.202:PAR.5', 'LC:108/2001'): L(
        'KEEP_WITH_ROUTE_FIX', 'ALTA', [], 'O § 5º estende a LC do § 4º, no que couber, às permissionárias e concessionárias de serviços '
        'públicos patrocinadoras. O art. 26 da LC 108 trata disso expressamente; a rota atual leva ao art. 1º.', 'art. 26',
        route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['26'])),
    ('CF88:ART.202:PAR.6', 'LC:108/2001'): L(
        'KEEP_WITH_ROUTE_FIX', 'ALTA', [], 'O § 6º manda a LC estabelecer requisitos para a designação das diretorias e disciplinar a inserção '
        'dos participantes nos colegiados. A LC 108 faz isso nos arts. 9º a 20 (estrutura, composição paritária do conselho deliberativo no '
        'art. 11, requisitos da diretoria no art. 20); a rota atual leva ao art. 1º.', 'arts. 9º, 11 e 20',
        route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['11', '20'])),
    ('CF88:ART.214:INC.I', 'LEI:15388/2026'): L(
        'RETARGET', 'ALTA', [], PNE_FANOUT + ' Os seis vínculos são consolidados em um único, no caput.', 'art. 1º',
        retarget_to='CF88:ART.214:CAPUT', route_fix=dict(mode='ABRIR_ARTIGO_INTERNO', articles=['1']), temporal=PNE_T,
        note='A meta de investimento em proporção do PIB (inciso VI) está no Anexo (Meta 19.a), sem artigo roteável: NEXT_STEP se a rota suportar anexos.'),
    **{('CF88:ART.214:INC.' + inc, 'LEI:15388/2026'): L(
        'REMOVE', 'ALTA', [], PNE_FANOUT + ' Este vínculo é removido por consolidação no caput (ver inciso I).', 'art. 4º', temporal=PNE_T,
        flags=('FAN_OUT_CONSOLIDATED',)) for inc in ('II', 'III', 'IV', 'V', 'VI')},
}


def pin_texts():
    files = json.loads(PIN.read_text(encoding='utf-8'))['relations_v2_package']['files']
    out = {}
    for path, f in files.items():
        parts = path.split('/')
        if len(parts) == 4 and parts[1] == '03_NORMAS_EXTERNAS':
            out[parts[2]] = dict(path=path, sha256=f['sha256'], bytes=f['bytes'], on_card=f['on_card'])
    return out


def build():
    base = json.loads(A.BASELINE.read_text(encoding='utf-8'))['links']
    c1a = {d['reference_id']: d for d in json.loads(A.OUT_JSON.read_text(encoding='utf-8'))['decisions']}
    texts = pin_texts()
    visible = [b for b in base if b['visibility'] == 'CURRENT_VISIBLE']
    hidden = [b for b in base if b['visibility'] != 'CURRENT_VISIBLE']
    used, rows = set(), []
    for b in visible:
        key = (b['target_id'], b['destination_norm_key'])
        row = dict(reference_id=b['reference_id'], target_id=b['target_id'], display_target=b['display_target'], relation_id=b['relation_id'],
                   destination_norm_id=b['destination_norm_id'], destination_norm_key=b['destination_norm_key'],
                   destination_norm_name=b['destination_norm_name'], current_route=dict(mode=b['relation_mode'], articles=b['relation_dest_articles']),
                   c0_plausibility=b['plausibility'], c0_citation=b['destination_text_citation'], c0_flags=b['review_flags'], applied=False)
        if b['reference_id'] in c1a:
            d = c1a[b['reference_id']]
            row.update(review_round='C1A', decision=d['decision'], confidence=d['confidence'], retarget_to=d['retarget_to'],
                       replacement_norms=d['replacement_norms'], route_fix=d['route_fix'], legal_analysis=d['legal_analysis'],
                       independent_review=d.get('independent_review'))
        else:
            r = REVIEW[key]
            used.add(key)
            ev = [dict(kind='CARD_TEXT_PIN', **texts[b['destination_norm_id']])]
            ev += [dict(kind='OFFICIAL_PLANALTO', source_id=k, **OFFICIAL[k]) for k in r['official']]
            row.update(review_round='LEGACY_FULL_REVIEW', decision=r['decision'], confidence=r['confidence'], retarget_to=r['retarget_to'],
                       replacement_norms=[], route_fix=r['route_fix'], legal_analysis=r['analysis'], relevant_provisions=r['provisions'],
                       temporal=r['temporal'], flags=r['flags'], scope=r['scope'], note=r['note'], evidence=ev)
        rows.append(row)
    if used != set(REVIEW):
        raise SystemExit(f'LEGACY_REVIEW_MISMATCH unused={sorted(set(REVIEW) - used)}')
    cnt = Counter(r['decision'] for r in rows)
    now = [r for r in rows if r['review_round'] == 'LEGACY_FULL_REVIEW']
    summary = dict(LEGACY_EXPORT_TOTAL=len(base), LEGACY_VISIBLE_TOTAL=len(visible), LEGACY_HIDDEN_HISTORICAL=len(hidden),
                   LEGACY_VISIBLE_REVIEWED=len(rows), decided_in_c1a=len(rows) - len(now), reviewed_now=len(now),
                   decisions={k: cnt.get(k, 0) for k in DECISIONS},
                   decisions_reviewed_now={k: sum(1 for r in now if r['decision'] == k) for k in DECISIONS},
                   flags_reviewed_now=dict(sorted(Counter(f for r in now for f in r['flags']).items())),
                   new_official_downloads=0)
    doc = dict(schema_version=1, artifact='CF88_CORRELATA_LEGACY_FULL_REVIEW', applied=False, verified_on=A.VERIFIED_ON, baseline=BASE,
               decision_values=list(DECISIONS),
               policy='Cada um dos 44 vínculos visíveis tem decisão auditável. Nada aplicado: o catálogo legado, as exclusões e o export RUN3 '
                      'não foram alterados. Um vínculo não é mantido só porque a norma cita o artigo: conteúdo material, dispositivo, '
                      'renumeração, vigência, fan-out, lei alteradora e target específico foram verificados.',
               summary=summary, links=rows,
               hidden_historical=[dict(reference_id=b['reference_id'], target_id=b['target_id'], visibility=b['visibility']) for b in hidden])
    return A.jdump(doc), report(summary, rows, doc['hidden_historical']).encode('utf-8')


def report(s, rows, hidden):
    L_ = []
    a = L_.append
    a('# CF88_CORRELATA — revisão integral dos vínculos legados visíveis')
    a('')
    a('**Decisões editoriais. Nada foi aplicado.** O catálogo, as exclusões e o export RUN3 não mudaram.')
    a('')
    a(f"- **Export:** {s['LEGACY_EXPORT_TOTAL']} vínculos; {s['LEGACY_VISIBLE_TOTAL']} visíveis; {s['LEGACY_HIDDEN_HISTORICAL']} históricos ocultos (fora da contagem).")
    a(f"- **Revisados:** {s['LEGACY_VISIBLE_REVIEWED']}/{s['LEGACY_VISIBLE_TOTAL']}; {s['decided_in_c1a']} já decididos na C1A; {s['reviewed_now']} revisados agora.")
    a('- **Evidência reutilizada:** texto da norma no cartão (sha256 do pin C0) e páginas oficiais já baixadas na C1A/C1B. Nenhum download novo.')
    a('')
    a('| Decisão | Total (44) | C1A | Agora |')
    a('|---|---:|---:|---:|')
    for k in DECISIONS:
        a(f"| {k} | {s['decisions'][k]} | {s['decisions'][k] - s['decisions_reviewed_now'][k]} | {s['decisions_reviewed_now'][k]} |")
    a('')
    a('## Pontos de atenção')
    a('')
    a('- **Lei 14.965/2024 × art. 37, II:** KEEP jurídico, mas a lei está em vacatio até 2028-01-01. Pela política C2, o vínculo deve ser '
      'neutralizado por exclusão temporária até a vigência (`SUPPRESS_UNTIL_EFFECTIVE`).')
    a('- **LC 70/1991 × art. 195, I:** retarget para a alínea b; a COFINS é extinta a partir de 2027 (ADCT, art. 126, II): revalidar em 2027-01-01.')
    a('- **LC 87/1996 (arts. 150, § 7º e 155, § 2º, XII):** ICMS em transição até 2033; revalidar.')
    a('- **PNE (Lei 15.388/2026):** seis vínculos de fan-out nos incisos do art. 214 viram um único vínculo no caput.')
    a('- **Lei 12.734/2012 × art. 20, § 1º:** REMOVE (lei alteradora incorporada).')
    a('- **LC 199/2023:** o retarget para o art. 146, III, b converge com um HIGH aprovado; aplicar uma única relação.')
    a('')
    a('## Vínculos (44)')
    a('')
    a('| Rodada | Target | Norma | Decisão | Retarget / rota | Temporal |')
    a('|---|---|---|---|---|---|')
    for r in rows:
        extra = r['retarget_to'] or ''
        if r.get('route_fix'):
            rf = r['route_fix']
            extra = (extra + ' ' if extra else '') + (f"arts. {', '.join(rf['articles'])}" if isinstance(rf, dict) and rf.get('articles') else 'rota')
        if r.get('replacement_norms'):
            extra = (extra + ' ' if extra else '') + 'substituir: ' + ', '.join(x.get('norm_name', str(x)) if isinstance(x, dict) else str(x)
                                                                             for x in r['replacement_norms'])
        t = (r.get('temporal') or {}).get('temporal_status', '—')
        a(f"| {r['review_round']} | `{r['target_id']}` | {r['destination_norm_name']} | {r['decision']} | {extra or '—'} | {t} |")
    a('')
    a(f'## Históricos ocultos ({len(hidden)}, fora dos 44)')
    a('')
    for h in hidden:
        a(f"- `{h['target_id']}` ({h['visibility']})")
    a('')
    return '\n'.join(L_) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('NOT_DETERMINISTIC')
    paths = (OUT_JSON, OUT_MD)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[0])['summary'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
