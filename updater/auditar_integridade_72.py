from datetime import datetime
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import unicodedata

import requests
from bs4 import BeautifulSoup


# ============================================================
# LEX MACHINA - AUDITORIA FORENSE DE INTEGRIDADE DAS 72 NORMAS
#
# OBJETIVO:
# - NÃO ALTERAR NADA NO CARTÃO;
# - comparar cada arquivo atual com:
#     1) a fonte oficial do catálogo mestre;
#     2) o backup mais recente disponível, quando existir;
# - detectar encolhimento, perda de artigos e truncamentos;
# - gerar relatório TXT + JSON no PC.
#
# IMPORTANTE:
# Este script é SOMENTE LEITURA para a unidade do cartão.
# ============================================================


CATALOGO = Path("catalogo_mestre_vademecum.json")
BACKUP_ROOT = Path("backup_catalogos")

REL_DIR = Path("saida/99_INDICES")
REL_TXT = REL_DIR / "AUDITORIA_INTEGRIDADE_72.txt"
REL_JSON = REL_DIR / "AUDITORIA_INTEGRIDADE_72.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 45

# Caminhos históricos conhecidos dos 20 itens BASE.
BASE_ALIASES = {
    "CF88": [
        "1- CONSTITUIÇÃO FEDERAL/cf.txt",
    ],
    "CC2002": [
        "2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt",
        "2- CÓDIGO CIVIL/codigo_civil_2002.txt",
    ],
    "CPC2015": [
        "3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil.txt",
        "3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil_2015.txt",
    ],
    "CP1940": [
        "4-CÓDIGO PENAL/codigo_penal.txt",
    ],
    "CPP1941": [
        "5-CÓDIGO PROCESSO PENAL/Código_de_Processo_Penal.txt",
        "5-CÓDIGO PROCESSO PENAL/codigo_processo_penal.txt",
    ],
    "CTN1966": [
        "6-CÓDIGO TRIBUTARIO NACIONAL/Código Tributário Nacional.txt",
        "6-CÓDIGO TRIBUTARIO NACIONAL/codigo_tributario_nacional.txt",
    ],
    "CE1965": [
        "7-CÓDIGO ELEITORAL/Código Eleitoral.txt",
        "7-CÓDIGO ELEITORAL/codigo_eleitoral.txt",
    ],
    "CLT1943": [
        "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/CLT.txt",
        "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/clt.txt",
    ],
    "CDC1990": [
        "9-CÓDIGO DE DEFESA DO CONSUMIDOR/01_CDC/cdc_lei_8078_1990.txt",
    ],
    "ECA1990": [
        "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE/"
        "Estatuto da Criança e do Adolescente (Lei nº 8.069 1990).txt",
        "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE/eca_lei_8069_1990.txt",
    ],
    "IDOSO2003": [
        "11- ESTATUTO DA PESSOA IDOSA/Estatuto da pessoa idosa.txt",
        "11- ESTATUTO DA PESSOA IDOSA/estatuto_pessoa_idosa.txt",
    ],
    "LBI2015": [
        "12-LEI BRASILEIRA DE INCLUSÃO DA PESSOA COM DEFICIÊNCIA/"
        "Lei Brasileira de Inclusão da Pessoa com Deficiência.txt",
        "12-LEI BRASILEIRA DE INCLUSÃO DA PESSOA COM DEFICIÊNCIA/"
        "lei_brasileira_inclusao.txt",
    ],
    "LEP1984": [
        "13- LEI DA EXECUÇÃO PENAL/Lei de Execução Penal.txt",
        "13- LEI DA EXECUÇÃO PENAL/lei_execucao_penal.txt",
    ],
    "DROGAS2006": [
        "14- LEI DE DROGAS/Lei de Drogas.txt",
        "14- LEI DE DROGAS/lei_drogas.txt",
    ],
    "MARIA2006": [
        "15-LEI MARIA DA PENHA/Lei Maria da Penha.txt",
        "15-LEI MARIA DA PENHA/lei_maria_da_penha.txt",
    ],
    "HEDIONDOS1990": [
        "16- LEI DE CRIMES HEDIONDOS/Lei de Crimes Hediondos.txt",
        "16- LEI DE CRIMES HEDIONDOS/lei_crimes_hediondos.txt",
    ],
    "LIC2021": [
        "17- LEI DE LICITAÇÕES E CONTRATOS/"
        "Lei de Licitações e Contratos Administrativos.txt",
        "17- LEI DE LICITAÇÕES E CONTRATOS/"
        "lei_licitacoes_contratos_14133.txt",
    ],
    "MCI2014": [
        "18- MARCO CIVIL DA INTERNET/Marco Civil da Internet.txt",
        "18- MARCO CIVIL DA INTERNET/marco_civil_internet.txt",
    ],
    "LGPD2018": [
        "19-LGPD LEI GERAL DA PROTEÇÃO DE DADOS/"
        "LGPD Lei Geral da Proteção de Dados.txt",
        "19-LGPD LEI GERAL DA PROTEÇÃO DE DADOS/lgpd.txt",
    ],
    "LAI2011": [
        "20- LEI DE ACESSO A INFORMAÇÃO/Lei de Acesso a Informação.txt",
        "20- LEI DE ACESSO A INFORMAÇÃO/lei_acesso_informacao.txt",
    ],
}


