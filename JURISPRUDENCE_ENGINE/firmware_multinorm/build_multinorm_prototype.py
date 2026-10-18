"""SPRINT DE ESCALA — Parte C: HOST-ONLY multinorm jurisprudence firmware prototype. NEVER flashes, NEVER modifies firmware/.

Base = the physically approved generic firmware (J2I app 1371e69a…) = firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE + JURIS_TYPE_PROTOTYPE patch.
Multinorm patch (exact anchors, fail closed; CRLF as in the .ino):
  1. LookupJurisCFCache.norma char[8] -> char[16] (catalog ids up to 15 chars, e.g. HEDIONDOS1990, were truncated -> never matched)
  2. NORMAS_JURIS[] generated from updater/catalogo_mestre_vademecum.json (pasta_destino, arquivo_sugerido only where a folder holds several
     norms, id) + normaJurisAtual(): CF88 (CF file, CF part) | ADCT (CF runtime, ADCT part) | catalog id by folder/file | "" (fail closed)
  3. normaTemJurisLookup(norma): the boot cache holds at least one JUR_LOOKUP row of that norm
  4. lookup + context label use normaJurisConsulta (default "CF88") instead of the literal "CF88"
  5. carregarRelacoesDoArtigo: CF branch unchanged; NEW branch for any other norm WITH rows (else the previous flow, byte-for-byte)
  6. key '2' / footer: a single "JURISPRUDENCIA" category opens the list directly also for the multinorm branch (as in the CF)
CF behaviour: the CF branch, its lookups and labels are untouched; ADCT keeps the LEXV1 layer (JUR_LOOKUP has no ADCT rows).
Sketch/binaries: %TEMP%/lex_machina_fw_multinorm/ (scratch, outside the repository). Writes MULTINORM_PROTOTYPE_BUILD.json + multinorm.patch.
Usage: python build_multinorm_prototype.py [--no-compile]
"""
import difflib
import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG = ROOT / 'updater/catalogo_mestre_vademecum.json'
TYPES = ROOT / 'JURISPRUDENCE_AUDIT/JURIS_TYPE_PROTOTYPE/build_juris_type_prototype.py'
TMP = Path(tempfile.gettempdir()) / 'lex_machina_fw_multinorm'   # scratch, outside the repository
OUT = HERE / 'MULTINORM_PROTOTYPE_BUILD.json'
PATCH_FILE = HERE / 'multinorm.patch'
J2I_APP_SHA = '1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c'
E = '\r\n'


def types_module():
    spec = importlib.util.spec_from_file_location('juris_type_prototype', TYPES)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def catalog_table():
    """(pasta, arquivo or '', id) for every catalog norm except CF88 (handled by arquivoAtualPertenceACF). arquivo only when shared."""
    items = json.loads(CATALOG.read_text(encoding='utf-8'))['itens']
    by = {}
    for c in items:
        by.setdefault(c['pasta_destino'], []).append(c)
    rows = []
    for c in items:
        if c['id'] == 'CF88':
            continue
        if len(c['id']) > 15:
            raise SystemExit(f'NORM_ID_TOO_LONG {c["id"]}')
        shared = len(by[c['pasta_destino']]) > 1
        rows.append((c['pasta_destino'], c['arquivo_sugerido'] if shared else '', c['id']))
    return rows


