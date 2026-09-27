"""Repository hygiene AUDIT (read-only). Never deletes, moves, renames or edits repo files.

Writes only inside CLEANUP_AUDIT/: inventory, disk usage, dependencies, exact duplicates,
protected list, orphans, and integrity snapshots (before/after).
Usage: python CLEANUP_AUDIT/_auditoria_higiene.py
"""
import collections, datetime, hashlib, json, os, re, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'CLEANUP_AUDIT'
V2 = 'LEX_MACHINA_REFERENCIAS_V2'
EXP = V2 + '/09_CATALOGO_EXPANSAO_200'
SKIP_TOP = {'.git', 'CLEANUP_AUDIT'}
TEXT_EXT = {'.py', '.cpp', '.c', '.h', '.hpp', '.ino', '.json', '.md', '.txt', '.yaml', '.yml', '.toml', '.ini', '.cfg',
            '.bat', '.ps1', '.sh', '.js', '.ts', '.csv', '.html', '.log', '.tsv'}
REF_EXT = 'py|json|md|txt|csv|tsv|ino|h|hpp|c|cpp|idx|bin|html|js|zip|yaml|yml|toml|ini|cfg|bat|ps1|sh|log|pdf|xlsx|ndjson|jsonl'
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def sha(p, cache={}):
    k = str(p)
    if k not in cache:
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            for b in iter(lambda: f.read(1 << 20), b''):
                h.update(b)
        cache[k] = h.hexdigest()
    return cache[k]


