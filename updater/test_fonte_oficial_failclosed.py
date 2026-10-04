"""MARIA2006_SOURCE_REPAIR: fonte oficial fail-closed do Catálogo Mestre.

Fluxo: fonte oficial -> download -> validar_resposta_fonte -> detecção de encoding -> extração -> verificar_texto/identidade ->
TXT. Qualquer falha = AtualizacaoBloqueada (UPDATE_BLOCKED) e o last-known-good fica intacto. Offline: a única fonte real é o
download arquivado como prova de origem em DEVICE_INTEGRATION/source_evidence/MARIA2006/.
"""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

import main as U

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / 'DEVICE_INTEGRATION/source_evidence/MARIA2006'
RAW = EVID / 'l11340_planalto_20261004.htm'
PROV = EVID / 'l11340_planalto_20261004.provenance.json'
CORRUPT_HEAD = 'ÿþ\n\n<h t m l >\n\n<h e a d >\n\n'
URL = 'https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11340.htm'


def item(numero='11.340', ano='2006'):
    return dict(id='TESTE2006', nome=f'Lei {numero}/{ano} - Teste', ramo='TESTE', prioridade='BASE', tipo='lei', fonte_oficial=URL,
                pasta_destino='99- TESTE', arquivo_sugerido='lei_teste.txt', detectar_por=['lei_teste'])


def pagina(artigos=12, numero='11.340'):
    corpo = ''.join(f'<p>Art. {n}º Disposição número {n} desta Lei, com redação válida e suficiente para a validação.</p>\n'
                    for n in range(1, artigos + 1))
    return ('<html><head><title>Lei nº ' + numero + '</title></head><body>'
            f'<p>LEI Nº {numero}, DE 7 DE AGOSTO DE 2006</p>\n' + corpo + '<p>Brasília, 7 de agosto de 2006.</p></body></html>')


class DecodificacaoTests(unittest.TestCase):
    def test_02_utf8_valido(self):
        texto, cod = U.extrair_texto(pagina().encode('utf-8'))
        self.assertEqual(cod, 'utf-8')
        self.assertIn('Art. 1º Disposição', texto)
        self.assertEqual(U.verificar_texto(texto), [])

    def test_03_utf16_valido_convertido(self):
        html = pagina()
        for raw, esperado in ((b'\xff\xfe' + html.encode('utf-16-le') + b' ' * 1559, 'utf-16-le'),   # BOM + enchimento 8 bits
                              (b'\xfe\xff' + html.encode('utf-16-be'), 'utf-16-be'),
                              (html.encode('utf-16-le'), 'utf-16-le'),                                # sem BOM: bytes nulos
                              (b'\xef\xbb\xbf' + html.encode('utf-8'), 'utf-8-sig')):
            texto, cod = U.extrair_texto(raw)
            self.assertEqual(cod, esperado)
            self.assertIn('LEI Nº 11.340, DE 7 DE AGOSTO DE 2006', texto)
            self.assertEqual(U.verificar_texto(texto), [], esperado)

    def test_04_html_valido_que_precisa_extracao(self):
        texto, _ = U.extrair_texto(pagina().encode('cp1252'))
        self.assertNotIn('<', texto)
        self.assertEqual(len(U._artigos_cabecalho(texto)), 12)
        cand = U.candidato_mestre_de_bytes(item(), pagina().encode('cp1252'), {})
        self.assertEqual(cand['metodo'], 'HTML_PLANALTO_COM_GUARDRAILS')

    def test_08_charset_incorreto(self):
        # o defeito original: UTF-16 lido como 8 bits -> letras espaçadas; texto com HTML residual
        self.assertTrue(any(p.startswith('ENCODING_CORRUPTION') for p in U.verificar_texto(CORRUPT_HEAD + 'L e i n º 1 1 . 3 4 0 ' * 20)))
        self.assertTrue(any(p.startswith('ENCODING_CORRUPTION') for p in U.verificar_texto('Art. 1º texto\x00' * 20)))
        self.assertTrue(any(p.startswith('HTML_EXTRACTION_FAILURE') for p in U.verificar_texto('<html><body><p>x</p><p>y</p><div>z</div>' * 10)))
        # UTF-16 com resíduo que não é enchimento de espaços: decodificação estrita bloqueia
        with self.assertRaises(U.AtualizacaoBloqueada) as c:
            U.decodificar_html(b'\xff\xfe' + pagina().encode('utf-16-le') + b'\x41')
        self.assertEqual(c.exception.codigo, 'ENCODING_INVALIDO')


