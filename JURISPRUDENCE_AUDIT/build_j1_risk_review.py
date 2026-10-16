"""J1 — risk-driven review of the 86 jurisprudence links flagged by J0 (READ-ONLY, host-only, no network).

The 86 decisions below are PERSISTED explicitly (local-evidence review of 2026-10-16, Claude, pending human ratification); this script only
attaches the archived evidence (J4 excerpt and thesis), validates coverage against J0, runs the light control of the 191 links without signal
and simulates the effect of the proposed removals. Nothing published is changed (no REF_*, TARGETS, firmware or package).
Writes JURISPRUDENCE_AUDIT/J1_DECISIONS.json.   Usage: python build_j1_risk_review.py [--check]
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
J0 = HERE / 'J0_DIAGNOSTIC_AUDIT.json'
J4 = Path('C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4/VINCULOS_EXPLICITOS.json')
TARGETS = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX'
OUT = HERE / 'J1_DECISIONS.json'
AUTHORITY = 'CLAUDE_LOCAL_EVIDENCE_REVIEW_2026-10-16 (pendente de ratificação humana; sem web)'

R = 'REMOVE_FALSE_POSITIVE'
X = 'EXTERNAL_REVIEW_REQUIRED'
DUP = 'DUPLICATE_OR_REDUNDANT'
K = 'KEEP_CONFIRMED'


def rid(src, key_tail, target):
    return f'JURISPRUDENCE:{src}:CF88:{key_tail}@{target}'


# (reference_id, decision, confidence, cited_norm, cause, comment, relocation_candidate, tier)
EXPLICIT = [
    # ---- Tier 1: norma/namespace confundidos (o trecho oficial cita OUTRA norma com o mesmo número)
    (rid('STF:RG:63', '1:-:-:-', 'CF88:ART.1'), R, 'ALTA', 'Decreto-Lei 491/1969, art. 1º', 'NUMERACAO_DE_OUTRA_NORMA',
     'Tese trata do crédito-prêmio de IPI instituído pelo art. 1º do DL 491/1969; não interpreta o art. 1º da CF.', None, 1),
    (rid('STF:RG:1266', '3:-:-:-', 'CF88:ART.3'), R, 'ALTA', 'LC 190/2022, art. 3º', 'NUMERACAO_DE_OUTRA_NORMA',
     'O "art. 3º" é da LC 190/2022 (vacatio legis do ICMS-DIFAL); a CF citada é o art. 150, III, c.', None, 1),
    (rid('STF:RG:295', '3:-:-:-', 'CF88:ART.3'), R, 'ALTA', 'Lei 8.009/1990, art. 3º, VII', 'NUMERACAO_DE_OUTRA_NORMA',
     'O "art. 3º, VII" é da Lei 8.009/1990 (fiador/bem de família); o vínculo com o art. 6º da CF permanece.', None, 1),
    (rid('STF:RG:1157', '19:-:-:-', 'CF88:ART.19'), R, 'ALTA', 'ADCT, art. 19', 'NAMESPACE_ADCT_LIDO_COMO_CF',
     'Estabilidade excepcional do art. 19 do ADCT, não o art. 19 da CF (vedações federativas).', 'ADCT:ART.19', 1),
    (rid('STF:RG:703', '47:-:-:-', 'CF88:ART.47'), R, 'ALTA', 'Lei 6.880/1980 (Estatuto dos Militares), art. 47', 'NUMERACAO_DE_OUTRA_NORMA',
     'Recepção do art. 47 da Lei 6.880/80; o art. 47 da CF (quórum de deliberação) não é objeto.', None, 1),
    (rid('STF:RG:241', '48:-:III:-', 'CF88:ART.48:INC.III'), R, 'ALTA', 'Lei 4.215/1963, art. 48, III', 'NUMERACAO_DE_OUTRA_NORMA',
     'Exame de Ordem previsto no art. 48, III, da antiga Lei 4.215/63.', None, 1),
    (rid('STF:RG:241', '8:-:IV:-', 'CF88:ART.8:INC.IV'), R, 'ALTA', 'Lei 8.906/1994 (EOAB), art. 8º, IV', 'NUMERACAO_DE_OUTRA_NORMA',
     'Exame de Ordem do art. 8º, IV, do Estatuto da OAB; o art. 8º, IV, da CF (contribuição confederativa) não é objeto.', None, 1),
    (rid('STF:RG:84', '14:2:-:-', 'CF88:ART.14:PAR.2'), R, 'ALTA', 'Lei 4.502/1964, art. 14, § 2º', 'NUMERACAO_DE_OUTRA_NORMA',
     'Tese declara inconstitucional o § 2º do art. 14 da Lei 4.502/64 (IPI); a CF citada é o art. 146, III, a. O art. 14, § 2º, da CF é alistamento eleitoral.', None, 1),
    (rid('STF:RG:63', '41:1:-:-', 'CF88:ART.41:PAR.1'), R, 'ALTA', 'ADCT, art. 41, § 1º', 'NAMESPACE_ADCT_LIDO_COMO_CF',
     'A tese cita "§ 1º do art. 41 do ADCT" (revogação de incentivos fiscais); o art. 41, § 1º, da CF trata da perda do cargo do servidor estável.', 'ADCT:ART.41:PAR.1', 1),
    (rid('STF:RG:975', '43:-:-:-', 'CF88:ART.43:CAPUT'), R, 'ALTA', 'LC estadual SP 1.059/2008, art. 43, caput', 'NUMERACAO_DE_OUTRA_NORMA',
     'Constitucionalidade do art. 43 da LC paulista 1.059/2008 (licença-prêmio); o art. 43 da CF (regiões) não é objeto.', None, 1),
    (rid('STF:RG:975', '43:1:-:-', 'CF88:ART.43:PAR.1'), R, 'ALTA', 'LC estadual SP 1.059/2008, art. 43, § 1º', 'NUMERACAO_DE_OUTRA_NORMA',
     'Mesma tese; o § 1º citado é da LC paulista.', None, 1),
    (rid('STF:RG:847', '98:-:-:-', 'CF88:ART.98:CAPUT'), R, 'ALTA', 'ADCT, art. 98, caput', 'NAMESPACE_ADCT_LIDO_COMO_CF',
     'Lotação de defensores conforme o art. 98 do ADCT (EC 80/2014); o art. 98 da CF trata dos juizados especiais.', 'ADCT:ART.98', 1),
    (rid('STF:RG:847', '98:2:-:-', 'CF88:ART.98:PAR.2'), R, 'ALTA', 'ADCT, art. 98, § 2º', 'NAMESPACE_ADCT_LIDO_COMO_CF',
     'Mesma tese; o § 2º citado é do art. 98 do ADCT.', 'ADCT:ART.98:PAR.2', 1),
    (rid('STF:RG:1031', '16:-:-:-', 'CF88:ART.16'), R, 'ALTA', 'Convenção 169 da OIT, art. 16.4', 'NUMERACAO_DE_OUTRA_NORMA',
     'O trecho cita "art. 16.4 da Convenção 169 OIT"; o art. 16 da CF é a anterioridade eleitoral. O Tema 1031 segue no art. 231.', None, 1),
    (rid('STF:RG:966', '227:-:-:-', 'CF88:ART.227'), R, 'ALTA', 'LC 75/1993, art. 227', 'NUMERACAO_DE_OUTRA_NORMA',
     'Lista de parcelas remuneratórias cita "art. 227, da LC nº 75/1993"; o art. 227 da CF (criança e adolescente) não é objeto.', None, 1),
    (rid('STF:RG:976', '227:-:-:-', 'CF88:ART.227'), R, 'ALTA', 'LC 75/1993, art. 227', 'NUMERACAO_DE_OUTRA_NORMA',
     'Mesmo trecho do Tema 966 (julgamento conjunto).', None, 1),
    (rid('STF:RG:396', '3:-:-:-', 'CF88:ART.3'), R, 'ALTA', 'EC 47/2005, art. 3º', 'NUMERACAO_DE_OUTRA_NORMA',
     'Regra de transição do art. 3º da EC 47/2005; o art. 3º da CF (objetivos fundamentais) não é objeto.', None, 1),
    (rid('STF:RG:396', '7:-:-:-', 'CF88:ART.7'), R, 'ALTA', 'EC 41/2003, art. 7º', 'NUMERACAO_DE_OUTRA_NORMA',
     'Paridade do art. 7º da EC 41/2003; o art. 7º da CF (direitos dos trabalhadores) não é objeto.', None, 1),
    (rid('STF:RG:455', '6:-:-:-', 'CF88:ART.6'), R, 'ALTA', 'Decreto 21.981/1932, arts. 6º a 8º', 'NUMERACAO_DE_OUTRA_NORMA',
     'Profissão de leiloeiro (arts. 6º a 8º do Decreto 21.981/1932); o vínculo com o art. 5º, XIII, da CF permanece.', None, 1),
    (rid('STF:RG:400', '96:-:-:-', 'CF88:ART.96'), R, 'ALTA', 'ADCT, art. 96', 'NAMESPACE_ADCT_LIDO_COMO_CF',
     'O trecho cita "art. 96, inserido no Ato das Disposições Constitucionais Transitórias".', 'ADCT:ART.96', 1),
    # ---- Tier 5 (temporal): a tese cita redação ANTERIOR; o texto atual do mesmo § trata de outra matéria (decisão exige fonte externa)
    (rid('STF:SV:17', '100:-:-:-', 'CF88:ART.100:PAR.1'), X, 'MEDIA', 'CF, art. 100, § 1º (redação anterior à EC 62/2009)', 'RENUMERACAO_POR_EMENDA',
     'SV 17 refere-se ao "período previsto no § 1º"; o § 1º atual (local) define débitos alimentícios e o prazo de pagamento está no § 5º. Confirmar correspondência antes de realocar.', 'CF88:ART.100:PAR.5?', 5),
    (rid('STF:RG:147', '100:-:-:-', 'CF88:ART.100:PAR.1'), X, 'MEDIA', 'CF, art. 100, § 1º (redação original e EC 30/2000)', 'RENUMERACAO_POR_EMENDA',
     'Mesma questão do período de graça; o trecho declara expressamente a redação original/EC 30.', 'CF88:ART.100:PAR.5?', 5),
    (rid('STF:RG:594', '40:-:-:-', 'CF88:ART.40:PAR.4'), X, 'MEDIA', 'CF, art. 40, § 4º (redação anterior à EC 20/1998)', 'REDACAO_ANTERIOR',
     'O § 4º atual (local) veda critérios diferenciados; a tese trata das regras na redação anterior à EC 20/98.', None, 5),
    (rid('STF:RG:594', '40:-:-:-', 'CF88:ART.40:PAR.5'), X, 'MEDIA', 'CF, art. 40, § 5º (redação anterior à EC 20/1998)', 'REDACAO_ANTERIOR',
     'O § 5º atual (local) trata da idade do professor; a tese trata da redação anterior à EC 20/98.', None, 5),
    # ---- Tier 2: materialmente idêntico com IDs diferentes
    (rid('STF:RG:387', '16:-:-:-', 'CF88:ART.16'), DUP, 'ALTA', 'CF, art. 16', 'TESE_IDENTICA_A_OUTRO_PRECEDENTE',
     'Texto da tese idêntico ao do Tema 367 no mesmo target; ambos válidos. Decidir se a exibição mantém os dois (temas distintos) ou consolida.', None, 2),
]

# KEEP_CONFIRMED: the excerpt names the CF provision explicitly; the signal was a heuristic (granularity/split/other norm also cited/parent-child)
KEEP_COMMENT = {
    'BROAD_ARTICLE_TARGET_WITH_SUBDIVISIONS': 'A citação nomeia o artigo da CF sem subdivisão; a granularidade do vínculo é fiel à fonte.',
    'SPLIT_FROM_MIXED_CITATION': 'Split determinístico fiel à citação literal da CF (cada dispositivo nomeado vira um vínculo).',
    'NORM_CONTEXT_CF_AND_OTHER_NORM_IN_SAME_CITATION': 'O dispositivo é citado como da CF; a outra norma aparece no mesmo trecho apenas como objeto/contexto.',
    'NORM_CONTEXT_NO_NORM_MARKER': 'A tese completa (arquivada) situa o dispositivo na CF/ADCT corretamente.',
    'PARENT_CHILD_SAME_SOURCE': 'A tese cita o artigo e o parágrafo separadamente; os dois vínculos são legítimos.',
    'TARGET_STATUS_UNKNOWN_VALIDITY': 'Tese cita expressamente o § 4º do art. 78 do ADCT; o sinal decorre só da validade temporal do target.',
}
KEEP_NOTES = {
    rid('STF:SV:7', '192:3:-:-', 'CF88:ART.192:PAR.3'): 'Vínculo correto (a SV trata do § revogado); o target revogado aparece com status CURRENT no catálogo de status — registrar para a Lei Seca.',
    rid('STF:RG:98', '192:3:-:-', 'CF88:ART.192:PAR.3'): 'Idem SV 7: § 3º revogado pela EC 40/2003 é o próprio objeto da tese.',
    rid('STF:RG:1254', '40:-:-:-', 'CF88:ART.40'): 'Cita o art. 40 "na redação dada pela EC 20/98"; vínculo de artigo mantido, com nota temporal.',
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def build():
    j0 = load(J0)
    j4 = {x['vinculo_id']: x for x in json.loads(J4.read_bytes().decode('utf-8'))}
    items = {n['reference_id']: n for n in j0['structural_audit']['items']}
    inv = {x['reference_id']: x for x in j0['inventory'] if x['visibility'] == 'CURRENT_VISIBLE'}
    explicit = {e[0]: e for e in EXPLICIT}
    missing = sorted(set(explicit) - set(items))
    if missing:
        raise SystemExit(f'DECISION_FOR_UNKNOWN_SIGNAL {missing[0]}')
    decisions = []
    for ref_id in sorted(items, key=lambda r: (min(TIER_OF(items[r]), explicit.get(r, (None,) * 8)[7] or 9), r)):
        n, x = items[ref_id], inv[ref_id]
        j = j4[x['link_key']]
        ev = j.get('evidencia_vinculo') or {}
        e = explicit.get(ref_id)
        if e:
            _, dec, conf, cited, cause, comment, reloc, tier = e
        else:
            base = n['reasons'][0].split(':')[0]
            dec, conf, cited, cause, reloc, tier = K, 'ALTA', 'CF', None, None, TIER_OF(n)
            comment = KEEP_NOTES.get(ref_id) or KEEP_COMMENT[base if base in KEEP_COMMENT else
                                                              next(r.split(':')[0] for r in n['reasons'] if r.split(':')[0] in KEEP_COMMENT)]
        decisions.append(dict(
            relation_id=ref_id, target_id=n['target_id'], precedent=n['source_id'], processo=j.get('processo_principal'), tier=tier,
            j0_severity=n['severity'], signal_reasons=n['reasons'], decision=dec, confidence=conf, cited_norm=cited, cause=cause,
            comment=comment, relocation_candidate=reloc,
            local_evidence=dict(excerpt=ev.get('referencia_detectada'), source='J4 VINCULOS_EXPLICITOS.evidencia_vinculo (texto oficial arquivado)',
                                official_url=(j.get('fonte_oficial') or {}).get('url'), official_sha256=(j.get('fonte_oficial') or {}).get('sha256_conteudo'),
                                thesis_sha256=sha((j.get('tese_ou_resumo') or '').encode('utf-8'))),
            authority=AUTHORITY))
    if len(decisions) != 86:
        raise SystemExit(f'SIGNAL_SET_NOT_86 {len(decisions)}')
    # ---- light control of the 191 links without signal (structure + provenance + broader other-norm scan)
    OTHER = r'(lei|decreto|c[oó]digo|LC|lei complementar|EC|emenda constitucional|ADCT|ato das disposi|conven[cç][aã]o|regimento|resolu|portaria|medida provis|estatuto|CTN|CPC|CPP|CLT)'
    no_signal = [x for r, x in sorted(inv.items()) if r not in items]
    scan = []
    for x in no_signal:
        j = j4[x['link_key']]
        art, tese = re.escape(str(j['origem_artigo'])), j['tese_ou_resumo']
        pats = [rf'art(?:igo)?s?\.?\s*{art}\s*(?:º|o|°)?\b[^.;()]{{0,60}}?\b(?:d[aoe]s?|inserid[oa] n[oa])\s+{OTHER}',
                rf'{OTHER}[^.;()]{{0,25}},\s*art(?:igo)?s?\.?\s*{art}\s*(?:º|o|°)?\b', rf'art(?:igo)?s?\.?\s*{art}\.\d']
        hits = [m.group(0) for p in pats for m in re.finditer(p, tese, re.I)]
        if hits:
            scan.append(dict(relation_id=x['reference_id'], target_id=x['target_id'], precedent=x['source_id'], hits=hits,
                             verdict='CF_CITATION_WITH_AMENDMENT_WORDING_NOTE' if all(re.search(r'constitui', h, re.I) for h in hits) else 'NEEDS_LOOK'))
    light = dict(relations=len(no_signal), classification='NO_SIGNAL_KEEP_PENDING_GLOBAL_REVIEW',
                 structure_ok=all(x['origin'] and x['tipo'] and x['numero'] for x in no_signal),
                 broader_other_norm_scan_hits=len(scan), needs_look=sum(s['verdict'] == 'NEEDS_LOOK' for s in scan), scan=scan)
    # ---- identical theses across precedents (materially identical, different IDs)
    by_text = collections.defaultdict(set)
    for x in j4.values():
        by_text[x['tese_ou_resumo']].add(x['id'])
    identical = [sorted(v) for v in sorted(by_text.values(), key=lambda s: sorted(s)) if len(v) > 1]
    # ---- impact of the proposed removals (logical simulation; nothing is regenerated)
    tflags = {l.split('|')[0]: l.split('|')[3] for l in TARGETS.read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')}
    removed = {d['relation_id'] for d in decisions if d['decision'] == R}
    remaining = [x for r, x in inv.items() if r not in removed]
    left = collections.Counter(x['target_id'] for x in remaining)
    touched = sorted({inv[r]['target_id'] for r in removed})
    lose = [t for t in touched if left[t] == 0]

    def query_keys(t):
        return [t, t + ':CAPUT'] if t.startswith('CF88:ART.') and ':' not in t[len('CF88:ART.'):] else [t]
    # what the reader shows on the article line (ART.n + ART.n:CAPUT)
    lines_losing = sorted({k for t in lose for k in ([t[:-len(':CAPUT')]] if t.endswith(':CAPUT') else [t])
                           if not any(left[q] for q in query_keys(k))})
    impact = dict(relations_before=len(inv), proposed_removals=len(removed), relations_after=len(remaining),
                  targets_touched=len(touched), targets_losing_last_j=len(lose), targets_keeping_j=len(touched) - len(lose),
                  targets_losing_last_j_list=lose, j_flags_that_would_change=[dict(target_id=t, before=tflags.get(t), after_position2='-') for t in lose],
                  reader_lines_losing_2_juris=lines_losing,
                  relocation_candidates=sorted({d['relocation_candidate'] for d in decisions if d['decision'] == R and d['relocation_candidate']}),
                  note='Simulação lógica. Materializar exige export RUN6 com exclusões (CF88_LINK_EXCLUSIONS) e prova de invariância das camadas congeladas.')
    summary = collections.Counter(d['decision'] for d in decisions)
    final = dict(KEEP_CONFIRMED=summary[K], REMOVE_FALSE_POSITIVE=summary[R], EXTERNAL_REVIEW_REQUIRED=summary[X],
                 DUPLICATE_OR_REDUNDANT=summary[DUP], WEAK_PROVENANCE=summary.get('KEEP_BUT_WEAK_PROVENANCE', 0),
                 NO_SIGNAL=light['relations'], TOTAL=sum(summary.values()) + light['relations'])
    critical = [d for d in decisions if d['j0_severity'] == 'HIGH']
    return dict(
        artifact='J1_DECISIONS', mode='READ_ONLY', authority=AUTHORITY, inputs=dict(j0_sha256=sha(J0.read_bytes().replace(b'\r\n', b'\n')),
                                                                                       j4_sha256=sha(J4.read_bytes())),
        reconciliation=dict(CRITICAL_SIGNAL_COUNT=len(critical), PROBABLE_CROSS_NORM_FALSE_POSITIVES=sum('LIKELY_OTHER_NORM_ARTICLE' in d['signal_reasons'] for d in critical),
                            critical_other=[dict(relation_id=d['relation_id'], reasons=d['signal_reasons']) for d in critical
                                            if 'LIKELY_OTHER_NORM_ARTICLE' not in d['signal_reasons']],
                            note='J0: 8 HIGH = 7 LIKELY_OTHER_NORM_ARTICLE + 1 TARGET_STATUS_UNKNOWN_VALIDITY (ADCT art. 78, § 4º ← Tema 231). '
                                 'A revisão local encontrou mais 13 falsos positivos da mesma classe em sinais MEDIUM/LOW (total 20).'),
        summary=final, decisions=decisions, no_signal_light_control=light, identical_theses=identical, removal_impact=impact,
        backlog_148_touched=False)


def TIER_OF(n):
    rs = [r.split(':')[0] for r in n['reasons']]
    if any(r in ('LIKELY_OTHER_NORM_ARTICLE',) or r.startswith('NORM_CONTEXT') for r in rs):
        return 1
    if any(r.startswith('DUPLICATE') for r in rs):
        return 2
    if 'PARENT_CHILD_SAME_SOURCE' in rs:
        return 3
    if any(r in ('SOURCE_NOT_VERIFIABLE', 'NO_J4_ORIGIN_RECORD') for r in rs):
        return 4
    return 5


def render():
    return (json.dumps(build(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = render()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print(json.dumps(dict(reconciliation={k: v for k, v in d['reconciliation'].items() if k != 'note'}, summary=d['summary'],
                          light={k: v for k, v in d['no_signal_light_control'].items() if k != 'scan'},
                          impact={k: v for k, v in d['removal_impact'].items() if k != 'note'}, identical=d['identical_theses']), ensure_ascii=False, indent=1))
