"""CC-J2 — final human review for the ratification dossier (DATA, not engine code). Re-reads the 30 pinned CC-J2 decisions against the
official sources; nothing here is approved. Group/decision may change from the preliminary review (CC_J2_DECISIONS.json stays pinned:
the change is recorded here, never written back).
"""
# LF-normalized sha256 of the batch as reviewed in CC-J2 (nothing may enter or leave silently).
PINS = {
    'CC_J2_DECISIONS.json': 'fbf64e06f92de1887034a57ef7aeed7899d0c30543216554e36b7f7740e82ec3',
    'CC_J2_REVIEW.md': '3cfa0b7c7be248c8b75c27972012c3415e9096ad969461d83fbdbe6cb34dbbdf',
    'CC_J2_SCALE_METRICS.json': '25b57717d5d75b484d033c873201af5bf1f83386683736ab18e3aa1d9dd8cb22',
    'CC_J2_SIMULATION_REPORT.md': '064eaaab6a2464ff018c9366d60ac6f45d7167fbdcbac9600a6be2d486f20cbe',
    'cc_j2/CC_J2_BACKLOG.json': '5d89a3d955798af937aff019827649b280f8bde7de2851e236a7005a58adc375',
    'cc_j2_simulation/CC_J2_SIMULATION_MANIFEST.json': '711df552aabcb97cf2e5847958fcf23aca13a6364158380cc1c0271b363d27c5',
    'CC_J2_RATIFICATION_DOSSIER.md': '40a0ccfeb966b18de067f332c6a91dff994c69ef51409ee91d1a5e1e37931a3f',
    'CC_J2_RATIFICATION_DOSSIER.json': 'b8aa96c49649af5aaa3ee97ac4251a5017f881b301b4d85954c45231ef32626c',
    'stj/STJ_SUMULAS_INDEX.json': '2cf0e0b9eefed36e087a822a72e623d5c570b44ebd4b47d8d5bdfa9512761ad5',
    'stj/STJ_PRECEDENTES_INDEX.json': '7f75c17ed83c987c280db0f2ae3652543e3f48ef3ec4aeac9ad1732aa3eee37d',
    'cc_j2/PLANALTO_CC2002_2026-10-18.json': '0529086218e826fb54c597ef28831e21d5ee3cf2e1a6fd3c09dc192a2ad1c52e',
    'cc_j2/STF_Q1_RECHECK.json': '68475e69b4ce1599f1d20a3854d2e4a9bf186df22478dc234675769b5f59a07a',
    'pilot_cc/cc_pilot_evidence.py': 'c6c38d2fad9acf2763e0810577691e3fa546198e4bf888a9df021f1c90c7dfc0',
    'pilot_cc/PORTABILITY_PILOT_CC.json': '6da0bfb45aee25b54720087824c9736ca1a72a60669d92d9f8cd63cac820a1e6',
}

# Official evidence captured in this mission (in addition to the pinned sources).
NEW_EVIDENCE = {
    'STF_T1432': dict(org='STF', url='https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=1432',
                      sha256='c85347eab3e7ea563efa7ef384ddba3da0a6c26b0fe54dc14e22d4267cb5a2f7', accessed_on='2026-10-18',
                      method='navegador embutido (innerText do body)',
                      proves='Tema 1432 (RE 1563850, eficácia do título coletivo do sindicato quanto à base territorial): "Não há repercussão geral '
                             '(questão infraconstitucional)"; Trânsito em Julgado - 18/09/2026.'),
    'STJ_PDF_642': dict(org='STJ', url='https://processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf',
                        sha256='bf92bdb1ae0d257379cdd8c5009e30152e6a91ca8a2dc631b15122962ec6e2a0', accessed_on='2026-10-18',
                        method='texto do PDF oficial já baixado (pdftotext); mesmo sha do índice STJ_SUMULAS_INDEX',
                        proves='Súmula 642, referências legislativas do próprio STJ: "LEG:FED LEI:010406 ANO:2002 ***** CC-02 ... ART:00012 ART:00943 '
                               'INC:00001 ART:00948 ART:01829 ART:01839".'),
    'PLANALTO_TEXT': dict(org='Planalto', url='https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm',
                          sha256='d44f92f51a443642d4a12a3131d691828ddde4901959d2845ef50a85966b755b', accessed_on='2026-10-18',
                          method='download direto (o mesmo da recaptura do CC-J2)',
                          proves='Art. 591: "Destinando-se o mútuo a fins econômicos, presumem-se devidos juros. (Redação dada pela Lei nº 14.905, de '
                                 '2024)". Art. 406: "... os juros serão fixados de acordo com a taxa legal. (Redação dada pela Lei nº 14.905, de 2024)". '
                                 'Arts. 757, 765, 768, 785, 787, 797, 798: "(Revogado pela Lei nº 15.040, de 2024)". Art. 943: sem incisos. Art. 1.238, '
                                 'p.u.: prazo reduzido a dez anos se houver moradia habitual "ou nele realizado obras ou serviços de caráter produtivo".'),
}

