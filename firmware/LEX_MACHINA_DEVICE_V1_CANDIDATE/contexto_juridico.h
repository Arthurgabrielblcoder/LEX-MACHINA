#pragma once

#include <stdint.h>
#include <string.h>
#include <ctype.h>

// Parser independente de Arduino. Mantem somente identificadores; nunca altera o TXT.
#if LEX_DEVICE_V1_ENABLED
// THOUSANDS_PARSER_FIX ativo (o sketch exige esta macro no build DEVICE V1: compilar com -DLEX_DEVICE_V1_ENABLED=1).
#define LEX_CONTEXTO_MILHAR 1
#define LEX_NUMERO_DISPOSITIVO_MAX 999999999u
#endif

struct ContextoJuridicoAtivo {
  char arquivo[64];
  char artigo[16];
  char paragrafo[16];
  char inciso[16];
  char alinea[8];

  uint32_t offsetArtigo;
  uint32_t offsetParagrafo;
  uint32_t offsetInciso;
  uint32_t offsetAlinea;
};

static inline void copiarContextoCampo(char *destino, size_t capacidade, const char *origem)
{
  if(capacidade==0) return;
  strncpy(destino,origem?origem:"",capacidade-1);
  destino[capacidade-1]='\0';
}

static inline void limparContextoJuridico(ContextoJuridicoAtivo &c, const char *arquivo="")
{
  memset(&c,0,sizeof(c));
  copiarContextoCampo(c.arquivo,sizeof(c.arquivo),arquivo);
}

static inline bool contextoJuridicoIgual(const ContextoJuridicoAtivo &a,
                                         const ContextoJuridicoAtivo &b)
{
  return strcmp(a.arquivo,b.arquivo)==0 &&
         strcmp(a.artigo,b.artigo)==0 &&
         strcmp(a.paragrafo,b.paragrafo)==0 &&
         strcmp(a.inciso,b.inciso)==0 &&
         strcmp(a.alinea,b.alinea)==0;
}

static inline const char *pularEspacosContexto(const char *p)
{
  // O texto constitucional pode usar espaco normal, tabulacao ou NBSP
  // (UTF-8 C2 A0) antes do marcador. Todos sao apenas indentacao.
  while(*p==' ' || *p=='\t' ||
        ((uint8_t)p[0]==0xC2 && (uint8_t)p[1]==0xA0)){
    if((uint8_t)p[0]==0xC2) p+=2;
    else p++;
  }
  return p;
}

static inline bool prefixoAsciiContexto(const char *p, const char *prefixo)
{
  while(*prefixo){
    unsigned char a=(unsigned char)*p++;
    unsigned char b=(unsigned char)*prefixo++;
    if(tolower(a)!=tolower(b)) return false;
  }
  return true;
}

static inline bool delimitadorDispositivo(const char *p)
{
  p=pularEspacosContexto(p);
  return *p=='-' || *p==':' || *p=='.' || *p=='\0' ||
         ((uint8_t)p[0]==0xE2 && (uint8_t)p[1]==0x80 &&
          ((uint8_t)p[2]==0x93 || (uint8_t)p[2]==0x94));
}

static inline bool lerNumeroDispositivo(const char *&p, char *saida, size_t capacidade)
{
  size_t n=0;

  while(isdigit((unsigned char)*p)){
    if(n+1<capacidade) saida[n++]=*p;
    p++;
  }

  if(n==0) return false;

#if LEX_DEVICE_V1_ENABLED
  // THOUSANDS_PARSER_FIX: na numeracao juridica brasileira o '.' pode ser separador de MILHAR ("Art. 2.000." = 2000;
  // Codigo Civil, CPC, CLT...). O ponto so pertence ao numero quando o bloco inicial tem 1-3 digitos e o ponto e seguido
  // de EXATAMENTE 3 digitos (o 4o caractere nao e digito): "Art. 2." -> 2; "Art. 2.000." -> 2000; "1.000.000" -> 1000000.
  // Nunca decimal. Valor inteiro acumulado com teto (LEX_NUMERO_DISPOSITIVO_MAX); excedeu -> false (contexto intacto).
  // Malformados ("1.00", "1.0000", "1234.567") param no ponto, como antes. O sufixo ("-A") e o ordinal seguem abaixo.
  if(n<=3){
    uint32_t valor=0;
    for(size_t i=0;i<n;i++) valor=valor*10u+(uint32_t)(saida[i]-'0');
    while(p[0]=='.' && isdigit((unsigned char)p[1]) && isdigit((unsigned char)p[2]) &&
          isdigit((unsigned char)p[3]) && !isdigit((unsigned char)p[4])){
      uint32_t grupo=(uint32_t)(p[1]-'0')*100u+(uint32_t)(p[2]-'0')*10u+(uint32_t)(p[3]-'0');
      if(valor>(LEX_NUMERO_DISPOSITIVO_MAX-grupo)/1000u) return false;
      if(n+3>=capacidade) return false;
      valor=valor*1000u+grupo;
      saida[n++]=p[1]; saida[n++]=p[2]; saida[n++]=p[3];
      p+=4;
    }
  }
#endif
  if((*p=='-' || *p=='.') && isalpha((unsigned char)p[1])){
    if(n+2<capacidade){
      saida[n++]=*p;
      saida[n++]=(char)toupper((unsigned char)p[1]);
    }
    p+=2;
  }

  saida[n]='\0';

  // ordinal masculino/feminino em UTF-8 depois do numero.
  if((uint8_t)p[0]==0xC2 &&
     ((uint8_t)p[1]==0xBA || (uint8_t)p[1]==0xAA)){
    p+=2;
  }

  return true;
}