class RespostaTests(unittest.TestCase):
    def block(self, *args):
        with self.assertRaises(U.AtualizacaoBloqueada) as c:
            U.validar_resposta_fonte(*args)
        return c.exception.codigo

    def test_06_pagina_de_erro(self):
        self.assertEqual(self.block(URL, URL, 404, 'text/html', b'x' * 5000), 'HTTP_STATUS')
        self.assertEqual(self.block(URL, URL, 503, 'text/html', b'x' * 5000), 'HTTP_STATUS')
        erro = '<html><body><h1>Request Rejected</h1><p>The requested URL was rejected. Please consult with your administrator.</p>' \
               '<p>Your support ID is: 1234</p></body></html>' * 3
        texto, _ = U.extrair_texto(erro.encode('utf-8'))
        self.assertTrue(any(p.startswith('PAGINA_INVALIDA') for p in U.verificar_texto(texto)))
        with self.assertRaises(U.AtualizacaoBloqueada):
            U.candidato_mestre_de_bytes(item(), erro.encode('utf-8'), {})
        captcha = '<html><body><p>Verificação de segurança: resolva o captcha para continuar.</p></body></html>' * 20
        self.assertTrue(any(p.startswith('PAGINA_INVALIDA') for p in U.verificar_texto(U.extrair_texto(captcha.encode())[0])))

    def test_07_conteudo_vazio(self):
        self.assertEqual(self.block(URL, URL, 200, 'text/html', b''), 'CONTEUDO_VAZIO')
        self.assertEqual(self.block(URL, URL, 200, 'text/html', b'<html></html>'), 'CONTEUDO_VAZIO')

    def test_09_redirect_e_content_type_inesperados(self):
        self.assertEqual(self.block(URL, 'https://login.exemplo.com/sso?next=x', 200, 'text/html', b'x' * 5000), 'REDIRECT_INESPERADO')
        self.assertEqual(self.block(URL, URL, 200, 'application/pdf', b'%PDF' * 2000), 'CONTENT_TYPE_INESPERADO')
        U.validar_resposta_fonte(URL, URL + '?x=1', 200, 'text/html; charset=utf-8', b'x' * 5000)    # mesmo host: aceito

    def test_05_pagina_html_invalida_sem_a_norma(self):
        portal = ('<html><body><h1>Portal da Legislação</h1>' + '<p>Consulte a legislação federal por número e ano.</p>' * 40 +
                  '</body></html>').encode('utf-8')
        with self.assertRaises(U.AtualizacaoBloqueada):
            U.candidato_mestre_de_bytes(item(), portal, {})
        # outra lei no lugar da esperada: identidade do ato
        with self.assertRaises(U.AtualizacaoBloqueada) as c:
            U.candidato_mestre_de_bytes(item(), pagina(numero='9.999').encode('utf-8'), {})
        self.assertIn('IDENTIDADE', str(c.exception))


class FonteOficialMaria2006Tests(unittest.TestCase):
    def test_01_fonte_oficial_valida_arquivada(self):
        prov = json.loads(PROV.read_text(encoding='utf-8'))
        raw = RAW.read_bytes()
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (prov['bytes'], prov['sha256']))
        self.assertEqual(prov['source_url'], json.loads((Path(__file__).parent / 'catalogo_mestre_vademecum.json').read_text(encoding='utf-8'))
                         ['itens'][[i['id'] for i in json.loads((Path(__file__).parent / 'catalogo_mestre_vademecum.json').read_text(
                             encoding='utf-8'))['itens']].index('MARIA2006')]['fonte_oficial'])
        U.validar_resposta_fonte(prov['source_url'], prov['final_url'], prov['http_status'], prov['content_type'], raw)
        self.assertEqual(U.detectar_codificacao_estrutural(raw), 'utf-16-le')
        cat = {i['id']: i for i in json.loads((Path(__file__).parent / 'catalogo_mestre_vademecum.json').read_text(encoding='utf-8'))['itens']}
        cand = U.candidato_mestre_de_bytes(cat['MARIA2006'], raw, prov, texto_local=CORRUPT_HEAD * 2000)
        self.assertEqual(cand['codificacao'], 'utf-16-le')
        self.assertIn('LEI Nº 11.340, DE 7 DE AGOSTO DE 2006', cand['texto'])
        self.assertIn('Art. 46. Esta Lei entra em vigor', cand['texto'])
        self.assertEqual(U.verificar_texto(cand['texto']), [])

    def test_01b_decodificacao_antiga_reproduz_o_defeito(self):
        # sem a detecção estrutural, o mesmo arquivo vira cp1252 com letras espaçadas (o TXT de 13/09/2026)
        raw = RAW.read_bytes()
        texto = raw.decode('cp1252', errors='replace').replace('\x00', ' ')
        self.assertTrue(texto.startswith('ÿþ'))
        self.assertTrue(any(p.startswith('ENCODING_CORRUPTION') for p in U.verificar_texto(texto)))


