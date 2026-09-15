import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
import importar_stf_repercussao_geral as stf


class CatalogoTemporario:
    def setUp(self):
        (Path(__file__).parent / 'saida').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent / 'saida')
        self.addCleanup(self.tmp.cleanup)
        self.catalogo = Path(self.tmp.name) / 'catalogo.json'
        self.anterior = [dict(tribunal='STF', tipo='repercussao_geral', numero=1,
                              origem_importacao='STF_OFICIAL_REPERCUSSAO_GERAL'),
                         dict(tribunal='STJ', numero=10)]
        self.catalogo.write_text(json.dumps(self.anterior), encoding='utf-8')
        self.original = self.catalogo.read_bytes()
        self.session = Mock()
        p = patch.object(stf, '_criar_session', return_value=self.session)
        p.start()
        self.addCleanup(p.stop)

    def atualizar(self):
        return stf.atualizar_catalogo_precedentes(self.catalogo, verbose=False)


class ImportadorTests(CatalogoTemporario, unittest.TestCase):
    def test_preserva_falhas_rede_e_layout(self):
        for resposta in (requests.exceptions.SSLError('certificado'),
                         requests.Timeout('rede'), [],
                         [dict(numero=1, texto_linha='outro assunto')]):
            with self.subTest(resposta=resposta):
                kwargs = ({'side_effect': resposta} if isinstance(resposta, Exception)
                          else {'return_value': resposta})
                with patch.object(stf, '_descobrir_temas', **kwargs):
                    self.assertFalse(self.atualizar()['ok'])
                self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_preserva_importacao_parcial_ou_vazia(self):
        temas = [dict(numero=n, texto_linha='consumidor') for n in (1, 2)]
        for detalhes in ([self.anterior[0], requests.Timeout()], [None, None]):
            with patch.object(stf, '_descobrir_temas', return_value=temas), \
                 patch.object(stf, '_carregar_detalhe', side_effect=detalhes):
                self.assertFalse(self.atualizar()['ok'])
                self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_sucesso_preserva_outras_entradas(self):
        novo = dict(self.anterior[0], texto='Texto oficial', relacionado_a=[])
        with patch.object(stf, '_descobrir_temas', return_value=[dict(numero=1, texto_linha='consumidor')]), \
             patch.object(stf, '_carregar_detalhe', return_value=novo):
            self.assertTrue(self.atualizar()['ok'])
        self.assertEqual(json.loads(self.catalogo.read_text()), [self.anterior[1], novo])
        self.session.close.assert_called_once()

    def test_catalogo_invalido_preservado(self):
        for texto in ('{quebrado', '{}'):
            self.catalogo.write_text(texto)
            self.assertFalse(self.atualizar()['ok'])
            self.assertEqual(self.catalogo.read_text(), texto)

    def test_tema_anterior_omitido_preserva_catalogo(self):
        with patch.object(stf, '_descobrir_temas', return_value=[dict(numero=2, texto_linha='consumidor')]), \
             patch.object(stf, '_carregar_detalhe', return_value=dict(numero=2)):
            self.assertFalse(self.atualizar()['ok'])
        self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_dependencia_ausente_preserva_catalogo(self):
        with patch.object(stf, '_criar_session', side_effect=ImportError('truststore')):
            self.assertFalse(self.atualizar()['ok'])
        self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_falha_gravacao_preserva_catalogo(self):
        with patch.object(stf, '_descobrir_temas', return_value=[dict(numero=1, texto_linha='consumidor')]), \
             patch.object(stf, '_carregar_detalhe', return_value=self.anterior[0]), \
             patch.object(Path, 'replace', side_effect=OSError('arquivo ocupado')):
            self.assertFalse(self.atualizar()['ok'])
        self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_detalhe_invalido_e_andamento_indisponivel(self):
        def resposta(html):
            return Mock(content=html.encode('utf-8'), status_code=200)
        self.session.get.return_value = resposta('<html>Manutenção</html>')
        with self.assertRaises(RuntimeError):
            stf._carregar_detalhe(self.session, dict(numero=1))
        html = '''<meta charset="utf-8"><p>Tema: 1</p><p>Título: Consumidor</p>
        <p>Descrição: Descrição oficial</p><p>Ver assuntos:</p>
        <p>Repercussão geral: Há repercussão geral</p>
        <p>Situação: Mérito julgado</p><p>Tese:</p>
        <a href="verAndamentoProcesso.asp">Andamento</a>'''
        self.session.get.side_effect = [resposta(html), requests.Timeout()]
        with self.assertRaisesRegex(RuntimeError, 'andamento'):
            stf._carregar_detalhe(self.session, dict(numero=1))

    def test_tls_obrigatorio_sem_injecao_global(self):
        contexto_original = ssl.SSLContext
        adapter = stf._AdaptadorTLSNativo()
        self.addCleanup(adapter.close)
        req = requests.Request('GET', stf.URL_TODOS_TEMAS).prepare()
        _, kwargs = adapter.build_connection_pool_key_attributes(req, True)
        self.assertIs(kwargs['ssl_context'], adapter.contexto)
        self.assertEqual(adapter.contexto.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(adapter.contexto.check_hostname)
        self.assertIs(ssl.SSLContext, contexto_original)
        with self.assertRaises(ValueError):
            adapter.build_connection_pool_key_attributes(req, False)

    def test_relacoes_exigem_referencia_explicita(self):
        self.assertEqual(stf._relacoes_cdc('art. 14 do CDC'), ['CDC art. 14'])
        self.assertEqual(stf._relacoes_cdc('Consumo. art. 5 da Constituição.'), [])
        self.assertEqual(stf._relacoes_cdc('CDC. art. 5 da Constituição.'), [])

    def test_relacoes_nao_atravessam_outras_leis(self):
        for texto in ('art. 5 da Constituição e art. 14 do CDC',
                      'art. 16 da Lei 7.347/1985 e art. 14 do CDC'):
            self.assertEqual(stf._relacoes_cdc(texto), ['CDC art. 14'])
        self.assertEqual(stf._relacoes_cdc('arts. 6º, III, 14 e 51 da Lei 8.078/1990'),
                         ['CDC art. 6', 'CDC art. 14', 'CDC art. 51'])
        self.assertEqual(stf._relacoes_cdc('art. 93, II, da Lei 8.078/1990'), ['CDC art. 93'])
        self.assertEqual(stf._relacoes_cdc('Lei 8.078/1990, arts. 6º e 14.'),
                         ['CDC art. 6', 'CDC art. 14'])


class FonteOficialTests(CatalogoTemporario, unittest.TestCase):
    """Respostas sintéticas com o contrato observado no JavaScript oficial."""

    def registro(self, numero='1'):
        return dict(numeroTema=numero, incidente='123', siglaClasse='RE',
                    numeroProcesso='456', descricaoTese='Consumidor: art. 14 do CDC.',
                    dataAndamento='15/09/2026')

    def resposta(self, dados, status=200):
        corpo = dados if isinstance(dados, bytes) else json.dumps(dados, ensure_ascii=False).encode('utf-8')
        return Mock(status_code=status, content=corpo, url=stf.URL_TESES_JSON)

    def detalhe(self, numero=1, rg='Há repercussão geral'):
        html = f'''<meta charset="utf-8"><section id="conteudo">
        <p>Tema: {numero}</p><p>Título: Defesa do consumidor</p>
        <p>Descrição: Descrição oficial.</p><p>Ver assuntos:</p>
        <h3>Informações gerais</h3><p>Leading Case: RE 456</p>
        <p>Ministro: MIN. TESTE</p><h3>Situação atual</h3>
        <p>Repercussão geral: {rg}</p><p>Data da Repercussão geral: 01/01/2020</p>
        <p>Situação: Trânsito em Julgado - 01/01/2021</p></section>
        <footer>art. 43 do CDC</footer>'''
        return Mock(status_code=200, content=html.encode('utf-8'), url=stf.URL_TEMA.format(numero=numero))

    def test_json_completo_sem_paginacao_servidor(self):
        self.session.post.return_value = self.resposta([self.registro(str(n)) for n in range(1, 26)])
        temas = stf._descobrir_temas(self.session)
        self.assertEqual(len(temas), 25)
        self.session.post.assert_called_once_with(stf.URL_TESES_JSON, data={'tipo': 'com'},
                                                 headers=stf.HEADERS_STF, timeout=60,
                                                 allow_redirects=False)

    def test_json_e_detalhe_integrados(self):
        self.session.post.return_value = self.resposta([self.registro()])
        self.session.get.return_value = self.detalhe()
        resultado = self.atualizar()
        self.assertTrue(resultado['ok'])
        novo = json.loads(self.catalogo.read_text(encoding='utf-8'))[-1]
        self.assertEqual(novo['relacionado_a'], ['CDC art. 14'])
        self.assertEqual(novo['texto_oficial_verificado'], self.registro()['descricaoTese'])
        self.assertEqual(novo['data_tese'], '15/09/2026')
        self.assertEqual(novo['situacao_oficial_stf'], 'Trânsito em Julgado - 01/01/2021')
        self.session.get.assert_called_once()  # Tese vem do JSON, sem consulta extra ao andamento.

    def test_falso_sucesso_e_respostas_incompletas(self):
        erros = [b'<h1>404</h1><p>Desculpe, mas n\xc3\xa3o encontramos o que voc\xc3\xaa est\xc3\xa1 procurando.</p>',
                 b'<html>Access Denied</html>', b'<html>Nova estrutura</html>',
                 b'[{"numeroTema":', [], {'dados': [self.registro()]},
                 [self.registro(), self.registro()], [dict(self.registro(), numeroTema='x')],
                 [dict(self.registro(), dataAndamento='31/02/2026')],
                 [dict(self.registro(), descricaoTese='')],
                 [dict(self.registro(), incidente=None)]]
        for dados in erros:
            with self.subTest(dados=dados):
                self.session.post.return_value = self.resposta(dados)
                self.assertFalse(self.atualizar()['ok'])
                self.assertEqual(self.original, self.catalogo.read_bytes())
        self.session.post.return_value = self.resposta(b'', status=202)
        self.assertFalse(self.atualizar()['ok'])
        self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_detalhe_errado_e_falha_parcial_preservam(self):
        self.session.post.return_value = self.resposta([self.registro(), self.registro('2')])
        self.session.get.side_effect = [self.detalhe(), self.detalhe(numero=999)]
        resultado = self.atualizar()
        self.assertFalse(resultado['ok'])
        self.assertEqual(resultado['temas_descobertos'], 2)
        self.assertEqual(resultado['candidatos'], 2)
        self.assertEqual(resultado['importados'], 0)
        self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_rejeita_rg_negada(self):
        self.session.post.return_value = self.resposta([self.registro()])
        self.session.get.return_value = self.detalhe(rg='Não há repercussão geral')
        self.assertFalse(self.atualizar()['ok'])
        self.assertEqual(self.original, self.catalogo.read_bytes())

    def test_rejeita_url_externa_e_http(self):
        for url in ('http://portal.stf.jus.br/tema', 'https://exemplo.com/tema'):
            with self.assertRaises(RuntimeError):
                stf._obter_html(self.session, url)
        self.session.get.assert_not_called()

    def test_redirecionamento_nao_e_seguido(self):
        self.session.post.return_value = self.resposta(b'redirect', status=302)
        self.assertFalse(self.atualizar()['ok'])
        self.assertFalse(self.session.post.call_args.kwargs['allow_redirects'])
        self.assertEqual(self.original, self.catalogo.read_bytes())


if __name__ == '__main__':
    (Path(__file__).parent / 'saida').mkdir(exist_ok=True)
    unittest.main()
