from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
OLD_PATH = ROOT / "LEX_MACHINA_REFERENCIAS_ENGINE_V1_2" / "data" / "CATALOGO_SEMANTICO_OBRAS.json"
NEW_PATH = ROOT / "LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2" / "DNA_SEMANTICO_45_APROVADO.json"
DECISIONS_PATH = ROOT / "LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2" / "DECISOES_HUMANAS_45.json"
CF_PATH = ROOT / "CF_SEGMENTADA_V2" / "CF_DISPOSITIVOS_LIMPOS.json"
BENCH_PATH = ROOT / "LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2" / "BENCHMARK_HUMANO_REFERENCIAS_CF_TOTAL.json"
ANALYZER_PATH = ROOT / "LEX_MACHINA_REFERENCIAS_ENGINE_V1_2" / "engine" / "analyzer.py"
V132_RUNNER_PATH = ROOT / "LEX_MACHINA_REFERENCIAS_ENGINE_V1_3_2" / "engine" / "run_v132.py"

CANONICAL_FIELDS = [
    "id", "titulo", "titulo_original", "tipo", "ano", "origem",
    "temas_centrais", "temas_fortes", "temas_secundarios",
    "objetos_juridicos_compativeis", "objetos_juridicos_fracos",
    "contextos_narrativos", "bens_juridicos_relacionados", "areas_prioritarias",
    "risco_generalizacao", "alertas_editoriais", "travas_editoriais",
    "potencial_interdisciplinar", "origem_catalogo", "versao_dna", "status_humano",
]

ENGINE_FIELDS = [
    "id", "nome", "tipo", "ano", "resumo", "temas", "conceitos_sociais",
    "conceitos_juridicos", "dominios_juridicos", "ambientes_contextos",
    "forca_por_tema", "tipos_relacao_possivel", "riscos_transposicao",
    "contexto_nacional", "natureza_obra", "valor_pedagogico",
    "observacoes_editoriais", "mecanica_central", "escolha_do_jogador",
    "experiencia_emergente", "tema_invariante", "tema_dependente_da_partida",
]
ENGINE_REQUIRED_DIRECT = ["id", "nome", "tipo", "ano", "resumo", "contexto_nacional", "natureza_obra", "valor_pedagogico"]

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def empty(value):
    return value in (None, "", "NAO_INFORMADO", [], {})

def type_names(values):
    names = set()
    for value in values:
        if value is None: names.add("null")
        elif isinstance(value, bool): names.add("boolean")
        elif isinstance(value, int): names.add("integer")
        elif isinstance(value, float): names.add("number")
        elif isinstance(value, str): names.add("string")
        elif isinstance(value, list): names.add("array")
        elif isinstance(value, dict): names.add("object")
        else: names.add(type(value).__name__)
    return sorted(names)

def canonical_old(raw):
    # Os campos sem classificação de força permanecem em extensões explícitas;
    # não são promovidos artificialmente a CENTRAL/FORTE/SECUNDÁRIO.
    return {
        "schema": "REFERENCIA_CANONICA_V1",
        "id": raw["id"], "titulo": raw["nome"], "titulo_original": None,
        "tipo": raw["tipo"], "ano": raw["ano"], "origem": "NAO_INFORMADO",
        "temas_centrais": [], "temas_fortes": [], "temas_secundarios": [],
        "objetos_juridicos_compativeis": list(raw.get("conceitos_juridicos", [])),
        "objetos_juridicos_fracos": [],
        "contextos_narrativos": list(raw.get("ambientes_contextos", [])),
        "bens_juridicos_relacionados": [], "areas_prioritarias": {},
        "risco_generalizacao": "NAO_INFORMADO",
        "alertas_editoriais": list(raw.get("riscos_transposicao", [])),
        "travas_editoriais": [], "potencial_interdisciplinar": [],
        "origem_catalogo": "CATALOGO_24_ORIGINAL", "versao_dna": "HISTORICO_PRE_V2",
        "status_humano": "NAO_INFORMADO",
        "extensoes_origem": {
            "temas_sem_classificacao": list(raw.get("temas", [])),
            "conceitos_sociais": list(raw.get("conceitos_sociais", [])),
            "dominios_juridicos_sem_classificacao": list(raw.get("dominios_juridicos", [])),
            "forca_por_tema_historica": dict(raw.get("forca_por_tema", {})),
            "tipos_relacao_possivel": list(raw.get("tipos_relacao_possivel", [])),
            "contexto_nacional": raw.get("contexto_nacional"),
            "natureza_obra": raw.get("natureza_obra"),
            "valor_pedagogico_historico": raw.get("valor_pedagogico"),
            "observacoes_editoriais": raw.get("observacoes_editoriais", ""),
            "mecanica_central": list(raw.get("mecanica_central", [])),
            "escolha_do_jogador": list(raw.get("escolha_do_jogador", [])),
            "experiencia_emergente": list(raw.get("experiencia_emergente", [])),
            "tema_invariante": list(raw.get("tema_invariante", [])),
            "tema_dependente_da_partida": list(raw.get("tema_dependente_da_partida", [])),
        },
        "registro_origem_integral": raw,
    }

