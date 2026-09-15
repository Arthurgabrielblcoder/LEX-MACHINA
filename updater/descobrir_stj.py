from datetime import datetime
from pathlib import Path
import csv
import io
import json
import re
import unicodedata

import requests


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO_JURISPRUDENCIA = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_SAIDA = Path(
    "saida/99_INDICES"
)

PASTA_CACHE = Path(
    "cache_stj"
)


URL_TEMAS = (
    "https://dadosabertos.web.stj.jus.br/"
    "dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/"
    "resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/"
    "download/temas.csv"
)


URL_PROCESSOS = (
    "https://dadosabertos.web.stj.jus.br/"
    "dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/"
    "resource/7ed21202-0049-4fcb-aa7c-48d810d3c499/"
    "download/processos.csv"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131 Safari/537.36"
    )
}


# ============================================================
# TERMOS CONSUMERISTAS
# ============================================================

TERMOS_PESOS = {
    "codigo de defesa do consumidor": 100,
    "código de defesa do consumidor": 100,
    "lei 8.078": 100,
    "lei nº 8.078": 100,
    "lei n. 8.078": 100,
    "lei 8078": 100,
    "cdc": 60,
    "direito do consumidor": 80,
    "consumerista": 50,
    "consumidor": 30,
    "fornecedor": 25,

    "cadastro de inadimplentes": 30,
    "cadastro de proteção ao crédito": 30,
    "cadastro de protecao ao credito": 30,
    "cadastro negativo": 25,
    "negativação": 25,
    "negativacao": 25,
    "inscrição indevida": 20,
    "inscricao indevida": 20,
    "serasa": 20,
    "spc": 20,
    "score de crédito": 20,
    "score de credito": 20,

    "instituição financeira": 20,
    "instituicao financeira": 20,
    "instituições financeiras": 20,
    "instituicoes financeiras": 20,
    "fraude bancária": 20,
    "fraude bancaria": 20,
    "operação bancária": 15,
    "operacao bancaria": 15,
    "cartão de crédito": 15,
    "cartao de credito": 15,

    "plano de saúde": 25,
    "plano de saude": 25,
    "planos de saúde": 25,
    "planos de saude": 25,
    "operadora de plano": 20,
    "seguro-saúde": 20,
    "seguro-saude": 20,
    "ans": 6,

    "vício do produto": 20,
    "vicio do produto": 20,
    "vício do serviço": 20,
    "vicio do servico": 20,
    "defeito do produto": 20,
    "defeito do serviço": 20,
    "defeito do servico": 20,
    "fato do produto": 20,
    "fato do serviço": 20,
    "fato do servico": 20,

    "responsabilidade objetiva": 8,
    "prática abusiva": 20,
    "pratica abusiva": 20,
    "cláusula abusiva": 20,
    "clausula abusiva": 20,
    "contrato de adesão": 15,
    "contrato de adesao": 15,
    "cobrança indevida": 18,
    "cobranca indevida": 18,
    "repetição de indébito": 12,
    "repeticao de indebito": 12,

    "comércio eletrônico": 20,
    "comercio eletronico": 20,
    "marketplace": 15,
    "plataforma digital": 10,

    "telefonia": 12,
    "telecomunicações": 10,
    "telecomunicacoes": 10,

    "energia elétrica": 12,
    "energia eletrica": 12,

    "transporte aéreo": 12,
    "transporte aereo": 12,
    "passageiro": 8,

    "seguro": 5,

    "superendividamento": 30,
}


PONTUACAO_MINIMA = 15


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def remover_acentos(texto):
    texto = str(
        texto or ""
    )

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )


def normalizar(texto):
    texto = remover_acentos(
        texto
    )

    texto = texto.casefold()

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def normalizar_chave(texto):
    texto = normalizar(
        texto
    )

    return re.sub(
        r"[^a-z0-9]",
        "",
        texto,
    )


# ============================================================
# DOWNLOAD
# ============================================================

