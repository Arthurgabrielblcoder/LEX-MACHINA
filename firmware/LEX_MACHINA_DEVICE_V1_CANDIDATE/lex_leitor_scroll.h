// lex_leitor_scroll.h - DEVICE V1 (LEX_DEVICE_V1_ENABLED=1): leitura BUFFERIZADA do TXT do leitor + contadores do scroll.
//
// BIDIRECTIONAL_SCROLL_PERFORMANCE_FIX. O leitor lia o TXT com File::read() byte a byte (~17,2 us/B medidos no aparelho).
// LexArquivoBuffer expoe a MESMA interface usada pelas rotinas do leitor (seek/position/available/read()/read(buf,n)/close),
// mas serve read() de um bloco de LEX_LEITOR_BLOCO bytes: as rotinas de wrap visual (avancarUmaLinhaVisual), indice
// (indexarAntesDaJanela/indexarAte), linha visual (lerLinhaVisualParaBuffer) e contexto (reconstruirContextoAntesOffset)
// continuam com o MESMO corpo; so o tipo do arquivo muda. Abertura/fechamento continuam transitorios (um handle por chamada,
// fechado no destrutor ou em close()), como na politica de descritores (FILE_DESCRIPTOR_POLICY.md).
#pragma once
#include <SD.h>

#ifndef LEX_LEITOR_BLOCO
#define LEX_LEITOR_BLOCO 512
#endif

// Contadores cumulativos (nunca zerados): cada medicao guarda o valor antes e calcula a diferenca.
struct LexScrollPerf {
  uint32_t bytes;        // bytes lidos do SD pelo leitor (IO_BYTES)
  uint32_t seeks;        // seeks fisicos (SEEK_COUNT)
  uint32_t aberturas;    // SD.open do TXT do leitor
  uint8_t abertos;       // handles do leitor abertos agora (transitorios: cada um fecha na mesma funcao)
  uint8_t maxAbertos;    // pico de handles simultaneos do leitor (politica de FDs)
};
static LexScrollPerf lexScrollPerf={0,0,0,0,0};

class LexArquivoBuffer {
 public:
  explicit LexArquivoBuffer(const char *caminho) : f_(SD.open(caminho,FILE_READ)), tam_(0), base_(0), len_(0), pos_(0) {
    if(f_){
      tam_=f_.size(); lexScrollPerf.aberturas++;
      if(++lexScrollPerf.abertos>lexScrollPerf.maxAbertos) lexScrollPerf.maxAbertos=lexScrollPerf.abertos;
    }
  }
  ~LexArquivoBuffer(){ close(); }
  LexArquivoBuffer(const LexArquivoBuffer&)=delete;
  LexArquivoBuffer &operator=(const LexArquivoBuffer&)=delete;

  explicit operator bool() const { return aberto_(); }
  void close(){ if(aberto_()){ f_.close(); if(lexScrollPerf.abertos) lexScrollPerf.abertos--; } }
  uint32_t size() const { return tam_; }
  bool seek(uint32_t p){ if(!aberto_() || p>tam_) return false; pos_=p; return true; }
  uint32_t position() const { return pos_; }
  int available() const { return pos_<tam_ ? (int)(tam_-pos_) : 0; }

  int read(){
    if(pos_>=tam_) return -1;
    if(pos_<base_ || pos_>=base_+len_){ if(!carregar_(pos_)) return -1; }
    return buf_[(pos_++)-base_];
  }

  // Bloco contiguo [pos, pos+n): servido do buffer quando ja esta nele; senao uma leitura direta (sem copiar para o buffer).
  int read(uint8_t *dst, size_t n){
    if(!aberto_() || pos_>=tam_) return 0;
    if(n>tam_-pos_) n=tam_-pos_;
    if(pos_>=base_ && pos_+n<=base_+len_){ memcpy(dst,buf_+(pos_-base_),n); pos_+=n; return (int)n; }
    if(!f_.seek(pos_)) return 0;
    lexScrollPerf.seeks++;
    int r=f_.read(dst,n);
    if(r>0){ pos_+=(uint32_t)r; lexScrollPerf.bytes+=(uint32_t)r; }
    return r;
  }

  // Varreduras PARA TRAS (inicio de linha fisica, ancora "Art."): examinam o bloco ja em RAM sem I/O; so carregam o bloco
  // que TERMINA em `fim` quando o byte fim-1 ainda nao esta nele. O wrap seguinte (para frente) reaproveita o mesmo bloco.
  bool contem(uint32_t p) const { return len_>0 && p>=base_ && p<base_+len_; }
  uint32_t baseBloco() const { return base_; }
  uint8_t byteEm(uint32_t p) const { return buf_[p-base_]; }            // somente com contem(p)
  bool carregarAte(uint32_t fim){ return fim>0 && carregar_(fim>LEX_LEITOR_BLOCO?fim-LEX_LEITOR_BLOCO:0) && contem(fim-1); }

 private:
  bool aberto_() const { return (bool)f_; }
  bool carregar_(uint32_t p){
    if(!f_.seek(p)) return false;
    lexScrollPerf.seeks++;
    uint32_t n=tam_-p; if(n>LEX_LEITOR_BLOCO) n=LEX_LEITOR_BLOCO;
    int r=f_.read(buf_,n);
    base_=p; len_=r>0?(uint32_t)r:0;
    lexScrollPerf.bytes+=len_;
    return len_>0;
  }
  mutable File f_;
  uint32_t tam_, base_, len_, pos_;
  uint8_t buf_[LEX_LEITOR_BLOCO];
};
