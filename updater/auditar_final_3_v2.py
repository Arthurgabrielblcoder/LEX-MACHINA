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
# LEX MACHINA
# AUDITORIA FINAL V2 - CF88, CC2002 e ECA1990
#
# CORREÇÕES DESTA VERSÃO:
# 1) NÃO aceita uma fonte oficial "pequena" como válida.
# 2) Testa MAIS DE UMA URL oficial para cada norma.
# 3) Escolhe automaticamente a fonte oficial mais completa.
# 4) Exige que a fonte contenha o artigo final esperado:
#       CF88    -> Art. 250
#       CC2002  -> Art. 2.046
#       ECA1990 -> Art. 267
# 5) Só depois compara o TEXTO VIGENTE com o arquivo local.
#
# NÃO ALTERA NENHUM ARQUIVO DO CARTÃO.
# ============================================================


REL_DIR = Path("saida/99_INDICES")
REL_TXT = REL_DIR / "AUDITORIA_FINAL_3_V2.txt"
REL_JSON = REL_DIR / "AUDITORIA_FINAL_3_V2.json"

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
        "urls": [
            "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
            "https://www4.planalto.gov.br/legislacao/legis-federal/constituicao",
        ],
        "artigo_final": 250,
        "min_chars_fonte": 150000,
    },
    {
        "id": "CC2002",
        "nome": "Lei 10.406/2002 - Código Civil",
        "arquivo": (
            Path("2- CÓDIGO CIVIL")
            / "codigo_civil_ lei10.406 2002.txt"
        ),
        "urls": [
            # IMPORTANTE: usa a página principal completa,
            # NÃO l10406compilada.htm, que estava retornando
            # uma resposta minúscula no computador.
            "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406.htm",
            "https://planalto.gov.br/ccivil_03/leis/2002/l10406.htm",
        ],
        "artigo_final": 2046,
        "min_chars_fonte": 300000,
    },
    {
        "id": "ECA1990",
        "nome": "Lei 8.069/1990 - Estatuto da Criança e do Adolescente",
        "arquivo": (
            Path("10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE")
            / (
                "Estatuto da Criança e do Adolescente "
                "(Lei nº 8.069 1990).txt"
            )
        ),
        "urls": [
            # Usa a página principal completa, não a variante
            # "compilado" que estava chegando truncada.
            "https://www.planalto.gov.br/ccivil_03/leis/l8069.htm",
            "https://planalto.gov.br/ccivil_03/leis/l8069.htm",
        ],
        "artigo_final": 267,
        "min_chars_fonte": 120000,
    },
]


def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - auditoria final V2 "
            "de Constituição, Código Civil e ECA"
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
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(
        c for c in texto
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
    texto = remover_acentos(texto).casefold()
    texto = re.sub(r"[^a-z0-9§º°]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def ler_local(caminho):
    dados = caminho.read_bytes()

    for codificacao in ("utf-8", "cp1252", "latin-1"):
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
            pass

    texto = dados.decode("utf-8", errors="replace")
    return {
        "bytes": len(dados),
        "linhas": len(texto.splitlines()),
        "caracteres": len(texto),
        "encoding": "utf-8-replace",
        "texto": limpar_texto(texto),
    }


def decodificar_html(dados):
    candidatos = []

    for codificacao in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            html = dados.decode(codificacao)
            candidatos.append(
                (
                    html.casefold().count("art"),
                    len(html),
                    codificacao,
                    html,
                )
            )
        except UnicodeDecodeError:
            pass

    if candidatos:
        candidatos.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True,
        )
        escolhido = candidatos[0]
        return escolhido[3], escolhido[2]

    return (
        dados.decode("cp1252", errors="replace"),
        "cp1252-replace",
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


def elemento_riscado(tag):
    if tag is None:
        return False

    nome = getattr(tag, "name", None)

    if nome in {"strike", "s", "del"}:
        return True

    attrs = getattr(tag, "attrs", None)

    if not attrs:
        return False

    estilo = str(attrs.get("style", "")).lower()
    estilo = re.sub(r"\s+", "", estilo)

    return "line-through" in estilo


def extrair_html(html, status_http, bytes_html, codificacao, url):
    soup_completo = BeautifulSoup(html, "lxml")
    remover_nao_textuais(soup_completo)

    soup_vigente = copy.deepcopy(soup_completo)

    for tag in reversed(list(soup_vigente.find_all(True))):
        try:
            if elemento_riscado(tag):
                tag.decompose()
        except (AttributeError, TypeError):
            pass

    corpo_completo = soup_completo.body or soup_completo
    corpo_vigente = soup_vigente.body or soup_vigente

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
        "url": url,
        "status_http": status_http,
        "bytes_html": bytes_html,
        "encoding_html": codificacao,
        "completo": {
            "texto": texto_completo,
            "linhas": len(texto_completo.splitlines()),
            "caracteres": len(texto_completo),
        },
        "vigente": {
            "texto": texto_vigente,
            "linhas": len(texto_vigente.splitlines()),
            "caracteres": len(texto_vigente),
        },
    }


def buscar_url(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    resposta.raise_for_status()

    html, codificacao = decodificar_html(
        resposta.content
    )

    return extrair_html(
        html=html,
        status_http=resposta.status_code,
        bytes_html=len(resposta.content),
        codificacao=codificacao,
        url=str(resposta.url),
    )


# ============================================================
# DETECTOR DE ARTIGOS
#
# Não depende de começo de linha.
# Serve, nesta auditoria, principalmente para confirmar que
# a fonte oficial escolhida realmente alcança o fim da norma.
# ============================================================

PADRAO_ARTIGO = re.compile(
    r"(?i)"
    r"(?<![A-Za-zÀ-ÿ])"
    r"art(?:igo)?"
    r"\s*\.?\s*"
    r"(?:\.\s*)?"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,4})"
)


