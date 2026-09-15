from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


# =============================================================================
# LEX MACHINA
# RECUPERAÇÃO DEFINITIVA DOS 3 TEXTOS-BASE
#
# Alvos:
#   - Constituição Federal de 1988
#   - Código Civil (Lei 10.406/2002)
#   - ECA (Lei 8.069/1990)
#
# ESTRATÉGIA
# ----------
# 1) NÃO usa mais scraping do HTML legado do Planalto para esses 3 arquivos.
# 2) Resolve dinamicamente, no portal oficial do Senado Federal, a linha
#    "Compilação Monovigente" / "Compilação Monovigente na CD".
# 3) Baixa o texto consolidado atual correspondente.
# 4) Valida a fonte com critérios estruturais fortes:
#      - tamanho mínimo;
#      - quantidade mínima de cabeçalhos de artigos;
#      - presença de uma série de artigos-âncora;
#      - presença do artigo final;
#      - presença de marcas de atualização recente.
# 5) Só se AS TRÊS fontes passarem, gera candidatos completos.
# 6) Sem --aplicar, apenas audita e cria os candidatos no PC.
# 7) Com --aplicar:
#      - faz backup dos 3 arquivos atuais no PC;
#      - grava arquivos temporários no cartão;
#      - revalida os temporários;
#      - substitui de forma atômica;
#      - reabre e revalida os arquivos finais;
#      - se qualquer etapa falhar, restaura os 3 backups.
#
# NUNCA substitui um arquivo se a fonte oficial não passar em TODOS os testes.
#
# O script NÃO altera catalogo_mestre_vademecum.json nem main.py.
# Esses dois serão corrigidos posteriormente, depois da recuperação.
# =============================================================================


# =============================================================================
# CAMINHOS DE SAÍDA NO PC
# =============================================================================

SAIDA_DIR = Path("saida/99_INDICES")
CANDIDATOS_DIR = SAIDA_DIR / "CANDIDATOS_RECUPERACAO_3"
BACKUP_ROOT = Path("backup_saida")

REL_TXT = SAIDA_DIR / "RECUPERACAO_DEFINITIVA_3.txt"
REL_JSON = SAIDA_DIR / "RECUPERACAO_DEFINITIVA_3.json"


# =============================================================================
# REDE
# =============================================================================

TIMEOUT = 60

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.5",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

MAX_TENTATIVAS = 4


# =============================================================================
# DEFINIÇÃO DOS 3 ALVOS
#
# norma_url:
#   página oficial do Senado que informa a versão "Compilação Monovigente".
#
# fallback_publicacao:
#   publicação monovigente conhecida em 13/09/2026. Ela só é usada se o
#   resolvedor dinâmico falhar. Mesmo nesse caso, a validação estrutural
#   continua obrigatória; portanto uma publicação velha/incompleta não passa.
# =============================================================================

ALVOS = [
    {
        "id": "CF88",
        "nome": "Constituição da República Federativa do Brasil de 1988",
        "arquivo_relativo": (
            Path("1- CONSTITUIÇÃO FEDERAL")
            / "cf.txt"
        ),
        "norma_url": "https://legis.senado.leg.br/norma/579494",
        "fallback_publicacao": (
            "https://legis.senado.leg.br/"
            "norma/579494/publicacao/16434817"
        ),
        "titulo_inicio": (
            "CONSTITUIÇÃO DA REPÚBLICA FEDERATIVA DO BRASIL"
        ),
        "min_caracteres": 180_000,
        "min_linhas": 2_000,
        "min_artigos": 235,
        "artigo_final": "250",
        "artigos_ancora": [
            "1",
            "5",
            "18",
            "31",
            "37",
            "60",
            "75",
            "93",
            "102",
            "127",
            "134",
            "144",
            "150",
            "170",
            "194",
            "196",
            "205",
            "225",
            "226",
            "227",
            "230",
            "250",
        ],
        "frases_recentes": [
            "vedada sua extinção, criação ou instalação",
            "os tribunais de contas são instituições permanentes",
        ],
    },
    {
        "id": "CC2002",
        "nome": "Lei 10.406/2002 - Código Civil",
        "arquivo_relativo": (
            Path("2- CÓDIGO CIVIL")
            / "codigo_civil_ lei10.406 2002.txt"
        ),
        "norma_url": "https://legis.senado.leg.br/norma/552282",
        "fallback_publicacao": (
            "https://legis.senado.leg.br/"
            "norma/552282/publicacao/34620807"
        ),
        "titulo_inicio": (
            "LEI Nº 10.406, DE 10 DE JANEIRO DE 2002"
        ),
        "min_caracteres": 400_000,
        "min_linhas": 5_000,
        "min_artigos": 1_900,
        "artigo_final": "2046",
        "artigos_ancora": [
            "1",
            "40",
            "44",
            "104",
            "186",
            "233",
            "404",
            "406",
            "421",
            "927",
            "966",
            "1045",
            "1225",
            "1421",
            "1511",
            "1784",
            "1829",
            "2002",
            "2046",
        ],
        "frases_recentes": [
            "empreendimentos de economia solidária",
            "lei nº 14.905",
        ],
    },
    {
        "id": "ECA1990",
        "nome": (
            "Lei 8.069/1990 - Estatuto da Criança e do Adolescente"
        ),
        "arquivo_relativo": (
            Path(
                "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE"
            )
            / (
                "Estatuto da Criança e do Adolescente "
                "(Lei nº 8.069 1990).txt"
            )
        ),
        "norma_url": "https://legis.senado.leg.br/norma/549945",
        "fallback_publicacao": (
            "https://legis.senado.leg.br/"
            "norma/549945/publicacao/34619929"
        ),
        "titulo_inicio": (
            "LEI Nº 8.069, DE 13 DE JULHO DE 1990"
        ),
        "min_caracteres": 120_000,
        "min_linhas": 1_500,
        "min_artigos": 250,
        "artigo_final": "267",
        "artigos_ancora": [
            "1",
            "7",
            "11-A",
            "53",
            "70",
            "101",
            "112",
            "131",
            "136",
            "149",
            "171",
            "190-F",
            "201",
            "208",
            "227-C",
            "240",
            "241-E",
            "267",
        ],
        "frases_recentes": [
            "lei nº 15.487",
            "art. 190-f",
            "art. 227-c",
        ],
    },
]