#if LEX_DEVICE_V1_ENABLED
// CONTEXT_CITATION_GUARD: o TXT oficial quebra a linha fisica no hyperlink de uma remissao ("...nos termos do" / "§ 8º do art. 226
// da Constituição Federal,"). A linha comeca com o marcador, mas e citacao de OUTRO dispositivo, nunca estrutura local. Decisao so
// pelos bytes da propria linha (identica no scroll, no pouso, na reconstrucao e na ancora; sem I/O, sem estado), com os sinais do
// parser estrutural aprovado (LEGAL_TARGET_ID/structure_parser.py, modo estrito dos indices do acervo):
//   - apos o numero (ou "unico"): ',' / ';' (lista de citacao) ou uma palavra de remissao (REMISSION_WORDS), em minusculas;
//   - artigo so com 'A' maiusculo (article_case_sensitive): "art. 701" no meio da frase e remissao;
//   - inciso com formato de cabecalho; alinea seguida de ',' / ';' e citacao ("alínea" / "e), ou ...").
#define LEX_CONTEXTO_CITACAO 1

// p = logo apos o numero do dispositivo (ordinal ja consumido) ou apos "unico". true = remissao.
static inline bool remissaoAposDispositivo(const char *p)
{
  if((uint8_t)p[0]==0xC2 && (uint8_t)p[1]==0xB0) p+=2;                 // grau usado como ordinal ("§ 6° deste artigo")
  else if(p[0]=='o' && (p[1]=='\0' || p[1]==' ' || p[1]=='\t' || p[1]=='.' || p[1]==',' || p[1]==';')) p++;   // "1o"
  p=pularEspacosContexto(p);
  if(*p==',' || *p==';') return true;                                   // "§ 6º, todos da Constituição", "Art. 101, I,"
  if(*p=='.') p=pularEspacosContexto(p+1);
  char w[12];
  size_t n=0;
  while(((*p>='a' && *p<='z') || *p=='/') && n<11) w[n++]=*p++;
  if(n==0 || (*p!='\0' && *p!=' ' && *p!='\t')) return false;
  w[n]='\0';
  static const char *const PALAVRAS_REMISSAO[]={"da","do","das","dos","desta","deste","destas","destes","inclusive",
                                                "pelo","pela","pelos","pelas","para","combinado","c/c"};
  for(size_t i=0;i<sizeof(PALAVRAS_REMISSAO)/sizeof(PALAVRAS_REMISSAO[0]);i++)
    if(strcmp(w,PALAVRAS_REMISSAO[i])==0) return true;
  return false;
}

