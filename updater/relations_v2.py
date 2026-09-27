from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import re
from typing import Any


VERSAO_RELATIONS_V2 = "2.0.0-infra"
CATALOGO_MESTRE_PADRAO = Path("catalogo_mestre_vademecum.json")
PASTA_SAIDA_PADRAO = Path("saida")
PASTA_V2_NOME = "99_RELATIONS_V2"

SUBPASTAS_V2 = (
    "01_RELACOES_GLOBAIS",
    "02_JURISPRUDENCIA",
    "03_HISTORICO_NORMATIVO",
    "04_FONTES",
    "99_AUDITORIA",
)

ID_RE = re.compile(r"^[A-Z][A-Z0-9_\-]{1,31}$")


@dataclass(frozen=True)
class NormaGlobal:
    id: str
    ramo: str
    nome: str
    prioridade: str
    tipo: str
    fonte_oficial: str
    pasta_destino: str
    arquivo_sugerido: str


class ErroRelationsV2(RuntimeError):
    pass


def carregar_catalogo(caminho: Path) -> dict[str, Any]:
    if not caminho.exists():
        raise ErroRelationsV2(f"Catálogo mestre não encontrado: {caminho}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ErroRelationsV2(f"Falha ao ler catálogo mestre: {exc}") from exc

    if not isinstance(dados, dict):
        raise ErroRelationsV2("Catálogo mestre deve ser um objeto JSON.")
    itens = dados.get("itens")
    if not isinstance(itens, list):
        raise ErroRelationsV2("Catálogo mestre não possui lista 'itens'.")
    return dados


def normalizar_normas(catalogo: dict[str, Any]) -> tuple[list[NormaGlobal], list[str]]:
    normas: list[NormaGlobal] = []
    erros: list[str] = []
    ids: set[str] = set()

    for pos, item in enumerate(catalogo.get("itens", []), start=1):
        if not isinstance(item, dict):
            erros.append(f"Item {pos}: registro não é objeto JSON.")
            continue

        identificador = str(item.get("id", "")).strip()
        if not identificador:
            erros.append(f"Item {pos}: sem id.")
            continue
        if not ID_RE.fullmatch(identificador):
            erros.append(f"{identificador}: id fora do padrão global.")
            continue
        if identificador in ids:
            erros.append(f"{identificador}: id duplicado.")
            continue
        ids.add(identificador)

        campos_obrigatorios = (
            "nome",
            "fonte_oficial",
            "pasta_destino",
        )
        ausentes = [
            campo
            for campo in campos_obrigatorios
            if not str(item.get(campo, "")).strip()
        ]
        if ausentes:
            erros.append(
                f"{identificador}: campos obrigatórios vazios: "
                + ", ".join(ausentes)
            )
            continue

        normas.append(
            NormaGlobal(
                id=identificador,
                ramo=str(item.get("ramo", "")).strip(),
                nome=str(item.get("nome", "")).strip(),
                prioridade=str(item.get("prioridade", "")).strip(),
                tipo=str(item.get("tipo", "")).strip(),
                fonte_oficial=str(item.get("fonte_oficial", "")).strip(),
                pasta_destino=str(item.get("pasta_destino", "")).strip(),
                arquivo_sugerido=str(item.get("arquivo_sugerido", "")).strip(),
            )
        )

    return normas, erros


def ler_contagem_artigos(indice: Path) -> dict[str, int]:
    contagens: dict[str, int] = {}
    if not indice.exists():
        return contagens

    try:
        for linha in indice.read_text(encoding="utf-8", errors="replace").splitlines():
            partes = linha.split("|")
            if len(partes) < 4:
                continue
            norma_id = partes[0].strip()
            if norma_id and ID_RE.fullmatch(norma_id):
                contagens[norma_id] = contagens.get(norma_id, 0) + 1
    except OSError:
        return {}
    return contagens


def escrever_json(caminho: Path, dados: Any) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def escrever_texto(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def preparar_estrutura(
    catalogo_path: Path,
    saida_raiz: Path,
) -> dict[str, Any]:
    catalogo = carregar_catalogo(catalogo_path)
    normas, erros = normalizar_normas(catalogo)

    pasta_v2 = saida_raiz / PASTA_V2_NOME
    for sub in SUBPASTAS_V2:
        (pasta_v2 / sub).mkdir(parents=True, exist_ok=True)

    indice_artigos = saida_raiz / "LEXDATA_V4_BUILD" / "ARTIGOS.IDX"
    contagens_artigos = ler_contagem_artigos(indice_artigos)

    gerado_em = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    catalogo_global = {
        "schema": "lex-machina-relations-v2/catalogo-normas/1",
        "versao_relations_v2": VERSAO_RELATIONS_V2,
        "catalogo_mestre_versao": str(catalogo.get("versao", "")),
        "gerado_em": gerado_em,
        "total_normas": len(normas),
        "normas": [
            {
                **asdict(norma),
                "artigos_indexados_lexdata_v4": contagens_artigos.get(norma.id),
            }
            for norma in normas
        ],
    }

    escrever_json(
        pasta_v2 / "04_FONTES" / "CATALOGO_NORMAS_GLOBAL.json",
        catalogo_global,
    )

    # Arquivos vazios, mas já com schema definido. Eles serão preenchidos nas
    # próximas etapas sem alterar o formato básico lido pelo firmware futuro.
    escrever_json(
        pasta_v2 / "01_RELACOES_GLOBAIS" / "RELACOES_GLOBAIS.json",
        {
            "schema": "lex-machina-relations-v2/relacoes/1",
            "versao_relations_v2": VERSAO_RELATIONS_V2,
            "gerado_em": gerado_em,
            "total": 0,
            "relacoes": [],
        },
    )
    escrever_json(
        pasta_v2 / "02_JURISPRUDENCIA" / "JURISPRUDENCIA_GLOBAL.json",
        {
            "schema": "lex-machina-relations-v2/jurisprudencia/1",
            "versao_relations_v2": VERSAO_RELATIONS_V2,
            "gerado_em": gerado_em,
            "total": 0,
            "registros": [],
        },
    )
    escrever_json(
        pasta_v2 / "03_HISTORICO_NORMATIVO" / "HISTORICO_NORMATIVO.json",
        {
            "schema": "lex-machina-relations-v2/historico/1",
            "versao_relations_v2": VERSAO_RELATIONS_V2,
            "gerado_em": gerado_em,
            "total": 0,
            "registros": [],
        },
    )

    ids = {n.id for n in normas}
    testes_obrigatorios = {
        "CF88_presente": "CF88" in ids,
        "CDC1990_presente": "CDC1990" in ids,
        "CPC2015_presente": "CPC2015" in ids,
        "catalogo_72_normas": len(normas) == 72,
        "ids_unicos": len(ids) == len(normas),
        "sem_erros_catalogo": not erros,
    }

    status = "OK" if all(testes_obrigatorios.values()) else "FALHA"
    auditoria = {
        "schema": "lex-machina-relations-v2/auditoria-infra/1",
        "versao_relations_v2": VERSAO_RELATIONS_V2,
        "gerado_em": gerado_em,
        "status": status,
        "catalogo_mestre": str(catalogo_path),
        "catalogo_mestre_versao": str(catalogo.get("versao", "")),
        "total_itens_catalogo_original": len(catalogo.get("itens", [])),
        "total_normas_globais_validas": len(normas),
        "total_ids_unicos": len(ids),
        "indice_artigos_encontrado": indice_artigos.exists(),
        "normas_com_contagem_artigos": len(contagens_artigos),
        "total_dispositivos_indexados": sum(contagens_artigos.values()),
        "testes_obrigatorios": testes_obrigatorios,
        "erros": erros,
        "proxima_etapa": (
            "Extrair referências legislativas expressas da Constituição "
            "e gerar relações diretas/reversas auditáveis."
        ),
    }

    escrever_json(
        pasta_v2 / "99_AUDITORIA" / "AUDITORIA_INFRAESTRUTURA.json",
        auditoria,
    )

    linhas = [
        "LEX MACHINA - RELATIONS V2",
        "AUDITORIA DE INFRAESTRUTURA",
        "=" * 60,
        f"Status: {status}",
        f"Versão V2: {VERSAO_RELATIONS_V2}",
        f"Catálogo mestre: {catalogo_path}",
        f"Versão catálogo mestre: {catalogo.get('versao', '')}",
        f"Normas globais válidas: {len(normas)}",
        f"IDs únicos: {len(ids)}",
        f"Índice ARTIGOS.IDX encontrado: {'SIM' if indice_artigos.exists() else 'NÃO'}",
        f"Normas com artigos indexados: {len(contagens_artigos)}",
        f"Dispositivos indexados detectados: {sum(contagens_artigos.values())}",
        "",
        "TESTES OBRIGATÓRIOS",
    ]
    for nome, ok in testes_obrigatorios.items():
        linhas.append(f"[{'OK' if ok else 'FALHA'}] {nome}")

    if erros:
        linhas.extend(["", "ERROS"])
        linhas.extend(f"- {erro}" for erro in erros)

    linhas.extend(
        [
            "",
            "SEGURANÇA",
            "- A V1 não foi apagada nem modificada.",
            "- O firmware não foi alterado.",
            "- Nenhuma consulta à internet é feita por este estágio.",
            "- A V2 é gerada em pasta paralela.",
            "",
            "PRÓXIMA ETAPA",
            "Extrair referências legislativas expressas da Constituição e",
            "gerar relações diretas/reversas auditáveis, começando por CF art. 103.",
        ]
    )
    escrever_texto(
        pasta_v2 / "99_AUDITORIA" / "AUDITORIA_INFRAESTRUTURA.txt",
        "\n".join(linhas) + "\n",
    )

    manifesto = "LEX MACHINA - RELATIONS V2\n\n"
    manifesto += "Esta árvore é paralela à 99_RELATIONS_V1.\n"
    manifesto += "Nesta etapa ela apenas estabelece schemas, catálogo global e auditoria.\n"
    manifesto += "Nenhum dado V1 é removido e o firmware atual continua usando V1.\n\n"
    manifesto += "Pastas:\n"
    manifesto += "01_RELACOES_GLOBAIS - relações legislativas entre dispositivos/normas\n"
    manifesto += "02_JURISPRUDENCIA - índice jurisprudencial global futuro\n"
    manifesto += "03_HISTORICO_NORMATIVO - alterações, redações e histórico normativo\n"
    manifesto += "04_FONTES - catálogo e rastreabilidade das fontes\n"
    manifesto += "99_AUDITORIA - cobertura, pendências e testes\n"
    escrever_texto(pasta_v2 / "LEIA-ME_RELATIONS_V2.txt", manifesto)

    return auditoria


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cria e audita a infraestrutura segura da RELATIONS V2."
    )
    parser.add_argument(
        "--catalogo",
        type=Path,
        default=CATALOGO_MESTRE_PADRAO,
        help="Caminho do catalogo_mestre_vademecum.json",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=PASTA_SAIDA_PADRAO,
        help="Raiz de saída do updater (padrão: saida)",
    )
    return parser.parse_args()


def main() -> int:
    args = argumentos()
    try:
        auditoria = preparar_estrutura(args.catalogo, args.saida)
    except ErroRelationsV2 as exc:
        print(f"ERRO RELATIONS V2: {exc}")
        return 2

    print()
    print("LEX MACHINA - RELATIONS V2")
    print("=" * 60)
    print(f"Status: {auditoria['status']}")
    print(f"Normas globais válidas: {auditoria['total_normas_globais_validas']}")
    print(f"Dispositivos indexados detectados: {auditoria['total_dispositivos_indexados']}")
    print(f"Saída: {args.saida / PASTA_V2_NOME}")
    print()
    print("A V1 não foi modificada.")
    return 0 if auditoria["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
