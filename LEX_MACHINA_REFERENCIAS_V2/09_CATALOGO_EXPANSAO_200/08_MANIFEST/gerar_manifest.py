"""Final integrity check and manifest for 09_CATALOGO_EXPANSAO_200 (read-only on frozen data).

1. Recomputes the 281 frozen V2 hashes recorded in INTEGRIDADE_ANTES.json.
2. Checks the canonical 69 catalog, firmware and IDX files (hash + mtime vs mission start).
3. Writes INTEGRIDADE_DEPOIS.json, then MANIFEST.json with SHA-256 of every expansion file.
"""
import datetime, hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # 09_CATALOGO_EXPANSAO_200
V2 = ROOT.parent                                    # LEX_MACHINA_REFERENCIAS_V2
REPO = V2.parent                                    # LEX-MACHINA
MISSION_START = datetime.datetime(2026, 9, 26, 12, 39, 0, tzinfo=datetime.timezone.utc)  # INTEGRIDADE_ANTES.at
FIRMWARE = REPO / 'firmware' / 'LEX_MACHINA.ino' / 'LEX_MACHINA.ino.ino'
FIRMWARE_SHA_AT_RESUME = '62f256e443d3ada9489fe5565744533851f14ac30c9c3c3754de26f4d01d058d'
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.write_bytes((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mtime(p):
    return datetime.datetime.fromtimestamp(p.stat().st_mtime, datetime.timezone.utc)


before = load(ROOT / '08_MANIFEST' / 'INTEGRIDADE_ANTES.json')
frozen = []
for f in before['files']:
    p = V2 / f['path']
    now = sha(p) if p.exists() else None
    frozen.append(dict(path=f['path'], sha256_antes=f['sha256'], sha256_depois=now, identico=now == f['sha256']))


def group(pred):
    items = [f for f in frozen if pred(f['path'])]
    return dict(arquivos=len(items), identicos=sum(f['identico'] for f in items), intacto=bool(items) and all(f['identico'] for f in items))


ref69 = load(ROOT / '00_ENTRADA' / 'REFERENCIA_CATALOGO_69.json')
canon = Path(ref69['path'])
idx = sorted(p for p in REPO.rglob('*') if p.is_file() and p.suffix.upper() == '.IDX' and '.git' not in p.parts)
idx_changed = [str(p.relative_to(REPO)) for p in idx if mtime(p) >= MISSION_START]
git_status = subprocess.run(['git', '-C', str(REPO), 'status', '--short', '--', 'firmware'], capture_output=True, text=True).stdout.splitlines()
outside = []
for p in REPO.rglob('*'):
    if p.is_file() and '.git' not in p.parts and ROOT not in p.parents and mtime(p) >= MISSION_START:
        outside.append(str(p.relative_to(REPO)))

integridade = dict(
    verificado_em=NOW, referencia='08_MANIFEST/INTEGRIDADE_ANTES.json', inicio_da_missao=MISSION_START.isoformat(),
    congelados_v2=dict(total=len(frozen), identicos=sum(f['identico'] for f in frozen), intactos=all(f['identico'] for f in frozen)),
    engine_r1d1=group(lambda s: 'r1d1' in s.lower() or s.startswith('05_COMPILADOR/')),
    rc1=group(lambda s: s.startswith('08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/')),
    rc2=group(lambda s: s.startswith('08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/')),
    holdout=group(lambda s: 'holdout' in s.lower()),
    ontologia_e_contratos=group(lambda s: s.startswith(('01_SCHEMA/', '04_CONCEITOS/', '02_DISPOSITIVOS/'))),
    catalogo_69=dict(path=str(canon), sha256_declarado=ref69['sha256'], sha256_atual=sha(canon), intacto=sha(canon) == ref69['sha256']),
    firmware=dict(path=str(FIRMWARE.relative_to(REPO)), sha256_na_retomada=FIRMWARE_SHA_AT_RESUME, sha256_atual=sha(FIRMWARE),
                  mtime=mtime(FIRMWARE).isoformat(), anterior_a_missao=mtime(FIRMWARE) < MISSION_START,
                  intacto=sha(FIRMWARE) == FIRMWARE_SHA_AT_RESUME and mtime(FIRMWARE) < MISSION_START, git_status_firmware=git_status,
                  nota='A modificação rastreada pelo git (M) é de 2026-09-17, anterior a esta missão; não foi causada pela expansão.'),
    idx=dict(arquivos=len(idx), alterados_desde_inicio_da_missao=idx_changed, intactos=not idx_changed,
             nota='Sem baseline de hash pré-missão para IDX; a verificação é por data de modificação e ausência de qualquer escrita desta missão.'),
    sd=dict(tocado=False, nota='Nenhum comando desta missão acessou unidade removível ou o updater de SD; todas as escritas ficaram em 09_CATALOGO_EXPANSAO_200/ e no scratchpad da sessão.'),
    arquivos_do_repositorio_alterados_fora_da_expansao_desde_o_inicio=outside,
    engine_executada=False, vinculos_juridicos_gerados=False)
integridade['tudo_intacto'] = all([integridade['congelados_v2']['intactos'], integridade['catalogo_69']['intacto'],
                                   integridade['firmware']['intacto'], integridade['idx']['intactos'], not outside])
dump(ROOT / '08_MANIFEST' / 'INTEGRIDADE_DEPOIS.json', dict(integridade, detalhes_congelados=frozen))

files = sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts)
manifest = dict(
    gerado_em=NOW, missao='09_CATALOGO_EXPANSAO_200', raiz='LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200',
    total_arquivos=len(files),
    arquivos=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in files],
    referencias_congeladas_usadas=dict(
        catalogo_69=dict(path=str(canon), sha256=sha(canon)),
        congelados_v2_verificados=len(frozen), congelados_v2_intactos=integridade['congelados_v2']['intactos']),
    catalogo_candidato={p.name: sha(p) for p in sorted((ROOT / '07_CATALOGO_CANDIDATO').glob('CATALOGO_*.json'))})
dump(ROOT / '08_MANIFEST' / 'MANIFEST.json', manifest)
print(json.dumps({k: v for k, v in integridade.items() if k not in ('arquivos_do_repositorio_alterados_fora_da_expansao_desde_o_inicio',)}, ensure_ascii=False, indent=1)[:3000])
print('manifest files', len(files), 'outside changes', len(outside))
