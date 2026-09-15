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

PASTA_JURISPRUDENCIA = Path(
    "saida/19_JURISPRUDENCIA"
)

PASTA_BACKUP = Path(
    "backup_saida"
)

PASTA_INDICES = Path(
    "saida/99_INDICES"
)

RELATORIO = (
    PASTA_INDICES
    / "RELATORIO_SANEAMENTO_SAIDA.txt"
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def timestamp():
    return datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


def limpar_texto(
    texto
):
    return str(
        texto or ""
    ).strip()


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


# ============================================================
# STATUS
# ============================================================

def status_normalizado(
    item
):
    status = limpar_texto(
        item.get(
            "status",
            ""
        )
    ).casefold()

    if status in {
        "julgado",
        "pendente",
        "sobrestado",
        "cancelado",
        "superado",
    }:
        return status

    oficial = limpar_texto(
        item.get(
            "status_oficial_stj",
            ""
        )
    ).casefold()

    if "cancelad" in oficial:
        return "cancelado"

    if "superad" in oficial:
        return "superado"

    if "sobrestad" in oficial:
        return "sobrestado"

    if (
        "afetad" in oficial
        or "em julgamento" in oficial
    ):
        return "pendente"

    if (
        "transito em julgado" in oficial
        or "trânsito em julgado" in oficial
        or "acordao publicado" in oficial
        or "acórdão publicado" in oficial
    ):
        return "julgado"

    return status


# ============================================================
# PASTA CORRETA
# ============================================================

def pasta_status(
    item
):
    tipo = limpar_texto(
        item.get(
            "tipo",
            ""
        )
    ).casefold()

    if tipo in {
        "sumula",
        "súmula",
    }:
        return "SUMULAS"

    status = status_normalizado(
        item
    )

    mapa = {
        "julgado": "JULGADOS",
        "pendente": "PENDENTES",
        "sobrestado": "SOBRESTADOS",
        "cancelado": "CANCELADOS",
        "superado": "SUPERADOS",
    }

    return mapa.get(
        status
    )


# ============================================================
# CAMINHO ESPERADO
# ============================================================

def caminho_esperado(
    item
):
    tribunal = limpar_texto(
        item.get(
            "tribunal",
            ""
        )
    )

    tipo = limpar_texto(
        item.get(
            "tipo",
            ""
        )
    ).casefold()

    arquivo = limpar_texto(
        item.get(
            "arquivo",
            ""
        )
    )

    if not (
        tribunal
        and arquivo
    ):
        return None

    if tipo in {
        "sumula",
        "súmula",
    }:
        return (
            PASTA_JURISPRUDENCIA
            / tribunal
            / "SUMULAS"
            / arquivo
        )

    pasta = pasta_status(
        item
    )

    if not pasta:
        return None

    return (
        PASTA_JURISPRUDENCIA
        / tribunal
        / "REPETITIVOS"
        / pasta
        / arquivo
    )


# ============================================================
# LOCALIZAR TODAS AS CÓPIAS
# ============================================================

def localizar_copias(
    nome_arquivo
):
    if not nome_arquivo:
        return []

    return [
        caminho
        for caminho
        in PASTA_JURISPRUDENCIA.rglob(
            nome_arquivo
        )
        if caminho.is_file()
    ]


# ============================================================
# BACKUP
# ============================================================

def copiar_para_backup(
    origem,
    raiz_backup
):
    relativo = origem.relative_to(
        Path(".")
    )

    destino = (
        raiz_backup
        / relativo
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        origem,
        destino,
    )

    return destino


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "LEX MACHINA - "
        "SANEAMENTO DA SAÍDA"
    )

    print(
        "=" * 60
    )

    print()

    catalogo = carregar_catalogo()

    raiz_backup = (
        PASTA_BACKUP
        / (
            "saneamento_"
            + timestamp()
        )
    )

    raiz_backup.mkdir(
        parents=True,
        exist_ok=True,
    )

    removidos = []
    ignorados = []
    problemas = []

    # ========================================================
    # ANALISAR CATÁLOGO
    # ========================================================

    for item in catalogo:

        tribunal = limpar_texto(
            item.get(
                "tribunal",
                ""
            )
        )

        tipo = limpar_texto(
            item.get(
                "tipo",
                ""
            )
        )

        numero = item.get(
            "numero"
        )

        arquivo = limpar_texto(
            item.get(
                "arquivo",
                ""
            )
        )

        if not (
            tribunal
            and tipo
            and arquivo
        ):
            continue

        esperado = caminho_esperado(
            item
        )

        if esperado is None:
            continue

        copias = localizar_copias(
            arquivo
        )

        # ----------------------------------------------------
        # SEM DUPLICIDADE
        # ----------------------------------------------------

        if len(
            copias
        ) <= 1:
            continue

        identificador = (
            f"{tribunal} "
            f"{tipo} "
            f"{numero}"
        )

        print()
        print(
            f"Duplicidade detectada: "
            f"{identificador}"
        )

        print(
            f"Arquivo: {arquivo}"
        )

        # ----------------------------------------------------
        # SEGURANÇA:
        # A CÓPIA CORRETA PRECISA EXISTIR.
        # ----------------------------------------------------

        esperado_resolvido = (
            esperado.resolve()
        )

        copia_correta = None

        for copia in copias:

            if (
                copia.resolve()
                == esperado_resolvido
            ):
                copia_correta = copia
                break

        if copia_correta is None:

            mensagem = (
                f"{identificador}: "
                "há duplicidade, mas a cópia "
                "na pasta esperada não existe. "
                "Nada foi alterado."
            )

            problemas.append(
                mensagem
            )

            print(
                "  ATENÇÃO:"
            )

            print(
                "  A cópia correta não foi "
                "encontrada."
            )

            continue

        print(
            "  Cópia correta:"
        )

        print(
            f"  {copia_correta}"
        )

        # ----------------------------------------------------
        # REMOVER SOMENTE CÓPIAS EXTRAS
        # ----------------------------------------------------

        for copia in copias:

            if (
                copia.resolve()
                == esperado_resolvido
            ):
                continue

            print(
                "  Cópia antiga:"
            )

            print(
                f"  {copia}"
            )

            # -----------------------------------------------
            # BACKUP DA CÓPIA ANTIGA
            # -----------------------------------------------

            destino_backup = (
                copiar_para_backup(
                    copia,
                    raiz_backup,
                )
            )

            print(
                "  Backup:"
            )

            print(
                f"  {destino_backup}"
            )

            # -----------------------------------------------
            # EXCLUI CÓPIA ANTIGA
            # -----------------------------------------------

            copia.unlink()

            removidos.append(
                {
                    "registro": identificador,
                    "arquivo": str(
                        copia
                    ),
                    "backup": str(
                        destino_backup
                    ),
                    "mantido": str(
                        copia_correta
                    ),
                }
            )

            print(
                "  Cópia antiga removida."
            )

    # ========================================================
    # RELATÓRIO
    # ========================================================

    PASTA_INDICES.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = [
        "LEX MACHINA",
        "SANEAMENTO DA SAÍDA",
        "=" * 78,
        "",
        f"EXECUTADO EM: {agora()}",
        "",
        (
            "BACKUP DAS CÓPIAS ANTIGAS: "
            f"{raiz_backup}"
        ),
        "",
        (
            "CÓPIAS ANTIGAS REMOVIDAS: "
            f"{len(removidos)}"
        ),
        (
            "PROBLEMAS: "
            f"{len(problemas)}"
        ),
        "",
    ]

    if removidos:

        linhas.extend(
            [
                "=" * 78,
                "ARQUIVOS SANEADOS",
                "=" * 78,
                "",
            ]
        )

        for item in removidos:

            linhas.extend(
                [
                    item[
                        "registro"
                    ],
                    (
                        "REMOVIDO: "
                        f"{item['arquivo']}"
                    ),
                    (
                        "BACKUP: "
                        f"{item['backup']}"
                    ),
                    (
                        "MANTIDO: "
                        f"{item['mantido']}"
                    ),
                    "",
                    "-" * 78,
                    "",
                ]
            )

    if problemas:

        linhas.extend(
            [
                "=" * 78,
                "PROBLEMAS",
                "=" * 78,
                "",
            ]
        )

        for problema in problemas:

            linhas.append(
                f"- {problema}"
            )

    RELATORIO.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    # ========================================================
    # RESUMO
    # ========================================================

    print()
    print(
        "=" * 60
    )

    print(
        "SANEAMENTO FINALIZADO"
    )

    print()

    print(
        "Cópias antigas removidas: "
        f"{len(removidos)}"
    )

    print(
        "Problemas encontrados: "
        f"{len(problemas)}"
    )

    print()

    print(
        f"Backup: "
        f"{raiz_backup}"
    )

    print(
        f"Relatório: "
        f"{RELATORIO}"
    )

    print()

    if not problemas:

        print(
            "✓ Saneamento concluído "
            "com segurança."
        )

        print()

        print(
            "As cópias corretas foram "
            "preservadas nas pastas de status."
        )

    else:

        print(
            "⚠ Houve situações que exigem "
            "análise antes de continuar."
        )


if __name__ == "__main__":
    main()