import copy
import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
import importar_stf_controle_concentrado as cc
import importar_stf_repercussao_geral as rg

FIXTURES = Path(__file__).parent / 'tests' / 'fixtures'


def base():
    return json.loads((FIXTURES / 'stf_controle_amostra.json').read_text(encoding='utf-8'))


def contagens():
    return {t: dict(encontrados=0, decisoes_encontradas=0, consumeristas=0,
                   sem_merito_colegiado_verificavel=0) for t in cc.TIPOS}


def selecionar(dados):
    return cc._selecionar(dados['processos'], dados['decisoes'], contagens(), '2026-09-15')


class ParsingTests(unittest.TestCase):
    def test_amostra_oficial_merito_e_embargos(self):
        registros = selecionar(base())
        adi = next(r for r in registros if r['tipo'] == 'adi')
        self.assertEqual(adi['numero'], 2591)
        self.assertEqual(adi['relacionado_a'], ['CDC art. 3'])
        self.assertEqual(adi['data_julgamento'], '07/06/2006')
        self.assertIn('14/12/2006', adi['texto'])
        self.assertIn('embargos', adi['texto'])
        self.assertEqual(adi['evidencias_relacoes_cdc'][0]['campo'], 'Legislação')

    def test_quatro_tipos_e_mesmo_numero_nao_colidem(self):
        dados = base()
        for i, p in enumerate(dados['processos']):
            p['Processo'] = cc.TIPOS[i].upper() + ' 10'
            p['Ramo do Direito'] = 'DIREITO DO CONSUMIDOR'
            p['Legislação'] = '*NI*'
        dados['decisoes'] = [dict(Processo=p['Processo'], Data='01/01/2025',
            Descrição='Procedente', **{'Andamento agrupado': 'Procedente', 'Subgrupo': 'Decisão Final',
            'Observação': 'O Tribunal julgou procedente a ação. Art. 14 do CDC.'}) for p in dados['processos']]
        regs = selecionar(dados)
        self.assertEqual({r['tipo'] for r in regs}, set(cc.TIPOS))
        self.assertEqual(len({r['arquivo'] for r in regs}), 4)
        self.assertTrue(all(r['relacionado_a'] == ['CDC art. 14'] for r in regs))

    def test_nao_transformar_liminar_ou_monocratica_em_merito(self):
        for subgrupo, texto, resultado in [
            ('Decisão Liminar', 'O Tribunal deferiu a liminar.', 'Procedente'),
            ('Decisão Final', 'Julgo procedente. Publique-se.', 'Procedente'),
            ('Decisão Final', 'Julgo procedente. Como decidiu o Tribunal, aplica-se o precedente.', 'Procedente'),
            ('Decisão Final', 'O Tribunal extinguiu a ação.', 'Extinto o processo'),
            ('Decisão Final', '*NI*', 'Procedente'),
        ]:
            with self.subTest(subgrupo=subgrupo, texto=texto):
                dados = base()
                for d in dados['decisoes']:
                    d.update(Subgrupo=subgrupo, Observação=texto)
                    d['Andamento agrupado'] = resultado
                self.assertEqual(selecionar(dados), [])

    def test_data_ausente_nao_e_inventada(self):
        dados = base()
        for d in dados['decisoes']:
            d['Data'] = '-'
        self.assertEqual(selecionar(dados), [])
        dados['decisoes'][0]['Data'] = '31/02/2025'
        with self.assertRaises(ValueError):
            selecionar(dados)

    def test_relacoes_nao_inferem_artigo_por_assunto(self):
        self.assertEqual(cc._relacoes_legislacao('Lei Federal nº 8.078, de 1990, Art. 43'), ['CDC art. 43'])
        self.assertEqual(cc._relacoes_legislacao('Código de Defesa do Consumidor de 1990, Art. 3º, § 2º'), ['CDC art. 3'])
        for texto in ['Código de Defesa do Consumidor', 'consumidor, art. 14 da Constituição',
                      'Lei Estadual nº 8.078, de 1990, Art. 43',
                      'Lei Federal nº 8.078, de 1991, Art. 43',
                      'CDC e art. 14 da Constituição',
                      'Código de Defesa do Consumidor; Código Civil, Art. 50']:
            self.assertEqual(cc._relacoes_legislacao(texto), [])
        dados = base()
        for p in dados['processos']:
            p['Legislação'] = '*NI*'
            p['Assunto relacionado'] = 'CDC art. 99'
        self.assertTrue(all('CDC art. 99' not in r['relacionado_a'] for r in selecionar(dados)))

    def test_fontes_e_identidades_invalidas(self):
        for url in ['http://portal.stf.jus.br/processos/detalhe.asp?incidente=1',
                    'https://portal.stf.jus.br.evil.test/processos/detalhe.asp?incidente=1',
                    'https://usuario@portal.stf.jus.br/processos/detalhe.asp?incidente=1',
                    'https://portal.stf.jus.br:444/processos/detalhe.asp?incidente=1',
                    'https://portal.stf.jus.br/noticia?incidente=1']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                cc._url_oficial(url, processo=True)
        for processo in ['RE 10', 'ADI 0', 'ADPF -1', 'ADI 2 citado na ADC 3']:
            with self.assertRaises(ValueError):
                cc._identidade(processo)

    def test_duplicatas_e_classe_ausente_rejeitadas(self):
        dados = base()
        dados['processos'].append(copy.deepcopy(dados['processos'][0]))
        with self.assertRaises(ValueError):
            selecionar(dados)
        dados = base()
        dados['processos'] = [p for p in dados['processos'] if not p['Processo'].startswith('ADO')]
        with self.assertRaises(ValueError):
            selecionar(dados)


