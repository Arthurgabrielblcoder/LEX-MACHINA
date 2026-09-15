from datetime import datetime
from pathlib import Path
import json
import re
import unicodedata


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO_CANDIDATOS = Path(
    "saida/99_INDICES/CANDIDATOS_STJ_CONSUMIDOR.json"
)

PASTA_SAIDA = Path(
    "saida/99_INDICES"
)


ARQUIVO_CLASSE_A = (
    PASTA_SAIDA
    / "STJ_CLASSE_A_CONSUMIDOR_DIRETO.json"
)

ARQUIVO_CLASSE_B = (
    PASTA_SAIDA
    / "STJ_CLASSE_B_CONSUMIDOR_PROVAVEL.json"
)

ARQUIVO_CLASSE_C = (
    PASTA_SAIDA
    / "STJ_CLASSE_C_REVISAR.json"
)

ARQUIVO_RELATORIO = (
    PASTA_SAIDA
    / "RELATORIO_TRIAGEM_STJ.txt"
)


# ============================================================
# TERMOS DE ALTA CONFIANÇA
# ============================================================

TERMOS_DIRETOS = [
    "codigo de defesa do consumidor",
    "código de defesa do consumidor",
    "lei 8.078",
    "lei 8078",
    "cdc",
    "direito do consumidor",
    "consumerista",
    "consumidor",
    "fornecedor",
]


# ============================================================
# TERMOS DE FORTE PROBABILIDADE
# ============================================================

TERMOS_PROVAVEIS = [
    "plano de saúde",
    "plano de saude",
    "planos de saúde",
    "planos de saude",
    "operadora de plano",
    "seguro-saúde",
    "seguro-saude",

    "instituição financeira",
    "instituicao financeira",
    "instituições financeiras",
    "instituicoes financeiras",

    "fraude bancária",
    "fraude bancaria",
    "cartão de crédito",
    "cartao de credito",

    "cadastro de inadimplentes",
    "cadastro negativo",
    "negativação",
    "negativacao",
    "serasa",
    "spc",
    "proteção ao crédito",
    "protecao ao credito",

    "prática abusiva",
    "pratica abusiva",
    "cláusula abusiva",
    "clausula abusiva",

    "vício do produto",
    "vicio do produto",
    "vício do serviço",
    "vicio do servico",

    "defeito do produto",
    "defeito do serviço",
    "defeito do servico",

    "cobrança indevida",
    "cobranca indevida",

    "comércio eletrônico",
    "comercio eletronico",
    "marketplace",

    "superendividamento",
]


# ============================================================
# TERMOS AMBÍGUOS
# ============================================================

TERMOS_AMBIGUOS = [
    "dano moral",
    "responsabilidade objetiva",
    "indenização",
    "indenizacao",
    "seguro",
    "passageiro",
    "banco",
    "crédito",
    "credito",
    "contrato",
    "serviço",
    "servico",
    "produto",
]


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


# ============================================================
# CARREGAMENTO
# ============================================================

def carregar_candidatos():
    if not ARQUIVO_CANDIDATOS.exists():
        raise FileNotFoundError(
            "Arquivo de candidatos não encontrado: "
            f"{ARQUIVO_CANDIDATOS}"
        )

    dados = json.loads(
        ARQUIVO_CANDIDATOS.read_text(
            encoding="utf-8"
        )
    )

    candidatos = dados.get(
        "candidatos",
        []
    )

    if not isinstance(
        candidatos,
        list,
    ):
        raise ValueError(
            "O arquivo de candidatos não contém "
            "uma lista válida."
        )

    return candidatos


# ============================================================
# TEXTO TOTAL DO CANDIDATO
# ============================================================

def texto_total(
    candidato
):
    campos = [
        "assuntos",
        "questao_oficial",
        "tese_oficial",
        "informacoes_complementares",
        "referencia_legislativa",
        "referencia_sumular",
    ]

    partes = []

    for campo in campos:
        valor = candidato.get(
            campo,
            "",
        )

        if valor:
            partes.append(
                str(valor)
            )

    return " ".join(
        partes
    )


# ============================================================
# CONTAGEM DE TERMOS
# ============================================================

def termos_encontrados(
    texto,
    lista_termos,
):
    normalizado = normalizar(
        texto
    )

    encontrados = []

    for termo in lista_termos:
        termo_normalizado = (
            normalizar(
                termo
            )
        )

        if (
            termo_normalizado
            and termo_normalizado
            in normalizado
        ):
            encontrados.append(
                termo
            )

    return list(
        dict.fromkeys(
            encontrados
        )
    )


# ============================================================
# DETECÇÃO DE REFERÊNCIA EXPRESSA AO CDC
# ============================================================

