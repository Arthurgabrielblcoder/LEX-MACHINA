from datetime import datetime
from pathlib import Path
import json
import shutil


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_BACKUP = Path(
    "backup_catalogos"
)

PASTA_SAIDA = Path(
    "saida/99_INDICES"
)

RELATORIO = (
    PASTA_SAIDA
    / "RELATORIO_RESOLUCAO_AUDITORIA_STJ.txt"
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def hoje():
    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


# ============================================================
# CATÁLOGO
# ============================================================

def carregar_catalogo():
    if not CATALOGO.exists():
        raise FileNotFoundError(
            f"Catálogo não encontrado: {CATALOGO}"
        )

    dados = json.loads(
        CATALOGO.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        dados,
        list,
    ):
        raise ValueError(
            "catalogo_jurisprudencia.json "
            "precisa conter uma lista."
        )

    return dados


def salvar_catalogo(
    catalogo
):
    CATALOGO.write_text(
        json.dumps(
            catalogo,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
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
            f"antes_resolucao_auditoria_{timestamp}.json"
        )
    )

    shutil.copy2(
        CATALOGO,
        destino,
    )

    return destino


# ============================================================
# LOCALIZAR TEMA
# ============================================================

def localizar_tema(
    catalogo,
    numero
):
    for registro in catalogo:

        if (
            registro.get("tribunal") == "STJ"
            and registro.get("tipo") == "repetitivo"
        ):

            try:
                numero_registro = int(
                    registro.get(
                        "numero"
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if numero_registro == numero:
                return registro

    return None


# ============================================================
# RESOLVER TEMA 1016
# ============================================================

def resolver_tema_1016(
    catalogo
):
    registro = localizar_tema(
        catalogo,
        1016,
    )

    if registro is None:
        return {
            "sucesso": False,
            "mensagem": (
                "Tema 1016 não encontrado."
            ),
        }

    tese_oficial = str(
        registro.get(
            "texto_oficial_verificado",
            "",
        )
        or ""
    ).strip()

    if not tese_oficial:
        return {
            "sucesso": False,
            "mensagem": (
                "Tema 1016 encontrado, "
                "mas não possui "
                "texto_oficial_verificado."
            ),
        }

    # --------------------------------------------------------
    # NÃO APAGA O TEXTO ORIGINAL.
    # --------------------------------------------------------

    registro[
        "status"
    ] = "julgado"

    registro[
        "status_oficial_stj"
    ] = (
        "Acórdão Publicado - RE Pendente"
    )

    registro[
        "resultado_ultima_verificacao_stj"
    ] = "verificado"

    registro[
        "fonte_texto_preferencial"
    ] = (
        "texto_oficial_verificado"
    )

    registro[
        "usar_tese_oficial"
    ] = True

    registro[
        "observacao_verificacao"
    ] = (
        "O texto local anterior divergia da tese "
        "oficial atualmente publicada pelo STJ. "
        "O texto original foi preservado. "
        "Para exibição jurídica, deve prevalecer "
        "texto_oficial_verificado."
    )

    registro[
        "resolucao_auditoria"
    ] = (
        "Divergência resolvida pela adoção "
        "da tese oficial verificada do STJ."
    )

    registro[
        "data_resolucao_auditoria"
    ] = hoje()

    return {
        "sucesso": True,
        "mensagem": (
            "Tema 1016: divergência resolvida. "
            "Tese oficial marcada como "
            "fonte preferencial."
        ),
    }


# ============================================================
# RESOLVER TEMA 954
# ============================================================

def resolver_tema_954(
    catalogo
):
    registro = localizar_tema(
        catalogo,
        954,
    )

    if registro is None:
        return {
            "sucesso": False,
            "mensagem": (
                "Tema 954 não encontrado."
            ),
        }

    registro[
        "status"
    ] = "sobrestado"

    registro[
        "status_oficial_stj"
    ] = "Sobrestado"

    registro[
        "resultado_ultima_verificacao_stj"
    ] = (
        "pendente"
    )

    registro[
        "usar_tese_oficial"
    ] = False

    registro[
        "observacao_verificacao"
    ] = (
        "Tema atualmente sobrestado no STJ. "
        "Não deve ser tratado como erro ou "
        "inconclusivo. A questão submetida "
        "permanece disponível para consulta."
    )

    registro[
        "resolucao_auditoria"
    ] = (
        "Inconclusão resolvida: "
        "Tema classificado como sobrestado."
    )

    registro[
        "data_resolucao_auditoria"
    ] = hoje()

    return {
        "sucesso": True,
        "mensagem": (
            "Tema 954: classificado "
            "corretamente como SOBRESTADO."
        ),
    }


# ============================================================
# CONTAGEM FINAL
# ============================================================

def classificar_final(
    registro
):
    resultado = str(
        registro.get(
            "resultado_ultima_verificacao_stj",
            "",
        )
        or ""
    ).casefold()

    status = str(
        registro.get(
            "status",
            "",
        )
        or ""
    ).casefold()

    if status == "cancelado":
        return "cancelado"

    if status == "superado":
        return "superado"

    if status == "sobrestado":
        return "sobrestado"

    if resultado == "verificado":
        return "confirmado"

    if (
        resultado == "pendente"
        or status == "pendente"
    ):
        return "pendente"

    if resultado == "divergencia":
        return "divergencia"

    if resultado == "inconclusivo":
        return "inconclusivo"

    return "outro"


def contar_resultados(
    catalogo
):
    contadores = {
        "confirmado": 0,
        "pendente": 0,
        "sobrestado": 0,
        "cancelado": 0,
        "superado": 0,
        "divergencia": 0,
        "inconclusivo": 0,
        "outro": 0,
    }

    for registro in catalogo:

        if not (
            registro.get("tribunal") == "STJ"
            and registro.get("tipo") == "repetitivo"
        ):
            continue

        categoria = classificar_final(
            registro
        )

        contadores[
            categoria
        ] += 1

    return contadores


# ============================================================
# RELATÓRIO
# ============================================================

def gerar_relatorio(
    backup,
    resultados,
    contadores
):
    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = [
        "LEX MACHINA",
        "RESOLUÇÃO DA AUDITORIA STJ",
        "=" * 72,
        "",
        f"DATA: {agora()}",
        "",
        f"BACKUP: {backup}",
        "",
        "=" * 72,
        "CASOS RESOLVIDOS",
        "=" * 72,
        "",
    ]

    for resultado in resultados:
        linhas.append(
            resultado[
                "mensagem"
            ]
        )

    linhas.extend(
        [
            "",
            "=" * 72,
            "RESULTADO FINAL",
            "=" * 72,
            "",
            (
                "CONFIRMADOS: "
                f"{contadores['confirmado']}"
            ),
            (
                "PENDENTES / AFETADOS: "
                f"{contadores['pendente']}"
            ),
            (
                "SOBRESTADOS: "
                f"{contadores['sobrestado']}"
            ),
            (
                "CANCELADOS: "
                f"{contadores['cancelado']}"
            ),
            (
                "SUPERADOS: "
                f"{contadores['superado']}"
            ),
            (
                "DIVERGÊNCIAS: "
                f"{contadores['divergencia']}"
            ),
            (
                "INCONCLUSIVOS: "
                f"{contadores['inconclusivo']}"
            ),
            (
                "OUTROS: "
                f"{contadores['outro']}"
            ),
            "",
            (
                "O campo 'texto' original "
                "não foi apagado."
            ),
            (
                "A tese oficial permanece em "
                "'texto_oficial_verificado'."
            ),
        ]
    )

    RELATORIO.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return RELATORIO


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "LEX MACHINA - "
        "RESOLUÇÃO DA AUDITORIA STJ"
    )
    print(
        "=" * 60
    )
    print()

    catalogo = carregar_catalogo()

    backup = criar_backup()

    print(
        f"Backup criado: {backup}"
    )

    print()

    resultados = []

    # --------------------------------------------------------
    # TEMA 1016
    # --------------------------------------------------------

    resultado_1016 = (
        resolver_tema_1016(
            catalogo
        )
    )

    resultados.append(
        resultado_1016
    )

    print(
        resultado_1016[
            "mensagem"
        ]
    )

    # --------------------------------------------------------
    # TEMA 954
    # --------------------------------------------------------

    resultado_954 = (
        resolver_tema_954(
            catalogo
        )
    )

    resultados.append(
        resultado_954
    )

    print(
        resultado_954[
            "mensagem"
        ]
    )

    # --------------------------------------------------------
    # SEGURANÇA
    # --------------------------------------------------------

    falhas = [
        item
        for item in resultados
        if not item[
            "sucesso"
        ]
    ]

    if falhas:

        print()
        print(
            "ATENÇÃO:"
        )

        print(
            "Uma ou mais resoluções falharam."
        )

        print(
            "O catálogo NÃO será salvo."
        )

        return

    # --------------------------------------------------------
    # SALVAR
    # --------------------------------------------------------

    salvar_catalogo(
        catalogo
    )

    contadores = contar_resultados(
        catalogo
    )

    relatorio = gerar_relatorio(
        backup,
        resultados,
        contadores,
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "AUDITORIA RESOLVIDA"
    )

    print()

    print(
        "Confirmados: "
        f"{contadores['confirmado']}"
    )

    print(
        "Pendentes / afetados: "
        f"{contadores['pendente']}"
    )

    print(
        "Sobrestados: "
        f"{contadores['sobrestado']}"
    )

    print(
        "Cancelados: "
        f"{contadores['cancelado']}"
    )

    print(
        "Superados: "
        f"{contadores['superado']}"
    )

    print(
        "Divergências: "
        f"{contadores['divergencia']}"
    )

    print(
        "Inconclusivos: "
        f"{contadores['inconclusivo']}"
    )

    print(
        "Outros: "
        f"{contadores['outro']}"
    )

    print()

    print(
        f"Relatório: {relatorio}"
    )


if __name__ == "__main__":
    main()