_A = 'aprovar como proposto'
_C = 'rejeitar'
_D = 'manter pendente'

# id -> final review. relation: DIRECT | EXCEPTION | EXCLUSION_CONTEXT | TRANSITION | CONTEXTUAL | NONE.
FINAL = {
    # ---------------------------------- GREEN (re-confirmed) ----------------------------------
    'CCJ2-02': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.835'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='O enunciado nomeia o art. 835 (exoneração do fiador por notificação).', superseded='não (vigente no PDF oficial)'),
    'CCJ2-04': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.405'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='A tese fixa o termo inicial dos juros de mora com base no art. 405.', superseded='não (trânsito em julgado)'),
    'CCJ2-05': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.50'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='Requisitos da desconsideração (Teoria Maior) "nos termos exigidos pelo art. 50".',
                    superseded='não; julgado em 2026, depois da redação da Lei 13.874/2019'),
    'CCJ2-07': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1829'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='A tese manda aplicar o regime do art. 1.829; o Planalto anota o RE 646.721 no art. 1.829.',
                    superseded='não; ficha STF_RG_498.TXT já no cartão (novo alvo do mesmo precedente, não duplicata)'),
    'CCJ2-14': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.286'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='Cessão dos créditos do empréstimo compulsório "notadamente [pelo] art. 286".', superseded='não (trânsito em julgado)'),
    'CCJ2-16': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.191'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='Delimita a renúncia tácita à prescrição do art. 191.', superseded='não (trânsito em julgado)'),
    'CCJ2-17': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1829'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='Mesma tese do Tema 498 em tema próprio (questão diferente: união heteroafetiva); o Planalto anota o RE 878.694 no art. 1.829.',
                    superseded='não; ficha STF_RG_809.TXT já no cartão'),
    'CCJ2-23': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.206:PAR.3:INC.III'], temporal='CURRENT', confidence='HIGH',
                    relation='DIRECT', material='Dividendos prescrevem em três anos "nos termos do art. 206, § 3º, inciso III".',
                    superseded='não; o Tema 309 (mesma tese) fica como duplicata (RED)'),
    'CCJ2-25': dict(group='GREEN', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.354'], temporal='CURRENT', confidence='HIGH', relation='DIRECT',
                    material='Aplica ao SFH a imputação do art. 354, salvo cláusula em contrário.', superseded='não (trânsito em julgado)'),
    # ---------------------------------- YELLOW (individual decision) ----------------------------------
    'CCJ2-01': dict(group='YELLOW', decision='MULTI_TARGET_RECOMMENDED', targets=['CC2002:ART.1208', 'CC2002:ART.1255'], temporal='CURRENT',
                    confidence='HIGH', relation='DIRECT',
                    material='Dois pontos distintos: (i) ocupação de bem público é detenção (art. 1.208: atos de mera tolerância não induzem posse); '
                             '(ii) não há indenização por acessões (o art. 1.255 dá indenização ao construtor de boa-fé, aqui afastada). Benfeitorias e '
                             'retenção (art. 1.219) também são afastadas, mas o STJ não referencia esse artigo. O art. 1.198 (detentor por dependência) '
                             'não é o caso.',
                    risk='Baixo. Duas referências do STJ, dois vínculos materiais reais; o 1.219 fica de fora por falta de referência oficial.',
                    alts=dict(A=_A + ' (1.208 e 1.255)', B='só o art. 1.208 (detenção)', C=_C, D=_D), reco='A',
                    ficha='Explicar os dois efeitos: detenção (1.208) e ausência de indenização por acessões (1.255) e benfeitorias.'),
    'CCJ2-06': dict(group='YELLOW', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.202:PAR.UNICO'], temporal='HISTORICAL_BUT_RELEVANT',
                    confidence='MEDIUM', relation='DIRECT',
                    material='Prescrição intercorrente nas execuções do CPC/73 "conforme interpretação extraída do art. 202, parágrafo único". '
                             'Utilidade atual: execuções antigas ainda em curso e a leitura do reinício do prazo; para o CPC/2015 vale o art. 921.',
                    risk='Médio: leitor aplicar a regra a execuções do CPC/2015. Primeiro IAC do aparelho: o rótulo "IAC n" existe no firmware, '
                         'mas não foi validado fisicamente (requisito de teste físico futuro, não impede a ratificação jurídica).',
                    alts=dict(A=_A + ' (HISTORICAL_BUT_RELEVANT, com nota CPC/73)', B='—', C=_C + ' (só histórico)', D=_D), reco='A',
                    ficha='"Aplica-se às execuções regidas pelo CPC/1973; sob o CPC/2015, ver art. 921."'),
    'CCJ2-08': dict(group='YELLOW', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.206:PAR.5:INC.I'], temporal='CURRENT', confidence='HIGH',
                    relation='DIRECT', changed='MULTI_TARGET (206, § 5º, I + 2.028) → PROMOTE só no 206, § 5º, I',
                    material='Para contratos sob o CC/2002 a tese aplica diretamente o art. 206, § 5º, I. O art. 2.028 aparece como ressalva '
                             '("sem embargo da norma de transição") e já tem a Súmula 547 (CC-J1) com a mesma função: vincular de novo não acrescenta '
                             'informação.',
                    risk='Baixo. Tema da Primeira Seção (crédito rural cedido à União, execução fiscal); a ficha deve dizer o contexto.',
                    alts=dict(A='aprovar como proposto originalmente (206, § 5º, I + 2.028)', B='aprovar só o art. 206, § 5º, I', C=_C, D=_D), reco='B',
                    ficha='Contexto: crédito rural, execução fiscal; 20 anos (CC/1916) ou 5 anos (CC/2002).'),
    'CCJ2-09': dict(group='YELLOW', decision='REALLOCATE_RECOMMENDED', targets=['CC2002:ART.943'], temporal='CURRENT', confidence='HIGH',
                    relation='DIRECT', source_anomaly='STJ_REFERENCE_TO_NONEXISTENT_DISPOSITIVO: o PDF oficial referencia "ART:00943 INC:00001", '
                                                      'mas o art. 943 não tem incisos (texto compilado do Planalto). Erro estrutural/editorial da fonte.',
                    material='Transmissibilidade do direito à indenização por dano moral: o art. 943 ("transmitem-se com a herança") é o fundamento '
                             'direto. 1.829/1.839 só identificam os herdeiros; 948 trata do homicídio; o 12 é referência oficial, mas sobre tutela '
                             'da personalidade.',
                    risk='Baixo para o vínculo; a anomalia da fonte fica registrada e nenhum alvo inexistente é criado.',
                    alts=dict(A=_A + ' (realocar para o art. 943)', B='943 e também o art. 12', C=_C, D=_D), reco='A'),
    'CCJ2-11': dict(group='YELLOW', decision='REALLOCATE_RECOMMENDED', targets=['CC2002:ART.1238:PAR.UNICO'], temporal='CURRENT', confidence='HIGH',
                    relation='DIRECT',
                    material='A tese usa o prazo de 10 anos "conforme parágrafo único do art. 1.238", e o fundamento é o requisito especial do p.u. '
                             '("obras ou serviços de caráter produtivo"), equiparado às obras do Poder Público. Não trata do caput (15 anos).',
                    risk='Baixo; tema de direito público (desapropriação indireta) num dispositivo de usucapião: a ficha deve dizer isso.',
                    alts=dict(A=_A + ' (1.238, p.u.)', B='manter no artigo (caput)', C=_C, D=_D), reco='A'),
    'CCJ2-18': dict(group='YELLOW', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1210:PAR.2'], temporal='CURRENT', confidence='MEDIUM',
                    relation='EXCEPTION',
                    material='Exceção: o § 2º veda a exceção de domínio na possessória; a súmula permite que o ente público que intervém alegue '
                             'até o domínio. Útil justamente por limitar a leitura literal do dispositivo.',
                    risk='Médio: a ficha precisa dizer "exceção", não concordância com o texto.',
                    alts=dict(A=_A + ' (como EXCEPTION)', B='—', C=_C + ' (processual)', D=_D), reco='A',
                    ficha='"Exceção ao art. 1.210, § 2º: o ente público pode deduzir o domínio ao intervir na possessória entre particulares."'),
    'CCJ2-20': dict(group='YELLOW', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1641:INC.II'], temporal='CURRENT', confidence='MEDIUM',
                    relation='DIRECT', changed='temporal NEEDS_REVIEW → CURRENT (compatibilidade com o Tema 1236 verificada)',
                    material='Compatível com o Tema 1236: o STF manteve a separação do art. 1.641, II como regime legal que vale "à falta de convenção" '
                             '(o caso concreto a aplicou); a súmula rege a união estável sem pacto e acrescenta a comunicação dos aquestos com '
                             'esforço comum. Não é duplicata: o Tema 1236 trata do afastamento por escritura, a súmula, do regime aplicável sem ela.',
                    risk='Médio: sem a ressalva, a ficha faria o regime parecer cogente.',
                    alts=dict(A=_A + ' (ficha com a ressalva do Tema 1236)', B='—', C=_C + ' (superada)', D=_D), reco='A',
                    ficha='"Após o Tema 1236/STF (2024), o regime pode ser afastado por escritura pública; sem pacto, aplica-se esta súmula."'),
    'CCJ2-21': dict(group='YELLOW', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.354'], temporal='CURRENT', confidence='MEDIUM',
                    relation='EXCLUSION_CONTEXT',
                    material='Jurisprudência negativa: delimita o campo do art. 354 (não se aplica à compensação tributária; originou a Súmula 464/STJ). '
                             'Útil ao lado do Tema 426 (que aplica o art. 354 ao SFH): o leitor vê onde a regra vale e onde não vale.',
                    risk='Médio: não pode parecer interpretação positiva da regra civil.',
                    alts=dict(A=_A + ' (EXCLUSION_CONTEXT, com nota editorial)', B='—', C=_C + ' (tributário)', D=_D), reco='A',
                    ficha='"Exclusão: a imputação do art. 354 NÃO se aplica à compensação tributária."'),
    'CCJ2-22': dict(group='YELLOW', decision='PROMOTE_PROVISIONAL_RECOMMENDED', targets=['CC2002:ART.76:PAR.UNICO'], temporal='CURRENT',
                    confidence='MEDIUM', relation='DIRECT', provisional=dict(
                        registry='J2_PROVISIONAL_REGISTRY (se ratificado)', reason='STJ: "Acórdão Publicado - RE Pendente" (dataset de 2026-10-09)',
                        trigger='confirmar no STJ a situação "Trânsito em Julgado"; o STF já negou repercussão geral no Tema 1432 (trânsito em '
                                '18/09/2026), então o RE não deve alterar a tese'),
                    material='"Domicílio necessário (art. 76, parágrafo único)" do servidor define o alcance do título coletivo do sindicato.',
                    risk='Médio e diminuindo: o obstáculo no STF acabou (sem RG), mas o dataset do STJ ainda não registra o trânsito.',
                    alts=dict(A=_A + ' (PROVISIONAL, com gatilho)', B='—', C=_C, D=_D + ' até o STJ registrar o trânsito'), reco='A'),
    'CCJ2-29': dict(group='YELLOW', decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.206:PAR.3:INC.IV'], temporal='CURRENT', confidence='HIGH',
                    relation='DIRECT', changed='MULTI_TARGET (206, § 3º, IV + 2.028) → PROMOTE só no 206, § 3º, IV',
                    material='O prazo trienal do art. 206, § 3º, IV para a nulidade de reajuste de plano de saúde é informação própria (setor). O art. '
                             '2.028 cumpre a mesma função da Súmula 547 já no CC-J1: não multiplicar vínculos de transição.',
                    risk='Baixo.', alts=dict(A='aprovar como proposto originalmente (206, § 3º, IV + 2.028)', B='aprovar só o art. 206, § 3º, IV',
                                             C=_C, D=_D), reco='B'),
    # ---------------------------------- RED (do not ratify) ----------------------------------
    'CCJ2-03': dict(group='RED', decision='REJECT_NOT_MATERIAL_RECOMMENDED', targets=[], temporal='CURRENT', confidence='HIGH', relation='NONE',
                    changed='YELLOW CONTEXTUAL → RED',
                    material='O art. 1.639, § 2º aparece só como exemplo ("e.g.") na modulação do ARE 1309642; não é interpretado e não é necessário '
                             'para compreender a tese, que já está no art. 1.641, II (CCJ1-06).',
                    reopen='Se STF ou STJ decidirem a mudança de regime (art. 1.639, § 2º) de casamentos com maiores de 70 anos.'),
    'CCJ2-13': dict(group='RED', decision='REJECT_NOT_MATERIAL_RECOMMENDED', targets=[], temporal='CURRENT', confidence='MEDIUM', relation='NONE',
                    changed='YELLOW CONTEXTUAL → RED',
                    material='A fidelidade aparece como valor do "ordenamento jurídico-constitucional" (monogamia), não como interpretação do art. '
                             '1.566, I. A ratio é constitucional e previdenciária; a mesma razão levou o usuário a recusar o art. 1.727 no CC-J1. A '
                             'evidência não é forte o bastante para um novo vínculo contextual.',
                    reopen='Se surgir precedente que interprete o dever de fidelidade do art. 1.566, I como regra civil.'),
    'CCJ2-28': dict(group='RED', decision='REJECT_NOT_MATERIAL_RECOMMENDED', targets=[], temporal='HISTORICAL_BUT_RELEVANT', confidence='MEDIUM',
                    relation='NONE', changed='YELLOW PROMOTE → RED',
                    material='Predominantemente processual (honorários de embargos e de execução, CPC/73; o CPC/2015, art. 85, § 14, resolve a '
                             'questão). O art. 368 entra só como premissa (falta de reciprocidade); o leitor do art. 368 ganha pouco.',
                    reopen='Se surgir precedente civil sobre o requisito de reciprocidade da compensação.'),
    'CCJ2-10': dict(group='RED', decision='REJECT_SUPERSEDED_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', relation='NONE',
                    material='Repercussão geral negada (questão infraconstitucional), sem tese de mérito; a matéria foi decidida com RG no Tema 932, '
                             'já no CC-J1 (art. 927, p.u.).', reopen='Nunca como precedente de mérito.'),
    'CCJ2-12': dict(group='RED', decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', relation='NONE',
                    material='A tese afasta o limite "do art. 591 c/c o art. 406". A Lei 14.905/2024 reescreveu os dois: o art. 591 só presume juros '
                             'e o art. 406 remete à taxa legal. O limite discutido não existe mais no texto.',
                    reopen='Se o STJ reafirmar a tese sob a redação da Lei 14.905/2024.'),
    'CCJ2-15': dict(group='RED', decision='REJECT_NOT_MATERIAL_RECOMMENDED', targets=[], temporal='CURRENT', confidence='MEDIUM', relation='NONE',
                    material='Núcleo é a taxa média do Bacen nos contratos bancários; arts. 112/122/170 são cânones gerais e 406/591 foram reescritos '
                             'pela Lei 14.905/2024.', reopen='Se um precedente fundamentar a taxa média no art. 170 ou no art. 122.'),
    'CCJ2-19': dict(group='RED', decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', relation='NONE',
                    material='A referência ao art. 591 era à "capitalização anual"; a Lei 14.905/2024 tirou a capitalização do texto.',
                    reopen='Se a capitalização voltar ao CC ou o STJ vincular a súmula à redação nova.'),
    'CCJ2-24': dict(group='RED', decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', relation='NONE',
                    material='Mesma razão da Súmula 539 (pactuação da capitalização contra a redação antiga do art. 591).', reopen='Idem à Súmula 539.'),
    'CCJ2-26': dict(group='RED', decision='DUPLICATE_RECOMMENDATION', targets=[], temporal='CURRENT', confidence='HIGH', relation='NONE',
                    material='Duplicata material do Tema 308: questão submetida e tese firmada idênticas, caractere por caractere, no dataset oficial '
                             '(mesmo julgamento, outro recurso).', reopen='Só se o usuário quiser registrar os dois temas.'),
    'CCJ2-27': dict(group='RED', decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', relation='NONE',
                    material='Arts. 757, 765 e 785 revogados pela Lei 15.040/2024 (o contrato de seguro saiu do CC).',
                    reopen='Se o STJ reafirmar a súmula sob a Lei 15.040/2024 (o vínculo iria para a lei nova, fora do CC).'),
    'CCJ2-30': dict(group='RED', decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', relation='NONE',
                    material='Arts. 797 e 798 revogados pela Lei 15.040/2024.', reopen='Idem à Súmula 465.'),
}
