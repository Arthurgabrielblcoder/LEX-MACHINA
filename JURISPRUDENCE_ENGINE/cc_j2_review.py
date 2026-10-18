"""CC-J2 — human reading of the official evidence (DATA, not engine code). One entry per selected precedent; validated fail-closed by
batch_engine.apply_review. Nothing here is approved: every item stays AWAITING_USER_RATIFICATION.
Fields: decision, targets (final proposal), temporal, confidence, group (GREEN/YELLOW/RED), risk, motive (<= 2 sentences), human (judgment
needed even if the rule would allow GREEN), yellow = (problem, favor, risk, option B, recommendation), reopen (RED), ccj1 = interaction with
the frozen CC-J1 (kind, note) — never a change to it.
"""
_SAME = 'CC_J1_SAME_PRECEDENT_NEW_TARGET'
_COMPAT = 'CC_J1_COMPATIBLE_INTERACTION'

REVIEW = {
    # ------------------------------ GREEN candidates ------------------------------
    'STJ:SUMULA:656': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.835'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                           risk='BAIXO', motive='O enunciado nomeia o art. 835: a exoneração do fiador depende da notificação ali prevista.'),
    'STJ:REPETITIVO:1133': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.405'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                                risk='BAIXO', motive='Tese fixa o termo inicial dos juros de mora "(art. 405 do Código Civil e art. 240 do CPC)"; '
                                                     'art. 405 vigente, sem nota de redação.'),
    'STJ:REPETITIVO:1210': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.50'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                                risk='BAIXO', motive='Desconsideração exige abuso "nos termos exigidos pelo art. 50 do Código Civil (Teoria Maior)"; '
                                                     'julgado em 2026, depois da redação da Lei 13.874/2019.'),
    'STF:RG:498': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1829'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                       risk='BAIXO', motive='A tese manda aplicar "o regime do art. 1.829 do CC/2002"; o Planalto anota o RE 646.721 no próprio art. 1.829.',
                       ccj1=dict(kind=_SAME, note='Mesmo precedente do CCJ1-03 (art. 1.790); novo alvo, mesma ficha STF_RG_498.TXT já no cartão. '
                                                  'O CC-J1 não muda.')),
    'STF:RG:809': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1829'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                       risk='BAIXO', motive='Mesma tese do Tema 498, tema próprio (união heteroafetiva); o Planalto anota o RE 878.694 no art. 1.829.',
                       ccj1=dict(kind=_SAME, note='Mesmo precedente do CCJ1-04; ficha STF_RG_809.TXT já no cartão.')),
    'STJ:REPETITIVO:368': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.286'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                               risk='BAIXO', motive='Créditos do empréstimo compulsório podem ser cedidos, incidindo "notadamente o art. 286 do Código '
                                                    'Civil" (cessão de crédito).'),
    'STJ:REPETITIVO:1109': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.191'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                                risk='BAIXO', motive='Tese delimita a renúncia tácita à prescrição "(art. 191 do Código Civil)" no reconhecimento '
                                                     'administrativo de direito.'),
    'STJ:REPETITIVO:308': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.206:PAR.3:INC.III'], temporal='CURRENT', confidence='HIGH',
                               group='GREEN', risk='BAIXO', motive='Dividendos da subscrição complementar CRT prescrevem em três anos "nos termos do '
                                                                   'art. 206, § 3º, inciso III, do Código Civil de 2002".'),
    'STJ:REPETITIVO:426': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.354'], temporal='CURRENT', confidence='HIGH', group='GREEN',
                               risk='BAIXO', motive='No SFH aplica-se, salvo cláusula em contrário, "a regra de imputação prevista no art. 354 do Código '
                                                    'Civil de 2002".'),
    # ------------------------------ YELLOW (review individually) ------------------------------
    'STJ:SUMULA:619': dict(decision='MULTI_TARGET_RECOMMENDED', targets=['CC2002:ART.1208', 'CC2002:ART.1255'], temporal='CURRENT',
                           confidence='HIGH', group='YELLOW', risk='BAIXO',
                           motive='Ocupação indevida de bem público é mera detenção (art. 1.208), sem indenização por acessões (art. 1.255); dois alvos.',
                           yellow=('Dois alvos: o fundamento (1.208) e o dispositivo cuja indenização a súmula afasta (1.255).',
                                   'Súmula 619 (Corte Especial, 24/10/2018); o STJ referencia CC 1.208 e 1.255 (e CF 191).',
                                   'Baixo; benfeitorias (art. 1.219) não são referenciadas pelo STJ.', 'vincular só no art. 1.208',
                                   'A — 1.208 e 1.255.')),
    'STF:RG:1236': dict(decision='CONTEXTUAL_RECOMMENDED', targets=['CC2002:ART.1639:PAR.2'], temporal='CURRENT', confidence='MEDIUM',
                        group='YELLOW', risk='MÉDIO', human=True,
                        motive='A ementa cita o art. 1.639, § 2º como exemplo de mudança consensual de regime para situações já constituídas; a tese '
                               'não o nomeia.',
                        yellow=('Relação contextual: o § 2º aparece na modulação ("e.g."), não na tese.',
                                'ARE 1309642 (Pleno, 01/02/2024), ementa item 10 e "atos normativos citados: arts. 1.641, II; e 1.639, § 2º".',
                                'Leitor pode entender que o tema decidiu a mudança de regime; não decidiu.', 'não vincular (fundamento lateral)',
                                'A — 1.639, § 2º como contextual, com a nota de modulação na ficha.'),
                        ccj1=dict(kind=_SAME, note='Mesmo precedente do CCJ1-06 (art. 1.641, II); novo alvo; ficha STF_RG_1236.TXT já no cartão.')),
    'STJ:IAC:1': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.202:PAR.UNICO'], temporal='HISTORICAL_BUT_RELEVANT', confidence='MEDIUM',
                      group='YELLOW', risk='MÉDIO',
                      motive='Prescrição intercorrente "conforme interpretação extraída do art. 202, parágrafo único, do Código Civil de 2002", '
                             'mas só nas causas regidas pelo CPC/73.',
                      yellow=('Tese restrita às execuções regidas pelo CPC/73 (hoje vale o art. 921 do CPC/2015).',
                              'IAC 1 (Segunda Seção, 27/06/2018; RG STF 1162 correlata): tese nomeia o art. 202, parágrafo único.',
                              'Aplicação indevida a execuções sob o CPC/2015.', 'rejeitar como temporalmente restrito',
                              'A — 202, p.u., com a restrição ao CPC/73 na ficha. Primeiro IAC do aparelho: rótulo "IAC 1" sem validação física.')),
    'STJ:REPETITIVO:639': dict(decision='MULTI_TARGET_RECOMMENDED', targets=['CC2002:ART.206:PAR.5:INC.I', 'CC2002:ART.2028'],
                               temporal='HISTORICAL_BUT_RELEVANT', confidence='MEDIUM', group='YELLOW', risk='MÉDIO',
                               motive='Crédito rural sob o CC/2002 prescreve em 5 anos (art. 206, § 5º, I); sob o CC/1916, 20 anos, com a transição '
                                      'do art. 2.028.',
                               yellow=('Dois alvos, um de transição; tema da Primeira Seção (crédito rural cedido à União, execução fiscal).',
                                       'Tese nomeia o art. 206, § 5º, I e "a norma de transição prevista no art. 2.028 do CC/2002".',
                                       'Alvos já cobertos pela Súmula 547 (CC-J1): risco de lista redundante, não de conflito.',
                                       'vincular só no art. 206, § 5º, I', 'A — 206, § 5º, I e 2.028 (nota temporal na ficha).'),
                               ccj1=dict(kind=_COMPAT, note='Alvos com a Súmula 547 (CCJ1-25), mesma solução de prazo e transição: coerente.')),
    'STJ:SUMULA:642': dict(decision='REALLOCATE_RECOMMENDED', targets=['CC2002:ART.943'], temporal='CURRENT', confidence='MEDIUM', group='YELLOW',
                           risk='MÉDIO', human=True,
                           motive='Transmissão do direito à indenização por dano moral com a morte: núcleo no art. 943; a referência "943, I" do STJ '
                                  'não existe no índice (o artigo não tem incisos).',
                           yellow=('Normalização de alvo (943, I → 943) e escolha entre cinco referências oficiais (12, 943, 948, 1.829, 1.839).',
                                   'Súmula 642 (Corte Especial, 02/12/2020): "transmite-se com o falecimento do titular"; art. 943: "transmitem-se com a herança".',
                                   'Arts. 1.829/1.839 só dizem quem são os herdeiros; art. 948 trata de homicídio.', 'acrescentar o art. 12',
                                   'A — 943 (a referência ao art. 12 fica para lote futuro).')),
    'STJ:REPETITIVO:1019': dict(decision='REALLOCATE_RECOMMENDED', targets=['CC2002:ART.1238:PAR.UNICO'], temporal='CURRENT', confidence='HIGH',
                                group='YELLOW', risk='BAIXO',
                                motive='Desapropriação indireta prescreve em 10 anos "conforme parágrafo único do art. 1.238 do CC"; o adaptador pegou '
                                       'só o artigo.',
                                yellow=('Realocação artigo → parágrafo único (o adaptador não lê "parágrafo único do art.").',
                                        'Tema 1019 (Primeira Seção, 12/02/2020): prazo de 10 anos do art. 1.238, parágrafo único.',
                                        'Tema de direito público num dispositivo de usucapião.', 'manter no artigo', 'A — 1.238, p.u.')),
    'STF:RG:529': dict(decision='CONTEXTUAL_RECOMMENDED', targets=['CC2002:ART.1566:INC.I'], temporal='CURRENT', confidence='MEDIUM',
                       group='YELLOW', risk='MÉDIO', human=True,
                       motive='A tese invoca "o dever de fidelidade e a monogamia"; a ementa cita o art. 1.566, I.',
                       yellow=('Relação por fundamento (dever de fidelidade), não pelo dispositivo julgado.',
                               'Tese do Tema 529: "em virtude da consagração do dever de fidelidade e da monogamia"; ementa do RE 1045273: "1.566, I".',
                               'No CC-J1 o usuário recusou o art. 1.727 como alvo adicional deste tema (fundamento).',
                               'não vincular (coerente com a recusa do 1.727)', 'D — decisão do usuário; recomendação fraca de A.'),
                       ccj1=dict(kind=_SAME, note='Mesmo precedente do CCJ1-05 (art. 1.723, § 1º); o 1.566, I nunca foi apresentado no CC-J1. '
                                                  'Ficha STF_RG_529.TXT já no cartão.')),
    'STJ:SUMULA:637': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1210:PAR.2'], temporal='CURRENT', confidence='MEDIUM',
                           group='YELLOW', risk='MÉDIO', human=True,
                           motive='O ente público pode deduzir até o domínio na possessória entre particulares: exceção ao art. 1.210, § 2º.',
                           yellow=('Súmula de exceção e em parte processual (intervenção do ente público).',
                                   'Súmula 637 (Corte Especial, 06/11/2019); o STJ referencia CC 1.210, § 2º (e CPC/2015, 557).',
                                   'Leitor tomar a exceção como regra geral.', 'rejeitar como processual', 'A — 1.210, § 2º.')),
    'STJ:SUMULA:655': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.1641:INC.II'], temporal='NEEDS_REVIEW', confidence='MEDIUM',
                           group='YELLOW', risk='MÉDIO', human=True,
                           motive='União estável de septuagenário: separação obrigatória, comunicando-se os aquestos com esforço comum; precisa ser '
                                  'lida junto com o Tema 1236 (2024).',
                           yellow=('Compatibilidade com o Tema 1236, que tornou o art. 1.641, II norma dispositiva.',
                                   'Súmula 655 (Segunda Seção, 09/11/2022); o Tema 1236 mantém o regime "à falta de convenção" (caso concreto aplicou-o).',
                                   'Ficha sem a ressalva do Tema 1236 induziria a ler o regime como cogente.', 'rejeitar como superada',
                                   'A — 1.641, II, com a ressalva do Tema 1236 na ficha.'),
                           ccj1=dict(kind=_COMPAT, note='Responde ao alerta do dossiê do CC-J1 (item 6): a súmula não foi superada; rege o caso sem '
                                                        'pacto. O vínculo do Tema 1236 no CC-J1 não muda.')),
    'STJ:REPETITIVO:381': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.354'], temporal='CURRENT', confidence='MEDIUM', group='YELLOW',
                               risk='MÉDIO', human=True,
                               motive='Tese de exclusão: a imputação do art. 354 não se aplica à compensação tributária (originou a Súmula 464/STJ).',
                               yellow=('Relação de exclusão, em tema tributário.',
                                       'Tema 381 (Primeira Seção, 09/06/2010): "a regra de imputação ... do art. 354 do Código Civil não se aplica".',
                                       'Ao lado do Tema 426 (que aplica o art. 354 ao SFH), o leitor precisa ver os dois sentidos.',
                                       'rejeitar como tributário', 'A — 354 (a ficha diz que é exclusão).')),
    'STJ:REPETITIVO:1130': dict(decision='PROMOTE_PROVISIONAL_RECOMMENDED', targets=['CC2002:ART.76:PAR.UNICO'], temporal='CURRENT',
                                confidence='MEDIUM', group='YELLOW', risk='MÉDIO',
                                motive='Título coletivo do sindicato restrito aos que têm domicílio necessário (art. 76, p.u.) na base territorial; '
                                       'RE pendente no STF (RG 1432).',
                                yellow=('Situação "Acórdão Publicado - RE Pendente": tese ainda pode mudar.',
                                        'Tema 1130 (Primeira Seção, 09/10/2024): "domicílio necessário (art. 76, parágrafo único, do Código Civil)".',
                                        'Provisório: exige gatilho de revalidação no trânsito em julgado.', 'aguardar o trânsito em julgado',
                                        'A — provisório, com gatilho na RG 1432.')),
    'STJ:REPETITIVO:587': dict(decision='PROMOTE_RECOMMENDED', targets=['CC2002:ART.368'], temporal='HISTORICAL_BUT_RELEVANT', confidence='MEDIUM',
                               group='YELLOW', risk='MÉDIO', human=True,
                               motive='Honorários de embargos e de execução não se compensam por falta de reciprocidade, pressuposto do art. 368.',
                               yellow=('Contexto processual do CPC/73 (o CPC/2015, art. 85, § 14, já veda a compensação de honorários).',
                                       'Tema 587 (Corte Especial, 18/12/2018): "ausência dos pressupostos do instituto da compensação (art. 368 do CC)".',
                                       'Valor prático hoje limitado.', 'rejeitar como processual/histórico', 'A — 368 (nota de contexto na ficha).')),
    'STJ:REPETITIVO:610': dict(decision='MULTI_TARGET_RECOMMENDED', targets=['CC2002:ART.206:PAR.3:INC.IV', 'CC2002:ART.2028'],
                               temporal='HISTORICAL_BUT_RELEVANT', confidence='MEDIUM', group='YELLOW', risk='MÉDIO',
                               motive='Nulidade de reajuste de plano de saúde: 3 anos (art. 206, § 3º, IV) sob o CC/2002, com a transição do art. 2.028.',
                               yellow=('Dois alvos, um de transição.', 'Tema 610 (Segunda Seção, 10/08/2016) nomeia o art. 206, § 3º, IV e o art. 2.028.',
                                       'Alvos já cobertos pela Súmula 547 (CC-J1).', 'vincular só no art. 206, § 3º, IV',
                                       'A — 206, § 3º, IV e 2.028.'),
                               ccj1=dict(kind=_COMPAT, note='Mesma solução de prazo da Súmula 547 (CCJ1-25): coerente.')),
    # ------------------------------ RED (do not ratify now) ------------------------------
    'STF:RG:920': dict(decision='REJECT_SUPERSEDED_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', group='RED', risk='—',
                       motive='Repercussão geral negada (questão infraconstitucional): não há tese de mérito; a matéria foi depois decidida no Tema 932.',
                       reopen='Nunca como precedente de mérito; o art. 927, p.u. já tem o Tema 932 (CCJ1-07).',
                       ccj1=dict(kind=_COMPAT, note='Confirma o CCJ1-07 (Tema 932 no art. 927, p.u.).')),
    'STJ:REPETITIVO:26': dict(decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', group='RED',
                              risk='—', motive='Afasta o limite "do art. 591 c/c o art. 406"; a Lei 14.905/2024 reescreveu os dois artigos e o limite não '
                                               'existe mais no texto.',
                              reopen='Se o STJ reafirmar a tese sob a redação da Lei 14.905/2024.'),
    'STJ:SUMULA:530': dict(decision='REJECT_NOT_MATERIAL_RECOMMENDED', targets=[], temporal='CURRENT', confidence='MEDIUM', group='RED', risk='—',
                           motive='Núcleo é a taxa média do Bacen nos contratos bancários; arts. 112/122/170 são cânones gerais e 406/591 foram '
                                  'reescritos em 2024.',
                           reopen='Se surgir precedente que fundamente a taxa média na conversão (art. 170) ou na condição potestativa (art. 122).'),
    'STJ:SUMULA:539': dict(decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', group='RED',
                           risk='—', motive='A referência ao art. 591 era à "capitalização anual"; a Lei 14.905/2024 tirou a capitalização do texto.',
                           reopen='Se a capitalização voltar ao CC ou o STJ vincular a súmula à redação nova.'),
    'STJ:SUMULA:541': dict(decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', group='RED',
                           risk='—', motive='Mesmo caso da Súmula 539: pactuação da capitalização contra a antiga redação do art. 591.',
                           reopen='Idem à Súmula 539.'),
    'STJ:SUMULA:465': dict(decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', group='RED',
                           risk='—', motive='Arts. 757, 765 e 785 revogados pela Lei 15.040/2024 (contrato de seguro saiu do CC).',
                           reopen='Se o STJ reafirmar a súmula sob a Lei 15.040/2024 (o vínculo iria para a lei nova, fora do CC).'),
    'STJ:SUMULA:610': dict(decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', targets=[], temporal='SUPERSEDED', confidence='HIGH', group='RED',
                           risk='—', motive='Arts. 797 e 798 revogados pela Lei 15.040/2024.', reopen='Idem à Súmula 465.'),
    'STJ:REPETITIVO:309': dict(decision='DUPLICATE_RECOMMENDATION', targets=[], temporal='CURRENT', confidence='HIGH', group='RED', risk='—',
                               motive='Questão e tese idênticas às do Tema 308 (mesmo julgamento, outro recurso): um único vínculo basta.',
                               reopen='Se o usuário preferir registrar os dois temas, como no par 498/809 (lá as questões eram diferentes).'),
}

BATCH_NOTES = dict(
    CCJ1_09='Tema 1194 continua PENDING_HUMAN_REVIEW: nenhuma fonte oficial nova liga o tema ao art. 206-A (Planalto sem anotação; '
            'dataset do STJ sem tema sobre o art. 206-A).',
    CCJ1_30='Súmula 609 continua PENDING_TEMPORAL_REVALIDATION: nenhuma decisão do STJ posterior à Lei 15.040/2024, nenhuma revisão ou '
            'cancelamento no PDF oficial nem no dataset de precedentes qualificados.',
    CC_J1_REVALIDATION_REQUIRED='0 — interações encontradas são todas compatíveis (Súmula 655 × Tema 1236; Temas 610/639 × Súmula 547; '
                                'Tema 920 × Tema 932) ou novos alvos de precedentes já publicados.',
    CF_MATERIALIZATION_PENDING='9 relações da CF ratificadas e não instaladas (Batch10 6 + Súmulas 203/403 STJ 3): fila separada, não '
                               'pesquisada nem tocada no CC-J2.')