def metricas_artigos(texto):
    numeros = []

    for match in PADRAO_ARTIGO.finditer(texto):
        bruto = match.group(1)

        try:
            numero = int(
                bruto.replace(".", "")
            )
        except ValueError:
            continue

        if 1 <= numero <= 9999:
            numeros.append(numero)

    return {
        "ocorrencias": len(numeros),
        "max": max(numeros) if numeros else 0,
        "numeros": sorted(set(numeros)),
    }


def contem_artigo_final(texto, artigo_final):
    metricas = metricas_artigos(texto)
    return artigo_final in set(metricas["numeros"])


def avaliar_fonte(alvo, fonte):
    completo = fonte["completo"]
    vigente = fonte["vigente"]

    metricas_completo = metricas_artigos(
        completo["texto"]
    )
    metricas_vigente = metricas_artigos(
        vigente["texto"]
    )

    motivos = []

    if completo["caracteres"] < alvo["min_chars_fonte"]:
        motivos.append(
            (
                "fonte completa pequena demais: "
                f"{completo['caracteres']} caracteres "
                f"(mínimo esperado {alvo['min_chars_fonte']})"
            )
        )

    if not contem_artigo_final(
        completo["texto"],
        alvo["artigo_final"],
    ):
        motivos.append(
            (
                "a fonte completa não contém o artigo final "
                f"esperado ({alvo['artigo_final']})"
            )
        )

    if not contem_artigo_final(
        vigente["texto"],
        alvo["artigo_final"],
    ):
        motivos.append(
            (
                "o texto vigente extraído não contém o artigo "
                f"final esperado ({alvo['artigo_final']})"
            )
        )

    # O vigente não pode ser absurdamente pequeno diante do completo.
    if (
        completo["caracteres"] >= 10000
        and vigente["caracteres"]
        < completo["caracteres"] * 0.25
    ):
        motivos.append(
            (
                "texto vigente extraído ficou abaixo de 25% "
                "do texto completo; possível remoção excessiva"
            )
        )

    return {
        "valida": not motivos,
        "motivos": motivos,
        "metricas_completo": metricas_completo,
        "metricas_vigente": metricas_vigente,
    }


def escolher_melhor_fonte(alvo):
    tentativas = []

    for url in alvo["urls"]:
        try:
            fonte = buscar_url(url)
            avaliacao = avaliar_fonte(
                alvo,
                fonte,
            )

            tentativas.append(
                {
                    "ok_http": True,
                    "url_pedida": url,
                    "fonte": fonte,
                    "avaliacao": avaliacao,
                }
            )

        except Exception as erro:
            tentativas.append(
                {
                    "ok_http": False,
                    "url_pedida": url,
                    "erro": str(erro),
                }
            )

    validas = [
        t
        for t in tentativas
        if (
            t.get("ok_http")
            and t["avaliacao"]["valida"]
        )
    ]

    if validas:
        validas.sort(
            key=lambda t: (
                t["fonte"]["completo"]["caracteres"],
                t["fonte"]["vigente"]["caracteres"],
            ),
            reverse=True,
        )

        return validas[0], tentativas

    # Se nenhuma passou, retorna a maior tentativa apenas para diagnóstico.
    candidatas = [
        t
        for t in tentativas
        if t.get("ok_http")
    ]

    if candidatas:
        candidatas.sort(
            key=lambda t: (
                t["fonte"]["completo"]["caracteres"]
            ),
            reverse=True,
        )
        return candidatas[0], tentativas

    return None, tentativas