# =============================================================================
# ARGUMENTOS
# =============================================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - recuperação definitiva de Constituição, "
            "Código Civil e ECA usando compilações oficiais monovigentes "
            "do Senado Federal."
        )
    )

    parser.add_argument(
        "origem",
        help="Raiz do cartão. Exemplo: D:\\",
    )

    parser.add_argument(
        "--aplicar",
        action="store_true",
        help=(
            "Depois de validar as 3 fontes, faz backup e substitui "
            "os três arquivos no cartão."
        ),
    )

    return parser.parse_args()


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256_bytes(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def sha256_texto(texto: str) -> str:
    return sha256_bytes(
        texto.encode("utf-8")
    )


def remover_acentos(texto: str) -> str:
    decomposicao = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    return "".join(
        caractere
        for caractere in decomposicao
        if not unicodedata.combining(caractere)
    )


def normalizar_busca(texto: str) -> str:
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


def limpar_linha(texto: str) -> str:
    texto = str(
        texto or ""
    )

    texto = (
        texto
        .replace("\xa0", " ")
        .replace("\u2002", " ")
        .replace("\u2003", " ")
        .replace("\u2009", " ")
        .replace("\ufeff", "")
    )

    texto = re.sub(
        r"[ \t]+",
        " ",
        texto,
    )

    return texto.strip()


def normalizar_quebras(texto: str) -> str:
    linhas_brutas = texto.splitlines()
    linhas = []

    vazio_anterior = False

    for linha in linhas_brutas:
        linha = limpar_linha(
            linha
        )

        if not linha:
            if not vazio_anterior:
                linhas.append("")
            vazio_anterior = True
            continue

        linhas.append(
            linha
        )

        vazio_anterior = False

    return (
        "\n".join(linhas)
        .strip()
        + "\n"
    )


def tamanho_texto(texto: str) -> dict:
    return {
        "caracteres": len(texto),
        "linhas": len(texto.splitlines()),
        "bytes_utf8": len(
            texto.encode("utf-8")
        ),
        "sha256": sha256_texto(texto),
    }


# =============================================================================
# SESSÃO HTTP COM RETENTATIVAS
# =============================================================================

def nova_sessao():
    sessao = requests.Session()
    sessao.headers.update(
        HEADERS
    )
    return sessao


def requisitar(
    sessao: requests.Session,
    url: str,
) -> requests.Response:
    ultimo_erro = None

    for tentativa in range(
        1,
        MAX_TENTATIVAS + 1,
    ):
        try:
            resposta = sessao.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=True,
            )

            if resposta.status_code in {
                429,
                500,
                502,
                503,
                504,
            }:
                espera = min(
                    2 ** tentativa,
                    12,
                )

                time.sleep(
                    espera
                )

                ultimo_erro = RuntimeError(
                    (
                        f"HTTP {resposta.status_code} "
                        f"em {resposta.url}"
                    )
                )

                continue

            resposta.raise_for_status()

            if len(
                resposta.content
            ) < 100:
                ultimo_erro = RuntimeError(
                    (
                        "Resposta HTTP pequena demais "
                        f"({len(resposta.content)} bytes)"
                    )
                )

                time.sleep(
                    tentativa
                )

                continue

            return resposta

        except Exception as erro:
            ultimo_erro = erro

            if tentativa < MAX_TENTATIVAS:
                time.sleep(
                    min(
                        2 ** tentativa,
                        12,
                    )
                )

    raise RuntimeError(
        (
            f"Falha ao acessar {url}: "
            f"{ultimo_erro}"
        )
    )


# =============================================================================
# RESOLVEDOR DINÂMICO DE "COMPILAÇÃO MONOVIGENTE"
# =============================================================================

