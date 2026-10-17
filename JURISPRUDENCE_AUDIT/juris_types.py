"""PÓS-NOTURNA Parte E — extensible jurisprudence type model (host side). Tribunal and classe are SEPARATE fields; the device label is derived
from (tribunal, classe, numero) by the same rule the generalized firmware prototype implements (JURIS_TYPE_PROTOTYPE/juris_types.patch).
The firmware table CLASSES_JURIS and TRIBUNAIS are parsed back from the patch and must equal CLASSES / TRIBUNAIS here (test_juris_types).

Legacy (installed, physically validated) types keep their exact labels: repercussao_geral -> "RG TEMA n", sumula_vinculante -> "SV n",
adi -> "ADI n" (+ adc, adpf, acordao, iac, sirdr, repetitivo_stj already in the firmware). Legacy IDs (STF:RG:63:CF88:1:-:-:-) are unchanged.
"""
import re

TRIBUNAIS = ('STF', 'STJ', 'TSE', 'TST', 'STM')
# IDX TIPO (lowercase) -> label prefix. Order = firmware table order.
CLASSES = (('hc', 'HC'), ('habeas_corpus', 'HC'), ('rhc', 'RHC'), ('ms', 'MS'), ('rms', 'RMS'), ('ap', 'AP'), ('ai', 'AI'), ('inq', 'Inq'),
           ('rcl', 'Rcl'), ('mi', 'MI'), ('pet', 'Pet'), ('ado', 'ADO'), ('re', 'RE'), ('are', 'ARE'), ('ext', 'Ext'))
LEGACY = {'sumula_vinculante': 'SV {n}', 'sv': 'SV {n}', 'repercussao_geral': 'RG TEMA {n}', 'rg': 'RG TEMA {n}', 'adi': 'ADI {n}',
          'adc': 'ADC {n}', 'adpf': 'ADPF {n}', 'acordao': 'ACORDAO {n}', 'iac': 'IAC {n}', 'sirdr': 'SIRDR {n}', 'repetitivo_stj': 'REPETITIVO STJ {n}'}
SUMULA = ('sumula', 'sumula_stf')
# review-module klass -> (IDX TIPO, tribunal override)
KLASS_TO_TIPO = {'RG': 'repercussao_geral', 'SV': 'sumula_vinculante', 'ADI': 'adi', 'ADC': 'adc', 'ADPF': 'adpf', 'HC': 'hc', 'RHC': 'rhc',
                 'MS': 'ms', 'RMS': 'rms', 'AP': 'ap', 'AI': 'ai', 'INQ': 'inq', 'RCL': 'rcl', 'MI': 'mi', 'PET': 'pet', 'ADO': 'ado', 'RE': 're',
                 'ARE': 'are', 'EXT': 'ext', 'SUMULA': 'sumula', 'SUMULA_TSE': 'sumula', 'SUMULA_STJ': 'sumula'}
LIST_WIDTH = 34          # imprimirUTF8(…, 34) in the relation list; the row prefix is "<pos> "


def label(tipo, tribunal, numero):
    """Device label exactly as the generalized firmware prints it. Raises for an unknown type (fail closed: never 'OUTRO n')."""
    t = tipo.lower()
    if t in LEGACY:
        return LEGACY[t].format(n=numero)
    if t in SUMULA:
        return f'Súmula {numero}' + (f' {tribunal}' if tribunal else '')
    for k, v in CLASSES:
        if t == k:
            return f'{v} {numero}'
    raise ValueError(f'UNKNOWN_JURIS_TYPE {tipo}')


def title(tipo, tribunal, numero):
    """Header of an opened ficha (nomeArquivoAtual): tribunal + label, without repeating the tribunal of a súmula."""
    lb = label(tipo, tribunal, numero)
    return lb if tipo.lower() in SUMULA else f'{tribunal} {lb}'


def identificador(tribunal, klass, numero):
    return f'{tribunal}:{klass}:{numero}'


def ficha(ident):
    """arquivoDetalheJurisCF: ':' and '/' -> '_' + .TXT (unchanged firmware rule)."""
    return ident.replace(':', '_').replace('/', '_') + '.TXT'


def id_accepted(row_id, tribunal):
    """tribunalJurisSuportado: ID prefix must be a whitelisted tribunal AND equal the TRIBUNAL column (legacy STF rows: always true)."""
    return tribunal in TRIBUNAIS and row_id.startswith(tribunal + ':')


def from_precedent(p):
    """(tipo, tribunal, numero, identificador, label) for a review-module precedent dict (id = TRIB:KLASS:NUM)."""
    trib, klass, num = p['id'].split(':')[:3]
    tipo = KLASS_TO_TIPO[p['klass']]
    return tipo, trib, num, identificador(trib, klass, num), label(tipo, trib, num)


def parse_firmware_tables(ino_text):
    classes = tuple(re.findall(r'\{"([a-z_]+)","([A-Za-z]+)"\}', ino_text.split('CLASSES_JURIS[]={', 1)[1].split('};', 1)[0]))
    tribs = tuple(re.findall(r'"([A-Z]{3})"', ino_text.split('TRIBUNAIS[]={', 1)[1].split('};', 1)[0]))
    return classes, tribs
