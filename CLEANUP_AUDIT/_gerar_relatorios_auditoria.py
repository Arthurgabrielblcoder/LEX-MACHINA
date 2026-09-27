"""Builds USO_DE_DISCO.md, PROTEGIDO_NAO_TOCAR.json and _ESTATISTICAS.json from INVENTARIO_REPOSITORIO.json (read-only)."""
import collections, json, re
from pathlib import Path

OUT = Path(__file__).resolve().parent
inv = json.loads((OUT / 'INVENTARIO_REPOSITORIO.json').read_text(encoding='utf-8'))
files = inv['arquivos']
TOT = sum(f['tamanho_bytes'] for f in files)
mb = lambda b: f'{b / 1048576:,.1f}'.replace(',', 'X').replace('.', ',').replace('X', '.')  # noqa: E731
top = lambda p: p.split('/')[0] if '/' in p else '(raiz)'  # noqa: E731

# --------------------------------------------------------------- directory sizes (recursive)
dirs = collections.defaultdict(lambda: [0, 0])
for f in files:
    parts = f['path'].split('/')[:-1]
    for i in range(1, len(parts) + 1):
        d = '/'.join(parts[:i])
        dirs[d][0] += f['tamanho_bytes']
        dirs[d][1] += 1
tops = {d: v for d, v in dirs.items() if '/' not in d}
tops['(raiz)'] = [sum(f['tamanho_bytes'] for f in files if '/' not in f['path']), sum(1 for f in files if '/' not in f['path'])]
cat_by_top = collections.defaultdict(collections.Counter)
for f in files:
    cat_by_top[top(f['path'])][f['categoria_preliminar']] += f['tamanho_bytes']

L = ['# Uso de disco — LEX-MACHINA', '',
     f"Árvore auditada: `{inv['raiz']}` (exclui `.git/` e `CLEANUP_AUDIT/`). **{len(files):,} arquivos, {mb(TOT)} MB.** `.git/` ≈ 95 MB (medido à parte).".replace(',', '.'), '',
     'Tamanho grande não significa lixo. A coluna "duplicado" soma cópias secundárias com SHA-256 idêntico a outro arquivo (DUPLICATA_EXATA).', '',
     '## Por pasta de primeiro nível', '', '| Pasta | Arquivos | MB | % | MB duplicado | MB cache | MB venv/gerado |', '|---|---:|---:|---:|---:|---:|---:|']
for d, (b, n) in sorted(tops.items(), key=lambda kv: -kv[1][0]):
    c = cat_by_top[d]
    L.append(f'| `{d}` | {n} | {mb(b)} | {100 * b / TOT:.1f} | {mb(c["DUPLICATA_EXATA"])} | {mb(c["CACHE_TEMPORARIO"])} | {mb(c["GERADO_REPRODUZIVEL"])} |')
conc = sorted(tops.items(), key=lambda kv: -kv[1][0])
acc = 0
L += ['', '## Concentração', '']
for i, (d, (b, n)) in enumerate(conc[:10], 1):
    acc += b
    L.append(f'- Top {i} pastas acumulam **{100 * acc / TOT:.1f}%** (até `{d}`).')
L += ['', '## 50 maiores diretórios (recursivo)', '', '| Diretório | Arquivos | MB |', '|---|---:|---:|']
for d, (b, n) in sorted(dirs.items(), key=lambda kv: -kv[1][0])[:50]:
    L.append(f'| `{d}` | {n} | {mb(b)} |')
L += ['', '## 100 maiores arquivos', '', '| # | Arquivo | MB | Categoria | Git |', '|---:|---|---:|---|---|']
for i, f in enumerate(sorted(files, key=lambda f: -f['tamanho_bytes'])[:100], 1):
    g = 'tracked' if f['tracked'] else 'ignored' if f['ignored'] else 'untracked'
    L.append(f"| {i} | `{f['path']}` | {mb(f['tamanho_bytes'])} | {f['categoria_preliminar']} | {g} |")
cats = collections.Counter()
catn = collections.Counter()
for f in files:
    cats[f['categoria_preliminar']] += f['tamanho_bytes']
    catn[f['categoria_preliminar']] += 1
L += ['', '## Por categoria preliminar', '', '| Categoria | Arquivos | MB | % |', '|---|---:|---:|---:|']
for k, b in cats.most_common():
    L.append(f'| {k} | {catn[k]} | {mb(b)} | {100 * b / TOT:.1f} |')
(OUT / 'USO_DE_DISCO.md').write_text('\n'.join(L) + '\n', encoding='utf-8')

