"""PÓS-NOTURNA Parte F — HOST-ONLY generalized jurisprudence-type firmware prototype. NEVER flashes, NEVER modifies firmware/.

Base = firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE as committed (Parte D: rebuilds the approved app 6e329c91… up to build metadata).
Patch (exact anchors, fail closed; CRLF as in the .ino):
  1. enum JTIPO_CLASSE (one generic value for every processual class; no enum growth per class)
  2. table CLASSES_JURIS {tipo, rótulo} + rotuloClasseJuris(): HC, RHC, MS, RMS, AP, AI, Inq, Rcl, MI, Pet, ADO, RE, ARE, Ext
  3. classificarTipoJurisprudencia: class table -> JTIPO_CLASSE
  4. label: JTIPO_CLASSE -> "<rótulo> <n>"; súmula comum -> "Súmula <n> <TRIBUNAL>" (never "SUMULA STF" for TSE/STJ)
  5. counters: JTIPO_CLASSE counted with the acórdãos
  6. ID acceptance: "STF:" prefix -> whitelist TRIBUNAIS {STF,STJ,TSE,TST,STM} AND prefix == TRIBUNAL column
  7. opened-ficha title: súmula label already carries the tribunal (no "TSE Súmula 9 TSE")
Legacy rows (all STF; repercussao_geral / sumula_vinculante / adi) keep identical labels, ids and fichas.
Sketches/binaries: DEVICE_INTEGRATION/_tmp_fw_types/, DEVICE_INTEGRATION/backups/juris_type_prototype/ (gitignored).
Writes JURIS_TYPE_PROTOTYPE_BUILD.json + juris_types.patch.   Usage: python build_juris_type_prototype.py
"""
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
import juris_types as JT  # noqa: E402