def canonical_new(raw):
    return {
        "schema": "REFERENCIA_CANONICA_V1",
        "id": raw["id"], "titulo": raw["titulo"], "titulo_original": raw["titulo_original"],
        "tipo": raw["tipo"], "ano": raw["ano"], "origem": raw["origem_geografica"],
        "temas_centrais": list(raw["temas_centrais"]), "temas_fortes": list(raw["temas_fortes"]),
        "temas_secundarios": list(raw["temas_secundarios"]),
        "objetos_juridicos_compativeis": list(raw["objetos_juridicos_compativeis"]),
        "objetos_juridicos_fracos": list(raw["objetos_juridicos_fracos"]),
        "contextos_narrativos": list(raw["contextos_narrativos"]),
        "bens_juridicos_relacionados": list(raw["bens_juridicos_relacionados"]),
        "areas_prioritarias": dict(raw["areas_constitucionais_prioritarias"]),
        "risco_generalizacao": raw["risco_de_generalizacao"],
        "alertas_editoriais": list(raw["alertas_editoriais"]),
        "travas_editoriais": list(raw["travas_editoriais"]),
        "potencial_interdisciplinar": list(raw["potencial_interdisciplinar"]),
        "origem_catalogo": "LOTE_45_V2_APROVADO", "versao_dna": raw["versao_dna"],
        "status_humano": raw["status_humano"],
        "extensoes_origem": {
            "autor_diretor_criador_desenvolvedora": raw["autor_diretor_criador_desenvolvedora"],
            "descricao_factual": raw["descricao_factual"], "fonte_verificacao": raw["fonte_verificacao"],
            "incompatibilidades_explicitas": list(raw["incompatibilidades_explicitas"]),
            "normalizacoes_editoriais": list(raw["normalizacoes_editoriais"]),
            "por_que_foi_escolhida": raw["por_que_foi_escolhida"],
            "obras_atuais_que_complementa_ou_substitui": list(raw["obras_atuais_que_complementa_ou_substitui"]),
            "ajuste_dna_material": raw["ajuste_dna_material"],
        },
        "registro_origem_integral": raw,
    }

def trace(raw, canonical, origin):
    transformed = {
        "CATALOGO_24_ORIGINAL": {
            "nome":"titulo", "conceitos_juridicos":"objetos_juridicos_compativeis",
            "ambientes_contextos":"contextos_narrativos", "riscos_transposicao":"alertas_editoriais",
        },
        "LOTE_45_V2_APROVADO": {
            "titulo":"titulo", "titulo_original":"titulo_original", "origem_geografica":"origem",
            "areas_constitucionais_prioritarias":"areas_prioritarias",
            "risco_de_generalizacao":"risco_generalizacao",
        },
    }[origin]
    return {
        "id_origem": raw["id"], "id_canonico": canonical["id"], "origem_catalogo": origin,
        "campos_origem": sorted(raw), "campos_transformados": transformed,
        "campos_vazios": [field for field in CANONICAL_FIELDS if empty(canonical[field])],
        "travas_preservadas": canonical["travas_editoriais"],
        "reversivel_por_registro_origem_integral": canonical["registro_origem_integral"] == raw,
    }