def c_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def patch_list():
    table = (',' + E + '  ').join('{%s,%s,%s}' % (c_str(p), c_str(a), c_str(i)) for p, a, i in catalog_table())
    new_funcs = (
        '// MULTINORMA (protótipo host-only): norma corrente derivada do arquivo aberto, a partir do Catálogo Mestre (gerado; fonte única).' + E +
        '// arquivo vazio = pasta de uma norma só; preenchido = pasta compartilhada (exige o nome do arquivo). Sem correspondência: "" (fail closed).' + E +
        'struct NormaJurisCatalogo { const char *pasta; const char *arquivo; const char *id; };' + E +
        'static const NormaJurisCatalogo NORMAS_JURIS[]={' + E + '  ' + table + E + '};' + E +
        'String normaJurisConsulta="CF88";     // norma usada pela consulta do JUR_LOOKUP (CF por padrão: comportamento anterior)' + E +
        'bool jurisMultinormaAtiva=false;      // a lista atual veio do ramo multinorma (não-CF)' + E + E +
        'String normaJurisAtual()' + E + '{' + E +
        '  if(arquivoAtualPertenceACF()) return "CF88";' + E +
        '#if LEX_DEVICE_V1_ENABLED' + E +
        '  if(caminhoArquivoAtual==LEXV1_RUNTIME_CF_PATH) return "ADCT";   // runtime da CF, parte do ADCT (sub-namespace)' + E +
        '#endif' + E +
        '  for(size_t i=0;i<sizeof(NORMAS_JURIS)/sizeof(NORMAS_JURIS[0]);i++){' + E +
        '    String pasta=String("/")+NORMAS_JURIS[i].pasta+"/";' + E +
        '    if(!caminhoArquivoAtual.startsWith(pasta)) continue;' + E +
        '    if(!NORMAS_JURIS[i].arquivo[0] || caminhoArquivoAtual.substring(pasta.length())==NORMAS_JURIS[i].arquivo) return NORMAS_JURIS[i].id;' + E +
        '  }' + E +
        '  return "";' + E + '}' + E + E +
        'bool normaTemJurisLookup(const String &norma)' + E + '{' + E +
        '  if(!cacheJurisCFCarregado || norma.length()==0) return false;   // normas novas exigem o cache de boot (sem varredura no SD)' + E +
        '  for(int i=0;i<totalJurLookupCFCache;i++) if(norma==jurLookupCFCache[i].norma) return true;' + E +
        '  return false;' + E + '}' + E + E)
    branch = (
        '  // MULTINORMA: outra norma do catálogo COM linhas no JUR_LOOKUP. Sem linhas, segue exatamente o fluxo anterior.' + E +
        '  {' + E +
        '    String nj=normaJurisAtual();' + E +
        '    if(nj.length() && nj!="CF88" && normaTemJurisLookup(nj)){' + E +
        '      normaJurisConsulta=nj;' + E +
        '      carregarJurisprudenciaCF(artigo);' + E +
        '      normaJurisConsulta="CF88";' + E +
        '      jurisMultinormaAtiva=totalRelacoesArtigo>0;' + E +
        '      menuRelacoesAtivo=jurisMultinormaAtiva;' + E +
        '      modoDigitacaoArtigo=!menuRelacoesAtivo;' + E +
        '      Serial.printf("PERF RODAPE_MULTINORMA: %lu us (norma=%s juris=%d)\\n",micros()-t0,nj.c_str(),totalRelacoesArtigo);' + E +
        '      return menuRelacoesAtivo;' + E +
        '    }' + E +
        '  }' + E + E)
    return [  # (anchor, replacement, expected count)
        ('struct LookupJurisCFCache {' + E + '  char norma[8];' + E, 'struct LookupJurisCFCache {' + E + '  char norma[16];' + E, 1),
        ('String normaOrigemRelationsV2Atual()' + E, new_funcs + 'String normaOrigemRelationsV2Atual()' + E, 1),
        ('    if(buscarLookupJurisCFExato("CF88",artigo,tentativas[i].p,' + E, '    if(buscarLookupJurisCFExato(normaJurisConsulta,artigo,tentativas[i].p,' + E, 1),
        ('    String rotulo=rotuloOrigemRelationsV2("CF88",artigo,parUsado,incUsado,aliUsada);' + E,
         '    String rotulo=rotuloOrigemRelationsV2(normaJurisConsulta,artigo,parUsado,incUsado,aliUsada);' + E, 1),
        ('bool carregarRelacoesDoArtigo(const String &artigo)' + E + '{' + E + '  uint32_t t0=micros();' + E,
         'bool carregarRelacoesDoArtigo(const String &artigo)' + E + '{' + E + '  uint32_t t0=micros();' + E + '  jurisMultinormaAtiva=false;' + E, 1),
        ('  if(!sdOK) return false;' + E + E + '  // O CDC continua no V1 nesta fase para preservar a jurisprudencia e' + E,
         '  if(!sdOK) return false;' + E + E + branch + '  // O CDC continua no V1 nesta fase para preservar a jurisprudencia e' + E, 1),
        ('arquivoAtualPertenceACF() && totalCategoriasJuris==1', '(arquivoAtualPertenceACF() || jurisMultinormaAtiva) && totalCategoriasJuris==1', 2),
    ]


