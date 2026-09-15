from datetime import datetime
from pathlib import Path
import argparse
import copy
import json
import re
import sys
import unicodedata

import requests
from bs4 import BeautifulSoup


# ============================================================
# LEX MACHINA - AUDITORIA FINAL DAS 3 FONTES ALTERNATIVAS
#
# Alvos:
# - Constituição Federal
# - Código Civil
# - ECA
#
# Usa URLs oficiais alternativas e específicas do Planalto,
# porque as URLs anteriores foram extraídas de forma incompleta.
#
# NÃO ALTERA NENHUM ARQUIVO DO CARTÃO.
# ============================================================


REL_DIR = Path("saida/99_INDICES")
REL_TXT = REL_DIR / "AUDITORIA_FINAL_3_FONTES_ALTERNATIVAS.txt"
REL_JSON = REL_DIR / "AUDITORIA_FINAL_3_FONTES_ALTERNATIVAS.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 60

ALVOS = [
    {
        "id": "CF88",
        "nome": "Constituição da República Federativa do Brasil de 1988",
        "arquivo": Path("1- CONSTITUIÇÃO FEDERAL") / "cf.txt",
        "url": (
            "https://www.planalto.gov.br/"
            "ccivil_03/constituicao/constituicao.htm"
        ),
    },
    {
        "id": "CC2002",
        "nome": "Lei 10.406/2002 - Código Civil",
        "arquivo": (
            Path("2- CÓDIGO CIVIL")
            / "codigo_civil_ lei10.406 2002.txt"
        ),
        "url": (
            "https://www.planalto.gov.br/"
            "ccivil_03/leis/2002/l10406compilada.htm"
        ),
    },
    {
        "id": "ECA1990",
        "nome": (
            "Lei 8.069/1990 - Estatuto da Criança "
            "e do Adolescente"
        ),
        "arquivo": (
            Path(
                "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE"
            )
            / (
                "Estatuto da Criança e do Adolescente "
                "(Lei nº 8.069 1990).txt"
            )
        ),
        "url": (
            "https://www.planalto.gov.br/"
            "ccivil_03/leis/l8069compilado.htm"
        ),
    },
]


def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - auditoria final de CF, CC e ECA "
            "com fontes oficiais alternativas"
        )
    )

    parser.add_argument(
        "origem",
        help="Raiz do cartão. Exemplo: D:\\",
    )

    return parser.parse_args()


def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def remover_acentos(texto):
    texto = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    return "".join(
        c
        for c in texto
        if not unicodedata.combining(c)
    )