class FontesTests(unittest.TestCase):
    def test_http_vazio_redirecionado_e_falso_200(self):
        for status, conteudo, url in [
            (202, b'', cc.URL_PAINEL), (200, b'', cc.URL_PAINEL),
            (200, b'<html>404 not found</html>', cc.URL_PAINEL),
            (200, b'<html>Access denied</html>', cc.URL_PAINEL),
            (200, b'pagina nao encontrada', cc.URL_PAINEL),
            (200, b'ok', 'https://example.org/'), (302, b'outro', cc.URL_PAINEL),
        ]:
            r = requests.Response()
            r.status_code, r._content, r.url = status, conteudo, url
            with self.subTest(status=status, conteudo=conteudo), self.assertRaises(ValueError):
                cc._validar_http(r, cc.URL_PAINEL)

    def test_colunas_json_na_ordem_oficial(self):
        fixture = json.loads((FIXTURES / 'stf_qlik_colunas.json').read_text(encoding='utf-8'))
        layout = fixture['layout']
        layout['qHyperCube']['qSize']['qcy'] = 3
        cliente = Mock()
        cliente.rpc.side_effect = [dict(qReturn=dict(qHandle=2)), dict(qLayout=layout),
                                   fixture['paginas'], dict(qLayout=layout)]
        linhas = cc._ler_tabela(cliente, 1, 'decisoes')
        self.assertEqual(linhas[0]['Data'], '02/12/1999')
        self.assertEqual(linhas[0]['Subgrupo'], 'Decisão Final')
        self.assertIn('O TRIBUNAL', linhas[0]['Observação'])

    def test_paginacao_incompleta_repetida_e_filtro(self):
        fixture = json.loads((FIXTURES / 'stf_qlik_colunas.json').read_text(encoding='utf-8'))
        for defeito in ['truncada', 'area', 'duplicada', 'filtro', 'vazia', 'colunas', 'mudanca']:
            with self.subTest(defeito=defeito):
                f = copy.deepcopy(fixture)
                layout = f['layout']
                layout['qHyperCube']['qSize']['qcy'] = 3
                final = copy.deepcopy(layout)
                pagina = f['paginas']['qDataPages'][0]
                if defeito == 'truncada':
                    pagina['qMatrix'].pop()
                elif defeito == 'area':
                    pagina['qArea']['qTop'] = 3
                elif defeito == 'duplicada':
                    pagina['qMatrix'][1] = pagina['qMatrix'][0]
                elif defeito == 'filtro':
                    layout['qHyperCube']['qDimensionInfo'][0]['qStateCounts']['qSelected'] = 1
                elif defeito == 'vazia':
                    layout['qHyperCube']['qSize']['qcy'] = 0
                elif defeito == 'colunas':
                    layout['qHyperCube']['qColumnOrder'] = [0] * 6
                else:
                    final['qHyperCube']['qSize']['qcy'] = 4
                cliente = Mock()
                cliente.rpc.side_effect = [dict(qReturn=dict(qHandle=2)), dict(qLayout=layout),
                                           f['paginas'], dict(qLayout=final)]
                with self.assertRaises(ValueError):
                    cc._ler_tabela(cliente, 1, 'decisoes')

    def test_rpc_invalido_erro_e_notificacao(self):
        cliente = object.__new__(cc.ClienteQlik)
        cliente.numero = 0
        cliente.ws = Mock()
        cliente.ws.recv.side_effect = ['{"jsonrpc":"2.0","method":"OnConnected"}',
            '{"jsonrpc":"2.0","id":1,"result":{"ok":true}}']
        self.assertEqual(cliente.rpc(1, 'GetLayout', []), {'ok': True})
        for resposta in ['<html>erro</html>', '[]', '{}',
                         '{"jsonrpc":"2.0","id":1,"error":{"code":1}}']:
            cliente.numero = 0
            cliente.ws.recv.side_effect = None
            cliente.ws.recv.return_value = resposta
            with self.assertRaises(ValueError):
                cliente.rpc(1, 'GetLayout', [])

    def test_tls_nativo_e_redirecionamento_bloqueado(self):
        with rg._criar_session() as session:
            resposta = Mock(status_code=200, content=b'qliksense.js', text='qliksense.js', url=cc.URL_PAINEL)
            script = Mock(status_code=200, content=b'js', text=' '.join([cc.APP_ID, *cc.OBJETOS.values()]), url=cc.URL_SCRIPT)
            with patch.object(session, 'get', side_effect=[resposta, script]) as get, \
                    patch('websocket.create_connection') as conectar:
                cliente = cc.ClienteQlik(session)
                contexto = conectar.call_args.kwargs['sslopt']['context']
                self.assertEqual(contexto.verify_mode, ssl.CERT_REQUIRED)
                self.assertTrue(contexto.check_hostname)
                self.assertIs(contexto, session.get_adapter(cc.URL_PAINEL).contexto)
                self.assertEqual(conectar.call_args.kwargs['redirect_limit'], 0)
                self.assertTrue(all(c.kwargs['allow_redirects'] is False for c in get.call_args_list))
                cliente.close()


