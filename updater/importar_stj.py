from datetime import datetime
from pathlib import Path
import json
import re
import shutil


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO_CLASSE_A = Path(
    "saida/99_INDICES/STJ_CLASSE_A_CONSUMIDOR_DIRETO.json"
)

CATALOGO = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_BACKUP = Path(
    "backup_catalogos"
)

PASTA_RELATORIO = Path(
    "saida/99_INDICES"
)


# ============================================================
# CARREGAMENTO JSON
# ============================================================

def carregar_json(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    return json.loads(
        caminho.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# BACKUP
# ============================================================

def criar_backup():
    PASTA_BACKUP.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    destino = (
        PASTA_BACKUP
        / (
            "catalogo_jurisprudencia_"
            f"antes_importacao_stj_{timestamp}.json"
        )
    )

    shutil.copy2(
        CATALOGO,
        destino,
    )

    return destino


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def limpar_texto(texto):
    texto = str(
        texto or ""
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


# ============================================================
# NOME DO TEMA
# ============================================================

def gerar_titulo(item):
    assuntos = limpar_texto(
        item.get(
            "assuntos",
            "",
        )
    )

    if assuntos:
        if len(
            assuntos
        ) <= 180:
            return assuntos

        return (
            assuntos[:177].rstrip()
            + "..."
        )

    questao = limpar_texto(
        item.get(
            "questao_oficial",
            "",
        )
    )

    if questao:
        primeira_frase = re.split(
            r"(?<=[.!?])\s+",
            questao,
        )[0]

        if len(
            primeira_frase
        ) <= 180:
            return primeira_frase

        return (
            primeira_frase[:177].rstrip()
            + "..."
        )

    return (
        "Tema Repetitivo "
        f"{item['numero']}"
    )


# ============================================================
# NOME DO ARQUIVO
# ============================================================

def gerar_nome_arquivo(numero):
    return (
        f"stj_tema_{numero}.txt"
    )


# ============================================================
# STATUS INTERNO
# ============================================================

def converter_status(
    status_oficial
):
    texto = limpar_texto(
        status_oficial
    ).casefold()

    if (
        "cancelado"
        in texto
        or "cancelada"
        in texto
    ):
        return "cancelado"

    if (
        "superado"
        in texto
        or "superada"
        in texto
    ):
        return "superado"

    pendentes = [
        "afetado",
        "aguardando julgamento",
        "pendente de julgamento",
        "em julgamento",
    ]

    if any(
        termo in texto
        for termo in pendentes
    ):
        return "pendente"

    julgados = [
        "trânsito em julgado",
        "transito em julgado",
        "acórdão publicado",
        "acordao publicado",
        "julgado",
    ]

    if any(
        termo in texto
        for termo in julgados
    ):
        return "julgado"

    # O status oficial continua armazenado
    # mesmo quando não conseguimos traduzi-lo.
    return "julgado"


# ============================================================
# DATA
# ============================================================

def converter_data(
    valor
):
    valor = limpar_texto(
        valor
    )

    if not valor:
        return ""

    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
    ]

    for formato in formatos:
        try:
            data = datetime.strptime(
                valor,
                formato,
            )

            return data.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue

    return valor


# ============================================================
# NÚMEROS JÁ EXISTENTES
# ============================================================

def indices_existentes(
    catalogo
):
    numeros = set()

    for registro in catalogo:
        if (
            registro.get(
                "tribunal"
            ) == "STJ"
            and registro.get(
                "tipo"
            ) == "repetitivo"
        ):
            try:
                numeros.add(
                    int(
                        registro[
                            "numero"
                        ]
                    )
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

    return numeros


# ============================================================
# CONSTRUÇÃO DO REGISTRO
# ============================================================

def construir_registro(
    item
):
    numero = int(
        item[
            "numero"
        ]
    )

    tese = limpar_texto(
        item.get(
            "tese_oficial",
            "",
        )
    )

    questao = limpar_texto(
        item.get(
            "questao_oficial",
            "",
        )
    )

    if tese:
        texto_base = tese
    elif questao:
        texto_base = questao
    else:
        texto_base = (
            "Tema Repetitivo "
            f"{numero}"
        )

    status_oficial = limpar_texto(
        item.get(
            "situacao",
            "",
        )
    )

    processos = item.get(
        "processos",
        [],
    )

    if not isinstance(
        processos,
        list,
    ):
        processos = []

    processos = [
        limpar_texto(
            processo
        )
        for processo in processos
        if limpar_texto(
            processo
        )
    ]

    registro = {
        "tribunal": "STJ",

        "tipo": "repetitivo",

        "numero": numero,

        "status": converter_status(
            status_oficial
        ),

        "tema": gerar_titulo(
            item
        ),

        "arquivo": gerar_nome_arquivo(
            numero
        ),

        "pasta_destino": (
            "19_JURISPRUDENCIA/STJ/REPETITIVOS"
        ),

        "texto": texto_base,

        "texto_oficial_verificado": (
            tese
        ),

        "questao_oficial_verificada": (
            questao
        ),

        "relacionado_a": [],

        "fonte": (
            "Superior Tribunal de Justiça - "
            f"Tema Repetitivo {numero}"
        ),

        "url_fonte": limpar_texto(
            item.get(
                "url_oficial",
                "",
            )
        ),

        "url_verificacao": limpar_texto(
            item.get(
                "url_oficial",
                "",
            )
        ),

        "status_oficial_stj": (
            status_oficial
        ),

        "ultima_verificacao": (
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        ),

        "processos": processos,

        "data_afetacao": converter_data(
            item.get(
                "data_primeira_afetacao",
                "",
            )
        ),

        "data_julgamento": converter_data(
            item.get(
                "data_julgamento",
                "",
            )
        ),

        "data_publicacao": "",

        "orgao_julgador": limpar_texto(
            item.get(
                "orgao_julgador",
                "",
            )
        ),

        "assuntos_stj": limpar_texto(
            item.get(
                "assuntos",
                "",
            )
        ),

        "referencia_legislativa_stj": (
            limpar_texto(
                item.get(
                    "referencia_legislativa",
                    "",
                )
            )
        ),

        "referencia_sumular_stj": (
            limpar_texto(
                item.get(
                    "referencia_sumular",
                    "",
                )
            )
        ),

        "informacoes_complementares_stj": (
            limpar_texto(
                item.get(
                    "informacoes_complementares",
                    "",
                )
            )
        ),

        "sequencial_precedente_stj": (
            limpar_texto(
                item.get(
                    "sequencial_precedente",
                    "",
                )
            )
        ),

        "classe_triagem": (
            item.get(
                "classe_triagem",
                "A",
            )
        ),

        "origem_importacao": (
            "DESCUBERTA_AUTOMATICA_STJ"
        ),
    }

    return registro


# ============================================================
# RELATÓRIO
# ============================================================

def gerar_relatorio(
    backup,
    total_classe_a,
    importados,
    duplicados,
    falhas,
):
    PASTA_RELATORIO.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_RELATORIO
        / "RELATORIO_IMPORTACAO_STJ.txt"
    )

    linhas = [
        "LEX MACHINA",
        "IMPORTAÇÃO AUTOMÁTICA - STJ",
        "=" * 72,
        "",
        (
            "DATA: "
            + datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        ),
        "",
        (
            "BACKUP DO CATÁLOGO: "
            f"{backup}"
        ),
        "",
        (
            "REGISTROS CLASSE A RECEBIDOS: "
            f"{total_classe_a}"
        ),
        (
            "IMPORTADOS: "
            f"{len(importados)}"
        ),
        (
            "DUPLICADOS IGNORADOS: "
            f"{len(duplicados)}"
        ),
        (
            "FALHAS: "
            f"{len(falhas)}"
        ),
        "",
    ]

    if importados:
        linhas.extend(
            [
                "=" * 72,
                "IMPORTADOS",
                "=" * 72,
                "",
            ]
        )

        for numero in importados:
            linhas.append(
                f"- Tema {numero}"
            )

        linhas.append("")

    if duplicados:
        linhas.extend(
            [
                "=" * 72,
                "DUPLICADOS IGNORADOS",
                "=" * 72,
                "",
            ]
        )

        for numero in duplicados:
            linhas.append(
                f"- Tema {numero}"
            )

        linhas.append("")

    if falhas:
        linhas.extend(
            [
                "=" * 72,
                "FALHAS",
                "=" * 72,
                "",
            ]
        )

        for falha in falhas:
            linhas.append(
                f"- {falha}"
            )

    caminho.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print(
        "LEX MACHINA - IMPORTAÇÃO STJ"
    )
    print(
        "=" * 50
    )
    print()

    # --------------------------------------------------------
    # CARREGAR CLASSE A
    # --------------------------------------------------------

    dados_classe_a = carregar_json(
        ARQUIVO_CLASSE_A
    )

    itens = dados_classe_a.get(
        "itens",
        [],
    )

    if not isinstance(
        itens,
        list,
    ):
        raise ValueError(
            "O arquivo da Classe A "
            "não contém uma lista válida."
        )

    print(
        "Registros Classe A recebidos: "
        f"{len(itens)}"
    )

    # --------------------------------------------------------
    # CARREGAR CATÁLOGO
    # --------------------------------------------------------

    catalogo = carregar_json(
        CATALOGO
    )

    if not isinstance(
        catalogo,
        list,
    ):
        raise ValueError(
            "catalogo_jurisprudencia.json "
            "precisa conter uma lista."
        )

    print(
        "Registros atuais no catálogo: "
        f"{len(catalogo)}"
    )

    # --------------------------------------------------------
    # BACKUP
    # --------------------------------------------------------

    backup = criar_backup()

    print(
        f"Backup criado: {backup}"
    )

    # --------------------------------------------------------
    # DUPLICIDADES
    # --------------------------------------------------------

    existentes = indices_existentes(
        catalogo
    )

    importados = []
    duplicados = []
    falhas = []

    # --------------------------------------------------------
    # IMPORTAÇÃO
    # --------------------------------------------------------

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        try:
            numero = int(
                item[
                    "numero"
                ]
            )

            print(
                f"[{indice}/{len(itens)}] "
                f"Tema {numero}"
            )

            if numero in existentes:
                print(
                    "  DUPLICADO - ignorado"
                )

                duplicados.append(
                    numero
                )

                continue

            registro = (
                construir_registro(
                    item
                )
            )

            catalogo.append(
                registro
            )

            existentes.add(
                numero
            )

            importados.append(
                numero
            )

            print(
                "  IMPORTADO"
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as erro:
            falhas.append(
                f"Registro {indice}: {erro}"
            )

            print(
                f"  ERRO: {erro}"
            )

    # --------------------------------------------------------
    # ORDENAÇÃO
    # --------------------------------------------------------

    def chave_ordenacao(
        registro
    ):
        tribunal = str(
            registro.get(
                "tribunal",
                "",
            )
        )

        tipo = str(
            registro.get(
                "tipo",
                "",
            )
        )

        try:
            numero = int(
                registro.get(
                    "numero",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            numero = 0

        return (
            tribunal,
            tipo,
            numero,
        )

    catalogo.sort(
        key=chave_ordenacao
    )

    # --------------------------------------------------------
    # SALVAR CATÁLOGO
    # --------------------------------------------------------

    CATALOGO.write_text(
        json.dumps(
            catalogo,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    relatorio = gerar_relatorio(
        backup,
        len(itens),
        importados,
        duplicados,
        falhas,
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()
    print(
        "=" * 50
    )

    print(
        "IMPORTAÇÃO FINALIZADA"
    )

    print(
        f"Classe A recebidos: "
        f"{len(itens)}"
    )

    print(
        f"Importados: "
        f"{len(importados)}"
    )

    print(
        f"Duplicados ignorados: "
        f"{len(duplicados)}"
    )

    print(
        f"Falhas: "
        f"{len(falhas)}"
    )

    print()

    print(
        "Registros finais no catálogo: "
        f"{len(catalogo)}"
    )

    print()

    print(
        f"Relatório: {relatorio}"
    )

    print()

    if falhas:
        print(
            "ATENÇÃO:"
        )

        print(
            "Houve falhas. Consulte o relatório "
            "antes de continuar."
        )

    else:
        print(
            "Importação concluída sem falhas."
        )


if __name__ == "__main__":
    main()