def limpar_texto(texto):
    texto = str(texto or "")

    texto = (
        texto
        .replace("\xa0", " ")
        .replace("\u2002", " ")
        .replace("\u2003", " ")
        .replace("\u2009", " ")
        .replace("\ufeff", "")
    )

    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def normalizar(texto):
    texto = remover_acentos(
        texto
    ).casefold()

    texto = re.sub(
        r"[^a-z0-9§º°]+",
        " ",
        texto,
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip()


def ler_local(caminho):
    dados = caminho.read_bytes()

    for codificacao in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            texto = dados.decode(codificacao)

            return {
                "bytes": len(dados),
                "linhas": len(texto.splitlines()),
                "caracteres": len(texto),
                "encoding": codificacao,
                "texto": limpar_texto(texto),
            }

        except UnicodeDecodeError:
            continue

    texto = dados.decode(
        "utf-8",
        errors="replace",
    )

    return {
        "bytes": len(dados),
        "linhas": len(texto.splitlines()),
        "caracteres": len(texto),
        "encoding": "utf-8-replace",
        "texto": limpar_texto(texto),
    }


def decodificar_html(dados):
    candidatos = []

    for codificacao in (
        "utf-8",
        "cp1252",
        "iso-8859-1",
    ):
        try:
            html = dados.decode(codificacao)

            candidatos.append(
                (
                    html.count("Art"),
                    len(html),
                    codificacao,
                    html,
                )
            )

        except UnicodeDecodeError:
            continue

    if candidatos:
        candidatos.sort(
            key=lambda x: (x[0], x[1]),
            reverse=True,
        )

        return (
            candidatos[0][3],
            candidatos[0][2],
        )

    return (
        dados.decode(
            "cp1252",
            errors="replace",
        ),
        "cp1252-replace",
    )


def elemento_riscado(tag):
    if tag is None:
        return False

    nome = getattr(
        tag,
        "name",
        None,
    )

    if nome in {
        "strike",
        "s",
        "del",
    }:
        return True

    attrs = getattr(
        tag,
        "attrs",
        None,
    )

    if not attrs:
        return False

    estilo = str(
        attrs.get(
            "style",
            "",
        )
    ).lower()

    estilo = re.sub(
        r"\s+",
        "",
        estilo,
    )

    return (
        "line-through"
        in estilo
    )


def remover_nao_textuais(soup):
    for nome in (
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
    ):
        for tag in soup.find_all(nome):
            try:
                tag.decompose()
            except AttributeError:
                pass


def baixar_oficial(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    resposta.raise_for_status()

    html, codificacao = decodificar_html(
        resposta.content
    )

    soup_completo = BeautifulSoup(
        html,
        "lxml",
    )

    remover_nao_textuais(
        soup_completo
    )

    soup_vigente = copy.deepcopy(
        soup_completo
    )

    for tag in reversed(
        list(
            soup_vigente.find_all(True)
        )
    ):
        try:
            if elemento_riscado(tag):
                tag.decompose()
        except (
            AttributeError,
            TypeError,
        ):
            pass

    corpo_completo = (
        soup_completo.body
        or soup_completo
    )

    corpo_vigente = (
        soup_vigente.body
        or soup_vigente
    )

    texto_completo = limpar_texto(
        corpo_completo.get_text(
            separator="\n",
            strip=True,
        )
    )

    texto_vigente = limpar_texto(
        corpo_vigente.get_text(
            separator="\n",
            strip=True,
        )
    )

    return {
        "status_http": resposta.status_code,
        "bytes_html": len(
            resposta.content
        ),
        "encoding_html": codificacao,
        "completo": {
            "texto": texto_completo,
            "linhas": len(
                texto_completo.splitlines()
            ),
            "caracteres": len(
                texto_completo
            ),
        },
        "vigente": {
            "texto": texto_vigente,
            "linhas": len(
                texto_vigente.splitlines()
            ),
            "caracteres": len(
                texto_vigente
            ),
        },
    }


def shingles(
    texto,
    n=7,
):
    palavras = normalizar(
        texto
    ).split()

    if len(palavras) < n:
        return set()

    return {
        " ".join(
            palavras[
                i:i+n
            ]
        )
        for i in range(
            len(palavras) - n + 1
        )
    }


def cobertura(
    referencia,
    candidato,
):
    ref = shingles(
        referencia
    )

    cand = shingles(
        candidato
    )

    if not ref:
        return 0.0

    return len(
        ref & cand
    ) / len(ref)


def blocos(
    texto,
    min_chars=100,
):
    linhas = [
        limpar_texto(linha)
        for linha in texto.splitlines()
    ]

    saida = []
    atual = []
    tamanho = 0

    for linha in linhas:
        if not linha:
            if atual:
                bloco = " ".join(
                    atual
                ).strip()

                if len(bloco) >= min_chars:
                    saida.append(bloco)

                atual = []
                tamanho = 0

            continue

        atual.append(linha)
        tamanho += len(linha)

        if tamanho >= 450:
            bloco = " ".join(
                atual
            ).strip()

            if len(bloco) >= min_chars:
                saida.append(bloco)

            atual = []
            tamanho = 0

    if atual:
        bloco = " ".join(
            atual
        ).strip()

        if len(bloco) >= min_chars:
            saida.append(bloco)

    return saida


def bloco_presente(
    bloco,
    local_norm,
):
    bloco_norm = normalizar(
        bloco
    )

    if not bloco_norm:
        return True

    if bloco_norm in local_norm:
        return True

    palavras = bloco_norm.split()

    if len(palavras) < 10:
        return False

    janela = min(
        14,
        len(palavras),
    )

    inicio = " ".join(
        palavras[:janela]
    )

    fim = " ".join(
        palavras[-janela:]
    )

    meio_indice = len(
        palavras
    ) // 2

    meio = " ".join(
        palavras[
            max(
                0,
                meio_indice - janela // 2
            ):
            meio_indice + janela // 2
        ]
    )

    presentes = sum(
        1
        for assinatura in (
            inicio,
            meio,
            fim,
        )
        if (
            assinatura
            and assinatura
            in local_norm
        )
    )

    return presentes >= 2


def encontrar_ausentes(
    oficial_vigente,
    local,
    limite=20,
):
    lista = blocos(
        oficial_vigente
    )

    local_norm = normalizar(
        local
    )

    total_ausentes = 0
    exemplos = []

    for bloco in lista:
        if bloco_presente(
            bloco,
            local_norm,
        ):
            continue

        total_ausentes += 1

        if len(exemplos) < limite:
            exemplos.append(
                re.sub(
                    r"\s+",
                    " ",
                    bloco,
                ).strip()[:800]
            )

    return {
        "total_blocos": len(lista),
        "total_ausentes": total_ausentes,
        "exemplos": exemplos,
    }


def validar(
    local,
    oficial,
):
    vigente = oficial[
        "vigente"
    ]

    cobertura_vigente = cobertura(
        vigente["texto"],
        local["texto"],
    )

    cobertura_local = cobertura(
        local["texto"],
        vigente["texto"],
    )

    ausentes = encontrar_ausentes(
        vigente["texto"],
        local["texto"],
    )

    proporcao_ausentes = (
        ausentes["total_ausentes"]
        / ausentes["total_blocos"]
        if ausentes["total_blocos"]
        else 0.0
    )

    motivos = []

    if vigente["caracteres"] < 5000:
        motivos.append(
            "fonte alternativa ainda parece pequena demais"
        )

    if cobertura_vigente < 0.95:
        motivos.append(
            (
                "cobertura do texto vigente oficial "
                "no arquivo local abaixo de 95%"
            )
        )

    if proporcao_ausentes > 0.04:
        motivos.append(
            (
                "mais de 4% dos blocos vigentes "
                "não foram localizados"
            )
        )

    if motivos:
        status = "REVISAR"
    else:
        status = "APROVADA_VIGENTE"

    return {
        "status": status,
        "motivos": motivos,
        "cobertura_vigente_no_local": cobertura_vigente,
        "cobertura_local_no_vigente": cobertura_local,
        "blocos_vigentes": ausentes["total_blocos"],
        "blocos_vigentes_ausentes": (
            ausentes["total_ausentes"]
        ),
        "proporcao_ausentes": proporcao_ausentes,
        "exemplos_ausentes": ausentes["exemplos"],
    }


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

    print()
    print(
        "LEX MACHINA - "
        "AUDITORIA FINAL DAS 3 FONTES ALTERNATIVAS"
    )

    print(
        "=" * 72
    )

    print(
        "Nenhum arquivo do cartão será alterado."
    )

    print()

    resultados = []

    for indice, alvo in enumerate(
        ALVOS,
        start=1,
    ):
        caminho = (
            origem
            / alvo[
                "arquivo"
            ]
        )

        print(
            f"[{indice}/3] "
            f"{alvo['id']} - "
            f"{alvo['nome']}"
        )

        if not caminho.exists():
            resultados.append(
                {
                    "id": alvo["id"],
                    "nome": alvo["nome"],
                    "status": "REVISAR",
                    "erro": (
                        "Arquivo local não encontrado."
                    ),
                }
            )

            print(
                "  ERRO: arquivo local não encontrado."
            )

            continue

        try:
            local = ler_local(
                caminho
            )

            oficial = baixar_oficial(
                alvo[
                    "url"
                ]
            )

            analise = validar(
                local,
                oficial,
            )

            resultado = {
                "id": alvo["id"],
                "nome": alvo["nome"],
                "arquivo": str(
                    caminho
                ),
                "fonte_alternativa": (
                    alvo["url"]
                ),
                "status": analise[
                    "status"
                ],
                "motivos": analise[
                    "motivos"
                ],
                "local": {
                    "bytes": local[
                        "bytes"
                    ],
                    "linhas": local[
                        "linhas"
                    ],
                    "caracteres": local[
                        "caracteres"
                    ],
                },
                "oficial_vigente": {
                    "linhas": oficial[
                        "vigente"
                    ][
                        "linhas"
                    ],
                    "caracteres": oficial[
                        "vigente"
                    ][
                        "caracteres"
                    ],
                },
                "cobertura_vigente_no_local": (
                    analise[
                        "cobertura_vigente_no_local"
                    ]
                ),
                "cobertura_local_no_vigente": (
                    analise[
                        "cobertura_local_no_vigente"
                    ]
                ),
                "blocos_vigentes": (
                    analise[
                        "blocos_vigentes"
                    ]
                ),
                "blocos_vigentes_ausentes": (
                    analise[
                        "blocos_vigentes_ausentes"
                    ]
                ),
                "exemplos_ausentes": (
                    analise[
                        "exemplos_ausentes"
                    ]
                ),
            }

            resultados.append(
                resultado
            )

            print(
                (
                    f"  {resultado['status']} "
                    "| vigente→local="
                    f"{resultado['cobertura_vigente_no_local']:.4f} "
                    "| ausentes="
                    f"{resultado['blocos_vigentes_ausentes']}/"
                    f"{resultado['blocos_vigentes']}"
                )
            )

        except Exception as erro:
            resultados.append(
                {
                    "id": alvo["id"],
                    "nome": alvo["nome"],
                    "arquivo": str(
                        caminho
                    ),
                    "status": "REVISAR",
                    "erro": str(
                        erro
                    ),
                }
            )

            print(
                f"  ERRO: {erro}"
            )

    REL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    aprovadas = [
        item
        for item in resultados
        if item.get(
            "status"
        )
        == "APROVADA_VIGENTE"
    ]

    revisar = [
        item
        for item in resultados
        if item.get(
            "status"
        )
        != "APROVADA_VIGENTE"
    ]

    linhas = [
        "LEX MACHINA",
        "AUDITORIA FINAL - 3 FONTES OFICIAIS ALTERNATIVAS",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        "",
        f"TOTAL: {len(resultados)}",
        f"APROVADAS: {len(aprovadas)}",
        f"REVISAR: {len(revisar)}",
        "",
        "=" * 78,
        "RESULTADOS",
        "=" * 78,
        "",
    ]

    for item in resultados:
        linhas.append(
            (
                f"[{item.get('status', '')}] "
                f"{item.get('id', '')} - "
                f"{item.get('nome', '')}"
            )
        )

        linhas.append(
            (
                "  Arquivo: "
                f"{item.get('arquivo', '')}"
            )
        )

        if item.get(
            "erro"
        ):
            linhas.append(
                (
                    "  ERRO: "
                    f"{item['erro']}"
                )
            )
            linhas.append("")
            continue

        linhas.append(
            (
                "  Fonte alternativa: "
                f"{item['fonte_alternativa']}"
            )
        )

        linhas.append(
            (
                "  Cobertura vigente -> local: "
                f"{item['cobertura_vigente_no_local']:.4f}"
            )
        )

        linhas.append(
            (
                "  Cobertura local -> vigente: "
                f"{item['cobertura_local_no_vigente']:.4f}"
            )
        )

        linhas.append(
            (
                "  Local: "
                f"{item['local']['caracteres']} caracteres"
            )
        )

        linhas.append(
            (
                "  Oficial vigente: "
                f"{item['oficial_vigente']['caracteres']} caracteres"
            )
        )

        linhas.append(
            (
                "  Blocos vigentes ausentes: "
                f"{item['blocos_vigentes_ausentes']}/"
                f"{item['blocos_vigentes']}"
            )
        )

        for motivo in item.get(
            "motivos",
            [],
        ):
            linhas.append(
                (
                    "  MOTIVO: "
                    f"{motivo}"
                )
            )

        if item.get(
            "exemplos_ausentes"
        ):
            linhas.append(
                "  Exemplos de possíveis omissões:"
            )

            for exemplo in item[
                "exemplos_ausentes"
            ][
                :10
            ]:
                linhas.append(
                    f"    - {exemplo}"
                )

        linhas.append("")

    linhas.extend(
        [
            "=" * 78,
            "CONCLUSÃO",
            "=" * 78,
            "",
        ]
    )

    if len(aprovadas) == 3:
        linhas.append(
            (
                "AS 3 NORMAS PASSARAM NA AUDITORIA "
                "COM FONTES OFICIAIS ALTERNATIVAS."
            )
        )
    else:
        linhas.append(
            (
                "AINDA NÃO APROVADO: pelo menos uma das "
                "3 normas exige revisão."
            )
        )

    REL_TXT.write_text(
        "\n".join(
            linhas
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    REL_JSON.write_text(
        json.dumps(
            {
                "gerado_em": agora(),
                "origem": str(
                    origem
                ),
                "resumo": {
                    "total": len(
                        resultados
                    ),
                    "aprovadas": len(
                        aprovadas
                    ),
                    "revisar": len(
                        revisar
                    ),
                },
                "resultados": resultados,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print()
    print(
        "=" * 72
    )

    print(
        "AUDITORIA FINALIZADA"
    )

    print(
        f"APROVADAS: {len(aprovadas)}"
    )

    print(
        f"REVISAR: {len(revisar)}"
    )

    print(
        f"Relatório TXT: {REL_TXT}"
    )

    print(
        f"Relatório JSON: {REL_JSON}"
    )

    print()

    print(
        "Nenhum arquivo do cartão foi alterado."
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