def baixar_csv(
    url,
    nome_cache,
):
    print(
        f"Baixando base oficial: "
        f"{nome_cache}"
    )

    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=90,
    )

    resposta.raise_for_status()

    PASTA_CACHE.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_CACHE
        / nome_cache
    )

    caminho.write_bytes(
        resposta.content
    )

    print(
        f"OK: {caminho}"
    )

    return resposta.content


# ============================================================
# DECODIFICAÇÃO
# ============================================================

def decodificar_csv(
    conteudo
):
    codificacoes = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "iso-8859-1",
    ]

    for codificacao in codificacoes:
        try:
            texto = conteudo.decode(
                codificacao,
                errors="strict",
            )

            return (
                texto,
                codificacao,
            )

        except UnicodeDecodeError:
            continue

    return (
        conteudo.decode(
            "cp1252",
            errors="replace",
        ),
        "cp1252",
    )


# ============================================================
# SEPARADOR
# ============================================================

def detectar_separador(
    texto
):
    primeira_linha = ""

    for linha in texto.splitlines():
        if linha.strip():
            primeira_linha = linha
            break

    candidatos = [
        ";",
        ",",
        "\t",
        "|",
    ]

    melhor = ";"
    maior = -1

    for separador in candidatos:
        quantidade = (
            primeira_linha.count(
                separador
            )
        )

        if quantidade > maior:
            maior = quantidade
            melhor = separador

    return melhor


# ============================================================
# LEITURA ROBUSTA
# ============================================================

def ler_csv(
    conteudo
):
    texto, codificacao = (
        decodificar_csv(
            conteudo
        )
    )

    separador = detectar_separador(
        texto
    )

    arquivo_virtual = io.StringIO(
        texto,
        newline="",
    )

    leitor = csv.DictReader(
        arquivo_virtual,
        delimiter=separador,
        quotechar='"',
        doublequote=True,
    )

    registros = []

    for linha in leitor:
        if not linha:
            continue

        registro = {}

        for chave, valor in (
            linha.items()
        ):
            if chave is None:
                continue

            chave = (
                str(chave)
                .replace(
                    "\ufeff",
                    "",
                )
                .strip()
            )

            if isinstance(
                valor,
                list,
            ):
                valor = " ".join(
                    str(item)
                    for item in valor
                    if item is not None
                )

            if valor is None:
                valor = ""

            registro[
                chave
            ] = str(
                valor
            ).strip()

        if registro:
            registros.append(
                registro
            )

    return (
        registros,
        codificacao,
        separador,
    )


# ============================================================
# ACESSO FLEXÍVEL A CAMPOS
# ============================================================

def campo(
    registro,
    *nomes,
):
    mapa = {
        normalizar_chave(
            chave
        ): valor
        for chave, valor
        in registro.items()
    }

    for nome in nomes:
        chave = normalizar_chave(
            nome
        )

        if chave in mapa:
            return str(
                mapa[chave]
            ).strip()

    return ""


# ============================================================
# NÚMERO DO PRECEDENTE
# ============================================================

def numero_precedente(
    registro
):
    valor = campo(
        registro,
        "numeroPrecedente",
        "numeroTema",
        "numero",
    )

    numeros = re.findall(
        r"\d+",
        valor,
    )

    if not numeros:
        return None

    try:
        return int(
            numeros[0]
        )

    except ValueError:
        return None


# ============================================================
# SEQUENCIAL
# ============================================================

def sequencial_precedente(
    registro
):
    return campo(
        registro,
        "sequencialPrecedente",
    )


# ============================================================
# TIPO
# ============================================================

def tipo_precedente(
    registro
):
    return campo(
        registro,
        "tipoPrecedente",
        "tipo",
    )


# ============================================================
# CATÁLOGO LOCAL
# ============================================================

def carregar_catalogo_local():
    if not (
        CATALOGO_JURISPRUDENCIA.exists()
    ):
        return []

    return json.loads(
        CATALOGO_JURISPRUDENCIA.read_text(
            encoding="utf-8"
        )
    )