# ============================================================
# COMPARAÇÃO TEXTUAL
# ============================================================

def shingles(texto, n=7):
    palavras = normalizar(texto).split()

    if len(palavras) < n:
        return set()

    return {
        " ".join(palavras[i:i+n])
        for i in range(
            len(palavras) - n + 1
        )
    }


def cobertura(referencia, candidato):
    ref = shingles(referencia)
    cand = shingles(candidato)

    if not ref:
        return 0.0

    return len(ref & cand) / len(ref)


def blocos(texto, min_chars=100):
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
                bloco = " ".join(atual).strip()

                if len(bloco) >= min_chars:
                    saida.append(bloco)

                atual = []
                tamanho = 0

            continue

        atual.append(linha)
        tamanho += len(linha)

        if tamanho >= 450:
            bloco = " ".join(atual).strip()

            if len(bloco) >= min_chars:
                saida.append(bloco)

            atual = []
            tamanho = 0

    if atual:
        bloco = " ".join(atual).strip()

        if len(bloco) >= min_chars:
            saida.append(bloco)

    return saida


def bloco_presente(bloco, local_norm):
    bloco_norm = normalizar(bloco)

    if not bloco_norm:
        return True

    if bloco_norm in local_norm:
        return True

    palavras = bloco_norm.split()

    if len(palavras) < 10:
        return False

    janela = min(14, len(palavras))

    inicio = " ".join(
        palavras[:janela]
    )

    fim = " ".join(
        palavras[-janela:]
    )

    centro = len(palavras) // 2

    meio = " ".join(
        palavras[
            max(0, centro - janela // 2):
            centro + janela // 2
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
            and assinatura in local_norm
        )
    )

    return presentes >= 2


def encontrar_ausentes(
    oficial_vigente,
    local,
    limite=25,
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


def classificar_local(
    alvo,
    local,
    fonte_escolhida,
):
    fonte = fonte_escolhida["fonte"]
    avaliacao_fonte = fonte_escolhida[
        "avaliacao"
    ]

    if not avaliacao_fonte["valida"]:
        return {
            "status": "FONTE_OFICIAL_INCONCLUSIVA",
            "motivos": avaliacao_fonte["motivos"],
            "cobertura_vigente_no_local": None,
            "cobertura_local_no_vigente": None,
            "blocos": None,
        }

    vigente = fonte["vigente"]["texto"]

    cob_vig_local = cobertura(
        vigente,
        local["texto"],
    )

    cob_local_vig = cobertura(
        local["texto"],
        vigente,
    )

    ausentes = encontrar_ausentes(
        vigente,
        local["texto"],
    )

    proporcao_ausentes = (
        ausentes["total_ausentes"]
        / ausentes["total_blocos"]
        if ausentes["total_blocos"]
        else 0.0
    )

    motivos = []

    if cob_vig_local < 0.95:
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
                "não foram encontrados no arquivo local"
            )
        )

    # A fonte deve conter o final da norma e o local também.
    if not contem_artigo_final(
        local["texto"],
        alvo["artigo_final"],
    ):
        motivos.append(
            (
                "arquivo local não contém o artigo final "
                f"esperado ({alvo['artigo_final']})"
            )
        )

    if motivos:
        status = "REVISAR"
    else:
        status = "APROVADA_VIGENTE"

    return {
        "status": status,
        "motivos": motivos,
        "cobertura_vigente_no_local": cob_vig_local,
        "cobertura_local_no_vigente": cob_local_vig,
        "blocos": ausentes,
    }