SRC = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
HEADER_SHA_LF = 'e420f4dec7923036448b4cf1129c6092a9489b8c36c8cef4921a5d534b6f55f8'
APPROVED_BIN = ROOT / 'DEVICE_INTEGRATION/backups/references4_r1/build_cand/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin'
APPROVED_SHA = '6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c'
HC_JSON = HERE.parent / 'HC_FIRMWARE_PROTOTYPE/HC_PROTOTYPE_BUILD.json'
TMP = ROOT / 'DEVICE_INTEGRATION/_tmp_fw_types'
BK = ROOT / 'DEVICE_INTEGRATION/backups/juris_type_prototype'
INO = 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
FQBN = 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default'
FLAGS = 'compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1'
APP_PARTITION = 1310720
AC = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe'
E = '\r\n'
TABLE = ','.join('{"%s","%s"}' % kv for kv in JT.CLASSES)
TRIBS = ','.join(f'"{t}"' for t in JT.TRIBUNAIS)
PATCH = [  # (anchor, replacement); every anchor must occur exactly once
    ('  JTIPO_ACORDAO, JTIPO_OUTRO' + E, '  JTIPO_ACORDAO, JTIPO_CLASSE, JTIPO_OUTRO' + E),
    ('TipoJurisprudencia classificarTipoJurisprudencia(String tipo)' + E + '{' + E,
     '// Classes processuais (tribunal separado da classe): TIPO minusculo do IDX -> rotulo. Nova classe = nova linha, sem novo enum.' + E +
     'struct ClasseJurisRotulo { const char *tipo; const char *rotulo; };' + E +
     'static const ClasseJurisRotulo CLASSES_JURIS[]={' + TABLE + '};' + E +
     'static const char *rotuloClasseJuris(const String &tipoMinusculo)' + E + '{' + E +
     '  for(size_t i=0;i<sizeof(CLASSES_JURIS)/sizeof(CLASSES_JURIS[0]);i++)' + E +
     '    if(tipoMinusculo==CLASSES_JURIS[i].tipo) return CLASSES_JURIS[i].rotulo;' + E +
     '  return nullptr;' + E + '}' + E + E +
     'TipoJurisprudencia classificarTipoJurisprudencia(String tipo)' + E + '{' + E),
    ('  if(tipo=="acordao") return JTIPO_ACORDAO;' + E,
     '  if(tipo=="acordao") return JTIPO_ACORDAO;' + E + '  if(rotuloClasseJuris(tipo)) return JTIPO_CLASSE;' + E),
    ('    case JTIPO_SUMULA_STF: return "SUMULA STF "+r.numero;' + E,
     '    case JTIPO_SUMULA_STF: return "Súmula "+r.numero+(r.tribunal.length()?" "+r.tribunal:String(""));   // súmula comum de QUALQUER tribunal' + E),
    ('    case JTIPO_ACORDAO: return "ACORDAO "+r.numero;' + E,
     '    case JTIPO_ACORDAO: return "ACORDAO "+r.numero;' + E +
     '    case JTIPO_CLASSE: { String t=r.tipo; t.toLowerCase(); return String(rotuloClasseJuris(t))+" "+r.numero; }' + E),
    ('    case JTIPO_ADPF: totalAcordaosArtigo++; break;' + E, '    case JTIPO_ADPF:' + E + '    case JTIPO_CLASSE: totalAcordaosArtigo++; break;' + E),
    ('bool adicionarLinhaJurisCF(String linha,' + E,
     '// ID = TRIBUNAL:CLASSE:NUMERO:...: o tribunal do ID deve estar na lista e ser o da coluna TRIBUNAL (fail closed). Legado STF inalterado.' + E +
     'static bool tribunalJurisSuportado(const String &id, const String &tribunal)' + E + '{' + E +
     '  static const char *TRIBUNAIS[]={' + TRIBS + '};' + E +
     '  for(size_t i=0;i<sizeof(TRIBUNAIS)/sizeof(TRIBUNAIS[0]);i++)' + E +
     '    if(tribunal==TRIBUNAIS[i] && id.startsWith(String(TRIBUNAIS[i])+":")) return true;' + E +
     '  return false;' + E + '}' + E + E + 'bool adicionarLinhaJurisCF(String linha,' + E),
    ('  if(!classe.startsWith("STF:") || tipo.length()==0 || identificador.length()==0)' + E,
     '  if(!tribunalJurisSuportado(classe,tribunal) || tipo.length()==0 || identificador.length()==0)' + E),
    ('  nomeArquivoAtual=r.tribunal+" "+rotuloTipoJurisprudencia(r);' + E,
     '  nomeArquivoAtual=(classificarTipoJurisprudencia(r.tipo)==JTIPO_SUMULA_STF)?rotuloTipoJurisprudencia(r)' + E +
     '                   :r.tribunal+" "+rotuloTipoJurisprudencia(r);' + E),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def assemble(dest):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SRC, dest / SRC.name)
    return dest / SRC.name