def resolver_compilacao_monovigente(
    sessao: requests.Session,
    alvo: dict,
) -> tuple[str, dict]:
    resposta = requisitar(
        sessao,
        alvo["norma_url"],
    )

    # Usa html.parser da biblioteca padrão de propósito.
    # Não depende do lxml usado nos scripts anteriores.
    soup = BeautifulSoup(
        resposta.content,
        "html.parser",
    )

    candidatos = []

    # Estratégia principal: linhas de tabela.
    for linha_tabela in soup.find_all(
        "tr"
    ):
        texto_linha = normalizar_busca(
            linha_tabela.get_text(
                " ",
                strip=True,
            )
        )

        if (
            "compilacao monovigente"
            not in texto_linha
        ):
            continue

        for link in linha_tabela.find_all(
            "a",
            href=True,
        ):
            href = str(
                link.get(
                    "href",
                    "",
                )
            ).strip()

            if (
                "/publicacao/"
                in href
            ):
                candidatos.append(
                    urljoin(
                        str(resposta.url),
                        href,
                    )
                )

    # Estratégia secundária: procura o texto e sobe na árvore.
    if not candidatos:
        for no_texto in soup.find_all(
            string=True
        ):
            if (
                "compilacao monovigente"
                not in normalizar_busca(
                    str(no_texto)
                )
            ):
                continue

            atual = getattr(
                no_texto,
                "parent",
                None,
            )

            for _ in range(8):
                if atual is None:
                    break

                for link in atual.find_all(
                    "a",
                    href=True,
                ):
                    href = str(
                        link.get(
                            "href",
                            "",
                        )
                    ).strip()

                    if (
                        "/publicacao/"
                        in href
                    ):
                        candidatos.append(
                            urljoin(
                                str(resposta.url),
                                href,
                            )
                        )

                if candidatos:
                    break

                atual = getattr(
                    atual,
                    "parent",
                    None,
                )

            if candidatos:
                break

    # Estratégia terciária: inspeciona links do documento todo e
    # usa somente links /publicacao/ como candidatos. Isso é último recurso.
    if not candidatos:
        for link in soup.find_all(
            "a",
            href=True,
        ):
            href = str(
                link.get(
                    "href",
                    "",
                )
            ).strip()

            if (
                "/publicacao/"
                in href
            ):
                candidatos.append(
                    urljoin(
                        str(resposta.url),
                        href,
                    )
                )

    # Remove duplicatas preservando ordem.
    unicos = []

    vistos = set()

    for candidato in candidatos:
        if candidato in vistos:
            continue

        vistos.add(
            candidato
        )

        unicos.append(
            candidato
        )

    # Se houver mais de um /publicacao/, o candidato certo será validado
    # mais adiante. Primeiro tentamos o primeiro encontrado na linha
    # "Compilação Monovigente".
    resolvido = (
        unicos[0]
        if unicos
        else alvo[
            "fallback_publicacao"
        ]
    )

    return (
        resolvido,
        {
            "pagina_norma": str(
                resposta.url
            ),
            "candidatos_publicacao": (
                unicos
            ),
            "usou_fallback": (
                not bool(
                    unicos
                )
            ),
        },
    )


# =============================================================================
# EXTRAÇÃO DA PUBLICAÇÃO MONOVIGENTE
# =============================================================================

MARCADORES_FIM = [
    "ENGLISH",
    "ESPAÑOL",
    "FRANÇAIS",
    "Intranet",
    "Servidor efetivo",
    "Fale com o Senado",
    "Senado Federal - Praça dos Três Poderes",
]


def extrair_corpo_legal(
    resposta: requests.Response,
    alvo: dict,
) -> str:
    soup = BeautifulSoup(
        resposta.content,
        "html.parser",
    )

    # Retira apenas elementos que nunca fazem parte da lei.
    for nome in (
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
        "form",
    ):
        for tag in soup.find_all(
            nome
        ):
            try:
                tag.decompose()
            except AttributeError:
                pass

    texto_total = soup.get_text(
        "\n",
        strip=False,
    )

    linhas = [
        limpar_linha(
            linha
        )
        for linha in texto_total.splitlines()
    ]

    titulo_norm = normalizar_busca(
        alvo[
            "titulo_inicio"
        ]
    )

    inicio = None

    for indice, linha in enumerate(
        linhas
    ):
        if (
            titulo_norm
            in normalizar_busca(
                linha
            )
        ):
            inicio = indice
            break

    if inicio is None:
        raise RuntimeError(
            (
                "Não foi possível localizar o título legal "
                f"esperado: {alvo['titulo_inicio']}"
            )
        )

    fim = len(
        linhas
    )

    # Corta o chrome/footer do Senado.
    for indice in range(
        inicio + 1,
        len(
            linhas
        ),
    ):
        linha_norm = normalizar_busca(
            linhas[
                indice
            ]
        )

        for marcador in MARCADORES_FIM:
            if (
                linha_norm
                == normalizar_busca(
                    marcador
                )
                or (
                    "senado federal praca dos tres poderes"
                    in linha_norm
                )
            ):
                fim = indice
                break

        if fim != len(
            linhas
        ):
            break

    corpo = "\n".join(
        linhas[
            inicio:fim
        ]
    )

    return normalizar_quebras(
        corpo
    )


# =============================================================================
# DETECÇÃO E CANONIZAÇÃO DE CABEÇALHOS DE ARTIGOS
#
# Somente cabeçalhos que começam uma linha são aceitos.
# Assim referências internas ("nos termos do art. 827") não viram artigos.
# =============================================================================