class LastKnownGoodTests(unittest.TestCase):
    """10. Atualização ruim nunca destrói a versão jurídica válida anterior."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)                                          # backup_catalogos/ do teste fica no temporário
        self.raiz = Path(self.tmp.name) / 'vademecum'
        self.it = dict(item(), id='MARIA2006', nome='Lei 11.340/2006 - Lei Maria da Penha', pasta_destino='15-LEI MARIA DA PENHA',
                       arquivo_sugerido='lei_maria_da_penha.txt', detectar_por=['maria da penha'])
        self.arq = self.raiz / '15-LEI MARIA DA PENHA' / 'Lei Maria da Penha.txt'
        self.arq.parent.mkdir(parents=True)
        self.orig = (U.RAIZ_VADEMECUM, U.PASTA_SAIDA, U.PASTA_RELATORIOS_GERAIS, U.baixar_fonte_oficial)
        U.configurar_destino(str(self.raiz))

    def tearDown(self):
        U.RAIZ_VADEMECUM, U.PASTA_SAIDA, U.PASTA_RELATORIOS_GERAIS, U.baixar_fonte_oficial = self.orig
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def processar(self, resposta):
        def falso(url):
            conteudo, meta = resposta
            U.validar_resposta_fonte(url, meta.get('url_final', url), meta.get('status', 200), meta.get('content_type', 'text/html'), conteudo)
            return conteudo, dict(meta, sha256=hashlib.sha256(conteudo).hexdigest())
        U.baixar_fonte_oficial = falso
        return U.processar_catalogo_mestre([self.it], atualizar=True)

    def test_10_last_known_good_preservado(self):
        bom = pagina(artigos=46).encode('utf-8')
        self.arq.write_bytes(('\n'.join(['Lei Maria da Penha'] + U._artigos_cabecalho(U.extrair_texto(bom)[0]) and
                                        [U.extrair_texto(bom)[0]])).encode('utf-8'))
        antes = self.arq.read_bytes()
        corrompida = b'\xff\xfe' + pagina(artigos=46).encode('utf-16-le') + b'\x41'          # UTF-16 inválido
        erro = ('<html><body><h1>Request Rejected</h1>' + '<p>The requested URL was rejected.</p>' * 3 + '</body></html>').encode()
        for resposta in ((corrompida, {}), (erro, {}), (b'', {}), (bom, {'url_final': 'https://outro.exemplo/x'}),
                         (bom, {'status': 500}), (b'%PDF' * 3000, {'content_type': 'application/pdf'}),
                         (pagina(artigos=46, numero='9.999').encode('utf-8'), {})):
            r = self.processar(resposta)
            self.assertEqual(r['resultados'][0]['status'], 'BLOQUEADO_INTEGRIDADE', r['resultados'][0])
            self.assertIn('UPDATE_BLOCKED', r['resultados'][0]['observacao'])
            self.assertEqual(self.arq.read_bytes(), antes)                                     # last-known-good intacto

    def test_10b_local_corrompido_e_reparado_pela_fonte_valida(self):
        self.arq.write_bytes(('LEX MACHINA\n' + '=' * 40 + '\nNORMA: Lei 11.340/2006\n' + '=' * 40 + '\n\n' + CORRUPT_HEAD * 3000).encode('utf-8'))
        self.assertTrue(U.arquivo_local_corrompido(self.arq.read_text(encoding='utf-8')))
        r = self.processar((b'\xff\xfe' + pagina(artigos=46).encode('utf-16-le') + b' ' * 1559, {}))
        self.assertEqual(r['resultados'][0]['status'], 'ATUALIZADO', r['resultados'][0])
        novo = self.arq.read_text(encoding='utf-8')
        self.assertIn('CODIFICACAO_ORIGEM: utf-16-le', novo)
        self.assertIn('Art. 46º Disposição', novo)
        self.assertFalse(U.arquivo_local_corrompido(novo))


if __name__ == '__main__':
    unittest.main()
