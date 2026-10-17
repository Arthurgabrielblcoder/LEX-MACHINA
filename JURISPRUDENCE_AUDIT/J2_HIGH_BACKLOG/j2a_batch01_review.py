"""J2A BATCH01 — legal review of the 10 selected HIGH candidates (official sources only; 2026-10-16). Data module, imported by
../build_j2a_batch01.py. Claude's review, AWAITING_USER_RATIFICATION. Nothing here is materialized.

Sources: STF portal / jurisprudência (rendered text read in the built-in browser because portal.stf.jus.br answers 403 to automated
clients, the J1.3 "fotografia por navegador" precedent; sha256 = rendered innerText) and the Planalto compiled CF (direct download).
"""

ACCESSED = '2026-10-16'
SOURCES = {
    'P1': dict(tier='A', org='Presidência da República (Planalto)', title='Constituição Federal — texto compilado (com redações anteriores e anotações "Vide ADI")',
               identifier='constituicao.htm', url='https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm', accessed_on=ACCESSED,
               method='download direto (curl)', snapshot_sha256='51ac764ae9b5e417897bea83d9a4e108b941ed7226fce23e9a56251236fc17cb',
               proves='Origem das 10 recomendações (CANONICAL_VIGENCY_ANNOTATION). "Vide ADIN 3392" aparece em todo dispositivo incluído ou alterado '
                      'pela EC 45/2004 (art. 5º LXXVIII e § 3º, 92 § 1º, 93 IV, 98 § 1º, 102 § 2º, 114). Art. 100, § 9º tem duas redações: a da EC 62/2009 '
                      '(compensação no momento da expedição; "Vide ADI 4425") e a da EC 113/2021 (vigente; "Vide ADI 7047/7064"). § 12 tem só a redação da '
                      'EC 62/2009. "Vide ADI 7697" em art. 165 § 9º III e § 10, art. 166 §§ 9º a 20 e art. 166-A.'),
    'S1': dict(tier='A', org='STF', title='Jurisprudência — acórdão ADI 3423 (no mesmo sentido: ADI 3392, 3432, 3520)', identifier='ADI 3392',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22ADI%203392%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='e34505f34d27614b43a4acbed26a2af7bed9ed662959e8917bd7c488c01903e8',
               proves='Ementa oficial: EC 45/2004 na parte que deu nova redação ao art. 114, §§ 2º e 3º (mútuo acordo para o dissídio coletivo; MPT '
                      'na greve em atividade essencial). Improcedente, Pleno, j. 29/05/2020, DJe 18/06/2020.'),
    'S2': dict(tier='A', org='STF', title='Portal — ADI 3392 (detalhe e aba Informações)', identifier='ADI 3392 (incidente 2267506)',
               url='https://portal.stf.jus.br/processos/abaInformacoes.asp?incidente=2267506', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='ba74c40c7d38b22919324da516b0bff11f76e95ed669155c409fc074f2424e55',
               proves='Requerente CNPL; Rel. Min. Gilmar Mendes; apenso principal ADI 3423; assunto "Direito do Trabalho | Sentença Normativa"; '
                      'improcedente (sessão virtual 22-28/05/2020); trânsito em julgado 21/08/2020.'),
    'S3': dict(tier='A', org='STF', title='Jurisprudência — acórdãos ADI 4425 (mérito, QO de modulação, ED)', identifier='ADI 4425',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22ADI%204425%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='ac1ee1c771f6d0e57797b81e20fdbb078ae1453f20189f711f3af78ca89f2577',
               proves='Mérito (Pleno, j. 14/03/2013, DJe 19/12/2013, red. p/ acórdão Min. Luiz Fux): inconstitucional o regime de compensação dos §§ 9º e '
                      '10 do art. 100 (EC 62/2009); inconstitucional a correção pela poupança; declaração parcial sem redução de "independentemente '
                      'de sua natureza" do art. 100, § 12. QO (j. 25/03/2015): modulação (TR até 25/03/2015; depois IPCA-E).'),
    'S4': dict(tier='A', org='STF', title='Jurisprudência — acórdão ADI 7064', identifier='ADI 7064',
               url='https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22ADI%207064%22&base=acordaos', accessed_on=ACCESSED,
               method='navegador embutido (innerText)', dom_text_sha256='4d1e398dc576b636f36fcb263c5189eb95ad724c316755ddd838a2c21a2c4e79',
               proves='Ementa (Pleno, Rel. Min. Luiz Fux, j. 01/12/2023, DJe 19/12/2023), item 28: a redação do art. 100, § 9º dada pela EC 113/2021, '
                      'embora diferente da declarada inconstitucional nas ADIs 4425/4357, tem a mesma essência e é incompatível com a Constituição.'),
    'S5': dict(tier='A', org='STF', title='Portal — ADI 7047, aba Decisões', identifier='ADI 7047 (incidente 6318731)',
               url='https://portal.stf.jus.br/processos/abaDecisoes.asp?incidente=6318731', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='d63a00509b6be37c53616c9f905b632fcdcac167d5edd42409abd4475ee2a7df',
               proves='Decisão de julgamento (sessão virtual extraordinária de 30/11/2023): parcialmente procedente; inconstitucionais o art. 100, § 9º da '
                      'CF e o art. 101, § 5º do ADCT, na redação da EC 113/21; interpretação conforme ao art. 100, § 11. Julgada em conjunto com a ADI 7064.'),
    'S6': dict(tier='A', org='STF', title='Portal — ADI 7064, aba Decisões', identifier='ADI 7064 (incidente 6330822)',
               url='https://portal.stf.jus.br/processos/abaDecisoes.asp?incidente=6330822', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='b71b5b660193853058fb78cd70d7ae31063bceddabf9a7f2843efadcfda644b0',
               proves='Decisão de julgamento (30/11/2023): interpretação conforme ao caput do art. 107-A do ADCT (só 2022); incisos II e III e §§ 3º, 5º e 6º '
                      'inconstitucionais; inconstitucionais o art. 100, § 9º da CF e o art. 101, § 5º do ADCT (EC 113/21); interpretação conforme ao art. 100, § 11.'),
    'S7': dict(tier='A', org='STF', title='Portal — ADI 7697, detalhe e aba Decisões', identifier='ADI 7697 (incidente 6997560)',
               url='https://portal.stf.jus.br/processos/abaDecisoes.asp?incidente=6997560', accessed_on=ACCESSED, method='navegador embutido (innerText)',
               dom_text_sha256='2d68ff18bfd6a73276b5c3f5a4a1888a2a5f3da93ecf52198358a627486336bb',
               proves='Requerente PSOL; Rel. Min. Flávio Dino. Liminar referendada por unanimidade (sessão virtual de 16/08/2024; registro de 19/08/2024): '
                      'interpretação conforme, efeitos ex nunc, aos arts. 165 § 9º III e § 10; 166 §§ 9º, 9º-A, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20; e 166-A '
                      '(emendas sem eficiência, transparência e rastreabilidade não podem ser executadas; impositividade não é absoluta). Referendo de '
                      '04/12/2024 sobre "emendas PIX" (plano de trabalho prévio). Mérito pendente (autos conclusos em 16/06/2026).'),
}