PADRAO_ARTIGO_LINHA = re.compile(
    r"(?im)"
    r"^\s*"
    r"Art(?:igo)?"
    r"\s*\.?\s*"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,4})"
    r"\s*"
    r"(?:º|°|o)?"
    r"\s*"
    r"(?:[-–—]\s*([A-Za-z]{1,5}(?:-[A-Za-z]{1,5})*))?"
    r"(?:\s*[\.\-–—])?"
)


def canonizar_numero_artigo(
    numero_bruto: str,
    sufixo: str | None,
) -> str:
    numero = str(
        int(
            numero_bruto.replace(
                ".",
                "",
            )
        )
    )

    if sufixo:
        return (
            numero
            + "-"
            + sufixo.upper()
        )

    return numero


def artigos_cabecalho(
    texto: str,
) -> list[str]:
    encontrados = []

    for match in PADRAO_ARTIGO_LINHA.finditer(
        texto
    ):
        try:
            chave = canonizar_numero_artigo(
                match.group(
                    1
                ),
                match.group(
                    2
                ),
            )
        except Exception:
            continue

        encontrados.append(
            chave
        )

    return encontrados


# =============================================================================
# VALIDAÇÃO FORTE
# =============================================================================

def validar_fonte(
    alvo: dict,
    texto: str,
) -> dict:
    metricas = tamanho_texto(
        texto
    )

    artigos = artigos_cabecalho(
        texto
    )

    conjunto = set(
        artigos
    )

    faltantes_ancora = [
        ancora
        for ancora in alvo[
            "artigos_ancora"
        ]
        if ancora
        not in conjunto
    ]

    norm_texto = normalizar_busca(
        texto
    )

    frases_ausentes = [
        frase
        for frase in alvo[
            "frases_recentes"
        ]
        if normalizar_busca(
            frase
        )
        not in norm_texto
    ]

    motivos = []

    if (
        metricas[
            "caracteres"
        ]
        < alvo[
            "min_caracteres"
        ]
    ):
        motivos.append(
            (
                "texto menor que o mínimo de segurança: "
                f"{metricas['caracteres']} < "
                f"{alvo['min_caracteres']} caracteres"
            )
        )

    if (
        metricas[
            "linhas"
        ]
        < alvo[
            "min_linhas"
        ]
    ):
        motivos.append(
            (
                "texto com menos linhas que o mínimo de segurança: "
                f"{metricas['linhas']} < "
                f"{alvo['min_linhas']}"
            )
        )

    if (
        len(
            artigos
        )
        < alvo[
            "min_artigos"
        ]
    ):
        motivos.append(
            (
                "quantidade de cabeçalhos de artigos abaixo do mínimo: "
                f"{len(artigos)} < {alvo['min_artigos']}"
            )
        )

    if (
        alvo[
            "artigo_final"
        ]
        not in conjunto
    ):
        motivos.append(
            (
                "artigo final não encontrado como cabeçalho: "
                f"{alvo['artigo_final']}"
            )
        )

    if faltantes_ancora:
        motivos.append(
            (
                "artigos-âncora ausentes: "
                + ", ".join(
                    faltantes_ancora
                )
            )
        )

    if frases_ausentes:
        motivos.append(
            (
                "marcas de atualização recente ausentes: "
                + " | ".join(
                    frases_ausentes
                )
            )
        )

    # Verificações adicionais de começo/fim.
    if artigos:
        primeira_base = artigos[
            0
        ]

        if primeira_base != "1":
            motivos.append(
                (
                    "o primeiro cabeçalho detectado não é Art. 1: "
                    f"{primeira_base}"
                )
            )

    else:
        motivos.append(
            "nenhum cabeçalho de artigo foi detectado"
        )

    return {
        "valida": not bool(
            motivos
        ),
        "motivos": motivos,
        "metricas": metricas,
        "quantidade_artigos": len(
            artigos
        ),
        "artigos_unicos": len(
            set(
                artigos
            )
        ),
        "primeiro_artigo": (
            artigos[
                0
            ]
            if artigos
            else ""
        ),
        "ultimo_artigo_detectado": (
            artigos[
                -1
            ]
            if artigos
            else ""
        ),
        "artigo_final_presente": (
            alvo[
                "artigo_final"
            ]
            in conjunto
        ),
        "artigos_ancora_faltantes": (
            faltantes_ancora
        ),
        "frases_recentes_ausentes": (
            frases_ausentes
        ),
    }


# =============================================================================
# DOWNLOAD E ESCOLHA DA PUBLICAÇÃO CERTA
# =============================================================================

