import json
import tempfile
import unittest
from pathlib import Path

from relations_v2 import preparar_estrutura


class RelationsV2InfraTest(unittest.TestCase):
    def test_catalogo_minimo_e_estrutura(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            catalogo = raiz / "catalogo.json"
            saida = raiz / "saida"
            itens = []
            for i in range(72):
                identificador = "CF88" if i == 0 else ("CDC1990" if i == 1 else ("CPC2015" if i == 2 else f"N{i:02d}"))
                itens.append({
                    "id": identificador,
                    "ramo": "TESTE",
                    "nome": f"Norma {i}",
                    "prioridade": "TESTE",
                    "tipo": "lei",
                    "fonte_oficial": "https://example.invalid/",
                    "pasta_destino": f"Pasta {i}",
                    "arquivo_sugerido": f"n{i}.txt",
                })
            catalogo.write_text(json.dumps({"versao":"teste","itens":itens}), encoding="utf-8")
            auditoria = preparar_estrutura(catalogo, saida)
            self.assertEqual(auditoria["status"], "OK")
            self.assertTrue((saida / "99_RELATIONS_V2" / "99_AUDITORIA" / "AUDITORIA_INFRAESTRUTURA.json").exists())
            self.assertTrue((saida / "99_RELATIONS_V2" / "04_FONTES" / "CATALOGO_NORMAS_GLOBAL.json").exists())


if __name__ == "__main__":
    unittest.main()