class PreservacaoTests(unittest.TestCase):
    def setUp(self):
        pasta = Path(__file__).parent / 'saida'
        pasta.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=pasta)
        self.addCleanup(self.tmp.cleanup)
        self.catalogo = Path(self.tmp.name) / 'catalogo.json'
        self.rg = dict(tribunal='STF', tipo='repercussao_geral', numero=1075,
                       relacionado_a=['CDC art. 93'], origem_importacao='STF_OFICIAL_REPERCUSSAO_GERAL')
        self.catalogo.write_text(json.dumps([self.rg]), encoding='utf-8')
        self.original = self.catalogo.read_bytes()
        self.dados = base()
        self.session = Mock()
        p = patch.object(cc, '_criar_session', return_value=self.session)
        p.start()
        self.addCleanup(p.stop)

    def executar(self, **kwargs):
        with patch.object(cc, '_consultar_base', return_value=(
                self.dados['processos'], self.dados['decisoes'], '2026-09-15')):
            return cc.atualizar_controle_concentrado(self.catalogo, verbose=False, **kwargs)

    def test_sucesso_preserva_rg_e_idempotencia(self):
        self.assertTrue(self.executar()['ok'])
        antes = self.catalogo.read_bytes()
        self.assertTrue(self.executar()['ok'])
        self.assertEqual(antes, self.catalogo.read_bytes())
        self.assertEqual(json.loads(antes)[0], self.rg)
        self.session.close.assert_called()

    def test_falha_de_rede_ou_pagina_preserva_bytes(self):
        for exc in [requests.exceptions.SSLError('TLS'), requests.Timeout('rede'),
                    ValueError('página incompleta'), ValueError('JSON inválido')]:
            with patch.object(cc, '_consultar_base', side_effect=exc):
                r = cc.atualizar_controle_concentrado(self.catalogo, verbose=False)
            self.assertFalse(r['ok'])
            self.assertFalse(r['contagens_completas'])
            self.assertEqual(self.catalogo.read_bytes(), self.original)

    def test_vazios_e_fontes_invalidas_preservam(self):
        for defeito in ['processos', 'decisoes', 'url', 'campo', 'sem_merito']:
            with self.subTest(defeito=defeito):
                self.dados = base()
                if defeito in ('processos', 'decisoes'):
                    self.dados[defeito] = []
                elif defeito == 'url':
                    self.dados['processos'][0]['Link Processo'] = 'https://example.org/'
                elif defeito == 'campo':
                    del self.dados['decisoes'][0]['Observação']
                else:
                    for d in self.dados['decisoes']:
                        d['Subgrupo'] = 'Decisão Liminar'
                self.assertFalse(self.executar()['ok'])
                self.assertEqual(self.catalogo.read_bytes(), self.original)

    def test_catalogo_invalido_preservado(self):
        for conteudo in [b'{', b'{}', b'[null]']:
            self.catalogo.write_bytes(conteudo)
            self.assertFalse(self.executar()['ok'])
            self.assertEqual(self.catalogo.read_bytes(), conteudo)

    def test_falha_gravacao_e_substituicao_preservam(self):
        for metodo in ['write_text', 'replace']:
            with patch.object(Path, metodo, side_effect=OSError('disco')):
                self.assertFalse(self.executar()['ok'])
            self.assertEqual(self.catalogo.read_bytes(), self.original)

    def test_anterior_ausente_nao_e_apagado(self):
        anterior = dict(tribunal='STF', tipo='adi', numero=999999, origem_importacao=cc.ORIGEM)
        self.catalogo.write_text(json.dumps([self.rg, anterior]), encoding='utf-8')
        original = self.catalogo.read_bytes()
        self.assertFalse(self.executar()['ok'])
        self.assertEqual(self.catalogo.read_bytes(), original)

    def test_duplicacao_entre_categorias_e_entradas_manuais(self):
        manual = dict(tribunal='STF', tipo='adi', numero=2591, nota='preservar')
        self.catalogo.write_text(json.dumps([self.rg, manual]), encoding='utf-8')
        r = self.executar()
        self.assertTrue(r['ok'])
        self.assertEqual(r['classes']['adi']['duplicados_preservados'], 1)
        self.assertIn(manual, json.loads(self.catalogo.read_text(encoding='utf-8')))
        self.catalogo.write_bytes(self.original)
        externo = dict(tribunal='STF', tipo='acordao', processos=['ADI 2591'])
        r = self.executar(outros_registros=[externo])
        self.assertEqual(r['classes']['adi']['importados'], 0)
        self.assertEqual(r['classes']['adi']['duplicados_preservados'], 1)

    def test_rg_preserva_novas_classes(self):
        self.assertTrue(self.executar()['ok'])
        anteriores = json.loads(self.catalogo.read_text(encoding='utf-8'))
        with patch.object(rg, '_criar_session', return_value=Mock()), \
                patch.object(rg, '_descobrir_temas', return_value=[dict(numero=1075, texto_linha='consumidor')]), \
                patch.object(rg, '_carregar_detalhe', return_value=self.rg):
            self.assertTrue(rg.atualizar_catalogo_precedentes(self.catalogo, verbose=False)['ok'])
        depois = json.loads(self.catalogo.read_text(encoding='utf-8'))
        self.assertEqual([r for r in anteriores if r != self.rg], [r for r in depois if r != self.rg])

    def test_integracao_renderiza_decisao_e_vinculo_no_indice(self):
        import main
        registro = next(r for r in selecionar(base()) if r['tipo'] == 'adi')
        with patch.object(main, 'PASTA_SAIDA', Path(self.tmp.name)):
            main.salvar_jurisprudencia(registro)
            indice = main.gerar_indice_relacoes_especializado([registro], 'precedentes')
        texto = (Path(self.tmp.name) / registro['pasta_destino'] / registro['arquivo']).read_text(encoding='utf-8')
        self.assertIn('DECISÃO DE MÉRITO E ANDAMENTOS POSTERIORES:', texto)
        self.assertNotIn('TESE OFICIAL VERIFICADA', texto)
        self.assertIn('CDC art. 3|STF|adi|2591|', indice.read_text(encoding='utf-8'))

    def test_opcao_de_ignorar_controle_preserva_opcao_rg(self):
        import main
        with patch('sys.argv', ['main.py', '--sem-stf-controle']):
            args = main.argumentos_main()
        self.assertTrue(args.sem_stf_controle)
        self.assertFalse(args.sem_stf)


if __name__ == '__main__':
    unittest.main()
