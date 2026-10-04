"""ETAPA "ÍNDICES DE ARTIGOS" do Updater (ARTICLE_SEARCH.IDX de todo o acervo).

ATUALIZAR LEGISLAÇÃO = atualizar textos -> validar -> gerar/atualizar os ARTICLE_SEARCH.IDX -> manifesto; só então a atualização está
pronta. A execução padrão do Updater (Catálogo Mestre + módulo consumidor = "ATUALIZAR TUDO") e --somente-mestre incluem esta etapa
automaticamente; --sem-indices-artigos a desliga.

A geração é a do DEVICE_INTEGRATION (tools/article_index_corpus.py): mesmas normas do Catálogo Mestre, mesmo localizador de arquivos
deste Updater, parser estrutural do LEGAL_TARGET_ID. É INCREMENTAL: fonte idêntica -> KEEP; fonte alterada -> REBUILD; norma nova ->
ADD; norma que saiu do acervo -> REMOVE (no staging); formato inesperado -> INDEX_BUILD_BLOCKED (norma, arquivo, linha, motivo), sem
índice parcial. Os índices vão para um STAGING (nunca direto para o cartão); a cópia para o SD é uma etapa de implantação separada.
--simular-mestre gera num diretório temporário e só relata.
"""
import sys
import tempfile
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[1]
SAIDA_PADRAO = RAIZ_REPO / 'DEVICE_INTEGRATION' / 'staging_article_indexes_full_corpus_candidate'


def _corpus():
    sys.path.insert(0, str(RAIZ_REPO / 'DEVICE_INTEGRATION' / 'tools'))
    import article_index_corpus as C
    return C


def executar_etapa_indices_artigos(raiz_vademecum, inventariar, localizar, saida=None, simular=False, manifesto_fisico=None):
    """Gera/atualiza os índices de artigos do acervo em `raiz_vademecum`. -> manifesto (dict) com summary/blocked/norms.
    inventariar/localizar = inventariar_vademecum e localizar_item_mestre do Updater (descoberta pelo catálogo, sem lista fixa)."""
    C = _corpus()
    saida = Path(saida) if saida else SAIDA_PADRAO
    anterior = saida if (saida / '_host' / 'ARTICLE_INDEX_MANIFEST.json').is_file() else C.APPROVED_STAGING
    localizador = (lambda raiz: inventariar(), localizar)
    if simular:
        with tempfile.TemporaryDirectory() as t:
            return C.build_corpus(raiz_vademecum, Path(t) / 'simulacao', previous_dir=anterior, physical_manifest=manifesto_fisico,
                                  locator=localizador)
    return C.build_corpus(raiz_vademecum, saida, previous_dir=anterior, physical_manifest=manifesto_fisico, locator=localizador)


def linhas_relatorio(manifesto, simular=False):
    s = manifesto['summary']
    L = ['ARTICLE INDEXES' + (' (SIMULAÇÃO: nada gravado)' if simular else ''),
         f"Normas analisadas: {s['norms_analysed']}",
         f"Índices mantidos: {s['KEEP']}",
         f"Regenerados: {s['REBUILD']}",
         f"Novos: {s['ADD']}",
         f"Removidos: {s['REMOVE']}",
         f"Bloqueados: {s['BLOCKED']}",
         f"Records totais: {s['records_total']}",
         f"Storage total: {s['index_storage_bytes']} B (+ catálogo {s['catalog_bytes']} B)",
         f"Maior índice: {s['index_bytes_max']} B ({s['index_bytes_max_norma']})",
         'Determinismo: saída sem relógio (mesma entrada -> mesmos bytes)']
    for b in manifesto['blocked']:
        L.append(f"  INDEX_BUILD_BLOCKED {b['norma']} | {b['file']} | linha {b['line']} | {b['reason']}")
    return L