def engine_map_new(canonical):
    # Somente mapeamento estrutural explícito. Os dois campos numéricos sem fonte
    # não são fabricados; por isso estes registros ficam em obras_bloqueadas.
    ext = canonical["extensoes_origem"]
    themes = canonical["temas_centrais"] + canonical["temas_fortes"] + canonical["temas_secundarios"]
    return {
        "id": canonical["id"], "nome": canonical["titulo"], "tipo": canonical["tipo"],
        "ano": canonical["ano"], "resumo": ext["descricao_factual"], "temas": themes,
        "conceitos_sociais": [], "conceitos_juridicos": canonical["objetos_juridicos_compativeis"],
        "dominios_juridicos": list(canonical["areas_prioritarias"]),
        "ambientes_contextos": canonical["contextos_narrativos"], "forca_por_tema": {},
        "tipos_relacao_possivel": [],
        "riscos_transposicao": canonical["alertas_editoriais"] + canonical["travas_editoriais"],
        "contexto_nacional": "NAO_INFORMADO", "natureza_obra": "NAO_INFORMADO",
        "valor_pedagogico": None,
        "observacoes_editoriais": " | ".join(canonical["travas_editoriais"] + canonical["alertas_editoriais"]),
        "mecanica_central": [], "escolha_do_jogador": [], "experiencia_emergente": [],
        "tema_invariante": [], "tema_dependente_da_partida": [],
        "bloqueios_contrato_engine": [
            "valor_pedagogico numérico obrigatório sem fonte no DNA aprovado",
            "forca_por_tema numérica não pode ser derivada de CENTRAL/FORTE/SECUNDARIO",
            "contexto_nacional e natureza_obra não possuem equivalentes canônicos diretos aprovados",
        ],
    }

def inventory(old, new):
    fields = sorted(set().union(*(set(x) for x in old), *(set(x) for x in new)))
    direct = {
        "id":"id", "nome":"titulo", "titulo":"titulo", "tipo":"tipo", "ano":"ano",
        "titulo_original":"titulo_original", "origem_geografica":"origem",
        "temas_centrais":"temas_centrais", "temas_fortes":"temas_fortes", "temas_secundarios":"temas_secundarios",
        "conceitos_juridicos":"objetos_juridicos_compativeis",
        "objetos_juridicos_compativeis":"objetos_juridicos_compativeis",
        "objetos_juridicos_fracos":"objetos_juridicos_fracos",
        "ambientes_contextos":"contextos_narrativos", "contextos_narrativos":"contextos_narrativos",
        "bens_juridicos_relacionados":"bens_juridicos_relacionados",
        "areas_constitucionais_prioritarias":"areas_prioritarias",
        "risco_de_generalizacao":"risco_generalizacao", "riscos_transposicao":"alertas_editoriais",
        "alertas_editoriais":"alertas_editoriais", "travas_editoriais":"travas_editoriais",
        "potencial_interdisciplinar":"potencial_interdisciplinar", "versao_dna":"versao_dna",
        "status_humano":"status_humano",
    }
    rows=[]
    for field in fields:
        ov=[x[field] for x in old if field in x]; nv=[x[field] for x in new if field in x]
        equivalent=direct.get(field)
        rows.append({
            "campo":field, "existe_24":bool(ov), "existe_45":bool(nv),
            "tipos_24":type_names(ov), "tipos_45":type_names(nv),
            "obrigatorio_24":len(ov)==len(old), "obrigatorio_45":len(nv)==len(new),
            "equivalente_canonico":equivalent, "conversao_direta":equivalent is not None,
            "risco_perda":"NENHUM_REGISTRO_ORIGEM_PRESERVADO" if equivalent else "PRESERVADO_EM_EXTENSOES_OU_REGISTRO_ORIGEM",
        })
    return rows

