"""Tela vermelha 3,2": firmware jurídico principal + correções de painel validadas no LEX_DIAG_CFG5_BOOT (58a22b0). Host-only.

Base: candidato INVON=0 (fonte aprovada f7e6b190 com PAINEL_PRECISA_INVON 1 -> 0; regenerada e conferida por build_tela_vermelha).
Patch de painel (só tela/boot; nada jurídico, SD, BLE ou touch):
  1. TFT_RST 14 -> 15 (fio RESET da tela no GPIO15)
  2. tft passa a ser Adafruit_ILI9341_PainelLex: setRotation() aplica MADCTL 0x40 (MX, RGB, sem MV) + geometria lógica 320x240
  3. setup: RST da tela em LOW desde a primeira linha; DISPOFF logo após tft.begin() (a init da lib termina com DISPON)
  4. setup: uma linha de boot pela USB nativa (instancia HWCDC propria, sem bloqueio) para verificação sem Monitor Serial
Uso:  python build_painel_candidate.py           compila baseline INVON=0 + candidato e grava relatório
      python build_painel_candidate.py --check   confere fonte, patch e .bin gerados (sem compilar)
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
import build_tela_vermelha as TV  # noqa: E402

INO = TV.INO
E = TV.E
OUT = HERE / 'candidate_painel'
PATCH_FILE = HERE / 'painel.patch'
REPORT = HERE / 'TELA_VERMELHA_PAINEL_BUILD.json'
INVON0_BIN = HERE / 'candidate_invon0' / f'{INO}.bin'
INVON0_APP_SHA = '936851787ee780c626a61d714ec798e806c5d4df45679b99c0becd9460ff302d'

PATCH = [  # (âncora, substituição); cada âncora deve ocorrer exatamente uma vez
    ('#define TFT_RST   14' + E,
     '#define TFT_RST   15   // tela vermelha 3,2": fio RESET no GPIO15 (DEVICE_INTEGRATION/TELA_VERMELHA/diag_faixa)' + E),
    ('Adafruit_ILI9341 tft(&spiBus, TFT_DC, TFT_CS, TFT_RST);' + E,
     '// Tela vermelha 3,2": painel nativo em paisagem. Orientacao validada fisicamente no LEX_DIAG_CFG5_BOOT (58a22b0):' + E +
     '// MADCTL 0x40 (MX, ordem RGB, sem MV) com geometria logica 320x240. setRotation() fica neutralizado: qualquer chamada' + E +
     '// reaplica essa configuracao, para nenhum codigo sobrescrever o MADCTL aprovado. A lib so usa _width/_height para recorte.' + E +
     '#define PAINEL_MADCTL 0x40' + E +
     'class Adafruit_ILI9341_PainelLex : public Adafruit_ILI9341' + E + '{' + E + 'public:' + E +
     '  using Adafruit_ILI9341::Adafruit_ILI9341;' + E +
     '  void setRotation(uint8_t) override { aplicarOrientacaoPainel(); }' + E +
     '  void aplicarOrientacaoPainel()' + E + '  {' + E +
     '    uint8_t m=PAINEL_MADCTL;' + E +
     '    sendCommand(ILI9341_MADCTL,&m,1);' + E +
     '    rotation=0; _width=320; _height=240;' + E +
     '  }' + E + '};' + E +
     'Adafruit_ILI9341_PainelLex tft(&spiBus, TFT_DC, TFT_CS, TFT_RST);' + E +
     '// USB-Serial/JTAG nativo (a COM da USB-C), so para uma linha de boot. Serial continua na UART0, como no aprovado.' + E +
     'HWCDC lexUsbSerial;' + E),
    ('void setup()' + E + '{' + E + '  Serial.begin(115200);' + E,
     'void setup()' + E + '{' + E +
     '  pinMode(TFT_RST,OUTPUT); digitalWrite(TFT_RST,LOW);   // painel em reset ate tft.begin(): sem chuvisco no boot' + E +
     '  Serial.begin(115200);' + E),
    ('  tft.begin(40000000);' + E + '  tft.setRotation(3);' + E,
     '  tft.begin(40000000);' + E +
     '  tft.sendCommand(ILI9341_DISPOFF);   // a init da lib termina com DISPON e GRAM aleatoria' + E +
     '  tft.setRotation(3);                 // neutralizado: aplica MADCTL 0x40 + 320x240 (Adafruit_ILI9341_PainelLex)' + E),
    ('  desenharTransicaoSplash(true);' + E + '  delay(3500);' + E,
     '  desenharTransicaoSplash(true);' + E + '  uint32_t msSplashVisivel=(uint32_t)millis();' + E + '  delay(3500);' + E),
    ('  ultimaInteracaoMs=(uint32_t)millis();' + E + '}' + E,
     '  ultimaInteracaoMs=(uint32_t)millis();' + E +
     '  // Uma linha de boot pela USB nativa (COM do USB-Serial/JTAG), sem bloquear se ninguem estiver lendo a porta.' + E +
     '  lexUsbSerial.setTxTimeoutMs(0);' + E +
     '  lexUsbSerial.begin();' + E +
     '  lexUsbSerial.printf("[LEXUSB] BOOT OK %lums splash=%lums SD=%s pastas=%d MADCTL=0x%02X 320x240 RST=%d\\n",' + E +
     '                     (unsigned long)millis(),(unsigned long)msSplashVisivel,sdOK?"OK":"FALHA",totalPastas,PAINEL_MADCTL,TFT_RST);' + E +
     '}' + E),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def base_text():
    return TV.invon0_text(TV.approved_source())


def painel_text(base):
    text = base
    for anchor, repl in PATCH:
        if text.count(anchor) != 1:
            raise SystemExit(f'ANCHOR_NOT_UNIQUE {anchor.strip()[:60]}')
        text = text.replace(anchor, repl)
    return text


def unified(base, cand):
    return ''.join(difflib.unified_diff(base.replace(E, '\n').splitlines(True), cand.replace(E, '\n').splitlines(True),
                                        f'a/{INO} (INVON=0 93685178)', f'b/{INO} (painel tela vermelha)'))


def main():
    base = base_text()
    cand = painel_text(base)
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
    base_info, base_bin, _ = TV.compile_sketch(TV.assemble('invon0', base), 'invon0')
    repro = TV.diff_bytes(base_bin, INVON0_BIN.read_bytes())
    if sha(INVON0_BIN.read_bytes()) != INVON0_APP_SHA or not repro['metadata_only']:
        raise SystemExit('INVON0_BASELINE_NOT_REPRODUCED ' + json.dumps(repro))
    cand_info, cand_bin, cand_build = TV.compile_sketch(TV.assemble('painel', cand), 'painel')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / INO).write_bytes(cand.encode('utf-8'))
    (OUT / f'{INO}.bin').write_bytes(cand_bin)
    for ext in ('elf', 'map'):   # locais (gitignored)
        shutil.copyfile(cand_build / f'{INO}.{ext}', OUT / f'{INO}.{ext}')
    PATCH_FILE.write_text(unified(base, cand), encoding='utf-8')
    report = dict(
        schema_version=1, status='HOST_ONLY_CANDIDATE', flashed=False, sd_changed=False,
        purpose='Tela vermelha 3,2": RST GPIO15, MADCTL 0x40 + 320x240 (RGB, INVOFF), boot sem chuvisco, log de boot na USB.',
        validated_by='DEVICE_INTEGRATION/TELA_VERMELHA/diag_faixa/LEX_DIAG_CFG5_BOOT (58a22b0) + comando b (MADCTL 0x40)',
        toolchain=TV.toolchain_info(),
        base=dict(name='INVON=0', app_sha256=INVON0_APP_SHA, source_sha256=sha(base.encode('utf-8')),
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