def argumentos():
    p = argparse.ArgumentParser(
        description="LEX MACHINA - auditoria forense de integridade das 72 normas"
    )
    p.add_argument(
        "origem",
        help="Raiz do cartão. Exemplo: D:\\"
    )
    return p.parse_args()


def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def remover_acentos(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(
        c for c in s
        if not unicodedata.combining(c)
    )


def norm(s):
    s = remover_acentos(s).casefold()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def compacto(s):
    return re.sub(r"[^a-z0-9]+", "", norm(s))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def ler_arquivo(path):
    data = path.read_bytes()

    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            return {
                "bytes": len(data),
                "linhas": len(text.splitlines()),
                "caracteres": len(text),
                "encoding": enc,
                "texto": text,
                "sha256": sha256_bytes(data),
            }
        except UnicodeDecodeError:
            pass

    text = data.decode("utf-8", errors="replace")
    return {
        "bytes": len(data),
        "linhas": len(text.splitlines()),
        "caracteres": len(text),
        "encoding": "utf-8-replace",
        "texto": text,
        "sha256": sha256_bytes(data),
    }


def carregar_catalogo():
    if not CATALOGO.exists():
        raise FileNotFoundError(
            f"Catálogo não encontrado: {CATALOGO}"
        )

    dados = json.loads(
        CATALOGO.read_text(encoding="utf-8")
    )

    itens = dados.get("itens", [])

    if not isinstance(itens, list):
        raise ValueError(
            "O campo 'itens' do catálogo mestre não é uma lista."
        )

    return dados, itens


def inventariar(origem):
    arquivos = []

    for p in origem.rglob("*"):
        if not p.is_file():
            continue

        try:
            rel = p.relative_to(origem)
        except ValueError:
            continue

        arquivos.append({
            "path": p,
            "rel": rel,
            "nome_compacto": compacto(p.name),
            "caminho_norm": norm(str(rel)),
        })

    return arquivos


def localizar_item(item, origem, arquivos):
    ident = str(item.get("id", "")).strip()

    # 1. aliases BASE conhecidos
    for rel_txt in BASE_ALIASES.get(ident, []):
        p = origem / Path(rel_txt)
        if p.exists():
            return p

    pasta = norm(item.get("pasta_destino", ""))
    nome = compacto(item.get("arquivo_sugerido", ""))

    # 2. nome exato do catálogo dentro da pasta esperada
    for arq in arquivos:
        if (
            arq["nome_compacto"] == nome
            and pasta in arq["caminho_norm"]
        ):
            return arq["path"]

    # 3. fallback BASE: único TXT na pasta
    if str(item.get("prioridade", "")).upper() == "BASE":
        candidatos = [
            arq["path"]
            for arq in arquivos
            if (
                arq["path"].suffix.lower() == ".txt"
                and pasta in arq["caminho_norm"]
            )
        ]
        if len(candidatos) == 1:
            return candidatos[0]

    return None


def localizar_backup(relativo):
    if not BACKUP_ROOT.exists():
        return None

    encontrados = []

    for pasta in BACKUP_ROOT.glob("catalogo_mestre_*"):
        candidato = pasta / relativo
        if candidato.exists() and candidato.is_file():
            encontrados.append(candidato)

    if not encontrados:
        # fallback por nome
        nome = relativo.name.casefold()
        for candidato in BACKUP_ROOT.rglob("*"):
            if (
                candidato.is_file()
                and candidato.name.casefold() == nome
            ):
                encontrados.append(candidato)

    if not encontrados:
        return None

    return max(
        encontrados,
        key=lambda p: p.stat().st_mtime
    )


# ============================================================
# EXTRAÇÃO CONSERVADORA DA FONTE OFICIAL
#
# NÃO remove <strike>, <s>, <del> nem line-through.
# O objetivo da auditoria é detectar perda, não limpar texto.
# ============================================================

def baixar_oficial(url):
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    r.raise_for_status()

    # requests normalmente identifica bem Planalto; fallback robusto
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding or r.encoding

    html = r.text

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    for nome in (
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
    ):
        for tag in soup.find_all(nome):
            tag.decompose()

    body = soup.body or soup

    texto = body.get_text(
        separator="\n",
        strip=True,
    )

    texto = (
        texto
        .replace("\xa0", " ")
        .replace("\u2002", " ")
        .replace("\u2003", " ")
        .replace("\u2009", " ")
    )

    texto = re.sub(r"[ \t]+", " ", texto)

    return {
        "url": url,
        "bytes_html": len(r.content),
        "caracteres_visiveis": len(texto),
        "linhas_visiveis": len(texto.splitlines()),
        "texto": texto,
        "status_http": r.status_code,
    }


# ============================================================
# DETECTOR DE ARTIGOS CONSERVADOR
#
# O objetivo é encontrar o MAIOR NÚMERO e o conjunto aparente
# de artigos, não decidir sozinho o que é juridicamente vigente.
# ============================================================

ART_RE = re.compile(
    r"(?im)"
    r"(?:^|\n)\s*"
    r"Art(?:igo)?"
    r"\s*\.?\s*"
    r"(?:\.\s*)?"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,4})"
    r"(?:\s*(?:º|°|o|\.\s*º|\.\s*°))?"
    r"(?:\s*[-–—]\s*([A-Za-z]{1,4}(?:-[A-Za-z]{1,4})*))?"
)


