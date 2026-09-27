from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SCRIPT = BASE / "adaptar_catalogo_69.py"
GENERATED = [
    "AUDITORIA_ESQUEMAS_24_45.json",
    "CATALOGO_69_CANONICO.json",
    "CATALOGO_69_INPUT_ENGINE_V132.json",
    "RASTREABILIDADE_ADAPTACAO_69.json",
    "CATALOGO_24_INPUT_ENGINE_V132_ADAPTADO.json",
    "RELATORIO_ADAPTADOR_CATALOGO_69.md",
]

def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT)], check=True)

    def test_canonical_69_unique(self):
        data=load("CATALOGO_69_CANONICO.json"); works=data["obras"]
        self.assertEqual(69,len(works)); self.assertEqual(69,len({x["id"] for x in works}))
        self.assertTrue(all(x["schema"]=="REFERENCIA_CANONICA_V1" for x in works))

    def test_sources_24_45(self):
        works=load("CATALOGO_69_CANONICO.json")["obras"]
        self.assertEqual(24,sum(x["origem_catalogo"]=="CATALOGO_24_ORIGINAL" for x in works))
        self.assertEqual(45,sum(x["origem_catalogo"]=="LOTE_45_V2_APROVADO" for x in works))

    def test_homonym(self):
        works=load("CATALOGO_69_CANONICO.json")["obras"]
        rows=[x for x in works if x["titulo"].casefold()=="o processo"]
        self.assertEqual({("REF-LIV-0002","LIVRO",1925),("EXP-DOC-005","DOCUMENTÁRIO",2018)},
                         {(x["id"],x["tipo"],x["ano"]) for x in rows})

    def test_reversible_and_no_loss_new(self):
        trace=load("RASTREABILIDADE_ADAPTACAO_69.json")["registros"]
        self.assertTrue(all(x["reversivel_por_registro_origem_integral"] for x in trace))
        source=json.loads((ROOT/"LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2/DNA_SEMANTICO_45_APROVADO.json").read_text(encoding="utf-8"))["obras"]
        canonical=load("CATALOGO_69_CANONICO.json")["obras"][24:]
        self.assertEqual(source,[x["registro_origem_integral"] for x in canonical])

    def test_no_invention_old(self):
        source=json.loads((ROOT/"LEX_MACHINA_REFERENCIAS_ENGINE_V1_2/data/CATALOGO_SEMANTICO_OBRAS.json").read_text(encoding="utf-8"))["obras"]
        canonical=load("CATALOGO_69_CANONICO.json")["obras"][:24]
        self.assertEqual(source,[x["registro_origem_integral"] for x in canonical])
        self.assertTrue(all(not x["temas_centrais"] and not x["temas_fortes"] and not x["temas_secundarios"] for x in canonical))

    def test_locks_preserved(self):
        source=json.loads((ROOT/"LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2/DNA_SEMANTICO_45_APROVADO.json").read_text(encoding="utf-8"))["obras"]
        canonical=load("CATALOGO_69_CANONICO.json")["obras"][24:]
        self.assertEqual([x["travas_editoriais"] for x in source],[x["travas_editoriais"] for x in canonical])
        self.assertEqual([x["alertas_editoriais"] for x in source],[x["alertas_editoriais"] for x in canonical])

    def test_engine_contract_block_is_explicit(self):
        data=load("CATALOGO_69_INPUT_ENGINE_V132.json")
        self.assertFalse(data["engine_executavel"]); self.assertFalse(data["engine_executada"])
        self.assertEqual(24,data["total_compativel_sem_inferencia"]); self.assertEqual(45,data["total_bloqueado"])
        self.assertTrue(all(x["valor_pedagogico"] is None for x in data["obras_novas_mapeadas_bloqueadas"]))

    def test_retrocompatibility_byte_for_byte(self):
        original=ROOT/"LEX_MACHINA_REFERENCIAS_ENGINE_V1_2/data/CATALOGO_SEMANTICO_OBRAS.json"
        adapted=BASE/"CATALOGO_24_INPUT_ENGINE_V132_ADAPTADO.json"
        self.assertEqual(original.read_bytes(),adapted.read_bytes())

    def test_determinism(self):
        before={name:digest(BASE/name) for name in GENERATED}
        subprocess.run([sys.executable,"-X","utf8",str(SCRIPT)],check=True)
        after={name:digest(BASE/name) for name in GENERATED}
        self.assertEqual(before,after)

    def test_protected_hashes(self):
        self.assertEqual("54f152214dbf127b284067609a5570bf4e8fe241a71afbced66ba059c7d52766",digest(ROOT/"LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2/BENCHMARK_HUMANO_REFERENCIAS_CF_TOTAL.json"))
        self.assertEqual("745d367dae70c8959378f5d6e557d6fb220f3ce9a4f4e06bce4bb337bbb61a14",digest(ROOT/"CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json"))
        self.assertEqual("48189658c9bd850895d043ba3489158744a3ec6c9754b8bd1559c19942b35d47",digest(ROOT/"LEX_MACHINA_REFERENCIAS_ENGINE_V1_2/data/CATALOGO_SEMANTICO_OBRAS.json"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
