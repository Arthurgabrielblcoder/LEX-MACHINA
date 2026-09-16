"""Controle concentrado: tabelas JSON públicas do Corte Aberta/STF.

Um registro por processo, somente com decisão final de mérito colegiada
identificável na fonte. Não transforma petições ou liminares em teses.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.parse import parse_qs, urlparse

from importar_stf_repercussao_geral import (
    HEADERS_STF, _criar_session, _eh_candidato_consumidor, _limpar, _relacoes_cdc,
)

TIPOS = ('adi', 'adc', 'adpf', 'ado')
ORIGEM = 'STF_OFICIAL_CONTROLE_CONCENTRADO'
URL_PAINEL = 'https://transparencia.stf.jus.br/extensions/controle_concentrado/controle_concentrado.html'
URL_SCRIPT = 'https://transparencia.stf.jus.br/extensions/controle_concentrado/qliksense.js'
APP_ID = 'c47ea922-dbfe-4c3e-9d21-77cd2fed770d'
URL_API = 'wss://transparencia.stf.jus.br/app/' + APP_ID
OBJETOS = {'processos': 'LBZHET', 'decisoes': '750a9fab-e94b-477f-ab91-f58cb67b854e'}
CAMPOS = {
    'processos': {'Processo', 'Link Processo', 'Relator Atual', 'Ramo do Direito',
                  'Assunto relacionado', 'Legislação', 'Situação processual', 'Tem decisão final?'},
    'decisoes': {'Processo', 'Data', 'Descrição', 'Andamento agrupado', 'Subgrupo', 'Observação'},
}


def _normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', _limpar(texto).lower())
                   if unicodedata.category(c) != 'Mn')


def _url_oficial(url, *, processo=False):
    p = urlparse(url)
    if (p.scheme != 'https' or p.hostname not in {'portal.stf.jus.br', 'transparencia.stf.jus.br'}
            or p.port not in (None, 443) or p.username or p.password or p.fragment):
        raise ValueError('URL fora da fonte oficial HTTPS do STF')
    if processo:
        q = parse_qs(p.query)
        if (p.hostname != 'portal.stf.jus.br' or p.path != '/processos/detalhe.asp'
                or set(q) != {'incidente'} or len(q['incidente']) != 1
                or not re.fullmatch(r'[1-9][0-9]*', q['incidente'][0])):
            raise ValueError('link processual oficial inválido')
    return url


def _validar_http(r, url):
    _url_oficial(url)
    r.raise_for_status()
    if r.status_code != 200 or not r.content or r.url != url:
        raise ValueError('resposta oficial vazia, redirecionada ou incompleta')
    texto = _normalizar(r.text)
    if any(x in texto for x in ('404 not found', 'pagina nao encontrada',
           'nao encontramos o que voce esta procurando', 'access denied',
           'acesso negado', 'servico indisponivel', 'site em manutencao')):
        raise ValueError('página de erro com falso HTTP 200')


class ClienteQlik:
    """Sessão anônima do painel; somente métodos de leitura do JSON-RPC."""
    def __init__(self, session):
        import websocket
        self.ws = None
        self.numero = 0
        r = session.get(URL_PAINEL, headers=HEADERS_STF, timeout=60, allow_redirects=False)
        _validar_http(r, URL_PAINEL)
        if 'qliksense.js' not in r.text:
            raise ValueError('estrutura do painel oficial não reconhecida')
        r = session.get(URL_SCRIPT, headers=HEADERS_STF, timeout=60, allow_redirects=False)
        _validar_http(r, URL_SCRIPT)
        if not all(x in r.text for x in (APP_ID, *OBJETOS.values())):
            raise ValueError('contrato das exportações do STF mudou')
        self.ws = websocket.create_connection(
            URL_API, origin='https://transparencia.stf.jus.br', timeout=60,
            redirect_limit=0,
            header={'User-Agent': HEADERS_STF['User-Agent']},
            cookie='; '.join(k + '=' + v for k, v in session.cookies.items()),
            sslopt={'context': session.get_adapter(URL_PAINEL).contexto},
        )

    def rpc(self, handle, method, params):
        if method not in {'OpenDoc', 'GetObject', 'GetLayout', 'GetHyperCubeData', 'GetAppLayout'}:
            raise ValueError('método fora do contrato de leitura')
        self.numero += 1
        self.ws.send(json.dumps(dict(jsonrpc='2.0', id=self.numero, handle=handle,
                                     method=method, params=params)))
        limite = time.monotonic() + 60
        for _ in range(100):
            if time.monotonic() > limite:
                break
            msg = json.loads(self.ws.recv())
            if not isinstance(msg, dict) or msg.get('jsonrpc') != '2.0':
                raise ValueError('resposta JSON-RPC inválida')
            if msg.get('id') == self.numero:
                if 'error' in msg or not isinstance(msg.get('result'), dict):
                    raise ValueError('erro retornado pela API oficial')
                return msg['result']
        raise ValueError('resposta JSON-RPC ausente')

    def close(self):
        if self.ws is not None:
            self.ws.close()


def _estrutura(layout, nome):
    cube = layout['qHyperCube']
    tamanho = cube['qSize']
    largura, total = tamanho['qcx'], tamanho['qcy']
    if (type(largura) is not int or type(total) is not int or not 0 < largura <= 100
            or not 0 < total <= 1000000 or cube.get('qMode') != 'S' or cube.get('qError')):
        raise ValueError('tabela oficial vazia ou estrutura inválida')
    campos = cube['qDimensionInfo'] + cube['qMeasureInfo']
    ordem = cube['qColumnOrder']
    if len(campos) != largura or sorted(ordem) != list(range(largura)):
        raise ValueError('ordem das colunas inválida')
    titulos = [campos[i]['qFallbackTitle'] for i in ordem]
    if len(set(titulos)) != largura or not CAMPOS[nome].issubset(titulos):
        raise ValueError('colunas oficiais obrigatórias ausentes')
    for dim in cube['qDimensionInfo']:
        estados = dim.get('qStateCounts', {})
        if any(estados.get(k, 0) for k in ('qSelected', 'qLocked', 'qSelectedExcluded', 'qLockedExcluded')):
            raise ValueError('a fonte oficial contém filtros ativos')
    return largura, total, titulos


def _ler_tabela(cliente, app, nome, verbose=False):
    handle = cliente.rpc(app, 'GetObject', [OBJETOS[nome]])['qReturn']['qHandle']
    layout = cliente.rpc(handle, 'GetLayout', [])['qLayout']
    largura, total, titulos = _estrutura(layout, nome)
    registros, vistos = [], set()
    # Limite Qlik de 10.000 células por página; margens para outras colunas.
    passo = min(500, 9000 // largura)
    for topo in range(0, total, passo):
        altura = min(passo, total - topo)
        area = dict(qTop=topo, qLeft=0, qHeight=altura, qWidth=largura)
        paginas = cliente.rpc(handle, 'GetHyperCubeData', ['/qHyperCubeDef', [area]])['qDataPages']
        if len(paginas) != 1 or paginas[0]['qArea'] != area:
            raise ValueError('página oficial ausente, repetida ou fora de ordem')
        matriz = paginas[0]['qMatrix']
        if len(matriz) != altura:
            raise ValueError('página oficial truncada')
        for linha in matriz:
            if len(linha) != largura or any(not isinstance(c.get('qText'), str) for c in linha):
                raise ValueError('linha oficial incompleta')
            valores = tuple(c['qText'] for c in linha)
            if valores in vistos:
                raise ValueError('linha duplicada entre páginas oficiais')
            vistos.add(valores)
            registros.append(dict(zip(titulos, valores)))
    if _estrutura(cliente.rpc(handle, 'GetLayout', [])['qLayout'], nome) != (largura, total, titulos):
        raise ValueError('a tabela oficial mudou durante a paginação')
    if verbose:
        print(f'STF CC: {total} linhas oficiais de {nome} lidas integralmente.')
    return registros


def _consultar_base(session, verbose=False):
    cliente = ClienteQlik(session)
    try:
        app = cliente.rpc(-1, 'OpenDoc', [APP_ID])['qReturn']['qHandle']
        atualizacao = cliente.rpc(app, 'GetAppLayout', [])['qLayout']['qLastReloadTime']
        processos = _ler_tabela(cliente, app, 'processos', verbose)
        decisoes = _ler_tabela(cliente, app, 'decisoes', verbose)
        if cliente.rpc(app, 'GetAppLayout', [])['qLayout']['qLastReloadTime'] != atualizacao:
            raise ValueError('a base oficial foi recarregada durante a consulta')
        return processos, decisoes, atualizacao
    finally:
        cliente.close()


def _identidade(processo):
    m = re.fullmatch(r'(ADI|ADC|ADPF|ADO)\s+([1-9][0-9]*)', _limpar(processo), re.I)
    if not m:
        raise ValueError('classe ou número processual inválido')
    return m[1].lower(), int(m[2])


def _validar_linhas(linhas, nome):
    if not isinstance(linhas, list) or not linhas:
        raise ValueError('base oficial vazia')
    for r in linhas:
        if not isinstance(r, dict) or any(not isinstance(r.get(c), str) for c in CAMPOS[nome]):
            raise ValueError('registro oficial incompleto')
        _identidade(r['Processo'])


def _texto_disponivel(texto):
    return bool(_limpar(texto)) and _limpar(texto) not in {'*NI*', '-', 'Não informado', 'Sem Descrição'}


def _data_decisao(d):
    # O painel publica '-' para datas não informadas; jamais inventar uma data.
    return datetime.strptime(d['Data'], '%d/%m/%Y') if d['Data'] != '-' else None


def _merito_colegiado(d):
    texto = _normalizar(d['Observação'])
    colegiado = re.search(
        r'^(?:decisao:\s*)?(?:(?:prosseguindo|retomando|colhid[oa]s?|convertida|preliminarmente)'
        r'[^.!?"“”]{0,220},\s*)?o (?:tribunal|plenario)\b', texto)
    return (d['Subgrupo'] == 'Decisão Final'
            and d['Andamento agrupado'] in {'Procedente', 'Procedente em parte', 'Improcedente'}
            and _data_decisao(d) is not None
            and _texto_disponivel(d['Observação'])
            and bool(colegiado))


def _relacoes_legislacao(texto):
    """Referência estruturada explícita a lei federal e artigo, sem atravessar outras leis."""
    lei = (r'(?:Código\s+de\s+Defesa\s+do\s+Consumidor(?:\s+de\s+1990)?'
           r'|Lei\s+(?:Federal\s+)?(?:n[º°o.]?\s*)?8\.?078(?:/1990|/90|,?\s+de\s+1990)?)')
    padrao = rf'\b{lei}\s*,\s*art(?:igo)?\.?\s+(\d{{1,3}})[º°]?(?=\s*(?:,|\.|-|;|$))'
    return sorted({f'CDC art. {int(m[1])}' for m in re.finditer(padrao, texto, re.I)
                   if 1 <= int(m[1]) <= 119}, key=lambda x: int(x.rsplit(' ', 1)[1]))


def _selecionar(processos, decisoes, contagens, atualizacao):
    _validar_linhas(processos, 'processos')
    _validar_linhas(decisoes, 'decisoes')
    por_processo, por_decisao = {}, defaultdict(list)
    incidentes = set()
    for p in processos:
        chave = _identidade(p['Processo'])
        url = _url_oficial(p['Link Processo'], processo=True)
        incidente = parse_qs(urlparse(url).query)['incidente'][0]
        if chave in por_processo or incidente in incidentes:
            raise ValueError('processo ou incidente duplicado na base oficial')
        incidentes.add(incidente)
        por_processo[chave] = p
        contagens[chave[0]]['encontrados'] += 1
    if {t for t, _ in por_processo} != set(TIPOS):
        raise ValueError('uma das quatro classes está ausente da base oficial')
    for d in decisoes:
        chave = _identidade(d['Processo'])
        if chave not in por_processo:
            raise ValueError('decisão sem processo na base oficial')
        _data_decisao(d)
        por_decisao[chave].append(d)
        contagens[chave[0]]['decisoes_encontradas'] += 1
    registros = []
    for (tipo, numero), p in sorted(por_processo.items()):
        finais = [d for d in por_decisao[(tipo, numero)] if d['Subgrupo'] == 'Decisão Final']
        campos = [p['Ramo do Direito'], p['Assunto relacionado'], p['Legislação']]
        campos += [d['Observação'] for d in finais]
        if not (any(_eh_candidato_consumidor(c) for c in campos) or _relacoes_legislacao(p['Legislação'])):
            continue
        contagens[tipo]['consumeristas'] += 1
        meritos = [d for d in finais if _merito_colegiado(d)]
        if not meritos:
            contagens[tipo]['sem_merito_colegiado_verificavel'] += 1
            continue
        ultima_data = max(_data_decisao(d) for d in meritos)
        ultimas = [d for d in meritos if _data_decisao(d) == ultima_data]
        # Ambiguidade na decisão final mais recente exige revisão humana.
        if len(ultimas) != 1:
            contagens[tipo]['sem_merito_colegiado_verificavel'] += 1
            continue
        d = ultimas[0]
        # Embargos podem estar classificados como "Decisão Final" no painel.
        # Mantém os andamentos posteriores, sem inferir se alteraram o mérito.
        posteriores = [v for v in por_decisao[(tipo, numero)] if v is not d and (
            _data_decisao(v) is None or _data_decisao(v) >= ultima_data)]
        posteriores.sort(key=lambda v: (_data_decisao(v) or datetime.max, v['Descrição'], v['Observação']))
        historico = [d] + posteriores
        texto = '\n\n'.join(f"{v['Data']} — {v['Subgrupo']} — {v['Andamento agrupado']}\n"
                            + (_limpar(v['Observação']) if _texto_disponivel(v['Observação'])
                               else 'Texto não informado na base oficial.') for v in historico)
        evidencias = []
        for v in historico:
            for rel in _relacoes_cdc(v['Observação']):
                evidencias.append(dict(relacao=rel, campo='Observação', data=v['Data'], texto=v['Observação']))
        for rel in _relacoes_legislacao(p['Legislação']):
            evidencias.append(dict(relacao=rel, campo='Legislação', texto=p['Legislação']))
        relacoes = sorted({e['relacao'] for e in evidencias}, key=lambda x: int(x.rsplit(' ', 1)[1]))
        registros.append({
            'tribunal': 'STF', 'tipo': tipo, 'numero': numero, 'status': 'julgado',
            'tema': f"{tipo.upper()} {numero} — {_limpar(p['Assunto relacionado'])}",
            'arquivo': f'stf_{tipo}_{numero}.txt',
            'pasta_destino': f'19_JURISPRUDENCIA/STF/PRECEDENTES/{tipo.upper()}',
            'texto': texto, 'texto_oficial_verificado': texto,
            'natureza_texto_oficial': 'registro_de_decisao_final_no_corte_aberta',
            'questao_oficial_verificada': '', 'relacionado_a': relacoes,
            'evidencias_relacoes_cdc': evidencias, 'decisoes_oficiais': historico,
            'fonte': 'Supremo Tribunal Federal — Corte Aberta — Controle Concentrado',
            'url_fonte': p['Link Processo'], 'url_verificacao': URL_PAINEL,
            'url_descoberta': URL_PAINEL, 'url_api': URL_API,
            'ultima_verificacao': datetime.now().strftime('%Y-%m-%d'),
            'processos': [f'{tipo.upper()} {numero}'], 'relator': p['Relator Atual'],
            'ramo_direito_oficial': p['Ramo do Direito'],
            'assunto_oficial': p['Assunto relacionado'],
            'legislacao_oficial': p['Legislação'],
            'situacao_oficial_stf': p['Situação processual'],
            'resultado_decisao_oficial': d['Andamento agrupado'],
            'data_julgamento': d['Data'], 'atualizacao_base_oficial': atualizacao,
            'sha256_texto_oficial': hashlib.sha256(texto.encode('utf-8')).hexdigest(),
            'usar_tese_oficial': False, 'fonte_texto_preferencial': 'texto_oficial_verificado',
            'origem_importacao': ORIGEM,
        })
    return registros


def _automatico(r):
    return r.get('tribunal') == 'STF' and r.get('tipo') in TIPOS and r.get('origem_importacao') == ORIGEM


def _identidades_existentes(registros):
    chaves, urls = set(), set()
    for r in registros:
        if str(r.get('tribunal', '')).upper() != 'STF':
            continue
        if str(r.get('tipo', '')).lower() in TIPOS:
            chaves.add(_identidade(f"{r['tipo']} {r['numero']}"))
        processos = r.get('processos', [])
        if isinstance(processos, str):
            processos = [processos]
        for p in processos:
            normal = re.sub(r'(?<=\d)\.(?=\d{3}\b)', '', _limpar(p))
            if re.fullmatch(r'(ADI|ADC|ADPF|ADO)\s*[1-9][0-9]*', normal, re.I):
                normal = re.sub(r'^(ADI|ADC|ADPF|ADO)\s*', r'\1 ', normal, flags=re.I)
                chaves.add(_identidade(normal))
        if r.get('url_fonte'):
            urls.add(r['url_fonte'])
    return chaves, urls


def atualizar_controle_concentrado(caminho_catalogo, verbose=True, outros_registros=()):
    """Transação única para as quatro classes; qualquer falha preserva os bytes anteriores."""
    caminho = Path(caminho_catalogo)
    session = None
    resumo = {t: dict(encontrados=0, decisoes_encontradas=0, consumeristas=0, importados=0,
                     com_relacao_cdc=0, duplicados_preservados=0,
                     sem_merito_colegiado_verificavel=0) for t in TIPOS}
    resultado = dict(ok=False, classes=resumo, fontes=[URL_PAINEL, URL_SCRIPT, URL_API],
                     contagens_completas=False)
    try:
        anteriores = json.loads(caminho.read_text(encoding='utf-8')) if caminho.exists() else []
        if not isinstance(anteriores, list) or any(not isinstance(r, dict) for r in anteriores):
            raise ValueError('catálogo anterior inválido')
        session = _criar_session()
        processos, decisoes, atualizacao = _consultar_base(session, verbose)
        novos = _selecionar(processos, decisoes, resumo, atualizacao)
        resultado.update(contagens_completas=True, atualizacao_base_oficial=atualizacao)
        if not novos:
            raise ValueError('nenhum precedente de mérito verificado; catálogo preservado')
        preservados = [r for r in anteriores if not _automatico(r)]
        chaves, urls = _identidades_existentes(preservados + list(outros_registros))
        unicos = []
        for r in novos:
            chave = r['tipo'], r['numero']
            if chave in chaves or r['url_fonte'] in urls:
                resumo[r['tipo']]['duplicados_preservados'] += 1
                continue
            chaves.add(chave)
            urls.add(r['url_fonte'])
            unicos.append(r)
        antigas = {(r['tipo'], int(r['numero'])) for r in anteriores if _automatico(r)}
        if not antigas.issubset(chaves):
            raise ValueError('precedentes anteriores ausentes da nova seleção; revisão necessária')
        tmp = caminho.with_suffix(caminho.suffix + '.controle.tmp')
        try:
            tmp.write_text(json.dumps(preservados + unicos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            tmp.replace(caminho)
        finally:
            tmp.unlink(missing_ok=True)
        for r in unicos:
            resumo[r['tipo']]['importados'] += 1
            resumo[r['tipo']]['com_relacao_cdc'] += bool(r['relacionado_a'])
        resultado['ok'] = True
    except Exception as exc:
        resultado['erro'] = str(exc)
        if verbose:
            print(f'[AVISO] STF controle concentrado não atualizado: {exc}. Catálogo anterior preservado.')
    finally:
        if session is not None:
            session.close()
    if verbose:
        for tipo, r in resumo.items():
            print(f"STF {tipo.upper()}: {r['encontrados']} processos oficiais; "
                  f"{r['consumeristas']} com sinal consumerista; {r['importados']} importados; "
                  f"{r['com_relacao_cdc']} com artigo do CDC explícito.")
    return resultado


if __name__ == '__main__':
    resultado = atualizar_controle_concentrado(Path('catalogo_precedentes.json'))
    Path('saida').mkdir(exist_ok=True)
    Path('saida/relatorio_stf_controle_concentrado.json').write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(0 if resultado['ok'] else 1)