def artigos_do_texto(texto):
    encontrados = []

    for m in ART_RE.finditer(texto):
        bruto = m.group(1)
        try:
            base = int(bruto.replace(".", ""))
        except ValueError:
            continue

        if base < 1 or base > 9999:
            continue

        suf = (m.group(2) or "").upper()

        chave = str(base)
        if suf:
            chave += "-" + suf

        encontrados.append({
            "chave": chave,
            "base": base,
            "pos": m.start(),
        })

    # conjunto conservador; preserva primeiro match de cada chave
    mapa = {}
    for x in encontrados:
        mapa.setdefault(x["chave"], x)

    unicos = list(mapa.values())
    unicos.sort(key=lambda x: (x["base"], x["chave"]))

    bases = sorted({x["base"] for x in unicos})

    return {
        "ocorrencias": len(encontrados),
        "unicos": len(unicos),
        "max_base": max(bases) if bases else 0,
        "bases": bases,
        "chaves": sorted(mapa.keys()),
    }


def propor_status(
    atual,
    oficial,
    backup,
):
    motivos_criticos = []
    motivos_revisar = []

    aa = artigos_do_texto(
        atual["texto"]
    )

    ao = artigos_do_texto(
        oficial["texto"]
    )

    ab = (
        artigos_do_texto(
            backup["texto"]
        )
        if backup
        else None
    )

    # 1. Nenhum artigo no local quando oficial tem muitos
    if aa["unicos"] == 0 and ao["unicos"] >= 5:
        motivos_criticos.append(
            "arquivo atual não apresenta artigos detectáveis, "
            "mas a fonte oficial apresenta vários"
        )

    # 2. Maior artigo local muito abaixo da fonte oficial
    if (
        ao["max_base"] >= 20
        and aa["max_base"] < ao["max_base"] * 0.70
    ):
        motivos_criticos.append(
            f"maior artigo local ({aa['max_base']}) muito abaixo "
            f"da fonte oficial ({ao['max_base']})"
        )

    # 3. Quantidade de artigos aparentes muito abaixo
    if (
        ao["unicos"] >= 20
        and aa["unicos"] < ao["unicos"] * 0.65
    ):
        motivos_criticos.append(
            f"artigos aparentes locais ({aa['unicos']}) muito abaixo "
            f"da fonte oficial ({ao['unicos']})"
        )

    # 4. Texto visível local drasticamente menor que oficial
    if (
        oficial["caracteres_visiveis"] >= 5000
        and atual["caracteres"]
        < oficial["caracteres_visiveis"] * 0.35
    ):
        motivos_criticos.append(
            "arquivo local é drasticamente menor que o texto "
            "visível da fonte oficial"
        )

    # 5. Comparação com backup
    if backup:
        if (
            backup["bytes"] >= 5000
            and atual["bytes"] < backup["bytes"] * 0.60
        ):
            motivos_criticos.append(
                f"arquivo atual encolheu de {backup['bytes']} bytes "
                f"(backup) para {atual['bytes']} bytes"
            )

        if (
            ab["unicos"] >= 20
            and aa["unicos"] < ab["unicos"] * 0.65
        ):
            motivos_criticos.append(
                f"artigos aparentes caíram de {ab['unicos']} "
                f"(backup) para {aa['unicos']} (atual)"
            )

        if (
            ab["max_base"] >= 20
            and aa["max_base"] < ab["max_base"] * 0.70
        ):
            motivos_criticos.append(
                f"maior artigo caiu de {ab['max_base']} "
                f"(backup) para {aa['max_base']} (atual)"
            )

    # Revisão por diferenças menos severas
    if not motivos_criticos:
        if (
            ao["unicos"] >= 20
            and aa["unicos"] < ao["unicos"] * 0.90
        ):
            motivos_revisar.append(
                "quantidade de artigos local está abaixo de 90% "
                "da quantidade aparente da fonte oficial"
            )

        if (
            ao["max_base"] >= 20
            and aa["max_base"] < ao["max_base"] * 0.90
        ):
            motivos_revisar.append(
                "maior artigo local está abaixo de 90% "
                "do maior artigo aparente da fonte oficial"
            )

        if backup and (
            atual["bytes"] < backup["bytes"] * 0.85
        ):
            motivos_revisar.append(
                "arquivo atual está mais de 15% menor que o backup"
            )

    if motivos_criticos:
        status = "CRITICO"
    elif motivos_revisar:
        status = "REVISAR"
    else:
        status = "OK"

    return status, motivos_criticos, motivos_revisar, aa, ao, ab