def referencia_expressa_cdc(
    candidato
):
    referencia = normalizar(
        candidato.get(
            "referencia_legislativa",
            "",
        )
    )

    padroes = [
        "lei 8078",
        "codigo de defesa do consumidor",
    ]

    return any(
        normalizar(
            padrao
        ) in referencia
        for padrao in padroes
    )


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_candidato(
    candidato
):
    texto = texto_total(
        candidato
    )

    diretos = termos_encontrados(
        texto,
        TERMOS_DIRETOS,
    )

    provaveis = termos_encontrados(
        texto,
        TERMOS_PROVAVEIS,
    )

    ambiguos = termos_encontrados(
        texto,
        TERMOS_AMBIGUOS,
    )

    score_original = int(
        candidato.get(
            "pontuacao_consumidor",
            0,
        )
        or 0
    )

    tem_ref_cdc = (
        referencia_expressa_cdc(
            candidato
        )
    )

    motivos = []

    # --------------------------------------------------------
    # CLASSE A
    # --------------------------------------------------------

    if tem_ref_cdc:
        motivos.append(
            "Referência legislativa expressa ao CDC"
        )

        return (
            "A",
            "CONSUMIDOR DIRETO",
            motivos,
            diretos,
            provaveis,
            ambiguos,
        )

    if len(
        diretos
    ) >= 2:
        motivos.append(
            "Múltiplos termos consumeristas diretos"
        )

        return (
            "A",
            "CONSUMIDOR DIRETO",
            motivos,
            diretos,
            provaveis,
            ambiguos,
        )

    if (
        "consumidor"
        in [
            normalizar(
                item
            )
            for item in diretos
        ]
        and len(
            provaveis
        ) >= 1
    ):
        motivos.append(
            "Termo consumidor combinado com "
            "tema setorial consumerista"
        )

        return (
            "A",
            "CONSUMIDOR DIRETO",
            motivos,
            diretos,
            provaveis,
            ambiguos,
        )

    # --------------------------------------------------------
    # CLASSE B
    # --------------------------------------------------------

    if len(
        provaveis
    ) >= 2:
        motivos.append(
            "Dois ou mais sinais fortes "
            "de relação de consumo"
        )

        return (
            "B",
            "CONSUMIDOR PROVÁVEL",
            motivos,
            diretos,
            provaveis,
            ambiguos,
        )

    if (
        len(
            provaveis
        ) >= 1
        and score_original >= 30
    ):
        motivos.append(
            "Tema setorial forte com "
            "pontuação consumerista relevante"
        )

        return (
            "B",
            "CONSUMIDOR PROVÁVEL",
            motivos,
            diretos,
            provaveis,
            ambiguos,
        )

    if (
        len(
            diretos
        ) == 1
        and score_original >= 25
    ):
        motivos.append(
            "Um sinal consumerista direto "
            "com pontuação suficiente"
        )

        return (
            "B",
            "CONSUMIDOR PROVÁVEL",
            motivos,
            diretos,
            provaveis,
            ambiguos,
        )

    # --------------------------------------------------------
    # CLASSE C
    # --------------------------------------------------------

    motivos.append(
        "Sinais insuficientes para "
        "classificação automática segura"
    )

    return (
        "C",
        "REVISAR",
        motivos,
        diretos,
        provaveis,
        ambiguos,
    )


# ============================================================
# ENRIQUECER RESULTADO
# ============================================================

def preparar_resultado(
    candidato
):
    (
        classe,
        descricao,
        motivos,
        diretos,
        provaveis,
        ambiguos,
    ) = classificar_candidato(
        candidato
    )

    resultado = dict(
        candidato
    )

    resultado[
        "classe_triagem"
    ] = classe

    resultado[
        "descricao_triagem"
    ] = descricao

    resultado[
        "motivos_triagem"
    ] = motivos

    resultado[
        "termos_diretos_encontrados"
    ] = diretos

    resultado[
        "termos_provaveis_encontrados"
    ] = provaveis

    resultado[
        "termos_ambiguos_encontrados"
    ] = ambiguos

    return resultado


# ============================================================
# SALVAR JSON
# ============================================================

def salvar_json(
    caminho,
    classe,
    descricao,
    itens,
):
    estrutura = {
        "gerado_em": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),
        "classe": classe,
        "descricao": descricao,
        "quantidade": len(
            itens
        ),
        "itens": itens,
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


# ============================================================
# RESUMO DE TEXTO
# ============================================================