def baixar_candidato_oficial(
    sessao: requests.Session,
    alvo: dict,
) -> dict:
    (
        url_resolvida,
        info_resolucao,
    ) = resolver_compilacao_monovigente(
        sessao,
        alvo,
    )

    # Testa primeiro a URL dinâmica.
    urls_teste = [
        url_resolvida
    ]

    # Depois qualquer outro /publicacao/ encontrado.
    for candidata in info_resolucao[
        "candidatos_publicacao"
    ]:
        if candidata not in urls_teste:
            urls_teste.append(
                candidata
            )

    # Fallback conhecido por último.
    if (
        alvo[
            "fallback_publicacao"
        ]
        not in urls_teste
    ):
        urls_teste.append(
            alvo[
                "fallback_publicacao"
            ]
        )

    tentativas = []

    for url in urls_teste:
        try:
            resposta = requisitar(
                sessao,
                url,
            )

            texto = extrair_corpo_legal(
                resposta,
                alvo,
            )

            validacao = validar_fonte(
                alvo,
                texto,
            )

            tentativa = {
                "url_solicitada": url,
                "url_final": str(
                    resposta.url
                ),
                "http_status": (
                    resposta.status_code
                ),
                "bytes_html": len(
                    resposta.content
                ),
                "validacao": (
                    validacao
                ),
            }

            tentativas.append(
                tentativa
            )

            if validacao[
                "valida"
            ]:
                return {
                    "ok": True,
                    "texto": texto,
                    "url_publicacao": str(
                        resposta.url
                    ),
                    "validacao": (
                        validacao
                    ),
                    "resolucao": (
                        info_resolucao
                    ),
                    "tentativas": (
                        tentativas
                    ),
                }

        except Exception as erro:
            tentativas.append(
                {
                    "url_solicitada": url,
                    "erro": str(
                        erro
                    ),
                }
            )

    return {
        "ok": False,
        "texto": "",
        "url_publicacao": "",
        "validacao": None,
        "resolucao": (
            info_resolucao
        ),
        "tentativas": (
            tentativas
        ),
    }


# =============================================================================
# CANDIDATOS NO PC
# =============================================================================

def salvar_candidato_pc(
    alvo: dict,
    texto: str,
) -> Path:
    CANDIDATOS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        CANDIDATOS_DIR
        / f"{alvo['id']}.txt"
    )

    caminho.write_text(
        texto,
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# =============================================================================
# BACKUP E SUBSTITUIÇÃO TRANSACIONAL
# =============================================================================

def criar_backups(
    origem: Path,
    alvos: list[dict],
) -> tuple[Path, dict[str, Path]]:
    pasta_backup = (
        BACKUP_ROOT
        / (
            "antes_recuperacao_monovigente_"
            + timestamp()
        )
    )

    mapa = {}

    for alvo in alvos:
        origem_arquivo = (
            origem
            / alvo[
                "arquivo_relativo"
            ]
        )

        if not origem_arquivo.exists():
            raise FileNotFoundError(
                (
                    "Arquivo atual não encontrado para backup: "
                    f"{origem_arquivo}"
                )
            )

        destino = (
            pasta_backup
            / alvo[
                "arquivo_relativo"
            ]
        )

        destino.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            origem_arquivo,
            destino,
        )

        if (
            destino.stat().st_size
            != origem_arquivo.stat().st_size
        ):
            raise RuntimeError(
                (
                    "Backup com tamanho divergente: "
                    f"{origem_arquivo}"
                )
            )

        mapa[
            alvo[
                "id"
            ]
        ] = destino

    return (
        pasta_backup,
        mapa,
    )


def preparar_temporarios(
    origem: Path,
    candidatos: dict[str, dict],
) -> dict[str, Path]:
    temporarios = {}

    for alvo in ALVOS:
        identificador = alvo[
            "id"
        ]

        destino_final = (
            origem
            / alvo[
                "arquivo_relativo"
            ]
        )

        destino_final.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporario = destino_final.with_name(
            destino_final.name
            + ".novo_lex_machina"
        )

        texto = candidatos[
            identificador
        ][
            "texto"
        ]

        temporario.write_text(
            texto,
            encoding="utf-8",
            newline="\n",
        )

        # Reabre o arquivo temporário.
        texto_reaberto = temporario.read_text(
            encoding="utf-8",
        )

        validacao = validar_fonte(
            alvo,
            texto_reaberto,
        )

        if not validacao[
            "valida"
        ]:
            raise RuntimeError(
                (
                    "O arquivo temporário falhou na revalidação: "
                    f"{identificador} -> "
                    + "; ".join(
                        validacao[
                            "motivos"
                        ]
                    )
                )
            )

        hash_esperado = sha256_texto(
            texto
        )

        hash_reaberto = sha256_texto(
            texto_reaberto
        )

        if (
            hash_reaberto
            != hash_esperado
        ):
            raise RuntimeError(
                (
                    "Hash do temporário não confere: "
                    f"{identificador}"
                )
            )

        temporarios[
            identificador
        ] = temporario

    return temporarios


def restaurar_backups(
    origem: Path,
    backups: dict[str, Path],
):
    for alvo in ALVOS:
        identificador = alvo[
            "id"
        ]

        backup = backups.get(
            identificador
        )

        if (
            backup is None
            or not backup.exists()
        ):
            continue

        destino = (
            origem
            / alvo[
                "arquivo_relativo"
            ]
        )

        destino.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            backup,
            destino,
        )


def substituir_atomicamente(
    origem: Path,
    temporarios: dict[str, Path],
):
    for alvo in ALVOS:
        identificador = alvo[
            "id"
        ]

        destino = (
            origem
            / alvo[
                "arquivo_relativo"
            ]
        )

        temporario = temporarios[
            identificador
        ]

        os.replace(
            temporario,
            destino,
        )


