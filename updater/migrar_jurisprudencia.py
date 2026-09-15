from datetime import datetime
from pathlib import Path
import json
import shutil


ARQUIVO_CATALOGO = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_BACKUP = Path(
    "backup_catalogos"
)


def carregar_catalogo():
    if not ARQUIVO_CATALOGO.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_CATALOGO}"
        )

    texto = ARQUIVO_CATALOGO.read_text(
        encoding="utf-8"
    )

    dados = json.loads(texto)

    if not isinstance(dados, list):
        raise ValueError(
            "O catálogo de jurisprudência "
            "precisa conter uma lista JSON."
        )

    return dados


def criar_backup():
    PASTA_BACKUP.mkdir(
        parents=True,
        exist_ok=True,
    )

    data_hora = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    destino = (
        PASTA_BACKUP
        / (
            "catalogo_jurisprudencia_"
            f"{data_hora}.json"
        )
    )

    shutil.copy2(
        ARQUIVO_CATALOGO,
        destino,
    )

    return destino


def valor_status_padrao(registro):
    tipo = (
        registro
        .get("tipo", "")
        .lower()
        .strip()
    )

    # Súmula publicada já é considerada firmada.
    if tipo in {
        "sumula",
        "sumula_vinculante",
    }:
        return "julgado"

    # Como os repetitivos atuais do seu catálogo
    # já foram cadastrados como teses firmadas,
    # assumimos "julgado" para preservar o estado atual.
    if tipo in {
        "repetitivo",
        "repercussao_geral",
        "iac",
        "irr",
    }:
        return "julgado"

    return "julgado"


def migrar_registro(registro):
    alteracoes = []

    campos_padrao = {
        "status": valor_status_padrao(
            registro
        ),
        "processos": [],
        "data_afetacao": "",
        "data_julgamento": "",
        "data_publicacao": "",
        "url_fonte": "",
        "ultima_verificacao": "",
    }

    for campo, valor in campos_padrao.items():
        if campo not in registro:
            registro[campo] = valor
            alteracoes.append(campo)

    return alteracoes


def salvar_catalogo(catalogo):
    texto = json.dumps(
        catalogo,
        ensure_ascii=False,
        indent=2,
    )

    ARQUIVO_CATALOGO.write_text(
        texto + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main():
    print()
    print(
        "LEX MACHINA - MIGRAÇÃO DE JURISPRUDÊNCIA"
    )
    print(
        "========================================"
    )
    print()

    catalogo = carregar_catalogo()

    print(
        f"Registros encontrados: {len(catalogo)}"
    )

    backup = criar_backup()

    print(
        f"Backup criado em: {backup}"
    )

    print()

    total_alterados = 0
    total_campos = 0

    for indice, registro in enumerate(
        catalogo,
        start=1,
    ):
        if not isinstance(registro, dict):
            print(
                f"[{indice}] Registro inválido. Ignorado."
            )
            continue

        alteracoes = migrar_registro(
            registro
        )

        if alteracoes:
            total_alterados += 1
            total_campos += len(
                alteracoes
            )

            tribunal = registro.get(
                "tribunal",
                "?"
            )

            tipo = registro.get(
                "tipo",
                "?"
            )

            numero = registro.get(
                "numero",
                "?"
            )

            print(
                f"[{indice}] "
                f"{tribunal} {tipo} {numero}"
            )

            print(
                "  Campos adicionados: "
                + ", ".join(
                    alteracoes
                )
            )

        else:
            print(
                f"[{indice}] "
                "Nenhuma alteração necessária."
            )

    salvar_catalogo(
        catalogo
    )

    print()
    print(
        "========================================"
    )
    print(
        "MIGRAÇÃO CONCLUÍDA"
    )
    print(
        f"Registros analisados: {len(catalogo)}"
    )
    print(
        f"Registros alterados: {total_alterados}"
    )
    print(
        f"Campos adicionados: {total_campos}"
    )
    print()
    print(
        "O catálogo atualizado foi salvo em:"
    )
    print(
        ARQUIVO_CATALOGO
    )
    print()
    print(
        "O arquivo original foi preservado "
        "na pasta backup_catalogos."
    )


if __name__ == "__main__":
    main()