// [inicio,fim) = sequencia romana lida. Cabecalho de inciso: maiuscula inicial ("II", OCR "Il"/"Vl") e sem '.' depois ("D.O.U.",
// "inciso" + "III."); inicial minuscula (OCR "lI -") so com travessao seguido de espaco/fim ("civil.", "mil-réis", "dividi-los",
// uma letra solta "c"/"x" sao palavras ou fragmentos).
static inline bool incisoComFormatoEstrutural(const char *inicio, const char *fim)
{
  const char *k=pularEspacosContexto(fim);
  if(*k=='.') return false;
  if(*inicio>='A' && *inicio<='Z') return true;
  const char *d;
  if(*k=='-') d=k+1;
  else if((uint8_t)k[0]==0xE2 && (uint8_t)k[1]==0x80 && ((uint8_t)k[2]==0x93 || (uint8_t)k[2]==0x94)) d=k+3;
  else return false;
  return *d=='\0' || *d==' ' || *d=='\t';
}
#endif
static inline bool aplicarLinhaContextoJuridico(ContextoJuridicoAtivo &c,
                                                 const char *linha,
                                                 bool inicioLinhaFisica,
                                                 uint32_t offset)
{
  if(!inicioLinhaFisica || !linha) return false;

  const char *p=pularEspacosContexto(linha);
  char valor[16]={0};

  // ARTIGO
  if(prefixoAsciiContexto(p,"Art")){
#if LEX_DEVICE_V1_ENABLED
    if(*p!='A') return false;                                           // CONTEXT_CITATION_GUARD: "art. 701" = remissao
#endif
    if(prefixoAsciiContexto(p,"Artigo")) p+=6;
    else p+=3;

    if(*p=='.') p++;

    if(*p!=' ' && *p!='\t') return false;

    p=pularEspacosContexto(p);

    if(!lerNumeroDispositivo(p,valor,sizeof(valor))) return false;
#if LEX_DEVICE_V1_ENABLED
    if(remissaoAposDispositivo(p)) return false;                        // "Art. 95 da Constituição"
#endif

    copiarContextoCampo(c.artigo,sizeof(c.artigo),valor);

    c.paragrafo[0]='\0';
    c.inciso[0]='\0';
    c.alinea[0]='\0';

    c.offsetArtigo=offset;
    c.offsetParagrafo=0;
    c.offsetInciso=0;
    c.offsetAlinea=0;

    return true;
  }

  // PARAGRAFO COM §
  if(((uint8_t)p[0]==0xC2 && (uint8_t)p[1]==0xA7)){
    p+=2;
    p=pularEspacosContexto(p);

    if(!lerNumeroDispositivo(p,valor,sizeof(valor))) return false;
#if LEX_DEVICE_V1_ENABLED
    if(remissaoAposDispositivo(p)) return false;                        // "§ 8º do art. 226 da Constituição Federal,"
#endif

    copiarContextoCampo(c.paragrafo,sizeof(c.paragrafo),valor);

    c.inciso[0]='\0';
    c.alinea[0]='\0';

    c.offsetParagrafo=offset;
    c.offsetInciso=0;
    c.offsetAlinea=0;

    return true;
  }

  // PARAGRAFO UNICO
  const char *aposParagrafo=nullptr;

  if(prefixoAsciiContexto(p,"Paragrafo")){
    aposParagrafo=p+9;
  }
  else if(prefixoAsciiContexto(p,"Par\xC3\xA1grafo")){
    aposParagrafo=p+10;
  }

  if(aposParagrafo){
    aposParagrafo=pularEspacosContexto(aposParagrafo);

    if(prefixoAsciiContexto(aposParagrafo,"unico") ||
       prefixoAsciiContexto(aposParagrafo,"\xC3\xBAnico")){
#if LEX_DEVICE_V1_ENABLED
      if(remissaoAposDispositivo(aposParagrafo+((uint8_t)aposParagrafo[0]==0xC3?6:5)))
        return false;                                                   // "parágrafo único do art. 274"
#endif
      copiarContextoCampo(c.paragrafo,sizeof(c.paragrafo),"unico");

      c.inciso[0]='\0';
      c.alinea[0]='\0';

      c.offsetParagrafo=offset;
      c.offsetInciso=0;
      c.offsetAlinea=0;

      return true;
    }
  }

  // ALINEA:
  // A prioridade vem antes de inciso porque c, d, i, l, m, v e x tambem
  // pertencem ao alfabeto romano. Uma letra minuscula seguida de ')' e
  // inequivocamente uma alinea, inclusive quando ocupa uma unica linha visual.
  if(p[0]>='a' && p[0]<='z' && p[1]==')'){
#if LEX_DEVICE_V1_ENABLED
    {
      const char *q=pularEspacosContexto(p+2);
      if(*q==',' || *q==';') return false;                              // "(§ 1º, alínea" / "e), ou deixar de divulgá-la"
    }
#endif
    valor[0]=p[0];
    valor[1]='\0';

    copiarContextoCampo(c.alinea,sizeof(c.alinea),valor);
    c.offsetAlinea=offset;

    return true;
  }

  // INCISO:
  // algarismo romano isolado no inicio, obrigatoriamente seguido de separador.
  const char *inicio=p;
  size_t n=0;

  while(*p &&
        strchr("IVXLCDM",toupper((unsigned char)*p)) &&
        n+1<sizeof(valor)){
    valor[n++]=(char)toupper((unsigned char)*p++);
  }

  valor[n]='\0';

#if LEX_DEVICE_V1_ENABLED
  if(n>0 && !incisoComFormatoEstrutural(inicio,p)) return false;
#endif
  if(n>0 && p>inicio && delimitadorDispositivo(p)){
    copiarContextoCampo(c.inciso,sizeof(c.inciso),valor);

    c.alinea[0]='\0';
    c.offsetInciso=offset;
    c.offsetAlinea=0;

    return true;
  }

  return false;
}

