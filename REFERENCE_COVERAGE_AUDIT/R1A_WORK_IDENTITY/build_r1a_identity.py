"""R1A: work identity of the two works held as APPROVED_PENDING_WORK_IDENTITY (REFERENCE_EXPANSION_01-P20 and -P21).

Output: R1A_WORK_IDENTITY_CATALOG.json, same record schema as CATALOGO_EXPANSAO_200 (candidate record), so the R1 promotion can apply the
same checks as apply_reference_expansion_round1.promote(). Every factual field below is supported by a consulted source recorded in
03_FONTES (collect_sources_r1a.py); the paraphrases are editorial (no third-party text is copied). Fail closed: a cited source that is not
PAGINA_CONSULTADA, or a record without an identity source, stops the build. Deterministic (no clock, no network).
Usage: python build_r1a_identity.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / '03_FONTES'
OUT = HERE / 'R1A_WORK_IDENTITY_CATALOG.json'
COLLECTION = 'R1A_WORK_IDENTITY'
# user decision of 2026-10-15 (R1A): sources disagree on the year of Pro Dia Nascer Feliz; the year of the Mostra archive record is used
YEAR_DECISION_P21 = dict(decided_on='2026-10-15', decided_by='ARTHUR', rule='Ano do registro oficial do arquivo da Mostra Internacional de '
                         'Cinema de São Paulo (29ª Mostra): primeira exibição pública documentada.', value=2005,
                         divergences=[dict(source=6, value=2006, note='UFMG Espaço do Conhecimento cita 2006.'),
                                      dict(source=5, value=2007, note='Catálogo PLFD Dartmouth data a obra em 2007 (lançamento comercial).'),
                                      dict(source=7, value=2006, note='Guia da Semana (ano de produção 2006): página não consultável (HTTP 403).'),
                                      dict(source=None, value=2006, note='Literal da proposta P21, sem fonte registrada.')])


def src(n, locator, supports):
    rec = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(SRC.glob(f'{n:03}_*.json'))]
    if len(rec) != 1:
        raise SystemExit(f'SOURCE_RECORD_NOT_FOUND {n}')
    r = rec[0]
    if r['verificacao'] != 'PAGINA_CONSULTADA':
        raise SystemExit(f'SOURCE_NOT_CONSULTED {n} {r["verificacao"]}')
    return dict(accessed_on=r['accessed_on'], locator=locator, supports=supports, tier=r['tier'], url=r['url'], verificacao=r['verificacao'],
                collection_record=f'{SRC.relative_to(ROOT).as_posix()}/{sorted(SRC.glob(f"{n:03}_*.json"))[0].name}',
                snapshot_sha256=r['snapshot_sha256'])


def evidence(work_id, cid, n, fact, predicate, content_type, source, limits):
    return dict(ONTOLOGY_GAP=dict(description='Descrição factual preservada. Objetos, participantes e qualificadores não preenchidos não devem ser '
                                              'inferidos; mapear explicitamente na ontologia congelada antes da ingestão.',
                                  status='REVISAO_SEMANTICA_PRE_INGESTAO'),
                centrality='CENTRAL', claim=dict(context=[], effects=[], factual_description=fact, objects=[], participants=[], predicate=predicate,
                                                 subjects=[]),
                content_type=content_type, evidence_id=f'{work_id}-E{n:02}', not_targeted_to_device=True,
                provenance=dict(candidate_id=cid, collection=COLLECTION, engine_executed=False, source_basis='Fonte concreta consultada; paráfrase editorial'),
                source=dict(source, paraphrase=fact), state='DOCUMENTADA_PRELIMINAR', transposition_limits=limits, work_id=work_id)


def records():
    out = []
    # ---- P20: SOS Saúde (Sicko) -> CF88:ART.196
    wid, cid = 'R1A-DOC-001', 'R1A-001'
    s1 = src(1, 'Festival de Cannes — ficha do filme (Hors Compétition 2007)', ['identidade', 'fato_central'])
    s2 = src(2, 'AdoroCinema — ficha e sinopse da obra', ['identidade', 'fato_central'])
    fact = ('Documentário de Michael Moore que examina o sistema de saúde dos Estados Unidos a partir de casos de pessoas comuns e o compara com '
            'sistemas públicos de saúde de outros países, como Canadá e Cuba.')
    limits = ['Documentário de autor e opinativo sobre o sistema norte-americano; não descreve o SUS nem o regime jurídico brasileiro.',
              'Áreas potenciais são metadados editoriais; não constituem correspondência com dispositivo.']
    out.append(dict(
        ano=2007, areas_potenciais=['saúde', 'seguro privado', 'sistemas universais'], candidate_id=cid, candidate_number=1,
        criadores=['Michael Moore'],
        evidencias=[evidence(wid, cid, 1, fact, 'DOCUMENTAR', 'ARGUMENTO_DOCUMENTAL', s2, limits)],
        fontes=[s1, s2], franquia=None,
        metadata_pendente=['Data de estreia no Brasil não confirmada nas fontes consultadas; não inferida.'],
        not_targeted_to_device=True, notas={}, objetos_juridicos_potenciais=['acesso universal à saúde', 'sistema de saúde baseado em seguros'],
        pais='Estados Unidos', provenance=dict(batch='R1A', candidate_id=cid, ingestion_ready=True, ontology_changed=False),
        publisher_distribuidor_editora=['Dog Eat Dog Films'], resumo_factual_curto=fact,
        riscos=['Obra opinativa; as comparações entre países são do autor.'],
        status_catalogo='CANDIDATO_NAO_INTEGRADO', status_triagem='APTA_COM_RESSALVA', subtipo=None, tipo='DOCUMENTÁRIO',
        titulo='Sicko - S.O.S. Saúde', titulo_informado='SOS Saúde (Sicko)', titulo_original='Sicko', titulo_ptbr='Sicko - S.O.S. Saúde',
        transposition_limits=limits, work_id=wid, required_by=dict(decision_id='REFERENCE_EXPANSION_01-P20', target_id='CF88:ART.196')))
    # ---- P21: Pro Dia Nascer Feliz -> CF88:ART.206:INC.I
    wid, cid = 'R1A-DOC-002', 'R1A-002'
    s3 = src(3, 'Mostra Internacional de Cinema em São Paulo — arquivo, ficha do filme (29ª Mostra)', ['identidade', 'fato_central', 'ano'])
    s4 = src(4, 'Mostra Internacional de Cinema em São Paulo — arquivo em inglês (título internacional)', ['identidade'])
    s5 = src(5, 'Portuguese Language Films @ Dartmouth — ficha do filme', ['identidade', 'fato_central'])
    s6 = src(6, 'UFMG Espaço do Conhecimento — notícia de exibição do documentário', ['identidade'])
    fact = ('Documentário de João Jardim que acompanha estudantes de 14 a 17 anos, de escolas públicas e particulares de Pernambuco, São Paulo e '
            'Rio de Janeiro, e registra o que eles relatam sobre a escola, o futuro, o preconceito e a violência.')
    limits = ['Recorte de algumas escolas e estudantes; não é retrato estatístico da educação brasileira.',
              'Áreas potenciais são metadados editoriais; não constituem correspondência com dispositivo.']
    out.append(dict(
        ano=YEAR_DECISION_P21['value'], ano_decisao=YEAR_DECISION_P21, areas_potenciais=['educação', 'desigualdade', 'adolescência'],
        candidate_id=cid, candidate_number=2, criadores=['João Jardim'],
        evidencias=[evidence(wid, cid, 1, fact, 'DOCUMENTAR', 'ARGUMENTO_DOCUMENTAL', s3, limits)],
        fontes=[s3, s4, s5, s6], franquia=None,
        metadata_pendente=['Ano divergente entre fontes (2005/2006/2007); adotado 2005 por decisão registrada em ano_decisao.',
                           'Produtoras não transcritas: a única lista consultada (PLFD Dartmouth) traz grafia divergente; não corrigida por inferência.'],
        not_targeted_to_device=True, notas={}, objetos_juridicos_potenciais=['igualdade de condições de acesso e permanência na escola'],
        pais='Brasil', provenance=dict(batch='R1A', candidate_id=cid, ingestion_ready=True, ontology_changed=False),
        publisher_distribuidor_editora=[],
        resumo_factual_curto=fact, riscos=['Depoimentos de estudantes; não mede indicadores educacionais.'],
        status_catalogo='CANDIDATO_NAO_INTEGRADO', status_triagem='APTA', subtipo=None, tipo='DOCUMENTÁRIO',
        titulo='Pro Dia Nascer Feliz', titulo_informado='Pro Dia Nascer Feliz', titulo_original='Pro Dia Nascer Feliz', titulo_ptbr=None,
        titulo_internacional='For a Better Day',
        transposition_limits=limits, work_id=wid, required_by=dict(decision_id='REFERENCE_EXPANSION_01-P21', target_id='CF88:ART.206:INC.I')))
    for o in out:
        if not any('identidade' in f['supports'] for f in o['fontes']) or not o['criadores'] or not o['resumo_factual_curto']:
            raise SystemExit(f'IDENTITY_INCOMPLETE {o["work_id"]}')
    return out


def render():
    obras = records()
    doc = dict(catalogo=COLLECTION, status_catalogo='CANDIDATO_NAO_INTEGRADO',
               aviso='Identidade bibliográfica das duas obras retidas no REFERENCE_EXPANSION_01 (P20, P21). Mesmo esquema do CATALOGO_EXPANSAO_200; '
                     'não cria vínculo obra↔dispositivo; Engine não executada.',
               criterio_inclusao=['APTA', 'APTA_COM_RESSALVA'], fontes_dir=SRC.relative_to(ROOT).as_posix(),
               source_records_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SRC.glob('*.json'))},
               total_obras=len(obras), obras=obras)
    return (json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = render()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(OUT.name, hashlib.sha256(b).hexdigest())
