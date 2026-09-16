import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

import importar_stj_repetitivos as m


def resposta(corpo, url=m.URL_TEMAS, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = corpo if isinstance(corpo, bytes) else corpo.encode("utf-8")
    r.url = url
    return r


def tema(numero=1, situacao="Trânsito em Julgado", texto="Relação de consumo"):
    return {
        "sequencialPrecedente": str(100 + numero), "tipoPrecedente": "Tema",
        "numeroPrecedente": str(numero), "dataPrimeiraAfetacao": "01/02/2020",
        "dataJulgamento": "02/03/2021", "dataPublicacaoAcordao": "03/04/2021",
        "situacao": situacao, "informacoesComplementares": "",
        "questaoSubmetidaAJulgamento": texto, "teseFirmada": texto,
        "anotacoesNUGEPNAC": "", "delimitacaoJulgado": "",
        "entendimentoAnterior": "", "referenciaLegislativa": "",
        "referenciaSumular": "", "sumulaOriginada": "", "audienciaPublica": "",
        "dataAudienciaPublica": "", "orgaoJulgador": "SEGUNDA SEÇÃO",
        "Assuntos": "DIREITO DO CONSUMIDOR", "numeroRepercussaoGeralSTF": "",
        "descricaoRepercussaoGeral": "",
    }


def processo(numero=1, desafetacao=""):
    return {
        "processo": f"REsp {numero}", "relator": "Ministro X",
        "leading_case": "Sim", "data_afetacao": "2020-02-01",
        "data_julgamento": "2021-03-02", "desafetacao": desafetacao,
    }


class FonteEParsingTests(unittest.TestCase):
    def test_fonte_oficial_e_tls_sem_desativar_verificacao(self):
        session = Mock()
        cab = list(m.COLUNAS_TEMAS)
        out = io.StringIO(); w = csv.DictWriter(out, fieldnames=cab); w.writeheader()
        item = tema(); w.writerow({k: item.get(k, "") for k in cab})
        session.get.return_value = resposta(out.getvalue())
        m._baixar_csv(session, m.URL_TEMAS, m.COLUNAS_TEMAS)
        kwargs = session.get.call_args.kwargs
        self.assertNotIn("verify", kwargs)
        self.assertFalse(kwargs["allow_redirects"])
        with self.assertRaises(ValueError):
            m._url_oficial("https://example.org/temas.csv")

    def test_resposta_vazia_falso_200_e_redirecionada(self):
        for r in (
            resposta(""), resposta("<html>404 not found</html>"),
            resposta("x", status=202), resposta("x", url=m.URL_PROCESSOS),
        ):
            with self.assertRaises((ValueError, requests.HTTPError)):
                m._ler_csv_resposta(r, m.URL_TEMAS, m.COLUNAS_TEMAS)

    def test_alteracao_de_estrutura(self):
        with self.assertRaises(ValueError):
            m._ler_csv_resposta(resposta("numero;texto\n1;x\n"), m.URL_TEMAS, m.COLUNAS_TEMAS)

    def test_parsing_deduplica_enriquecimento_sem_aceitar_conflito(self):
        a = tema(); b = tema(); b["numeroRepercussaoGeralSTF"] = "123"
        itens = m._deduplicar_temas([a, b], validar_colecao=False)
        self.assertEqual((len(itens), itens[0]["numeroRepercussaoGeralSTF"]), (1, "123"))
        b = tema(); b["teseFirmada"] = "outra tese"
        with self.assertRaises(ValueError):
            m._deduplicar_temas([a, b], validar_colecao=False)

    def test_situacoes_cancelado_desafetado_e_sem_tese(self):
        cancelado = m._montar_oficial(tema(situacao="Cancelado"), [processo(desafetacao="Despacho oficial")])
        sem_tese = m._montar_oficial(tema(situacao="Sem Processo Vinculado"), [])
        self.assertEqual(cancelado["status"], "cancelado")
        self.assertTrue(cancelado["tema_desafetado"])
        self.assertFalse(cancelado["vigente_aplicavel"])
        self.assertEqual(sem_tese["status"], "sem_tese_aplicavel")
        self.assertTrue(sem_tese["sem_tese_aplicavel"])

    def test_desafetacao_incompativel_rejeitada(self):
        with self.assertRaises(ValueError):
            m._montar_oficial(tema(), [processo(desafetacao="Despacho oficial")])

    def test_relacao_cdc_exige_mencao_explicita(self):
        explicito = tema(texto="Prazo do art. 26 do Código de Defesa do Consumidor")
        implicito = tema(texto="Prazo do art. 26 para o consumidor")
        self.assertEqual(m._relacoes_explicitas(explicito), ["CDC art. 26"])
        self.assertEqual(m._relacoes_explicitas(implicito), [])

    def test_grafia_oficial_lei_n_8078_entra_na_triagem(self):
        item = tema(texto="Providência do art. 94 da Lei n.8.078/90")
        item["Assuntos"] = "DIREITO PROCESSUAL CIVIL"
        self.assertEqual(m._relacoes_explicitas(item), ["CDC art. 94"])
        self.assertTrue(m._eh_consumerista(item))


class CatalogoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent / "saida")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "catalogo.json"
        self.antigo = {
            "tribunal": "STJ", "tipo": "repetitivo", "numero": 1,
            "tema": "ID editorial preservado", "arquivo": "id_historico.txt",
            "pasta_destino": "19_JURISPRUDENCIA/STJ/REPETITIVOS",
            "texto": "texto histórico", "relacionado_a": ["CDC art. 7"],
            "fonte": "STJ", "status": "julgado",
        }
        self.path.write_text(json.dumps([self.antigo]), encoding="utf-8")
        self.temas = [tema(1), tema(2), tema(3, "Cancelado")]
        self.processos = {"101": [processo(1)], "102": [processo(2)], "103": [processo(3)]}

    def executar(self, outros=()):
        with patch.object(m, "_criar_session", return_value=Mock()), \
             patch.object(m, "_baixar_csv", side_effect=[self.temas, []]), \
             patch.object(m, "_deduplicar_temas", return_value=self.temas), \
             patch.object(m, "_agrupar_processos", return_value=self.processos):
            return m.atualizar_repetitivos_stj(self.path, False, outros)

    def test_preserva_id_relacao_historica_e_adiciona_novo(self):
        resultado = self.executar()
        self.assertTrue(resultado["ok"])
        dados = json.loads(self.path.read_text(encoding="utf-8"))
        velho = next(x for x in dados if x["numero"] == 1)
        self.assertEqual(velho["arquivo"], "id_historico.txt")
        self.assertEqual(velho["tema"], "ID editorial preservado")
        self.assertEqual(velho["relacionado_a"], ["CDC art. 7"])
        self.assertEqual((resultado["ja_existiam"], resultado["novos"]), (1, 1))

    def test_cancelado_nao_importado_como_vigente(self):
        self.assertTrue(self.executar()["ok"])
        dados = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertFalse(any(x.get("numero") == 3 for x in dados))

    def test_duplicacao_com_outra_categoria_preserva_catalogo(self):
        original = self.path.read_bytes()
        outro = {"tribunal": "STJ", "tipo": "acordao", "numero": "X", "url_fonte": m.URL_TEMA.format(numero=1)}
        self.assertFalse(self.executar([outro])["ok"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_subtipos_distintos_de_precedente_relevante_nao_colidem(self):
        outros = [
            {"tribunal": "STF", "tipo": "precedente_relevante", "subtipo": "adi", "numero": 1},
            {"tribunal": "STF", "tipo": "precedente_relevante", "subtipo": "adpf", "numero": 1},
        ]
        self.assertTrue(self.executar(outros)["ok"])

    def test_falha_parcial_preserva_catalogo(self):
        original = self.path.read_bytes()
        with patch.object(m, "_criar_session", return_value=Mock()), \
             patch.object(m, "_baixar_csv", side_effect=[self.temas, ValueError("fonte vazia")]):
            resultado = m.atualizar_repetitivos_stj(self.path, False)
        self.assertFalse(resultado["ok"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_catalogo_invalido_preservado(self):
        self.path.write_text("{}", encoding="utf-8")
        original = self.path.read_bytes()
        self.assertFalse(m.atualizar_repetitivos_stj(self.path, False)["ok"])
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