/*
  ESCOLHA DO CONTEXTO VISUAL — V2

  Regra principal:
  - a LINHA CENTRAL representa o dispositivo juridico ativo;
  - isso permite selecionar incisos/paragrafos curtos, mesmo que ocupem
    somente uma linha visual;
  - a antiga "predominancia de 5 linhas" continua existindo somente como
    fallback quando a linha central nao possui contexto juridico valido.

  Motivo da alteracao:
  a regra antiga exigia que um novo contexto superasse o atual por duas
  linhas dentro de uma faixa central de cinco linhas. Dispositivos curtos
  (por exemplo, um inciso de uma unica linha) podiam ser pulados:
  INC. I -> INC. III, sem nunca ativar INC. II.
*/
// Linha visual que representa o dispositivo juridico ativo (regra principal abaixo).
// Definicao UNICA: o CONTEXTO, o ACTIVE_TARGET e o pouso da busca por artigo (DEVICE V1) usam esta mesma posicao.
static inline int linhaContextoAtivo(int total)
{
  return total/2;
}

static inline int escolherContextoPredominante(const ContextoJuridicoAtivo *linhas,
                                                int total,
                                                const ContextoJuridicoAtivo &atual)
{
  if(total<=0) return -1;

  int centro=linhaContextoAtivo(total);

  // 1) REGRA PRINCIPAL:
  // O contexto juridico exatamente no centro da tela tem prioridade.
  // Se ele for valido, ele representa o dispositivo ativo.
  if(centro>=0 && centro<total && linhas[centro].artigo[0]!='\0'){
    return centro;
  }

  // 2) FALLBACK:
  // Se por alguma razao a linha central nao tiver contexto valido,
  // usa predominancia em uma janela central de cinco linhas.
  int inicio=centro-2;
  if(inicio<0) inicio=0;

  int fim=centro+2;
  if(fim>=total) fim=total-1;

  int melhor=-1;
  int melhorPontos=-1;
  int melhorDistancia=9999;

  for(int i=inicio;i<=fim;i++){
    if(linhas[i].artigo[0]=='\0') continue;

    int pontos=0;

    for(int j=inicio;j<=fim;j++){
      if(contextoJuridicoIgual(linhas[i],linhas[j])){
        pontos++;
      }
    }

    int distancia=i-centro;
    if(distancia<0) distancia=-distancia;

    if(pontos>melhorPontos ||
       (pontos==melhorPontos && distancia<melhorDistancia)){
      melhor=i;
      melhorPontos=pontos;
      melhorDistancia=distancia;
    }
  }

  if(melhor>=0) return melhor;

  // 3) ULTIMO FALLBACK:
  // procura o contexto valido mais proximo do centro na tela inteira.
  for(int d=1; d<total; d++){
    int cima=centro-d;
    int baixo=centro+d;

    if(cima>=0 && linhas[cima].artigo[0]!='\0'){
      return cima;
    }

    if(baixo<total && linhas[baixo].artigo[0]!='\0'){
      return baixo;
    }
  }

  return -1;
}