def resumo(
    texto,
    limite=300,
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
    classe_a,
    classe_b,
    classe_c,
):
    linhas = [
        "LEX MACHINA",
        "TRIAGEM AUTOMÁTICA DE TEMAS DO STJ",
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
            "CLASSE A - CONSUMIDOR DIRETO: "
            f"{len(classe_a)}"
        ),
        (
            "CLASSE B - CONSUMIDOR PROVÁVEL: "
            f"{len(classe_b)}"
        ),
        (
            "CLASSE C - REVISAR: "
            f"{len(classe_c)}"
        ),
        "",
        (
            "TOTAL TRIADO: "
            f"{len(classe_a) + len(classe_b) + len(classe_c)}"
        ),
        "",
        "=" * 76,
        "CLASSE A - CONSUMIDOR DIRETO",
        "=" * 76,
        "",
    ]

    for item in classe_a:
        linhas.extend(
            [
                (
                    f"TEMA {item['numero']} "
                    f"| SCORE "
                    f"{item.get('pontuacao_consumidor', 0)}"
                ),
                (
                    "SITUAÇÃO: "
                    f"{item.get('situacao', '')}"
                ),
                (
                    "QUESTÃO: "
                    + resumo(
                        item.get(
                            "questao_oficial",
                            "",
                        )
                    )
                ),
                (
                    "TESE: "
                    + resumo(
                        item.get(
                            "tese_oficial",
                            "",
                        )
                    )
                ),
                (
                    "REFERÊNCIA: "
                    + resumo(
                        item.get(
                            "referencia_legislativa",
                            "",
                        )
                    )
                ),
                (
                    "MOTIVOS: "
                    + ", ".join(
                        item.get(
                            "motivos_triagem",
                            [],
                        )
                    )
                ),
                "",
                "-" * 76,
                "",
            ]
        )

    linhas.extend(
        [
            "",
            "=" * 76,
            "CLASSE B - CONSUMIDOR PROVÁVEL",
            "=" * 76,
            "",
        ]
    )

    for item in classe_b:
        linhas.extend(
            [
                (
                    f"TEMA {item['numero']} "
                    f"| SCORE "
                    f"{item.get('pontuacao_consumidor', 0)}"
                ),
                (
                    "QUESTÃO: "
                    + resumo(
                        item.get(
                            "questao_oficial",
                            "",
                        )
                    )
                ),
                (
                    "MOTIVOS: "
                    + ", ".join(
                        item.get(
                            "motivos_triagem",
                            [],
                        )
                    )
                ),
                "",
                "-" * 76,
                "",
            ]
        )

    linhas.extend(
        [
            "",
            "=" * 76,
            "CLASSE C - REVISAR",
            "=" * 76,
            "",
        ]
    )

    for item in classe_c:
        linhas.extend(
            [
                (
                    f"TEMA {item['numero']} "
                    f"| SCORE "
                    f"{item.get('pontuacao_consumidor', 0)}"
                ),
                (
                    "QUESTÃO: "
                    + resumo(
                        item.get(
                            "questao_oficial",
                            "",
                        )
                    )
                ),
                "",
                "-" * 76,
                "",
            ]
        )

    ARQUIVO_RELATORIO.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print(
        "LEX MACHINA - TRIAGEM STJ"
    )
    print(
        "=" * 50
    )
    print()

    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidatos = carregar_candidatos()

    # --------------------------------------------------------
    # SOMENTE NOVOS
    # --------------------------------------------------------

    candidatos = [
        item
        for item in candidatos
        if not item.get(
            "ja_cadastrado",
            False,
        )
    ]

    print(
        f"Novos candidatos recebidos: "
        f"{len(candidatos)}"
    )

    classe_a = []
    classe_b = []
    classe_c = []

    for candidato in candidatos:
        resultado = (
            preparar_resultado(
                candidato
            )
        )

        classe = resultado[
            "classe_triagem"
        ]

        if classe == "A":
            classe_a.append(
                resultado
            )

        elif classe == "B":
            classe_b.append(
                resultado
            )

        else:
            classe_c.append(
                resultado
            )

    # --------------------------------------------------------
    # ORDENAÇÃO
    # --------------------------------------------------------

    chave_ordenacao = lambda item: (
        -int(
            item.get(
                "pontuacao_consumidor",
                0,
            )
            or 0
        ),
        int(
            item.get(
                "numero",
                0,
            )
            or 0
        ),
    )

    classe_a.sort(
        key=chave_ordenacao
    )

    classe_b.sort(
        key=chave_ordenacao
    )

    classe_c.sort(
        key=chave_ordenacao
    )

    # --------------------------------------------------------
    # SALVAR
    # --------------------------------------------------------

    salvar_json(
        ARQUIVO_CLASSE_A,
        "A",
        "CONSUMIDOR DIRETO",
        classe_a,
    )

    salvar_json(
        ARQUIVO_CLASSE_B,
        "B",
        "CONSUMIDOR PROVÁVEL",
        classe_b,
    )

    salvar_json(
        ARQUIVO_CLASSE_C,
        "C",
        "REVISAR",
        classe_c,
    )

    salvar_relatorio(
        classe_a,
        classe_b,
        classe_c,
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()
    print(
        "TRIAGEM FINALIZADA"
    )

    print(
        "=" * 50
    )

    print(
        "Classe A - Consumidor direto: "
        f"{len(classe_a)}"
    )

    print(
        "Classe B - Consumidor provável: "
        f"{len(classe_b)}"
    )

    print(
        "Classe C - Revisar: "
        f"{len(classe_c)}"
    )

    print()

    print(
        "Total triado: "
        f"{len(candidatos)}"
    )

    print()

    print(
        f"Classe A: "
        f"{ARQUIVO_CLASSE_A}"
    )

    print(
        f"Classe B: "
        f"{ARQUIVO_CLASSE_B}"
    )

    print(
        f"Classe C: "
        f"{ARQUIVO_CLASSE_C}"
    )

    print(
        f"Relatório: "
        f"{ARQUIVO_RELATORIO}"
    )

    print()

    print(
        "Nenhum registro foi adicionado "
        "automaticamente ao catálogo."
    )


if __name__ == "__main__":
    main()