def multinorm_text(base_text):
    text = base_text
    for anchor, repl, n in patch_list():
        if text.count(anchor) != n:
            raise SystemExit(f'ANCHOR_COUNT {text.count(anchor)}!={n}: {anchor.strip()[:70]}')
        text = text.replace(anchor, repl)
    return text


def main():
    T = types_module()
    base = T.patched_text()                       # = source of the J2I app (generic classes/tribunals)
    multi = multinorm_text(base)
    diff = ''.join(difflib.unified_diff(base.replace('\r\n', '\n').splitlines(True), multi.replace('\r\n', '\n').splitlines(True),
                                        f'a/{T.INO} (J2I = base + juris_types.patch)', f'b/{T.INO} (multinorma)'))
    PATCH_FILE.write_text(diff, encoding='utf-8', newline='\n')
    doc = dict(part='C', status='HOST_ONLY_PROTOTYPE', flashed=False, firmware_dir_modified=False, physical_approval=False,
               base=dict(source='firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE + JURIS_TYPE_PROTOTYPE/juris_types.patch', physical_app_sha256=J2I_APP_SHA,
                         ino_sha256=hashlib.sha256(base.encode('utf-8')).hexdigest()),
               patch=dict(file='JURISPRUDENCE_ENGINE/firmware_multinorm/multinorm.patch', edits=sum(n for *_, n in patch_list()),
                          ino_sha256=hashlib.sha256(multi.encode('utf-8')).hexdigest(), catalog_norms_in_table=len(catalog_table()),
                          shared_folder_rows=sum(1 for _, a, _ in catalog_table() if a)))
    lookups = sum(1 for l in (ROOT / 'JURISPRUDENCE_AUDIT/J2H_CANDIDATE_B_OVER_A/candidate/SD/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX')
                  .read_text(encoding='utf-8').splitlines() if l and not l.startswith('#'))
    doc['runtime_memory'] = dict(
        psram_lookup_cache=f'LookupJurisCFCache: 60 -> 68 B por lookup (+8 B no campo norma); J2I: {lookups} lookups -> +{8 * lookups} B de PSRAM',
        psram_records='JURISPRUDENCIA.IDX inteiro em PSRAM, como antes; cresce só com as linhas de dados de outras normas (~150-200 B por vínculo)',
        cache_limits='MAX_JUR_LOOKUPS_SEGURANCA=4096, MAX_RELACOES_ARTIGO=32 e quantidade por lookup <= 255 inalterados; o mesmo cache serve todas as normas',
        boot='nenhuma leitura nova no boot: o cache é o mesmo arquivo; a tabela de normas está em flash (const)',
        per_lookup='CF: idêntico (mesma função, norma "CF88"); outras normas: +1 varredura linear do cache (<= 4096 entradas) em normaTemJurisLookup',
        not_verified=['teste físico', 'tempo real de boot e de lookup no ESP32', 'PSRAM em execução'])
    if '--no-compile' in sys.argv and OUT.is_file():
        prev = json.loads(OUT.read_text(encoding='utf-8'))
        if prev.get('patch', {}).get('ino_sha256') == doc['patch']['ino_sha256']:
            doc.update({k: prev[k] for k in ('toolchain', 'builds', 'base_reproduces_j2i_app', 'delta') if k in prev})
    if '--no-compile' not in sys.argv:
        if TMP.exists():
            shutil.rmtree(TMP)
        builds = {}
        for name, text in (('j2i_base', base), ('multinorm', multi)):
            sk = T.assemble(TMP / f'src_{name}')
            (sk / T.INO).write_bytes(text.encode('utf-8'))
            builds[name], _ = T.compile_sketch(sk, TMP / f'build_{name}')
        b, m = builds['j2i_base'], builds['multinorm']
        doc.update(toolchain=dict(fqbn=T.FQBN, build_property=T.FLAGS, arduino_cli=str(T.AC.name), core='esp32:esp32 3.3.11'),
                   builds=builds, base_reproduces_j2i_app=b['app_bin_bytes'] == 1102176,
                   delta=dict(program_bytes=m['program_bytes'] - b['program_bytes'], static_ram_bytes=m['static_ram_bytes'] - b['static_ram_bytes'],
                              app_bin_bytes=m['app_bin_bytes'] - b['app_bin_bytes']))
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: doc[k] for k in doc if k in ('patch', 'builds', 'delta', 'base_reproduces_j2i_app')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