def main():
    args = argumentos()

    origem = Path(args.origem)

    if not origem.exists() or not origem.is_dir():
        raise FileNotFoundError(
            f"Origem inválida: {origem}"
        )

    catalogo, itens = carregar_catalogo()
    arquivos = inventariar(origem)

    print()
    print("LEX MACHINA - AUDITORIA FORENSE DE INTEGRIDADE")
    print("=" * 68)
    print(f"Origem: {origem}")
    print(f"Normas no catálogo: {len(itens)}")
    print("MODO: SOMENTE LEITURA NO CARTÃO")
    print()

    resultados = []

    for i, item in enumerate(itens, start=1):
        nome = item.get("nome", "")
        print(f"[{i}/{len(itens)}] {nome}")

        atual_path = localizar_item(
            item,
            origem,
            arquivos,
        )

        if atual_path is None:
            resultados.append({
                "id": item.get("id"),
                "nome": nome,
                "status": "CRITICO",
                "motivos_criticos": [
                    "arquivo atual não encontrado"
                ],
                "motivos_revisar": [],
            })
            print("  CRÍTICO: arquivo não encontrado")
            continue

        try:
            rel = atual_path.relative_to(origem)
        except ValueError:
            rel = Path(atual_path.name)

        backup_path = localizar_backup(rel)

        try:
            atual = ler_arquivo(atual_path)
        except Exception as e:
            resultados.append({
                "id": item.get("id"),
                "nome": nome,
                "arquivo": str(atual_path),
                "status": "CRITICO",
                "motivos_criticos": [
                    f"falha ao ler arquivo atual: {e}"
                ],
                "motivos_revisar": [],
            })
            print(f"  CRÍTICO: {e}")
            continue

        backup = None
        if backup_path:
            try:
                backup = ler_arquivo(backup_path)
            except Exception:
                backup = None

        try:
            oficial = baixar_oficial(
                item["fonte_oficial"]
            )
        except Exception as e:
            resultados.append({
                "id": item.get("id"),
                "nome": nome,
                "arquivo": str(atual_path),
                "backup": str(backup_path) if backup_path else "",
                "status": "REVISAR",
                "motivos_criticos": [],
                "motivos_revisar": [
                    f"não foi possível consultar a fonte oficial: {e}"
                ],
                "local_bytes": atual["bytes"],
                "local_linhas": atual["linhas"],
            })
            print(f"  REVISAR: fonte oficial indisponível ({e})")
            continue

        (
            status,
            criticos,
            revisar,
            aa,
            ao,
            ab,
        ) = propor_status(
            atual,
            oficial,
            backup,
        )

        resultado = {
            "id": item.get("id"),
            "nome": nome,
            "prioridade": item.get("prioridade"),
            "arquivo": str(atual_path),
            "fonte_oficial": item.get("fonte_oficial"),
            "backup": str(backup_path) if backup_path else "",
            "status": status,
            "motivos_criticos": criticos,
            "motivos_revisar": revisar,
            "local": {
                "bytes": atual["bytes"],
                "linhas": atual["linhas"],
                "caracteres": atual["caracteres"],
                "encoding": atual["encoding"],
                "sha256": atual["sha256"],
                "artigos_aparentes": aa["unicos"],
                "maior_artigo_aparente": aa["max_base"],
            },
            "oficial": {
                "status_http": oficial["status_http"],
                "bytes_html": oficial["bytes_html"],
                "caracteres_visiveis": oficial["caracteres_visiveis"],
                "linhas_visiveis": oficial["linhas_visiveis"],
                "artigos_aparentes": ao["unicos"],
                "maior_artigo_aparente": ao["max_base"],
            },
            "backup_info": (
                {
                    "bytes": backup["bytes"],
                    "linhas": backup["linhas"],
                    "caracteres": backup["caracteres"],
                    "encoding": backup["encoding"],
                    "sha256": backup["sha256"],
                    "artigos_aparentes": ab["unicos"] if ab else 0,
                    "maior_artigo_aparente": ab["max_base"] if ab else 0,
                }
                if backup
                else None
            ),
        }

        resultados.append(resultado)

        print(
            f"  {status}: local art={aa['unicos']} max={aa['max_base']} "
            f"| oficial art={ao['unicos']} max={ao['max_base']}"
        )

        if backup:
            print(
                f"  backup: {backup['bytes']} bytes "
                f"| atual: {atual['bytes']} bytes"
            )

    REL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    criticos = [
        r for r in resultados
        if r["status"] == "CRITICO"
    ]
    revisar = [
        r for r in resultados
        if r["status"] == "REVISAR"
    ]
    ok = [
        r for r in resultados
        if r["status"] == "OK"
    ]

    linhas = [
        "LEX MACHINA",
        "AUDITORIA FORENSE DE INTEGRIDADE DAS 72 NORMAS",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        f"VERSÃO DO CATÁLOGO: {catalogo.get('versao', '')}",
        "MODO: SOMENTE LEITURA NO CARTÃO",
        "",
        f"TOTAL: {len(resultados)}",
        f"OK: {len(ok)}",
        f"REVISAR: {len(revisar)}",
        f"CRÍTICO: {len(criticos)}",
        "",
        "=" * 78,
        "RESULTADOS",
        "=" * 78,
        "",
    ]

    for r in resultados:
        linhas.append(
            f"[{r['status']}] {r.get('id', '')} - {r.get('nome', '')}"
        )
        linhas.append(
            f"  Arquivo: {r.get('arquivo', '')}"
        )

        local = r.get("local")
        oficial = r.get("oficial")
        backup_info = r.get("backup_info")

        if local:
            linhas.append(
                "  Local: "
                f"bytes={local['bytes']} "
                f"| linhas={local['linhas']} "
                f"| artigos_aparentes={local['artigos_aparentes']} "
                f"| maior_artigo={local['maior_artigo_aparente']}"
            )

        if oficial:
            linhas.append(
                "  Oficial: "
                f"caracteres_visiveis={oficial['caracteres_visiveis']} "
                f"| linhas={oficial['linhas_visiveis']} "
                f"| artigos_aparentes={oficial['artigos_aparentes']} "
                f"| maior_artigo={oficial['maior_artigo_aparente']}"
            )

        if backup_info:
            linhas.append(
                "  Backup: "
                f"bytes={backup_info['bytes']} "
                f"| linhas={backup_info['linhas']} "
                f"| artigos_aparentes={backup_info['artigos_aparentes']} "
                f"| maior_artigo={backup_info['maior_artigo_aparente']}"
            )

        for m in r.get("motivos_criticos", []):
            linhas.append(
                f"  CRÍTICO: {m}"
            )

        for m in r.get("motivos_revisar", []):
            linhas.append(
                f"  REVISAR: {m}"
            )

        linhas.append("")

    linhas.extend([
        "=" * 78,
        "CONCLUSÃO",
        "=" * 78,
        "",
    ])

    if criticos:
        linhas.append(
            "AUDITORIA REPROVADA: existem arquivos com indícios fortes de perda "
            "ou truncamento. NÃO usar o índice ESP32 e NÃO executar atualização "
            "automática antes da recuperação."
        )
    elif revisar:
        linhas.append(
            "AUDITORIA NÃO APROVADA AINDA: não há perda crítica detectada, "
            "mas existem itens que exigem revisão."
        )
    else:
        linhas.append(
            "AUDITORIA APROVADA NESTE NÍVEL: nenhum indício automático de "
            "truncamento foi encontrado."
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
                "versao_catalogo": catalogo.get("versao", ""),
                "resumo": {
                    "total": len(resultados),
                    "ok": len(ok),
                    "revisar": len(revisar),
                    "critico": len(criticos),
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
    print("=" * 68)
    print("AUDITORIA FINALIZADA")
    print(f"OK: {len(ok)}")
    print(f"REVISAR: {len(revisar)}")
    print(f"CRÍTICO: {len(criticos)}")
    print(f"Relatório TXT: {REL_TXT}")
    print(f"Relatório JSON: {REL_JSON}")
    print()
    print("Nenhum arquivo do cartão foi alterado.")


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print()
        print("ERRO FATAL:")
        print(erro)
        sys.exit(1)