# --------------------------------------------------------------- protected list
prot = [f for f in files if f['protecao'] == 'PROTEGIDO']
groups = collections.defaultdict(list)
RULES = [
    ('ENGINE_R1D1_ONTOLOGIA_CONTRATOS', lambda p: p.startswith('LEX_MACHINA_REFERENCIAS_V2/') and p.split('/')[1] in ('01_SCHEMA', '02_DISPOSITIVOS', '03_OBRAS', '04_CONCEITOS', '05_COMPILADOR')),
    ('RC1', lambda p: '/CF_REFERENCIAS_V2_RC1/' in p),
    ('RC2_REVISAO_HUMANA', lambda p: '/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/' in p),
    ('HOLDOUT', lambda p: 'holdout' in p.lower()),
    ('CHECKPOINTS_V2_PROVAS', lambda p: p.startswith('LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/')),
    ('BENCHMARKS_V2', lambda p: p.startswith('LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/')),
    ('V2_OUTROS_CONGELADOS', lambda p: p.startswith('LEX_MACHINA_REFERENCIAS_V2/') and not p.startswith('LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/')),
    ('ENRIQUECIDO_V1', lambda p: '/07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/' in p),
    ('EXPANSAO_200_ENTRADAS_DECISOES_DOSSIES_CATALOGO', lambda p: p.startswith('LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/')),
    ('CATALOGO_69_ORIGINAL', lambda p: p.endswith('CATALOGO_69_CANONICO.json')),
    ('IDX', lambda p: p.upper().endswith('.IDX')),
    ('FIRMWARE_ATIVO', lambda p: p.startswith('firmware/')),
    ('UPDATER_ATIVO_E_BACKUP_SD', lambda p: p.startswith('updater/')),
    ('OUTROS_PROTEGIDOS_PROTECTED545_BACKUP_SD_RAIZ_DOCS', lambda p: True),
]
for f in prot:
    name = next(n for n, r in RULES if r(f['path']))
    groups[name].append(f)
prot_out = dict(
    regra='NÃO tocar sem nova autorização explícita. Na dúvida, PROTEGER.',
    total_arquivos=len(prot), total_bytes=sum(f['tamanho_bytes'] for f in prot),
    nao_versionados=sum(1 for f in prot if not f['tracked']),
    grupos={n: dict(arquivos=len(g), bytes=sum(f['tamanho_bytes'] for f in g), nao_versionados=sum(1 for f in g if not f['tracked']),
                    exemplos=sorted(f['path'] for f in g)[:12]) for n, g in sorted(groups.items())},
    padroes_protegidos=[
        'LEX_MACHINA_REFERENCIAS_V2/** (Engine R1D1, ontologia, contratos, RC1, RC2 com decisões humanas, holdout, benchmarks, checkpoints, relatórios de integridade)',
        'LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/** (entradas, triagens, dossiês, overlays, checkpoints, baselines, manifests, scripts geradores, ENRIQUECIDO_V1)',
        'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json (catálogo original de 69)',
        '**/*.IDX (130 índices)', 'firmware/LEX_MACHINA.ino/** (firmware ativo)', 'updater/** (pipeline, backup_sd, caches de fonte, saida implantada)',
        '545 arquivos externos listados em LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json (escopo protected545 da prova R1D1)',
        '**/backup_sd/**', 'README.md, HISTORICO_RELEASES.md, docs/**, sdcard/**, .gitignore'],
    arquivos=sorted(f['path'] for f in prot))
(OUT / 'PROTEGIDO_NAO_TOCAR.json').write_bytes((json.dumps(prot_out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))

# --------------------------------------------------------------- families & stats
fam_re = re.compile(r'([_\- ]?(v\d+([_.]\d+)*|alpha\d*|beta\d*|rc\d*|final\d*|backup|bak|copy|copia|old|new|teste?|tmp|temp|\d+))+$', re.I)
fam = collections.defaultdict(list)
for d in [d for d in tops if d != '(raiz)']:
    base = fam_re.sub('', d.replace('1- ', '')) or d
    fam[base].append(d)
fams = {k: sorted(v) for k, v in fam.items() if len(v) > 1}
name_fam = collections.Counter()
for f in files:
    for tok in re.findall(r'(?i)(?<![a-z])(v\d+|alpha\d*|beta|rc\d|final\d*|backup|bak|copy|copia|old|teste?|tmp|temp)(?![a-z])', f['nome']):
        name_fam[tok.lower()] += 1
stats = dict(total_arquivos=len(files), total_bytes=TOT,
             categorias={k: dict(arquivos=catn[k], bytes=b) for k, b in cats.items()},
             ondas={
                 'ONDA_1': [f['path'] for f in files if f['categoria_preliminar'] == 'CACHE_TEMPORARIO'],
                 'ONDA_2': [f['path'] for f in files if f['categoria_preliminar'] == 'DUPLICATA_EXATA'],
                 'ONDA_3': [f['path'] for f in files if f['categoria_preliminar'] == 'GERADO_REPRODUZIVEL' and f['protecao'] == 'LIVRE'],
                 'ONDA_4': [f['path'] for f in files if f['categoria_preliminar'] in ('CANDIDATO_ARQUIVAMENTO', 'LEGADO_NAO_REFERENCIADO') and f['protecao'] == 'LIVRE']},
             familias_pastas_topo=fams, tokens_de_versao_em_nomes=dict(name_fam.most_common()))
by = {f['path']: f for f in files}
stats['ondas_bytes'] = {k: dict(arquivos=len(v), bytes=sum(by[p]['tamanho_bytes'] for p in v)) for k, v in stats['ondas'].items()}
(OUT / '_ESTATISTICAS.json').write_bytes((json.dumps(stats, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
print(json.dumps(dict(ondas=stats['ondas_bytes'], protegidos=len(prot), grupos_prot={n: len(g) for n, g in groups.items()}, familias=fams), ensure_ascii=False, indent=1))
