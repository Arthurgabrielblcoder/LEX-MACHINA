"""Regressões de capacidade e preservação da v7.12.0 (sem hardware/SD real)."""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
INO = BASE / "LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA.ino"
J4 = ROOT / "LEX_MACHINA_JURIS_CF_J4"
V7111 = ROOT / "firmware" / "LEX_MACHINA_v7.11.1_JURIS_CF_PILOTO"


def simular_loader(lookup: bytes, juris: bytes, limite=4096) -> tuple[int, int]:
    linhas = [x for x in lookup.decode("utf-8").splitlines() if x and not x.startswith("#")]
    if not linhas or len(linhas) > limite:
        raise ValueError("quantidade inválida")
    registros = juris.splitlines()
    if not registros or not registros[0].startswith(b"#ID|"):
        raise ValueError("índice inválido")
    bruto = juris
    total = 0
    for linha in linhas:
        campos = linha.split("|")
        if len(campos) != 7 or not campos[0] or not campos[1]:
            raise ValueError("schema inválido")
        offset, quantidade = int(campos[5]), int(campos[6])
        if quantidade < 1 or quantidade > 255 or offset >= len(juris):
            raise ValueError("offset/quantidade inválido")
        if offset and bruto[offset - 1] != ord("\n"):
            raise ValueError("offset desalinhado")
        cursor = offset
        for _ in range(quantidade):
            fim = bruto.find(b"\n", cursor)
            if fim < 0:
                raise ValueError("quantidade ultrapassa índice")
            cursor = fim + 1
        total += quantidade
    if total != len(registros) - 1:
        raise ValueError("total inconsistente")
    return len(linhas), total


def fabricar(n: int) -> tuple[bytes, bytes]:
    juris = "#ID|TIPO|TRIBUNAL|NUMERO|STATUS|TITULO_CURTO|IDENTIFICADOR|FONTE\n"
    lookup = ["#ORIGEM_NORMA|ARTIGO|PARAGRAFO|INCISO|ALINEA|OFFSET|QUANTIDADE"]
    for i in range(n):
        offset = len(juris.encode("utf-8"))
        juris += f"STF:RG:{i}|repercussao_geral|STF|{i}|tese_fixada|Tema {i}|STF:RG:{i}|https://portal.stf.jus.br\n"
        lookup.append(f"CF88|{i + 1}||||{offset}|1")
    return ("\n".join(lookup) + "\n").encode(), juris.encode()


class CapacidadeJurisV7120Test(unittest.TestCase):
    def test_01_zero_rejeitado(self):
        with self.assertRaises(ValueError): simular_loader(*fabricar(0))
    def test_02_um(self): self.assertEqual(simular_loader(*fabricar(1)), (1, 1))
    def test_03_sessenta_e_quatro(self): self.assertEqual(simular_loader(*fabricar(64)), (64, 64))
    def test_04_sessenta_e_cinco_sem_corte(self): self.assertEqual(simular_loader(*fabricar(65)), (65, 65))
    def test_05_cento_e_setenta_e_oito(self): self.assertEqual(simular_loader(*fabricar(178)), (178, 178))
    def test_06_duzentos_e_cinquenta_e_seis(self): self.assertEqual(simular_loader(*fabricar(256)), (256, 256))

    def test_07_indices_j4_integrais(self):
        self.assertEqual(simular_loader((J4 / "JUR_LOOKUP.IDX").read_bytes(), (J4 / "JURISPRUDENCIA.IDX").read_bytes()), (178, 296))

    def test_08_corrupcoes_rejeitadas(self):
        lookup, juris = fabricar(2)
        with self.assertRaises(ValueError): simular_loader(lookup.replace(b"|1\n", b"|999\n", 1), juris)
        with self.assertRaises(ValueError): simular_loader(lookup.replace(b"|1\n", b"|0\n", 1), juris)

    def test_09_firmware_dinamico_e_sem_64(self):
        fonte = INO.read_text(encoding="utf-8")
        self.assertNotIn("MAX_JUR_LOOKUP_CF", fonte)
        self.assertIn("quantidadeLookups", fonte)
        self.assertIn("MALLOC_CAP_SPIRAM", fonte)
        self.assertIn("local=PSRAM", fonte)
        self.assertIn("fonte=CACHE", fonte)
        self.assertIn("quantidade total inconsistente", fonte)

    def test_10_contexto_e_assets_preservados(self):
        for relativo in ("contexto_juridico.h", "assets/lex_boot_screen.h", "assets/lex_boot_screen_preview.png"):
            self.assertEqual(hashlib.sha256((BASE / relativo).read_bytes()).digest(), hashlib.sha256((V7111 / relativo).read_bytes()).digest(), relativo)

    def test_11_indices_j4_nao_alterados(self):
        self.assertEqual(hashlib.sha256((J4 / "JUR_LOOKUP.IDX").read_bytes()).hexdigest(), "7931e28e7a0592e2bd1a1872ee0904149eac50365c1c98990370a1235c618956")
        self.assertEqual(hashlib.sha256((J4 / "JURISPRUDENCIA.IDX").read_bytes()).hexdigest(), "f85108baf4ee296a7672e11733d63a32be60882d60364063a5a466e7a982b6f1")

    def test_12_fluxos_preservados(self):
        fonte = INO.read_text(encoding="utf-8")
        for trecho in ("buscarMelhorLookupJurisCF", "carregarCacheRelationsV2", "abrirRelacaoSelecionada", "TELA_JURIS_CATEGORIAS", "visualizandoReferencia", "SD-FALLBACK"):
            self.assertIn(trecho, fonte)


if __name__ == "__main__":
    unittest.main(verbosity=2)