def temas_ja_cadastrados(
    catalogo
):
    numeros = set()

    for item in catalogo:
        if (
            item.get(
                "tribunal"
            ) == "STJ"
            and item.get(
                "tipo"
            ) == "repetitivo"
        ):
            try:
                numeros.add(
                    int(
                        item[
                            "numero"
                        ]
                    )
                )

            except (
                KeyError,
                ValueError,
                TypeError,
            ):
                continue

    return numeros


# ============================================================
# APRENDIZADO DO TIPO REAL DOS TEMAS REPETITIVOS
# ============================================================

def aprender_tipos_repetitivos(
    temas,
    temas_conhecidos,
):
    tipos = set()

    encontrados = {}

    for registro in temas:
        numero = numero_precedente(
            registro
        )

        if (
            numero is None
            or numero
            not in temas_conhecidos
        ):
            continue

        tipo = tipo_precedente(
            registro
        )

        encontrados[
            numero
        ] = tipo

        if tipo:
            tipos.add(
                normalizar(
                    tipo
                )
            )

    return (
        tipos,
        encontrados,
    )


# ============================================================
# LISTA DE TODOS OS TIPOS EXISTENTES
# ============================================================

def contar_tipos(
    temas
):
    contagem = {}

    for registro in temas:
        tipo = tipo_precedente(
            registro
        ).strip()

        if not tipo:
            tipo = (
                "[CAMPO VAZIO]"
            )

        contagem[
            tipo
        ] = (
            contagem.get(
                tipo,
                0,
            )
            + 1
        )

    return contagem


# ============================================================
# DETECÇÃO ADAPTATIVA DE TEMA REPETITIVO
# ============================================================

def eh_tema_repetitivo(
    registro,
    tipos_aprendidos,
    conhecidos,
):
    numero = numero_precedente(
        registro
    )

    # --------------------------------------------------------
    # PRIMEIRO: UM TEMA QUE JÁ CONHECEMOS É SEMPRE ACEITO.
    # --------------------------------------------------------

    if (
        numero is not None
        and numero in conhecidos
    ):
        return True

    tipo_original = tipo_precedente(
        registro
    )

    tipo = normalizar(
        tipo_original
    )

    # --------------------------------------------------------
    # SEGUNDO: USA O TIPO REAL APRENDIDO DOS TEMAS CONHECIDOS.
    # --------------------------------------------------------

    if (
        tipo
        and tipo in tipos_aprendidos
    ):
        return True

    # --------------------------------------------------------
    # TERCEIRO: FALLBACK SEMÂNTICO.
    # --------------------------------------------------------

    expressoes = [
        "repetitivo",
        "repetitivos",
        "recurso repetitivo",
        "recursos repetitivos",
        "tema repetitivo",
    ]

    if any(
        expressao in tipo
        for expressao in expressoes
    ):
        return True

    # --------------------------------------------------------
    # QUARTO: ALGUMAS BASES PODEM USAR APENAS SIGLA.
    # --------------------------------------------------------

    if tipo in {
        "rr",
        "repet",
        "rep",
    }:
        return True

    return False


# ============================================================
# TEXTO PARA CLASSIFICAÇÃO
# ============================================================

def texto_classificacao(
    registro
):
    nomes = [
        "questaoSubmetidaAJulgamento",
        "teseFirmada",
        "informacoesComplementares",
        "anotacoesNUGEPNAC",
        "delimitacaoJulgado",
        "entendimentoAnterior",
        "referenciaLegislativa",
        "referenciaSumular",
        "sumulaOriginada",
        "Assuntos",
        "descricaoRepercussaoGeral",
    ]

    partes = []

    for nome in nomes:
        valor = campo(
            registro,
            nome,
        )

        if valor:
            partes.append(
                valor
            )

    return " ".join(
        partes
    )


# ============================================================
# CLASSIFICAÇÃO CONSUMERISTA
# ============================================================

