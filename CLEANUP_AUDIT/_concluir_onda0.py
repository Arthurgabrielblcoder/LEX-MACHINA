"""Verificações direcionadas da ONDA 0; não executa engine, snapshot ou limpeza.

prepare: materializa paths explícitos autorizados pelo GIT_VERSIONING_PLAN.md.
verify: confere somente manifests/listas existentes e cobertura de proteção.
staged: confere o índice contra a lista aprovada e os bytes normalizados pelo Git.
Não realiza git add, commit, tag, push, remoção ou movimentação.
"""
import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'CLEANUP_AUDIT'
V2 = 'LEX_MACHINA_REFERENCIAS_V2'
EXP = V2 + '/09_CATALOGO_EXPANSAO_200'
SNAP = Path('C:/GitHub_LEX_MACHINA_SAFETY_PRE_CLEANUP_2026-09-26')
HEAD = 'd4e816fb5a904f401b5ea1133720fc052d69412d'
REMOTE = 'https://github.com/Arthurgabrielblcoder/LEX-MACHINA.git'
BLOCKED = EXP + '/03_FONTES/BUSCA_118.json'
EXCLUDED = {BLOCKED, EXP+'/06_RELATORIOS/CONSULTA_CP11.txt', EXP+'/06_RELATORIOS/CONSULTA_CP12.txt'}
LARGE_AUDIT = {'INVENTARIO_REPOSITORIO.json','DEPENDENCIAS.json','DUPLICATAS_EXATAS.json','_ESTATISTICAS.json'}

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p, value): p.write_bytes((json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def git(*args, data=None):
    return subprocess.run(['git','-C',str(REPO),*args],input=data,capture_output=True,check=True).stdout
def paths_git(*args): return {p.decode('utf-8') for p in git(*args,'-z').split(b'\0') if p}
def excluded(p):
    return p in EXCLUDED or any(x in p.split('/') for x in ('.venv','venv','__pycache__','.pytest_cache')) or Path(p).suffix.lower() in ('.pyc','.pyo','.idx')
def approved_paths():
    paths=set()
    # A1, B1, B2, B3: somente diretórios explicitamente enumerados no plano.
    for name in ('00_CHECKPOINTS','01_SCHEMA','02_DISPOSITIVOS','03_OBRAS','04_CONCEITOS','05_COMPILADOR','06_BENCHMARKS','07_EXECUCAO_COMPLETA','08_RELEASE_CANDIDATE','09_CATALOGO_EXPANSAO_200','09_RELATORIOS','tests'):
        paths.update(p.relative_to(REPO).as_posix() for p in (REPO/V2/name).rglob('*') if p.is_file())
    paths.add(V2+'/README.md')
    paths.add('firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino')
    paths.update(p.relative_to(REPO).as_posix() for p in (REPO/'firmware/LEX_MACHINA.ino/assets').rglob('*') if p.is_file())
    paths.update('updater/'+n for n in ('implantar_sd.py','relations_v2.py','test_implantar_sd.py','test_relations_v2.py'))
    paths.update(p.relative_to(REPO).as_posix() for p in (REPO/'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1').iterdir() if p.is_file() and p.suffix in ('.py','.json','.md'))
    paths.update(p.relative_to(REPO).as_posix() for p in OUT.iterdir() if p.is_file() and p.name not in LARGE_AUDIT)
    return sorted(p for p in paths if not excluded(p))

def verify():
    baseline=load(OUT/'_INTEGRIDADE_ANTES_AUDITORIA.json')
    frozen=load(REPO/EXP/'08_MANIFEST/INTEGRIDADE_ANTES.json')['files']
    groups={
        'congelados_v2': lambda p: True,
        'engine_r1d1': lambda p: 'r1d1' in p.lower() or p.startswith('05_COMPILADOR/'),
        'rc1': lambda p:p.startswith('08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/'),
        'rc2': lambda p:p.startswith('08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/'),
        'holdout': lambda p:'holdout' in p.lower(),
        'ontologia_contratos': lambda p:p.startswith(('01_SCHEMA/','02_DISPOSITIVOS/','04_CONCEITOS/'))}
    checked={f['path']:(REPO/V2/f['path']).is_file() and sha(REPO/V2/f['path'])==f['sha256'] for f in frozen}
    result={k:{'arquivos':sum(pred(p) for p in checked),'identicos':sum(pred(p) and ok for p,ok in checked.items())} for k,pred in groups.items()}
    protected=load(REPO/V2/'00_CHECKPOINTS/INTEGRITY_BEFORE.json')['files']
    bad545=[f['path'] for f in protected if not (REPO/f['path']).is_file() or sha(REPO/f['path'])!=f['sha256']]
    result['protected545']={'arquivos':len(protected),'identicos':len(protected)-len(bad545),'divergencias':bad545}
    badidx=[p for p,h in baseline['idx'].items() if not (REPO/p).is_file() or sha(REPO/p)!=h]
    result['idx']={'arquivos':len(baseline['idx']),'identicos':len(baseline['idx'])-len(badidx),'divergencias':badidx,'policy':'IDX_SNAPSHOT_APENAS'}
    firmware=sha(REPO/'firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino')
    result['firmware']={'sha256':firmware,'identico':firmware==baseline['firmware_sha']}
    ref=load(REPO/EXP/'00_ENTRADA/REFERENCIA_CATALOGO_69.json')
    result['catalogo_69']={'sha256':sha(Path(ref['path'])),'identico':sha(Path(ref['path']))==ref['sha256']}
    package=REPO/EXP/'07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1'
    manifest=load(package/'MANIFEST.json')
    badpkg=[f['path'] for f in manifest['arquivos'] if sha(package/f['path'])!=f['sha256']]
    result['enriquecido_v1']={'arquivos':len(manifest['arquivos'])+1,'divergencias':badpkg,'manifest_sha256':sha(package/'MANIFEST.json'),'identico':not badpkg and sha(package/'MANIFEST.json')==baseline['enriquecido_v1_manifest_sha']}
    safety=load(SNAP/'SAFETY_MANIFEST.json')
    sums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (SNAP/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if line}
    result['sha256sums']={'arquivos':len(sums),'valido':all(sha(SNAP/n)==h for n,h in sums.items()),'hashes':sums}
    assert safety['validacao']['valido'] and safety['total_arquivos']==3713
    sm={e['path_relativo']:e for e in safety['arquivos']}
    # Não refaz o ZIP nem a auditoria: valida a cobertura dos paths já protegidos.
    tracked=paths_git('ls-files')
    protected_paths=load(OUT/'PROTEGIDO_NAO_TOCAR.json')['arquivos']
    uncovered=[p for p in protected_paths if p not in tracked and p not in sm]
    blocked_hash=sha(REPO/BLOCKED)
    result['segredo_conhecido']={'path':BLOCKED,'fora_do_indice':BLOCKED not in tracked,'snapshot_preserva_mesmos_bytes':blocked_hash==sm[BLOCKED]['sha256']}
    result['cobertura_protegidos']={'total':len(protected_paths),'sem_git_ou_snapshot':uncovered}
    result['snapshot']={'valido':True,'base':'Validação individual do ZIP concluída pelo Claude; manifest válido e checksum do artefato revalidado.','arquivos':3713}
    git('bundle','verify',str(SNAP/'LEX_MACHINA_PRE_CLEANUP.bundle'))
    result['bundle']={'valido':True,'base':'Clone mirror e fsck herdados do Claude; git bundle verify reexecutado.'}
    result['engine_executada']=False;result['sd_tocado']=False
    result['resultado']='PASSA' if all(v['arquivos']==v['identicos'] for k,v in result.items() if k in groups or k in ('protected545','idx')) and result['firmware']['identico'] and result['catalogo_69']['identico'] and result['enriquecido_v1']['identico'] and result['sha256sums']['valido'] and all(result['segredo_conhecido'][k] for k in ('fora_do_indice','snapshot_preserva_mesmos_bytes')) and not uncovered else 'FALHA'
    return result

def prepare():
    assert git('rev-parse','HEAD').decode().strip()==HEAD,'ESTADO_DIVERGIU_DESDE_CLAUDE'
    assert git('branch','--show-current').decode().strip()=='main'
    assert git('remote','get-url','origin').decode().strip()==REMOTE
    assert not paths_git('diff','--cached','--name-only'),'Índice não vazio'
    inv={f['path']:f for f in load(OUT/'INVENTARIO_REPOSITORIO.json')['arquivos']}
    candidates=approved_paths()
    diffs=[p for p in candidates if not p.startswith('CLEANUP_AUDIT/') and (p not in inv or sha(REPO/p)!=inv[p]['sha256'])]
    assert not diffs, 'Divergências desde auditoria: '+str(diffs)
    integrity=verify();dump(OUT/'_INTEGRIDADE_FINAL_ONDA0.json',integrity)
    assert integrity['resultado']=='PASSA'
    # Inclui os próprios registros documentais em D3; sem depender de hash circular.
    additions=['CLEANUP_AUDIT/_ONDA0_PRE_STAGING.json','CLEANUP_AUDIT/ONDA0_STAGING_PATHS.txt']
    candidates=sorted(set(approved_paths()+additions))
    hashes={p:sha(REPO/p) for p in candidates if not p.startswith('CLEANUP_AUDIT/')}
    groups=collections.Counter(p.split('/')[0] for p in candidates)
    dump(OUT/'_ONDA0_PRE_STAGING.json',{'head':HEAD,'branch':'main','remote':REMOTE,'staged_antes':0,'total_paths_aprovados':len(candidates),'grupos':groups,'paths':candidates,'hashes_funcionais_worktree':hashes,'diferencas_inventario':diffs,'plano_sha256':sha(OUT/'GIT_VERSIONING_PLAN.md'),'exclusoes':sorted(EXCLUDED),'core_autocrlf':git('config','--get','core.autocrlf').decode().strip()})
    (OUT/'ONDA0_STAGING_PATHS.txt').write_bytes(('\n'.join(candidates)+'\n').encode('utf-8'))
    print(json.dumps({'estado':'PRONTO_PARA_STAGING_SELETIVO','arquivos':len(candidates),'grupos':groups,'integridade':integrity['resultado']},ensure_ascii=False))

def staged():
    plan=load(OUT/'_ONDA0_PRE_STAGING.json'); approved=set(plan['paths'])
    actual=paths_git('diff','--cached','--name-only')
    assert actual==approved, json.dumps({'inesperados':sorted(actual-approved),'faltantes':sorted(approved-actual)})
    assert not actual & EXCLUDED
    for p,h in plan['hashes_funcionais_worktree'].items(): assert sha(REPO/p)==h,'Worktree mudou: '+p
    # Compara os blobs com git hash-object --path (respeita core.autocrlf sem escrever no worktree).
    indexed={}
    for row in git('ls-files','--stage','-z').split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1); indexed[p.decode('utf-8')]=meta.split()[1].decode()
    mismatch=[]
    for p in sorted(actual):
        expected=git('hash-object','--path='+p,'--',p).decode().strip()
        if indexed[p]!=expected: mismatch.append(p)
    assert not mismatch,'Blobs diferentes: '+str(mismatch)
    print(json.dumps({'staged':len(actual),'somente_aprovados':True,'segredo_fora':True,'blobs_correspondem_ao_worktree_com_normalizacao_git':True,'bytes_funcionais_preservados':True},ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='staged': staged()
    elif sys.argv[1]=='verify':
        result=verify(); print(json.dumps(result,ensure_ascii=False)); assert result['resultado']=='PASSA'
