import tempfile
import unittest
import json
from pathlib import Path

import implantar_sd as deploy


class ImplantarSDTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        self.saida = self.raiz / "saida"
        self.cartao = self.raiz / "cartao"
        self.cdc = self.cartao / deploy.PASTA_CDC
        (self.saida / "19_JURISPRUDENCIA/STJ/SUMULAS").mkdir(parents=True)
        (self.saida / "99_INDICES").mkdir(parents=True)
        (self.saida / "99_RELATIONS_V1/01_SUMULAS").mkdir(parents=True)
        (self.cdc / "01_CDC").mkdir(parents=True)
        (self.cartao / "1- CONSTITUIÇÃO FEDERAL").mkdir(parents=True)
        (self.cdc / "01_CDC/cdc.txt").write_text("Art. 1º Lei", encoding="utf-8")

        sumula = self.saida / "19_JURISPRUDENCIA/STJ/SUMULAS/stj_sumula_1.txt"
        sumula.write_text("Súmula oficial", encoding="utf-8")
        registro = [{
            "tipo": "sumula", "tribunal": "STJ", "numero": "1",
            "arquivo": sumula.name,
            "pasta_destino": "19_JURISPRUDENCIA/STJ/SUMULAS",
        }]
        (self.raiz / "catalogo_jurisprudencia.json").write_text(
            json.dumps(registro), encoding="utf-8"
        )
        (self.raiz / "catalogo_precedentes.json").write_text("[]", encoding="utf-8")
        (self.raiz / "catalogo_acordaos.json").write_text("[]", encoding="utf-8")
        (self.saida / deploy.INDICE_JURIS).write_text(
            "CDC art. 1|STJ|sumula|1|vigente|stj_sumula_1.txt\n",
            encoding="utf-8",
        )
        (self.saida / "99_RELATIONS_V1/01_SUMULAS/INDICE_SUMULAS.txt").write_text(
            "STJ|1|vigente|stj_sumula_1.txt|19_JURISPRUDENCIA/STJ/SUMULAS\n",
            encoding="utf-8",
        )
        correlatas = self.cartao / deploy.INDICE_CORRELATAS
        correlatas.parent.mkdir(parents=True)
        (self.cartao / "2- CÓDIGO CIVIL").mkdir()
        (self.cartao / "2- CÓDIGO CIVIL/cc.txt").write_text("Art. 1º", encoding="utf-8")
        correlatas.write_text(
            "CDC art. 1|Código Civil|1|/2- CÓDIGO CIVIL\n", encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_plano_contem_apenas_artefatos_permitidos(self):
        lixo = self.saida / "cache.json"
        lixo.write_text("{}", encoding="utf-8")
        plano = deploy.montar_plano(self.saida, self.cartao, self.raiz)
        relativos = {item.relativo_cartao.as_posix() for item in plano}
        self.assertIn(
            f"{deploy.PASTA_CDC}/19_JURISPRUDENCIA/STJ/SUMULAS/stj_sumula_1.txt",
            relativos,
        )
        self.assertFalse(any("cache.json" in item for item in relativos))
        self.assertFalse(any("01_CDC/cdc.txt" in item for item in relativos))

    def test_validacao_aceita_cartao_lex_em_diretorio_de_teste(self):
        validado = deploy.validar_destino(self.cartao, exigir_removivel=False)
        self.assertEqual(validado, self.cartao.resolve())

    def test_validacao_rejeita_estrutura_sem_leis(self):
        vazio = self.raiz / "vazio"
        (vazio / deploy.PASTA_CDC).mkdir(parents=True)
        with self.assertRaises(deploy.ErroImplantacao):
            deploy.validar_destino(vazio, exigir_removivel=False)

    def test_backup_e_copia_atomica_preservam_lei(self):
        plano = deploy.montar_plano(self.saida, self.cartao, self.raiz)
        destino = self.cdc / "19_JURISPRUDENCIA/STJ/SUMULAS/stj_sumula_1.txt"
        destino.parent.mkdir(parents=True)
        destino.write_text("versão anterior", encoding="utf-8")
        lei_antes = (self.cdc / "01_CDC/cdc.txt").read_bytes()

        alterados, _, backup = deploy.executar(plano, self.raiz / "backup")

        self.assertGreater(alterados, 0)
        self.assertEqual(destino.read_text(encoding="utf-8"), "Súmula oficial")
        self.assertEqual((self.cdc / "01_CDC/cdc.txt").read_bytes(), lei_antes)
        self.assertTrue((backup / destino.relative_to(self.cartao)).is_file())
        self.assertFalse(any(self.cartao.rglob("*.lex-novo")))

    def test_validacao_detecta_referencia_ausente(self):
        plano = deploy.montar_plano(self.saida, self.cartao, self.raiz)
        indice = self.saida / deploy.INDICE_JURIS
        indice.write_text(
            "CDC art. 1|STJ|sumula|99|vigente|arquivo_inexistente.txt\n",
            encoding="utf-8",
        )
        erros = deploy.validar_referencias(self.cartao, plano=plano)
        self.assertTrue(any("arquivo_inexistente.txt" in erro for erro in erros))

    def test_indice_correlatas_e_obrigatorio(self):
        (self.cartao / deploy.INDICE_CORRELATAS).unlink()
        erros = deploy.validar_referencias(
            self.cartao, plano=deploy.montar_plano(self.saida, self.cartao, self.raiz)
        )
        self.assertTrue(any("correlatas ausente" in erro.lower() for erro in erros))

    def test_txt_orfao_nao_entra_no_plano(self):
        orfao = self.saida / "19_JURISPRUDENCIA/STJ/SUMULAS/stj_sumula_999.txt"
        orfao.write_text("resíduo", encoding="utf-8")
        catalogados, orfaos = deploy.auditar_orfaos(self.saida.resolve(), self.raiz)
        plano = deploy.montar_plano(self.saida, self.cartao, self.raiz)
        self.assertEqual(len(catalogados), 1)
        self.assertIn(orfao.resolve(), orfaos)
        self.assertFalse(any(item.origem == orfao.resolve() for item in plano))

    def test_catalogo_com_arquivo_ausente_bloqueia_plano(self):
        dados = json.loads((self.raiz / "catalogo_jurisprudencia.json").read_text())
        dados[0]["arquivo"] = "ausente.txt"
        (self.raiz / "catalogo_jurisprudencia.json").write_text(json.dumps(dados))
        with self.assertRaises(deploy.ErroImplantacao):
            deploy.montar_plano(self.saida, self.cartao, self.raiz)


if __name__ == "__main__":
    unittest.main()