NO_DEVICE_RECORD = ('O índice de jurisprudência do aparelho (JURISPRUDENCIA.IDX legado, f85108ba…) só tem Temas de RG (284) e SVs (12); nenhuma ADI. '
                    'Materializar exige definir na J2B um registro e um conteúdo para controle concentrado, compatíveis com o firmware.')

# recommendation_id -> review (only the 10 selected; build fails closed if the selection differs)
REVIEW = {
    'J0-BL-136': dict(precedent='STF:ADI:7697', court='STF', klass='ADI', number='7697', rapporteur='Min. Flávio Dino',
                      judgment='MC referendada pelo Pleno em 16/08/2024 (unânime); mérito pendente', publication='DJE (referendo); registro em 19/08/2024',
                      subject='Emendas parlamentares impositivas: execução condicionada a eficiência, transparência e rastreabilidade',
                      namespace='CF88', namespace_evidence='A decisão nomeia "art. 166, § 9º (EC/126) … todos da Constituição Federal".',
                      target_check='PASS', recommended_target='CF88:ART.166:PAR.9', temporal_version='redação da EC 126/2022 (vigente)',
                      decision='PROMOTE_RECOMMENDED', confidence='HIGH (identidade, alvo e namespace); estabilidade: MEDIUM',
                      provisional=True, sources=['S7', 'P1'],
                      reason='O § 9º está expressamente entre os dispositivos com interpretação conforme na cautelar referendada pelo Pleno. Como o mérito '
                             'está pendente, o vínculo precisa trazer o status "medida cautelar referendada — mérito pendente" e ser revalidado quando o '
                             'mérito for julgado.'),
    'J0-BL-137': dict(precedent='STF:ADI:7697', court='STF', klass='ADI', number='7697', rapporteur='Min. Flávio Dino',
                      judgment='MC referendada pelo Pleno em 16/08/2024 (unânime); mérito pendente', publication='DJE (referendo); registro em 19/08/2024',
                      subject='Emendas parlamentares impositivas: a execução obrigatória do § 11 não é absoluta',
                      namespace='CF88', namespace_evidence='A decisão nomeia "art. 166, § 11 (EC/126) … todos da Constituição Federal".',
                      target_check='PASS', recommended_target='CF88:ART.166:PAR.11', temporal_version='redação da EC 126/2022 (vigente)',
                      decision='PROMOTE_RECOMMENDED', confidence='HIGH (identidade, alvo e namespace); estabilidade: MEDIUM',
                      provisional=True, sources=['S7', 'P1'],
                      reason='O § 11 (execução obrigatória das emendas individuais) é o núcleo da tese "impositividade não absoluta". O alvo é expresso na '
                             'cautelar referendada. Mérito pendente, então vale a mesma exigência de status e revalidação do item anterior.'),
    'J0-BL-080': dict(precedent='STF:ADI:4425', court='STF', klass='ADI', number='4425', rapporteur='Min. Ayres Britto; red. p/ acórdão Min. Luiz Fux',
                      judgment='14/03/2013 (mérito); QO de modulação 25/03/2015', publication='DJe 19/12/2013; QO DJe 04/08/2015',
                      subject='Compensação de precatórios com débitos da Fazenda (EC 62/2009)',
                      namespace='CF88', namespace_evidence='A ementa cita "§§ 9º e 10 do art. 100 da Constituição Federal, incluídos pela EC nº 62/09".',
                      target_check='FAIL_TEMPORAL', recommended_target=None,
                      temporal_version='Julgou o § 9º na redação da EC 62/2009 (compensação no momento da expedição). O § 9º vigente é da EC 113/2021 e '
                                       'tem outro texto.',
                      decision='REJECT_TEMPORAL_MISMATCH', confidence='HIGH', provisional=False, sources=['S3', 'P1', 'S4'],
                      reason='O texto declarado inconstitucional pela ADI 4425 não está mais no § 9º. A política J1.3/J1.4 proíbe vincular uma tese de '
                             'redação histórica ao dispositivo atual de conteúdo diferente. O § 9º atual é coberto pelas ADIs 7047/7064 (J0-BL-081/082), '
                             'que registram a continuidade com a ADI 4425 (ementa da ADI 7064, item 28). Um vínculo da ADI 4425 em nível de artigo, com '
                             'nota temporal, fica para a recomendação J0-BL-075 (art. 100), fora deste lote.',
                      redirect='J0-BL-075 (CF88:ART.100; fora do lote; não decidido aqui)'),
    'J0-BL-081': dict(precedent='STF:ADI:7047', court='STF', klass='ADI', number='7047', rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023 (sessão virtual extraordinária), julgamento conjunto com a ADI 7064', publication='acórdão publicado em 2023',
                      subject='Precatórios — EC 113/2021: encontro de contas do art. 100, § 9º',
                      namespace='CF88', namespace_evidence='A decisão declara inconstitucional o "art. 100, § 9º, da Constituição Federal … com redação '
                                                           'estabelecida pelo art. 1º da EC 113/21".',
                      target_check='PASS', recommended_target='CF88:ART.100:PAR.9', temporal_version='redação da EC 113/2021 (texto vigente no compilado, '
                                                                                                    'declarado inconstitucional)',
                      decision='PROMOTE_RECOMMENDED', confidence='HIGH', provisional=False, sources=['S5', 'S4', 'P1'], joint_judgment_with='STF:ADI:7064',
                      reason='Decisão definitiva de mérito que declara inconstitucional exatamente o § 9º vigente. Alta utilidade: o texto continua no '
                             'compilado, mas não vale. A ADI 7064, julgada em conjunto, também é recomendada; os números são distintos e pesquisáveis '
                             '(mesma lógica do KEEP_BOTH 367/387).'),
    'J0-BL-082': dict(precedent='STF:ADI:7064', court='STF', klass='ADI', number='7064', rapporteur='Min. Luiz Fux',
                      judgment='30/11/2023 (sessão virtual extraordinária); acórdão j. 01/12/2023', publication='DJe 19/12/2023',
                      subject='Precatórios — EC 113 e 114/2021: § 9º, § 11, ADCT 101 § 5º e 107-A',
                      namespace='CF88', namespace_evidence='A decisão declara inconstitucional o "art. 100, § 9º, da Constituição Federal … com redação '
                                                           'estabelecida pelo art. 1º da EC 113/21"; a ementa (item 28) trata do mesmo § 9º.',
                      target_check='PASS', recommended_target='CF88:ART.100:PAR.9', temporal_version='redação da EC 113/2021 (vigente no compilado, '
                                                                                                    'declarado inconstitucional)',
                      decision='PROMOTE_RECOMMENDED', confidence='HIGH', provisional=False, sources=['S6', 'S4', 'P1'], joint_judgment_with='STF:ADI:7047',
                      reason='Mérito definitivo; o § 9º atual é declarado inconstitucional, e a ementa explicita a continuidade com as ADIs 4425/4357. '
                             'É o processo com a ementa publicada mais completa do julgamento conjunto.'),
    'J0-BL-084': dict(precedent='STF:ADI:4425', court='STF', klass='ADI', number='4425', rapporteur='Min. Ayres Britto; red. p/ acórdão Min. Luiz Fux',
                      judgment='14/03/2013 (mérito); QO de modulação 25/03/2015', publication='DJe 19/12/2013; QO DJe 04/08/2015',
                      subject='Atualização de precatórios pela poupança e juros de precatórios tributários (art. 100, § 12)',
                      namespace='CF88', namespace_evidence='A ementa cita a expressão "contida no art. 100, §12, da CF, incluído pela EC nº 62/09".',
                      target_check='PASS', recommended_target='CF88:ART.100:PAR.12',
                      temporal_version='redação da EC 62/2009, que continua sendo a única do § 12 no compilado',
                      decision='PROMOTE_RECOMMENDED', confidence='HIGH', provisional=False, sources=['S3', 'P1'],
                      reason='O texto atual do § 12 é o mesmo julgado: a correção pela poupança é inconstitucional e "independentemente de sua natureza" '
                             'tem declaração parcial sem redução. A modulação da QO (TR até 25/03/2015, depois IPCA-E) deve constar da nota.'),
    'J0-BL-069': dict(precedent='STF:ADI:3392', court='STF', klass='ADI', number='3392', rapporteur='Min. Gilmar Mendes',
                      judgment='29/05/2020 (sessão virtual 22-28/05/2020), improcedente', publication='DJe 18/06/2020',
                      subject='EC 45/2004 — art. 114, §§ 2º e 3º (dissídio coletivo de comum acordo)',
                      namespace='CF88', namespace_evidence='É a CF, mas o dispositivo é o art. 114, §§ 2º e 3º (ementa da ADI 3423, mesmo sentido da 3392).',
                      target_check='FAIL', recommended_target=None, temporal_version=None,
                      decision='REJECT_FALSE_POSITIVE', confidence='HIGH', provisional=False, sources=['S1', 'S2', 'P1'],
                      reason='Falso positivo de anotação: o Planalto põe "Vide ADIN 3392" em todo dispositivo tocado pela EC 45/2004. A ação só '
                             'impugnou o art. 114, §§ 2º e 3º e não tem relação com o art. 92 (§ 1º). É o mesmo padrão do erro J1 (número coincidente, '
                             'objeto diverso). Um eventual vínculo correto (art. 114, § 2º) não faz parte do backlog e não foi criado.'),
    'J0-BL-074': dict(precedent='STF:ADI:3392', court='STF', klass='ADI', number='3392', rapporteur='Min. Gilmar Mendes',
                      judgment='29/05/2020 (sessão virtual 22-28/05/2020), improcedente', publication='DJe 18/06/2020',
                      subject='EC 45/2004 — art. 114, §§ 2º e 3º (dissídio coletivo de comum acordo)',
                      namespace='CF88', namespace_evidence='É a CF, mas o dispositivo é o art. 114, §§ 2º e 3º.',
                      target_check='FAIL', recommended_target=None, temporal_version=None,
                      decision='REJECT_FALSE_POSITIVE', confidence='HIGH', provisional=False, sources=['S1', 'S2', 'P1'],
                      reason='Mesmo falso positivo de anotação genérica da EC 45/2004, aqui no art. 98 (§ 1º, juizados especiais federais). A ADI 3392 '
                             'não trata do art. 98.'),
    'J0-BL-135': dict(precedent='STF:ADI:7697', court='STF', klass='ADI', number='7697', rapporteur='Min. Flávio Dino',
                      judgment='MC referendada pelo Pleno em 16/08/2024; mérito pendente', publication='DJE (referendo)',
                      subject='Emendas parlamentares (art. 166, em nível de artigo)',
                      namespace='CF88', namespace_evidence='A decisão nomeia parágrafos do art. 166 da Constituição Federal; o caput não é objeto.',
                      target_check='FAIL_GRANULARITY', recommended_target=None, temporal_version=None,
                      decision='DUPLICATE_RECOMMENDATION', confidence='HIGH', provisional=True, sources=['S7', 'P1'],
                      duplicate_of=['J0-BL-136', 'J0-BL-137'],
                      reason='A cautelar interpreta parágrafos específicos (§§ 9º a 20), não o caput do art. 166. O aparelho não herda vínculos entre '
                             'níveis (query keys exatas), e os vínculos específicos do § 9º e do § 11 deste lote já levam o precedente aos dispositivos '
                             'interpretados. Um vínculo no artigo seria o alvo amplo que o J0 sinaliza (BROAD_ARTICLE_TARGET_WITH_SUBDIVISIONS).'),
    'J0-BL-138': dict(precedent='STF:ADI:7697', court='STF', klass='ADI', number='7697', rapporteur='Min. Flávio Dino',
                      judgment='MC referendada pelo Pleno em 16/08/2024 (unânime); referendo de 04/12/2024 (emendas PIX); mérito pendente',
                      publication='DJE (referendos)', subject='Transferências especiais ("emendas PIX") — art. 166-A: plano de trabalho prévio, transparência',
                      namespace='CF88', namespace_evidence='A decisão nomeia "art. 166- A (EC/105) … da Constituição Federal".',
                      target_check='PASS', recommended_target='CF88:ART.166-A', temporal_version='redação da EC 105/2019 (vigente)',
                      decision='PROMOTE_RECOMMENDED', confidence='HIGH (identidade, alvo e namespace); estabilidade: MEDIUM',
                      provisional=True, sources=['S7', 'P1'],
                      reason='O art. 166-A inteiro está entre os dispositivos com interpretação conforme, e o referendo de 04/12/2024 trata das '
                             'transferências especiais. O alvo em nível de artigo é o correto, porque a decisão nomeia o artigo, não um parágrafo. Mérito '
                             'pendente: exige status e revalidação.'),
}