def calcular_pontuacao(
    registro
):
    texto = normalizar(
        texto_classificacao(
            registro
        )
    )

    pontos = 0
    motivos = []

    referencia = normalizar(
        campo(
            registro,
            "referenciaLegislativa",
        )
    )

    referencias_cdc = [
        "lei 8078",
        "codigo de defesa do consumidor",
    ]

    if any(
        normalizar(item)
        in referencia
        for item in referencias_cdc
    ):
        pontos += 150

        motivos.append(
            "Referência legislativa ao CDC"
        )

    termos_contados = set()

    for termo_original, peso in (
        TERMOS_PESOS.items()
    ):
        termo = normalizar(
            termo_original
        )

        if (
            termo
            and termo in texto
            and termo
            not in termos_contados
        ):
            pontos += peso

            termos_contados.add(
                termo
            )

            motivos.append(
                termo_original
            )

    motivos = list(
        dict.fromkeys(
            motivos
        )
    )

    return (
        pontos,
        motivos,
    )


# ============================================================
# PROCESSOS
# ============================================================

def agrupar_processos(
    registros
):
    mapa = {}

    for registro in registros:
        sequencial = campo(
            registro,
            "sequencialPrecedente",
        )

        if not sequencial:
            continue

        processo = campo(
            registro,
            "Processo",
            "processo",
            "numeroProcesso",
        )

        if not processo:
            continue

        mapa.setdefault(
            sequencial,
            [],
        )

        if (
            processo
            not in mapa[
                sequencial
            ]
        ):
            mapa[
                sequencial
            ].append(
                processo
            )

    return mapa


# ============================================================
# URL OFICIAL
# ============================================================

def url_tema_stj(
    numero
):
    return (
        "https://processo.stj.jus.br/"
        "repetitivos/temas_repetitivos/"
        "pesquisa.jsp"
        f"?cod_tema_inicial={numero}"
        f"&cod_tema_final={numero}"
        "&novaConsulta=true"
        "&tipo_pesquisa=T"
    )


# ============================================================
# CONSTRUÇÃO DOS CANDIDATOS
# ============================================================

def construir_candidatos(
    temas,
    processos_por_sequencial,
    existentes,
    tipos_aprendidos,
):
    candidatos = []

    total_repetitivos = 0
    sem_numero = 0

    for registro in temas:
        if not eh_tema_repetitivo(
            registro,
            tipos_aprendidos,
            existentes,
        ):
            continue

        total_repetitivos += 1

        numero = numero_precedente(
            registro
        )

        if numero is None:
            sem_numero += 1
            continue

        pontos, motivos = (
            calcular_pontuacao(
                registro
            )
        )

        # ----------------------------------------------------
        # TEMAS JÁ CADASTRADOS ENTRAM MESMO COM SCORE BAIXO.
        #
        # Isso funciona como teste de sanidade.
        # ----------------------------------------------------

        if (
            numero not in existentes
            and pontos
            < PONTUACAO_MINIMA
        ):
            continue

        sequencial = (
            sequencial_precedente(
                registro
            )
        )

        processos = (
            processos_por_sequencial.get(
                sequencial,
                [],
            )
        )

        candidato = {
            "numero": numero,

            "tipo_precedente_original": (
                tipo_precedente(
                    registro
                )
            ),

            "ja_cadastrado": (
                numero
                in existentes
            ),

            "pontuacao_consumidor": (
                pontos
            ),

            "motivos": motivos,

            "situacao": campo(
                registro,
                "situacao",
            ),

            "data_primeira_afetacao": campo(
                registro,
                "dataPrimeiraAfetacao",
            ),

            "data_julgamento": campo(
                registro,
                "dataJulgamento",
            ),

            "orgao_julgador": campo(
                registro,
                "orgaoJulgador",
            ),

            "assuntos": campo(
                registro,
                "Assuntos",
            ),

            "questao_oficial": campo(
                registro,
                "questaoSubmetidaAJulgamento",
            ),

            "tese_oficial": campo(
                registro,
                "teseFirmada",
            ),

            "informacoes_complementares": campo(
                registro,
                "informacoesComplementares",
            ),

            "referencia_legislativa": campo(
                registro,
                "referenciaLegislativa",
            ),

            "referencia_sumular": campo(
                registro,
                "referenciaSumular",
            ),

            "processos": processos,

            "sequencial_precedente": (
                sequencial
            ),

            "url_oficial": (
                url_tema_stj(
                    numero
                )
            ),
        }

        candidatos.append(
            candidato
        )

    # --------------------------------------------------------
    # REMOVE DUPLICIDADE
    # --------------------------------------------------------

    melhores = {}

    for candidato in candidatos:
        numero = candidato[
            "numero"
        ]

        atual = melhores.get(
            numero
        )

        if (
            atual is None
            or candidato[
                "pontuacao_consumidor"
            ]
            > atual[
                "pontuacao_consumidor"
            ]
        ):
            melhores[
                numero
            ] = candidato

    candidatos = list(
        melhores.values()
    )

    candidatos.sort(
        key=lambda item: (
            item[
                "ja_cadastrado"
            ],
            -item[
                "pontuacao_consumidor"
            ],
            item[
                "numero"
            ],
        )
    )

    return (
        candidatos,
        total_repetitivos,
        sem_numero,
    )


