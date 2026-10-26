"""Tela vermelha 3,2": candidato EXPERIMENTAL de repouso com tela preta. Host-only; nunca faz flash.

Base: candidato painel 22367f3 (1bb3deb0; regenerado por build_painel_candidate e conferido só por metadados).
Edições, só na rotina de repouso:
  1. definirDisplayLigado(false): fillScreen(COR_FUNDO) com o display LIGADO, em vez de DISPOFF (painel TN normally white
     mostra BRANCO com DISPOFF). Ao acordar: DISPON (inócuo) e o redesenho completo que já existia.
  2. atualizarInatividadeDisplay(): marca displayApagado ANTES de pintar e reconfere o timeout; se uma tecla chegou nesse
     intervalo, desiste do repouso. Assim nenhuma ação de tecla pode desenhar por cima da tela preta.
SOLUÇÃO VISUAL PROVISÓRIA: o backlight continua aceso (está no 3,3 V, sem GPIO); não há economia de energia de um desligamento real.
Uso:  python build_repouso_candidate.py           compila base painel + candidato e grava relatório
      python build_repouso_candidate.py --check   confere fonte, patch e .bin gerados (sem compilar)
"""
from __future__ import annotations

import difflib
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_painel_candidate as P  # noqa: E402

TV = P.TV
INO = TV.INO
E = TV.E
OUT = HERE / 'candidate_repouso'
PATCH_FILE = HERE / 'repouso.patch'
REPORT = HERE / 'TELA_VERMELHA_REPOUSO_BUILD.json'
PAINEL_BIN = HERE / 'candidate_painel' / f'{INO}.bin'
PAINEL_APP_SHA = '1bb3deb0561451a1a998d530470204fd200cc4160b878aba28200ad1372f4ce3'

PATCH = [  # (âncora, substituição); cada âncora deve ocorrer exatamente uma vez
    ('  // DISPOFF preserva RAM/configuracao do ILI9341. Nao usamos SLPIN,' + E +
     '  // portanto DISPON basta e nao ha espera de SLPOUT no loop.' + E +
     '  tft.sendCommand(ligado ? ILI9341_DISPON : ILI9341_DISPOFF);' + E,
     '  // Tela vermelha (TN, normally white): DISPOFF mostra BRANCO. Repouso = GRAM preta com o display ligado.' + E +
     '  // SOLUCAO VISUAL PROVISORIA: o backlight continua aceso (3V3, sem GPIO); nao ha economia de energia real.' + E +
     '  // Ao acordar, atualizarInatividadeDisplay() ja chama redesenharTelaAtual(): a GRAM nao precisa ser preservada.' + E +
     '  if(ligado) tft.sendCommand(ILI9341_DISPON);' + E +
     '  else tft.fillScreen(COR_FUNDO);' + E),
    ('           (uint32_t)((uint32_t)millis()-ultimaInteracaoMs)>=TIMEOUT_TELA_MS){' + E +
     '    displayApagado=true;' + E +
     '    definirDisplayLigado(false);' + E,
     '           (uint32_t)((uint32_t)millis()-ultimaInteracaoMs)>=TIMEOUT_TELA_MS){' + E +
     '    // Marca o repouso ANTES de pintar e reconfere: uma tecla que chegou depois do teste acima ja atualizou' + E +
     '    // ultimaInteracaoMs (desiste do repouso); uma que chegue depois desta linha e consumida so para acordar.' + E +
     '    displayApagado=true;' + E +
     '    if((uint32_t)((uint32_t)millis()-ultimaInteracaoMs)<TIMEOUT_TELA_MS){ displayApagado=false; return; }' + E +
     '    definirDisplayLigado(false);' + E),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def repouso_text(base):
    text = base
    for anchor, repl in PATCH:
        if text.count(anchor) != 1:
            raise SystemExit(f'ANCHOR_NOT_UNIQUE {anchor.strip()[:60]}')
        text = text.replace(anchor, repl)
    return text


def unified(base, cand):
    return ''.join(difflib.unified_diff(base.replace(E, '\n').splitlines(True), cand.replace(E, '\n').splitlines(True),
                                        f'a/{INO} (painel 1bb3deb0)', f'b/{INO} (repouso tela preta)'))


def main():
    base = P.painel_text(P.base_text())
    cand = repouso_text(base)
    if '--check' in sys.argv:
        rep = json.loads(REPORT.read_text(encoding='utf-8'))
        ok = (OUT / INO).read_bytes() == cand.encode('utf-8') and sha(cand.encode('utf-8')) == rep['candidate']['source_sha256']
        ok = ok and sha((OUT / f'{INO}.bin').read_bytes()) == rep['candidate']['app_sha256']
        ok = ok and PATCH_FILE.read_text(encoding='utf-8') == unified(base, cand)
        print('UP_TO_DATE' if ok else 'STALE')
        return 0 if ok else 1
    if not TV.AC.is_file():
        raise SystemExit(f'ARDUINO_CLI_NOT_FOUND {TV.AC}')
    if TV.TMP.exists():
        shutil.rmtree(TV.TMP)
    base_info, base_bin, _ = TV.compile_sketch(TV.assemble('painel', base), 'painel')
    repro = TV.diff_bytes(base_bin, PAINEL_BIN.read_bytes())
    if sha(PAINEL_BIN.read_bytes()) != PAINEL_APP_SHA or not repro['metadata_only']:
        raise SystemExit('PAINEL_BASELINE_NOT_REPRODUCED ' + json.dumps(repro))
    cand_info, cand_bin, cand_build = TV.compile_sketch(TV.assemble('repouso', cand), 'repouso')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / INO).write_bytes(cand.encode('utf-8'))
    (OUT / f'{INO}.bin').write_bytes(cand_bin)
    for ext in ('elf', 'map'):   # locais (gitignored)
        shutil.copyfile(cand_build / f'{INO}.{ext}', OUT / f'{INO}.{ext}')
    PATCH_FILE.write_text(unified(base, cand), encoding='utf-8')
    report = dict(
        schema_version=1, status='HOST_ONLY_EXPERIMENTAL_CANDIDATE', flashed=False, sd_changed=False,
        purpose='Repouso com tela preta (fillScreen) em vez de DISPOFF, que fica branco no painel TN da tela vermelha.',
        limitation='SOLUCAO VISUAL PROVISORIA: backlight continua aceso (3V3, sem GPIO); sem economia de energia de desligamento real.',
        toolchain=TV.toolchain_info(),
        base=dict(name='painel 22367f3', app_sha256=PAINEL_APP_SHA, source_sha256=sha(base.encode('utf-8')),
                  rebuilt=base_info, vs_committed_bin=repro, verdict='REPRODUCED (idêntico exceto metadados de build)'),
        patch=dict(file=PATCH_FILE.name, edits=len(PATCH)),
        candidate=dict(source=str((OUT / INO).relative_to(TV.ROOT)).replace('\\', '/'), source_sha256=sha(cand.encode('utf-8')),
                       binary=str((OUT / f'{INO}.bin').relative_to(TV.ROOT)).replace('\\', '/'), **cand_info),
        candidate_vs_base=dict(program_bytes=cand_info['program_bytes'] - base_info['program_bytes'],
                               static_ram_bytes=cand_info['static_ram_bytes'] - base_info['static_ram_bytes'],
                               app_bin_bytes=cand_info['app_bin_bytes'] - base_info['app_bin_bytes']),
    )
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(base=report['base'], candidate=report['candidate'], delta=report['candidate_vs_base']),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