def compile_sketch(sketch, out):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    r = subprocess.run([str(AC), 'compile', '--fqbn', FQBN, '--build-property', FLAGS, '--output-dir', str(out), str(sketch)],
                       capture_output=True, text=True)
    (out.parent / f'compile_{out.name}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    if r.returncode != 0:
        raise SystemExit(f'COMPILE_FAILED {out.name}')
    prog = int(re.search(r'Sketch uses (\d+) bytes', r.stdout).group(1))
    ram = int(re.search(r'Global variables use (\d+) bytes', r.stdout).group(1))
    b = (out / f'{INO}.bin').read_bytes()
    return dict(program_bytes=prog, static_ram_bytes=ram, app_bin_bytes=len(b), app_sha256=sha(b), app_partition_bytes=APP_PARTITION,
                app_partition_free=APP_PARTITION - len(b)), b


def metadata_only_diff(a, b):
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    banner = a.find(b'Software Info:\n\x00')
    ok = [(0xb0, 0xd0), (banner + 15, banner + 15 + 21), (len(a) - 33, len(a))]
    return len(a) == len(b) and all(any(lo <= i < hi for lo, hi in ok) for i in diff), len(diff)


def patched_text():
    text = (SRC / INO).read_bytes().decode('utf-8')
    for anchor, repl in PATCH:
        if text.count(anchor) != 1:
            raise SystemExit(f'ANCHOR_NOT_UNIQUE {anchor.strip()[:60]}')
        text = text.replace(anchor, repl)
    return text


def main():
    if not AC.is_file():
        raise SystemExit('ARDUINO_CLI_NOT_FOUND')
    if sha((SRC / 'lex_ref_detail_data.h').read_bytes().replace(b'\r\n', b'\n')) != HEADER_SHA_LF:
        raise SystemExit('FIRMWARE_HEADER_NOT_124 (Parte D)')
    base = assemble(TMP / 'base')
    gen = assemble(TMP / 'types')
    text = patched_text()
    (gen / INO).write_bytes(text.encode('utf-8'))
    orig = (base / INO).read_bytes().decode('utf-8').replace('\r\n', '\n').splitlines(keepends=True)
    patch = ''.join(difflib.unified_diff(orig, text.replace('\r\n', '\n').splitlines(keepends=True), f'a/{INO}', f'b/{INO}', n=2))
    (HERE / 'juris_types.patch').write_text(patch, encoding='utf-8', newline='\n')
    others_identical = all((base / p.relative_to(gen)).read_bytes() == p.read_bytes() for p in gen.rglob('*') if p.is_file() and p.name != INO)
    base_info, base_bin = compile_sketch(base, BK / 'build_base')
    gen_info, gen_bin = compile_sketch(gen, BK / 'build_types')
    approved = APPROVED_BIN.read_bytes()
    if sha(approved) != APPROVED_SHA:
        raise SystemExit('APPROVED_BINARY_MISSING_OR_CHANGED')
    same_meta, ndiff = metadata_only_diff(approved, base_bin)
    hc = json.loads(HC_JSON.read_text(encoding='utf-8'))['hc_build']
    tables = JT.parse_firmware_tables(text)
    report = dict(
        phase='F', status='HOST_ONLY_PROTOTYPE', flashed=False, firmware_dir_modified=False, physical_approval=False,
        toolchain=dict(arduino_cli=AC.name, core='esp32:esp32 3.3.11', fqbn=FQBN, build_property=FLAGS),
        base=dict(source='firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE (Parte D, header 124)', build=base_info,
                  vs_approved_differing_bytes=ndiff, vs_approved_metadata_only=same_meta),
        patch=dict(file='JURISPRUDENCE_AUDIT/JURIS_TYPE_PROTOTYPE/juris_types.patch', edits=len(PATCH), other_files_identical=others_identical,
                   ino_sha256_base=sha((base / INO).read_bytes()), ino_sha256_types=sha(text.encode('utf-8')),
                   firmware_tables_equal_host=tables == (JT.CLASSES, JT.TRIBUNAIS)),
        types_build=gen_info,
        comparison=[dict(build='aprovado (R2, gravado)', program_bytes=1100991, static_ram_bytes=126148, app_bin_bytes=len(approved)),
                    dict(build='base firmware/ (Parte D)', **{k: base_info[k] for k in ('program_bytes', 'static_ram_bytes', 'app_bin_bytes')}),
                    dict(build='protótipo HC (overnight)', **{k: hc[k] for k in ('program_bytes', 'static_ram_bytes', 'app_bin_bytes')}),
                    dict(build='protótipo tipos genéricos', **{k: gen_info[k] for k in ('program_bytes', 'static_ram_bytes', 'app_bin_bytes')})],
        delta_vs_base=dict(program_bytes=gen_info['program_bytes'] - base_info['program_bytes'],
                           static_ram_bytes=gen_info['static_ram_bytes'] - base_info['static_ram_bytes'],
                           app_bin_bytes=gen_info['app_bin_bytes'] - base_info['app_bin_bytes']),
        runtime_memory=dict(psram='inalterado pelo código: o cache PSRAM do JURISPRUDENCIA.IDX cresce só com as linhas de dados (~150-200 B por vínculo)',
                            buffers='MAX_RELACOES_ARTIGO=32 e RelacaoJuridica inalterados; nenhuma alocação nova',
                            tables_in_flash=f'{len(JT.CLASSES)} pares de const char* + {len(JT.TRIBUNAIS)} tribunais (rodata)'),
        not_verified=['teste físico (boot, lista, ficha, BACK)', 'renderização de "Súmula" na tela', 'tempo de boot', 'PSRAM em execução'],
        binaries='DEVICE_INTEGRATION/backups/juris_type_prototype/{build_base,build_types} (fora do Git)')
    (HERE / 'JURIS_TYPE_PROTOTYPE_BUILD.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report[k] for k in ('base', 'comparison', 'delta_vs_base', 'patch')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
