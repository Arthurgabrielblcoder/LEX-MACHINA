import json, ssl, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock, patch
import requests
from bs4 import BeautifulSoup
import importar_stf_sumulas_vinculantes as sv
import importar_stf_repercussao_geral as rg

def lista(itens=((1,1185,''),(2,1188,''))):
    links=''.join(f'<div class="sumula-item"><a href="sumariosumulas.asp?base=26&sumula={i}">Súmula Vinculante {n} {s}</a></div>' for n,i,s in itens)
    return f'<div class="sumarioSumulas"><h3>Súmulas Vinculantes</h3>{links}</div>'

def detalhe(n=1, texto='Serviço ao consumidor. art. 14 do CDC', estado=''):
    return f'''<section class="conteudo"><div class="container"><div class="titulo">Súmula Vinculante {n} {estado}</div><div class="parCOM">{texto}</div><div class="titulo">Observação</div><div class="parCOM">Data de publicação do enunciado: DJE de 20-6-2008.</div></div></section>'''

def resposta(html, status=200, url=sv.URL_LISTA):
    r=requests.Response(); r.status_code=status; r._content=html.encode(); r.url=url; return r

class ParsingTests(unittest.TestCase):
    def test_lista_detalhe_e_categoria_propria(self):
        s=Mock(); s.get.return_value=resposta(lista()); itens=sv._descobrir(s)
        self.assertEqual([x['numero'] for x in itens],[1,2])
        d=sv._parsear_detalhe(BeautifulSoup(detalhe(),'html.parser'),itens[0])
        r=sv._registro(d,'2026-09-16')
        self.assertEqual((r['tipo'],r['data_publicacao']),('sumula_vinculante','20-6-2008'))
        self.assertEqual(r['relacionado_a'],['CDC art. 14'])

    def test_lista_vazia_duplicada_ou_incompleta(self):
        for h in ('<html/>',lista(()),lista(((1,1,''),(1,2,''))),lista(((1,1,''),(3,3,'')))):
            s=Mock(); s.get.return_value=resposta(h)
            with self.subTest(h=h),self.assertRaises(ValueError): sv._descobrir(s)

    def test_detalhe_identidade_situacao_data_invalidos(self):
        item={'numero':1,'id_stf':1,'url':sv.URL_DETALHE.format(id_stf=1),'situacao_lista':'vigente'}
        for h in (detalhe(2),detalhe(estado='(cancelada)'),detalhe().replace('20-6-2008','31-2-2008'),'<html/>'):
            with self.subTest(h=h),self.assertRaises(ValueError): sv._parsear_detalhe(BeautifulSoup(h,'html.parser'),item)

    def test_relacao_cdc_nao_inferida(self):
        base={'numero':1,'situacao':'vigente','data_publicacao':'20-6-2008','url':sv.URL_DETALHE.format(id_stf=1),'observacao':''}
        for texto,esperado in [('art. 14 do CDC',['CDC art. 14']),('consumidor, art. 14 da Constituição',[]),('Código de Defesa do Consumidor',[])]:
            self.assertEqual(sv._registro({**base,'texto':texto},'2026-09-16')['relacionado_a'],esperado)

class FonteTests(unittest.TestCase):
    def test_tls_e_verify_false(self):
        a=rg._AdaptadorTLSNativo(); self.addCleanup(a.close)
        req=requests.Request('GET',sv.URL_LISTA).prepare(); _,kw=a.build_connection_pool_key_attributes(req,True)
        self.assertEqual(kw['ssl_context'].verify_mode,ssl.CERT_REQUIRED); self.assertTrue(kw['ssl_context'].check_hostname)
        with self.assertRaises(ValueError): a.build_connection_pool_key_attributes(req,False)

    def test_url_resposta_vazia_redirecionada_falso_200(self):
        for u in ('http://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=26','https://example.org/x?base=26',sv.URL_LISTA+'&x=1'):
            with self.assertRaises(ValueError): sv._url_oficial(u)
        for r in (resposta(''),resposta('404 not found'),resposta('ok',202),resposta('ok',url=sv.URL_LISTA+'&sumula=1')):
            with self.assertRaises(ValueError): sv._validar_resposta(r,sv.URL_LISTA)

class PreservacaoTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(dir=Path(__file__).parent/'saida'); self.addCleanup(self.t.cleanup)
        self.p=Path(self.t.name)/'c.json'; self.rg={'tribunal':'STF','tipo':'repercussao_geral','numero':1075}
        self.p.write_text(json.dumps([self.rg]),encoding='utf8')
        self.item={'numero':1,'id_stf':1,'url':sv.URL_DETALHE.format(id_stf=1),'situacao_lista':'vigente'}

    def executar(self,outros=()):
        with patch.object(sv,'_criar_session',return_value=Mock()),patch.object(sv,'_descobrir',return_value=[self.item]),patch.object(sv,'_obter',return_value=BeautifulSoup(detalhe(),'html.parser')):
            return sv.atualizar_sumulas_vinculantes(self.p,False,outros)

    def test_preserva_camadas_e_idempotencia(self):
        self.assertTrue(self.executar()['ok']); primeiro=self.p.read_bytes(); self.assertTrue(self.executar()['ok']); self.assertEqual(primeiro,self.p.read_bytes())
        self.assertEqual(json.loads(primeiro)[0],self.rg)

    def test_falha_parcial_e_catalogo_invalido_preservam(self):
        original=self.p.read_bytes()
        with patch.object(sv,'_criar_session',side_effect=requests.exceptions.SSLError('TLS')): self.assertFalse(sv.atualizar_sumulas_vinculantes(self.p,False)['ok'])
        self.assertEqual(original,self.p.read_bytes())
        self.p.write_bytes(b'{'); invalido=self.p.read_bytes(); self.assertFalse(sv.atualizar_sumulas_vinculantes(self.p,False)['ok']); self.assertEqual(invalido,self.p.read_bytes())

    def test_duplicacao_preserva(self):
        original=self.p.read_bytes()
        duplicada={'tribunal':'STF','tipo':'sumula_vinculante','numero':1}
        self.assertFalse(self.executar([duplicada])['ok']); self.assertEqual(original,self.p.read_bytes())
        comum={'tribunal':'STF','tipo':'sumula','numero':1}
        self.assertTrue(self.executar([comum])['ok'])
        tipos={(x['tipo'],x['numero']) for x in json.loads(self.p.read_bytes())}
        self.assertIn(('sumula_vinculante',1),tipos)