def main():
    args = argumentos()

    origem = Path(args.origem)

    if (
        not origem.exists()
        or not origem.is_dir()
    ):
        raise FileNotFoundError(
            f"Origem inválida: {origem}"
        )

    print()
    print(
        "LEX MACHINA - AUDITORIA FINAL V2"
    )
    print(
        "=" * 72
    )
    print(
        "Alvos: Constituição, Código Civil e ECA"
    )
    print(
        "Modo: SOMENTE LEITURA NO CARTÃO"
    )
    print()

    resultados = []

    for indice, alvo in enumerate(
        ALVOS,
        start=1,
    ):
        print(
            f"[{indice}/3] "
            f"{alvo['id']} - {alvo['nome']}"
        )

        caminho = (
            origem
            / alvo["arquivo"]
        )

        if not caminho.exists():
            resultado = {
                "id": alvo["id"],
                "nome": alvo["nome"],
                "status": "REVISAR",
                "erro": "Arquivo local não encontrado.",
            }
            resultados.append(resultado)
            print(
                "  REVISAR: arquivo local não encontrado."
            )
            continue

        local = ler_local(
            caminho
        )

        melhor, tentativas = escolher_melhor_fonte(
            alvo
        )

        if melhor is None:
            resultado = {
                "id": alvo["id"],
                "nome": alvo["nome"],
                "arquivo": str(caminho),
                "status": "FONTE_OFICIAL_INCONCLUSIVA",
                "erro": (
                    "Nenhuma URL oficial respondeu corretamente."
                ),
                "tentativas": tentativas,
            }

            resultados.append(resultado)

            print(
                "  FONTE_OFICIAL_INCONCLUSIVA"
            )
            continue

        analise = classificar_local(
            alvo,
            local,
            melhor,
        )

        resultado = {
            "id": alvo["id"],
            "nome": alvo["nome"],
            "arquivo": str(caminho),
            "status": analise["status"],
            "motivos": analise["motivos"],
            "fonte_escolhida": (
                melhor["fonte"]["url"]
            ),
            "fonte_completo_caracteres": (
                melhor["fonte"][
                    "completo"
                ][
                    "caracteres"
                ]
            ),
            "fonte_vigente_caracteres": (
                melhor["fonte"][
                    "vigente"
                ][
                    "caracteres"
                ]
            ),
            "fonte_completo_artigos": (
                melhor[
                    "avaliacao"
                ][
                    "metricas_completo"
                ][
                    "ocorrencias"
                ]
            ),
            "fonte_completo_max_artigo": (
                melhor[
                    "avaliacao"
                ][
                    "metricas_completo"
                ][
                    "max"
                ]
            ),
            "local_caracteres": (
                local["caracteres"]
            ),
            "local_artigos": (
                metricas_artigos(
                    local["texto"]
                )[
                    "ocorrencias"
                ]
            ),
            "local_max_artigo": (
                metricas_artigos(
                    local["texto"]
                )[
                    "max"
                ]
            ),
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
            "blocos": (
                analise["blocos"]
            ),
            "tentativas": [
                {
                    "url_pedida": t.get(
                        "url_pedida",
                        "",
                    ),
                    "ok_http": t.get(
                        "ok_http",
                        False,
                    ),
                    "url_final": (
                        t.get(
                            "fonte",
                            {},
                        ).get(
                            "url",
                            "",
                        )
                    ),
                    "caracteres_completo": (
                        t.get(
                            "fonte",
                            {},
                        ).get(
                            "completo",
                            {},
                        ).get(
                            "caracteres",
                            0,
                        )
                    ),
                    "caracteres_vigente": (
                        t.get(
                            "fonte",
                            {},
                        ).get(
                            "vigente",
                            {},
                        ).get(
                            "caracteres",
                            0,
                        )
                    ),
                    "fonte_valida": (
                        t.get(
                            "avaliacao",
                            {},
                        ).get(
                            "valida",
                            False,
                        )
                    ),
                    "motivos": (
                        t.get(
                            "avaliacao",
                            {},
                        ).get(
                            "motivos",
                            [],
                        )
                    ),
                    "erro": t.get(
                        "erro",
                        "",
                    ),
                }
                for t in tentativas
            ],
        }

        resultados.append(
            resultado
        )

        if (
            analise[
                "cobertura_vigente_no_local"
            ]
            is not None
        ):
            blocos_info = analise["blocos"]

            print(
                (
                    f"  {analise['status']} "
                    f"| fonte={melhor['fonte']['completo']['caracteres']} chars "
                    f"| vigente→local="
                    f"{analise['cobertura_vigente_no_local']:.4f} "
                    f"| ausentes="
                    f"{blocos_info['total_ausentes']}/"
                    f"{blocos_info['total_blocos']}"
                )
            )
        else:
            print(
                "  FONTE_OFICIAL_INCONCLUSIVA"
            )

    REL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    aprovadas = [
        r
        for r in resultados
        if r.get("status")
        == "APROVADA_VIGENTE"
    ]

    revisar = [
        r
        for r in resultados
        if r.get("status")
        == "REVISAR"
    ]

    inconclusivas = [
        r
        for r in resultados
        if r.get("status")
        == "FONTE_OFICIAL_INCONCLUSIVA"
    ]

    linhas = [
        "LEX MACHINA",
        "AUDITORIA FINAL V2 - CF88, CC2002 E ECA1990",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        "",
        f"TOTAL: {len(resultados)}",
        f"APROVADAS: {len(aprovadas)}",
        f"REVISAR: {len(revisar)}",
        (
            "FONTE OFICIAL INCONCLUSIVA: "
            f"{len(inconclusivas)}"
        ),
        "",
        "=" * 78,
        "RESULTADOS",
        "=" * 78,
        "",
    ]

    for r in resultados:
        linhas.append(
            (
                f"[{r.get('status', '')}] "
                f"{r.get('id', '')} - "
                f"{r.get('nome', '')}"
            )
        )

        linhas.append(
            f"  Arquivo: {r.get('arquivo', '')}"
        )

        if r.get("erro"):
            linhas.append(
                f"  ERRO: {r['erro']}"
            )
            linhas.append("")
            continue

        linhas.append(
            (
                "  Fonte escolhida: "
                f"{r.get('fonte_escolhida', '')}"
            )
        )

        linhas.append(
            (
                "  Fonte completa: "
                f"{r.get('fonte_completo_caracteres', 0)} caracteres "
                f"| artigos_aparentes="
                f"{r.get('fonte_completo_artigos', 0)} "
                f"| maior_artigo="
                f"{r.get('fonte_completo_max_artigo', 0)}"
            )
        )

        linhas.append(
            (
                "  Fonte vigente: "
                f"{r.get('fonte_vigente_caracteres', 0)} caracteres"
            )
        )

        linhas.append(
            (
                "  Local: "
                f"{r.get('local_caracteres', 0)} caracteres "
                f"| artigos_aparentes="
                f"{r.get('local_artigos', 0)} "
                f"| maior_artigo="
                f"{r.get('local_max_artigo', 0)}"
            )
        )

        if (
            r.get(
                "cobertura_vigente_no_local"
            )
            is not None
        ):
            linhas.append(
                (
                    "  Cobertura vigente -> local: "
                    f"{r['cobertura_vigente_no_local']:.4f}"
                )
            )

            linhas.append(
                (
                    "  Cobertura local -> vigente: "
                    f"{r['cobertura_local_no_vigente']:.4f}"
                )
            )

        blocos_info = r.get(
            "blocos"
        )

        if blocos_info:
            linhas.append(
                (
                    "  Blocos vigentes ausentes: "
                    f"{blocos_info['total_ausentes']}/"
                    f"{blocos_info['total_blocos']}"
                )
            )

            if blocos_info[
                "exemplos"
            ]:
                linhas.append(
                    "  Exemplos de possíveis omissões:"
                )

                for exemplo in (
                    blocos_info[
                        "exemplos"
                    ][
                        :10
                    ]
                ):
                    linhas.append(
                        f"    - {exemplo}"
                    )

        for motivo in r.get(
            "motivos",
            [],
        ):
            linhas.append(
                f"  MOTIVO: {motivo}"
            )

        linhas.append(
            "  Tentativas de fonte:"
        )

        for t in r.get(
            "tentativas",
            [],
        ):
            linhas.append(
                (
                    "    - "
                    f"{t['url_pedida']} "
                    f"| HTTP_OK={t['ok_http']} "
                    f"| chars={t['caracteres_completo']} "
                    f"| válida={t['fonte_valida']}"
                )
            )

            for motivo in t.get(
                "motivos",
                [],
            ):
                linhas.append(
                    f"      motivo: {motivo}"
                )

            if t.get("erro"):
                linhas.append(
                    f"      erro: {t['erro']}"
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

    if (
        len(aprovadas) == 3
        and not revisar
        and not inconclusivas
    ):
        linhas.append(
            (
                "AS 3 NORMAS PASSARAM NA AUDITORIA FINAL V2 "
                "COM FONTES OFICIAIS COMPLETAS."
            )
        )
    else:
        linhas.append(
            (
                "AINDA NÃO APROVADO: existe pelo menos uma "
                "norma ou fonte que exige revisão."
            )
        )

    REL_TXT.write_text(
        "\n".join(linhas) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    REL_JSON.write_text(
        json.dumps(
            {
                "gerado_em": agora(),
                "origem": str(origem),
                "resumo": {
                    "total": len(resultados),
                    "aprovadas": len(aprovadas),
                    "revisar": len(revisar),
                    "fonte_oficial_inconclusiva": len(
                        inconclusivas
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
        "AUDITORIA FINAL V2 CONCLUÍDA"
    )
    print(
        f"APROVADAS: {len(aprovadas)}"
    )
    print(
        f"REVISAR: {len(revisar)}"
    )
    print(
        "FONTE OFICIAL INCONCLUSIVA: "
        f"{len(inconclusivas)}"
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
        print("ERRO FATAL:")
        print(erro)
        sys.exit(1)
