"""CC mass discovery — Passagem 2: human-equivalent re-reading of the deterministic sample against the captured official text (DATA).
Each verdict was given re-reading the ementa / tese / enunciado / legislação citada of the official capture (hash in the record). 'OK' or the error.
Systematic errors found in earlier draws of this sample were fixed IN THE RULE and the whole group reprocessed (see the audit), so the sample
below is the final draw after those fixes."""
_OK = dict(source_identity='OK', target_mapping='OK', temporal='OK', material_relevance='OK', duplicate='OK')


def _ok(note):
    return dict(_OK, note=note)


SAMPLE_REVIEW = {
    'CCMD-0C190B7EAC': _ok('REsp 2145365: comunhão universal, "ressalvadas as hipóteses do art. 1.668" nas razões; listado nos dispositivos relevantes.'),
    'CCMD-0CBA176F7F': _ok('Tema 310: a tese nomeia "regra de transição prevista no art. 2.028 do Código Civil de 2002".'),
    'CCMD-10DDDFCC37': _ok('REsp 1679434: "O art. 2.045 do CC/2002 revogou o art. 499 do CCo/1850" — fundamento da decisão (prazo do frete).'),
    'CCMD-151261A851': _ok('REsp 1642331: "Nos termos do art. 935 do CC/02, a responsabilidade civil é independente da criminal".'),
    'CCMD-2820EB2A75': _ok('EREsp 1951463: dispositivo e tese aplicam o prazo decenal do art. 205; o § 3º, IV só aparece na questão (corretamente em C).'),
    'CCMD-2C2E1C2939': _ok('Tema 919: "norma de transição do art. 2.028 desse último Diploma Legal" (CC/2002) na tese.'),
    'CCMD-2D74B31D75': _ok('Súmula 464: o enunciado nomeia o art. 354 do Código Civil (imputação de pagamento).'),
    'CCMD-2FAFBF3E2A': _ok('REsp 2000938: testamento particular sem testemunhas, art. 1.876 nas razões.'),
    'CCMD-30C7163126': _ok('Tema 1232 STF: a tese remete ao incidente de desconsideração (art. 50 do CC); § 4º colapsado ao artigo (sem apoio textual).'),
    'CCMD-32DDED89ED': _ok('REsp 2230861: "responsabilidade civil do fundo ... à luz do art. 1.368-E" nas razões (o REsp da corretora não foi conhecido, o outro sim).'),
    'CCMD-346650603A': _ok('EAREsp 749198: prescrição decenal (art. 205 do CC/2002) na verbetação e nas razões.'),
    'CCMD-43C15E049C': _ok('ADPF 132 (com ADI 4277): interpretação conforme do art. 1.723; sinal USO_CONTEXTUAL é cautela, a pertinência é direta.'),
    'CCMD-4BE8F727D8': _ok('REsp 1256825: "O art. 1.229 do Código Civil ... critério de utilidade" — fundamento.'),
    'CCMD-5153BF964A': _ok('Tema 1418 (afetado): art. 168, parágrafo único, na questão; corretamente PROVISÓRIO (B).'),
    'CCMD-559F64C0DA': _ok('REsp 2253418: "nos termos do art. 202, III, do CC/02, houve a interrupção" — aplicação direta.'),
    'CCMD-5683B057FF': _ok('Tema 433: confusão (art. 381) é o fundamento da tese sobre honorários à Defensoria; evidência na questão (B).'),
    'CCMD-592825F303': _ok('REsp 1148631: justo título do parágrafo único do art. 1.201 como critério da melhor posse.'),
    'CCMD-5AFED73989': _ok('REsp 1099480: "interpretação do art. 108 do CC" é o objeto do julgamento.'),
    'CCMD-6199799E8E': _ok('AREsp 3006916: nas razões, legitimidade do condomínio "com base no art. 1.348, II, do CC".'),
    'CCMD-6263C35580': _ok('Súmula 504: referência legislativa oficial ao art. 206, § 5º, I (monitória de nota promissória); evidência estruturada (B).'),
    'CCMD-676822FFFA': _ok('REsp 1994309: penhora do imóvel "em violação do art. 1.368-B do Código Civil" — fundamento.'),
    'CCMD-7442242D4C': _ok('Tema 1173 (corretor): referência legislativa do leading case ao art. 722 (contrato de corretagem); só estruturada (B).'),
    'CCMD-8E2CA0B9DF': _ok('REsp 715894 (2006): "arts. 112 e 113 do CC/02" nomeados expressamente; estruturada + lista (B).'),
    'CCMD-90D0827DD1': dict(_OK, material_relevance='ERRO: uso conceitual (personalidade/registro de entidade sindical) em ADI trabalhista',
                            note='ADI 3890: o art. 45 é citado como conceito; não é jurisprudência sobre o dispositivo. Sinal USO_CONTEXTUAL o pôs no grupo de risco.'),
    'CCMD-9D7DBC8E22': _ok('REsp 2050372: administração pelo síndico (art. 1.347 do CC/02) fundamenta a ilegitimidade do condômino.'),
    'CCMD-9DDEB4D26D': _ok('REsp 447431 (2007): juros "a partir da vigência do atual Código Civil na forma do respectivo art. 406"; sinal de redação alterada correto.'),
    'CCMD-A5C6A7EA91': dict(_OK, material_relevance='ERRO: uso conceitual (obrigação de fazer) em tese tributária de ISS',
                            note='Tema 581 STF: o art. 247 entra só na legislação citada; a tese é de ISS. Sinal USO_CONTEXTUAL o pôs no grupo de risco.'),
    'CCMD-AEEB402E4E': dict(_OK, material_relevance='ERRO: abuso de direito usado como analogia em matéria eleitoral',
                            note='ADC 29/30 + ADI 4578 (julgamento conjunto, contado uma vez): o art. 187 é analogia; sinal USO_CONTEXTUAL correto.'),
    'CCMD-BFF84F1F9B': _ok('REsp 1385957: "Inteligência do art. 281 do CC/02" — exceções pessoais do devedor solidário.'),
    'CCMD-C474A5287E': _ok('REsp 1792271: fraude contra credores exige ação pauliana (CC/2002, art. 161).'),
    'CCMD-CBA1562FD9': _ok('REsp 665651: aplicou o CC/1916 (arts. 849, III, e 851), "correspondentes aos arts. 1.499, IV, e 1.500"; sinal CORRESPONDENCIA_CC1916 correto.'),
    'CCMD-CD9CE0D87D': _ok('AREsp 3007847: "Interpretação do art. 1.660, V, do CC" sobre benfeitorias na partilha.'),
    'CCMD-D2CC9B4160': _ok('REsp 2198859: mérito sobre a "interpretação do art. 1.336, § 2º" (multa condominial).'),
    'CCMD-D68F6F62CC': _ok('REsp 1621610: rejeita exegese extensiva da exceção do art. 2.027 (anulação da partilha) — fundamento.'),
    'CCMD-DCDF574EC7': _ok('REsp 1183133: "O art. 548 do Código Civil estabelece ser nula a doação de todos os bens" — fundamento.'),
    'CCMD-E457197ADF': _ok('SEC 1735: interesse do sócio pelo parágrafo único do art. 1.030; classe homologatória sinalizada (B).'),
    'CCMD-E736FD445A': _ok('REsp 2039541: interpretação do art. 1.857, § 1º (legítima e testamento) — mérito provido.'),
    'CCMD-E9A1EB9C99': _ok('REsp 1559595: depósito (art. 627 do CC) na qualificação da relação.'),
    'CCMD-EFF7D6EB99': _ok('EREsp 1171820: CC/1916 vigente à época, "matéria atualmente regida pelo art. 1.641, II"; sinal CORRESPONDENCIA_CC1916 correto.'),
    'CCMD-F1AAAD4657': _ok('EREsp 1141037: "art. 3º do mesmo Codex" (absolutamente incapaz) — fundamento da não fluência da prescrição.'),
}
