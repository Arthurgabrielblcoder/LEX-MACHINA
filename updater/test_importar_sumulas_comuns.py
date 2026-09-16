import json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
import requests
from bs4 import BeautifulSoup
import importar_sumulas_comuns as m

def resp(body,url,status=200):
    r=requests.Response(); r.status_code=status; r._content=body if isinstance(body,bytes) else body.encode(); r.url=url; return r

class FonteParsingTests(unittest.TestCase):
    def test_status_vigencia(self):
        self.assertEqual(m._status('Súmula 1'),'vigente')
        self.assertEqual(m._status('Súmula cancelada'),'cancelado')
        self.assertEqual(m._status('Súmula revogada'),'superado')
        self.assertEqual(m._status('Súmula superada'),'superado')

    def test_url_falso_200_vazio_redirecionado(self):
        with self.assertRaises(ValueError): m._oficial('https://example.org/x','STF')
        for r in (resp('',m.STF_LISTA),resp('404 not found',m.STF_LISTA),resp('ok',m.STF_LISTA,202),resp('ok',m.STF_API)):
            with self.assertRaises(ValueError): m._resposta(r,m.STF_LISTA,'STF')

    def test_json_invalido(self):
        for corpo in ('{}','[]','{'):
            with self.assertRaises(ValueError): m._resposta(resp(corpo,m.STF_API),m.STF_API,'STF',True)

    def test_parser_stf_estruturado_exclui_vinculantes(self):
        links=''.join(f'<div class="sumula-item"><a href="?base=30&sumula={1000+n}">Súmula {n}</a></div>' for n in range(1,701))
        soup=BeautifulSoup(f'<div class="sumarioSumulas"><h3>Súmulas</h3>{links}</div>','html.parser')
        dados=[{'num':f'Súmula {n}','link':str(1000+n),'comentario':f'Texto oficial {n}'} for n in range(1,701)]
        s=Mock(); s.post.return_value=resp(json.dumps(dados),m.STF_API)
        with patch.object(m,'_get',return_value=soup): regs=m._stf(s)
        self.assertEqual((len(regs),regs[-1]['numero']),(700,700))
        self.assertTrue(all(x['numero']!=1001 for x in regs))

    def test_parser_stj_total_texto_data_cancelamento(self):
        html='''<span class="numDocs">2 súmulas</span><div id="listaSumulas">
        <div class="gridSumula"><span class="numeroSumula">1</span><div class="blocoVerbete">Texto um. (PRIMEIRA SEÇÃO, julgado em 1/2/2020, DJe de 3/2/2020)</div></div>
        <div class="gridSumula"><span class="numeroSumula">2</span><div class="blocoVerbete">Texto dois. SÚMULA CANCELADA</div></div></div>'''
        cancel='<span class="numDocs">1 súmulas</span><div id="listaSumulas"><span class="numeroSumula">2</span></div>'
        with patch.object(m,'_get',side_effect=[BeautifulSoup(html,'html.parser'),BeautifulSoup(cancel,'html.parser')]): regs=m._stj(Mock())
        self.assertEqual(regs[0]['data'],'3/2/2020'); self.assertEqual(regs[1]['situacao'],'cancelado')

    def test_relacao_exige_cdc_e_artigo(self):
        base={'numero':1,'situacao':'vigente','data':'','url':m.STJ_ITEM.format(numero=1),'observacao':''}
        self.assertEqual(m._novo({**base,'texto':'art. 26 do CDC'},'STJ','2026-09-16')['relacionado_a'],['CDC art. 26'])
        self.assertEqual(m._novo({**base,'texto':'consumidor e art. 5 da Constituição'},'STJ','2026-09-16')['relacionado_a'],[])

class CatalogoTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(dir=Path(__file__).parent/'saida'); self.addCleanup(self.t.cleanup)
        self.p=Path(self.t.name)/'c.json'; self.antigo={'tribunal':'STJ','tipo':'sumula','numero':10,'tema':'original','arquivo':'stj_sumula_10.txt','pasta_destino':'x','texto':'consumidor','relacionado_a':['CDC art. 1'],'fonte':'STJ','status':'julgado'}
        self.outro={'tribunal':'STF','tipo':'sumula_vinculante','numero':10}
        self.p.write_text(json.dumps([self.antigo]),encoding='utf8')
        self.stf=[{'numero':20,'texto':'consumidor','situacao':'vigente','data':'','url':m.STF_DETALHE.format(id_stf=20),'observacao':''}]
        self.stj=[{'numero':10,'texto':'consumidor','situacao':'vigente','data':'','url':m.STJ_ITEM.format(numero=10)}, {'numero':11,'texto':'consumidor','situacao':'cancelado','data':'','url':m.STJ_ITEM.format(numero=11)}]

    def executar(self,outros=()):
        with patch.object(m,'_criar_session',return_value=Mock()),patch.object(m,'_stf',return_value=self.stf),patch.object(m,'_stj',return_value=self.stj),patch.object(m,'_detalhe_stf',side_effect=lambda s,x:x):
            return m.atualizar_sumulas_comuns(self.p,False,outros)

    def test_preserva_stj_id_campos_e_separa_vinculante(self):
        self.assertTrue(self.executar([self.outro])['ok']); d=json.loads(self.p.read_bytes())
        atual=next(x for x in d if x.get('tribunal')=='STJ'); self.assertEqual(atual['tema'],'original'); self.assertEqual(atual['relacionado_a'],['CDC art. 1'])
        self.assertEqual(sum(x.get('tipo')=='sumula' and x.get('numero')==10 for x in d),1)

    def test_cancelada_nao_importada(self):
        self.assertTrue(self.executar()['ok']); d=json.loads(self.p.read_bytes()); self.assertFalse(any(x.get('numero')==11 for x in d))

    def test_falha_parcial_preserva_bytes(self):
        original=self.p.read_bytes()
        with patch.object(m,'_criar_session',side_effect=requests.exceptions.SSLError('TLS')): self.assertFalse(m.atualizar_sumulas_comuns(self.p,False)['ok'])
        self.assertEqual(original,self.p.read_bytes())

    def test_duplicacao_preserva(self):
        original=self.p.read_bytes(); self.assertFalse(self.executar([self.antigo])['ok']); self.assertEqual(original,self.p.read_bytes())
