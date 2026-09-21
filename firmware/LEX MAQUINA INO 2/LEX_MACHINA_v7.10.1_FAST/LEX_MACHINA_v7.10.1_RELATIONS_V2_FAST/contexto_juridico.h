#pragma once

#include <stdint.h>
#include <string.h>
#include <ctype.h>

// Parser independente de Arduino. Mantem somente identificadores; nunca altera o TXT.

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
  while(*p==' ' || *p=='\t') p++;
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
    if(prefixoAsciiContexto(p,"Artigo")) p+=6;
    else p+=3;

    if(*p=='.') p++;

    if(*p!=' ' && *p!='\t') return false;

    p=pularEspacosContexto(p);

    if(!lerNumeroDispositivo(p,valor,sizeof(valor))) return false;

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
      copiarContextoCampo(c.paragrafo,sizeof(c.paragrafo),"unico");

      c.inciso[0]='\0';
      c.alinea[0]='\0';

      c.offsetParagrafo=offset;
      c.offsetInciso=0;
      c.offsetAlinea=0;

      return true;
    }
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

  if(n>0 && p>inicio && delimitadorDispositivo(p)){
    copiarContextoCampo(c.inciso,sizeof(c.inciso),valor);

    c.alinea[0]='\0';
    c.offsetInciso=offset;
    c.offsetAlinea=0;

    return true;
  }

  // ALINEA:
  // letra minuscula seguida imediatamente de ')'.
  if(p[0]>='a' && p[0]<='z' && p[1]==')'){
    valor[0]=p[0];
    valor[1]='\0';

    copiarContextoCampo(c.alinea,sizeof(c.alinea),valor);
    c.offsetAlinea=offset;

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
static inline int escolherContextoPredominante(const ContextoJuridicoAtivo *linhas,
                                                int total,
                                                const ContextoJuridicoAtivo &atual)
{
  if(total<=0) return -1;

  int centro=total/2;

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

  return falhas;
}