def validar_finais(
    origem: Path,
    candidatos: dict[str, dict],
) -> dict[str, dict]:
    resultados = {}

    for alvo in ALVOS:
        identificador = alvo[
            "id"
        ]

        caminho = (
            origem
            / alvo[
                "arquivo_relativo"
            ]
        )

        texto = caminho.read_text(
            encoding="utf-8",
        )

        validacao = validar_fonte(
            alvo,
            texto,
        )

        hash_final = sha256_texto(
            texto
        )

        hash_candidato = sha256_texto(
            candidatos[
                identificador
            ][
                "texto"
            ]
        )

        hash_ok = (
            hash_final
            == hash_candidato
        )

        resultados[
            identificador
        ] = {
            "validacao": (
                validacao
            ),
            "hash_final": (
                hash_final
            ),
            "hash_candidato": (
                hash_candidato
            ),
            "hash_ok": (
                hash_ok
            ),
        }

        if (
            not validacao[
                "valida"
            ]
            or not hash_ok
        ):
            raise RuntimeError(
                (
                    "Validação final falhou após a substituição: "
                    f"{identificador}"
                )
            )

    return resultados


# =============================================================================
# RELATÓRIO
# =============================================================================

def escrever_relatorio(
    origem: Path,
    modo_aplicar: bool,
    resultados_fontes: dict[str, dict],
    candidatos_pc: dict[str, Path],
    status_aplicacao: str,
    pasta_backup: Path | None,
    validacao_final: dict[str, dict] | None,
):
    SAIDA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fontes_ok = sum(
        1
        for item in resultados_fontes.values()
        if item.get(
            "ok"
        )
    )

    linhas = [
        "LEX MACHINA",
        "RECUPERAÇÃO DEFINITIVA - CF88, CC2002 E ECA1990",
        "=" * 86,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        (
            "MODO: "
            + (
                "APLICAR"
                if modo_aplicar
                else "AUDITORIA / SEM ALTERAR O CARTÃO"
            )
        ),
        "",
        (
            "FONTE-BASE: Portal oficial de Legislação Federal "
            "do Senado Federal"
        ),
        (
            "CRITÉRIO: Compilação Monovigente / "
            "Compilação Monovigente na Câmara dos Deputados"
        ),
        "",
        f"FONTES VALIDADAS: {fontes_ok}/3",
        f"STATUS DA APLICAÇÃO: {status_aplicacao}",
        (
            f"BACKUP: {pasta_backup}"
            if pasta_backup
            else "BACKUP: não criado neste modo"
        ),
        "",
        "=" * 86,
        "RESULTADOS POR NORMA",
        "=" * 86,
        "",
    ]

    json_resultados = {}

    for alvo in ALVOS:
        identificador = alvo[
            "id"
        ]

        resultado = resultados_fontes[
            identificador
        ]

        linhas.append(
            (
                f"[{identificador}] "
                f"{alvo['nome']}"
            )
        )

        linhas.append(
            (
                "  Arquivo de destino: "
                f"{origem / alvo['arquivo_relativo']}"
            )
        )

        linhas.append(
            (
                "  Página da norma: "
                f"{alvo['norma_url']}"
            )
        )

        linhas.append(
            (
                "  Fonte validada: "
                f"{resultado.get('url_publicacao', '')}"
            )
        )

        if resultado.get(
            "ok"
        ):
            validacao = resultado[
                "validacao"
            ]

            linhas.append(
                (
                    "  Candidato no PC: "
                    f"{candidatos_pc.get(identificador, '')}"
                )
            )

            linhas.append(
                (
                    "  Caracteres: "
                    f"{validacao['metricas']['caracteres']}"
                )
            )

            linhas.append(
                (
                    "  Linhas: "
                    f"{validacao['metricas']['linhas']}"
                )
            )

            linhas.append(
                (
                    "  Cabeçalhos de artigo: "
                    f"{validacao['quantidade_artigos']}"
                )
            )

            linhas.append(
                (
                    "  Artigos únicos: "
                    f"{validacao['artigos_unicos']}"
                )
            )

            linhas.append(
                (
                    "  Primeiro artigo: "
                    f"{validacao['primeiro_artigo']}"
                )
            )

            linhas.append(
                (
                    "  Último cabeçalho detectado: "
                    f"{validacao['ultimo_artigo_detectado']}"
                )
            )

            linhas.append(
                (
                    "  Artigo final esperado presente: "
                    f"{validacao['artigo_final_presente']}"
                )
            )

            linhas.append(
                (
                    "  SHA-256 candidato: "
                    f"{validacao['metricas']['sha256']}"
                )
            )

            linhas.append(
                "  VALIDAÇÃO DA FONTE: APROVADA"
            )

            if (
                validacao_final
                and identificador
                in validacao_final
            ):
                final = validacao_final[
                    identificador
                ]

                linhas.append(
                    (
                        "  VALIDAÇÃO APÓS GRAVAÇÃO: "
                        + (
                            "APROVADA"
                            if (
                                final[
                                    "validacao"
                                ][
                                    "valida"
                                ]
                                and final[
                                    "hash_ok"
                                ]
                            )
                            else "FALHOU"
                        )
                    )
                )

        else:
            linhas.append(
                "  VALIDAÇÃO DA FONTE: FALHOU"
            )

            for tentativa in resultado.get(
                "tentativas",
                [],
            ):
                if tentativa.get(
                    "erro"
                ):
                    linhas.append(
                        (
                            "    ERRO: "
                            f"{tentativa['url_solicitada']} -> "
                            f"{tentativa['erro']}"
                        )
                    )

                elif tentativa.get(
                    "validacao"
                ):
                    linhas.append(
                        (
                            "    Fonte testada: "
                            f"{tentativa.get('url_final', '')}"
                        )
                    )

                    for motivo in tentativa[
                        "validacao"
                    ][
                        "motivos"
                    ]:
                        linhas.append(
                            f"      - {motivo}"
                        )

        linhas.append("")

        json_resultados[
            identificador
        ] = {
            "nome": alvo[
                "nome"
            ],
            "arquivo_destino": str(
                origem
                / alvo[
                    "arquivo_relativo"
                ]
            ),
            "norma_url": alvo[
                "norma_url"
            ],
            "fonte_ok": resultado.get(
                "ok",
                False,
            ),
            "url_publicacao": resultado.get(
                "url_publicacao",
                "",
            ),
            "validacao": resultado.get(
                "validacao"
            ),
            "candidato_pc": str(
                candidatos_pc.get(
                    identificador,
                    "",
                )
            ),
            "tentativas": resultado.get(
                "tentativas",
                [],
            ),
            "validacao_final": (
                validacao_final.get(
                    identificador
                )
                if validacao_final
                else None
            ),
        }

    linhas.extend(
        [
            "=" * 86,
            "CONCLUSÃO",
            "=" * 86,
            "",
        ]
    )

    if fontes_ok != 3:
        linhas.append(
            (
                "NÃO APLICAR. Pelo menos uma das três fontes "
                "não passou na validação forte."
            )
        )

    elif not modo_aplicar:
        linhas.append(
            (
                "AS 3 FONTES OFICIAIS PASSARAM. "
                "O cartão NÃO foi alterado neste modo."
            )
        )
        linhas.append(
            (
                "Para substituir os arquivos com backup e "
                "revalidação transacional, execute o mesmo "
                "script com --aplicar."
            )
        )

    elif status_aplicacao == "APLICADO_E_REVALIDADO":
        linhas.append(
            (
                "RECUPERAÇÃO CONCLUÍDA. "
                "Os 3 arquivos foram substituídos por compilações "
                "oficiais validadas e revalidados após a gravação."
            )
        )

    else:
        linhas.append(
            (
                "A APLICAÇÃO NÃO FOI CONCLUÍDA. "
                "Os arquivos originais foram preservados ou restaurados."
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
                "modo_aplicar": (
                    modo_aplicar
                ),
                "fontes_validadas": (
                    fontes_ok
                ),
                "status_aplicacao": (
                    status_aplicacao
                ),
                "pasta_backup": (
                    str(
                        pasta_backup
                    )
                    if pasta_backup
                    else ""
                ),
                "resultados": (
                    json_resultados
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


# =============================================================================
# MAIN
# =============================================================================

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

    SAIDA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    CANDIDATOS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print(
        "LEX MACHINA"
    )
    print(
        "RECUPERAÇÃO DEFINITIVA DOS 3 TEXTOS-BASE"
    )
    print(
        "=" * 74
    )
    print(
        f"Cartão: {origem}"
    )
    print(
        (
            "Modo: "
            + (
                "APLICAR COM BACKUP + ROLLBACK"
                if args.aplicar
                else "AUDITORIA / NÃO ALTERA O CARTÃO"
            )
        )
    )
    print()
    print(
        "Fonte: Senado Federal -> Compilação Monovigente"
    )
    print()

    sessao = nova_sessao()

    resultados_fontes = {}
    candidatos_pc = {}

    # -------------------------------------------------------------------------
    # 1. Baixa e valida as três fontes antes de qualquer alteração.
    # -------------------------------------------------------------------------

    for indice, alvo in enumerate(
        ALVOS,
        start=1,
    ):
        print(
            (
                f"[{indice}/3] "
                f"{alvo['id']} - {alvo['nome']}"
            )
        )

        resultado = baixar_candidato_oficial(
            sessao,
            alvo,
        )

        resultados_fontes[
            alvo[
                "id"
            ]
        ] = resultado

        if resultado[
            "ok"
        ]:
            caminho_pc = salvar_candidato_pc(
                alvo,
                resultado[
                    "texto"
                ],
            )

            candidatos_pc[
                alvo[
                    "id"
                ]
            ] = caminho_pc

            validacao = resultado[
                "validacao"
            ]

            print(
                (
                    "  FONTE APROVADA"
                    f" | chars={validacao['metricas']['caracteres']}"
                    f" | linhas={validacao['metricas']['linhas']}"
                    f" | artigos={validacao['quantidade_artigos']}"
                    f" | final={alvo['artigo_final']}"
                )
            )

            print(
                (
                    "  Publicação: "
                    f"{resultado['url_publicacao']}"
                )
            )

        else:
            print(
                "  FONTE REPROVADA / INCONCLUSIVA"
            )

            for tentativa in resultado[
                "tentativas"
            ]:
                if tentativa.get(
                    "erro"
                ):
                    print(
                        (
                            "    ERRO: "
                            f"{tentativa['erro']}"
                        )
                    )

                    continue

                validacao = tentativa.get(
                    "validacao"
                )

                if validacao:
                    for motivo in validacao[
                        "motivos"
                    ]:
                        print(
                            f"    - {motivo}"
                        )

        print()

    fontes_ok = all(
        resultados_fontes[
            alvo[
                "id"
            ]
        ][
            "ok"
        ]
        for alvo in ALVOS
    )

    # -------------------------------------------------------------------------
    # 2. Se qualquer fonte falhou, encerra SEM TOCAR NO CARTÃO.
    # -------------------------------------------------------------------------

    if not fontes_ok:
        escrever_relatorio(
            origem=origem,
            modo_aplicar=args.aplicar,
            resultados_fontes=(
                resultados_fontes
            ),
            candidatos_pc=(
                candidatos_pc
            ),
            status_aplicacao=(
                "NAO_APLICADO_FONTE_REPROVADA"
            ),
            pasta_backup=None,
            validacao_final=None,
        )

        print(
            "=" * 74
        )
        print(
            "RECUPERAÇÃO BLOQUEADA"
        )
        print(
            "As 3 fontes oficiais não passaram simultaneamente."
        )
        print(
            "Nenhum arquivo do cartão foi alterado."
        )
        print(
            f"Relatório: {REL_TXT}"
        )

        return

    # -------------------------------------------------------------------------
    # 3. Modo auditoria: para aqui. Os candidatos ficam no PC.
    # -------------------------------------------------------------------------

    if not args.aplicar:
        escrever_relatorio(
            origem=origem,
            modo_aplicar=False,
            resultados_fontes=(
                resultados_fontes
            ),
            candidatos_pc=(
                candidatos_pc
            ),
            status_aplicacao=(
                "NAO_APLICADO_MODO_AUDITORIA"
            ),
            pasta_backup=None,
            validacao_final=None,
        )

        print(
            "=" * 74
        )
        print(
            "FONTES VALIDADAS: 3/3"
        )
        print(
            "O CARTÃO NÃO FOI ALTERADO."
        )
        print()
        print(
            "Candidatos oficiais salvos em:"
        )
        print(
            f"  {CANDIDATOS_DIR}"
        )
        print()
        print(
            "Para aplicar com backup e rollback automático:"
        )
        print(
            r"  python recuperar_3_definitivo.py D:\ --aplicar"
        )
        print()
        print(
            f"Relatório: {REL_TXT}"
        )

        return

    # -------------------------------------------------------------------------
    # 4. Aplicação transacional.
    # -------------------------------------------------------------------------

    pasta_backup = None
    backups = {}
    temporarios = {}
    validacao_final = None
    status_aplicacao = (
        "INICIANDO"
    )

    try:
        print(
            "=" * 74
        )
        print(
            "AS 3 FONTES PASSARAM."
        )
        print(
            "Iniciando backup e substituição transacional..."
        )
        print()

        (
            pasta_backup,
            backups,
        ) = criar_backups(
            origem,
            ALVOS,
        )

        print(
            f"Backup criado em: {pasta_backup}"
        )

        temporarios = preparar_temporarios(
            origem,
            resultados_fontes,
        )

        print(
            "3 arquivos temporários gravados e revalidados."
        )

        substituir_atomicamente(
            origem,
            temporarios,
        )

        print(
            "Substituição atômica concluída."
        )

        validacao_final = validar_finais(
            origem,
            resultados_fontes,
        )

        status_aplicacao = (
            "APLICADO_E_REVALIDADO"
        )

        print(
            "Revalidação final: 3/3 APROVADOS."
        )

    except Exception as erro:
        status_aplicacao = (
            "FALHOU_ROLLBACK_EXECUTADO"
        )

        print()
        print(
            "FALHA DURANTE A APLICAÇÃO:"
        )
        print(
            erro
        )
        print(
            "Restaurando os arquivos anteriores..."
        )

        try:
            if backups:
                restaurar_backups(
                    origem,
                    backups,
                )

            print(
                "Rollback concluído."
            )

        except Exception as rollback_erro:
            status_aplicacao = (
                "FALHA_CRITICA_ROLLBACK"
            )

            print(
                "ERRO CRÍTICO NO ROLLBACK:"
            )
            print(
                rollback_erro
            )

        # Limpa temporários remanescentes.
        for temporario in temporarios.values():
            try:
                if temporario.exists():
                    temporario.unlink()
            except Exception:
                pass

    escrever_relatorio(
        origem=origem,
        modo_aplicar=True,
        resultados_fontes=(
            resultados_fontes
        ),
        candidatos_pc=(
            candidatos_pc
        ),
        status_aplicacao=(
            status_aplicacao
        ),
        pasta_backup=(
            pasta_backup
        ),
        validacao_final=(
            validacao_final
        ),
    )

    print()
    print(
        "=" * 74
    )
    print(
        "RESULTADO FINAL"
    )
    print(
        f"STATUS: {status_aplicacao}"
    )
    print(
        f"Relatório: {REL_TXT}"
    )

    if (
        status_aplicacao
        == "APLICADO_E_REVALIDADO"
    ):
        print()
        print(
            "Os três arquivos foram recuperados e validados."
        )
        print(
            "NÃO rode ainda o main.py nem o gerador de índices."
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