static inline int validarRotinaContextoJuridico()
{
  int falhas=0;

  ContextoJuridicoAtivo c;
  limparContextoJuridico(c,"lei.txt");

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"Art. 5\xC2\xBA - direitos",true,10
    ) ||
    strcmp(c.artigo,"5")!=0;

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"II - ninguém",true,20
    ) ||
    strcmp(c.inciso,"II")!=0;

  falhas +=
    aplicarLinhaContextoJuridico(
      c,"conforme o art. 7\xC2\xBA do CDC",true,25
    );

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"Par\xC3\xA1grafo \xC3\xBAnico. Regra",true,30
    ) ||
    strcmp(c.paragrafo,"unico")!=0 ||
    c.inciso[0];

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"\xC2\xA7 1\xC2\xBA Regra",true,35
    ) ||
    strcmp(c.paragrafo,"1")!=0;

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"III - hipótese",true,40
    ) ||
    strcmp(c.inciso,"III")!=0;

  falhas +=
    aplicarLinhaContextoJuridico(
      c,"continuação visual do mesmo inciso",false,45
    ) ||
    strcmp(c.inciso,"III")!=0;

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"a) primeira",true,50
    ) ||
    strcmp(c.alinea,"a")!=0;

  // Alíneas têm offset próprio e substituem a anterior, inclusive as letras
  // que também existem como numerais romanos (c e d).
  const char *alineas[]={"b) longa","c) curta","d) curta","e) longa"};
  const uint32_t offsetsAlineas[]={51,52,53,54};
  for(int i=0;i<4;i++){
    falhas += !aplicarLinhaContextoJuridico(c,alineas[i],true,offsetsAlineas[i]) ||
               c.alinea[0]!=(char)('b'+i) || c.alinea[1]!='\0' ||
               c.offsetAlinea!=offsetsAlineas[i];
  }

  falhas +=
    aplicarLinhaContextoJuridico(
      c,"Art. 99 citado no meio",false,60
    );

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"Art 12. Texto",true,70
    ) ||
    strcmp(c.artigo,"12")!=0 ||
    c.paragrafo[0] ||
    c.inciso[0] ||
    c.alinea[0];

  falhas +=
    !aplicarLinhaContextoJuridico(
      c,"Artigo 13. Texto",true,80
    ) ||
    strcmp(c.artigo,"13")!=0;

#if LEX_DEVICE_V1_ENABLED
  // THOUSANDS_PARSER_FIX: separador de milhar, sufixo e ordinal; malformados param no ponto; excesso falha sem alterar.
  {
    static const char *const entradas[]={"Art. 2. Texto","Art. 999. Texto","Art. 1.000. Texto","Art. 2.000. Texto",
                                         "Art. 2.046. Texto","Art. 1.000-A. Texto","Art. 5\xC2\xBA Texto","Art. 29-A. Texto",
                                         "Art. 1.00. Texto","Art. 1.0000 Texto","Art. 1234.567 Texto","Art. 1.000.000 Texto"};
    static const char *const esperados[]={"2","999","1000","2000","2046","1000-A","5","29-A","1","1","1234","1000000"};
    for(int i=0;i<12;i++){
      falhas += !aplicarLinhaContextoJuridico(c,entradas[i],true,90+i) || strcmp(c.artigo,esperados[i])!=0;
    }
    falhas += aplicarLinhaContextoJuridico(c,"Art. 999.999.999.999 Texto",true,110) || strcmp(c.artigo,"1000000")!=0;
  }
  // CONTEXT_CITATION_GUARD: remissoes em inicio de linha fisica nao mudam o contexto; cabecalhos reais continuam mudando.
  {
    limparContextoJuridico(c,"lei.txt");
    falhas += !aplicarLinhaContextoJuridico(c,"Art. 1\xC2\xBA Esta Lei cria mecanismos",true,200) || strcmp(c.artigo,"1")!=0;
    static const char *const citacoes[]={"\xC2\xA7 8\xC2\xBA do art. 226 da Constitui\xC3\xA7\xC3\xA3o Federal,","\xC2\xA7 3\xC2\xBA do",
                                         "\xC2\xA7 6\xC2\xBA, todos da Constitui\xC3\xA7\xC3\xA3o Federal","\xC2\xA7 6\xC2\xB0 deste artigo",
                                         "par\xC3\xA1grafo \xC3\xBAnico do art. 274","art. 226 da Constitui\xC3\xA7\xC3\xA3o","art. 701",
                                         "Art. 95 da Constitui\xC3\xA7\xC3\xA3o","Art. 101, I,","III.","civil.","mil-r\xC3\xA9is a dois",
                                         "D.O.U. de 2.9.1981","c","e), ou deixar de divulg\xC3\xA1-la"};
    for(size_t i=0;i<sizeof(citacoes)/sizeof(citacoes[0]);i++)
      falhas += aplicarLinhaContextoJuridico(c,citacoes[i],true,210+i) || strcmp(c.artigo,"1")!=0 || c.paragrafo[0] ||
                c.inciso[0] || c.alinea[0];
    falhas += !aplicarLinhaContextoJuridico(c,"\xC2\xA7 1\xC2\xBA o trabalho ter\xC3\xA1 a",true,230) || strcmp(c.paragrafo,"1")!=0;
    falhas += !aplicarLinhaContextoJuridico(c,"III - hip\xC3\xB3tese",true,231) || strcmp(c.inciso,"III")!=0;
    falhas += !aplicarLinhaContextoJuridico(c,"b) da empregada gestante",true,232) || strcmp(c.alinea,"b")!=0;
    falhas += !aplicarLinhaContextoJuridico(c,"lI - OCR do inciso",true,233) || strcmp(c.inciso,"LI")!=0;
    falhas += !aplicarLinhaContextoJuridico(c,"Par\xC3\xA1grafo \xC3\xBAnico. a exclus\xC3\xA3o",true,234) ||
              strcmp(c.paragrafo,"unico")!=0 || c.inciso[0];
    falhas += !aplicarLinhaContextoJuridico(c,"Art. 2\xC2\xBA Toda mulher",true,235) || strcmp(c.artigo,"2")!=0 || c.paragrafo[0];
  }
