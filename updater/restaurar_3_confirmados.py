from datetime import datetime
from pathlib import Path
import argparse
import shutil
import sys


# ============================================================
# LEX MACHINA - RESTAURAÇÃO SEGURA DOS 3 ARQUIVOS
# CONFIRMADAMENTE TRUNCADOS
#
# RESTAURA APENAS:
# - Constituição Federal
# - Código Civil
# - ECA
#
# NÃO TOCA EM NENHUMA OUTRA NORMA.
#
# O script procura o MAIOR backup compatível encontrado em
# backup_catalogos, cria uma cópia de segurança do arquivo
# atual truncado e só então restaura o backup completo.
# ============================================================


BACKUP_ROOT = Path("backup_catalogos")
QUARENTENA_ROOT = Path("backup_saida")

ALVOS = {
    "CF88": {
        "relativo": Path(
            "1- CONSTITUIÇÃO FEDERAL"
        ) / "cf.txt",
        "min_backup_bytes": 500_000,
    },
    "CC2002": {
        "relativo": Path(
            "2- CÓDIGO CIVIL"
        ) / "codigo_civil_ lei10.406 2002.txt",
        "min_backup_bytes": 500_000,
    },
    "ECA1990": {
        "relativo": Path(
            "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE"
        ) / (
            "Estatuto da Criança e do Adolescente "
            "(Lei nº 8.069 1990).txt"
        ),
        "min_backup_bytes": 150_000,
    },
}


def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - restaura somente CF88, "
            "Código Civil e ECA a partir dos backups."
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Raiz do cartão. Exemplo: D:\\"
        ),
    )

    return parser.parse_args()


def encontrar_backups(relativo):
    encontrados = []

    if not BACKUP_ROOT.exists():
        return encontrados

    # Preferência 1: mesma estrutura relativa
    for pasta in BACKUP_ROOT.glob(
        "catalogo_mestre_*"
    ):
        candidato = pasta / relativo

        if (
            candidato.exists()
            and candidato.is_file()
        ):
            encontrados.append(
                candidato
            )

    # Preferência 2: mesmo nome de arquivo
    if not encontrados:
        nome = relativo.name.casefold()

        for candidato in BACKUP_ROOT.rglob(
            "*"
        ):
            if (
                candidato.is_file()
                and candidato.name.casefold()
                == nome
            ):
                encontrados.append(
                    candidato
                )

    return encontrados


def escolher_backup(
    relativo,
    minimo
):
    candidatos = encontrar_backups(
        relativo
    )

    validos = []

    for candidato in candidatos:
        try:
            tamanho = candidato.stat().st_size
        except OSError:
            continue

        if tamanho >= minimo:
            validos.append(
                (
                    tamanho,
                    candidato,
                )
            )

    if not validos:
        return None

    # Escolhemos o maior, e não simplesmente o mais recente,
    # para evitar selecionar por engano uma cópia já truncada.
    validos.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return validos[0][1]


def main():
    args = argumentos()

    origem = Path(
        args.origem
    )

    if (
        not origem.exists()
        or not origem.is_dir()
    ):
        raise FileNotFoundError(
            f"Origem inválida: {origem}"
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    quarentena = (
        QUARENTENA_ROOT
        / (
            "antes_restauracao_"
            + timestamp
        )
    )

    print()
    print(
        "LEX MACHINA - RESTAURAÇÃO SEGURA"
    )
    print(
        "=" * 64
    )
    print(
        "Serão restaurados SOMENTE:"
    )
    print(
        "- Constituição Federal"
    )
    print(
        "- Código Civil"
    )
    print(
        "- ECA"
    )
    print()

    restaurados = 0
    falhas = 0

    for identificador, dados in (
        ALVOS.items()
    ):
        relativo = dados[
            "relativo"
        ]

        atual = (
            origem
            / relativo
        )

        print(
            f"[{identificador}]"
        )
        print(
            f"  Atual: {atual}"
        )

        if not atual.exists():
            print(
                "  ERRO: arquivo atual não encontrado."
            )
            falhas += 1
            print()
            continue

        backup = escolher_backup(
            relativo,
            dados[
                "min_backup_bytes"
            ],
        )

        if backup is None:
            print(
                "  ERRO: nenhum backup completo "
                "compatível foi encontrado."
            )
            falhas += 1
            print()
            continue

        tamanho_atual = (
            atual.stat().st_size
        )

        tamanho_backup = (
            backup.stat().st_size
        )

        print(
            f"  Tamanho atual: {tamanho_atual} bytes"
        )
        print(
            f"  Backup escolhido: {backup}"
        )
        print(
            f"  Tamanho backup: {tamanho_backup} bytes"
        )

        # Guarda o arquivo atual truncado fora do cartão.
        destino_quarentena = (
            quarentena
            / relativo
        )

        destino_quarentena.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            atual,
            destino_quarentena,
        )

        # Restaura o backup completo.
        shutil.copy2(
            backup,
            atual,
        )

        tamanho_final = (
            atual.stat().st_size
        )

        if tamanho_final != tamanho_backup:
            print(
                "  ERRO: tamanho final diferente "
                "do backup. Restauração não confirmada."
            )
            falhas += 1
            print()
            continue

        restaurados += 1

        print(
            f"  OK: restaurado com {tamanho_final} bytes."
        )
        print(
            "  Cópia do arquivo truncado guardada em:"
        )
        print(
            f"  {destino_quarentena}"
        )
        print()

    print(
        "=" * 64
    )
    print(
        "RESTAURAÇÃO FINALIZADA"
    )
    print(
        f"Restaurados: {restaurados}"
    )
    print(
        f"Falhas: {falhas}"
    )
    print()

    if falhas == 0:
        print(
            "Os 3 arquivos confirmadamente truncados "
            "foram restaurados."
        )
    else:
        print(
            "Há falhas. Não prossiga com atualização "
            "automática nem com o índice ESP32."
        )


if __name__ == "__main__":
    try:
        main()

    except Exception as erro:
        print()
        print(
            "ERRO FATAL:"
        )
        print(
            erro
        )
        sys.exit(
            1
        )
