# C3B.1 — diff das flags do `CF88_TARGETS.IDX`

- **Resumo:** só a posição C muda; 8 targets ganham C e 23 perdem C.
- **Prova de isolamento** (`C3B1_FILE_DIFF.json`): ENTENDA, JURIS, WORK_REFERENCE, R, X e demais campos = 0 mudanças.

| Target | Antes | Depois | Mudança |
|---|---|---|---|
| `CF88:ART.146:INC.III:AL.b` | `--J-R-` | `-CJ-R-` | GAINED_C |
| `CF88:ART.155:PAR.2:INC.VII` | `E----X` | `EC---X` | GAINED_C |
| `CF88:ART.158:PAR.1:INC.I` | `------` | `-C----` | GAINED_C |
| `CF88:ART.195:INC.I:AL.b` | `------` | `-C----` | GAINED_C |
| `CF88:ART.202:PAR.1` | `------` | `-C----` | GAINED_C |
| `CF88:ART.214:CAPUT` | `------` | `-C----` | GAINED_C |
| `CF88:ART.239:PAR.3` | `E----X` | `EC---X` | GAINED_C |
| `CF88:ART.239:PAR.4` | `------` | `-C----` | GAINED_C |
| `CF88:ART.146` | `EC--RX` | `E---RX` | LOST_C |
| `CF88:ART.155:PAR.1:INC.III` | `-CJ-R-` | `--J-R-` | LOST_C |
| `CF88:ART.158:PAR.1:INC.II` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.195:INC.I` | `ECJ-R-` | `E-J-R-` | LOST_C |
| `CF88:ART.195:INC.II` | `-CJ-R-` | `--J-R-` | LOST_C |
| `CF88:ART.195:PAR.1` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.195:PAR.2` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.201:INC.I` | `-C-WR-` | `---WR-` | LOST_C |
| `CF88:ART.201:INC.II` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.201:INC.IV` | `-CJ-R-` | `--J-R-` | LOST_C |
| `CF88:ART.201:INC.V` | `-CJ-R-` | `--J-R-` | LOST_C |
| `CF88:ART.20:PAR.1` | `EC--RX` | `E---RX` | LOST_C |
| `CF88:ART.214:INC.I` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.214:INC.II` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.214:INC.III` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.214:INC.IV` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.214:INC.V` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.214:INC.VI` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.37:INC.II` | `ECJ-RX` | `E-J-RX` | LOST_C |
| `CF88:ART.37:PAR.3:INC.II` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.37:PAR.3:INC.III` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.43:PAR.1:INC.I` | `-C--R-` | `----R-` | LOST_C |
| `CF88:ART.43:PAR.1:INC.II` | `-C--R-` | `----R-` | LOST_C |