#endif
  /*
    TESTE DA CORRECAO DE DISPOSITIVO CURTO

    A linha central e INC. II, enquanto INC. I e INC. III
    ocupam mais linhas ao redor. Mesmo assim II deve ser escolhido.
  */
  ContextoJuridicoAtivo linhas[13];

  for(int i=0;i<13;i++){
    limparContextoJuridico(linhas[i],"lei.txt");
    copiarContextoCampo(linhas[i].artigo,16,"201");

    if(i<=5){
      copiarContextoCampo(linhas[i].inciso,16,"I");
    }else if(i==6){
      copiarContextoCampo(linhas[i].inciso,16,"II");
    }else{
      copiarContextoCampo(linhas[i].inciso,16,"III");
    }
  }

  ContextoJuridicoAtivo atual=linhas[5];

  int escolhido=
    escolherContextoPredominante(
      linhas,
      13,
      atual
    );

  falhas +=
    escolhido<0 ||
    strcmp(linhas[escolhido].inciso,"II")!=0;

  /*
    Teste normal:
    se a linha central pertence ao inciso III,
    III deve ser o contexto ativo.
  */
  for(int i=0;i<13;i++){
    limparContextoJuridico(linhas[i],"lei.txt");
    copiarContextoCampo(linhas[i].artigo,16,"201");

    if(i<6){
      copiarContextoCampo(linhas[i].inciso,16,"II");
    }else{
      copiarContextoCampo(linhas[i].inciso,16,"III");
    }
  }

  escolhido=
    escolherContextoPredominante(
      linhas,
      13,
      atual
    );

  falhas +=
    escolhido<0 ||
    strcmp(linhas[escolhido].inciso,"III")!=0;

  /*
    Regressao ALINEA CURTA: B ocupa varias linhas; C e D, uma linha cada;
    E ocupa varias linhas. Ao cruzar a linha central, a ordem obrigatoria e
    B -> C -> D -> E. A selecao é a mesma de artigo/paragrafo/inciso: a
    linha central primeiro; predominancia apenas se o centro nao for valido.
  */
  const char *esperadas[]={"b","c","d","e"};
  const int inicioContexto[]={0,6,7,8};
  for(int caso=0;caso<4;caso++){
    for(int i=0;i<12;i++){
      limparContextoJuridico(linhas[i],"lei.txt");
      copiarContextoCampo(linhas[i].artigo,16,"X");
      const char *alinea=i<inicioContexto[1]?"b":
                         i<inicioContexto[2]?"c":
                         i<inicioContexto[3]?"d":"e";
      copiarContextoCampo(linhas[i].alinea,8,alinea);
    }
    // desloca a janela para que o contexto desejado ocupe seu centro (6).
    int deslocamento=6-inicioContexto[caso];
    for(int i=0;i<12;i++){
      int origem=i-deslocamento;
      const char *alinea=origem<inicioContexto[1]?"b":
                         origem<inicioContexto[2]?"c":
                         origem<inicioContexto[3]?"d":"e";
      copiarContextoCampo(linhas[i].alinea,8,alinea);
    }
    escolhido=escolherContextoPredominante(linhas,12,atual);
    falhas += escolhido<0 || strcmp(linhas[escolhido].alinea,esperadas[caso])!=0;
  }

  return falhas;
}