def main():
    old_doc=load(OLD_PATH); new_doc=load(NEW_PATH); decisions=load(DECISIONS_PATH)
    old=old_doc["obras"]; new=new_doc["obras"]
    assert len(old)==24 and len(new)==45 and len(decisions["decisoes"])==45
    canonical=[canonical_old(x) for x in old]+[canonical_new(x) for x in new]
    assert len(canonical)==69 and len({x["id"] for x in canonical})==69
    hom=[x for x in canonical if x["titulo"].casefold()=="o processo"]
    assert {(x["id"],x["tipo"],x["ano"]) for x in hom}=={("REF-LIV-0002","LIVRO",1925),("EXP-DOC-005","DOCUMENTÁRIO",2018)}
    traces=[trace(raw,can,"CATALOGO_24_ORIGINAL") for raw,can in zip(old,canonical[:24])]
    traces += [trace(raw,can,"LOTE_45_V2_APROVADO") for raw,can in zip(new,canonical[24:])]
    assert all(x["reversivel_por_registro_origem_integral"] for x in traces)

    audit_rows=inventory(old,new)
    analyzer=ANALYZER_PATH.read_text(encoding="utf-8")
    v132=V132_RUNNER_PATH.read_text(encoding="utf-8")
    audit={
        "schema":"AUDITORIA_ESQUEMAS_24_45_V1", "campos":audit_rows,
        "campos_uniao_24":sorted(set().union(*(set(x) for x in old))),
        "campos_uniao_45":sorted(set().union(*(set(x) for x in new))),
        "campos_canonicos":CANONICAL_FIELDS,
        "contrato_engine_historico":{
            "leitor":"LEX_MACHINA_REFERENCIAS_ENGINE_V1_2/engine/analyzer.py::DeterministicSemanticAnalyzer.analyze_work",
            "campos_lidos":ENGINE_FIELDS, "campos_obrigatorios_acesso_direto":ENGINE_REQUIRED_DIRECT,
            "campos_com_default":sorted(set(ENGINE_FIELDS)-set(ENGINE_REQUIRED_DIRECT)),
            "normalizacoes":["ano -> int","valor_pedagogico -> float","valores forca_por_tema -> float","listas -> tuple"],
            "campos_ignorados":"qualquer campo fora de ENGINE_FIELDS",
            "hash_analyzer":sha(ANALYZER_PATH),
        },
        "contrato_v132":{
            "le_catalogo_obras":False,
            "entrada_real":"RESULTADO_BENCHMARK_V131.json e AMOSTRA_CF_V131.json",
            "evidencia":"run_v132.py não contém analyze_work nem CATALOGO_SEMANTICO_OBRAS",
            "hash_runner":sha(V132_RUNNER_PATH),
            "confirmacao_textual":("CATALOGO_SEMANTICO_OBRAS" not in v132 and "analyze_work" not in v132 and "RESULTADO_BENCHMARK_V131.json" in v132),
        },
        "bloqueios_45":["valor_pedagogico numérico ausente","forca_por_tema numérica ausente","contexto_nacional sem equivalente direto","natureza_obra sem equivalente direto"],
        "politica":"Nenhum peso ou inferência nova foi criado.",
    }
    dump(BASE/"AUDITORIA_ESQUEMAS_24_45.json",audit)
    dump(BASE/"CATALOGO_69_CANONICO.json",{
        "schema":"REFERENCIA_CANONICA_V1","total":69,"ids_unicos":69,"duplicatas_reais":0,
        "homonimos_legitimos":[{"titulo":"O Processo","ids":["REF-LIV-0002","EXP-DOC-005"]}],
        "fontes_sha256":{"catalogo_24":sha(OLD_PATH),"dna_45":sha(NEW_PATH),"decisoes_45":sha(DECISIONS_PATH)},
        "obras":canonical,
    })
    dump(BASE/"RASTREABILIDADE_ADAPTACAO_69.json",{
        "schema":"RASTREABILIDADE_ADAPTACAO_69_V1","total":69,"registros":traces,
        "campos_vazios_24_total":sum(len(x["campos_vazios"]) for x in traces[:24]),
        "campos_vazios_45_total":sum(len(x["campos_vazios"]) for x in traces[24:]),
        "campos_vazios_24_distintos":sorted(set().union(*(set(x["campos_vazios"]) for x in traces[:24]))),
        "campos_vazios_45_distintos":sorted(set().union(*(set(x["campos_vazios"]) for x in traces[24:]))),
    })

    # Retrocompatibilidade máxima: cópia byte a byte da entrada histórica.
    (BASE/"CATALOGO_24_INPUT_ENGINE_V132_ADAPTADO.json").write_bytes(OLD_PATH.read_bytes())
    blocked=[engine_map_new(x) for x in canonical[24:]]
    dump(BASE/"CATALOGO_69_INPUT_ENGINE_V132.json",{
        "schema":"INPUT_ENGINE_V132_PREPARADO_MAS_BLOQUEADO_V1",
        "status_compatibilidade":"BLOQUEADO_POR_CAMPOS_NUMERICOS_SEM_FONTE",
        "engine_executavel":False, "engine_executada":False,
        "motivo":"A v1.3.2 não lê catálogo diretamente; o leitor histórico exige valor_pedagogico numérico. Criá-lo ou converter faixas em números introduziria pesos proibidos.",
        "contrato_historico_campos":ENGINE_FIELDS,
        "obras_historicas_compativeis":old,
        "obras_novas_mapeadas_bloqueadas":blocked,
        "total_previsto":69,"total_compativel_sem_inferencia":24,"total_bloqueado":45,
    })

    direct_count=len({row["equivalente_canonico"] for row in audit_rows if row["conversao_direta"]})
    empty24=sum(len(x["campos_vazios"]) for x in traces[:24]); empty45=sum(len(x["campos_vazios"]) for x in traces[24:])
    report=f"""# Adaptador determinístico do catálogo de 69 obras

## Resultado

O adaptador normalizou 24 obras históricas e 45 obras aprovadas para `REFERENCIA_CANONICA_V1`, com 69 IDs únicos, reversibilidade integral e preservação do homônimo `O Processo`.

## Esquemas

- **Esquema A — 24 antigas:** {len(audit['campos_uniao_24'])} campos históricos; inclui temas sem faixas, `forca_por_tema` numérica e `valor_pedagogico` numérico.
- **Esquema B — 45 novas:** {len(audit['campos_uniao_45'])} campos; distingue temas centrais/fortes/secundários, objetos compatíveis/fracos, áreas categóricas, alertas e travas.
- **REFERENCIA_CANONICA_V1:** {len(CANONICAL_FIELDS)} campos principais, extensões de origem e cópia integral do registro-fonte para reversibilidade.

Foram mapeados diretamente **{direct_count} campos canônicos distintos**. Nas antigas houve **{empty24} ocorrências de campos vazios/default explícito**; nas novas, **{empty45}**. Nenhum conteúdo foi inventado e nenhuma informação de origem foi perdida, pois `registro_origem_integral` preserva cada registro byte-semanticamente.

## Contrato real da Engine

A v1.3.2 é calibradora: recebe resultados da v1.3.1 e não lê catálogo de obras. O leitor histórico aplicável está na v1.2 (`DeterministicSemanticAnalyzer.analyze_work`). Ele lê {len(ENGINE_FIELDS)} campos e acessa diretamente {len(ENGINE_REQUIRED_DIRECT)} deles. Converte `ano`, `valor_pedagogico` e `forca_por_tema` em números.

As 45 novas não possuem `valor_pedagogico` numérico nem `forca_por_tema` numérica. Converter `CENTRAL/FORTE/SECUNDARIO` em números ou escolher um valor pedagógico violaria a proibição de pesos ocultos. Por isso, `CATALOGO_69_INPUT_ENGINE_V132.json` é um artefato de preflight marcado `engine_executavel=false`, com 24 registros compatíveis e 45 bloqueados de forma explícita.

## Retrocompatibilidade das 24

`CATALOGO_24_INPUT_ENGINE_V132_ADAPTADO.json` é cópia byte a byte da entrada histórica. SHA-256 original e adaptado: `{sha(OLD_PATH)}`. Não há diferença estrutural ou semântica.

## Determinismo e preservação

O script ordena chaves, usa ordem fixa das fontes e não contém relógio, aleatoriedade ou rede. A validação executa o adaptador duas vezes e exige hashes idênticos. Engine, benchmark, CF segmentada e arquivos-fonte permanecem somente leitura.

## Recomendação

Os 69 registros estão prontos no esquema canônico, mas **não estão prontos para scoring da Engine**. Antes da execução comparativa, é necessária uma decisão humana/versionada sobre os campos numéricos exigidos pelo leitor histórico, ou um contrato de entrada novo em versão futura da Engine. Nenhuma dessas decisões deve ser introduzida silenciosamente pelo adaptador.
"""
    (BASE/"RELATORIO_ADAPTADOR_CATALOGO_69.md").write_text(report,encoding="utf-8")

if __name__ == "__main__":
    main()