FIELDS = ('precedent', 'court', 'klass', 'number', 'rapporteur', 'judgment', 'publication', 'subject', 'namespace', 'namespace_evidence',
          'target_check', 'recommended_target', 'temporal_version', 'decision', 'confidence', 'provisional', 'sources', 'reason')
DECISIONS = ('PROMOTE_RECOMMENDED', 'REJECT_FALSE_POSITIVE', 'REJECT_NOT_MATERIAL', 'REJECT_TEMPORAL_MISMATCH', 'ALREADY_COVERED',
             'DUPLICATE_RECOMMENDATION', 'UNRESOLVED_EXTERNAL')


def decisions(doc):
    if sorted(REVIEW) != sorted(doc['selected']):
        raise SystemExit('REVIEW_DOES_NOT_MATCH_SELECTION')
    q = {x['recommendation_id']: x for x in doc['high_queue']}
    out = []
    for rid in doc['selected']:
        r = REVIEW[rid]
        if any(f not in r for f in FIELDS) or r['decision'] not in DECISIONS or any(s not in SOURCES for s in r['sources']):
            raise SystemExit('INCOMPLETE_REVIEW ' + rid)
        if r['decision'] == 'PROMOTE_RECOMMENDED' and not (r['recommended_target'] and r['target_check'] == 'PASS' and r['namespace'] == 'CF88'):
            raise SystemExit('PROMOTE_WITHOUT_TARGET ' + rid)
        out.append(dict(recommendation_id=rid, rank=q[rid]['rank'], recommended_by_backlog=q[rid]['target_id'],
                        suggested_identifiers=q[rid]['suggested_identifiers'], **{k: v for k, v in r.items()},
                        NAMESPACE_CHECK='PASS' if r['namespace'] == 'CF88' else 'FAIL', OFFICIAL_SOURCE_REVIEWED=True,
                        device_record_exists=False, device_note=NO_DEVICE_RECORD, status='AWAITING_USER_RATIFICATION'))
    return out
