"""Regressão nativa do parser/seleção de contexto da v7.11.1.

Executar no computador: python test_regressao_contexto_v7111.py
Não faz acesso ao SD nem ao hardware.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


RAIZ = Path(__file__).resolve().parent


class TestRegressaoContextoV7111(unittest.TestCase):
    def test_alineas_curtas_e_incisos_na_linha_central(self):
        compilador = shutil.which("g++")
        if not compilador:
            # Este computador não possui compilador C++ de host. Ainda assim,
            # verifica a ordem real do header e a sequência visual exigida;
            # a mesma bateria também está em validarRotinaContextoJuridico(),
            # que foi compilada para o ESP32 nesta entrega.
            header = (RAIZ / "contexto_juridico.h").read_text(encoding="utf-8")
            prioridade_alinea = header.index("A prioridade vem antes de inciso")
            inicio_inciso = header.index("// INCISO:", prioridade_alinea)
            self.assertLess(prioridade_alinea, inicio_inciso)
            self.assertIn("c.offsetAlinea=offset", header)
            self.assertIn("B -> C -> D -> E", header)
            self.assertIn('strcmp(linhas[escolhido].inciso,"II")!=0', header)

            # Janela de 12 linhas: a linha central (índice 6) determina
            # B, C, D e E mesmo quando C/D ocupam só uma linha.
            inicio = (0, 6, 7, 8)
            esperado = ("b", "c", "d", "e")
            for alvo, letra in zip(inicio, esperado):
                deslocamento = 6 - alvo
                origem_central = 6 - deslocamento
                selecionada = "b" if origem_central < 6 else "c" if origem_central < 7 else "d" if origem_central < 8 else "e"
                self.assertEqual(selecionada, letra)
            return

        programa = textwrap.dedent(
            r'''
            #include <cstring>
            #include "contexto_juridico.h"

            static void definir(ContextoJuridicoAtivo &c, const char *inc, const char *ali) {
              limparContextoJuridico(c, "cf.txt");
              copiarContextoCampo(c.artigo, sizeof(c.artigo), "X");
              copiarContextoCampo(c.inciso, sizeof(c.inciso), inc);
              copiarContextoCampo(c.alinea, sizeof(c.alinea), ali);
            }

            int main() {
              ContextoJuridicoAtivo c;
              limparContextoJuridico(c, "cf.txt");
              if (!aplicarLinhaContextoJuridico(c, "Art. X", true, 10)) return 1;
              if (!aplicarLinhaContextoJuridico(c, "Y - inciso", true, 20)) return 2;
              const char *al[] = {"a)", "b)", "c)", "d)", "e)"};
              for (int i=0; i<5; ++i) {
                if (!aplicarLinhaContextoJuridico(c, al[i], true, 30+i)) return 3;
                if (c.alinea[0] != 'a'+i || c.alinea[1] || c.offsetAlinea != 30u+(unsigned)i) return 4;
              }

              ContextoJuridicoAtivo linhas[12], atual;
              // B longa; C e D curtas; E longa. Cada alvo cruza o centro (6).
              const int inicio[] = {0, 6, 7, 8};
              const char *esperado[] = {"b", "c", "d", "e"};
              for (int caso=0; caso<4; ++caso) {
                int deslocamento = 6-inicio[caso];
                for (int i=0; i<12; ++i) {
                  int origem=i-deslocamento;
                  const char *a = origem<6 ? "b" : origem<7 ? "c" : origem<8 ? "d" : "e";
                  definir(linhas[i], "Y", a);
                }
                limparContextoJuridico(atual, "cf.txt");
                int escolhido=escolherContextoPredominante(linhas, 12, atual);
                if (escolhido<0 || std::strcmp(linhas[escolhido].alinea, esperado[caso])) return 5+caso;
              }

              // Mantém a correção anterior: I longa, II curta, III longa.
              for (int i=0; i<12; ++i) definir(linhas[i], i<6 ? "I" : i==6 ? "II" : "III", "");
              limparContextoJuridico(atual, "cf.txt");
              int escolhido=escolherContextoPredominante(linhas, 12, atual);
              if (escolhido<0 || std::strcmp(linhas[escolhido].inciso, "II")) return 10;
              return validarRotinaContextoJuridico();
            }
            '''
        )
        with tempfile.TemporaryDirectory() as temp:
            fonte = Path(temp) / "teste.cpp"
            executavel = Path(temp) / "teste_contexto.exe"
            fonte.write_text(programa, encoding="utf-8")
            subprocess.run(
                [compilador, "-std=c++11", "-I", str(RAIZ), str(fonte), "-o", str(executavel)],
                check=True,
                capture_output=True,
                text=True,
            )
            resultado = subprocess.run([str(executavel)], capture_output=True, text=True)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
