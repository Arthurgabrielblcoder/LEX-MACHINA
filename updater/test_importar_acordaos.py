import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import importar_acordaos as m
import main


def item(id="1", processo="1234567", ementa="Aplicam-se o art. 14 do CDC ao fornecedor. " * 8):
    return {
        "id": id, "numeroProcesso": processo, "numeroRegistro": "202600000001",
        "siglaClasse": "REsp", "nomeOrgaoJulgador": "TERCEIRA TURMA",
        "ministroRelator": "MINISTRA TESTE", "dataPublicacao": "DJEN DATA:01/09/2026",
        "ementa": ementa, "tipoDeDecisao": "ACÓRDÃO", "dataDecisao": "20260831",
        "decisao": "Recurso provido.",
        "referenciasLegislativas": ["LEG:FED LEI:008078 ANO:1990\n ART:00014"],
    }


class ParsingTests(unittest.TestCase):
    def test_parsing_e_relacao_explicita(self):
        registro = m._registro(item(), ["CDC art. 14"], {"CDC art. 14": ["ART:00014"]}, "2026-09-16")
        self.assertEqual((registro["tipo"], registro["numero_processo"]), ("acordao", "REsp 1234567"))
        self.assertEqual(m._relacoes_cdc(item()), ["CDC art. 14"])

    def test_sem_inferencia_semantica(self):
        dado = item(ementa="Relação de consumo e responsabilidade civil. " * 8)
        dado["referenciasLegislativas"] = []
        self.assertEqual(m._relacoes_cdc(dado), [])

    def test_artigo_de_outra_lei_nao_vira_cdc(self):
        dado = item(ementa="Incide o CDC e o art. 489 do CPC. " * 10)
        dado["referenciasLegislativas"] = ["LEG:FED LEI:008078 ANO:1990"]
        self.assertEqual(m._relacoes_cdc(dado), [])

    def test_duplicacao_por_processo_e_decisao(self):
        self.assertEqual(m._chave(item()), m._chave(dict(item(), ementa="outro texto")))

    def test_selecao_deterministica_independe_da_ordem(self):
        entradas = []
        for i in range(30):
            dado = item(str(i + 1), str(2000000 + i))
            dado["dataDecisao"] = f"202608{(i % 28) + 1:02d}"
            dado["referenciasLegislativas"] = [
                f"LEG:FED LEI:008078 ANO:1990\n ART:{(i % 12) + 1:05d}"
            ]
            entradas.append((dado, m._relacoes_cdc(dado)))
        direta = [x[0]["id"] for x in m._selecionar_editorialmente(entradas)]
        inversa = [x[0]["id"] for x in m._selecionar_editorialmente(list(reversed(entradas)))]
        self.assertEqual(direta, inversa)
        self.assertEqual(len(direta), 20)

    def test_extracao_processos_qualificados(self):
        encontrados = m._processos_qualificados([{"processos": ["REsp 1.234.567"]}])
        self.assertIn("RESP1234567", encontrados)

    def test_resposta_vazia_e_estrutura_alterada(self):
        with self.assertRaises(ValueError):
            m._validar_colecao([], validar_volume=False)
        with self.assertRaises(ValueError):
            m._validar_colecao([{"id": "1"}], validar_volume=False)

    def test_falso_http_200(self):
        resposta = Mock()
        resposta.headers = {"Content-Type": "text/html"}
        resposta.raise_for_status.return_value = None
        session = Mock(); session.get.return_value = resposta
        with self.assertRaises(ValueError):
            m._get_json(session, "https://dadosabertos.web.stj.jus.br/falso")


class TransactionTests(unittest.TestCase):
    def test_indice_expoe_quantidade_da_categoria(self):
        with tempfile.TemporaryDirectory() as pasta:
            anterior = main.PASTA_SAIDA
            main.PASTA_SAIDA = Path(pasta)
            try:
                caminho = main.gerar_indice_relacoes_especializado([
                    dict(m._registro(item(), ["CDC art. 14"], {"CDC art. 14": ["ART:00014"]}, "2026-09-16"))
                ], "acordaos")
                self.assertTrue(caminho.read_text(encoding="utf-8").startswith("ACÓRDÃOS (1)\n"))
            finally:
                main.PASTA_SAIDA = anterior

    def test_preserva_catalogo_em_falha(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "catalogo.json"
            original = [{"tribunal": "STJ", "tipo": "acordao", "numero": "antigo"}]
            caminho.write_text(json.dumps(original), encoding="utf-8")
            with patch.object(m, "_criar_session", side_effect=RuntimeError("fonte indisponível")):
                resultado = m.atualizar_acordaos(caminho, verbose=False)
            self.assertFalse(resultado["ok"])
            self.assertEqual(json.loads(caminho.read_text(encoding="utf-8")), original)

    def test_exclusao_qualificado_e_limite(self):
        dados = [item(str(i), str(1234500 + i)) for i in range(105)]
        pacotes = [{"success": True, "result": {"resources": [
            {"name": m.DATA_AMOSTRA, "format": "JSON", "url": f"https://dadosabertos.web.stj.jus.br/{n}.json"}
        ]}} for n in range(3)]
        respostas = [*pacotes, dados, dados, dados]
        class Sessao:
            def get(self, *args, **kwargs):
                valor = respostas.pop(0)
                r = Mock(); r.headers = {"Content-Type": "application/json"}
                r.raise_for_status.return_value = None; r.json.return_value = valor
                return r
            def close(self): pass
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "catalogo.json"; caminho.write_text("[]", encoding="utf-8")
            with patch.object(m, "_criar_session", return_value=Sessao()):
                resultado = m.atualizar_acordaos(
                    caminho, verbose=False, registros_qualificados=[{"processos": ["REsp 1234500"]}],
                )
            self.assertTrue(resultado["ok"])
            self.assertEqual(resultado["excluidos_qualificados"], 1)
            self.assertEqual(resultado["importados"], m.LIMITE_IMPORTACAO)
            self.assertEqual(len(json.loads(caminho.read_text(encoding="utf-8"))), m.LIMITE_IMPORTACAO)


if __name__ == "__main__":
    unittest.main()