# ============================================================
# DIAGNÓSTICO
# ============================================================

def salvar_diagnostico(
    temas,
    processos,
    tipos,
    aprendidos,
    encontrados,
):
    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_SAIDA
        / "DIAGNOSTICO_STJ.txt"
    )

    linhas = [
        "LEX MACHINA",
        "DIAGNÓSTICO DA BASE DE PRECEDENTES DO STJ",
        "=" * 76,
        "",
        "COLUNAS TEMAS.CSV:",
    ]

    if temas:
        for coluna in temas[
            0
        ].keys():
            linhas.append(
                f"- {coluna}"
            )

    linhas.extend(
        [
            "",
            "COLUNAS PROCESSOS.CSV:",
        ]
    )

    if processos:
        for coluna in processos[
            0
        ].keys():
            linhas.append(
                f"- {coluna}"
            )

    linhas.extend(
        [
            "",
            "=" * 76,
            "VALORES ENCONTRADOS EM tipoPrecedente:",
        ]
    )

    for tipo, quantidade in sorted(
        tipos.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):
        linhas.append(
            f"- {tipo}: {quantidade}"
        )

    linhas.extend(
        [
            "",
            "=" * 76,
            "TEMAS CONHECIDOS LOCALIZADOS:",
        ]
    )

    for numero in sorted(
        encontrados.keys()
    ):
        linhas.append(
            f"- Tema {numero}: "
            f"tipoPrecedente = "
            f"{repr(encontrados[numero])}"
        )

    linhas.extend(
        [
            "",
            "TIPOS APRENDIDOS COMO REPETITIVOS:",
        ]
    )

    if aprendidos:
        for tipo in sorted(
            aprendidos
        ):
            linhas.append(
                f"- {tipo}"
            )
    else:
        linhas.append(
            "- Nenhum tipo pôde ser aprendido."
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
# JSON
# ============================================================

def salvar_json(
    candidatos,
    total_repetitivos,
):
    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_SAIDA
        / "CANDIDATOS_STJ_CONSUMIDOR.json"
    )

    estrutura = {
        "gerado_em": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),

        "fonte": (
            "Portal de Dados Abertos "
            "do Superior Tribunal de Justiça"
        ),

        "pontuacao_minima": (
            PONTUACAO_MINIMA
        ),

        "total_temas_repetitivos": (
            total_repetitivos
        ),

        "quantidade_candidatos": (
            len(
                candidatos
            )
        ),

        "candidatos": (
            candidatos
        ),
    }

    caminho.write_text(
        json.dumps(
            estrutura,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return caminho


# ============================================================
# RESUMO
# ============================================================

def resumo_texto(
    texto,
    limite=350,
):
    texto = re.sub(
        r"\s+",
        " ",
        str(
            texto or ""
        ),
    ).strip()

    if len(
        texto
    ) <= limite:
        return texto

    return (
        texto[
            : limite - 3
        ].rstrip()
        + "..."
    )


# ============================================================
# RELATÓRIO
# ============================================================

def salvar_relatorio(
    candidatos,
    total_registros,
    total_repetitivos,
    existentes,
):
    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_SAIDA
        / "RELATORIO_DESCOBERTA_STJ.txt"
    )

    novos = [
        item
        for item in candidatos
        if not item[
            "ja_cadastrado"
        ]
    ]

    cadastrados = [
        item
        for item in candidatos
        if item[
            "ja_cadastrado"
        ]
    ]

    linhas = [
        "LEX MACHINA",
        "DESCOBERTA DE TEMAS REPETITIVOS - STJ",
        "=" * 76,
        "",
        (
            "GERADO EM: "
            + datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        ),
        "",
        (
            f"REGISTROS TOTAIS: "
            f"{total_registros}"
        ),
        (
            f"TEMAS REPETITIVOS IDENTIFICADOS: "
            f"{total_repetitivos}"
        ),
        (
            "TEMAS REPETITIVOS JÁ CADASTRADOS: "
            f"{len(existentes)}"
        ),
        (
            "CANDIDATOS CONSUMERISTAS: "
            f"{len(candidatos)}"
        ),
        (
            "NOVOS CANDIDATOS: "
            f"{len(novos)}"
        ),
        (
            "JÁ CADASTRADOS RECONHECIDOS: "
            f"{len(cadastrados)}"
        ),
        "",
        "=" * 76,
        "NOVOS CANDIDATOS",
        "=" * 76,
        "",
    ]

    for candidato in novos:
        linhas.extend(
            [
                (
                    f"TEMA "
                    f"{candidato['numero']} "
                    f"| SCORE "
                    f"{candidato['pontuacao_consumidor']}"
                ),

                (
                    "TIPO STJ: "
                    f"{candidato['tipo_precedente_original']}"
                ),

                (
                    "SITUAÇÃO: "
                    f"{candidato['situacao']}"
                ),

                (
                    "QUESTÃO: "
                    + resumo_texto(
                        candidato[
                            "questao_oficial"
                        ]
                    )
                ),

                (
                    "TESE: "
                    + resumo_texto(
                        candidato[
                            "tese_oficial"
                        ]
                    )
                ),

                (
                    "REFERÊNCIA LEGISLATIVA: "
                    + resumo_texto(
                        candidato[
                            "referencia_legislativa"
                        ]
                    )
                ),

                (
                    "MOTIVOS: "
                    + ", ".join(
                        candidato[
                            "motivos"
                        ]
                    )
                ),

                (
                    "URL: "
                    f"{candidato['url_oficial']}"
                ),

                "",
                "-" * 76,
                "",
            ]
        )

    caminho.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return (
        caminho,
        len(novos),
        len(cadastrados),
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print(
        "LEX MACHINA - DESCOBERTA STJ"
    )
    print(
        "=" * 50
    )
    print()

    try:
        conteudo_temas = baixar_csv(
            URL_TEMAS,
            "Temas.csv",
        )

        conteudo_processos = baixar_csv(
            URL_PROCESSOS,
            "Processos.csv",
        )

    except requests.RequestException as erro:
        print()
        print(
            "ERRO AO BAIXAR BASE:"
        )
        print(
            erro
        )
        return

    print()
    print(
        "Lendo arquivos oficiais..."
    )

    temas, cod_temas, sep_temas = (
        ler_csv(
            conteudo_temas
        )
    )

    (
        processos,
        cod_processos,
        sep_processos,
    ) = ler_csv(
        conteudo_processos
    )

    print(
        f"Registros Temas.csv: "
        f"{len(temas)}"
    )

    print(
        f"Registros Processos.csv: "
        f"{len(processos)}"
    )

    print(
        f"Separador Temas: "
        f"{repr(sep_temas)}"
    )

    print(
        f"Separador Processos: "
        f"{repr(sep_processos)}"
    )

    print()

    catalogo = (
        carregar_catalogo_local()
    )

    existentes = (
        temas_ja_cadastrados(
            catalogo
        )
    )

    print(
        "Temas repetitivos já cadastrados: "
        f"{sorted(existentes)}"
    )

    print()
    print(
        "Aprendendo como o STJ identifica "
        "Temas Repetitivos..."
    )

    (
        tipos_aprendidos,
        temas_conhecidos_encontrados,
    ) = aprender_tipos_repetitivos(
        temas,
        existentes,
    )

    print(
        "Temas conhecidos localizados: "
        f"{len(temas_conhecidos_encontrados)}"
    )

    for numero in sorted(
        temas_conhecidos_encontrados
    ):
        print(
            f"  Tema {numero}: "
            f"{repr(temas_conhecidos_encontrados[numero])}"
        )

    print()

    print(
        "Tipos aprendidos: "
        f"{sorted(tipos_aprendidos)}"
    )

    tipos = contar_tipos(
        temas
    )

    processos_por_sequencial = (
        agrupar_processos(
            processos
        )
    )

    print()
    print(
        "Precedentes com processos relacionados: "
        f"{len(processos_por_sequencial)}"
    )

    print()
    print(
        "Classificando Temas Repetitivos..."
    )

    (
        candidatos,
        total_repetitivos,
        sem_numero,
    ) = construir_candidatos(
        temas,
        processos_por_sequencial,
        existentes,
        tipos_aprendidos,
    )

    novos = [
        item
        for item in candidatos
        if not item[
            "ja_cadastrado"
        ]
    ]

    reconhecidos = [
        item
        for item in candidatos
        if item[
            "ja_cadastrado"
        ]
    ]

    diagnostico = salvar_diagnostico(
        temas,
        processos,
        tipos,
        tipos_aprendidos,
        temas_conhecidos_encontrados,
    )

    print()
    print(
        "RESULTADO DA DESCOBERTA"
    )

    print(
        "=" * 50
    )

    print(
        f"Registros analisados: "
        f"{len(temas)}"
    )

    print(
        f"Temas Repetitivos identificados: "
        f"{total_repetitivos}"
    )

    print(
        f"Candidatos consumeristas: "
        f"{len(candidatos)}"
    )

    print(
        f"Novos candidatos: "
        f"{len(novos)}"
    )

    print(
        "Já cadastrados reconhecidos: "
        f"{len(reconhecidos)}"
    )

    print(
        f"Temas sem número: "
        f"{sem_numero}"
    )

    json_candidatos = salvar_json(
        candidatos,
        total_repetitivos,
    )

    (
        relatorio,
        quantidade_novos,
        quantidade_reconhecidos,
    ) = salvar_relatorio(
        candidatos,
        len(temas),
        total_repetitivos,
        existentes,
    )

    print()
    print(
        f"Diagnóstico: {diagnostico}"
    )

    print(
        f"JSON: {json_candidatos}"
    )

    print(
        f"Relatório: {relatorio}"
    )

    print()
    print(
        "TESTE DE SANIDADE:"
    )

    print(
        "Temas conhecidos encontrados: "
        f"{len(temas_conhecidos_encontrados)}"
        f"/{len(existentes)}"
    )

    print(
        "Temas conhecidos reconhecidos "
        "como candidatos: "
        f"{quantidade_reconhecidos}"
        f"/{len(existentes)}"
    )

    print()

    print(
        "Nenhum candidato foi adicionado "
        "automaticamente ao catálogo."
    )

    print(
        "Novos candidatos aguardando revisão: "
        f"{quantidade_novos}"
    )


if __name__ == "__main__":
    main()