from editorial import *
import sys
batch=int(sys.argv[1]);rows=[]
for line in (ROOT/'02_TRIAGEM'/f'CURADORIA_{batch:02}.tsv').read_text(encoding='utf-8').splitlines():
 if not line.strip():continue
 n,year,creator,publisher,tier,url,fact,areas=line.split('|');n=int(n)
 typ='EVENTO_NARRATIVO' if n<=125 else 'ARGUMENTO_DOCUMENTAL' if n<=160 else 'ARGUMENTO_ACADEMICO'
 # Nonfiction needs attribution to the author, not narration of a fictional event.
 if n in [180,192]:typ='EVENTO_AUTOBIOGRAFICO'
 if n in [188,189,190,191,200]:typ='EVENTO_NARRATIVO'
 status='APTA' if n>125 else 'APTA_COM_RESSALVA'
 risk='Relato e seleção do realizador/autor; não tomar a obra como inventário exaustivo ou decisão jurídica.' if n>125 else 'Ficção ou dramatização; o evento narrado não comprova a ocorrência histórica nem os requisitos de um instituto brasileiro.'
 if n in [128,129,130,131,132,133,145,146,147,148,150,152,153,154,161,162,163,164,165,166,167,168,171,174,175,176,180,185,188,189,190,191,192,193,194,195,196,197,198,199,200]:status='APTA_COM_RESSALVA'
 if year=='?':status='FONTE_EM_REVISAO'
 row=dict(number=n,ano=int(year) if year!='?' else None,criador_principal=creator.split(';') if creator!='?' else [],publisher_distribuidor_editora=publisher.split(';') if publisher!='?' else [],status_triagem=status,fontes=[dict(url=url,tier=tier,accessed_on='2026-09-26',locator='Ficha e sinopse/apresentação da obra',supports=['identidade','fato_central'],paraphrase=fact)],facts=[dict(text=fact,content_type=typ)],areas_potenciais=areas.split(';'),objetos_juridicos_potenciais=areas.split(';'),riscos=[risk],transposition_limits=[risk,'Áreas potenciais são metadados editoriais; não constituem correspondência com dispositivo.'])
 if n==92:row.update(status_triagem='REJEITADA_DUPLICATA_EXISTENTE',duplicate_of='EXP-SER-002',titulo_ptbr='A Escuta',motivo='The Wire é o título original de A Escuta (2002), já presente nas 69 obras.')
 if n==138:row.update(tipo='SÉRIE',subtipo='SERIE_DOCUMENTAL',nota_correcao='Entrada agrupada em documentários; formato factual é série documental. Preservado o candidato, sem trocar a obra.')
 if n==101:row.update(subtipo='TEMPORADA_DE_ANTOLOGIA',franquia='American Crime Story',nota_edicao='Unidade curada: temporada The People v. O.J. Simpson; não abrange outras temporadas.')
 if n==107:row.update(nota_edicao='Desambiguação: série norte-americana de 2013; não a minissérie britânica de 1990.')
 if n==110:row.update(nota_edicao='Desambiguação: The Diplomat, série Netflix de 2023, criada por Debora Cahn; não a série britânica homônima de Ben Richards.')
 if n==152:row.update(nota_edicao='Desambiguação documental: Nausheen Khan, Índia, 2023; não Land of Dreams, ficção de Shirin Neshat.')
 if n==74:row['titulo_original']='Anatomie d’une chute'
 rows.append(row)
process(batch,rows)
