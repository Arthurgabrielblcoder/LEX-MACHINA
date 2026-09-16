import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

import importar_precedentes_relevantes as m


def item(tipo="IAC", numero=1, situacao=None, texto="contrato de plano de saúde"):
    if situacao is None:
        situacao = "Trânsito em Julgado" if tipo == "IAC" else "Suspensão deferida"
    return {
        "sequencialPrecedente": str(100 + numero), "tipoPrecedente": tipo,
        "numeroPrecedente": str(numero), "dataPrimeiraAfetacao": "01/02/2020",
        "dataJulgamento": "02/03/2021", "dataPublicacaoAcordao": "03/04/2021",
        "situacao": situacao, "informacoesComplementares": "",
        "questaoSubmetidaAJulgamento": texto, "teseFirmada": texto,
        "anotacoesNUGEPNAC": "IRDR 2/TJDFT (0001)", "delimitacaoJulgado": "",
        "entendimentoAnterior": "", "referenciaLegislativa": "",
        "referenciaSumular": "", "sumulaOriginada": "", "audienciaPublica": "",
        "dataAudienciaPublica": "", "orgaoJulgador": "SEGUNDA SEÇÃO",
        "Assuntos": "DIREITO DO CONSUMIDOR", "numeroRepercussaoGeralSTF": "",
        "descricaoRepercussaoGeral": "",
    }


class ParsingTests(unittest.TestCase):
    def test_subtipos_e_situacoes(self):
        self.assertEqual(len(m._deduplicar([item()], "IAC", False)), 1)
        self.assertEqual(len(m._deduplicar([item("SIRDR")], "SIRDR", False)), 1)
        with self.assertRaises(ValueError):
            m._deduplicar([item(situacao="situação inventada")], "IAC", False)

    def test_duplicata_divergente(self):
        a = item(); b = item(); b["teseFirmada"] = "outra tese"
        with self.assertRaises(ValueError):
            m._deduplicar([a, b], "IAC", False)

    def test_relacao_explicita_sem_inferencia(self):
        explicito = item(texto="Aplicação do art. 26 do CDC")
        implicito = item(texto="Consumidor e artigo 26 do Código Civil")
        self.assertEqual(m._registro(explicito, [], "iac", "2026-09-16")["relacionado_a"], ["CDC art. 26"])
        self.assertEqual(m._registro(implicito, [], "iac", "2026-09-16")["relacionado_a"], [])

    def test_artigo_com_inciso_e_cdc_expresso(self):
        registro = m._registro(item(texto="Competência do art. 93, I e II, do CDC"), [], "iac", "2026-09-16")
        self.assertEqual(registro["relacionado_a"], ["CDC art. 93"])

    def test_origem_irdr_e_classe_sirdr(self):
        registro = m._registro(item("SIRDR"), [], "sirdr", "2026-09-16")
        self.assertEqual((registro["tipo"], registro["subtipo"], registro["classe"]),
                         ("precedente_relevante", "sirdr", "SIRDR"))
        self.assertEqual(registro["tribunais_origem_irdr"], ["TJDFT"])
        self.assertEqual(registro["numero_sirdr_stj"], 1)
        self.assertEqual(registro["identificacoes_irdr_origem"], ["2/TJDFT", "0001"])

    def test_classificacao_dos_seis_subtipos(self):
        for subtipo in ("adi", "adc", "adpf", "ado"):
            r = {"tipo": subtipo}
            m._consolidar_controle(r)
            self.assertEqual((r["tipo"], r["subtipo"]), ("precedente_relevante", subtipo))
        for subtipo in ("iac", "irdr", "sirdr"):
            m._consolidar_controle({"tipo": "precedente_relevante", "subtipo": subtipo})


class CatalogoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent / "saida")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "catalogo.json"
        self.adi = {
            "tribunal": "STF", "tipo": "adi", "numero": 1, "tema": "preservado",
            "arquivo": "adi_1.txt", "pasta_destino": "x", "texto": "texto",
            "relacionado_a": ["CDC art. 1"], "fonte": "STF", "url_fonte": "https://portal.stf.jus.br/adi1",
        }
        self.rg = {
            "tribunal": "STF", "tipo": "repercussao_geral", "numero": 2,
            "tema": "RG", "arquivo": "rg.txt", "pasta_destino": "x", "texto": "x",
            "relacionado_a": [], "fonte": "STF", "url_fonte": "https://portal.stf.jus.br/rg2",
        }
        self.path.write_text(json.dumps([self.adi, self.rg]), encoding="utf-8")
        self.iacs = [item("IAC", 1), item("IAC", 2, "Cancelado")]
        self.sirdrs = [item("SIRDR", 1), item("SIRDR", 2, "Vinculada a tema repetitivo")]

    def executar(self, outros=()):
        with patch.object(m, "_criar_session", return_value=Mock()), \
             patch.object(m, "_baixar_csv", side_effect=[self.iacs + self.sirdrs, []]), \
             patch.object(m, "_deduplicar", side_effect=[self.iacs, self.sirdrs]), \
             patch.object(m, "_agrupar_processos", return_value={}):
            return m.atualizar_precedentes_relevantes(self.path, False, outros)

    def test_preserva_controle_e_outras_categorias(self):
        resultado = self.executar()
        self.assertTrue(resultado["ok"])
        dados = json.loads(self.path.read_text(encoding="utf-8"))
        adi = next(x for x in dados if x.get("subtipo") == "adi")
        self.assertEqual((adi["tema"], adi["arquivo"], adi["relacionado_a"]),
                         ("preservado", "adi_1.txt", ["CDC art. 1"]))
        self.assertTrue(any(x["tipo"] == "repercussao_geral" for x in dados))

    def test_cancelado_e_vinculado_repetitivo_nao_importados(self):
        self.assertTrue(self.executar()["ok"])
        dados = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(sum(x.get("subtipo") == "iac" for x in dados), 1)
        self.assertEqual(sum(x.get("subtipo") == "sirdr" for x in dados), 1)

    def test_duplicacao_entre_categorias_preserva(self):
        original = self.path.read_bytes()
        url = m._registro(self.iacs[0], [], "iac", "2026-09-16")["url_fonte"]
        outro = {"tribunal": "STJ", "tipo": "acordao", "numero": 9, "url_fonte": url}
        self.assertFalse(self.executar([outro])["ok"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_falha_parcial_preserva_bytes(self):
        original = self.path.read_bytes()
        with patch.object(m, "_criar_session", return_value=Mock()), \
             patch.object(m, "_baixar_csv", side_effect=requests.exceptions.SSLError("TLS")):
            self.assertFalse(m.atualizar_precedentes_relevantes(self.path, False)["ok"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_resposta_vazia_ou_estrutura_alterada_preserva(self):
        original = self.path.read_bytes()
        for erro in (ValueError("CSV vazio"), ValueError("estrutura alterada")):
            with patch.object(m, "_criar_session", return_value=Mock()), \
                 patch.object(m, "_baixar_csv", side_effect=erro):
                self.assertFalse(m.atualizar_precedentes_relevantes(self.path, False)["ok"])
            self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
