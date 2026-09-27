"""Implantação segura dos artefatos jurídicos gerados no microSD.

Não formata, não remove arquivos e nunca copia a árvore ``saida`` inteira.
Os backups ficam no computador, em ``backup_sd``, e não no cartão.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PASTA_CDC = "9-CÓDIGO DE DEFESA DO CONSUMIDOR"
INDICE_JURIS = Path("99_INDICES/INDICE_JURISPRUDENCIA_CDC.txt")
INDICE_CORRELATAS = Path("99_RELATIONS_V1/01_CORRELATAS/INDICE_CORRELATAS.txt")
CATALOGOS_FINAIS = (
    Path("catalogo_jurisprudencia.json"),
    Path("catalogo_precedentes.json"),
    Path("catalogo_acordaos.json"),
)

INDICES_RELACOES_PERMITIDOS = {
    Path("LEIA-ME_CAMADAS_JURIDICAS.txt"),
    Path("01_SUMULAS/INDICE_SUMULAS.txt"),
    Path("02_SUMULAS_VINCULANTES/INDICE_SUMULAS_VINCULANTES.txt"),
    Path("02_ACORDAOS/INDICE_ACORDAOS.txt"),
    Path("03_PRECEDENTES/INDICE_PRECEDENTES.txt"),
    Path("03_PRECEDENTES_RELEVANTES/INDICE_PRECEDENTES_RELEVANTES.txt"),
    Path("05_RECURSOS_REPETITIVOS/INDICE_RECURSOS_REPETITIVOS.txt"),
}


class ErroImplantacao(RuntimeError):
    """Falha de segurança ou integridade da implantação."""


@dataclass(frozen=True)
class Copia:
    origem: Path
    destino: Path
    relativo_cartao: Path


def sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _raiz_windows(caminho: Path) -> str:
    return caminho.anchor.rstrip("\\/").upper()


def validar_destino(cartao: Path, *, exigir_removivel: bool = True) -> Path:
    cartao = cartao.expanduser().resolve(strict=True)
    if not cartao.is_dir():
        raise ErroImplantacao("O destino não é um diretório.")
    if exigir_removivel and cartao != Path(cartao.anchor).resolve():
        raise ErroImplantacao("Informe a raiz da unidade, por exemplo E:\\.")

    if os.name == "nt":
        unidade = _raiz_windows(cartao)
        sistema = os.environ.get("SystemDrive", "C:").rstrip("\\/").upper()
        if exigir_removivel and unidade == sistema:
            raise ErroImplantacao("A unidade do sistema nunca pode ser usada como destino.")
        if exigir_removivel:
            tipo = ctypes.windll.kernel32.GetDriveTypeW(str(cartao))
            if tipo != 2:  # DRIVE_REMOVABLE
                raise ErroImplantacao("O destino não foi reconhecido como unidade removível.")

    pasta_cdc = cartao / PASTA_CDC
    if not pasta_cdc.is_dir():
        raise ErroImplantacao(f"Marcador ausente no cartão: {PASTA_CDC}")

    leis_cdc = [
        p for p in pasta_cdc.rglob("*.txt")
        if "19_JURISPRUDENCIA" not in p.parts and "99_INDICES" not in p.parts
    ]
    outras_leis = [
        "1- CONSTITUIÇÃO FEDERAL",
        "2- CÓDIGO CIVIL",
        "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE",
    ]
    if not leis_cdc or not any((cartao / nome).is_dir() for nome in outras_leis):
        raise ErroImplantacao(
            "A estrutura não parece ser um cartão LEX MACHINA: legislação-base ausente."
        )
    return cartao


def arquivos_catalogados(saida: Path, catalogos_raiz: Path) -> set[Path]:
    """Resolve somente os TXT representados pelos catálogos finais atuais."""
    selecionados: set[Path] = set()
    destinos: dict[str, Path] = {}
    for catalogo_relativo in CATALOGOS_FINAIS:
        catalogo = catalogos_raiz / catalogo_relativo
        if not catalogo.is_file():
            raise ErroImplantacao(f"Catálogo final ausente: {catalogo}")
        try:
            registros = json.loads(catalogo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise ErroImplantacao(f"Catálogo final inválido: {catalogo}: {exc}") from exc
        if not isinstance(registros, list):
            raise ErroImplantacao(f"Catálogo final precisa conter uma lista: {catalogo}")

        for numero, registro in enumerate(registros, 1):
            if not isinstance(registro, dict):
                raise ErroImplantacao(f"Registro {numero} inválido em {catalogo}")
            arquivo = str(registro.get("arquivo", "")).strip()
            pasta_texto = str(registro.get("pasta_destino", "")).strip()
            pasta = Path(pasta_texto.replace("\\", "/").lstrip("/"))
            if (
                not arquivo.lower().endswith(".txt")
                or not pasta.parts
                or pasta.parts[0] != "19_JURISPRUDENCIA"
                or ".." in pasta.parts
                or Path(arquivo).name != arquivo
            ):
                raise ErroImplantacao(
                    f"Destino jurídico inseguro no registro {numero} de {catalogo}: "
                    f"{pasta_texto}/{arquivo}"
                )

            base = saida / pasta
            direto = base / arquivo
            candidatos = [direto] if direto.is_file() else list(base.rglob(arquivo))
            candidatos = sorted({p.resolve() for p in candidatos if p.is_file()})
            if len(candidatos) != 1:
                raise ErroImplantacao(
                    f"O catálogo exige uma origem única para {pasta}/{arquivo}; "
                    f"encontradas: {len(candidatos)}"
                )
            origem = candidatos[0]
            relativo = origem.relative_to(saida)
            chave = relativo.as_posix().casefold()
            anterior = destinos.get(chave)
            if anterior is not None and anterior != origem:
                raise ErroImplantacao(f"Destino jurídico duplicado: {relativo}")
            destinos[chave] = origem
            selecionados.add(origem)
    return selecionados


def auditar_orfaos(saida: Path, catalogos_raiz: Path) -> tuple[set[Path], set[Path]]:
    catalogados = arquivos_catalogados(saida, catalogos_raiz)
    existentes = {p.resolve() for p in (saida / "19_JURISPRUDENCIA").rglob("*.txt")}
    return catalogados, existentes - catalogados


def montar_plano(
    saida: Path,
    cartao: Path,
    catalogos_raiz: Path = Path("."),
) -> list[Copia]:
    saida = saida.resolve(strict=True)
    catalogos_raiz = catalogos_raiz.resolve(strict=True)
    plano: list[Copia] = []

    juris = saida / "19_JURISPRUDENCIA"
    indice = saida / INDICE_JURIS
    if not juris.is_dir() or not indice.is_file():
        raise ErroImplantacao(
            "Saída incompleta: faltam 19_JURISPRUDENCIA ou "
            "99_INDICES/INDICE_JURISPRUDENCIA_CDC.txt."
        )

    catalogados, _ = auditar_orfaos(saida, catalogos_raiz)
    for origem in sorted(catalogados):
        relativo = Path(PASTA_CDC) / origem.relative_to(saida)
        plano.append(Copia(origem, cartao / relativo, relativo))

    relativo_indice = Path(PASTA_CDC) / INDICE_JURIS
    plano.append(Copia(indice, cartao / relativo_indice, relativo_indice))

    raiz_relacoes = saida / "99_RELATIONS_V1"
    for relativo in sorted(INDICES_RELACOES_PERMITIDOS):
        origem = raiz_relacoes / relativo
        if origem.is_file():
            destino_relativo = Path("99_RELATIONS_V1") / relativo
            plano.append(Copia(origem, cartao / destino_relativo, destino_relativo))

    correlatas_origem = saida / INDICE_CORRELATAS
    if correlatas_origem.is_file():
        relativo = INDICE_CORRELATAS
        plano.append(Copia(correlatas_origem, cartao / relativo, relativo))

    if not plano:
        raise ErroImplantacao("Nenhum artefato permitido foi encontrado.")
    return plano


def _linhas_dados(caminho: Path):
    for linha in caminho.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith(("=", "#", "LEX MACHINA", "FORMATO:")):
            continue
        if "ARQUIVO" in linha.upper() and (
            "PASTA_DESTINO" in linha.upper() or linha.upper().startswith("REFER")
        ):
            continue
        yield linha


def _resolver_pasta_cdc(cartao: Path, valor: str) -> Path:
    relativo = Path(valor.strip().replace("\\", "/").lstrip("/"))
    partes = relativo.parts
    if partes and partes[0] == PASTA_CDC:
        return cartao / relativo
    return cartao / PASTA_CDC / relativo


def validar_referencias(cartao: Path, *, plano: list[Copia] | None = None) -> list[str]:
    erros: list[str] = []
    sobreposicoes = {item.destino: item.origem for item in (plano or [])}

    def existe(caminho: Path) -> bool:
        return caminho.is_file() or caminho in sobreposicoes

    def existe_na_arvore(pasta: Path, arquivo: str) -> bool:
        if plano is not None:
            return any(
                item.destino.name.casefold() == arquivo.casefold()
                and item.destino.is_relative_to(pasta)
                for item in plano
            )
        direto = pasta / arquivo
        if existe(direto):
            return True
        if pasta.is_dir() and any(pasta.rglob(arquivo)):
            return True
        return any(
            item.destino.name.casefold() == arquivo.casefold()
            and item.destino.is_relative_to(pasta)
            for item in (plano or [])
        )

    indice_juris = cartao / PASTA_CDC / INDICE_JURIS
    fonte_indice = sobreposicoes.get(indice_juris, indice_juris)
    if not fonte_indice.is_file():
        erros.append(f"Índice obrigatório ausente: {indice_juris}")
    else:
        nomes = {}
        raiz = cartao / PASTA_CDC / "19_JURISPRUDENCIA"
        for arquivo in raiz.rglob("*.txt") if raiz.exists() else []:
            nomes.setdefault(arquivo.name.casefold(), []).append(arquivo)
        for item in plano or []:
            if "19_JURISPRUDENCIA" in item.relativo_cartao.parts:
                nomes.setdefault(item.destino.name.casefold(), []).append(item.destino)
        for linha in _linhas_dados(fonte_indice):
            campos = linha.split("|")
            if len(campos) >= 6 and campos[0].upper().startswith("CDC ART."):
                nome = campos[5].strip().casefold()
                if plano is not None:
                    encontrado = any(
                        item.destino.name.casefold() == nome
                        and "19_JURISPRUDENCIA" in item.relativo_cartao.parts
                        for item in plano
                    )
                else:
                    encontrado = bool(nomes.get(nome))
                if not encontrado:
                    erros.append(f"Jurisprudência referenciada ausente: {campos[5].strip()}")

    for relativo in INDICES_RELACOES_PERMITIDOS:
        indice_rel = cartao / "99_RELATIONS_V1" / relativo
        fonte = sobreposicoes.get(indice_rel, indice_rel)
        if not fonte.is_file() or relativo.name == "LEIA-ME_CAMADAS_JURIDICAS.txt":
            continue
        for linha in _linhas_dados(fonte):
            campos = linha.split("|")
            if len(campos) < 4:
                continue
            arquivo, pasta = campos[-2].strip(), campos[-1].strip()
            pasta_destino = _resolver_pasta_cdc(cartao, pasta)
            if not existe_na_arvore(pasta_destino, arquivo):
                erros.append(f"Arquivo de índice ausente: {pasta_destino / arquivo}")

    correlatas = cartao / INDICE_CORRELATAS
    fonte_correlatas = sobreposicoes.get(correlatas, correlatas)
    if not fonte_correlatas.is_file():
        erros.append(f"Índice de correlatas ausente: {correlatas}")
    else:
        for linha in _linhas_dados(fonte_correlatas):
            campos = linha.split("|")
            if len(campos) < 4 or not campos[0].upper().startswith("CDC ART."):
                continue
            pasta = cartao / campos[3].strip().replace("\\", "/").lstrip("/")
            if not pasta.is_dir() or not any(pasta.glob("*.txt")):
                erros.append(f"Pasta correlata sem TXT: {pasta}")
    return sorted(set(erros))


def copiar_atomicamente(origem: Path, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(f".{destino.name}.lex-novo")
    try:
        with origem.open("rb") as entrada, temporario.open("wb") as saida:
            shutil.copyfileobj(entrada, saida, 1024 * 1024)
            saida.flush()
            os.fsync(saida.fileno())
        if sha256(temporario) != sha256(origem):
            raise ErroImplantacao(f"Hash divergente ao gravar {destino}")
        os.replace(temporario, destino)
        if sha256(destino) != sha256(origem):
            raise ErroImplantacao(f"Hash divergente após substituir {destino}")
    finally:
        temporario.unlink(missing_ok=True)


def executar(plano: list[Copia], backup_raiz: Path) -> tuple[int, int, Path | None]:
    alterados = 0
    inalterados = 0
    pasta_backup: Path | None = None
    for item in plano:
        if item.destino.is_file() and sha256(item.destino) == sha256(item.origem):
            inalterados += 1
            continue
        if item.destino.exists() and not item.destino.is_file():
            raise ErroImplantacao(f"O destino deveria ser arquivo: {item.destino}")
        if item.destino.is_file():
            if pasta_backup is None:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                pasta_backup = backup_raiz / f"microSD_{stamp}"
            backup = pasta_backup / item.relativo_cartao
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item.destino, backup)
        copiar_atomicamente(item.origem, item.destino)
        alterados += 1
    return alterados, inalterados, pasta_backup


def argumentos(argv=None):
    parser = argparse.ArgumentParser(description="Implanta somente dados gerados no microSD LEX MACHINA.")
    parser.add_argument("cartao", help="Raiz/letra da unidade removível, por exemplo E:\\")
    parser.add_argument("--dry-run", action="store_true", help="Valida e mostra o plano sem escrever.")
    parser.add_argument("--saida", type=Path, default=Path("saida"), help="Saída gerada pelo updater.")
    parser.add_argument("--backup", type=Path, default=Path("backup_sd"), help="Diretório local dos backups.")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = argumentos(argv)
    try:
        cartao = validar_destino(Path(args.cartao))
        plano = montar_plano(args.saida, cartao)
        catalogados, orfaos = auditar_orfaos(args.saida.resolve(), Path(".").resolve())
        erros_previos = validar_referencias(cartao, plano=plano)
        print(f"Cartão validado: {cartao}")
        print(f"Arquivos permitidos no plano: {len(plano)}")
        print(f"TXT jurídicos catalogados: {len(catalogados)}")
        print(f"TXT órfãos ignorados: {len(orfaos)}")
        for item in plano:
            acao = "ATUALIZAR" if item.destino.exists() else "CRIAR"
            print(f"{acao}: /{item.relativo_cartao.as_posix()}")
        if erros_previos:
            print("\nPendências detectadas:")
            for erro in erros_previos:
                print(f"- {erro}")
        if args.dry_run:
            print("\nDRY-RUN: nenhum arquivo foi alterado.")
            return 2 if erros_previos else 0
        if erros_previos:
            raise ErroImplantacao("A implantação foi bloqueada pelas pendências acima.")

        alterados, inalterados, backup = executar(plano, args.backup.resolve())
        erros_finais = validar_referencias(cartao)
        if erros_finais:
            raise ErroImplantacao("Validação final falhou:\n- " + "\n- ".join(erros_finais))
        print(f"\nAtualizados/criados: {alterados}; já idênticos: {inalterados}")
        print(f"Backup local: {backup if backup else 'dispensado (nenhuma substituição)'}")
        print("VALIDAÇÃO FINAL: cartão pronto para o firmware.")
        return 0
    except (ErroImplantacao, OSError, UnicodeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