def dump(name, obj):
    (OUT / name).write_bytes((json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n').encode('utf-8'))


def git_list(*args):
    r = subprocess.run(['git', '-C', str(REPO), '-c', 'core.quotepath=off'] + list(args) + ['-z'], capture_output=True)
    return {x.decode('utf-8', 'replace') for x in r.stdout.split(b'\0') if x}


# ------------------------------------------------------------------ integrity snapshot (read-only)
def integrity():
    base = REPO / V2
    ante = json.loads((REPO / EXP / '08_MANIFEST/INTEGRIDADE_ANTES.json').read_text(encoding='utf-8'))['files']
    frozen = {f['path']: (sha(base / f['path'], {}) == f['sha256']) for f in ante}
    grp = lambda pred: dict(arquivos=sum(1 for p in frozen if pred(p)), identicos=sum(1 for p, ok in frozen.items() if pred(p) and ok))  # noqa: E731
    ref = json.loads((REPO / EXP / '00_ENTRADA/REFERENCIA_CATALOGO_69.json').read_text(encoding='utf-8'))
    enr = REPO / EXP / '07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1'
    man = json.loads((enr / 'MANIFEST.json').read_text(encoding='utf-8'))
    idx = sorted(p for p in REPO.rglob('*') if p.is_file() and p.suffix.upper() == '.IDX' and '.git' not in p.parts and 'CLEANUP_AUDIT' not in p.parts)
    return dict(
        congelados_v2=grp(lambda p: True),
        engine_r1d1=grp(lambda p: 'r1d1' in p.lower() or p.startswith('05_COMPILADOR/')),
        rc1=grp(lambda p: p.startswith('08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/')),
        rc2=grp(lambda p: p.startswith('08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/')),
        holdout=grp(lambda p: 'holdout' in p.lower()),
        ontologia_contratos=grp(lambda p: p.startswith(('01_SCHEMA/', '04_CONCEITOS/', '02_DISPOSITIVOS/'))),
        catalogo_69=sha(Path(ref['path']), {}) == ref['sha256'],
        enriquecido_v1=all(sha(enr / f['path'], {}) == f['sha256'] for f in man['arquivos']),
        enriquecido_v1_manifest_sha=sha(enr / 'MANIFEST.json', {}),
        firmware_sha=sha(REPO / 'firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino', {}),
        idx={p.relative_to(REPO).as_posix(): sha(p, {}) for p in idx})


def main():
    OUT.mkdir(exist_ok=True)
    before = integrity()
    dump('_INTEGRIDADE_ANTES_AUDITORIA.json', dict(at=NOW, **before))

    tracked = git_list('ls-files')
    untracked = git_list('ls-files', '--others', '--exclude-standard')
    ignored = git_list('ls-files', '--others', '--ignored', '--exclude-standard')
    modified = git_list('diff', '--name-only')
    staged = git_list('diff', '--cached', '--name-only')

    ante = json.loads((REPO / EXP / '08_MANIFEST/INTEGRIDADE_ANTES.json').read_text(encoding='utf-8'))['files']
    frozen_v2 = {V2 + '/' + f['path'] for f in ante}
    enr_man = json.loads((REPO / EXP / '07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/MANIFEST.json').read_text(encoding='utf-8'))
    catalog69 = Path(json.loads((REPO / EXP / '00_ENTRADA/REFERENCIA_CATALOGO_69.json').read_text(encoding='utf-8'))['path'])
    catalog69 = catalog69.relative_to(REPO).as_posix()
    # 545 external files hashed by the frozen V2 integrity proof (INTEGRITY_BEFORE, re-checked as protected545 in R1D1)
    prot545 = {f['path'] for f in json.loads((REPO / V2 / '00_CHECKPOINTS/INTEGRITY_BEFORE.json').read_text(encoding='utf-8'))['files']}
    ACTIVE_TOPS = {V2, 'updater', 'firmware', 'docs', 'sdcard', '(raiz)'}
    LISTING = re.compile(r'^(INTEGRITY|INTEGRIDADE|BASELINE_ENRIQUECIMENTO|INVENTARIO)', re.I)

    # ------------------------------------------------------------------ walk
    files = []
    for root, dirs, fnames in os.walk(REPO):
        rel_root = Path(root).relative_to(REPO)
        if rel_root.parts and rel_root.parts[0] in SKIP_TOP:
            dirs[:] = []
            continue
        if not rel_root.parts:
            dirs[:] = [d for d in dirs if d not in SKIP_TOP]
        for fn in fnames:
            p = Path(root) / fn
            rel = p.relative_to(REPO).as_posix()
            st = p.stat()
            files.append(dict(path=rel, nome=fn, extensao=p.suffix.lower(), tamanho_bytes=st.st_size, sha256=sha(p),
                              tracked=rel in tracked, untracked=rel in untracked, ignored=rel in ignored,
                              modified=rel in modified, staged=rel in staged,
                              data_modificacao=datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).replace(microsecond=0).isoformat(),
                              diretorio_pai=Path(rel).parent.as_posix(), top=rel.split('/')[0] if '/' in rel else '(raiz)'))
    by_path = {f['path']: f for f in files}
    tops = sorted({f['top'] for f in files})

    # ------------------------------------------------------------------ reference corpus
    tok_re = re.compile(r'[\w\-\.]+\.(?:' + REF_EXT + r')\b', re.I)
    top_names = [t for t in tops if t != '(raiz)']
    top_re = re.compile('|'.join(re.escape(t) for t in sorted(top_names, key=len, reverse=True)))
    WRITE_HINT = re.compile(r"['\"]w[b+]?['\"]|write_|\.write\(|dump\(|to_csv|mkdir|SAIDA|saida|OUT\b|out_dir|output", re.I)
    refs = collections.defaultdict(dict)       # basename_lower -> {referrer: kind}
    top_refs = collections.defaultdict(set)    # top folder name -> referrers
    corpus_files = 0
    for f in files:
        parts = f['path'].split('/')
        if f['extensao'] not in TEXT_EXT or f['tamanho_bytes'] > 2_000_000:
            continue
        if any(x in ('.venv', 'venv', 'site-packages', '__pycache__', '.pytest_cache') or x.startswith('cache_') for x in parts):
            continue
        try:
            txt = (REPO / f['path']).read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        corpus_files += 1
        is_py = f['extensao'] == '.py'
        for line in txt.splitlines() if is_py else [txt]:
            for m in tok_re.finditer(line):
                b = m.group(0).split('/')[-1].split('\\')[-1].lower()
                kind = ('GERADO_POR' if WRITE_HINT.search(line) else 'CONSUMIDO_POR') if is_py else 'REFERENCIADO_POR'
                prev = refs[b].get(f['path'])
                if prev != 'GERADO_POR':
                    refs[b][f['path']] = kind
        if not LISTING.match(f['nome']):
            for m in set(top_re.findall(txt)):
                top_refs[m].add(f['path'])

    def references(fp):
        b = fp['nome'].lower()
        r = {k: v for k, v in refs.get(b, {}).items() if k != fp['path']}
        ext = {k: v for k, v in r.items() if k.split('/')[0] != fp['top']}
        return r, ext

    # ------------------------------------------------------------------ duplicates
    groups = collections.defaultdict(list)
    for f in files:
        if f['tamanho_bytes'] > 0:
            groups[f['sha256']].append(f)
    dup_groups = {h: g for h, g in groups.items() if len(g) > 1}

    # ------------------------------------------------------------------ classification
    frozen_dirs_v2 = ('00_CHECKPOINTS/', '08_RELEASE_CANDIDATE/', '07_EXECUCAO_COMPLETA/', '09_RELATORIOS/', 'tests/')
    engine_dirs_v2 = ('05_COMPILADOR/', '01_SCHEMA/', '02_DISPOSITIVOS/', '03_OBRAS/', '04_CONCEITOS/')
    DERIVED_REPORTS = {'METRICAS_FINAIS.json', 'COBERTURA_EDITORIAL.json', 'CORRECOES_ENTRADA.json', 'REDUNDANCIA_69_MAIS_200.json',
                       'REDUNDANCIA_69_MAIS_200.md', 'JOGOS_EXPANSAO.md', 'DETERMINISMO_COMPILACAO.json', 'ESTADO_FINAL.json',
                       'REJEICOES.json', 'FONTE_EM_REVISAO.json'}
    LEGACY_ARCHIVE_HINT = re.compile(r'BACKUP|ETAPA|stage|_SD_TESTE|corrigida', re.I)

    def venv_req(parts):
        i = next(i for i, x in enumerate(parts) if x in ('.venv', 'venv'))
        parent = REPO.joinpath(*parts[:i])
        return any(parent.glob('requirements*.txt'))

    def classify(f):
        p, parts, name, ext = f['path'], f['path'].split('/'), f['nome'], f['extensao']
        # caches / env
        if '__pycache__' in parts or ext in ('.pyc', '.pyo') or '.pytest_cache' in parts or ext in ('.tmp', '.temp') \
                or name.lower() in ('thumbs.db', 'desktop.ini', '.ds_store'):
            return 'CACHE_TEMPORARIO', 'Cache/bytecode/temporário recriado automaticamente pela ferramenta.', 'PROTEGIDO' if False else 'LIVRE'
        if '.venv' in parts or 'venv' in parts:
            if venv_req(parts):
                return 'GERADO_REPRODUZIVEL', 'Ambiente virtual Python; recriável com pip install -r requirements.txt do diretório pai.', 'LIVRE'
            return 'REVISAR_MANUALMENTE', 'Ambiente virtual sem requirements*.txt no diretório pai.', 'LIVRE'
        # protected families
        if ext == '.idx':
            return 'CONGELADO_PROVA', 'Arquivo IDX (índice do SD): protegido por instrução.', 'PROTEGIDO'
        if p == catalog69:
            return 'CONGELADO_PROVA', 'Catálogo original de 69 obras (hash declarado na expansão).', 'PROTEGIDO'
        if p.startswith(EXP + '/07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/'):
            return 'CONGELADO_PROVA', 'Pacote ENRIQUECIDO_V1 congelado (MANIFEST próprio).', 'PROTEGIDO'
        if p in frozen_v2:
            sub = p[len(V2) + 1:]
            if sub.startswith(engine_dirs_v2):
                return 'ATIVO_CRITICO', 'Engine R1D1 / ontologia / contratos / evidências V2 (congelado, INTEGRIDADE_ANTES).', 'PROTEGIDO'
            if sub.startswith('06_BENCHMARKS/'):
                return 'BENCHMARK_BASELINE', 'Benchmark V2 congelado (INTEGRIDADE_ANTES).', 'PROTEGIDO'
            return 'CONGELADO_PROVA', 'Checkpoint/RC/relatório V2 congelado (INTEGRIDADE_ANTES).', 'PROTEGIDO'
        if p.startswith(V2 + '/') and not p.startswith(EXP + '/'):
            sub = p[len(V2) + 1:]
            if sub.startswith(frozen_dirs_v2 + engine_dirs_v2 + ('06_BENCHMARKS/',)) or '/' not in sub:
                return 'CONGELADO_PROVA', 'Área congelada da V2 fora da lista INTEGRIDADE_ANTES (tratar como protegida).', 'PROTEGIDO'
            return 'REVISAR_MANUALMENTE', 'Arquivo da V2 fora das áreas conhecidas.', 'PROTEGIDO'
        if p.startswith(EXP + '/'):
            sub = p[len(EXP) + 1:]
            if sub.startswith('08_MANIFEST/INTEGRIDADE_ANTES') or name == 'BASELINE_ENRIQUECIMENTO_V1.json' or sub.startswith('06_RELATORIOS/CHECKPOINTS_ENRIQUECIMENTO/') \
                    or name in ('CHECKPOINT_LOTES.json', 'CHECKPOINT_ENRIQUECIMENTO.json'):
                return 'BENCHMARK_BASELINE', 'Baseline/checkpoint da expansão (prova de progresso e integridade).', 'PROTEGIDO'
            if sub.startswith('08_MANIFEST/'):
                return 'CONGELADO_PROVA', 'Manifest/integridade da expansão.', 'PROTEGIDO'
            if name.startswith('CONSULTA_CP') or re.match(r'(BUSCA_\d+|STEAM_\d{3})\.json$', name):
                return 'RAW_SOURCE_CAPTURE', 'Captura bruta de coleta (busca/loja/consulta).', 'PROTEGIDO'
            if sub.startswith('06_RELATORIOS/') and name in DERIVED_REPORTS or sub.startswith('05_REJEITADAS/'):
                return 'GERADO_REPRODUZIVEL', 'Gerado por 06_RELATORIOS/gerar_relatorios.py a partir de 02_TRIAGEM/04_DOSSIERS (executado com sucesso em 2026-09-26).', 'PROTEGIDO'
            if sub.startswith(('00_ENTRADA/', '01_IDENTIDADE/', '02_TRIAGEM/LOTE_', '04_DOSSIERS/', '07_CATALOGO_CANDIDATO/CATALOGO_')):
                return 'ATIVO_CRITICO', 'Entrada/decisão/dossiê/catálogo da expansão (necessário para reproduzir ENRIQUECIDO_V1).', 'PROTEGIDO'
            return 'ATIVO_SUPORTE', 'Script, relatório, curadoria ou registro de proveniência da expansão.', 'PROTEGIDO'
        if p.startswith('firmware/LEX_MACHINA.ino/') or p == 'firmware/README.md':
            return 'ATIVO_CRITICO', 'Firmware ativo.', 'PROTEGIDO'
        if p.startswith('updater/'):
            if parts[1] in ('backup_sd',) or 'backup' in parts[1].lower():
                return 'CONGELADO_PROVA', 'Backup do SD / updater (prova de implantação).', 'PROTEGIDO'
            if parts[1].startswith('cache_'):
                return 'RAW_SOURCE_CAPTURE', 'Cache de fontes oficiais baixadas pelo updater (insumo de build).', 'PROTEGIDO'
            if parts[1] == 'saida':
                return 'REVISAR_MANUALMENTE', 'Saída de build do updater (conteúdo implantado no SD; reprodução depende de fontes remotas).', 'PROTEGIDO'
            if f['tracked']:
                return 'ATIVO_CRITICO', 'Updater versionado (pipeline ativo de dados do SD).', 'PROTEGIDO'
            return 'ATIVO_SUPORTE', 'Updater: arquivo não versionado junto ao pipeline ativo.', 'PROTEGIDO'
        if f['top'] in ('(raiz)', 'docs', 'sdcard'):
            return 'ATIVO_CRITICO' if f['tracked'] else 'ATIVO_SUPORTE', 'Documentação/raiz do projeto.', 'PROTEGIDO'
        if f['tracked']:
            return 'ATIVO_SUPORTE', 'Arquivo versionado.', 'PROTEGIDO'
        if 'backup_sd' in parts:
            return 'CONGELADO_PROVA', 'Backup de SD em pasta legada.', 'PROTEGIDO'
        if p in prot545:
            return 'LEGADO_REFERENCIADO', 'Arquivo externo hasheado pela prova de integridade congelada da V2 (INTEGRITY_BEFORE / protected545).', 'PROTEGIDO'
        # legacy
        top = f['top']
        top_ext_refs = {r for r in top_refs.get(top, set()) if r.split('/')[0] != top and (r.split('/')[0] if '/' in r else '(raiz)') in ACTIVE_TOPS}
        if f['top'] == 'firmware':
            return ('CANDIDATO_ARQUIVAMENTO', 'Versão/backup anterior de firmware (não ativa).', 'LIVRE')
        if any(x.startswith('cache_') for x in parts):
            return 'RAW_SOURCE_CAPTURE', 'Cache de fontes oficiais em pasta legada.', 'LIVRE'
        if top_ext_refs:
            return 'LEGADO_REFERENCIADO', f'Pasta legada citada por nome em {len(top_ext_refs)} arquivo(s) de áreas ativas/congeladas.', 'LIVRE'
        if LEGACY_ARCHIVE_HINT.search(top) or ext == '.zip':
            return 'CANDIDATO_ARQUIVAMENTO', 'Snapshot/etapa/backup legado sem referência externa por nome de pasta.', 'LIVRE'
        return 'LEGADO_NAO_REFERENCIADO', 'Pasta legada de pesquisa sem referência externa por nome de pasta.', 'LIVRE'

    for f in files:
        cat, why, prot = classify(f)
        f.update(categoria_preliminar=cat, justificativa=why, protecao=prot)

    # principal copy per duplicate group; secondary unprotected copies -> DUPLICATA_EXATA
    PRIO = {'ATIVO_CRITICO': 0, 'CONGELADO_PROVA': 1, 'BENCHMARK_BASELINE': 2, 'ATIVO_SUPORTE': 3, 'RAW_SOURCE_CAPTURE': 4,
            'GERADO_REPRODUZIVEL': 5, 'LEGADO_REFERENCIADO': 6, 'REVISAR_MANUALMENTE': 7, 'LEGADO_NAO_REFERENCIADO': 8,
            'CANDIDATO_ARQUIVAMENTO': 9, 'CACHE_TEMPORARIO': 10}
    dup_out = []
    for h, g in sorted(dup_groups.items(), key=lambda kv: -kv[1][0]['tamanho_bytes'] * len(kv[1])):
        g.sort(key=lambda f: (not f['tracked'], PRIO.get(f['categoria_preliminar'], 9), len(f['path']), f['path']))
        main_f = g[0]
        others = g[1:]
        for f in others:
            f['duplicata_de'] = main_f['path']
            if f['protecao'] != 'PROTEGIDO' and f['categoria_preliminar'] not in ('CACHE_TEMPORARIO', 'GERADO_REPRODUZIVEL'):
                f['categoria_preliminar'] = 'DUPLICATA_EXATA'
                f['justificativa'] = f'SHA-256 idêntico a {main_f["path"]}.'
        risk = 'ALTO' if any(f['protecao'] == 'PROTEGIDO' for f in others) else 'MEDIO' if any(f['categoria_preliminar'] == 'LEGADO_REFERENCIADO' for f in g) else 'BAIXO'
        dup_out.append(dict(hash=h, tamanho_individual=main_f['tamanho_bytes'], quantidade=len(g),
                            espaco_total=main_f['tamanho_bytes'] * len(g), espaco_redundante=main_f['tamanho_bytes'] * (len(g) - 1),
                            arquivo_sugerido_principal=main_f['path'], demais_paths=[f['path'] for f in others], paths=[f['path'] for f in g],
                            categorias=sorted({f['categoria_preliminar'] for f in g}),
                            risco_de_remocao=risk,
                            motivo_da_sugestao='Principal escolhido por: versionado > área ativa/congelada > caminho mais curto.' +
                                               (' Há cópias em área protegida: não remover essas.' if risk == 'ALTO' else '')))

    # references & orphans
    deps = []
    orphans = []
    for f in files:
        if f['categoria_preliminar'] in ('CACHE_TEMPORARIO',) or '.venv' in f['path'].split('/'):
            continue
        r, ext = references(f)
        rec = dict(path=f['path'], categoria=f['categoria_preliminar'],
                   REFERENCIADO_POR=sorted(k for k, v in r.items() if v == 'REFERENCIADO_POR')[:8],
                   GERADO_POR=sorted(k for k, v in r.items() if v == 'GERADO_POR')[:8],
                   CONSUMIDO_POR=sorted(k for k, v in r.items() if v == 'CONSUMIDO_POR')[:8],
                   total_referencias=len(r), referencias_externas_a_pasta_topo=len(ext))
        f['referencias'] = len(r)
        f['referencias_externas'] = len(ext)
        if r:
            deps.append(rec)
        if f['protecao'] != 'PROTEGIDO' and not r and f['categoria_preliminar'] not in ('DUPLICATA_EXATA', 'GERADO_REPRODUZIVEL') \
                and f['extensao'] not in ('.idx',):
            orphans.append(dict(path=f['path'], categoria=f['categoria_preliminar'], tamanho_bytes=f['tamanho_bytes'],
                                tracked=f['tracked'], nota='Sem referência por nome em arquivos de texto do repositório; não é prova de inutilidade.'))

    # ------------------------------------------------------------------ outputs
    inv = [{k: f[k] for k in ('path', 'nome', 'extensao', 'tamanho_bytes', 'sha256', 'tracked', 'untracked', 'ignored', 'modified', 'staged',
                             'data_modificacao', 'diretorio_pai', 'categoria_preliminar', 'justificativa', 'protecao')}
           | ({'duplicata_de': f['duplicata_de']} if 'duplicata_de' in f else {}) | {'referencias': f.get('referencias', 0)} for f in files]
    dump('INVENTARIO_REPOSITORIO.json', dict(gerado_em=NOW, raiz=str(REPO), excluidos=['.git/', 'CLEANUP_AUDIT/'], total_arquivos=len(inv),
                                             total_bytes=sum(f['tamanho_bytes'] for f in files), arquivos=inv))
    dump('DEPENDENCIAS.json', dict(gerado_em=NOW, metodo=dict(
        corpus=f'{corpus_files} arquivos de texto (≤2 MB; exclui .venv, site-packages, __pycache__, cache_*)',
        referencia='nome de arquivo com extensão conhecida citado no texto; em .py, a linha é classificada como GERADO_POR (indício de escrita) ou CONSUMIDO_POR',
        limites='Referência por nome é indicativa (nomes genéricos como main.py geram falso positivo); ausência de referência não prova inutilidade.'),
        referencias_a_pastas_de_topo={t: dict(total=len(top_refs.get(t, ())), externas=sorted(r for r in top_refs.get(t, ()) if r.split('/')[0] != t)[:15],
                                              externas_total=sum(1 for r in top_refs.get(t, ()) if r.split('/')[0] != t)) for t in top_names},
        arquivos=deps))
    dump('DUPLICATAS_EXATAS.json', dict(gerado_em=NOW, criterio='Somente SHA-256 idêntico (arquivos com 0 bytes excluídos).', grupos=len(dup_out),
                                        arquivos_envolvidos=sum(g['quantidade'] for g in dup_out), espaco_redundante_bytes=sum(g['espaco_redundante'] for g in dup_out),
                                        grupos_detalhe=dup_out))
    dump('ORFAOS_CANDIDATOS.json', dict(gerado_em=NOW, criterio='Não protegido, sem referência por nome em nenhum arquivo de texto, não duplicata, não gerado reprodutível.',
                                        total=len(orphans), bytes=sum(o['tamanho_bytes'] for o in orphans),
                                        por_pasta_topo=dict(collections.Counter(o['path'].split('/')[0] for o in orphans).most_common()),
                                        orfaos=orphans))
    after = integrity()
    same = {k: before[k] == after[k] for k in before}
    dump('_INTEGRIDADE_DEPOIS_AUDITORIA.json', dict(at=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
                                                    identico_ao_antes=same, tudo_identico=all(same.values()), **after))
    cats = collections.Counter(f['categoria_preliminar'] for f in files)
    print(json.dumps(dict(arquivos=len(files), bytes=sum(f['tamanho_bytes'] for f in files), categorias=dict(cats), dup_grupos=len(dup_out),
                          orfaos=len(orphans), corpus=corpus_files, integridade_identica=all(same.values())), ensure_ascii=False))


if __name__ == '__main__':
    main()
