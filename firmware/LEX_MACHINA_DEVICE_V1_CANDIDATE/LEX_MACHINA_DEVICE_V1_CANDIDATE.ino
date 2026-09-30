#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <EspBle.h>
#include <esp_system.h>
#include <esp_heap_caps.h>
#include <new>
#include "assets/lex_boot_screen.h"
#include "contexto_juridico.h"

// DEVICE V1 (candidato A3B): leitura do overlay /99_LEX_V1 (schema LEX_DEVICE_SCHEMA_VERSION). Desligado por padrao: com 0 o
// comportamento e identico ao v7.12.0. Com 1, apenas diagnostico serial no boot (sem UI nova, somente leitura no SD).
#ifndef LEX_DEVICE_V1_ENABLED
#define LEX_DEVICE_V1_ENABLED 0
#endif
#include "lex_device_v1.h"
#if LEX_DEVICE_V1_ENABLED
#include "mbedtls/sha256.h"
void lexV1DiagnosticoBoot();
bool lexV1Sha256Arquivo(const char *tipo, const char *caminho, const char *etapa, uint32_t &bytes, char hex[65]);
#endif

// =====================================================
// LEX MACHINA - CYBERDECK JURIDICO
// DEVICE V1 CANDIDATE (A3B) - copia de integracao da v7.12.0; unica mudanca: modulo lex_device_v1.h atras de flag
//               + runtime canonico /99_LEX_V1/05_TEXT/CF88_RUNTIME.txt com verificacao de tamanho e sha256 (fail closed)
// v7.12.0 JURIS CF EXPANDIDA - cache jurisprudencial dinamico em PSRAM
//               + preserva integralmente Relations V2, CDC V1 e fluidez 7.10.2
// v7.10.2 RELATIONS V2 FLUIDA - RELACOES.IDX em PSRAM + diagnostico agregado
//               + elimina leitura do indice de relacoes durante a rolagem
//               + remove redraw duplicado do rodape ao abrir o leitor
//               + fallback preservado para leitura direta do SD
// v7.10.1 RELATIONS V2 FAST - cache V2 em PSRAM + rodape sem redraw redundante
//               + mantem integralmente a base v7.9.4 CF BUSCA/CONTEXTO
//               + lookup por artigo/paragrafo/inciso/alinea com fallback de especificidade
//               + abertura direta de norma externa e salto por offset de artigo
//               + mantem integralmente a base v7.9.3 RODAPE SIMPLIFICADO
//               + atalhos sem contadores no leitor
//               + quantidade exibida somente dentro da categoria
//               + opções do rodapé aparecem apenas quando houver conteúdo
//               + correção de navegação por roda e touch na tela de relações
//               + fonte Arimo/Arial real rasterizada, proporcional e antialias
//               + cache de texto em RAM (sem framebuffer de tela inteira)
//               + quebra de linha por largura real em pixels, sem cortar palavras
//               + SEM scroll por hardware do ILI9341
//               + busca rapida de artigo mantida
//               + diagnostico de reset/heap no Serial
// =====================================================

// ---------------- PINOS ----------------
#define TFT_CS    10
#define TFT_DC     9
#define TFT_RST   14
#define TFT_MOSI  11
#define TFT_SCK   12
#define TFT_MISO  13
#define SD_CS      4

#define TOUCH_SDA  7
#define TOUCH_SCL  6
#define TOUCH_RST  5
#define TOUCH_INT  8
#define FT_ADDR 0x38

// ---------------- SPI COMPARTILHADO ----------------
SPIClass spiBus(FSPI);
Adafruit_ILI9341 tft(&spiBus, TFT_DC, TFT_CS, TFT_RST);

// ---------------- BLUETOOTH ----------------
EspBle ble;
EspBleConnectionId keyboardConnectionId = 0;
const char *NOME_TECLADO = "MINI-KEYBOARD";

// ---------------- CORES ----------------
#define COR_FUNDO        ILI9341_BLACK
#define COR_VERDE        ILI9341_GREEN
#define COR_VERDE_SUAVE  0x03E0
#define COR_VERDE_ESCURO 0x0180
#define COR_CINZA        0x2104

// No seu painel, INVON e o modo que entrega preto/verde corretamente.
#define PAINEL_PRECISA_INVON 1

// =====================================================
// FONTE DO LEITOR - ARIMO 12 px, ANTIALIAS 4 BITS
// =====================================================
// Rasterizada e embutida no firmware. Nao ha arquivo de fonte no SD.
// Arimo tem desenho metrico compativel com Arial e, nesta resolucao,
// produz g/m/n/e/a muito mais distintos do que a antiga grade 6x10.
//
// Cada glyph e proporcional (largura real), e o antialias usa 16 niveis
// de verde. Isso deixa o texto menos "serrilhado" e menos cansativo.
struct GlyphArimoAA {
  uint16_t offset;
  uint8_t width;
  uint8_t height;
  int8_t xOffset;
  int8_t yOffset;
  uint8_t advance;
};

static const uint8_t FONTE_ARIMO_A4_BITMAP[] PROGMEM = {
  0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x2F, 0x2E, 0x02, 0xF2, 0xE0, 0x2C,
  0x2C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x91, 0x0A,
  0x00, 0x0A, 0x00, 0x90, 0x00, 0xA0, 0x27, 0x07, 0xBD, 0xAC, 0xC6, 0x05, 0x50, 0x82, 0x00, 0x82, 0x0A, 0x00, 0xCE, 0xDD,
  0xED, 0x40, 0xA0, 0x28, 0x00, 0x28, 0x06, 0x40, 0x00, 0x07, 0xDF, 0xC2, 0x1F, 0x3E, 0x39, 0x1F, 0x3E, 0x01, 0x0C, 0xBE,
  0x00, 0x02, 0x9F, 0xE4, 0x00, 0x2E, 0x7C, 0x35, 0x2E, 0x2E, 0x4D, 0x3E, 0x5C, 0x08, 0xEF, 0xD4, 0x00, 0x2E, 0x00, 0x05,
  0xDD, 0x30, 0x03, 0xB0, 0x00, 0xE3, 0x5B, 0x00, 0xB2, 0x00, 0x1F, 0x02, 0xE0, 0x58, 0x00, 0x01, 0xF0, 0x3D, 0x1C, 0x4B,
  0xA2, 0x0D, 0x36, 0xA8, 0x5D, 0x25, 0xA0, 0x4C, 0xC5, 0xB1, 0xF0, 0x3D, 0x00, 0x00, 0xA3, 0x1F, 0x03, 0xE0, 0x00, 0x58,
  0x00, 0xE3, 0x6B, 0x00, 0x0C, 0x10, 0x05, 0xDC, 0x30, 0x00, 0x4C, 0xDC, 0x40, 0x00, 0x0E, 0x20, 0x5D, 0x00, 0x00, 0xE1,
  0x08, 0xB0, 0x00, 0x0A, 0xAC, 0xA1, 0x00, 0x04, 0xDF, 0x30, 0x07, 0x00, 0xD4, 0xAC, 0x02, 0xC0, 0x2F, 0x02, 0xEB, 0xA6,
  0x00, 0xE3, 0x08, 0xFF, 0x10, 0x04, 0xBD, 0xD8, 0x8D, 0xA0, 0x2F, 0x02, 0xF0, 0x2C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x5B, 0x00, 0x1D, 0x20, 0x07, 0x90, 0x00, 0xC4, 0x00, 0x0F, 0x10, 0x01, 0xF0, 0x00, 0x1F,
  0x00, 0x00, 0xF2, 0x00, 0x0C, 0x40, 0x00, 0x7A, 0x00, 0x01, 0xD2, 0x00, 0x04, 0xA0, 0x1C, 0x30, 0x00, 0x4C, 0x00, 0x00,
  0xC4, 0x00, 0x07, 0x90, 0x00, 0x4C, 0x00, 0x03, 0xE0, 0x00, 0x3E, 0x00, 0x04, 0xC0, 0x00, 0x79, 0x00, 0x0C, 0x40, 0x03,
  0xC0, 0x01, 0xC3, 0x00, 0x02, 0xF0, 0x08, 0x6F, 0x56, 0x3A, 0xF8, 0x21, 0xC5, 0xB0, 0x14, 0x05, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x8D, 0xDF, 0xDD, 0x60, 0x02, 0xF0,
  0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0xA0, 0x05, 0x00, 0x0D, 0xDC, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0xB3, 0x00, 0xD0, 0x04, 0xA0, 0x08, 0x60, 0x0C, 0x20, 0x1D, 0x00, 0x59,
  0x00, 0x95, 0x00, 0xD1, 0x00, 0x01, 0xAD, 0xD8, 0x00, 0x99, 0x01, 0xB6, 0x0E, 0x30, 0x05, 0xB1, 0xF0, 0x00, 0x3D, 0x2F,
  0x00, 0x02, 0xE1, 0xF0, 0x00, 0x3D, 0x0E, 0x30, 0x06, 0xB0, 0x89, 0x01, 0xC5, 0x01, 0xAD, 0xD8, 0x00, 0x01, 0xAF, 0x00,
  0x01, 0xD8, 0xF0, 0x00, 0x12, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F,
  0x00, 0x00, 0x02, 0xF0, 0x00, 0x5D, 0xDF, 0xDC, 0x00, 0x03, 0xCD, 0xC3, 0x00, 0xD4, 0x06, 0xC0, 0x05, 0x00, 0x3E, 0x00,
  0x00, 0x07, 0xB0, 0x00, 0x03, 0xE2, 0x00, 0x03, 0xD4, 0x00, 0x02, 0xD4, 0x00, 0x00, 0xB5, 0x00, 0x00, 0x2F, 0xDD, 0xDD,
  0x10, 0x05, 0xDD, 0xC3, 0x02, 0xE2, 0x07, 0xC0, 0x24, 0x00, 0x3E, 0x00, 0x00, 0x09, 0x90, 0x00, 0x7E, 0xC1, 0x00, 0x00,
  0x08, 0xA0, 0x24, 0x00, 0x3E, 0x04, 0xD1, 0x07, 0xB0, 0x07, 0xDD, 0xB2, 0x00, 0x00, 0x00, 0x9F, 0x00, 0x00, 0x03, 0xDF,
  0x00, 0x00, 0x0C, 0x5F, 0x00, 0x00, 0x78, 0x2F, 0x00, 0x02, 0xC0, 0x2F, 0x00, 0x0B, 0x30, 0x2F, 0x00, 0x2E, 0xEE, 0xEF,
  0xE2, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x2F, 0xDD, 0xD6, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02,
  0xFA, 0xDA, 0x10, 0x19, 0x20, 0xAA, 0x00, 0x00, 0x03, 0xE0, 0x12, 0x00, 0x3D, 0x04, 0xD1, 0x09, 0x90, 0x08, 0xDD, 0xA1,
  0x00, 0x01, 0xAD, 0xC2, 0x00, 0x89, 0x06, 0x70, 0x0E, 0x20, 0x00, 0x01, 0xF7, 0xDB, 0x20, 0x2F, 0x50, 0x9A, 0x01, 0xF0,
  0x03, 0xD0, 0x0E, 0x10, 0x3D, 0x00, 0x97, 0x08, 0xA0, 0x01, 0xBD, 0xB1, 0x00, 0x9D, 0xDD, 0xDD, 0x00, 0x00, 0x09, 0x70,
  0x00, 0x02, 0xD0, 0x00, 0x00, 0xA5, 0x00, 0x00, 0x2D, 0x00, 0x00, 0x07, 0x90, 0x00, 0x00, 0xC4, 0x00, 0x00, 0x0F, 0x10,
  0x00, 0x01, 0xF0, 0x00, 0x00, 0x04, 0xCD, 0xB2, 0x00, 0xE3, 0x06, 0xB0, 0x2F, 0x00, 0x3E, 0x00, 0xD5, 0x07, 0xA0, 0x03,
  0xEE, 0xD2, 0x00, 0xD5, 0x07, 0xB0, 0x2F, 0x00, 0x3E, 0x00, 0xE4, 0x06, 0xB0, 0x04, 0xCD, 0xC3, 0x00, 0x03, 0xCD, 0xA0,
  0x00, 0xD5, 0x09, 0x70, 0x1F, 0x00, 0x3C, 0x01, 0xF1, 0x03, 0xE0, 0x0D, 0x60, 0x9E, 0x00, 0x3C, 0xC7, 0xD0, 0x00, 0x00,
  0x5B, 0x00, 0xB4, 0x0B, 0x50, 0x04, 0xDD, 0x80, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00,
  0x2C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0xA0, 0x05, 0x00, 0x00, 0x00, 0x00, 0x60, 0x00, 0x01,
  0x7D, 0x90, 0x02, 0x9D, 0x81, 0x00, 0x0F, 0x71, 0x00, 0x00, 0x09, 0xD8, 0x10, 0x00, 0x00, 0x17, 0xD9, 0x30, 0x00, 0x00,
  0x05, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x5D, 0xDD, 0xDD, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0xDD, 0xDD, 0xD5,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x09, 0xD7, 0x10, 0x00, 0x00, 0x18, 0xD9, 0x20, 0x00,
  0x00, 0x17, 0xF0, 0x00, 0x02, 0x8D, 0x90, 0x03, 0x9D, 0x71, 0x00, 0x0C, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02,
  0xAD, 0xDA, 0x10, 0xC6, 0x00, 0x8A, 0x19, 0x00, 0x03, 0xE0, 0x00, 0x00, 0x7C, 0x00, 0x00, 0x7D, 0x20, 0x00, 0x8C, 0x10,
  0x00, 0x0E, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x02, 0x9D, 0xDD, 0x92, 0x00, 0x00, 0x4D, 0x50,
  0x01, 0x7E, 0x20, 0x02, 0xE3, 0x9D, 0xC6, 0xA8, 0x90, 0x09, 0x88, 0xA0, 0x1E, 0x73, 0xD0, 0x0E, 0x3E, 0x20, 0x0D, 0x43,
  0xE0, 0x1F, 0x2F, 0x00, 0x2F, 0x15, 0xC0, 0x2F, 0x1E, 0x21, 0x9F, 0x0B, 0x60, 0x0E, 0x36, 0xCA, 0x2B, 0xC6, 0x00, 0x0A,
  0x90, 0x00, 0x00, 0x10, 0x00, 0x01, 0xD8, 0x10, 0x17, 0xD0, 0x00, 0x00, 0x18, 0xCD, 0xC7, 0x10, 0x00, 0x00, 0x0C, 0xC0,
  0x00, 0x00, 0x3B, 0xA3, 0x00, 0x00, 0x86, 0x59, 0x00, 0x00, 0xD1, 0x1D, 0x00, 0x04, 0xA0, 0x09, 0x50, 0x0A, 0xEE, 0xEE,
  0xA0, 0x1E, 0x00, 0x00, 0xE1, 0x6A, 0x00, 0x00, 0x96, 0xC5, 0x00, 0x00, 0x5C, 0x2F, 0xDD, 0xDB, 0x20, 0x2F, 0x00, 0x07,
  0xC0, 0x2F, 0x00, 0x03, 0xE0, 0x2F, 0x00, 0x08, 0x90, 0x2F, 0xDD, 0xED, 0x10, 0x2F, 0x00, 0x08, 0xB0, 0x2F, 0x00, 0x03,
  0xE0, 0x2F, 0x00, 0x07, 0xB0, 0x2F, 0xDD, 0xDB, 0x20, 0x00, 0x4C, 0xDD, 0xA2, 0x00, 0x4E, 0x40, 0x06, 0xE1, 0x0C, 0x60,
  0x00, 0x04, 0x11, 0xF1, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x01, 0xF1, 0x00, 0x00, 0x00, 0x0C, 0x60, 0x00, 0x07,
  0x20, 0x4E, 0x40, 0x06, 0xD1, 0x00, 0x4C, 0xDD, 0xA2, 0x00, 0x2F, 0xDD, 0xDA, 0x20, 0x02, 0xF0, 0x00, 0x7E, 0x20, 0x2F,
  0x00, 0x00, 0x99, 0x02, 0xF0, 0x00, 0x04, 0xD0, 0x2F, 0x00, 0x00, 0x3E, 0x02, 0xF0, 0x00, 0x04, 0xD0, 0x2F, 0x00, 0x00,
  0x98, 0x02, 0xF0, 0x00, 0x6E, 0x10, 0x2F, 0xDD, 0xDA, 0x20, 0x00, 0x2F, 0xDD, 0xDD, 0xD1, 0x2F, 0x00, 0x00, 0x00, 0x2F,
  0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xA0, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F,
  0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD4, 0x2F, 0xDD, 0xDD, 0x92, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00,
  0x00, 0x2F, 0xDD, 0xDD, 0x72, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x00,
  0x4B, 0xDD, 0xC7, 0x00, 0x04, 0xE4, 0x00, 0x2C, 0x70, 0x0C, 0x60, 0x00, 0x01, 0x00, 0x1F, 0x10, 0x00, 0x00, 0x00, 0x2F,
  0x00, 0x09, 0xDD, 0xD0, 0x1F, 0x20, 0x00, 0x02, 0xE0, 0x0B, 0x70, 0x00, 0x02, 0xE0, 0x03, 0xE5, 0x00, 0x2B, 0xC0, 0x00,
  0x3B, 0xDD, 0xC7, 0x10, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00,
  0x02, 0xE0, 0x2F, 0xDD, 0xDD, 0xDE, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0,
  0x2F, 0x00, 0x00, 0x2E, 0x00, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x00, 0x00,
  0x9D, 0xF0, 0x00, 0x02, 0xF0, 0x00, 0x02, 0xF0, 0x00, 0x02, 0xF0, 0x00, 0x02, 0xF0, 0x00, 0x02, 0xF0, 0x51, 0x02, 0xE0,
  0xB8, 0x07, 0xB0, 0x2C, 0xDB, 0x20, 0x2F, 0x00, 0x08, 0xC1, 0x2F, 0x00, 0x6D, 0x10, 0x2F, 0x04, 0xD2, 0x00, 0x2F, 0x3D,
  0x30, 0x00, 0x2F, 0xDE, 0x30, 0x00, 0x2F, 0x25, 0xD1, 0x00, 0x2F, 0x00, 0x8B, 0x00, 0x2F, 0x00, 0x0C, 0x80, 0x2F, 0x00,
  0x02, 0xE5, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02,
  0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0x20, 0x2F, 0x90, 0x00, 0x0B, 0xE0, 0x2F,
  0xD0, 0x00, 0x1D, 0xE0, 0x2F, 0x95, 0x00, 0x69, 0xE0, 0x2F, 0x5A, 0x00, 0xB4, 0xE0, 0x2F, 0x0D, 0x11, 0xC2, 0xE0, 0x2F,
  0x09, 0x56, 0x72, 0xE0, 0x2F, 0x04, 0xAB, 0x22, 0xE0, 0x2F, 0x00, 0xDC, 0x02, 0xE0, 0x2F, 0x00, 0x97, 0x02, 0xE0, 0x2F,
  0x90, 0x00, 0x2E, 0x02, 0xFD, 0x30, 0x02, 0xE0, 0x2F, 0x5C, 0x00, 0x2E, 0x02, 0xF0, 0xB6, 0x02, 0xE0, 0x2F, 0x03, 0xD1,
  0x2E, 0x02, 0xF0, 0x09, 0x82, 0xE0, 0x2F, 0x00, 0x1E, 0x4E, 0x02, 0xF0, 0x00, 0x6D, 0xE0, 0x2F, 0x00, 0x00, 0xCE, 0x00,
  0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x04, 0xE4, 0x00, 0x5E, 0x20, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x1F, 0x10, 0x00, 0x04, 0xD0,
  0x2F, 0x00, 0x00, 0x03, 0xE0, 0x1F, 0x10, 0x00, 0x04, 0xD0, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x04, 0xE4, 0x00, 0x5D, 0x20,
  0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x2F, 0xDD, 0xDA, 0x10, 0x2F, 0x00, 0x09, 0xA0, 0x2F, 0x00, 0x03, 0xD0, 0x2F, 0x00, 0x03,
  0xD0, 0x2F, 0x00, 0x09, 0x90, 0x2F, 0xDD, 0xD9, 0x10, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00,
  0x00, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x04, 0xD4, 0x00, 0x5E, 0x20, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x1F, 0x10, 0x00, 0x04,
  0xD0, 0x2F, 0x00, 0x00, 0x03, 0xE0, 0x1F, 0x10, 0x00, 0x04, 0xD0, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x05, 0xE4, 0x00, 0x5E,
  0x20, 0x00, 0x5C, 0xDE, 0xB3, 0x00, 0x00, 0x00, 0x5C, 0x00, 0x00, 0x00, 0x00, 0x1E, 0x40, 0x00, 0x00, 0x00, 0x05, 0xDC,
  0x00, 0x2F, 0xDD, 0xDD, 0xA2, 0x02, 0xF0, 0x00, 0x08, 0xB0, 0x2F, 0x00, 0x00, 0x3E, 0x02, 0xF0, 0x00, 0x19, 0xA0, 0x2F,
  0xDD, 0xDF, 0x91, 0x02, 0xF0, 0x01, 0xE5, 0x00, 0x2F, 0x00, 0x06, 0xD0, 0x02, 0xF0, 0x00, 0x0C, 0x60, 0x2F, 0x00, 0x00,
  0x4E, 0x10, 0x04, 0xCD, 0xDA, 0x10, 0x0E, 0x40, 0x0A, 0x80, 0x1F, 0x10, 0x01, 0x10, 0x0C, 0xC5, 0x10, 0x00, 0x01, 0x8D,
  0xFB, 0x20, 0x00, 0x00, 0x3B, 0xB0, 0x23, 0x00, 0x03, 0xE0, 0x4E, 0x20, 0x08, 0xA0, 0x06, 0xCD, 0xDA, 0x10, 0xCD, 0xDF,
  0xDD, 0xA0, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00,
  0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F,
  0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x1F, 0x20, 0x00,
  0x5C, 0x00, 0x9A, 0x10, 0x2C, 0x60, 0x00, 0x8D, 0xDC, 0x60, 0x00, 0xC6, 0x00, 0x00, 0x6B, 0x6C, 0x00, 0x00, 0xB6, 0x1E,
  0x20, 0x02, 0xE1, 0x0A, 0x70, 0x07, 0xA0, 0x04, 0xD0, 0x0D, 0x40, 0x00, 0xD3, 0x3D, 0x00, 0x00, 0x88, 0x88, 0x00, 0x00,
  0x2D, 0xD2, 0x00, 0x00, 0x0C, 0xB0, 0x00, 0xC5, 0x00, 0x0E, 0x50, 0x00, 0xF2, 0x89, 0x00, 0x4E, 0x90, 0x04, 0xD0, 0x4D,
  0x00, 0x88, 0xD0, 0x08, 0x90, 0x1F, 0x20, 0xB3, 0xD2, 0x0C, 0x50, 0x0B, 0x61, 0xE0, 0x95, 0x1F, 0x10, 0x07, 0xA4, 0xB0,
  0x59, 0x4C, 0x00, 0x03, 0xD8, 0x70, 0x2D, 0x88, 0x00, 0x00, 0xEC, 0x30, 0x0D, 0xC4, 0x00, 0x00, 0xAE, 0x00, 0x09, 0xE0,
  0x00, 0x3E, 0x20, 0x01, 0xE3, 0x07, 0xB0, 0x0A, 0x80, 0x00, 0xC6, 0x4D, 0x00, 0x00, 0x3E, 0xD3, 0x00, 0x00, 0x0C, 0xD0,
  0x00, 0x00, 0x6B, 0xB7, 0x00, 0x02, 0xE2, 0x2E, 0x20, 0x0B, 0x70, 0x07, 0xC0, 0x6C, 0x00, 0x00, 0xC6, 0x1E, 0x30, 0x00,
  0x5D, 0x00, 0x6C, 0x00, 0x1D, 0x40, 0x00, 0xC6, 0x08, 0xA0, 0x00, 0x03, 0xE3, 0xE1, 0x00, 0x00, 0x09, 0xE6, 0x00, 0x00,
  0x00, 0x2F, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x07, 0xDD,
  0xDD, 0xF7, 0x00, 0x00, 0x04, 0xD1, 0x00, 0x00, 0x1D, 0x40, 0x00, 0x00, 0xA9, 0x00, 0x00, 0x06, 0xD1, 0x00, 0x00, 0x2E,
  0x30, 0x00, 0x00, 0xC7, 0x00, 0x00, 0x07, 0xB0, 0x00, 0x00, 0x0F, 0xED, 0xDD, 0xDA, 0x2F, 0xD4, 0x2F, 0x00, 0x2F, 0x00,
  0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0xD4, 0xD1, 0x00,
  0x95, 0x00, 0x59, 0x00, 0x1D, 0x00, 0x0C, 0x20, 0x08, 0x60, 0x04, 0xA0, 0x01, 0xD0, 0x00, 0xB3, 0x6D, 0xF0, 0x02, 0xF0,
  0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x6D, 0xF0,
  0x00, 0x74, 0x00, 0x04, 0xAC, 0x00, 0x0B, 0x38, 0x60, 0x3B, 0x02, 0xC0, 0xB4, 0x00, 0x95, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2D, 0xDD, 0xDD, 0xDA, 0x0A,
  0x80, 0x00, 0x94, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02,
  0xCD, 0xC4, 0x00, 0xB7, 0x06, 0xC0, 0x00, 0x00, 0x2E, 0x00, 0x5C, 0xDD, 0xE0, 0x1F, 0x40, 0x3E, 0x01, 0xF1, 0x09, 0xF0,
  0x08, 0xEC, 0x3C, 0xC0, 0x2F, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x2F, 0x7D, 0xC2, 0x2F, 0x60, 0x8A, 0x2F, 0x10, 0x3D, 0x2F,
  0x00, 0x2E, 0x2F, 0x10, 0x3D, 0x2F, 0x60, 0x8A, 0x2E, 0x7D, 0xC2, 0x02, 0xBD, 0xC3, 0x00, 0xB6, 0x05, 0xD0, 0x0F, 0x10,
  0x01, 0x02, 0xF0, 0x00, 0x00, 0x0F, 0x10, 0x02, 0x00, 0xB7, 0x04, 0xC0, 0x02, 0xBD, 0xC3, 0x00, 0x00, 0x00, 0x2E, 0x00,
  0x00, 0x02, 0xE0, 0x04, 0xDD, 0x7E, 0x00, 0xC5, 0x08, 0xE0, 0x1F, 0x10, 0x3E, 0x02, 0xF0, 0x02, 0xE0, 0x1F, 0x10, 0x4E,
  0x00, 0xD5, 0x09, 0xE0, 0x04, 0xDD, 0x7E, 0x00, 0x02, 0xBD, 0xC3, 0x00, 0xB7, 0x03, 0xD0, 0x0F, 0x10, 0x0C, 0x32, 0xFD,
  0xDD, 0xE4, 0x0F, 0x10, 0x00, 0x00, 0xB6, 0x01, 0xA1, 0x02, 0xBD, 0xD6, 0x00, 0x00, 0xBD, 0x30, 0x2F, 0x10, 0x0D, 0xFD,
  0x30, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x04, 0xDD, 0x6F, 0x00,
  0xC5, 0x0A, 0xE0, 0x1F, 0x10, 0x4E, 0x02, 0xF0, 0x02, 0xE0, 0x1F, 0x10, 0x4E, 0x00, 0xD5, 0x09, 0xE0, 0x05, 0xDC, 0x6E,
  0x00, 0x00, 0x03, 0xD0, 0x0A, 0x60, 0x8A, 0x00, 0x3C, 0xDB, 0x20, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x6C,
  0xD5, 0x02, 0xF6, 0x06, 0xC0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F,
  0x00, 0x2E, 0x00, 0x2C, 0x00, 0x00, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x00, 0x02, 0xC0, 0x00,
  0x00, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x03, 0xE0, 0x3E,
  0x80, 0x2F, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x00, 0x2F, 0x00, 0xA9, 0x02, 0xF0, 0x7B, 0x00, 0x2F, 0x5C, 0x10, 0x02, 0xFE,
  0xB0, 0x00, 0x2F, 0x2C, 0x60, 0x02, 0xF0, 0x2E, 0x20, 0x2F, 0x00, 0x7C, 0x00, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F,
  0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x00, 0x2D, 0x7C, 0xE5, 0x7D, 0xD5, 0x02, 0xF6, 0x05, 0xE6, 0x05, 0xD0, 0x2F, 0x00,
  0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x02, 0xE0,
  0x2F, 0x00, 0x2E, 0x00, 0x2E, 0x00, 0x2D, 0x7C, 0xD5, 0x02, 0xF6, 0x05, 0xC0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0,
  0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x00, 0x01, 0xAD, 0xD9, 0x10, 0xB8, 0x00, 0xA8, 0x0F, 0x10,
  0x04, 0xC2, 0xF0, 0x00, 0x2E, 0x0F, 0x10, 0x04, 0xC0, 0xA8, 0x00, 0xA8, 0x01, 0xAD, 0xD9, 0x10, 0x2E, 0x7D, 0xC2, 0x2F,
  0x60, 0x8A, 0x2F, 0x10, 0x3D, 0x2F, 0x00, 0x2E, 0x2F, 0x10, 0x3D, 0x2F, 0x60, 0x8A, 0x2F, 0x7D, 0xC2, 0x2F, 0x00, 0x00,
  0x2F, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x04, 0xDD, 0x7E, 0x00, 0xC5, 0x09, 0xE0, 0x1F, 0x10, 0x3E, 0x02, 0xF0, 0x02, 0xE0,
  0x1F, 0x10, 0x4E, 0x00, 0xD5, 0x09, 0xE0, 0x04, 0xDD, 0x7E, 0x00, 0x00, 0x02, 0xE0, 0x00, 0x00, 0x2E, 0x00, 0x00, 0x02,
  0xE0, 0x00, 0x00, 0x2D, 0x9B, 0x2F, 0x50, 0x2F, 0x10, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x06, 0xDD, 0xC3,
  0x1F, 0x10, 0x48, 0x0E, 0x72, 0x00, 0x03, 0xAE, 0xC3, 0x00, 0x00, 0x7D, 0x3B, 0x10, 0x4D, 0x08, 0xDD, 0xC4, 0x06, 0x00,
  0x0E, 0x00, 0xBF, 0xD2, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x10, 0x0C, 0xE3, 0x2F, 0x00, 0x2E, 0x02,
  0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x3E, 0x01, 0xF3, 0x09, 0xE0, 0x07, 0xEC, 0x5E,
  0x00, 0xC5, 0x00, 0x5C, 0x79, 0x00, 0x97, 0x2E, 0x00, 0xE2, 0x0C, 0x44, 0xC0, 0x07, 0x89, 0x70, 0x02, 0xCD, 0x20, 0x00,
  0xCB, 0x00, 0x0D, 0x20, 0x5F, 0x10, 0x79, 0x0A, 0x50, 0x9C, 0x40, 0xA5, 0x06, 0x90, 0xC6, 0x70, 0xE1, 0x02, 0xC1, 0xC2,
  0xB2, 0xC0, 0x00, 0xD5, 0x80, 0xD6, 0x80, 0x00, 0x9C, 0x50, 0xAC, 0x40, 0x00, 0x5F, 0x10, 0x7F, 0x00, 0x7A, 0x00, 0xB6,
  0x0C, 0x45, 0xC0, 0x03, 0xCD, 0x30, 0x00, 0xCB, 0x00, 0x04, 0xCC, 0x40, 0x1D, 0x33, 0xD1, 0x89, 0x00, 0x98, 0xC5, 0x00,
  0x4C, 0x7A, 0x00, 0x97, 0x2E, 0x00, 0xD2, 0x0B, 0x53, 0xC0, 0x06, 0xA7, 0x70, 0x01, 0xEC, 0x20, 0x00, 0xBC, 0x00, 0x00,
  0x96, 0x00, 0x02, 0xD1, 0x00, 0x8D, 0x50, 0x00, 0x0A, 0xDD, 0xEF, 0x00, 0x00, 0x0B, 0x80, 0x00, 0x07, 0xC0, 0x00, 0x03,
  0xE3, 0x00, 0x00, 0xC7, 0x00, 0x00, 0x8B, 0x00, 0x00, 0x0F, 0xDD, 0xDD, 0x20, 0x00, 0xAE, 0x40, 0x2F, 0x10, 0x02, 0xF0,
  0x00, 0x2F, 0x00, 0x06, 0xD0, 0x05, 0xF4, 0x00, 0x06, 0xC0, 0x00, 0x2E, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x01, 0xF2,
  0x00, 0x09, 0xE4, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F, 0x02,
  0xF0, 0x6E, 0x70, 0x00, 0x4E, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x01, 0xF3, 0x00, 0x05, 0xF3, 0x00, 0xE4, 0x00, 0x2F,
  0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x04, 0xE0, 0x06, 0xE6, 0x00, 0x09, 0xDB, 0x52, 0x60, 0x05, 0x03, 0xAD, 0x90, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0xDD, 0xC2, 0x01, 0xF2, 0x06, 0x80, 0x1E, 0x50,
  0x00, 0x00, 0x4F, 0xD8, 0x10, 0x0D, 0x42, 0xAB, 0x01, 0xF1, 0x03, 0xD0, 0x0A, 0xC6, 0xB6, 0x00, 0x04, 0x9D, 0x40, 0x00,
  0x00, 0x5D, 0x03, 0xC1, 0x06, 0xC0, 0x06, 0xCC, 0xB2, 0x00, 0x3B, 0xA6, 0x05, 0x10, 0xC0, 0x49, 0x8C, 0x0C, 0x02, 0xD0,
  0x6B, 0x88, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x9B, 0x1C, 0x40, 0x5C, 0x1B, 0x70,
  0x0E, 0x26, 0xD0, 0x00, 0x6B, 0x1B, 0x70, 0x00, 0x9A, 0x1C, 0x40, 0x00, 0x00, 0x00, 0x07, 0xD4, 0x01, 0xF5, 0xD0, 0x1F,
  0x5D, 0x00, 0x7D, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4B, 0xB4, 0xB1,
  0x1B, 0xB0, 0x0B, 0xA1, 0x1A, 0x2A, 0xA2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0B, 0x53, 0xE2, 0x00, 0x1D,
  0x45, 0xC1, 0x00, 0x6E, 0x09, 0x60, 0x1D, 0x45, 0xC1, 0x0B, 0x63, 0xE2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3E, 0x30, 0x00,
  0x00, 0x03, 0xB0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0xC0, 0x00, 0x00, 0x3B, 0xA3, 0x00, 0x00, 0x86, 0x59, 0x00,
  0x00, 0xD1, 0x1D, 0x00, 0x04, 0xA0, 0x09, 0x50, 0x0A, 0xEE, 0xEE, 0xA0, 0x1E, 0x00, 0x00, 0xE1, 0x6A, 0x00, 0x00, 0x96,
  0xC5, 0x00, 0x00, 0x5C, 0x00, 0x00, 0xC6, 0x00, 0x00, 0x08, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0xC0, 0x00,
  0x00, 0x3B, 0xA3, 0x00, 0x00, 0x86, 0x59, 0x00, 0x00, 0xD1, 0x1D, 0x00, 0x04, 0xA0, 0x09, 0x50, 0x0A, 0xEE, 0xEE, 0xA0,
  0x1E, 0x00, 0x00, 0xE1, 0x6A, 0x00, 0x00, 0x96, 0xC5, 0x00, 0x00, 0x5C, 0x00, 0x1D, 0xD1, 0x00, 0x00, 0x95, 0x5A, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0xC0, 0x00, 0x00, 0x3B, 0xA3, 0x00, 0x00, 0x86, 0x59, 0x00, 0x00, 0xD1, 0x1D, 0x00,
  0x04, 0xA0, 0x09, 0x50, 0x0A, 0xEE, 0xEE, 0xA0, 0x1E, 0x00, 0x00, 0xE1, 0x6A, 0x00, 0x00, 0x96, 0xC5, 0x00, 0x00, 0x5C,
  0x00, 0x9C, 0x49, 0x10, 0x00, 0xA4, 0xCA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0xC0, 0x00, 0x00, 0x3B, 0xA3, 0x00,
  0x00, 0x86, 0x59, 0x00, 0x00, 0xD1, 0x1D, 0x00, 0x04, 0xA0, 0x09, 0x50, 0x0A, 0xEE, 0xEE, 0xA0, 0x1E, 0x00, 0x00, 0xE1,
  0x6A, 0x00, 0x00, 0x96, 0xC5, 0x00, 0x00, 0x5C, 0x00, 0x5C, 0xDD, 0xA1, 0x00, 0x5D, 0x30, 0x08, 0xC0, 0x0C, 0x60, 0x00,
  0x05, 0x01, 0xF1, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x01, 0xF1, 0x00, 0x00, 0x00, 0x0C, 0x60, 0x00, 0x08, 0x10,
  0x4E, 0x30, 0x08, 0xC0, 0x00, 0x4C, 0xDD, 0x91, 0x00, 0x00, 0x0A, 0x30, 0x00, 0x00, 0x00, 0x3B, 0x00, 0x00, 0x00, 0x2A,
  0x60, 0x00, 0x00, 0x5D, 0x10, 0x00, 0x00, 0x05, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD1, 0x2F, 0x00,
  0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xA0, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00,
  0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD4, 0x00, 0x01, 0xD4, 0x00, 0x00, 0x09, 0x40, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD1, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0xDD,
  0xDD, 0xA0, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD4, 0x00, 0x1D,
  0xD1, 0x00, 0x00, 0xA5, 0x5A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD1, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00,
  0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xA0, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x2F, 0x00,
  0x00, 0x00, 0x2F, 0xDD, 0xDD, 0xD4, 0x1D, 0x50, 0x01, 0xB1, 0x00, 0x00, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0,
  0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x08, 0xB0, 0x3B, 0x10, 0x00, 0x00, 0x2F, 0x00, 0x2F, 0x00,
  0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x2F, 0x00, 0x08, 0xF6, 0x04, 0xA2, 0xB2, 0x00,
  0x00, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x02,
  0xF0, 0x00, 0x2F, 0x00, 0x00, 0x4E, 0x84, 0x80, 0x00, 0x08, 0x38, 0xE3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xF9, 0x00,
  0x02, 0xE0, 0x2F, 0xD3, 0x00, 0x2E, 0x02, 0xF5, 0xC0, 0x02, 0xE0, 0x2F, 0x0B, 0x60, 0x2E, 0x02, 0xF0, 0x3D, 0x12, 0xE0,
  0x2F, 0x00, 0x98, 0x2E, 0x02, 0xF0, 0x01, 0xE4, 0xE0, 0x2F, 0x00, 0x06, 0xDE, 0x02, 0xF0, 0x00, 0x0C, 0xE0, 0x00, 0x03,
  0x70, 0x00, 0x00, 0x00, 0x00, 0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x04, 0xE4,
  0x00, 0x5E, 0x20, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x1F, 0x10, 0x00, 0x04, 0xD0, 0x2F, 0x00, 0x00, 0x03, 0xE0, 0x1F, 0x10,
  0x00, 0x04, 0xD0, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x04, 0xE4, 0x00, 0x5D, 0x20, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x00, 0x00,
  0x17, 0x20, 0x00, 0x00, 0x00, 0xA5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x04, 0xE4,
  0x00, 0x5E, 0x20, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x1F, 0x10, 0x00, 0x04, 0xD0, 0x2F, 0x00, 0x00, 0x03, 0xE0, 0x1F, 0x10,
  0x00, 0x04, 0xD0, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x04, 0xE4, 0x00, 0x5D, 0x20, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x00, 0x00,
  0x66, 0x00, 0x00, 0x00, 0x08, 0x78, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x04, 0xE4,
  0x00, 0x5E, 0x20, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x1F, 0x10, 0x00, 0x04, 0xD0, 0x2F, 0x00, 0x00, 0x03, 0xE0, 0x1F, 0x10,
  0x00, 0x04, 0xD0, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x04, 0xE4, 0x00, 0x5D, 0x20, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x00, 0x0C,
  0xB3, 0x90, 0x00, 0x00, 0x38, 0x5D, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x04, 0xE4,
  0x00, 0x5E, 0x20, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x1F, 0x10, 0x00, 0x04, 0xD0, 0x2F, 0x00, 0x00, 0x03, 0xE0, 0x1F, 0x10,
  0x00, 0x04, 0xD0, 0x0C, 0x60, 0x00, 0x08, 0x90, 0x04, 0xE4, 0x00, 0x5D, 0x20, 0x00, 0x4B, 0xDD, 0xA2, 0x00, 0x00, 0x07,
  0x30, 0x00, 0x00, 0x00, 0x2A, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E,
  0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x01, 0xF2,
  0x00, 0x05, 0xC0, 0x09, 0xA1, 0x02, 0xC6, 0x00, 0x08, 0xDD, 0xC6, 0x00, 0x00, 0x00, 0x46, 0x00, 0x00, 0x00, 0x5A, 0x10,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F,
  0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x01, 0xF2, 0x00, 0x05, 0xC0, 0x09, 0xA1, 0x02,
  0xC6, 0x00, 0x08, 0xDD, 0xC6, 0x00, 0x00, 0x03, 0x82, 0x00, 0x00, 0x04, 0xA5, 0xB3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02,
  0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00,
  0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x01, 0xF2, 0x00, 0x05, 0xC0, 0x09, 0xA1, 0x02, 0xC6, 0x00, 0x08, 0xDD, 0xC6, 0x00,
  0x00, 0x2C, 0x2C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00,
  0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x2F, 0x00, 0x00, 0x2E, 0x02, 0xF0, 0x00, 0x02, 0xE0, 0x1F, 0x20, 0x00, 0x5C,
  0x00, 0x9A, 0x10, 0x2C, 0x60, 0x00, 0x8D, 0xDC, 0x60, 0x00, 0x00, 0x63, 0x00, 0x00, 0x01, 0x92, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x2C, 0xDC, 0x40, 0x0B, 0x70, 0x6C, 0x00, 0x00, 0x02, 0xE0, 0x05, 0xCD, 0xDE, 0x01, 0xF4, 0x03, 0xE0, 0x1F, 0x10,
  0x9F, 0x00, 0x8E, 0xC3, 0xCC, 0x00, 0x02, 0x70, 0x00, 0x01, 0xA2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0xDC, 0x40, 0x0B,
  0x70, 0x6C, 0x00, 0x00, 0x02, 0xE0, 0x05, 0xCD, 0xDE, 0x01, 0xF4, 0x03, 0xE0, 0x1F, 0x10, 0x9F, 0x00, 0x8E, 0xC3, 0xCC,
  0x00, 0x27, 0x20, 0x00, 0x1A, 0x5A, 0x20, 0x00, 0x00, 0x00, 0x00, 0x2C, 0xDC, 0x40, 0x0B, 0x70, 0x6C, 0x00, 0x00, 0x02,
  0xE0, 0x05, 0xCD, 0xDE, 0x01, 0xF4, 0x03, 0xE0, 0x1F, 0x10, 0x9F, 0x00, 0x8E, 0xC3, 0xCC, 0x00, 0xCA, 0x39, 0x00, 0x47,
  0x7E, 0x50, 0x00, 0x00, 0x00, 0x00, 0x2C, 0xDC, 0x40, 0x0B, 0x70, 0x6C, 0x00, 0x00, 0x02, 0xE0, 0x05, 0xCD, 0xDE, 0x01,
  0xF4, 0x03, 0xE0, 0x1F, 0x10, 0x9F, 0x00, 0x8E, 0xC3, 0xCC, 0x02, 0xBD, 0xC4, 0x00, 0xB6, 0x04, 0xE0, 0x0F, 0x10, 0x01,
  0x02, 0xF0, 0x00, 0x00, 0x0F, 0x10, 0x02, 0x00, 0xB7, 0x03, 0xE0, 0x02, 0xBD, 0xC3, 0x00, 0x00, 0xC3, 0x00, 0x00, 0x04,
  0xC0, 0x00, 0x03, 0xA6, 0x00, 0x00, 0x36, 0x00, 0x00, 0x00, 0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2B, 0xDC, 0x30, 0x0B,
  0x70, 0x2D, 0x00, 0xF1, 0x00, 0xA3, 0x2F, 0xDD, 0xDD, 0x40, 0xF1, 0x00, 0x00, 0x0B, 0x70, 0x19, 0x10, 0x2B, 0xDD, 0x60,
  0x00, 0x01, 0x71, 0x00, 0x00, 0x94, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2B, 0xDC, 0x30, 0x0B, 0x70, 0x3D, 0x00, 0xF1, 0x00,
  0xB3, 0x2F, 0xDD, 0xDD, 0x40, 0xF1, 0x00, 0x00, 0x0B, 0x70, 0x19, 0x10, 0x2B, 0xDD, 0x60, 0x00, 0x17, 0x40, 0x00, 0x1A,
  0x5A, 0x30, 0x00, 0x00, 0x00, 0x00, 0x2B, 0xDC, 0x30, 0x0B, 0x70, 0x3D, 0x00, 0xF1, 0x00, 0xC3, 0x2F, 0xDD, 0xDE, 0x40,
  0xF1, 0x00, 0x00, 0x0B, 0x60, 0x1A, 0x10, 0x2B, 0xDD, 0x60, 0x06, 0x10, 0x03, 0xA1, 0x00, 0x00, 0x02, 0xF0, 0x02, 0xF0,
  0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x02, 0xF0, 0x03, 0x54, 0xA1, 0x00, 0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x2F,
  0x02, 0xF0, 0x2F, 0x02, 0xF0, 0x02, 0x62, 0x03, 0xA5, 0xA2, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00,
  0x02, 0xF0, 0x00, 0x2F, 0x00, 0x02, 0xF0, 0x00, 0x2F, 0x00, 0x04, 0xD7, 0x57, 0x00, 0x84, 0x9D, 0x20, 0x00, 0x00, 0x00,
  0x02, 0xD6, 0xCD, 0x50, 0x2F, 0x60, 0x5C, 0x02, 0xF1, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00,
  0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x00, 0x37, 0x00, 0x00, 0x00, 0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1A, 0xDD, 0x91, 0x0B,
  0x80, 0x0A, 0x80, 0xF1, 0x00, 0x4C, 0x2F, 0x00, 0x02, 0xE0, 0xF1, 0x00, 0x4C, 0x0A, 0x80, 0x0A, 0x80, 0x1A, 0xDD, 0x91,
  0x00, 0x00, 0x65, 0x00, 0x00, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1A, 0xDD, 0x91, 0x0B, 0x80, 0x0A, 0x80, 0xF1, 0x00,
  0x4C, 0x2F, 0x00, 0x02, 0xE0, 0xF1, 0x00, 0x4C, 0x0A, 0x80, 0x0A, 0x80, 0x1A, 0xDD, 0x91, 0x00, 0x07, 0x60, 0x00, 0x1A,
  0x67, 0x90, 0x00, 0x00, 0x00, 0x00, 0x1A, 0xDD, 0x91, 0x0B, 0x80, 0x0A, 0x80, 0xF1, 0x00, 0x4C, 0x2F, 0x00, 0x02, 0xE0,
  0xF1, 0x00, 0x4C, 0x0A, 0x80, 0x0A, 0x80, 0x1A, 0xDD, 0x91, 0x00, 0xCC, 0x47, 0x30, 0x48, 0x5C, 0xC0, 0x00, 0x00, 0x00,
  0x00, 0x1A, 0xDD, 0x91, 0x0B, 0x80, 0x0A, 0x80, 0xF1, 0x00, 0x4C, 0x2F, 0x00, 0x02, 0xE0, 0xF1, 0x00, 0x4C, 0x0A, 0x80,
  0x0A, 0x80, 0x1A, 0xDD, 0x91, 0x00, 0x53, 0x00, 0x00, 0x01, 0x93, 0x00, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x02, 0xE0, 0x2F,
  0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x03, 0xE0, 0x1F, 0x30, 0x9E, 0x00, 0x7E, 0xC5, 0xE0,
  0x00, 0x03, 0x50, 0x00, 0x03, 0x91, 0x00, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02,
  0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x03, 0xE0, 0x1F, 0x30, 0x9E, 0x00, 0x7E, 0xC5, 0xE0, 0x00, 0x26, 0x10, 0x00, 0x3A,
  0x5A, 0x10, 0x00, 0x00, 0x00, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02,
  0xF0, 0x03, 0xE0, 0x1F, 0x30, 0x9E, 0x00, 0x7E, 0xC5, 0xE0, 0x02, 0xC2, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x2E,
  0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x2E, 0x02, 0xF0, 0x02, 0xE0, 0x2F, 0x00, 0x3E, 0x01, 0xF3, 0x09, 0xE0, 0x07, 0xEC,
  0x5E, 0x00, 0xDD, 0xDD, 0xDD, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xDD, 0xDD, 0xDD, 0xDD,
  0xDD, 0xDD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x0A, 0x01, 0x80, 0x2F, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2E, 0x00, 0xA0, 0x03, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0A, 0x0A, 0x18, 0x18, 0x2F, 0x2E, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2E, 0x2D, 0x0A, 0x09, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x02, 0xC0, 0x02, 0xC0, 0x02, 0xC0, 0x00,
};

static const GlyphArimoAA FONTE_ARIMO_A4_GLYPHS[148] PROGMEM = {
  {0, 3, 0, 0, 0, 4}, // U+0020
  {0, 3, 9, 0, -9, 4}, // U+0021
  {14, 5, 9, 0, -9, 5}, // U+0022
  {37, 7, 9, 0, -9, 7}, // U+0023
  {69, 6, 10, 0, -9, 7}, // U+0024
  {99, 11, 9, 0, -9, 11}, // U+0025
  {149, 9, 9, 0, -9, 9}, // U+0026
  {190, 3, 9, 0, -9, 3}, // U+0027
  {204, 5, 12, 0, -9, 4}, // U+0028
  {234, 5, 12, -1, -9, 4}, // U+0029
  {264, 5, 9, 0, -9, 5}, // U+002A
  {287, 7, 7, 0, -7, 8}, // U+002B
  {312, 3, 3, 0, -1, 4}, // U+002C
  {317, 4, 4, 0, -4, 4}, // U+002D
  {325, 3, 1, 0, -1, 4}, // U+002E
  {327, 4, 9, 0, -9, 4}, // U+002F
  {345, 7, 9, 0, -9, 7}, // U+0030
  {377, 7, 9, 0, -9, 7}, // U+0031
  {409, 7, 9, 0, -9, 7}, // U+0032
  {441, 7, 9, 0, -9, 7}, // U+0033
  {473, 8, 9, 0, -9, 7}, // U+0034
  {509, 7, 9, 0, -9, 7}, // U+0035
  {541, 7, 9, 0, -9, 7}, // U+0036
  {573, 7, 9, 0, -9, 7}, // U+0037
  {605, 7, 9, 0, -9, 7}, // U+0038
  {637, 7, 9, 0, -9, 7}, // U+0039
  {669, 3, 7, 0, -7, 4}, // U+003A
  {680, 3, 9, 0, -7, 4}, // U+003B
  {694, 8, 8, 0, -8, 8}, // U+003C
  {726, 7, 6, 0, -6, 8}, // U+003D
  {747, 8, 8, 0, -8, 8}, // U+003E
  {779, 7, 9, 0, -9, 7}, // U+003F
  {811, 12, 11, 0, -9, 13}, // U+0040
  {877, 8, 9, 0, -9, 9}, // U+0041
  {913, 8, 9, 0, -9, 9}, // U+0042
  {949, 9, 9, 0, -9, 9}, // U+0043
  {990, 9, 9, 0, -9, 9}, // U+0044
  {1031, 8, 9, 0, -9, 9}, // U+0045
  {1067, 7, 9, 0, -9, 8}, // U+0046
  {1099, 10, 9, 0, -9, 10}, // U+0047
  {1144, 9, 9, 0, -9, 9}, // U+0048
  {1185, 3, 9, 0, -9, 4}, // U+0049
  {1199, 6, 9, 0, -9, 6}, // U+004A
  {1226, 8, 9, 0, -9, 9}, // U+004B
  {1262, 7, 9, 0, -9, 7}, // U+004C
  {1294, 10, 9, 0, -9, 10}, // U+004D
  {1339, 9, 9, 0, -9, 9}, // U+004E
  {1380, 10, 9, 0, -9, 10}, // U+004F
  {1425, 8, 9, 0, -9, 9}, // U+0050
  {1461, 10, 12, 0, -9, 10}, // U+0051
  {1521, 9, 9, 0, -9, 9}, // U+0052
  {1562, 8, 9, 0, -9, 9}, // U+0053
  {1598, 7, 9, 0, -9, 8}, // U+0054
  {1630, 9, 9, 0, -9, 9}, // U+0055
  {1671, 8, 9, 0, -9, 9}, // U+0056
  {1707, 12, 9, 0, -9, 12}, // U+0057
  {1761, 8, 9, 0, -9, 9}, // U+0058
  {1797, 9, 9, 0, -9, 9}, // U+0059
  {1838, 8, 9, 0, -9, 8}, // U+005A
  {1874, 4, 12, 0, -9, 4}, // U+005B
  {1898, 4, 9, 0, -9, 4}, // U+005C
  {1916, 4, 12, 0, -9, 4}, // U+005D
  {1940, 6, 9, 0, -9, 6}, // U+005E
  {1967, 8, 3, -1, 0, 7}, // U+005F
  {1979, 4, 10, 0, -10, 4}, // U+0060
  {1999, 7, 7, 0, -7, 7}, // U+0061
  {2024, 6, 9, 0, -9, 7}, // U+0062
  {2051, 7, 7, 0, -7, 6}, // U+0063
  {2076, 7, 9, 0, -9, 7}, // U+0064
  {2108, 7, 7, 0, -7, 7}, // U+0065
  {2133, 5, 9, -1, -9, 4}, // U+0066
  {2156, 7, 10, 0, -7, 7}, // U+0067
  {2191, 7, 9, 0, -9, 7}, // U+0068
  {2223, 3, 9, 0, -9, 3}, // U+0069
  {2237, 4, 12, -1, -9, 3}, // U+006A
  {2261, 7, 9, 0, -9, 6}, // U+006B
  {2293, 3, 9, 0, -9, 3}, // U+006C
  {2307, 11, 7, 0, -7, 10}, // U+006D
  {2346, 7, 7, 0, -7, 7}, // U+006E
  {2371, 7, 7, 0, -7, 7}, // U+006F
  {2396, 6, 10, 0, -7, 7}, // U+0070
  {2426, 7, 10, 0, -7, 7}, // U+0071
  {2461, 4, 8, 0, -8, 4}, // U+0072
  {2477, 6, 7, 0, -7, 6}, // U+0073
  {2498, 4, 9, 0, -9, 4}, // U+0074
  {2516, 7, 7, 0, -7, 7}, // U+0075
  {2541, 6, 7, 0, -7, 6}, // U+0076
  {2562, 10, 7, -1, -7, 9}, // U+0077
  {2597, 6, 7, 0, -7, 6}, // U+0078
  {2618, 6, 10, 0, -7, 6}, // U+0079
  {2648, 7, 7, 0, -7, 7}, // U+007A
  {2673, 5, 12, 0, -9, 5}, // U+007B
  {2703, 3, 12, 0, -9, 4}, // U+007C
  {2721, 5, 12, 0, -9, 5}, // U+007D
  {2751, 8, 5, 0, -5, 8}, // U+007E
  {2771, 7, 11, 0, -9, 7}, // U+00A7
  {2810, 5, 9, 0, -9, 5}, // U+00AA
  {2833, 7, 6, 0, -6, 7}, // U+00AB
  {2854, 5, 9, 0, -9, 5}, // U+00B0
  {2877, 4, 9, 0, -9, 5}, // U+00BA
  {2895, 7, 6, 0, -6, 7}, // U+00BB
  {2916, 8, 12, 0, -12, 9}, // U+00C0
  {2964, 8, 12, 0, -12, 9}, // U+00C1
  {3012, 8, 12, 0, -12, 9}, // U+00C2
  {3060, 8, 12, 0, -12, 9}, // U+00C3
  {3108, 9, 12, 0, -9, 9}, // U+00C7
  {3162, 8, 12, 0, -12, 9}, // U+00C8
  {3210, 8, 12, 0, -12, 9}, // U+00C9
  {3258, 8, 12, 0, -12, 9}, // U+00CA
  {3306, 4, 12, -1, -12, 4}, // U+00CC
  {3330, 4, 12, 0, -12, 4}, // U+00CD
  {3354, 5, 12, -1, -12, 4}, // U+00CE
  {3384, 9, 12, 0, -12, 9}, // U+00D1
  {3438, 10, 12, 0, -12, 10}, // U+00D2
  {3498, 10, 12, 0, -12, 10}, // U+00D3
  {3558, 10, 12, 0, -12, 10}, // U+00D4
  {3618, 10, 12, 0, -12, 10}, // U+00D5
  {3678, 9, 12, 0, -12, 9}, // U+00D9
  {3732, 9, 12, 0, -12, 9}, // U+00DA
  {3786, 9, 12, 0, -12, 9}, // U+00DB
  {3840, 9, 11, 0, -11, 9}, // U+00DC
  {3890, 7, 10, 0, -10, 7}, // U+00E0
  {3925, 7, 10, 0, -10, 7}, // U+00E1
  {3960, 7, 10, 0, -10, 7}, // U+00E2
  {3995, 7, 10, 0, -10, 7}, // U+00E3
  {4030, 7, 10, 0, -7, 6}, // U+00E7
  {4065, 7, 10, 0, -10, 7}, // U+00E8
  {4100, 7, 10, 0, -10, 7}, // U+00E9
  {4135, 7, 10, 0, -10, 7}, // U+00EA
  {4170, 4, 10, 0, -10, 4}, // U+00EC
  {4190, 3, 10, 0, -10, 4}, // U+00ED
  {4205, 5, 10, -1, -10, 4}, // U+00EE
  {4230, 7, 10, 0, -10, 7}, // U+00F1
  {4265, 7, 10, 0, -10, 7}, // U+00F2
  {4300, 7, 10, 0, -10, 7}, // U+00F3
  {4335, 7, 10, 0, -10, 7}, // U+00F4
  {4370, 7, 10, 0, -10, 7}, // U+00F5
  {4405, 7, 10, 0, -10, 7}, // U+00F9
  {4440, 7, 10, 0, -10, 7}, // U+00FA
  {4475, 7, 10, 0, -10, 7}, // U+00FB
  {4510, 7, 9, 0, -9, 7}, // U+00FC
  {4542, 7, 4, 0, -4, 7}, // U+2013
  {4556, 12, 4, 0, -4, 12}, // U+2014
  {4580, 3, 9, 0, -9, 3}, // U+2018
  {4594, 3, 9, 0, -9, 3}, // U+2019
  {4608, 4, 9, 0, -9, 5}, // U+201C
  {4626, 4, 9, 0, -9, 5}, // U+201D
  {4644, 13, 1, 0, -1, 13}, // U+2026
};

// 16 niveis de verde RGB565 para o antialias sobre fundo preto.
static const uint16_t VERDE_AA[16] = {
  0x0000, 0x0080, 0x0100, 0x0180,
  0x0200, 0x02A0, 0x0320, 0x03A0,
  0x0440, 0x04C0, 0x0540, 0x05C0,
  0x0660, 0x06E0, 0x0760, 0x07E0
};

int indiceGlyphArimo(uint16_t cp)
{
  if(cp>=32 && cp<=126) return (int)cp-32;
  if(cp==0x00A0) return 0; // espaco nao separavel

  switch(cp){
    case 0x00A7: return 95;
    case 0x00AA: return 96;
    case 0x00AB: return 97;
    case 0x00B0: return 98;
    case 0x00BA: return 99;
    case 0x00BB: return 100;
    case 0x00C0: return 101;
    case 0x00C1: return 102;
    case 0x00C2: return 103;
    case 0x00C3: return 104;
    case 0x00C7: return 105;
    case 0x00C8: return 106;
    case 0x00C9: return 107;
    case 0x00CA: return 108;
    case 0x00CC: return 109;
    case 0x00CD: return 110;
    case 0x00CE: return 111;
    case 0x00D1: return 112;
    case 0x00D2: return 113;
    case 0x00D3: return 114;
    case 0x00D4: return 115;
    case 0x00D5: return 116;
    case 0x00D9: return 117;
    case 0x00DA: return 118;
    case 0x00DB: return 119;
    case 0x00DC: return 120;
    case 0x00E0: return 121;
    case 0x00E1: return 122;
    case 0x00E2: return 123;
    case 0x00E3: return 124;
    case 0x00E7: return 125;
    case 0x00E8: return 126;
    case 0x00E9: return 127;
    case 0x00EA: return 128;
    case 0x00EC: return 129;
    case 0x00ED: return 130;
    case 0x00EE: return 131;
    case 0x00F1: return 132;
    case 0x00F2: return 133;
    case 0x00F3: return 134;
    case 0x00F4: return 135;
    case 0x00F5: return 136;
    case 0x00F9: return 137;
    case 0x00FA: return 138;
    case 0x00FB: return 139;
    case 0x00FC: return 140;
    case 0x2013: return 141;
    case 0x2014: return 142;
    case 0x2018: return 143;
    case 0x2019: return 144;
    case 0x201C: return 145;
    case 0x201D: return 146;
    case 0x2026: return 147;
    default: return ('?'-32);
  }
}

int avancoGlyphArimo(uint16_t cp)
{
  int idx=indiceGlyphArimo(cp);
  return pgm_read_byte(&FONTE_ARIMO_A4_GLYPHS[idx].advance);
}

// =====================================================
// ESTADO GERAL
// =====================================================
enum TelaAtual { TELA_PASTAS, TELA_LEITOR, TELA_BUSCA_TEXTO, TELA_SPLASH, TELA_RELACOES, TELA_JURIS_CATEGORIAS, TELA_REFERENCIAS };
TelaAtual telaAtual = TELA_PASTAS;
// O tipo de busca nao depende de o teclado virtual estar visivel.
enum BuscaAtiva { BUSCA_NENHUMA, BUSCA_ARTIGO, BUSCA_TEXTO };
BuscaAtiva buscaAtiva = BUSCA_NENHUMA;

bool tecladoConectado = false;
bool touchAnterior = false;
bool sdOK = false;

// Um unico relogio de atividade; subtracao unsigned tolera rollover de millis().
const uint32_t TIMEOUT_TELA_MS = 180000UL;
volatile uint32_t ultimaInteracaoMs = 0;
volatile bool displayApagado = false;
volatile bool pedirAcordarDisplay = false;
uint16_t teclaDespertar = 0;
bool ignorarTouchAteSoltar = false;

bool registrarAtividadeUsuario()
{
  ultimaInteracaoMs=(uint32_t)millis();
  if(displayApagado || pedirAcordarDisplay){
    pedirAcordarDisplay=true;
    return true; // Esta entrada serve apenas para acordar.
  }
  return false;
}


// =====================================================
// PASTAS
// =====================================================
#define MAX_PASTAS 48
#define PASTAS_VISIVEIS 6

String pastas[MAX_PASTAS];
bool itemEhPasta[MAX_PASTAS];
int totalPastas = 0;
int pastaSelecionada = 0;
int primeiraPastaVisivel = 0;
String statusSD = "";

volatile int deltaPastas = 0;
volatile int deltaLeitor = 0;
volatile bool pedirAbrir = false;
volatile bool pedirVoltar = false;
volatile bool pedirBuscar = false;
volatile bool pedirRedesenharBusca = false;
volatile bool pedirBuscaTexto = false;
volatile bool pedirBackTexto = false;
volatile bool pedirFecharSplash = false;
volatile int deltaRelacoes = 0;
volatile uint8_t pedirCategoriaRelacao = 0;
volatile bool pedirAbrirRelacao = false;
uint8_t enterTextoPressionado = 0;
uint8_t backTextoPressionado = 0;
uint8_t enterSplashPressionado = 0;

// Diagnostico leve: agrega 32 movimentos antes de escrever no Serial, para
// que a propria instrumentacao nao introduza travadas perceptiveis no scroll.
uint32_t perfScrollTotalUs=0;
uint32_t perfScrollMaxUs=0;
uint16_t perfScrollAmostras=0;

// Temporario: desativar apos identificar o botao fisico escolhido.
#define DIAGNOSTICO_HID 1

bool ehEnterFisico(uint8_t usage)
{
  return usage==0x28 || usage==0x58; // Enter principal / Enter numerico.
}

void solicitarBuscaTexto()
{
  if(buscaAtiva==BUSCA_TEXTO &&
     (telaAtual==TELA_BUSCA_TEXTO || telaAtual==TELA_LEITOR)) pedirBuscaTexto=true;
}

// =====================================================
// LEITOR TXT
// =====================================================
String pastaAtual = "/";
String caminhoArquivoAtual = "";
String nomeArquivoAtual = "";
String artigoDigitado = "";
uint32_t tamanhoArquivoAtual = 0;

// =====================================================
// CAMADA JURIDICA V1 - INDICE REVERSO ARTIGO -> REFERENCIAS
// =====================================================
// Primeira integracao deliberadamente pequena e isolada:
// - a lei seca continua sendo o leitor principal;
// - o indice existente do CDC e lido somente apos uma busca de artigo;
// - o rodape oferece atalhos numericos sem alterar o TXT da lei;
// - os arquivos de sumulas/repetitivos continuam sendo a fonte unica do texto.

#define MAX_RELACOES_ARTIGO 32
#define RELACOES_VISIVEIS 6

enum CategoriaRelacao {
  REL_NENHUMA=0,
  REL_CORRELATAS=1,
  REL_SUMULAS=2,
  REL_SUMULAS_VINCULANTES=3,
  REL_ACORDAOS=4,
  REL_REPERCUSSAO_GERAL=5,
  REL_REPETITIVOS=6,
  REL_PRECEDENTES_RELEVANTES=7,
  REL_JURIS_TODAS=8,
  REL_OUTROS=9
};

// Tipagem extensivel. O piloto usa SV/RG, mas o parser nao depende deles.
enum TipoJurisprudencia {
  JTIPO_SV=0, JTIPO_SUMULA_STF, JTIPO_RG, JTIPO_REPETITIVO_STJ,
  JTIPO_IAC, JTIPO_SIRDR, JTIPO_ADI, JTIPO_ADC, JTIPO_ADPF,
  JTIPO_ACORDAO, JTIPO_OUTRO
};

struct RelacaoJuridica {
  String referencia;
  String tribunal;
  String tipo;
  String numero;
  String status;
  String arquivo;
  String caminho;
};

struct CorrelataJuridica {
  String origem;
  String relacaoId;
  String normaId;
  String normaDestino;
  String modoAbertura;
  String artigoDestino;
  String pastaDestino;   // V1 legado
  String caminhoTXT;     // V2
};

// Os indices do SD sao parseados uma unica vez. O conjunto contextual exibido
// continua pequeno; estes vetores sao apenas a fonte em RAM para as consultas.
#define MAX_REGISTROS_INDICE_JUR 128
#define MAX_REGISTROS_INDICE_COR 128
#define CONTEXTOS_LRU 4
RelacaoJuridica *indiceJurisCache=nullptr;
CorrelataJuridica *indiceCorrelatasCache=nullptr;
int totalIndiceJurisCache=0, totalIndiceCorrelatasCache=0;
bool indicesContextuaisCarregados=false;

struct ResultadoContextoLRU {
  String chave;
  uint8_t juris[MAX_RELACOES_ARTIGO];
  uint8_t correlatas[MAX_RELACOES_ARTIGO];
  uint8_t totalJuris, totalCorrelatas;
  uint32_t uso;
  bool valido;
};
ResultadoContextoLRU contextosLRU[CONTEXTOS_LRU];
uint32_t relogioContextosLRU=0;

// Prototipos explicitos: evitam que o pre-processador do Arduino IDE
// gere declaracoes automaticas antes de conhecer os tipos customizados
// RelacaoJuridica e CategoriaRelacao.
String caminhoArquivoRelacao(RelacaoJuridica &r);
String primeiroTXTDaPasta(String pasta);
String localizarArquivoRecursivo(const String &pasta, const String &arquivo, int profundidade);
bool carregarIndicesContextuais();
bool carregarCacheJurisCF();
TipoJurisprudencia classificarTipoJurisprudencia(String tipo);
String rotuloTipoJurisprudencia(const RelacaoJuridica &r);
void abrirCategoriaRelacao(CategoriaRelacao categoria);
void desenharBarraBusca();
String nomeCategoriaRelacao(CategoriaRelacao categoria);
int quantidadeCategoriaRelacao(CategoriaRelacao categoria);

RelacaoJuridica relacoesArtigo[MAX_RELACOES_ARTIGO];
CorrelataJuridica correlatasArtigo[MAX_RELACOES_ARTIGO];
int totalRelacoesArtigo=0;
int totalSumulasArtigo=0;
int totalSumulasVinculantesArtigo=0;
int totalAcordaosArtigo=0;
int totalRepercussaoGeralArtigo=0;
int totalRepetitivosArtigo=0;
int totalPrecedentesRelevantesArtigo=0;
int totalOutrosJurisArtigo=0;
int totalCorrelatasArtigo=0;
int totalReferenciasArtigo=0;
bool menuRelacoesAtivo=false;
bool modoDigitacaoArtigo=true;
String artigoRelacoes="";

CategoriaRelacao categoriaRelacaoAtual=REL_NENHUMA;
int indicesRelacaoCategoria[MAX_RELACOES_ARTIGO];
int totalRelacoesCategoria=0;
int relacaoSelecionada=0;
int primeiraRelacaoVisivel=0;
CategoriaRelacao categoriasJurisDisponiveis[8];
int totalCategoriasJuris=0;
int categoriaJurisSelecionada=0;

// Ao abrir uma sumula/tema, guardamos apenas o minimo necessario para voltar
// exatamente ao contexto do artigo, sem duplicar o grande indice de linhas.
bool visualizandoReferencia=false;
String origemCaminhoArtigo="";
String origemNomeArtigo="";
uint32_t origemTamanhoArtigo=0;
uint32_t origemTopoByte=0;
String origemArtigoDigitado="";
String contextoRelacoesRotulo="";
String contextoDocumentoReferencia="";
CategoriaRelacao origemCategoriaRelacao=REL_NENHUMA;
int origemRelacaoSelecionada=0;
int origemPrimeiraRelacaoVisivel=0;
int origemCategoriaJurisSelecionada=0;

const char *CAMINHO_INDICE_CDC =
  "/9-CÓDIGO DE DEFESA DO CONSUMIDOR/99_INDICES/INDICE_JURISPRUDENCIA_CDC.txt";
const char *CAMINHO_INDICE_CORRELATAS =
  "/99_RELATIONS_V1/01_CORRELATAS/INDICE_CORRELATAS.txt";

// Relations V2 / ESP32 - gerados pela ETAPA 2E.5.
const char *CAMINHO_REL_LOOKUP_V2 =
  "/99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX";
const char *CAMINHO_RELACOES_V2 =
  "/99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX";
const char *CAMINHO_EXT_NORMAS_V2 =
  "/99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_NORMAS.IDX";
const char *CAMINHO_EXT_ARTIGOS_V2 =
  "/99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX";

// Jurisprudencia constitucional piloto J3. Estrutura separada de Relations V2.
const char *CAMINHO_JUR_LOOKUP_CF =
  "/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX";
const char *CAMINHO_JURISPRUDENCIA_CF =
  "/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX";
const char *PASTA_CONTEUDO_JURIS_CF =
  "/99_JURISPRUDENCIA_V2/03_CONTEUDO";

// Cache compacto do Relations V2. O lookup da CF deixa de abrir/varrer o SD
// a cada mudanca de inciso/paragrafo. Com PSRAM habilitada, estes blocos ficam
// fora do heap interno usado pelo BLE.
#define MAX_LOOKUP_V2_CACHE 64
#define MAX_NORMAS_V2_CACHE 32

struct LookupRelationsV2Cache {
  char norma[8];
  char artigo[12];
  char paragrafo[12];
  char inciso[16];
  char alinea[4];
  uint32_t offset;
  uint8_t quantidade;
};

struct NormaExternaV2Cache {
  char id[32];
  char nome[72];
  char caminho[192];
};

LookupRelationsV2Cache *lookupV2Cache=nullptr;
NormaExternaV2Cache *normasV2Cache=nullptr;
char *relacoesV2Cache=nullptr;
size_t tamanhoRelacoesV2Cache=0;
int totalLookupV2Cache=0;
int totalNormasV2Cache=0;
bool cacheRelationsV2Carregado=false;

// Limite defensivo contra arquivo corrompido; nao e capacidade operacional.
// A capacidade real e contada no arquivo e alocada dinamicamente em PSRAM.
#define MAX_JUR_LOOKUPS_SEGURANCA 4096
struct LookupJurisCFCache {
  char norma[8];
  char artigo[12];
  char paragrafo[12];
  char inciso[16];
  char alinea[4];
  uint32_t offset;
  uint8_t quantidade;
};

LookupJurisCFCache *jurLookupCFCache=nullptr;
char *jurisprudenciaCFCache=nullptr;
size_t tamanhoJurisprudenciaCFCache=0;
int totalJurLookupCFCache=0;
size_t capacidadeJurLookupCFCache=0;
int totalRegistrosJurisCFCache=0;
bool cacheJurisCFCarregado=false;
bool cacheJurisCFTentado=false;
bool cacheJurisCFEmPSRAM=false;
uint32_t perfJurisLookupTotalUs=0;
uint32_t perfJurisLookupMaxUs=0;
uint32_t perfJurisLookupQuantidade=0;

// Declaracao explicita porque o cache V2 e definido antes da implementacao
// do parser pipe no sketch.
String campoPipe(const String &linha, int campo);

static inline void copiarCampoV2(char *destino, size_t capacidade, const String &origem)
{
  if(!destino || capacidade==0) return;
  size_t n=origem.length();
  if(n>=capacidade) n=capacidade-1;
  memcpy(destino,origem.c_str(),n);
  destino[n]='\0';
}

bool carregarCacheRelationsV2()
{
  if(cacheRelationsV2Carregado) return true;
  if(!sdOK) return false;
  if(!SD.exists(CAMINHO_REL_LOOKUP_V2) || !SD.exists(CAMINHO_EXT_NORMAS_V2) ||
     !SD.exists(CAMINHO_RELACOES_V2))
    return false;

  bool temPSRAM=psramFound();
  auto alocar=[&](size_t bytes)->void* {
    void *p=nullptr;
    if(temPSRAM) p=heap_caps_malloc(bytes,MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if(!p) p=heap_caps_malloc(bytes,MALLOC_CAP_8BIT);
    return p;
  };

  if(!lookupV2Cache)
    lookupV2Cache=(LookupRelationsV2Cache*)alocar(sizeof(LookupRelationsV2Cache)*MAX_LOOKUP_V2_CACHE);
  if(!normasV2Cache)
    normasV2Cache=(NormaExternaV2Cache*)alocar(sizeof(NormaExternaV2Cache)*MAX_NORMAS_V2_CACHE);

  if(!lookupV2Cache || !normasV2Cache){
    Serial.println("RELV2 CACHE: memoria insuficiente");
    return false;
  }

  memset(lookupV2Cache,0,sizeof(LookupRelationsV2Cache)*MAX_LOOKUP_V2_CACHE);
  memset(normasV2Cache,0,sizeof(NormaExternaV2Cache)*MAX_NORMAS_V2_CACHE);
  totalLookupV2Cache=0;
  totalNormasV2Cache=0;

  uint32_t t0=micros();

  File f=SD.open(CAMINHO_REL_LOOKUP_V2,FILE_READ);
  if(!f) return false;
  while(f.available() && totalLookupV2Cache<MAX_LOOKUP_V2_CACHE){
    String linha=f.readStringUntil('\n');
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') continue;

    LookupRelationsV2Cache &r=lookupV2Cache[totalLookupV2Cache++];
    copiarCampoV2(r.norma,sizeof(r.norma),campoPipe(linha,0));
    copiarCampoV2(r.artigo,sizeof(r.artigo),campoPipe(linha,1));
    copiarCampoV2(r.paragrafo,sizeof(r.paragrafo),campoPipe(linha,2));
    copiarCampoV2(r.inciso,sizeof(r.inciso),campoPipe(linha,3));
    copiarCampoV2(r.alinea,sizeof(r.alinea),campoPipe(linha,4));
    r.offset=(uint32_t)campoPipe(linha,5).toInt();
    int q=campoPipe(linha,6).toInt();
    if(q<0) q=0; if(q>255) q=255;
    r.quantidade=(uint8_t)q;
  }
  f.close();

  File fn=SD.open(CAMINHO_EXT_NORMAS_V2,FILE_READ);
  if(!fn) return false;
  while(fn.available() && totalNormasV2Cache<MAX_NORMAS_V2_CACHE){
    String linha=fn.readStringUntil('\n');
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') continue;

    NormaExternaV2Cache &n=normasV2Cache[totalNormasV2Cache++];
    copiarCampoV2(n.id,sizeof(n.id),campoPipe(linha,0));
    copiarCampoV2(n.nome,sizeof(n.nome),campoPipe(linha,1));
    copiarCampoV2(n.caminho,sizeof(n.caminho),campoPipe(linha,2));
  }
  fn.close();

  // REL_LOOKUP.IDX guarda offsets absolutos dentro de RELACOES.IDX. Mantendo
  // uma copia byte a byte deste arquivo na PSRAM, os mesmos offsets continuam
  // validos e a semantica juridica nao muda. Se a PSRAM/cache falhar, a rotina
  // de consulta conserva o caminho anterior e le diretamente do SD.
  File fr=SD.open(CAMINHO_RELACOES_V2,FILE_READ);
  if(fr){
    size_t bytes=(size_t)fr.size();
    if(temPSRAM && bytes>0){
      relacoesV2Cache=(char*)heap_caps_malloc(bytes+1,MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
      if(relacoesV2Cache){
        size_t lidos=fr.read((uint8_t*)relacoesV2Cache,bytes);
        if(lidos==bytes){
          relacoesV2Cache[bytes]='\0';
          tamanhoRelacoesV2Cache=bytes;
        }else{
          heap_caps_free(relacoesV2Cache);
          relacoesV2Cache=nullptr;
        }
      }
    }
    fr.close();
  }

  cacheRelationsV2Carregado=true;
  Serial.printf("RELV2 CACHE: lookup=%d normas=%d relacoes=%u bytes tempo=%lu ms (%s)\\n",
                totalLookupV2Cache,totalNormasV2Cache,
                (unsigned)tamanhoRelacoesV2Cache,
                (micros()-t0)/1000,temPSRAM?"PSRAM":"RAM");
  return true;
}

TipoJurisprudencia classificarTipoJurisprudencia(String tipo)
{
  tipo.toLowerCase();
  if(tipo=="sumula_vinculante" || tipo=="sv") return JTIPO_SV;
  if(tipo=="sumula_stf" || tipo=="sumula") return JTIPO_SUMULA_STF;
  if(tipo=="repercussao_geral" || tipo=="rg") return JTIPO_RG;
  if(tipo=="repetitivo_stj" || tipo.indexOf("repetitivo")>=0) return JTIPO_REPETITIVO_STJ;
  if(tipo=="iac") return JTIPO_IAC;
  if(tipo=="sirdr") return JTIPO_SIRDR;
  if(tipo=="adi") return JTIPO_ADI;
  if(tipo=="adc") return JTIPO_ADC;
  if(tipo=="adpf") return JTIPO_ADPF;
  if(tipo=="acordao") return JTIPO_ACORDAO;
  return JTIPO_OUTRO;
}

String rotuloTipoJurisprudencia(const RelacaoJuridica &r)
{
  switch(classificarTipoJurisprudencia(r.tipo)){
    case JTIPO_SV: return "SV "+r.numero;
    case JTIPO_SUMULA_STF: return "SUMULA STF "+r.numero;
    case JTIPO_RG: return "RG TEMA "+r.numero;
    case JTIPO_REPETITIVO_STJ: return "REPETITIVO STJ "+r.numero;
    case JTIPO_IAC: return "IAC "+r.numero;
    case JTIPO_SIRDR: return "SIRDR "+r.numero;
    case JTIPO_ADI: return "ADI "+r.numero;
    case JTIPO_ADC: return "ADC "+r.numero;
    case JTIPO_ADPF: return "ADPF "+r.numero;
    case JTIPO_ACORDAO: return "ACORDAO "+r.numero;
    default: return "OUTRO "+r.numero;
  }
}

String arquivoDetalheJurisCF(String identificador)
{
  identificador.replace(":","_");
  identificador.replace("/","_");
  return identificador+".TXT";
}

bool carregarCacheJurisCF()
{
  if(cacheJurisCFCarregado) return true;
  if(cacheJurisCFTentado) return false;
  cacheJurisCFTentado=true;
  if(!sdOK || !SD.exists(CAMINHO_JUR_LOOKUP_CF) ||
     !SD.exists(CAMINHO_JURISPRUDENCIA_CF)) return false;

  uint32_t t0=micros();
  uint32_t psramAntes=ESP.getFreePsram();
  auto falhar=[&](const char *motivo)->bool {
    if(jurLookupCFCache){ heap_caps_free(jurLookupCFCache); jurLookupCFCache=nullptr; }
    if(jurisprudenciaCFCache){ heap_caps_free(jurisprudenciaCFCache); jurisprudenciaCFCache=nullptr; }
    totalJurLookupCFCache=0;
    capacidadeJurLookupCFCache=0;
    totalRegistrosJurisCFCache=0;
    tamanhoJurisprudenciaCFCache=0;
    cacheJurisCFCarregado=false;
    cacheJurisCFEmPSRAM=false;
    Serial.printf("JUR CACHE: falha=%s fonte=SD-FALLBACK\n",motivo);
    return false;
  };

  if(!psramFound()) return falhar("PSRAM indisponivel");

  // Primeira passagem: conta exatamente as entradas. Ela ocorre apenas no boot.
  File f=SD.open(CAMINHO_JUR_LOOKUP_CF,FILE_READ);
  if(!f) return falhar("lookup inacessivel");
  size_t quantidadeLookups=0;
  while(f.available()){
    String linha=f.readStringUntil('\n');
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') continue;
    quantidadeLookups++;
    if(quantidadeLookups>MAX_JUR_LOOKUPS_SEGURANCA){
      f.close();
      return falhar("quantidade de lookups acima do limite de seguranca");
    }
  }
  f.close();
  if(quantidadeLookups==0) return falhar("lookup vazio");

  size_t bytesLookup=sizeof(LookupJurisCFCache)*quantidadeLookups;
  jurLookupCFCache=(LookupJurisCFCache*)heap_caps_malloc(
    bytesLookup,MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  if(!jurLookupCFCache) return falhar("alocacao PSRAM do lookup");
  memset(jurLookupCFCache,0,bytesLookup);
  capacidadeJurLookupCFCache=quantidadeLookups;

  auto inteiroValido=[](const String &valor, uint32_t &saida)->bool {
    if(valor.length()==0) return false;
    char *fim=nullptr;
    unsigned long n=strtoul(valor.c_str(),&fim,10);
    if(fim==valor.c_str() || *fim!='\0') return false;
    saida=(uint32_t)n;
    return true;
  };

  // Segunda passagem: carrega e valida o schema sem qualquer corte silencioso.
  f=SD.open(CAMINHO_JUR_LOOKUP_CF,FILE_READ);
  if(!f) return falhar("lookup inacessivel na segunda passagem");
  totalJurLookupCFCache=0;
  while(f.available()){
    String linha=f.readStringUntil('\n');
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') continue;
    if((size_t)totalJurLookupCFCache>=capacidadeJurLookupCFCache){
      f.close();
      return falhar("contagem do lookup mudou durante a carga");
    }
    String norma=campoPipe(linha,0),artigo=campoPipe(linha,1);
    String offsetTexto=campoPipe(linha,5),quantidadeTexto=campoPipe(linha,6);
    uint32_t offset=0,q=0;
    if(norma.length()==0 || artigo.length()==0 ||
       !inteiroValido(offsetTexto,offset) || !inteiroValido(quantidadeTexto,q) ||
       q==0 || q>255){
      f.close();
      return falhar("linha de lookup corrompida");
    }
    LookupJurisCFCache &r=jurLookupCFCache[totalJurLookupCFCache++];
    copiarCampoV2(r.norma,sizeof(r.norma),norma);
    copiarCampoV2(r.artigo,sizeof(r.artigo),artigo);
    copiarCampoV2(r.paragrafo,sizeof(r.paragrafo),campoPipe(linha,2));
    copiarCampoV2(r.inciso,sizeof(r.inciso),campoPipe(linha,3));
    copiarCampoV2(r.alinea,sizeof(r.alinea),campoPipe(linha,4));
    r.offset=offset;
    r.quantidade=(uint8_t)q;
  }
  f.close();
  if((size_t)totalJurLookupCFCache!=quantidadeLookups)
    return falhar("quantidade carregada inconsistente");

  File fi=SD.open(CAMINHO_JURISPRUDENCIA_CF,FILE_READ);
  if(!fi) return falhar("indice de registros inacessivel");
  size_t bytes=(size_t)fi.size();
  if(bytes==0 || bytes>16U*1024U*1024U){
    fi.close();
    return falhar("tamanho do indice de registros invalido");
  }
  jurisprudenciaCFCache=(char*)heap_caps_malloc(
    bytes+1,MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  if(!jurisprudenciaCFCache){
    fi.close();
    return falhar("alocacao PSRAM dos registros");
  }
  size_t lidos=fi.read((uint8_t*)jurisprudenciaCFCache,bytes);
  fi.close();
  if(lidos!=bytes) return falhar("leitura incompleta dos registros");
  jurisprudenciaCFCache[bytes]='\0';
  tamanhoJurisprudenciaCFCache=bytes;
  int linhas=0;
  for(size_t i=0;i<bytes;i++) if(jurisprudenciaCFCache[i]=='\n') linhas++;
  totalRegistrosJurisCFCache=max(0,linhas-1); // desconta o cabecalho
  if(totalRegistrosJurisCFCache<=0) return falhar("indice de registros vazio");

  // Offsets devem iniciar uma linha e cada quantidade deve caber integralmente.
  uint32_t somaQuantidades=0;
  for(int i=0;i<totalJurLookupCFCache;i++){
    const LookupJurisCFCache &r=jurLookupCFCache[i];
    if(r.offset>=bytes || (r.offset>0 && jurisprudenciaCFCache[r.offset-1]!='\n'))
      return falhar("offset fora do indice ou desalinhado");
    size_t cursor=r.offset;
    for(int n=0;n<r.quantidade;n++){
      if(cursor>=bytes) return falhar("quantidade ultrapassa o indice");
      while(cursor<bytes && jurisprudenciaCFCache[cursor]!='\n') cursor++;
      if(cursor>=bytes) return falhar("registro sem terminador de linha");
      cursor++;
    }
    somaQuantidades+=r.quantidade;
  }
  if(somaQuantidades!=(uint32_t)totalRegistrosJurisCFCache)
    return falhar("quantidade total inconsistente");

  cacheJurisCFEmPSRAM=true;
  cacheJurisCFCarregado=true;
  size_t usados=bytesLookup+bytes+1;
  Serial.printf("JUR CACHE: lookups=%d registros=%d bytes=%u local=PSRAM PSRAM_livre_antes=%u PSRAM_livre_depois=%u tempo=%lu ms fonte=CACHE\n",
                totalJurLookupCFCache,totalRegistrosJurisCFCache,(unsigned)usados,
                (unsigned)psramAntes,(unsigned)ESP.getFreePsram(),
                (micros()-t0)/1000);
  return true;
}

// Estado da busca independente da rolagem e do cache do leitor.
String numeroUltimaBusca = "";
uint32_t offsetUltimaOcorrencia = 0;
uint32_t inicioProximaBusca = 0;
bool temOcorrenciaDaBusca = false;
bool numeroBuscaEditado = false;

void reiniciarEstadoBusca()
{
  numeroUltimaBusca="";
  offsetUltimaOcorrencia=0;
  inicioProximaBusca=0;
  temOcorrenciaDaBusca=false;
  numeroBuscaEditado=false;
}

// Busca textual independente: teclado virtual produz ASCII sem acentos.
const int MAX_CONSULTA_TEXTO=80;
const int MAX_TERMOS_TEXTO=40;
const int JANELA_TERMOS_TEXTO=120;
const int MAX_HISTORICO_TEXTO=32;
char consultaTexto[MAX_CONSULTA_TEXTO+1]={0};
char ultimaConsultaTexto[MAX_CONSULTA_TEXTO+1]={0};
int cursorBuscaTexto=0;
uint32_t offsetUltimoTexto=0; // Primeiro byte original da ocorrencia.
uint32_t offsetFinalTexto=0; // Ultimo byte original, inclusive.
uint32_t inicioProximoTexto=0;
uint32_t historicoInicioTexto[MAX_HISTORICO_TEXTO];
uint32_t historicoFimTexto[MAX_HISTORICO_TEXTO];
uint8_t totalHistoricoTexto=0;
uint8_t indiceHistoricoTexto=0;
bool temResultadoTexto=false;
bool destaqueTextoAtivo=false;
bool consultaTextoEditada=false;
const char *statusBuscaTexto="Digite palavra ou frase";

void reiniciarBuscaTexto()
{
  consultaTexto[0]='\0';
  ultimaConsultaTexto[0]='\0';
  cursorBuscaTexto=0;
  offsetUltimoTexto=0;
  offsetFinalTexto=0;
  inicioProximoTexto=0;
  totalHistoricoTexto=0;
  indiceHistoricoTexto=0;
  temResultadoTexto=false;
  destaqueTextoAtivo=false;
  consultaTextoEditada=false;
  statusBuscaTexto="Digite palavra ou frase";
}

// Arimo proporcional rasterizada diretamente em 12 px, com antialias A4.
// Nao ha ampliacao de pixels; as metricas abaixo pertencem ao novo raster.
#define LEITOR_LINHAS_VISIVEIS 12
#define MAX_LINHAS_INDEXADAS 16000
#define LEITOR_TEXTO_W 312
#define LEITOR_LINHA_H 15
#define LEITOR_BASELINE 12

// A diferenca da v4: NAO indexamos o arquivo inteiro ao abrir.
// Janela de linhas alcancadas: cada offset e um byte ABSOLUTO do TXT.
// linhaTopo e apenas um indice nesta janela; inicio real do arquivo e sempre 0.
// Depois de uma busca, offsetsLinhas[0] pode ser >0 e a janela pode crescer para tras.
uint32_t offsetsLinhas[MAX_LINHAS_INDEXADAS];
int linhasIndexadas = 0;
bool fimDoArquivoIndexado = false;
int linhaTopo = 0;

// Cache SOMENTE do texto visivel. Como a fonte agora e proporcional,
// uma linha pode conter mais caracteres estreitos; 384 bytes deixam folga
// inclusive para UTF-8 sem criar framebuffer grande.
#define BYTES_CACHE_LINHA 384
char cacheLeitor[LEITOR_LINHAS_VISIVEIS][BYTES_CACHE_LINHA];
bool inicioFisicoCache[LEITOR_LINHAS_VISIVEIS];
bool linhaCacheValida[LEITOR_LINHAS_VISIVEIS];
uint32_t offsetLinhaCache[LEITOR_LINHAS_VISIVEIS];
ContextoJuridicoAtivo contextoLinhasCache[LEITOR_LINHAS_VISIVEIS];
ContextoJuridicoAtivo contextoAntesCache;
ContextoJuridicoAtivo contextoJuridicoAtivo;
#define MAX_CHECKPOINTS_CONTEXTO 128
struct CheckpointContexto {
  uint32_t offset;
  ContextoJuridicoAtivo contexto; // contexto imediatamente antes de offset
  bool valido;
};
CheckpointContexto *checkpointsContexto=nullptr;
int proximoCheckpointContexto=0;
String arquivoCheckpoints="";
// Intervalos no cache derivados dos bytes ORIGINAIS; o texto nao e modificado.
uint16_t destaqueInicioCache[LEITOR_LINHAS_VISIVEIS];
uint16_t destaqueFimCache[LEITOR_LINHAS_VISIVEIS];
bool cacheLeitorValido = false;
int cacheLeitorTopo = -1;

// Buffer RGB de UMA linha do leitor (~9,4 KB), estatico e seguro.
// Nao existe framebuffer da tela inteira.
#define LEITOR_BUFFER_W 312
uint16_t bufferLinhaLeitor[LEITOR_BUFFER_W * LEITOR_LINHA_H];

// =====================================================
// TOUCH / GESTO
// =====================================================
bool touchAtivo = false;
int ultimoTouchY = 0;
int acumuladorTouch = 0;
int inicioTouchX=0, inicioTouchY=0, itemTouch=-1;
bool touchArrastou=false, touchConsumido=false;

// =====================================================
// UTF-8 / ACENTOS PORTUGUESES
// =====================================================
// O fonte padrao do Adafruit_GFX nao entende UTF-8 diretamente.
// Esta rotina desenha as letras acentuadas PT-BR usando a letra base +
// o sinal grafico (agudo, til, circunflexo, cedilha etc.).

uint16_t proximoUnicode(const String &s, int &i)
{
  if (i >= (int)s.length()) return 0;

  uint8_t b0 = (uint8_t)s[i++];
  if (b0 < 0x80) return b0;

  if ((b0 & 0xE0) == 0xC0 && i < (int)s.length()) {
    uint8_t b1 = (uint8_t)s[i++];
    return ((uint16_t)(b0 & 0x1F) << 6) | (b1 & 0x3F);
  }

  if ((b0 & 0xF0) == 0xE0 && i + 1 < (int)s.length()) {
    uint8_t b1 = (uint8_t)s[i++];
    uint8_t b2 = (uint8_t)s[i++];
    return ((uint16_t)(b0 & 0x0F) << 12) |
           ((uint16_t)(b1 & 0x3F) << 6) |
           (b2 & 0x3F);
  }

  // Ignora continuacoes extras de caracteres de 4 bytes.
  while (i < (int)s.length() && (((uint8_t)s[i] & 0xC0) == 0x80)) i++;
  return '?';
}

enum TipoAcento { AC_NENHUM, AC_AGUDO, AC_GRAVE, AC_CIRC, AC_TIL, AC_TREMA, AC_CEDILHA };

void desenharCaractereUnicode(int x, int y, uint16_t cp, uint16_t cor, uint16_t fundo)
{
  char base = '?';
  TipoAcento ac = AC_NENHUM;

  if (cp >= 32 && cp <= 126) {
    base = (char)cp;
  } else {
    switch (cp) {
      case 0x00C0: base='A'; ac=AC_GRAVE; break; case 0x00E0: base='a'; ac=AC_GRAVE; break;
      case 0x00C1: base='A'; ac=AC_AGUDO; break; case 0x00E1: base='a'; ac=AC_AGUDO; break;
      case 0x00C2: base='A'; ac=AC_CIRC;  break; case 0x00E2: base='a'; ac=AC_CIRC;  break;
      case 0x00C3: base='A'; ac=AC_TIL;   break; case 0x00E3: base='a'; ac=AC_TIL;   break;
      case 0x00C7: base='C'; ac=AC_CEDILHA; break; case 0x00E7: base='c'; ac=AC_CEDILHA; break;
      case 0x00C8: base='E'; ac=AC_GRAVE; break; case 0x00E8: base='e'; ac=AC_GRAVE; break;
      case 0x00C9: base='E'; ac=AC_AGUDO; break; case 0x00E9: base='e'; ac=AC_AGUDO; break;
      case 0x00CA: base='E'; ac=AC_CIRC;  break; case 0x00EA: base='e'; ac=AC_CIRC;  break;
      case 0x00CC: base='I'; ac=AC_GRAVE; break; case 0x00EC: base='i'; ac=AC_GRAVE; break;
      case 0x00CD: base='I'; ac=AC_AGUDO; break; case 0x00ED: base='i'; ac=AC_AGUDO; break;
      case 0x00CE: base='I'; ac=AC_CIRC;  break; case 0x00EE: base='i'; ac=AC_CIRC;  break;
      case 0x00D2: base='O'; ac=AC_GRAVE; break; case 0x00F2: base='o'; ac=AC_GRAVE; break;
      case 0x00D3: base='O'; ac=AC_AGUDO; break; case 0x00F3: base='o'; ac=AC_AGUDO; break;
      case 0x00D4: base='O'; ac=AC_CIRC;  break; case 0x00F4: base='o'; ac=AC_CIRC;  break;
      case 0x00D5: base='O'; ac=AC_TIL;   break; case 0x00F5: base='o'; ac=AC_TIL;   break;
      case 0x00D9: base='U'; ac=AC_GRAVE; break; case 0x00F9: base='u'; ac=AC_GRAVE; break;
      case 0x00DA: base='U'; ac=AC_AGUDO; break; case 0x00FA: base='u'; ac=AC_AGUDO; break;
      case 0x00DB: base='U'; ac=AC_CIRC;  break; case 0x00FB: base='u'; ac=AC_CIRC;  break;
      case 0x00DC: base='U'; ac=AC_TREMA; break; case 0x00FC: base='u'; ac=AC_TREMA; break;
      case 0x00BA: base='o'; break;
      case 0x00AA: base='a'; break;
      case 0x00A7: base='S'; break;
      case 0x2013: base='-'; break;
      case 0x2014: base='-'; break;
      case 0x2018: case 0x2019: base='\''; break;
      case 0x201C: case 0x201D: base='"'; break;
      case 0x2026: base='.'; break;
      default: base='?'; break;
    }
  }

  // O glifo fica 1 px abaixo, deixando espaco para o acento.
  tft.drawChar(x, y + 1, base, cor, fundo, 1);

  switch (ac) {
    case AC_AGUDO:
      tft.drawPixel(x+4, y, cor); tft.drawPixel(x+3, y+1, cor); break;
    case AC_GRAVE:
      tft.drawPixel(x+1, y, cor); tft.drawPixel(x+2, y+1, cor); break;
    case AC_CIRC:
      tft.drawPixel(x+2, y+1, cor); tft.drawPixel(x+3, y, cor); tft.drawPixel(x+4, y+1, cor); break;
    case AC_TIL:
      tft.drawPixel(x+1, y+1, cor); tft.drawPixel(x+2, y, cor);
      tft.drawPixel(x+3, y, cor);   tft.drawPixel(x+4, y+1, cor); break;
    case AC_TREMA:
      tft.drawPixel(x+1, y, cor); tft.drawPixel(x+4, y, cor); break;
    case AC_CEDILHA:
      tft.drawPixel(x+3, y+9, cor); tft.drawPixel(x+2, y+8, cor); break;
    default: break;
  }
}

int imprimirUTF8(int x, int y, const String &texto, uint16_t cor, uint16_t fundo, int maxChars = -1)
{
  int i = 0;
  int col = 0;
  while (i < (int)texto.length()) {
    if (maxChars >= 0 && col >= maxChars) break;
    uint16_t cp = proximoUnicode(texto, i);
    if (cp == '\n' || cp == '\r') break;
    if (cp == '\t') cp = ' ';
    desenharCaractereUnicode(x + col * 6, y, cp, cor, fundo);
    col++;
  }
  return col;
}

int contarCaracteresUTF8(const String &texto)
{
  int i=0, n=0;
  while (i < (int)texto.length()) { proximoUnicode(texto, i); n++; }
  return n;
}

// =====================================================
// VISUAL
// =====================================================
void centralizarTexto(const String &texto, int y, int tamanho, uint16_t cor)
{
  tft.setTextSize(tamanho);
  tft.setTextColor(cor, COR_FUNDO);
  int largura = texto.length() * 6 * tamanho;
  int x = (320 - largura) / 2;
  if (x < 0) x = 0;
  tft.setCursor(x, y);
  tft.print(texto);
}

void desenharMolduraCyber()
{
  tft.drawRect(2, 2, 316, 236, COR_VERDE_ESCURO);
  tft.drawFastHLine(2, 2, 18, COR_VERDE);   tft.drawFastVLine(2, 2, 18, COR_VERDE);
  tft.drawFastHLine(300, 2, 18, COR_VERDE); tft.drawFastVLine(317, 2, 18, COR_VERDE);
  tft.drawFastHLine(2, 237, 18, COR_VERDE); tft.drawFastVLine(2, 219, 18, COR_VERDE);
  tft.drawFastHLine(300,237,18,COR_VERDE);  tft.drawFastVLine(317,219,18,COR_VERDE);
}

void desenharSplashLexMachina()
{
  // O overload const/PROGMEM do Adafruit_GFX usa writePixel() para cada pixel.
  // Uma linha pequena em RAM permite uma unica janela e transferencias SPI em bloco.
  static uint16_t linhaSplash[LEX_BOOT_WIDTH];
  tft.startWrite();
  tft.setAddrWindow(0,0,LEX_BOOT_WIDTH,LEX_BOOT_HEIGHT);
  for(uint16_t y=0;y<LEX_BOOT_HEIGHT;y++){
    uint32_t base=(uint32_t)y*LEX_BOOT_WIDTH;
    for(uint16_t x=0;x<LEX_BOOT_WIDTH;x++)
      linhaSplash[x]=pgm_read_word(&lex_boot_screen[base+x]);
    tft.writePixels(linhaSplash,LEX_BOOT_WIDTH);
  }
  tft.endWrite();
}

// =====================================================
// TOUCH
// =====================================================
bool lerTouchRaw(int &rawX, int &rawY)
{
  Wire.beginTransmission(FT_ADDR); Wire.write(0x02);
  if (Wire.endTransmission(false) != 0) return false;
  Wire.requestFrom(FT_ADDR, (uint8_t)1);
  if (!Wire.available()) return false;
  uint8_t qtd = Wire.read() & 0x0F;
  if (qtd == 0 || qtd > 2) return false;

  Wire.beginTransmission(FT_ADDR); Wire.write(0x03);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(FT_ADDR, (uint8_t)4) != 4) return false;

  uint8_t xh=Wire.read(), xl=Wire.read(), yh=Wire.read(), yl=Wire.read();
  rawX=((xh & 0x0F)<<8)|xl;
  rawY=((yh & 0x0F)<<8)|yl;
  return true;
}

void converterTouch(int rawX, int rawY, int &xTela, int &yTela)
{
  float x=(-0.00149f*rawX)+(-1.04252f*rawY)+322.812f;
  float y=(1.15374f*rawX)+(-0.08449f*rawY)-4.575f;
  xTela=(int)(x+0.5f);
  yTela=(int)(y+0.5f);
  yTela=120+(int)((yTela-120)*0.90f);
  xTela=constrain(xTela,0,319);
  yTela=constrain(yTela,0,239);
}

// =====================================================
// SD
// =====================================================
bool iniciarSDUmaVez()
{
  digitalWrite(TFT_CS,HIGH);
  digitalWrite(SD_CS,HIGH);
#if LEX_DEVICE_V1_ENABLED
  // DEVICE V1: mesmos pino/SPI/frequencias/mountpoint; so max_files sobe de 5 (padrao do core) para LEXV1_SD_MAX_FILES.
  // format_if_empty=false explicito: o DEVICE V1 nunca formata o cartao.
  sdOK=SD.begin(SD_CS,spiBus,12000000,"/sd",LEXV1_SD_MAX_FILES,false);
  if(!sdOK){
    SD.end();
    sdOK=SD.begin(SD_CS,spiBus,4000000,"/sd",LEXV1_SD_MAX_FILES,false);
  }
#else
  sdOK=SD.begin(SD_CS,spiBus,12000000);
  if(!sdOK){
    SD.end();
    sdOK=SD.begin(SD_CS,spiBus,4000000);
  }
#endif
  return sdOK;
}

String somenteNome(const String &caminho)
{
  int p=caminho.lastIndexOf('/');
  if(p>=0 && p<(int)caminho.length()-1) return caminho.substring(p+1);
  return caminho;
}

bool terminaComTXT(String nome)
{
  nome.toLowerCase();
  return nome.endsWith(".txt");
}

String caminhoFilho(const String &pasta, const String &nome)
{
  return pasta=="/" ? "/"+nome : pasta+"/"+nome;
}

// -----------------------------------------------------
// RELACOES JURIDICAS - LEITURA DO INDICE EXISTENTE
// -----------------------------------------------------
String campoPipe(const String &linha, int campo)
{
  int inicio=0;
  for(int atual=0; atual<campo; atual++){
    int p=linha.indexOf('|',inicio);
    if(p<0) return "";
    inicio=p+1;
  }
  int fim=linha.indexOf('|',inicio);
  if(fim<0) fim=linha.length();
  String r=linha.substring(inicio,fim);
  r.trim();
  return r;
}

String somenteDigitos(const String &texto)
{
  String r="";
  for(unsigned int i=0;i<texto.length();i++)
    if(texto[i]>='0' && texto[i]<='9') r+=texto[i];
  return r;
}

bool referenciaEhDoArtigoCDC(const String &referencia, const String &artigo)
{
  const String prefixo="CDC art. ";
  if(!referencia.startsWith(prefixo)) return false;
  int inicio=prefixo.length();
  int fim=referencia.indexOf(',',inicio);
  if(fim<0) fim=referencia.length();
  String parte=referencia.substring(inicio,fim);
  return somenteDigitos(parte)==somenteDigitos(artigo);
}

int especificidadeReferenciaAtiva(const String &referencia, const String &artigo)
{
  if(!referenciaEhDoArtigoCDC(referencia,artigo)) return -1;
  int nivel=1;
  int virgula=referencia.indexOf(',');
  if(virgula<0) return nivel;

  String detalhe=referencia.substring(virgula+1);
  detalhe.trim();
  String par=contextoJuridicoAtivo.paragrafo;
  String inc=contextoJuridicoAtivo.inciso;
  String ali=contextoJuridicoAtivo.alinea;

  int marcaPar=detalhe.indexOf("§");
  if(marcaPar>=0){
    if(par.length()==0) return -1;
    int fimPar=detalhe.indexOf(',',marcaPar);
    String trechoPar=fimPar<0?detalhe.substring(marcaPar):detalhe.substring(marcaPar,fimPar);
    String digitosRef=somenteDigitos(trechoPar);
    String digitosAtivo=somenteDigitos(par);
    if(digitosRef.length()>0 || digitosAtivo.length()>0){
      if(digitosRef!=digitosAtivo) return -1;
    }else{
      String refUnico=trechoPar; refUnico.toLowerCase();
      String ativoUnico=par; ativoUnico.toLowerCase();
      if(refUnico.indexOf("nico")<0 || ativoUnico.indexOf("nico")<0) return -1;
    }
    nivel=2;
    if(fimPar>=0) detalhe=detalhe.substring(fimPar+1);
    else detalhe="";
    detalhe.trim();
  }

  if(detalhe.length()>0){
    int fimInc=detalhe.indexOf(',');
    String trechoInc=fimInc<0?detalhe:detalhe.substring(0,fimInc);
    trechoInc.trim(); trechoInc.toUpperCase();
    String incAtivo=inc; incAtivo.trim(); incAtivo.toUpperCase();
    if(incAtivo.length()==0 || trechoInc!=incAtivo) return -1;
    nivel=3;
    if(fimInc>=0){
      String trechoAli=detalhe.substring(fimInc+1);
      trechoAli.trim(); trechoAli.toLowerCase();
      String aliAtiva=ali; aliAtiva.trim(); aliAtiva.toLowerCase();
      trechoAli.replace(")","");
      if(aliAtiva.length()==0 || trechoAli!=aliAtiva) return -1;
      nivel=4;
    }
  }
  return nivel;
}

bool arquivoAtualPertenceAoCDC()
{
  return caminhoArquivoAtual.startsWith("/9-CÓDIGO DE DEFESA DO CONSUMIDOR/");
}

bool arquivoAtualPertenceACF()
{
  return caminhoArquivoAtual.startsWith("/1- CONSTITUIÇÃO FEDERAL/") ||
         caminhoArquivoAtual.startsWith("/1-CONSTITUIÇÃO FEDERAL/");
}

String normaOrigemRelationsV2Atual()
{
  if(arquivoAtualPertenceACF()) return "CF88";
  return "";
}

String rotuloOrigemRelationsV2(const String &norma,
                               const String &artigo,
                               const String &paragrafo,
                               const String &inciso,
                               const String &alinea)
{
  String r=(norma=="CF88")?"CF ART. ":"ART. ";
  r+=artigo;
  if(paragrafo.length()){
    if(paragrafo=="unico") r+=", PAR. UNICO";
    else r+=", § "+paragrafo+"º";
  }
  if(inciso.length()) r+=", "+inciso;
  if(alinea.length()) r+=", "+alinea+")";
  return r;
}

bool linhaLookupV2Igual(const String &linha,
                        const String &norma,
                        const String &artigo,
                        const String &paragrafo,
                        const String &inciso,
                        const String &alinea)
{
  return campoPipe(linha,0)==norma &&
         campoPipe(linha,1)==artigo &&
         campoPipe(linha,2)==paragrafo &&
         campoPipe(linha,3)==inciso &&
         campoPipe(linha,4)==alinea;
}

bool buscarLookupRelationsV2(const String &norma,
                             const String &artigo,
                             const String &paragrafo,
                             const String &inciso,
                             const String &alinea,
                             uint32_t &offset,
                             int &quantidade)
{
  offset=0; quantidade=0;
  if(!carregarCacheRelationsV2()) return false;

  for(int i=0;i<totalLookupV2Cache;i++){
    const LookupRelationsV2Cache &r=lookupV2Cache[i];
    if(norma==r.norma && artigo==r.artigo &&
       paragrafo==r.paragrafo && inciso==r.inciso && alinea==r.alinea){
      offset=r.offset;
      quantidade=r.quantidade;
      return quantidade>0;
    }
  }
  return false;
}

bool buscarMelhorLookupRelationsV2(const String &norma,
                                   const String &artigo,
                                   uint32_t &offset,
                                   int &quantidade,
                                   String &parUsado,
                                   String &incUsado,
                                   String &aliUsada)
{
  String par=contextoJuridicoAtivo.paragrafo;
  String inc=contextoJuridicoAtivo.inciso;
  String ali=contextoJuridicoAtivo.alinea;

  struct Tentativa { String p,i,a; };
  Tentativa tentativas[4];
  int total=0;

  // Mais especifico -> menos especifico. Inciso/alinea podem existir sem
  // paragrafo (ex.: CF art. 5, XLIII e art. 34, V, b), portanto nao exigimos
  // paragrafo para tentar essas chaves.
  if(ali.length()) tentativas[total++]={par,inc,ali};
  if(inc.length()) tentativas[total++]={par,inc,""};
  if(par.length()) tentativas[total++]={par,"",""};
  tentativas[total++]={"","",""};

  for(int i=0;i<total;i++){
    if(buscarLookupRelationsV2(norma,artigo,
                               tentativas[i].p,tentativas[i].i,tentativas[i].a,
                               offset,quantidade)){
      parUsado=tentativas[i].p;
      incUsado=tentativas[i].i;
      aliUsada=tentativas[i].a;
      return true;
    }
  }
  return false;
}

bool resolverNormaExternaV2(const String &id, String &nome, String &caminho)
{
  if(!carregarCacheRelationsV2()) return false;
  for(int i=0;i<totalNormasV2Cache;i++){
    const NormaExternaV2Cache &n=normasV2Cache[i];
    if(id==n.id){
      nome=String(n.nome);
      caminho=String(n.caminho);
      return caminho.length()>0;
    }
  }
  return false;
}

bool buscarOffsetArtigoExternoV2(const String &id,
                                 const String &artigo,
                                 uint32_t &offset)
{
  offset=0;
  File f=SD.open(CAMINHO_EXT_ARTIGOS_V2,FILE_READ);
  if(!f) return false;
  while(f.available()){
    String linha=f.readStringUntil('\n');
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') continue;
    if(campoPipe(linha,0)==id && campoPipe(linha,1)==artigo){
      offset=(uint32_t)campoPipe(linha,2).toInt();
      f.close();
      return true;
    }
  }
  f.close();
  return false;
}

void adicionarCorrelataV2(const String &origem,
                          const String &relacaoId,
                          const String &normaId,
                          const String &normaDestino,
                          const String &modo,
                          const String &artigoDestino,
                          const String &caminhoTXT)
{
  if(totalCorrelatasArtigo>=MAX_RELACOES_ARTIGO) return;
  CorrelataJuridica &c=correlatasArtigo[totalCorrelatasArtigo++];
  c.origem=origem;
  c.relacaoId=relacaoId;
  c.normaId=normaId;
  c.normaDestino=normaDestino;
  c.modoAbertura=modo;
  c.artigoDestino=artigoDestino;
  c.pastaDestino="";
  c.caminhoTXT=caminhoTXT;
}

bool carregarCorrelatasRelationsV2(const String &artigo)
{
  String norma=normaOrigemRelationsV2Atual();
  if(norma.length()==0) return false;
  if(!relacoesV2Cache &&
     (!SD.exists(CAMINHO_REL_LOOKUP_V2) || !SD.exists(CAMINHO_RELACOES_V2)))
    return false;

  uint32_t offset=0;
  int quantidade=0;
  String parUsado="",incUsado="",aliUsada="";
  if(!buscarMelhorLookupRelationsV2(norma,artigo,offset,quantidade,
                                    parUsado,incUsado,aliUsada))
    return false;

  String origem=rotuloOrigemRelationsV2(norma,artigo,parUsado,incUsado,aliUsada);
  auto processarLinha=[&](String linha)->bool {
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') return false;

    String relacaoId=campoPipe(linha,5);
    String normaId=campoPipe(linha,6);
    String nome=campoPipe(linha,7);
    String modo=campoPipe(linha,8);
    String artigos=campoPipe(linha,9);
    String caminho=campoPipe(linha,10);

    // EXT_NORMAS.IDX e a fonte compacta canonica do caminho/nome.
    String nomeCanonico="", caminhoCanonico="";
    if(resolverNormaExternaV2(normaId,nomeCanonico,caminhoCanonico)){
      if(nomeCanonico.length()) nome=nomeCanonico;
      if(caminhoCanonico.length()) caminho=caminhoCanonico;
    }

    if(modo=="ABRIR_ARTIGO_INTERNO" && artigos.length()){
      int inicio=0;
      while(inicio<(int)artigos.length() && totalCorrelatasArtigo<MAX_RELACOES_ARTIGO){
        int fim=artigos.indexOf(',',inicio);
        if(fim<0) fim=artigos.length();
        String art=artigos.substring(inicio,fim);
        art.trim();
        if(art.length())
          adicionarCorrelataV2(origem,relacaoId,normaId,nome,modo,art,caminho);
        inicio=fim+1;
      }
    }else{
      adicionarCorrelataV2(origem,relacaoId,normaId,nome,modo,"",caminho);
    }
    return true;
  };

  int lidas=0;
  if(relacoesV2Cache && offset<tamanhoRelacoesV2Cache){
    size_t cursor=offset;
    while(cursor<tamanhoRelacoesV2Cache && lidas<quantidade &&
          totalCorrelatasArtigo<MAX_RELACOES_ARTIGO){
      size_t fim=cursor;
      while(fim<tamanhoRelacoesV2Cache && relacoesV2Cache[fim]!='\n') fim++;
      String linha;
      linha.reserve((unsigned)(fim-cursor));
      for(size_t i=cursor;i<fim;i++)
        if(relacoesV2Cache[i]!='\r') linha+=(char)relacoesV2Cache[i];
      if(processarLinha(linha)) lidas++;
      cursor=fim<tamanhoRelacoesV2Cache ? fim+1 : fim;
    }
  }else{
    File f=SD.open(CAMINHO_RELACOES_V2,FILE_READ);
    if(!f || !f.seek(offset)){ if(f) f.close(); return false; }
    while(f.available() && lidas<quantidade && totalCorrelatasArtigo<MAX_RELACOES_ARTIGO){
      String linha=f.readStringUntil('\n');
      if(processarLinha(linha)) lidas++;
    }
    f.close();
  }

  Serial.printf("RELATIONS V2: %s -> %d correlata(s), chave %s|%s|%s|%s (%s)\n",
                artigo.c_str(),totalCorrelatasArtigo,
                artigo.c_str(),parUsado.c_str(),incUsado.c_str(),aliUsada.c_str(),
                relacoesV2Cache?"PSRAM":"SD");
  return totalCorrelatasArtigo>0;
}

bool buscarLookupJurisCFExato(const String &norma,
                              const String &artigo,
                              const String &paragrafo,
                              const String &inciso,
                              const String &alinea,
                              uint32_t &offset,
                              int &quantidade)
{
  offset=0; quantidade=0;
  if(cacheJurisCFCarregado){
    for(int i=0;i<totalJurLookupCFCache;i++){
      const LookupJurisCFCache &r=jurLookupCFCache[i];
      if(norma==r.norma && artigo==r.artigo && paragrafo==r.paragrafo &&
         inciso==r.inciso && alinea==r.alinea){
        offset=r.offset; quantidade=r.quantidade;
        return quantidade>0;
      }
    }
    return false;
  }

  // Fallback controlado: somente se o cache de boot falhou. Nao e o caminho normal.
  File f=SD.open(CAMINHO_JUR_LOOKUP_CF,FILE_READ);
  if(!f) return false;
  while(f.available()){
    String linha=f.readStringUntil('\n');
    linha.trim();
    if(linha.length()==0 || linha[0]=='#') continue;
    if(campoPipe(linha,0)==norma && campoPipe(linha,1)==artigo &&
       campoPipe(linha,2)==paragrafo && campoPipe(linha,3)==inciso &&
       campoPipe(linha,4)==alinea){
      offset=(uint32_t)campoPipe(linha,5).toInt();
      quantidade=campoPipe(linha,6).toInt();
      f.close();
      Serial.println("JUR CACHE: lookup em fallback SD");
      return quantidade>0;
    }
  }
  f.close();
  return false;
}

bool buscarMelhorLookupJurisCF(const String &artigo,
                               uint32_t &offset,
                               int &quantidade,
                               String &parUsado,
                               String &incUsado,
                               String &aliUsada)
{
  String par=contextoJuridicoAtivo.paragrafo;
  String inc=contextoJuridicoAtivo.inciso;
  String ali=contextoJuridicoAtivo.alinea;
  struct Tentativa { String p,i,a; } tentativas[4];
  int total=0;
  if(ali.length()) tentativas[total++]={par,inc,ali};
  if(inc.length()) tentativas[total++]={par,inc,""};
  if(par.length()) tentativas[total++]={par,"",""};
  tentativas[total++]={"","",""};
  for(int i=0;i<total;i++){
    if(buscarLookupJurisCFExato("CF88",artigo,tentativas[i].p,
                               tentativas[i].i,tentativas[i].a,
                               offset,quantidade)){
      parUsado=tentativas[i].p;
      incUsado=tentativas[i].i;
      aliUsada=tentativas[i].a;
      return true;
    }
  }
  return false;
}

void contabilizarTipoJurisCF(const String &tipo)
{
  switch(classificarTipoJurisprudencia(tipo)){
    case JTIPO_SV: totalSumulasVinculantesArtigo++; break;
    case JTIPO_SUMULA_STF: totalSumulasArtigo++; break;
    case JTIPO_RG: totalRepercussaoGeralArtigo++; break;
    case JTIPO_REPETITIVO_STJ: totalRepetitivosArtigo++; break;
    case JTIPO_ACORDAO:
    case JTIPO_ADI:
    case JTIPO_ADC:
    case JTIPO_ADPF: totalAcordaosArtigo++; break;
    default: totalOutrosJurisArtigo++; break;
  }
}

bool adicionarLinhaJurisCF(String linha,
                           const String &rotuloContexto)
{
  linha.trim();
  if(linha.length()==0 || linha[0]=='#' || totalRelacoesArtigo>=MAX_RELACOES_ARTIGO)
    return false;
  String classe=campoPipe(linha,0);
  String tipo=campoPipe(linha,1);
  String tribunal=campoPipe(linha,2);
  String numero=campoPipe(linha,3);
  String status=campoPipe(linha,4);
  String identificador=campoPipe(linha,6);
  if(!classe.startsWith("STF:") || tipo.length()==0 || identificador.length()==0)
    return false;

  RelacaoJuridica &r=relacoesArtigo[totalRelacoesArtigo++];
  r.referencia=rotuloContexto;
  r.tribunal=tribunal;
  r.tipo=tipo;
  r.numero=numero;
  r.status=status;
  r.arquivo=arquivoDetalheJurisCF(identificador);
  r.caminho=String(PASTA_CONTEUDO_JURIS_CF)+"/"+r.arquivo;
  contabilizarTipoJurisCF(tipo);
  return true;
}

bool carregarJurisprudenciaCF(const String &artigo)
{
  uint32_t inicio=micros();
  uint32_t offset=0;
  int quantidade=0;
  String parUsado="",incUsado="",aliUsada="";
  bool achou=buscarMelhorLookupJurisCF(artigo,offset,quantidade,
                                       parUsado,incUsado,aliUsada);
  if(achou){
    String rotulo=rotuloOrigemRelationsV2("CF88",artigo,parUsado,incUsado,aliUsada);
    int lidas=0;
    if(cacheJurisCFCarregado && jurisprudenciaCFCache &&
       offset<tamanhoJurisprudenciaCFCache){
      size_t cursor=offset;
      while(cursor<tamanhoJurisprudenciaCFCache && lidas<quantidade){
        size_t fim=cursor;
        while(fim<tamanhoJurisprudenciaCFCache && jurisprudenciaCFCache[fim]!='\n') fim++;
        String linha;
        linha.reserve((unsigned)(fim-cursor));
        for(size_t i=cursor;i<fim;i++) if(jurisprudenciaCFCache[i]!='\r') linha+=(char)jurisprudenciaCFCache[i];
        if(adicionarLinhaJurisCF(linha,rotulo)) lidas++;
        cursor=fim<tamanhoJurisprudenciaCFCache ? fim+1 : fim;
      }
    }else{
      File f=SD.open(CAMINHO_JURISPRUDENCIA_CF,FILE_READ);
      if(f && f.seek(offset)){
        while(f.available() && lidas<quantidade){
          if(adicionarLinhaJurisCF(f.readStringUntil('\n'),rotulo)) lidas++;
        }
      }
      if(f) f.close();
    }
    if(lidas>0){
      // Na CF o botao abre uma lista unica, independentemente do tipo.
      categoriasJurisDisponiveis[0]=REL_JURIS_TODAS;
      totalCategoriasJuris=1;
    }
  }

  uint32_t duracao=micros()-inicio;
  perfJurisLookupTotalUs+=duracao;
  if(duracao>perfJurisLookupMaxUs) perfJurisLookupMaxUs=duracao;
  perfJurisLookupQuantidade++;
  if((perfJurisLookupQuantidade%32)==0){
    Serial.printf("PERF JUR LOOKUP: media=%lu us max=%lu us lookups=%lu heap=%u psram=%u fonte=%s\n",
                  perfJurisLookupTotalUs/perfJurisLookupQuantidade,
                  perfJurisLookupMaxUs,perfJurisLookupQuantidade,
                  (unsigned)ESP.getFreeHeap(),(unsigned)ESP.getFreePsram(),
                  cacheJurisCFCarregado?"CACHE":"SD-FALLBACK");
  }
  return achou && totalRelacoesArtigo>0;
}

bool inicializarCachesGrandes()
{
  if(indiceJurisCache && indiceCorrelatasCache && checkpointsContexto) return true;

  bool temPSRAM=psramFound();
  Serial.print("PSRAM detectada: ");
  Serial.println(temPSRAM ? "SIM" : "NAO");
  if(temPSRAM){
    Serial.print("PSRAM livre antes dos caches: ");
    Serial.println(ESP.getFreePsram());
  }

  auto alocarBloco=[&](size_t bytes)->void* {
    void *mem=nullptr;
    if(temPSRAM)
      mem=heap_caps_malloc(bytes,MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if(!mem)
      mem=heap_caps_malloc(bytes,MALLOC_CAP_8BIT);
    return mem;
  };

  void *memJ=alocarBloco(sizeof(RelacaoJuridica)*MAX_REGISTROS_INDICE_JUR);
  void *memC=alocarBloco(sizeof(CorrelataJuridica)*MAX_REGISTROS_INDICE_COR);
  void *memP=alocarBloco(sizeof(CheckpointContexto)*MAX_CHECKPOINTS_CONTEXTO);
  if(!memJ || !memC || !memP){
    Serial.println("ERRO: memoria insuficiente para caches juridicos");
    if(memJ) heap_caps_free(memJ);
    if(memC) heap_caps_free(memC);
    if(memP) heap_caps_free(memP);
    return false;
  }

  indiceJurisCache=(RelacaoJuridica*)memJ;
  indiceCorrelatasCache=(CorrelataJuridica*)memC;
  checkpointsContexto=(CheckpointContexto*)memP;
  for(int i=0;i<MAX_REGISTROS_INDICE_JUR;i++) new (&indiceJurisCache[i]) RelacaoJuridica();
  for(int i=0;i<MAX_REGISTROS_INDICE_COR;i++) new (&indiceCorrelatasCache[i]) CorrelataJuridica();
  memset(checkpointsContexto,0,sizeof(CheckpointContexto)*MAX_CHECKPOINTS_CONTEXTO);

  Serial.print("Heap apos caches juridicos: ");
  Serial.println(ESP.getFreeHeap());
  if(temPSRAM){
    Serial.print("PSRAM livre apos caches: ");
    Serial.println(ESP.getFreePsram());
  }
  return true;
}

void limparRelacoesArtigo()
{
  for(int i=0;i<MAX_RELACOES_ARTIGO;i++){
    relacoesArtigo[i].referencia="";
    relacoesArtigo[i].tribunal="";
    relacoesArtigo[i].tipo="";
    relacoesArtigo[i].numero="";
    relacoesArtigo[i].status="";
    relacoesArtigo[i].arquivo="";
    relacoesArtigo[i].caminho="";
  }
  for(int i=0;i<MAX_RELACOES_ARTIGO;i++){
    correlatasArtigo[i].origem="";
    correlatasArtigo[i].relacaoId="";
    correlatasArtigo[i].normaId="";
    correlatasArtigo[i].normaDestino="";
    correlatasArtigo[i].modoAbertura="";
    correlatasArtigo[i].artigoDestino="";
    correlatasArtigo[i].pastaDestino="";
    correlatasArtigo[i].caminhoTXT="";
  }
  totalRelacoesArtigo=0;
  totalSumulasArtigo=0;
  totalSumulasVinculantesArtigo=0;
  totalAcordaosArtigo=0;
  totalRepercussaoGeralArtigo=0;
  totalRepetitivosArtigo=0;
  totalPrecedentesRelevantesArtigo=0;
  totalOutrosJurisArtigo=0;
  totalCorrelatasArtigo=0;
  totalReferenciasArtigo=0;
  menuRelacoesAtivo=false;
  artigoRelacoes="";
  categoriaRelacaoAtual=REL_NENHUMA;
  totalRelacoesCategoria=0;
  relacaoSelecionada=0;
  primeiraRelacaoVisivel=0;
  totalCategoriasJuris=0;
  categoriaJurisSelecionada=0;
}

String chaveContextoAtual(const String &artigo)
{
  return artigo+"|"+String(contextoJuridicoAtivo.paragrafo)+"|"+
         String(contextoJuridicoAtivo.inciso)+"|"+String(contextoJuridicoAtivo.alinea);
}

// Uma unica caminhada associa os nomes do indice aos caminhos reais. Ela e
// feita ao montar o cache, nunca ao abrir cada item.
void indexarCaminhosJurisprudencia(const String &pasta, int profundidade)
{
  if(profundidade<0) return;
  File dir=SD.open(pasta.c_str());
  if(!dir || !dir.isDirectory()){ if(dir) dir.close(); return; }
  while(true){
    File item=dir.openNextFile();
    if(!item) break;
    String nome=somenteNome(String(item.name()));
    bool ehPasta=item.isDirectory();
    item.close();
    String caminho=pasta+"/"+nome;
    if(ehPasta) indexarCaminhosJurisprudencia(caminho,profundidade-1);
    else{
      for(int i=0;i<totalIndiceJurisCache;i++)
        if(indiceJurisCache[i].caminho.length()==0 && indiceJurisCache[i].arquivo==nome)
          indiceJurisCache[i].caminho=caminho;
    }
    yield();
  }
  dir.close();
}

bool carregarIndicesContextuais()
{
  if(indicesContextuaisCarregados) return true;
  if(!inicializarCachesGrandes()) return false;
  uint32_t t0=micros(), tLeitura=0, tParse=0;
  totalIndiceJurisCache=totalIndiceCorrelatasCache=0;
  File f=SD.open(CAMINHO_INDICE_CDC,FILE_READ);
  if(!f) return false;
  while(f.available() && totalIndiceJurisCache<MAX_REGISTROS_INDICE_JUR){
    uint32_t a=micros(); String linha=f.readStringUntil('\n'); tLeitura+=micros()-a;
    linha.trim();
    if(linha.length()==0 || linha[0]=='=' || linha.startsWith("LEX MACHINA") ||
       linha.startsWith("FORMATO:") || linha.startsWith("REFERÊNCIA|") ||
       linha.startsWith("REFERENCIA|")) continue;
    a=micros();
    RelacaoJuridica &r=indiceJurisCache[totalIndiceJurisCache++];
    r.referencia=campoPipe(linha,0); r.tribunal=campoPipe(linha,1);
    r.tipo=campoPipe(linha,2); r.numero=campoPipe(linha,3);
    r.status=campoPipe(linha,4); r.arquivo=campoPipe(linha,5); r.caminho="";
    tParse+=micros()-a;
  }
  f.close();
  File fc=SD.open(CAMINHO_INDICE_CORRELATAS,FILE_READ);
  if(fc){
    while(fc.available() && totalIndiceCorrelatasCache<MAX_REGISTROS_INDICE_COR){
      uint32_t a=micros(); String linha=fc.readStringUntil('\n'); tLeitura+=micros()-a;
      linha.trim(); if(linha.length()==0 || linha[0]=='#' || linha[0]=='=') continue;
      a=micros();
      CorrelataJuridica &c=indiceCorrelatasCache[totalIndiceCorrelatasCache++];
      c.origem=campoPipe(linha,0); c.relacaoId=""; c.normaId="";
      c.normaDestino=campoPipe(linha,1); c.modoAbertura="V1";
      c.artigoDestino=campoPipe(linha,2); c.pastaDestino=campoPipe(linha,3);
      c.caminhoTXT="";
      tParse+=micros()-a;
    }
    fc.close();
  }
  // Nao percorremos mais toda a arvore de jurisprudencia aqui.
  // Os caminhos sao resolvidos sob demanda por categoria/nome de arquivo e
  // ficam memorizados no proprio registro. Isso evita centenas de acessos ao SD
  // durante a primeira mudanca de contexto do CDC.
  indicesContextuaisCarregados=true;
  Serial.printf("PERF INDICE_JUR: %lu ms (leitura=%lu, parsing=%lu, caminhos=adiados, registros=%d)\n",
    (micros()-t0)/1000,tLeitura/1000,tParse/1000,totalIndiceJurisCache);
  return true;
}

void limparContextoRelationsV2Rapido()
{
  // Na CF o arquivo ja foi zerado integralmente ao ser aberto. Durante o
  // scroll, limpamos somente as correlatas realmente usadas no contexto
  // anterior, evitando limpar centenas de objetos String a cada inciso.
  int usados=totalCorrelatasArtigo;
  if(usados<0) usados=0;
  if(usados>MAX_RELACOES_ARTIGO) usados=MAX_RELACOES_ARTIGO;
  for(int i=0;i<usados;i++){
    correlatasArtigo[i].origem="";
    correlatasArtigo[i].relacaoId="";
    correlatasArtigo[i].normaId="";
    correlatasArtigo[i].normaDestino="";
    correlatasArtigo[i].modoAbertura="";
    correlatasArtigo[i].artigoDestino="";
    correlatasArtigo[i].pastaDestino="";
    correlatasArtigo[i].caminhoTXT="";
  }
  totalCorrelatasArtigo=0;
  totalRelacoesArtigo=0;
  totalSumulasArtigo=0;
  totalSumulasVinculantesArtigo=0;
  totalAcordaosArtigo=0;
  totalRepercussaoGeralArtigo=0;
  totalRepetitivosArtigo=0;
  totalPrecedentesRelevantesArtigo=0;
  totalOutrosJurisArtigo=0;
  totalReferenciasArtigo=0;
  totalCategoriasJuris=0;
  categoriaJurisSelecionada=0;
  categoriaRelacaoAtual=REL_NENHUMA;
  totalRelacoesCategoria=0;
  relacaoSelecionada=0;
  primeiraRelacaoVisivel=0;
  menuRelacoesAtivo=false;
}

bool carregarRelacoesDoArtigo(const String &artigo)
{
  uint32_t t0=micros();

  // A Constituicao e atualizada muitas vezes durante a rolagem (cada inciso
  // pode mudar o contexto). Nao fazemos a limpeza pesada dos caches V1 aqui.
  if(arquivoAtualPertenceACF()){
    limparContextoRelationsV2Rapido();
    artigoRelacoes=artigo;
    contextoRelacoesRotulo=montarRotuloContextoRelacoes(artigo);
    if(!sdOK) return false;
    carregarCorrelatasRelationsV2(artigo);
    carregarJurisprudenciaCF(artigo);
    menuRelacoesAtivo=(totalCorrelatasArtigo>0 || totalRelacoesArtigo>0);
    modoDigitacaoArtigo=!menuRelacoesAtivo;
    Serial.printf("PERF RODAPE_CONTEXTOV2: %lu us (correlatas=%d juris=%d fonte-jur=%s)\n",
                  micros()-t0,totalCorrelatasArtigo,totalRelacoesArtigo,
                  cacheJurisCFCarregado?"CACHE":"SD-FALLBACK");
    return menuRelacoesAtivo;
  }

  limparRelacoesArtigo();
  artigoRelacoes=artigo;
  contextoRelacoesRotulo=montarRotuloContextoRelacoes(artigo);
  if(!sdOK) return false;

  // O CDC continua no V1 nesta fase para preservar a jurisprudencia e
  // O CDC continua no V1 nesta fase para preservar a jurisprudencia e
  // as correlatas antigas ate o motor geral ser expandido para todas as normas.
  if(!arquivoAtualPertenceAoCDC() || !carregarIndicesContextuais()) return false;

  String chave=chaveContextoAtual(artigo);
  ResultadoContextoLRU *entrada=nullptr;
  for(int i=0;i<CONTEXTOS_LRU;i++)
    if(contextosLRU[i].valido && contextosLRU[i].chave==chave){ entrada=&contextosLRU[i]; break; }

  bool hit=(entrada!=nullptr);
  if(!entrada){
    int slot=0;
    for(int i=0;i<CONTEXTOS_LRU;i++){
      if(!contextosLRU[i].valido){ slot=i; break; }
      if(contextosLRU[i].uso<contextosLRU[slot].uso) slot=i;
    }
    entrada=&contextosLRU[slot];
    entrada->chave=chave; entrada->totalJuris=entrada->totalCorrelatas=0; entrada->valido=true;
    int melhor=-1;
    for(int i=0;i<totalIndiceJurisCache;i++)
      melhor=max(melhor,especificidadeReferenciaAtiva(indiceJurisCache[i].referencia,artigo));
    for(int i=0;i<totalIndiceJurisCache && entrada->totalJuris<MAX_RELACOES_ARTIGO;i++)
      if(especificidadeReferenciaAtiva(indiceJurisCache[i].referencia,artigo)==melhor)
        entrada->juris[entrada->totalJuris++]=(uint8_t)i;
    melhor=-1;
    for(int i=0;i<totalIndiceCorrelatasCache;i++)
      melhor=max(melhor,especificidadeReferenciaAtiva(indiceCorrelatasCache[i].origem,artigo));
    for(int i=0;i<totalIndiceCorrelatasCache && entrada->totalCorrelatas<MAX_RELACOES_ARTIGO;i++)
      if(especificidadeReferenciaAtiva(indiceCorrelatasCache[i].origem,artigo)==melhor)
        entrada->correlatas[entrada->totalCorrelatas++]=(uint8_t)i;
  }
  entrada->uso=++relogioContextosLRU;

  for(int i=0;i<entrada->totalJuris;i++){
    RelacaoJuridica &r=relacoesArtigo[totalRelacoesArtigo];
    r=indiceJurisCache[entrada->juris[i]];
    String tipo=r.tipo; tipo.toLowerCase();
    if(tipo=="sumula") totalSumulasArtigo++;
    else if(tipo=="sumula_vinculante") totalSumulasVinculantesArtigo++;
    else if(tipo=="acordao") totalAcordaosArtigo++;
    else if(tipo=="repercussao_geral") totalRepercussaoGeralArtigo++;
    else if(tipo.indexOf("repetitivo")>=0) totalRepetitivosArtigo++;
    else if(tipo=="precedente_relevante") totalPrecedentesRelevantesArtigo++;
    else continue;
    totalRelacoesArtigo++;
  }
  for(int i=0;i<entrada->totalCorrelatas;i++)
    correlatasArtigo[totalCorrelatasArtigo++]=indiceCorrelatasCache[entrada->correlatas[i]];

  if(totalSumulasArtigo) categoriasJurisDisponiveis[totalCategoriasJuris++]=REL_SUMULAS;
  if(totalSumulasVinculantesArtigo) categoriasJurisDisponiveis[totalCategoriasJuris++]=REL_SUMULAS_VINCULANTES;
  if(totalAcordaosArtigo) categoriasJurisDisponiveis[totalCategoriasJuris++]=REL_ACORDAOS;
  if(totalRepercussaoGeralArtigo) categoriasJurisDisponiveis[totalCategoriasJuris++]=REL_REPERCUSSAO_GERAL;
  if(totalRepetitivosArtigo) categoriasJurisDisponiveis[totalCategoriasJuris++]=REL_REPETITIVOS;
  if(totalPrecedentesRelevantesArtigo) categoriasJurisDisponiveis[totalCategoriasJuris++]=REL_PRECEDENTES_RELEVANTES;
  menuRelacoesAtivo=(totalCategoriasJuris>0 || totalCorrelatasArtigo>0 || totalReferenciasArtigo>0);
  modoDigitacaoArtigo=!menuRelacoesAtivo;
  Serial.printf("PERF RODAPE_CONTEXTO: %lu us (%s)\n",micros()-t0,hit?"LRU":"RAM");
  Serial.print("JURISPRUDENCIA: SUMULAS="); Serial.print(totalSumulasArtigo);
  Serial.print(" SV="); Serial.print(totalSumulasVinculantesArtigo);
  Serial.print(" ACORDAOS="); Serial.print(totalAcordaosArtigo);
  Serial.print(" RG="); Serial.print(totalRepercussaoGeralArtigo);
  Serial.print(" REP="); Serial.print(totalRepetitivosArtigo);
  Serial.print(" PREC="); Serial.println(totalPrecedentesRelevantesArtigo);
  return menuRelacoesAtivo;
}
String caminhoArquivoRelacao(RelacaoJuridica &r)
{
  if(r.caminho.length()) return r.caminho;

  const String raiz="/9-CÓDIGO DE DEFESA DO CONSUMIDOR/19_JURISPRUDENCIA";
  String nome=r.arquivo;
  String tipo=r.tipo; tipo.toLowerCase();
  String status=r.status; status.toLowerCase();
  String candidato="";

  auto existeArquivo=[&](const String &caminho)->bool {
    if(!SD.exists(caminho.c_str())) return false;
    File f=SD.open(caminho.c_str(),FILE_READ);
    bool ok=(bool)f && !f.isDirectory();
    if(f) f.close();
    if(ok){ r.caminho=caminho; return true; }
    return false;
  };

  // Pastas deterministicas da colecao atual. A resolucao por caminho conhecido
  // custa apenas poucos exists/open em vez de uma varredura recursiva de ~480 TXT.
  if(tipo=="sumula"){
    if(nome.startsWith("stf_")) candidato=raiz+"/STF/SUMULAS/"+nome;
    else candidato=raiz+"/STJ/SUMULAS/"+nome;
    if(existeArquivo(candidato)) return r.caminho;
  }else if(tipo=="sumula_vinculante"){
    candidato=raiz+"/STF/SUMULAS_VINCULANTES/"+nome;
    if(existeArquivo(candidato)) return r.caminho;
  }else if(tipo=="acordao"){
    candidato=raiz+"/STJ/ACORDAOS/"+nome;
    if(existeArquivo(candidato)) return r.caminho;
  }else if(tipo=="repercussao_geral"){
    candidato=raiz+"/STF/PRECEDENTES/REPERCUSSAO_GERAL/"+nome;
    if(existeArquivo(candidato)) return r.caminho;
  }else if(tipo.indexOf("repetitivo")>=0){
    const char *pastas[4]={"JULGADOS","PENDENTES","SOBRESTADOS","CANCELADOS"};
    int primeira=0;
    if(status.indexOf("pend")>=0) primeira=1;
    else if(status.indexOf("sobrest")>=0) primeira=2;
    else if(status.indexOf("cancel")>=0) primeira=3;
    for(int passo=0;passo<4;passo++){
      int idx=(primeira+passo)%4;
      candidato=raiz+"/STJ/REPETITIVOS/"+String(pastas[idx])+"/"+nome;
      if(existeArquivo(candidato)) return r.caminho;
    }
  }else if(tipo=="precedente_relevante"){
    if(nome.startsWith("stf_adi_")) candidato=raiz+"/STF/PRECEDENTES/ADI/"+nome;
    else if(nome.startsWith("stf_adc_")) candidato=raiz+"/STF/PRECEDENTES/ADC/"+nome;
    else if(nome.startsWith("stf_adpf_")) candidato=raiz+"/STF/PRECEDENTES/ADPF/"+nome;
    else if(nome.startsWith("stf_ado_")) candidato=raiz+"/STF/PRECEDENTES/ADO/"+nome;
    else if(nome.startsWith("stj_iac_")) candidato=raiz+"/STJ/PRECEDENTES_RELEVANTES/IAC/"+nome;
    else if(nome.startsWith("stj_sirdr_")) candidato=raiz+"/STJ/PRECEDENTES_RELEVANTES/SIRDR/"+nome;
    if(candidato.length() && existeArquivo(candidato)) return r.caminho;
  }

  // Compatibilidade defensiva: se surgir uma categoria/nome novo no SD,
  // procura apenas quando o usuario realmente abrir esse item. O resultado
  // encontrado fica cacheado em r.caminho para as proximas aberturas.
  String encontrado=localizarArquivoRecursivo(raiz,nome,5);
  if(encontrado.length()) r.caminho=encontrado;
  return r.caminho;
}

String localizarArquivoRecursivo(const String &pasta, const String &arquivo, int profundidade)
{
  if(profundidade<0) return "";
  File dir=SD.open(pasta.c_str());
  if(!dir || !dir.isDirectory()){
    if(dir) dir.close();
    return "";
  }
  String achado="";
  while(achado.length()==0){
    File item=dir.openNextFile();
    if(!item) break;
    String nome=somenteNome(String(item.name()));
    bool ehPasta=item.isDirectory();
    item.close();
    String caminho=pasta+"/"+nome;
    if(ehPasta) achado=localizarArquivoRecursivo(caminho,arquivo,profundidade-1);
    else if(nome==arquivo) achado=caminho;
  }
  dir.close();
  return achado;
}

String primeiroTXTDaPasta(String pasta)
{
  pasta.trim();
  while(pasta.length()>1 && pasta.endsWith("/")) pasta.remove(pasta.length()-1);
  File dir=SD.open(pasta.c_str());
  if(!dir || !dir.isDirectory()){
    if(dir) dir.close();
    return "";
  }
  String resultado="";
  while(true){
    File item=dir.openNextFile();
    if(!item) break;
    String nome=somenteNome(String(item.name()));
    bool ehPasta=item.isDirectory();
    item.close();
    if(!ehPasta && terminaComTXT(nome)){
      resultado=pasta+"/"+nome;
      break;
    }
  }
  dir.close();
  return resultado;
}

bool carregarPastas(const String &caminho)
{
  // Falhas de abertura preservam o contexto anterior.
  if(!sdOK){statusSD="ERRO: CARTAO SD NAO ENCONTRADO"; return false;}
  File dir=SD.open(caminho.c_str());
  if(!dir || !dir.isDirectory()){
    if(dir) dir.close();
    statusSD="ERRO AO ABRIR PASTA";
    return false;
  }
  pastaAtual=caminho;
  for(int i=0;i<MAX_PASTAS;i++){pastas[i]=""; itemEhPasta[i]=false;}
  totalPastas=0;
  pastaSelecionada=0;
  primeiraPastaVisivel=0;
  bool limitado=false;
  while(true){
    File item=dir.openNextFile();
    if(!item) break;
    String nome=somenteNome(String(item.name()));
    bool pasta=item.isDirectory();
    bool incluir=nome.length()>0 && nome!="System Volume Information" &&
                 nome!="." && nome!=".." && (pasta || terminaComTXT(nome));
    item.close();
    if(!incluir) continue;
    if(totalPastas>=MAX_PASTAS){limitado=true; break;}
    pastas[totalPastas]=nome;
    itemEhPasta[totalPastas++]=pasta;
  }
  dir.close();
  statusSD=limitado ? "LIMITE: PRIMEIROS 48 ITENS" :
           (totalPastas>0 ? String(totalPastas)+" ITEM(NS)" : "PASTA VAZIA / SEM TXT");
  return true;
}

// =====================================================
// MENU DE PASTAS
// =====================================================
const int PASTA_Y0=53;
const int PASTA_H=27;

void desenharLinhaPasta(int linhaVisual)
{
  if(linhaVisual<0 || linhaVisual>=PASTAS_VISIVEIS) return;
  int indice=primeiraPastaVisivel+linhaVisual;
  int y=PASTA_Y0+linhaVisual*PASTA_H;

  tft.fillRect(8,y,304,25,COR_FUNDO);
  if(indice<0 || indice>=totalPastas) return;

  bool sel=(indice==pastaSelecionada);
  uint16_t cor=sel?COR_VERDE:COR_VERDE_ESCURO;
  tft.drawRoundRect(10,y,300,24,4,cor);

  tft.drawRect(18,y+7,14,10,sel?COR_VERDE:COR_VERDE_SUAVE);
  if(itemEhPasta[indice])
    tft.drawFastHLine(20,y+5,7,sel?COR_VERDE:COR_VERDE_SUAVE);
  else{
    tft.drawFastHLine(21,y+10,8,sel?COR_VERDE:COR_VERDE_SUAVE);
    tft.drawFastHLine(21,y+13,8,sel?COR_VERDE:COR_VERDE_SUAVE);
  }

  String nome=pastas[indice];
  imprimirUTF8(40,y+6,nome,sel?COR_VERDE:COR_VERDE_SUAVE,COR_FUNDO,38);
  tft.setTextSize(1);
  tft.setTextColor(sel?COR_VERDE:COR_VERDE_SUAVE,COR_FUNDO);
  tft.setCursor(296,y+8); tft.print(">");
}

void desenharTodasLinhasPastas()
{
  for(int i=0;i<PASTAS_VISIVEIS;i++) desenharLinhaPasta(i);
}

void desenharTelaPastas()
{
  tft.fillScreen(COR_FUNDO);
  desenharMolduraCyber();

  tft.drawRoundRect(3,2,68,23,3,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(10,10); tft.print("< VOLTAR");
  String titulo=pastaAtual=="/" ? "SD / (RAIZ)" : somenteNome(pastaAtual);
  imprimirUTF8(78,10,titulo,COR_VERDE,COR_FUNDO,39);
  tft.drawFastHLine(10,31,300,COR_VERDE_ESCURO);

  tft.setTextSize(1); tft.setTextColor(COR_VERDE_SUAVE,COR_FUNDO);
  tft.setCursor(12,37); tft.print(statusSD);

  desenharTodasLinhasPastas();

  tft.drawFastHLine(10,218,300,COR_VERDE_ESCURO);
  tft.setCursor(12,225); tft.print("RODA/SETAS: mover   ENTER: abrir");
}

void desenharTransicaoSplash(bool mostrarSplash)
{
  // Oculta a construcao da tela usando a RAM do proprio ILI9341.
  // Nao usa SLPIN, framebuffer, GPIO de backlight nem atraso adicional.
  tft.sendCommand(ILI9341_DISPOFF);
  if(mostrarSplash) desenharSplashLexMachina();
  else desenharTelaPastas();
  // A transicao nao modifica o temporizador nem acorda uma tela suspensa.
  if(!displayApagado) tft.sendCommand(ILI9341_DISPON);
}

void abrirSplashManual()
{
  if(telaAtual!=TELA_PASTAS || pastaAtual!="/") return;
  telaAtual=TELA_SPLASH;
  desenharTransicaoSplash(true);
}

void fecharSplashManual()
{
  if(telaAtual!=TELA_SPLASH) return;
  telaAtual=TELA_PASTAS;
  desenharTransicaoSplash(false); // Preserva lista e selecao da raiz.
}

void moverSelecaoPasta(int delta)
{
  if(totalPastas<=0 || delta==0) return;

  int antigo=pastaSelecionada;
  int antigaPrimeira=primeiraPastaVisivel;
  pastaSelecionada=constrain(pastaSelecionada+delta,0,totalPastas-1);
  if(pastaSelecionada==antigo) return;

  if(pastaSelecionada<primeiraPastaVisivel) primeiraPastaVisivel=pastaSelecionada;
  if(pastaSelecionada>=primeiraPastaVisivel+PASTAS_VISIVEIS)
    primeiraPastaVisivel=pastaSelecionada-PASTAS_VISIVEIS+1;

  if(primeiraPastaVisivel==antigaPrimeira){
    desenharLinhaPasta(antigo-antigaPrimeira);
    desenharLinhaPasta(pastaSelecionada-primeiraPastaVisivel);
  }else{
    desenharTodasLinhasPastas();
  }
}

// =====================================================
// INDICE SOB DEMANDA
// =====================================================
// Processa UMA linha visual e devolve o byte onde comeca a proxima.
// Conta caracteres UTF-8 corretamente: ã, ç, é etc. contam como 1 coluna.
bool avancarUmaLinhaVisual(File &f, uint32_t inicio, uint32_t &proximo)
{
  if(!f.seek(inicio)) return false;
  if(!f.available()) return false;

  int larguraPx=0;
  uint32_t ultimoEspacoDepois=inicio;
  bool achouEspaco=false;

  while(f.available()){
    uint32_t posAntes=f.position();
    uint8_t b0=(uint8_t)f.read();

    if(b0=='\r') continue;

    if(b0=='\n'){
      proximo=f.position();
      return proximo < tamanhoArquivoAtual;
    }

    uint16_t cp=b0;

    // Decodifica UTF-8 diretamente do arquivo para medir a largura REAL
    // da letra. Assim a quebra de linha nao depende mais de "44 colunas".
    if((b0 & 0xE0)==0xC0){
      if(f.available()){
        uint8_t b1=(uint8_t)f.read();
        cp=((uint16_t)(b0 & 0x1F)<<6) | (b1 & 0x3F);
      }
    }else if((b0 & 0xF0)==0xE0){
      if(f.available()){
        uint8_t b1=(uint8_t)f.read();
        if(f.available()){
          uint8_t b2=(uint8_t)f.read();
          cp=((uint16_t)(b0 & 0x0F)<<12) |
             ((uint16_t)(b1 & 0x3F)<<6) |
             (b2 & 0x3F);
        }
      }
    }else if((b0 & 0xF8)==0xF0){
      // Fora do conjunto juridico comum; consome a sequencia e mostra '?'
      for(int k=0;k<3 && f.available();k++) f.read();
      cp='?';
    }

    if(cp=='\t') cp=' ';

    if(cp==' ' || cp==0x00A0){
      ultimoEspacoDepois=f.position();
      achouEspaco=true;
    }

    int av=avancoGlyphArimo(cp);

    if(larguraPx + av > LEITOR_TEXTO_W){
      // Havendo espaco na linha, a palavra inteira vai para a proxima.
      if(achouEspaco && ultimoEspacoDepois>inicio){
        proximo=ultimoEspacoDepois;
      }else if(posAntes>inicio){
        // Somente palavras maiores que a largura total podem ser partidas.
        proximo=posAntes;
      }else{
        proximo=f.position();
      }
      return proximo < tamanhoArquivoAtual;
    }

    larguraPx += av;
  }

  proximo=f.position();
  return false;
}

// Reposiciona a janela, sem redefinir o inicio real navegavel do arquivo.
void reiniciarIndice(uint32_t inicio=0)
{
  linhasIndexadas=1;
  offsetsLinhas[0]=inicio;
  linhaTopo=0;
  fimDoArquivoIndexado=(inicio>=tamanhoArquivoAtual);

  cacheLeitorValido=false;
  cacheLeitorTopo=-1;
  limparContextoJuridico(contextoAntesCache,nomeArquivoAtual.c_str());
  limparContextoJuridico(contextoJuridicoAtivo,nomeArquivoAtual.c_str());
}

// Reconstroi ate uma tela de linhas ANTES da janela atual, sem ler o TXT inteiro.
// A busca reversa encontra o inicio da linha fisica; a quebra visual usa a
// mesma rotina de pixels/UTF-8 do leitor, inclusive para paragrafos longos.
int indexarAntesDaJanela()
{
  if(linhasIndexadas<=0 || offsetsLinhas[0]==0) return 0;
  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f) return 0;

  const uint32_t limite=offsetsLinhas[0];
  uint32_t inicio=0;
  uint32_t cursor=limite;
  uint8_t bloco[256];
  bool encontrouInicio=false;
  while(cursor>0 && !encontrouInicio){
    uint32_t base=cursor>sizeof(bloco) ? cursor-sizeof(bloco) : 0;
    int quantidade=(int)(cursor-base);
    if(!f.seek(base) || f.read(bloco,quantidade)!=quantidade){
      f.close();
      return 0; // Nao modifica o indice se a leitura falhar.
    }
    for(int i=quantidade-1;i>=0;i--){
      uint32_t pos=base+(uint32_t)i;
      // Se limite ja inicia uma linha, ignore seu LF imediatamente anterior.
      if(bloco[i]=='\n' && pos<limite-1){
        inicio=pos+1;
        encontrouInicio=true;
        break;
      }
    }
    cursor=base;
    yield();
  }

  // Anel pequeno de offsets: guarda so as ultimas linhas antes do limite.
  // Mantemos quatro telas anteriores. Quando o leitor chega ao inicio da
  // janela durante a subida, uma unica indexacao alimenta varios passos e evita
  // as pequenas pausas que antes reapareciam a cada ~13 linhas.
  const int LINHAS_PRE_INDEXADAS=LEITOR_LINHAS_VISIVEIS*4;
  uint32_t anteriores[LINHAS_PRE_INDEXADAS];
  int quantidade=0;
  int proxima=0;
  uint32_t pos=inicio;
  while(pos<limite){
    anteriores[proxima]=pos;
    proxima=(proxima+1)%LINHAS_PRE_INDEXADAS;
    if(quantidade<LINHAS_PRE_INDEXADAS) quantidade++;
    uint32_t seguinte=pos;
    avancarUmaLinhaVisual(f,pos,seguinte);
    if(seguinte<=pos){f.close(); return 0;}
    pos=seguinte;
    yield();
  }
  f.close();
  if(quantidade==0) return 0;

  // Preserva os offsets posteriores enquanto couberem no indice existente.
  // Se a cauda sair da janela, ela sera indexada novamente ao descer.
  int manter=min(linhasIndexadas,MAX_LINHAS_INDEXADAS-quantidade);
  if(manter<linhasIndexadas) fimDoArquivoIndexado=false;
  memmove(offsetsLinhas+quantidade,offsetsLinhas,manter*sizeof(offsetsLinhas[0]));
  int primeiro=quantidade==LINHAS_PRE_INDEXADAS ? proxima : 0;
  for(int i=0;i<quantidade;i++)
    offsetsLinhas[i]=anteriores[(primeiro+i)%LINHAS_PRE_INDEXADAS];
  linhasIndexadas=manter+quantidade;
  linhaTopo+=quantidade; // Mesmo byte visivel, agora em outro indice da janela.
  cacheLeitorValido=false;
  cacheLeitorTopo=-1;
  return quantidade;
}

// Garante que exista indice ate "linhaAlvo". So le o trecho necessario.
void indexarAte(int linhaAlvo)
{
  if(fimDoArquivoIndexado) return;
  if(linhaAlvo < linhasIndexadas) return;
  if(linhasIndexadas >= MAX_LINHAS_INDEXADAS) return;

  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f) return;

  while(linhasIndexadas<=linhaAlvo && !fimDoArquivoIndexado && linhasIndexadas<MAX_LINHAS_INDEXADAS){
    uint32_t inicio=offsetsLinhas[linhasIndexadas-1];
    uint32_t prox=inicio;
    bool temProxima=avancarUmaLinhaVisual(f,inicio,prox);

    if(prox<=inicio || prox>=tamanhoArquivoAtual){
      fimDoArquivoIndexado=true;
      break;
    }

    offsetsLinhas[linhasIndexadas++]=prox;
    if(!temProxima) fimDoArquivoIndexado=true;
  }

  f.close();
}

void lerLinhaVisualParaBuffer(File &f, int indice, char *saida, int capacidade, int slotCache)
{
  destaqueInicioCache[slotCache]=0;
  destaqueFimCache[slotCache]=0;
  if(capacidade<=0) return;
  saida[0]='\0';

  if(indice<0 || indice>=linhasIndexadas) return;

  uint32_t inicio=offsetsLinhas[indice];
  linhaCacheValida[slotCache]=true;
  uint32_t fim=tamanhoArquivoAtual;
  offsetLinhaCache[slotCache]=inicio;
  inicioFisicoCache[slotCache]=(inicio==0);
  if(inicio>0 && f.seek(inicio-1)) inicioFisicoCache[slotCache]=(f.read()=='\n');

  // O indice seguinte marca exatamente onde esta linha visual termina.
  if(indice+1<linhasIndexadas) fim=offsetsLinhas[indice+1];

  if(!f.seek(inicio)) return;

  int pos=0;

  while(f.available() && f.position()<fim && pos<capacidade-4){
    uint32_t byteOriginal=f.position();
    int inicioNoCache=pos;
    uint8_t b=(uint8_t)f.read();

    if(b=='\r' || b=='\n') continue;

    saida[pos++]=(char)b;

    if((b & 0xE0)==0xC0){
      if(f.available() && f.position()<fim && pos<capacidade-1)
        saida[pos++]=(char)f.read();
    }else if((b & 0xF0)==0xE0){
      if(f.available() && f.position()<fim && pos<capacidade-1)
        saida[pos++]=(char)f.read();
      if(f.available() && f.position()<fim && pos<capacidade-1)
        saida[pos++]=(char)f.read();
    }else if((b & 0xF8)==0xF0){
      if(f.available() && f.position()<fim && pos<capacidade-1)
        saida[pos++]=(char)f.read();
      if(f.available() && f.position()<fim && pos<capacidade-1)
        saida[pos++]=(char)f.read();
      if(f.available() && f.position()<fim && pos<capacidade-1)
        saida[pos++]=(char)f.read();
    }
    if(destaqueTextoAtivo && byteOriginal<=offsetFinalTexto && f.position()>offsetUltimoTexto){
      if(destaqueFimCache[slotCache]==0) destaqueInicioCache[slotCache]=inicioNoCache;
      destaqueFimCache[slotCache]=pos;
    }
  }

  // Remove espacos que ficaram no fim da linha por causa do word-wrap.
  while(pos>0 && (saida[pos-1]==' ' || saida[pos-1]=='\t')) pos--;

  saida[pos]='\0';
}

void guardarCheckpointContexto(uint32_t offset, const ContextoJuridicoAtivo &contexto)
{
  if(!checkpointsContexto && !inicializarCachesGrandes()) return;
  if(arquivoCheckpoints!=caminhoArquivoAtual){
    if(!checkpointsContexto && !inicializarCachesGrandes()) return;
    memset(checkpointsContexto,0,sizeof(CheckpointContexto)*MAX_CHECKPOINTS_CONTEXTO);
    proximoCheckpointContexto=0; arquivoCheckpoints=caminhoArquivoAtual;
  }
  for(int i=0;i<MAX_CHECKPOINTS_CONTEXTO;i++)
    if(checkpointsContexto[i].valido && checkpointsContexto[i].offset==offset){
      checkpointsContexto[i].contexto=contexto; return;
    }
  CheckpointContexto &cp=checkpointsContexto[proximoCheckpointContexto];
  cp.offset=offset; cp.contexto=contexto; cp.valido=true;
  proximoCheckpointContexto=(proximoCheckpointContexto+1)%MAX_CHECKPOINTS_CONTEXTO;
}

bool obterCheckpointContexto(uint32_t limite, uint32_t &offset, ContextoJuridicoAtivo &contexto)
{
  if(!checkpointsContexto && !inicializarCachesGrandes()) return false;
  if(arquivoCheckpoints!=caminhoArquivoAtual) return false;
  bool achou=false; offset=0;
  for(int i=0;i<MAX_CHECKPOINTS_CONTEXTO;i++)
    if(checkpointsContexto[i].valido && checkpointsContexto[i].offset<=limite &&
       (!achou || checkpointsContexto[i].offset>offset)){
      offset=checkpointsContexto[i].offset; contexto=checkpointsContexto[i].contexto; achou=true;
    }
  return achou;
}

// Reconstrucao pontual usada ao abrir, buscar ou rolar para cima. Parte do
// checkpoint anterior mais proximo; a janela de 256 KB e apenas o fallback da
// primeira visita a uma regiao, nunca o custo recorrente de cada passo.
bool arquivoAtualEhConstituicao()
{
  return caminhoArquivoAtual.startsWith("/1- CONSTITUIÇÃO FEDERAL/") ||
         nomeArquivoAtual.equalsIgnoreCase("cf.txt");
}

bool linhaEhMarcadorArtigoIsolado(const char *linha)
{
  if(!linha) return false;
  while(*linha==' ' || *linha=='\t') linha++;
  char tmp[8];
  int n=0;
  while(*linha && n<(int)sizeof(tmp)-1){
    char c=*linha++;
    if(c!=' ' && c!='\t' && c!='\r') tmp[n++]=c;
  }
  tmp[n]='\0';
  if(n==3 || n==4){
    char a=tmp[0], r=tmp[1], t=tmp[2];
    if(a>='A'&&a<='Z') a+=32;
    if(r>='A'&&r<='Z') r+=32;
    if(t>='A'&&t<='Z') t+=32;
    if(a=='a' && r=='r' && t=='t' && (n==3 || tmp[3]=='.')) return true;
  }
  return false;
}

bool linhaComecaNumeroArtigo(const char *linha)
{
  if(!linha) return false;
  while(*linha==' ' || *linha=='\t') linha++;
  return *linha>='0' && *linha<='9';
}

void aplicarLinhaContextoCompatCF(ContextoJuridicoAtivo &contexto,
                                  const char *linha,
                                  bool inicioFisico,
                                  uint32_t offset,
                                  const char *proximaLinha=nullptr)
{
  // O cf.txt possui trechos no formato:
  // Art.
  // 12. São brasileiros...
  // O parser juridico original recebe linhas isoladas. Para a CF, quando
  // detectamos esse par, criamos apenas para o parser uma linha logica
  // "Art. 12...". O TXT exibido e o arquivo no SD permanecem intocados.
  if(arquivoAtualEhConstituicao() && proximaLinha &&
     linhaEhMarcadorArtigoIsolado(linha) && linhaComecaNumeroArtigo(proximaLinha)){
    char logica[512];
    snprintf(logica,sizeof(logica),"Art. %s",proximaLinha);
    aplicarLinhaContextoJuridico(contexto,logica,true,offset);
    return;
  }
  aplicarLinhaContextoJuridico(contexto,linha,inicioFisico,offset);
}

void reconstruirContextoAntesOffset(uint32_t limite, ContextoJuridicoAtivo &saida)
{
  uint32_t t0=micros();
  limparContextoJuridico(saida,nomeArquivoAtual.c_str());
  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f) return;
  const uint32_t JANELA_RECONSTRUCAO=262144;
  uint32_t inicio=0;
  bool usouCheckpoint=obterCheckpointContexto(limite,inicio,saida);
  if(!usouCheckpoint) inicio=limite>JANELA_RECONSTRUCAO ? limite-JANELA_RECONSTRUCAO : 0;
  if(inicio>0 && !usouCheckpoint){
    f.seek(inicio);
    while(f.available() && f.position()<limite && f.read()!='\n') yield();
    inicio=f.position();
  }else f.seek(inicio);

  char linha[512];
  while(f.available() && f.position()<limite){
    uint32_t offset=f.position();
    int n=0;
    while(f.available()){
      int b=f.read();
      if(b=='\n') break;
      if(b!='\r' && n<(int)sizeof(linha)-1) linha[n++]=(char)b;
    }
    linha[n]='\0';

    if(arquivoAtualEhConstituicao() && linhaEhMarcadorArtigoIsolado(linha) && f.position()<limite){
      uint32_t inicioProxima=f.position();
      char proxima[512];
      int np=0;
      while(f.available() && f.position()<limite){
        int b=f.read();
        if(b=='\n') break;
        if(b!='\r' && np<(int)sizeof(proxima)-1) proxima[np++]=(char)b;
      }
      proxima[np]='\0';
      if(linhaComecaNumeroArtigo(proxima)){
        aplicarLinhaContextoCompatCF(saida,linha,true,offset,proxima);
        // A linha numerada ja foi consumida pelo look-ahead. Aplicamo-la
        // normalmente para que paragrafos/incisos na mesma linha continuem
        // podendo atualizar o contexto sem perder o artigo recem-detectado.
        aplicarLinhaContextoJuridico(saida,proxima,true,inicioProxima);
        guardarCheckpointContexto(f.position(),saida);
        yield();
        continue;
      }
      f.seek(inicioProxima);
    }

    aplicarLinhaContextoCompatCF(saida,linha,true,offset);
    guardarCheckpointContexto(f.position(),saida);
    yield();
  }
  f.close();
  Serial.printf("PERF CONTEXTO_UP: %lu us (checkpoint=%s, bytes=%lu)\n",
    micros()-t0,usouCheckpoint?"sim":"nao",limite-inicio);
}

void recalcularContextosCache(const ContextoJuridicoAtivo &antes)
{
  ContextoJuridicoAtivo corrente=antes;
  copiarContextoCampo(corrente.arquivo,sizeof(corrente.arquivo),nomeArquivoAtual.c_str());
  for(int i=0;i<LEITOR_LINHAS_VISIVEIS;i++){
    if(!linhaCacheValida[i]){
      limparContextoJuridico(contextoLinhasCache[i],nomeArquivoAtual.c_str());
      continue;
    }
    guardarCheckpointContexto(offsetLinhaCache[i],corrente);
    const char *proximaLinha=nullptr;
    if(i+1<LEITOR_LINHAS_VISIVEIS && linhaCacheValida[i+1])
      proximaLinha=cacheLeitor[i+1];
    aplicarLinhaContextoCompatCF(corrente,cacheLeitor[i],inicioFisicoCache[i],
                                 offsetLinhaCache[i],proximaLinha);
    contextoLinhasCache[i]=corrente;
  }
}

void diagnosticarContextoSeMudou()
{
  uint32_t t0=micros();
  int indice=escolherContextoPredominante(
    contextoLinhasCache,LEITOR_LINHAS_VISIVEIS,contextoJuridicoAtivo
  );
  if(indice<0) return;
  const ContextoJuridicoAtivo &novo=contextoLinhasCache[indice];
  if(contextoJuridicoIgual(novo,contextoJuridicoAtivo)) return;
  contextoJuridicoAtivo=novo;
  Serial.print("CONTEXTO: ART="); Serial.print(novo.artigo[0]?novo.artigo:"-");
  Serial.print(" PAR="); Serial.print(novo.paragrafo[0]?novo.paragrafo:"-");
  Serial.print(" INC="); Serial.print(novo.inciso[0]?novo.inciso:"-");
  Serial.print(" ALINEA="); Serial.println(novo.alinea[0]?novo.alinea:"-");

  // Os indices atuais usam artigo. A chamada ocorre somente na troca estavel
  // de contexto; quando surgirem chaves mais especificas, a mesma consulta
  // podera tentar alinea, inciso e paragrafo antes deste fallback.
  if(!visualizandoReferencia && novo.artigo[0]){
    // Apenas atualiza o estado juridico. O rodape sera redesenhado uma unica
    // vez ao final do viewport, evitando duas escritas TFT por mudanca.
    carregarRelacoesDoArtigo(String(novo.artigo));
  }
  Serial.printf("PERF CONTEXTO_ATUALIZAR: %lu us\n",micros()-t0);
}

// =====================================================
// LEITOR - FONTE ~25% MAIOR + CACHE + DESENHO EM BLOCO
// =====================================================
const int TEXTO_Y0=23;
const int TEXTO_H=LEITOR_LINHA_H;

String rotuloContextoFixoRodape()
{
  // Ao visualizar um documento relacionado, preserva o vinculo exato que
  // originou a abertura. No leitor da lei seca, mostra o dispositivo ativo.
  if(visualizandoReferencia && contextoDocumentoReferencia.length())
    return contextoDocumentoReferencia;

  if(!contextoJuridicoAtivo.artigo[0]) return "";

  String r="ART. "+String(contextoJuridicoAtivo.artigo);
  if(contextoJuridicoAtivo.paragrafo[0]){
    if(strcmp(contextoJuridicoAtivo.paragrafo,"unico")==0) r+=" | PAR. UNICO";
    else r+=" | § "+String(contextoJuridicoAtivo.paragrafo)+"º";
  }
  if(contextoJuridicoAtivo.inciso[0])
    r+=" | INC. "+String(contextoJuridicoAtivo.inciso);
  if(contextoJuridicoAtivo.alinea[0])
    r+=" | AL. "+String(contextoJuridicoAtivo.alinea)+")";
  return r;
}

void desenharIndicadorContextoRodape()
{
  // Faixa fixa imediatamente acima dos botoes. Ela nunca depende de o caput
  // estar visivel na tela; assim artigos longos mantem o referencial juridico.
  tft.fillRect(0,204,320,16,COR_FUNDO);
  tft.drawFastHLine(0,204,320,COR_VERDE_ESCURO);
  tft.drawFastHLine(0,219,320,COR_VERDE_ESCURO);

  String contexto=rotuloContextoFixoRodape();
  if(contexto.length()==0){
    imprimirUTF8(6,208,"CONTEXTO: --",COR_VERDE_SUAVE,COR_FUNDO,48);
    return;
  }

  String texto="CONTEXTO: "+contexto;
  if(texto.length()>50) texto=texto.substring(0,50);
  imprimirUTF8(6,208,texto,COR_VERDE_SUAVE,COR_FUNDO,50);
}

void desenharAtalhoRodape(int x, int y, int w, const char *rotulo)
{
  tft.drawRoundRect(x, y, w, 14, 3, COR_VERDE_ESCURO);
  int larguraTexto=(int)strlen(rotulo)*6;
  int tx=x+((w-larguraTexto)/2);
  if(tx<x+4) tx=x+4;
  tft.setTextSize(1);
  tft.setTextColor(COR_VERDE, COR_FUNDO);
  tft.setCursor(tx, y+3);
  tft.print(rotulo);
}

void desenharBarraBusca()
{
  desenharIndicadorContextoRodape();
  tft.fillRect(0,220,320,20,COR_FUNDO);
  tft.drawFastHLine(0,220,320,COR_VERDE_ESCURO);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(4,228);

  if(visualizandoReferencia){
    tft.print("BACK: lista");
    String contextoMostrar=contextoDocumentoReferencia.length()?contextoDocumentoReferencia:contextoRelacoesRotulo;
    if(contextoMostrar.length()){
      tft.print(" | ");
      String curto=contextoMostrar;
      if(curto.length()>34) curto=curto.substring(0,34);
      tft.print(curto);
    }
    return;
  }

  if(menuRelacoesAtivo && !modoDigitacaoArtigo){
    // Posicoes fixas preservam o significado de 1, 2 e 3 mesmo quando um
    // item intermediario esta oculto por nao possuir conteudo.
    if(totalCorrelatasArtigo>0) desenharAtalhoRodape(4,223,100,"1 LEGISLACAO");
    if(totalCategoriasJuris>0) desenharAtalhoRodape(110,223,100,"2 JURISPR.");
    if(totalReferenciasArtigo>0) desenharAtalhoRodape(216,223,100,"3 REFER.");
    return;
  }

  if(artigoDigitado.length()>0){
    tft.print("ART. "); tft.print(artigoDigitado); tft.print("   ENTER = BUSCAR");
  }else{
    tft.print("Arraste/role para ler | Digite artigo");
  }
}

// Parser UTF-8 para C-string, usado pelo cache do leitor.
uint16_t proximoUnicodeBuffer(const char *s, int &i)
{
  uint8_t b0=(uint8_t)s[i++];
  if(b0<0x80) return b0;

  if((b0 & 0xE0)==0xC0 && s[i]){
    uint8_t b1=(uint8_t)s[i++];
    return ((uint16_t)(b0 & 0x1F)<<6) | (b1 & 0x3F);
  }

  if((b0 & 0xF0)==0xE0 && s[i] && s[i+1]){
    uint8_t b1=(uint8_t)s[i++];
    uint8_t b2=(uint8_t)s[i++];
    return ((uint16_t)(b0 & 0x0F)<<12) |
           ((uint16_t)(b1 & 0x3F)<<6) |
           (b2 & 0x3F);
  }

  while(s[i] && (((uint8_t)s[i] & 0xC0)==0x80)) i++;
  return '?';
}

// =====================================================
// RENDER DO LEITOR - ARIMO PROPORCIONAL COM ANTIALIAS
// =====================================================
inline void pixelBufferLeitor(int x, int y, uint16_t cor)
{
  if(x>=0 && x<LEITOR_BUFFER_W && y>=0 && y<LEITOR_LINHA_H)
    bufferLinhaLeitor[y*LEITOR_BUFFER_W+x]=cor;
}

void desenharGlyphArimoNoBuffer(int x, uint16_t cp, bool marcado)
{
  int idx=indiceGlyphArimo(cp);

  uint16_t offset=pgm_read_word(&FONTE_ARIMO_A4_GLYPHS[idx].offset);
  uint8_t w=pgm_read_byte(&FONTE_ARIMO_A4_GLYPHS[idx].width);
  uint8_t h=pgm_read_byte(&FONTE_ARIMO_A4_GLYPHS[idx].height);
  int8_t xo=(int8_t)pgm_read_byte(&FONTE_ARIMO_A4_GLYPHS[idx].xOffset);
  int8_t yo=(int8_t)pgm_read_byte(&FONTE_ARIMO_A4_GLYPHS[idx].yOffset);

  if(w==0 || h==0) return;

  int x0=x+xo;
  int y0=LEITOR_BASELINE+yo;
  int pixel=0;

  for(int gy=0; gy<h; gy++){
    for(int gx=0; gx<w; gx++,pixel++){
      uint8_t packed=pgm_read_byte(&FONTE_ARIMO_A4_BITMAP[offset+(pixel>>1)]);
      uint8_t alpha=(pixel & 1) ? (packed & 0x0F) : (packed >> 4);

      if(alpha){
        pixelBufferLeitor(x0+gx,y0+gy,VERDE_AA[marcado ? 15-alpha : alpha]);
      }
    }
  }
}

void montarLinhaRGB(const char *texto, int slotCache)
{
  for(int i=0;i<LEITOR_BUFFER_W*LEITOR_LINHA_H;i++)
    bufferLinhaLeitor[i]=COR_FUNDO;
  // Fundos antes dos glyphs preservam as bordas das letras proporcionais.
  for(int passagem=destaqueTextoAtivo?0:1;passagem<2;passagem++){
    int i=0, x=0;
    while(texto[i]){
      int inicio=i;
      uint16_t cp=proximoUnicodeBuffer(texto,i);
      if(cp=='\r' || cp=='\n') break;
      if(cp=='\t' || cp==0x00A0) cp=' ';
      int av=avancoGlyphArimo(cp);
      if(x+av>LEITOR_TEXTO_W) break;
      bool marcado=destaqueTextoAtivo &&
                   inicio<destaqueFimCache[slotCache] && i>destaqueInicioCache[slotCache];
      if(passagem==0 && marcado){
        for(int y=0;y<LEITOR_LINHA_H;y++)
          for(int px=x;px<x+av;px++) pixelBufferLeitor(px,y,COR_VERDE);
      }else if(passagem==1) desenharGlyphArimoNoBuffer(x,cp,marcado);
      x+=av;
    }
  }
}

void carregarCacheLeitorCompleto()
{
  memset(cacheLeitor,0,sizeof(cacheLeitor));
  memset(inicioFisicoCache,0,sizeof(inicioFisicoCache));
  memset(linhaCacheValida,0,sizeof(linhaCacheValida));
  memset(offsetLinhaCache,0,sizeof(offsetLinhaCache));
  memset(destaqueInicioCache,0,sizeof(destaqueInicioCache));
  memset(destaqueFimCache,0,sizeof(destaqueFimCache));
  indexarAte(linhaTopo+LEITOR_LINHAS_VISIVEIS+1);

  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(f){
    for(int i=0;i<LEITOR_LINHAS_VISIVEIS;i++){
      int idx=linhaTopo+i;
      if(idx<linhasIndexadas)
        lerLinhaVisualParaBuffer(f,idx,cacheLeitor[i],BYTES_CACHE_LINHA,i);
    }
    f.close();
  }

  cacheLeitorTopo=linhaTopo;
  cacheLeitorValido=true;
  uint32_t offsetTopo=(linhaTopo>=0 && linhaTopo<linhasIndexadas)?offsetsLinhas[linhaTopo]:0;
  reconstruirContextoAntesOffset(offsetTopo,contextoAntesCache);
  recalcularContextosCache(contextoAntesCache);
}

void atualizarCacheLeitor()
{
  if(!cacheLeitorValido || cacheLeitorTopo<0){
    carregarCacheLeitorCompleto();
    return;
  }

  int delta=linhaTopo-cacheLeitorTopo;
  if(delta==0) return;

  if(abs(delta)>=LEITOR_LINHAS_VISIVEIS){
    carregarCacheLeitorCompleto();
    return;
  }

  indexarAte(linhaTopo+LEITOR_LINHAS_VISIVEIS+1);
  const size_t tamLinha=BYTES_CACHE_LINHA;

  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f){
    carregarCacheLeitorCompleto();
    return;
  }

  ContextoJuridicoAtivo novoAntes;
  if(delta>0) novoAntes=contextoLinhasCache[delta-1];
  else reconstruirContextoAntesOffset(offsetsLinhas[linhaTopo],novoAntes);

  if(delta>0){
    int manter=LEITOR_LINHAS_VISIVEIS-delta;
    memmove(&cacheLeitor[0][0],&cacheLeitor[delta][0],manter*tamLinha);
    memset(&cacheLeitor[manter][0],0,delta*tamLinha);
    memmove(destaqueInicioCache,destaqueInicioCache+delta,manter*sizeof(uint16_t));
    memmove(destaqueFimCache,destaqueFimCache+delta,manter*sizeof(uint16_t));
    memmove(inicioFisicoCache,inicioFisicoCache+delta,manter*sizeof(bool));
    memmove(linhaCacheValida,linhaCacheValida+delta,manter*sizeof(bool));
    memmove(offsetLinhaCache,offsetLinhaCache+delta,manter*sizeof(uint32_t));
    memset(destaqueInicioCache+manter,0,delta*sizeof(uint16_t));
    memset(destaqueFimCache+manter,0,delta*sizeof(uint16_t));
    memset(inicioFisicoCache+manter,0,delta*sizeof(bool));
    memset(linhaCacheValida+manter,0,delta*sizeof(bool));
    memset(offsetLinhaCache+manter,0,delta*sizeof(uint32_t));

    for(int i=manter;i<LEITOR_LINHAS_VISIVEIS;i++){
      int idx=linhaTopo+i;
      if(idx<linhasIndexadas)
        lerLinhaVisualParaBuffer(f,idx,cacheLeitor[i],BYTES_CACHE_LINHA,i);
    }
  }else{
    int subir=-delta;
    int manter=LEITOR_LINHAS_VISIVEIS-subir;
    memmove(&cacheLeitor[subir][0],&cacheLeitor[0][0],manter*tamLinha);
    memset(&cacheLeitor[0][0],0,subir*tamLinha);
    memmove(destaqueInicioCache+subir,destaqueInicioCache,manter*sizeof(uint16_t));
    memmove(destaqueFimCache+subir,destaqueFimCache,manter*sizeof(uint16_t));
    memmove(inicioFisicoCache+subir,inicioFisicoCache,manter*sizeof(bool));
    memmove(linhaCacheValida+subir,linhaCacheValida,manter*sizeof(bool));
    memmove(offsetLinhaCache+subir,offsetLinhaCache,manter*sizeof(uint32_t));
    memset(destaqueInicioCache,0,subir*sizeof(uint16_t));
    memset(destaqueFimCache,0,subir*sizeof(uint16_t));
    memset(inicioFisicoCache,0,subir*sizeof(bool));
    memset(linhaCacheValida,0,subir*sizeof(bool));
    memset(offsetLinhaCache,0,subir*sizeof(uint32_t));

    for(int i=0;i<subir;i++){
      int idx=linhaTopo+i;
      if(idx<linhasIndexadas)
        lerLinhaVisualParaBuffer(f,idx,cacheLeitor[i],BYTES_CACHE_LINHA,i);
    }
  }

  f.close();
  cacheLeitorTopo=linhaTopo;
  contextoAntesCache=novoAntes;
  recalcularContextosCache(contextoAntesCache);
}

void desenharViewportLeitor()
{
  // Primeiro lemos/ajustamos o cache. So depois usamos o SPI para o TFT.
  // Assim SD e TFT nunca brigam pelo barramento durante a renderizacao.
  atualizarCacheLeitor();
  diagnosticarContextoSeMudou();

  for(int i=0;i<LEITOR_LINHAS_VISIVEIS;i++){
    montarLinhaRGB(cacheLeitor[i],i);
    int y=TEXTO_Y0+i*TEXTO_H;
    tft.drawRGBBitmap(4,y,bufferLinhaLeitor,LEITOR_BUFFER_W,TEXTO_H);
  }

  // Pequena faixa entre a ultima linha e a barra inferior.
  int fim=TEXTO_Y0+LEITOR_LINHAS_VISIVEIS*TEXTO_H;
  if(fim<204) tft.fillRect(0,fim,320,204-fim,COR_FUNDO);
  // Indicador + atalhos em uma unica passagem. Antes o contexto podia
  // redesenhar esta area duas vezes durante o mesmo scroll.
  desenharBarraBusca();
}

void desenharCabecalhoLeitor()
{
  tft.fillRect(0,0,320,21,COR_FUNDO);
  tft.drawFastHLine(0,20,320,COR_VERDE_ESCURO);

  tft.drawRoundRect(3,2,68,16,3,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(10,6); tft.print("< VOLTAR");

  // Recorta por caracteres completos, reservando o canto para a busca textual.
  imprimirUTF8(78,5,nomeArquivoAtual,COR_VERDE,COR_FUNDO,30);
  tft.drawRoundRect(264,2,52,16,3,COR_VERDE);
  tft.setCursor(275,6); tft.print("TEXTO");
}

void desenharTelaLeitor()
{
  tft.fillScreen(COR_FUNDO);
  desenharCabecalhoLeitor();
  desenharViewportLeitor();
}

// =====================================================
// TELA DE RELACOES JURIDICAS
// =====================================================
String nomeCategoriaRelacao(CategoriaRelacao categoria)
{
  switch(categoria){
    case REL_SUMULAS: return "SUMULAS";
    case REL_SUMULAS_VINCULANTES: return "SUMULAS VINCULANTES";
    case REL_ACORDAOS: return "ACORDAOS";
    case REL_REPERCUSSAO_GERAL: return "REPERCUSSAO GERAL";
    case REL_REPETITIVOS: return "RECURSOS REPETITIVOS";
    case REL_PRECEDENTES_RELEVANTES: return "PRECEDENTES RELEVANTES";
    case REL_CORRELATAS: return "LEGISLACAO CORRELATA";
    case REL_JURIS_TODAS: return "JURISPRUDENCIA";
    case REL_OUTROS: return "OUTROS PRECEDENTES";
    default: return "";
  }
}

int quantidadeCategoriaRelacao(CategoriaRelacao categoria)
{
  switch(categoria){
    case REL_SUMULAS: return totalSumulasArtigo;
    case REL_SUMULAS_VINCULANTES: return totalSumulasVinculantesArtigo;
    case REL_ACORDAOS: return totalAcordaosArtigo;
    case REL_REPERCUSSAO_GERAL: return totalRepercussaoGeralArtigo;
    case REL_REPETITIVOS: return totalRepetitivosArtigo;
    case REL_PRECEDENTES_RELEVANTES: return totalPrecedentesRelevantesArtigo;
    case REL_CORRELATAS: return totalCorrelatasArtigo;
    case REL_JURIS_TODAS: return totalRelacoesArtigo;
    case REL_OUTROS: return totalOutrosJurisArtigo;
    default: return 0;
  }
}

String montarRotuloContextoRelacoes(const String &artigo)
{
  String r="ART. "+artigo;
  if(contextoJuridicoAtivo.paragrafo[0]){
    if(strcmp(contextoJuridicoAtivo.paragrafo,"unico")==0) r+=" | PAR. UNICO";
    else r+=" | § "+String(contextoJuridicoAtivo.paragrafo)+"º";
  }
  if(contextoJuridicoAtivo.inciso[0]) r+=" | "+String(contextoJuridicoAtivo.inciso);
  if(contextoJuridicoAtivo.alinea[0]) r+=" | "+String(contextoJuridicoAtivo.alinea)+")";
  return r;
}

String contextoExatoCategoriaAtual()
{
  if(categoriaRelacaoAtual==REL_CORRELATAS){
    if(totalRelacoesCategoria>0) return correlatasArtigo[0].origem;
    return contextoRelacoesRotulo;
  }
  if(totalRelacoesCategoria>0){
    int idx=indicesRelacaoCategoria[0];
    if(idx>=0 && idx<totalRelacoesArtigo && relacoesArtigo[idx].referencia.length())
      return relacoesArtigo[idx].referencia;
  }
  if(totalRelacoesArtigo>0 && relacoesArtigo[0].referencia.length())
    return relacoesArtigo[0].referencia;
  return contextoRelacoesRotulo;
}

void desenharContextoRelacoesCabecalho(const String &rotulo="")
{
  String texto=rotulo.length()?rotulo:contextoRelacoesRotulo;
  if(texto.length()==0) return;
  imprimirUTF8(80,22,texto,COR_VERDE_SUAVE,COR_FUNDO,38);
}

void desenharLinhaCategoriaJuris(int indice)
{
  int y=43+indice*28;
  tft.fillRect(6,y,308,26,COR_FUNDO);
  if(indice<0 || indice>=totalCategoriasJuris) return;
  bool sel=indice==categoriaJurisSelecionada;
  tft.drawRoundRect(8,y,304,24,3,sel?COR_VERDE:COR_VERDE_ESCURO);
  CategoriaRelacao categoria=categoriasJurisDisponiveis[indice];
  String rotulo=nomeCategoriaRelacao(categoria)+" ("+String(quantidadeCategoriaRelacao(categoria))+")";
  imprimirUTF8(14,y+6,rotulo,sel?COR_VERDE:COR_VERDE_SUAVE,COR_FUNDO,42);
}

void desenharTelaCategoriasJuris()
{
  tft.fillScreen(COR_FUNDO);
  desenharMolduraCyber();
  tft.drawRoundRect(3,2,68,20,3,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(10,8); tft.print("< VOLTAR");
  imprimirUTF8(78,7,"JURISPRUDENCIA",COR_VERDE,COR_FUNDO,37);
  String contextoJuris=(totalRelacoesArtigo>0 && relacoesArtigo[0].referencia.length()) ? relacoesArtigo[0].referencia : contextoRelacoesRotulo;
  desenharContextoRelacoesCabecalho(contextoJuris);
  tft.drawFastHLine(8,36,304,COR_VERDE_ESCURO);
  for(int i=0;i<6;i++) desenharLinhaCategoriaJuris(i);
  tft.drawFastHLine(8,216,304,COR_VERDE_ESCURO);
  imprimirUTF8(10,224,"RODA/TOUCH: mover  ENTER: abrir",COR_VERDE_SUAVE,COR_FUNDO,48);
}

void desenharTelaReferenciasProvisoria()
{
  tft.fillScreen(COR_FUNDO);
  desenharMolduraCyber();
  tft.drawRoundRect(3,2,68,20,3,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(10,8); tft.print("< VOLTAR");
  imprimirUTF8(78,7,"REFERENCIAS",COR_VERDE,COR_FUNDO,37);
  imprimirUTF8(24,104,"SEM DADOS PARA ESTE CONTEXTO",COR_VERDE_SUAVE,COR_FUNDO,44);
}

void abrirTelaCategoriasJuris()
{
  if(totalCategoriasJuris<=0) return;
  uint32_t t0=micros();
  categoriaJurisSelecionada=0;
  telaAtual=TELA_JURIS_CATEGORIAS;
  desenharTelaCategoriasJuris();
  Serial.printf("PERF ABRIR_JURIS: %lu us\n",micros()-t0);
}

void moverSelecaoCategoriaJuris(int delta)
{
  if(delta==0 || totalCategoriasJuris<=0) return;
  int antigo=categoriaJurisSelecionada;
  categoriaJurisSelecionada=constrain(categoriaJurisSelecionada+delta,0,totalCategoriasJuris-1);
  if(antigo!=categoriaJurisSelecionada){
    desenharLinhaCategoriaJuris(antigo);
    desenharLinhaCategoriaJuris(categoriaJurisSelecionada);
  }
}

void desenharLinhaRelacao(int linhaVisual)
{
  if(linhaVisual<0 || linhaVisual>=RELACOES_VISIVEIS) return;
  int pos=primeiraRelacaoVisivel+linhaVisual;
  int y=43+linhaVisual*28;
  tft.fillRect(6,y,308,26,COR_FUNDO);
  if(pos<0 || pos>=totalRelacoesCategoria) return;

  bool sel=(pos==relacaoSelecionada);
  uint16_t cor=sel?COR_VERDE:COR_VERDE_SUAVE;
  tft.drawRoundRect(8,y,304,24,3,sel?COR_VERDE:COR_VERDE_ESCURO);

  String rotulo=String(pos+1)+" ";
  if(categoriaRelacaoAtual==REL_CORRELATAS){
    CorrelataJuridica &c=correlatasArtigo[pos];
    rotulo+=c.normaDestino;
    if(c.artigoDestino.length()) rotulo+=" ART. "+c.artigoDestino;
    else if(c.modoAbertura=="ABRIR_NORMA_SEM_SALTO") rotulo+=" (NORMA)";
  }else{
    int idx=indicesRelacaoCategoria[pos];
    RelacaoJuridica &r=relacoesArtigo[idx];
    rotulo+=rotuloTipoJurisprudencia(r);
  }
  imprimirUTF8(14,y+6,rotulo,cor,COR_FUNDO,34);
}

void desenharTelaRelacoes()
{
  tft.fillScreen(COR_FUNDO);
  desenharMolduraCyber();
  tft.drawRoundRect(3,2,68,20,3,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(10,8); tft.print("< VOLTAR");

  String titulo=nomeCategoriaRelacao(categoriaRelacaoAtual);
  titulo+=" ("+String(totalRelacoesCategoria)+")";
  imprimirUTF8(78,7,titulo,COR_VERDE,COR_FUNDO,37);
  desenharContextoRelacoesCabecalho(contextoExatoCategoriaAtual());
  tft.drawFastHLine(8,36,304,COR_VERDE_ESCURO);

  for(int i=0;i<RELACOES_VISIVEIS;i++) desenharLinhaRelacao(i);

  tft.drawFastHLine(8,216,304,COR_VERDE_ESCURO);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE_SUAVE,COR_FUNDO);
  tft.setCursor(10,224); tft.print("SETAS: mover  ENTER/numero: abrir");
}

void abrirCategoriaRelacao(CategoriaRelacao categoria)
{
  uint32_t t0=micros();
  categoriaRelacaoAtual=categoria;
  totalRelacoesCategoria=0;
  relacaoSelecionada=0;
  primeiraRelacaoVisivel=0;

  if(categoria==REL_CORRELATAS){
    totalRelacoesCategoria=totalCorrelatasArtigo;
  }else{
    for(int i=0;i<totalRelacoesArtigo;i++){
      String tipo=relacoesArtigo[i].tipo; tipo.toLowerCase();
      bool incluir=(categoria==REL_SUMULAS && tipo=="sumula") ||
                  (categoria==REL_SUMULAS_VINCULANTES && tipo=="sumula_vinculante") ||
                  (categoria==REL_ACORDAOS && tipo=="acordao") ||
                  (categoria==REL_REPERCUSSAO_GERAL && tipo=="repercussao_geral") ||
                  (categoria==REL_REPETITIVOS && tipo.indexOf("repetitivo")>=0) ||
                  (categoria==REL_PRECEDENTES_RELEVANTES && tipo=="precedente_relevante") ||
                  (categoria==REL_JURIS_TODAS) ||
                  (categoria==REL_OUTROS && classificarTipoJurisprudencia(tipo)==JTIPO_OUTRO);
      if(incluir && totalRelacoesCategoria<MAX_RELACOES_ARTIGO)
        indicesRelacaoCategoria[totalRelacoesCategoria++]=i;
    }
  }
  if(totalRelacoesCategoria<=0){
    categoriaRelacaoAtual=REL_NENHUMA;
    return;
  }
  telaAtual=TELA_RELACOES;
  desenharTelaRelacoes();
  Serial.printf("PERF ABRIR_LISTA: %lu us (itens=%d)\n",micros()-t0,totalRelacoesCategoria);
}

void moverSelecaoRelacao(int delta)
{
  if(totalRelacoesCategoria<=0 || delta==0) return;
  int antigo=relacaoSelecionada;
  int antigaPrimeira=primeiraRelacaoVisivel;
  relacaoSelecionada=constrain(relacaoSelecionada+delta,0,totalRelacoesCategoria-1);
  if(relacaoSelecionada==antigo) return;
  if(relacaoSelecionada<primeiraRelacaoVisivel) primeiraRelacaoVisivel=relacaoSelecionada;
  if(relacaoSelecionada>=primeiraRelacaoVisivel+RELACOES_VISIVEIS)
    primeiraRelacaoVisivel=relacaoSelecionada-RELACOES_VISIVEIS+1;
  if(primeiraRelacaoVisivel==antigaPrimeira){
    desenharLinhaRelacao(antigo-antigaPrimeira);
    desenharLinhaRelacao(relacaoSelecionada-primeiraRelacaoVisivel);
  }else{
    for(int i=0;i<RELACOES_VISIVEIS;i++) desenharLinhaRelacao(i);
  }
}

void rolarLeitor(int delta)
{
  if(delta==0) return;
  uint32_t t0=micros();

  // Limita saltos absurdos produzidos por varios eventos acumulados de touch,
  // mantendo resposta previsivel. Page Up/Down continuam funcionando.
  if(delta>LEITOR_LINHAS_VISIVEIS) delta=LEITOR_LINHAS_VISIVEIS;
  if(delta<-LEITOR_LINHAS_VISIVEIS) delta=-LEITOR_LINHAS_VISIVEIS;

  // Expandir a janela nao muda o byte do topo; apenas permite subir antes dele.
  if(delta<0){
    while(linhaTopo+delta<0 && offsetsLinhas[0]>0){
      if(indexarAntesDaJanela()==0) break;
    }
  }
  int antigo=linhaTopo;

  if(delta>0){
    int desejado=linhaTopo+delta;
    indexarAte(desejado+LEITOR_LINHAS_VISIVEIS+1);

    int maxConhecido=linhasIndexadas-1;
    if(fimDoArquivoIndexado)
      maxConhecido=max(0,linhasIndexadas-LEITOR_LINHAS_VISIVEIS);

    // Uma busca perto do EOF pode deixar menos de uma tela abaixo do topo.
    // Rolar para baixo nunca deve deslocar o leitor para tras nesse caso.
    linhaTopo=max(linhaTopo,min(desejado,maxConhecido));
  }else{
    linhaTopo=max(0,linhaTopo+delta);
  }

  if(linhaTopo==antigo) return;

  // O cache reaproveita as linhas que ja estavam em RAM e le do SD apenas
  // as linhas novas que entraram na tela.
  desenharViewportLeitor();

  uint32_t duracao=micros()-t0;
  perfScrollTotalUs+=duracao;
  if(duracao>perfScrollMaxUs) perfScrollMaxUs=duracao;
  perfScrollAmostras++;
  if(perfScrollAmostras>=32){
    Serial.printf("PERF SCROLL: media=%lu us max=%lu us heap=%u psram=%u relv2=%s\n",
                  perfScrollTotalUs/perfScrollAmostras,perfScrollMaxUs,
                  (unsigned)ESP.getFreeHeap(),(unsigned)ESP.getFreePsram(),
                  relacoesV2Cache?"PSRAM":"SD");
    perfScrollTotalUs=0;
    perfScrollMaxUs=0;
    perfScrollAmostras=0;
  }
}

void abrirRelacaoSelecionada()
{
  uint32_t t0=micros();
  if(telaAtual!=TELA_RELACOES || relacaoSelecionada<0 ||
     relacaoSelecionada>=totalRelacoesCategoria) return;

  if(categoriaRelacaoAtual==REL_CORRELATAS){
    CorrelataJuridica &c=correlatasArtigo[relacaoSelecionada];

    // V2 possui caminho TXT direto. V1 continua resolvendo pela pasta antiga.
    String caminho=c.caminhoTXT;
    bool ehV2=caminho.length()>0;
    if(!ehV2) caminho=primeiroTXTDaPasta(c.pastaDestino);

    if(caminho.length()==0){
      tft.fillRect(0,220,320,20,COR_FUNDO);
      tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
      tft.setCursor(6,228); tft.print("TXT DA CORRELATA NAO ENCONTRADO");
      return;
    }

    File arquivo=SD.open(caminho.c_str(),FILE_READ);
    if(!arquivo || arquivo.isDirectory()){
      if(arquivo) arquivo.close();
      tft.fillRect(0,220,320,20,COR_FUNDO);
      tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
      tft.setCursor(6,228); tft.print("ARQUIVO EXTERNO NAO ENCONTRADO");
      return;
    }

    origemCaminhoArtigo=caminhoArquivoAtual;
    origemNomeArtigo=nomeArquivoAtual;
    origemTamanhoArtigo=tamanhoArquivoAtual;
    origemTopoByte=(linhasIndexadas>0 && linhaTopo<linhasIndexadas)?offsetsLinhas[linhaTopo]:0;
    origemArtigoDigitado=artigoRelacoes;
    origemCategoriaRelacao=categoriaRelacaoAtual;
    origemRelacaoSelecionada=relacaoSelecionada;
    origemPrimeiraRelacaoVisivel=primeiraRelacaoVisivel;
    origemCategoriaJurisSelecionada=categoriaJurisSelecionada;
    contextoDocumentoReferencia=c.origem;

    caminhoArquivoAtual=caminho;
    nomeArquivoAtual=c.normaDestino;
    if(c.artigoDestino.length()) nomeArquivoAtual+=" - ART. "+c.artigoDestino;
    tamanhoArquivoAtual=arquivo.size();
    arquivo.close();

    reiniciarEstadoBusca();
    reiniciarBuscaTexto();
    visualizandoReferencia=true;

    if(ehV2){
      uint32_t offsetDestino=0;
      if(c.modoAbertura=="ABRIR_ARTIGO_INTERNO" && c.artigoDestino.length()){
        if(!buscarOffsetArtigoExternoV2(c.normaId,c.artigoDestino,offsetDestino)){
          // Falha segura: a relacao continua valida no nivel da norma,
          // mas nunca fazemos um salto cujo artigo nao esteja no indice.
          Serial.print("RELATIONS V2: artigo destino nao indexado: ");
          Serial.print(c.normaId); Serial.print(" ART. "); Serial.println(c.artigoDestino);
          offsetDestino=0;
        }
      }
      buscaAtiva=BUSCA_NENHUMA;
      artigoDigitado="";
      reiniciarIndice(offsetDestino);
      linhaTopo=0;
    }else{
      // Compatibilidade integral com correlatas V1.
      buscaAtiva=BUSCA_ARTIGO;
      artigoDigitado=c.artigoDestino;
      if(!pesquisarArtigo(c.artigoDestino,0)){
        caminhoArquivoAtual=origemCaminhoArtigo;
        nomeArquivoAtual=origemNomeArtigo;
        tamanhoArquivoAtual=origemTamanhoArtigo;
        artigoDigitado=origemArtigoDigitado;
        visualizandoReferencia=false;
        reiniciarIndice(origemTopoByte);
        linhaTopo=0;
        telaAtual=TELA_LEITOR;
        desenharTelaLeitor();
        return;
      }
    }

    telaAtual=TELA_LEITOR;
    desenharTelaLeitor();
    Serial.printf("PERF ABRIR_ITEM: %lu us (%s)\\n",
                  micros()-t0,ehV2?"correlata-v2":"correlata-v1");
    return;
  }

  int idx=indicesRelacaoCategoria[relacaoSelecionada];
  RelacaoJuridica &r=relacoesArtigo[idx];
  String caminho=caminhoArquivoRelacao(r);
  if(caminho.length()==0){
    tft.fillRect(0,220,320,20,COR_FUNDO);
    tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
    tft.setCursor(6,228); tft.print("ARQUIVO DA REFERENCIA NAO ENCONTRADO");
    return;
  }

  File arquivo=SD.open(caminho.c_str(),FILE_READ);
  if(!arquivo || arquivo.isDirectory()){
    if(arquivo) arquivo.close();
    return;
  }

  origemCaminhoArtigo=caminhoArquivoAtual;
  origemNomeArtigo=nomeArquivoAtual;
  origemTamanhoArtigo=tamanhoArquivoAtual;
  origemTopoByte=(linhasIndexadas>0 && linhaTopo<linhasIndexadas)?offsetsLinhas[linhaTopo]:0;
  origemArtigoDigitado=artigoRelacoes;
  origemCategoriaRelacao=categoriaRelacaoAtual;
  origemRelacaoSelecionada=relacaoSelecionada;
  origemPrimeiraRelacaoVisivel=primeiraRelacaoVisivel;
  origemCategoriaJurisSelecionada=categoriaJurisSelecionada;
  contextoDocumentoReferencia=r.referencia;

  caminhoArquivoAtual=caminho;
  nomeArquivoAtual=r.tribunal+" "+rotuloTipoJurisprudencia(r);
  tamanhoArquivoAtual=arquivo.size();
  arquivo.close();

  reiniciarEstadoBusca();
  reiniciarBuscaTexto();
  buscaAtiva=BUSCA_NENHUMA;
  artigoDigitado="";
  visualizandoReferencia=true;
  reiniciarIndice(0);
  telaAtual=TELA_LEITOR;
  desenharTelaLeitor();
  Serial.printf("PERF ABRIR_ITEM: %lu us (direto)\n",micros()-t0);
}

void restaurarArtigoAposReferencia()
{
  if(!visualizandoReferencia) return;
  caminhoArquivoAtual=origemCaminhoArtigo;
  nomeArquivoAtual=origemNomeArtigo;
  tamanhoArquivoAtual=origemTamanhoArtigo;
  artigoDigitado=origemArtigoDigitado;
  visualizandoReferencia=false;
  contextoDocumentoReferencia="";
  buscaAtiva=BUSCA_ARTIGO;
  modoDigitacaoArtigo=false;
  reiniciarIndice(origemTopoByte);
  linhaTopo=0;
  categoriaRelacaoAtual=origemCategoriaRelacao;
  relacaoSelecionada=origemRelacaoSelecionada;
  primeiraRelacaoVisivel=origemPrimeiraRelacaoVisivel;
  categoriaJurisSelecionada=origemCategoriaJurisSelecionada;
  telaAtual=TELA_RELACOES;
  desenharTelaRelacoes();
}

void voltarDaTelaRelacoes()
{
  if(telaAtual!=TELA_RELACOES) return;
  bool veioDaJuris=categoriaRelacaoAtual!=REL_CORRELATAS &&
                   categoriaRelacaoAtual!=REL_JURIS_TODAS;
  categoriaRelacaoAtual=REL_NENHUMA;
  if(veioDaJuris){
    telaAtual=TELA_JURIS_CATEGORIAS;
    desenharTelaCategoriasJuris();
  }else{
    telaAtual=TELA_LEITOR;
    modoDigitacaoArtigo=false;
    desenharTelaLeitor();
  }
}

void abrirPastaSelecionada()
{
  if(pastaSelecionada<0 || pastaSelecionada>=totalPastas) return;
  String caminho=caminhoFilho(pastaAtual,pastas[pastaSelecionada]);
  if(itemEhPasta[pastaSelecionada]){
    carregarPastas(caminho);
    desenharTelaPastas();
    return;
  }
  File arquivo=SD.open(caminho.c_str(),FILE_READ);
  if(!arquivo || arquivo.isDirectory()){
    if(arquivo) arquivo.close();
    statusSD="ERRO AO ABRIR TXT";
    desenharTelaPastas();
    return;
  }
  caminhoArquivoAtual=caminho;
  nomeArquivoAtual=pastas[pastaSelecionada];
  tamanhoArquivoAtual=arquivo.size();
  arquivo.close();
  reiniciarEstadoBusca(); // Inclusive ao reabrir o mesmo TXT.
  reiniciarBuscaTexto();
  limparRelacoesArtigo();
  visualizandoReferencia=false;
  modoDigitacaoArtigo=true;
  buscaAtiva=BUSCA_NENHUMA;
  pedirBuscaTexto=false;
  // Preserva a indexacao sob demanda e o cache do leitor estavel.
  reiniciarIndice(0);
  artigoDigitado="";
  telaAtual=TELA_LEITOR;
  desenharTelaLeitor();
}

void voltarPastas()
{
  if(telaAtual==TELA_JURIS_CATEGORIAS || telaAtual==TELA_REFERENCIAS){
    telaAtual=TELA_LEITOR;
    modoDigitacaoArtigo=false;
    desenharTelaLeitor();
    return;
  }
  if(telaAtual==TELA_RELACOES){
    voltarDaTelaRelacoes();
    return;
  }
  if(telaAtual==TELA_LEITOR && visualizandoReferencia){
    restaurarArtigoAposReferencia();
    return;
  }

  artigoDigitado="";
  if(telaAtual==TELA_LEITOR){
    destaqueTextoAtivo=false;
    limparRelacoesArtigo();
    modoDigitacaoArtigo=true;
    // Mantem a pasta, a selecao e a posicao da lista ao sair do TXT.
    telaAtual=TELA_PASTAS;
    desenharTelaPastas();
  }else if(telaAtual==TELA_PASTAS){
    if(pastaAtual=="/"){
      abrirSplashManual();
      return;
    }
    String anterior=somenteNome(pastaAtual);
    int separador=pastaAtual.lastIndexOf('/');
    String pai=separador<=0 ? String("/") : pastaAtual.substring(0,separador);
    if(carregarPastas(pai)){
      for(int i=0;i<totalPastas;i++){
        if(itemEhPasta[i] && pastas[i]==anterior){
          pastaSelecionada=i;
          primeiraPastaVisivel=max(0,i-PASTAS_VISIVEIS+1);
          break;
        }
      }
    }
    desenharTelaPastas();
  }
}

// =====================================================
// PESQUISA DE ARTIGO - RAPIDA, SEM CONSUMIR MUITA RAM
// =====================================================
bool ehDigitoAscii(char c){ return c>='0' && c<='9'; }

bool acharPadraoNoBuffer(char *buf, int total, const char *padrao, int &indice, bool ultimoBloco, bool inicioLinhaNoBuffer)
{
  // O padrao contem somente o marcador, um espaco e o numero.
  const char *numero=strchr(padrao,' ');
  if(!numero) return false;
  int marcadorLen=numero-padrao;
  numero++;
  int numeroLen=strlen(numero);
  const int MAX_WHITESPACE_ARTIGO=32;
  if(numeroLen<=0) return false;

  // Estado ANTES de buf[0], herdado dos bytes anteriores do arquivo.
  // Somente LF reinicia a linha; CRLF funciona porque o LF vem depois do CR.
  bool inicioLinha=inicioLinhaNoBuffer;
  for(int i=0; i+marcadorLen<=total; i++){
    bool candidato=inicioLinha;
    char atual=buf[i];
    inicioLinha=(atual=='\n') ||
                (inicioLinha && (atual==' ' || atual=='\t'));
    if(!candidato) continue;
    bool ok=true;
    for(int j=0; j<marcadorLen; j++){
      char a=buf[i+j];
      if(a>='A' && a<='Z') a=(char)(a+32);
      if(a!=padrao[j]){ ok=false; break; }
    }
    if(!ok) continue;

    int inicioNumero=i+marcadorLen;
    int whitespace=0;
    while(inicioNumero<total){
      char c=buf[inicioNumero];
      if(c!=' ' && c!='\t' && c!='\r' && c!='\n') break;
      inicioNumero++;
      if(++whitespace>MAX_WHITESPACE_ARTIGO) break;
    }
    if(whitespace>MAX_WHITESPACE_ARTIGO) continue;
    // Art.5 continua valido; a palavra Artigo exige separacao.
    if(marcadorLen==6 && whitespace==0) continue;
    if(inicioNumero+numeroLen>total) continue;
    if(memcmp(buf+inicioNumero,numero,numeroLen)!=0) continue;

    // Nunca aceite um prefixo de numero (100 em 1000, 1 em 1.000).
    // No limite do bloco, espere o proximo: a sobreposicao preserva o padrao.
    int depois=inicioNumero+numeroLen;
    if(depois==total && !ultimoBloco) continue;
    char prox=(depois<total)?buf[depois]:'\0';
    if(ehDigitoAscii(prox)) continue;
    if(prox=='.'){
      if(depois+1==total && !ultimoBloco) continue;
      if(depois+1<total && ehDigitoAscii(buf[depois+1])) continue;
    }
    indice=i;
    return true;
  }
  return false;
}

bool correspondeArtigoNoInicioLinhaRapido(const char *buf, int total, int i,
                                          const char *numero, int numeroLen,
                                          bool ultimoBloco, bool permitirQuebraLinha,
                                          int &fimMatch)
{
  int p=i;
  if(p+3>total) return false;
  char a0=buf[p], a1=buf[p+1], a2=buf[p+2];
  if(a0>='A'&&a0<='Z') a0+=32;
  if(a1>='A'&&a1<='Z') a1+=32;
  if(a2>='A'&&a2<='Z') a2+=32;
  if(a0!='a' || a1!='r' || a2!='t') return false;
  p+=3;

  // Aceita "Art.", "Art" e "Artigo". Para "Artigo", exige separacao.
  bool palavraArtigo=false;
  if(p+3<=total){
    char c0=buf[p], c1=buf[p+1], c2=buf[p+2];
    if(c0>='A'&&c0<='Z') c0+=32;
    if(c1>='A'&&c1<='Z') c1+=32;
    if(c2>='A'&&c2<='Z') c2+=32;
    if(c0=='i' && c1=='g' && c2=='o'){ palavraArtigo=true; p+=3; }
  }
  if(!palavraArtigo && p<total && buf[p]=='.') p++;

  int espacos=0;
  while(p<total && (buf[p]==' ' || buf[p]=='\t' || buf[p]=='\r' ||
                     (permitirQuebraLinha && buf[p]=='\n'))){
    p++; if(++espacos>32) return false;
  }
  if(palavraArtigo && espacos==0) return false;

  // Compara o numero ignorando pontos de milhar no TXT (1.000 == 1000).
  int n=0;
  while(p<total && n<numeroLen){
    if(buf[p]=='.'){ p++; continue; }
    if(buf[p]!=numero[n]) return false;
    p++; n++;
  }
  if(n!=numeroLen) return false;
  while(p<total && buf[p]=='.'){
    // Um ponto seguido de digito ainda pertence a um numero maior.
    if(p+1>=total){ if(!ultimoBloco) return false; break; }
    if(ehDigitoAscii(buf[p+1])) return false;
    break;
  }
  if(p>=total && !ultimoBloco) return false;
  if(p<total && ehDigitoAscii(buf[p])) return false;
  fimMatch=p;
  return true;
}

bool pesquisarArtigo(const String &numero, uint32_t inicioBusca)
{
  uint32_t t0=micros();
  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f) return false;
  uint32_t tamanho=f.size();
  if(inicioBusca>=tamanho || !f.seek(inicioBusca)){
    f.close();
    return false;
  }

  // O arquivo pode ter MB. A busca antiga usava blocos de 2 KB e fazia ate
  // quatro varreduras completas por bloco. Aqui fazemos UMA passagem por
  // blocos grandes, preferencialmente em PSRAM, examinando apenas inicios de linha.
  const int BLOCO_PSRAM=32768;
  const int BLOCO_FALLBACK=4096;
  const int SOBREPOSICAO=128;
  int bloco=BLOCO_FALLBACK;
  char *buf=nullptr;
  if(psramFound()){
    buf=(char*)heap_caps_malloc(BLOCO_PSRAM+SOBREPOSICAO+1,
                               MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if(buf) bloco=BLOCO_PSRAM;
  }
  if(!buf) buf=(char*)heap_caps_malloc(BLOCO_FALLBACK+SOBREPOSICAO+1,MALLOC_CAP_8BIT);
  if(!buf){ f.close(); return false; }

  char numeroAscii[24];
  int numeroLen=min((int)numero.length(),(int)sizeof(numeroAscii)-1);
  memcpy(numeroAscii,numero.c_str(),numeroLen); numeroAscii[numeroLen]='\0';

  int carry=0;
  bool inicioLinhaNoBuffer=(inicioBusca==0);
  uint32_t bytesLidos=inicioBusca;
  uint32_t posAchada=0;
  bool achou=false;

  while(f.available()){
    int n=f.read((uint8_t*)buf+carry,bloco);
    if(n<=0) break;
    int total=carry+n;
    buf[total]='\0';
    uint32_t baseBuffer=(bytesLidos >= (uint32_t)carry) ? bytesLidos-(uint32_t)carry : 0;
    bool ultimoBloco=!f.available();

    // A maioria das normas usa cabeçalhos de artigo no início físico da linha.
    // O cf.txt é uma exceção histórica: vários artigos foram extraídos no meio
    // de linhas longas. Para a CF aceitamos também "Art." com A MAIÚSCULO
    // fora do início da linha. Remissões comuns aparecem como "art." minúsculo
    // e continuam descartadas, preservando a precisão da busca rápida.
    bool arquivoConstituicao = caminhoArquivoAtual.startsWith("/1- CONSTITUIÇÃO FEDERAL/") ||
                              nomeArquivoAtual.equalsIgnoreCase("cf.txt");
    bool inicioLinha=inicioLinhaNoBuffer;
    for(int i=0;i<total;i++){
      bool candidatoInicioLinha=inicioLinha;
      char atual=buf[i];
      inicioLinha=(atual=='\n') || (inicioLinha && (atual==' ' || atual=='\t'));

      bool candidatoCFMeioLinha = arquivoConstituicao && buf[i]=='A';
      if(!candidatoInicioLinha && !candidatoCFMeioLinha) continue;

      int fimMatch=0;
      if(correspondeArtigoNoInicioLinhaRapido(buf,total,i,numeroAscii,numeroLen,
                                             ultimoBloco,arquivoConstituicao,fimMatch)){
        posAchada=baseBuffer+(uint32_t)i;
        achou=true;
        break;
      }
    }
    if(achou) break;

    bytesLidos+=(uint32_t)n;
    carry=min(SOBREPOSICAO,total);
    int descartados=total-carry;
    // Estado de inicio de linha no ponto que vira buf[0] no proximo bloco.
    bool estado=inicioLinhaNoBuffer;
    for(int i=0;i<descartados;i++){
      char c=buf[i];
      estado=(c=='\n') || (estado && (c==' ' || c=='\t'));
    }
    inicioLinhaNoBuffer=estado;
    memmove(buf,buf+descartados,carry);
    yield();
  }

  heap_caps_free(buf);
  f.close();
  if(!achou){
    Serial.printf("PERF BUSCA_ARTIGO: %lu ms (nao encontrado, bloco=%d)\n",
                  (micros()-t0)/1000,bloco);
    return false;
  }

  reiniciarIndice(posAchada);
  linhaTopo=0;

  // A busca acabou de localizar o inicio exato do artigo. Antes, ao desenhar
  // a primeira tela depois do salto, o leitor reconstruia ate 256 KB de texto
  // anterior apenas para descobrir o contexto juridico. Para um salto direto
  // isso e desnecessario: antes da propria linha "Art. N" o contexto pode
  // comecar vazio, pois a linha visivel sera parseada imediatamente e passara
  // a ser o contexto ativo. Este checkpoint exato elimina a releitura massiva
  // do SD na abertura de artigos distantes (correlatas e busca numerica).
  ContextoJuridicoAtivo contextoAntesDoArtigo;
  limparContextoJuridico(contextoAntesDoArtigo,nomeArquivoAtual.c_str());

  // Na Constituição, alguns cabeçalhos "Art. N" não começam uma linha física.
  // Nesse caso o parser visual, por segurança, não os trataria como dispositivo.
  // Como a própria busca acabou de validar o cabeçalho solicitado, semeamos o
  // contexto com o número encontrado. Isso mantém o indicador do rodapé correto
  // sem alterar a regra geral anti-falso-positivo do leitor.
  bool arquivoConstituicao = caminhoArquivoAtual.startsWith("/1- CONSTITUIÇÃO FEDERAL/") ||
                            nomeArquivoAtual.equalsIgnoreCase("cf.txt");
  if(arquivoConstituicao){
    copiarContextoCampo(contextoAntesDoArtigo.artigo,
                        sizeof(contextoAntesDoArtigo.artigo),
                        numero.c_str());
    contextoAntesDoArtigo.offsetArtigo=posAchada;
  }
  guardarCheckpointContexto(posAchada,contextoAntesDoArtigo);

  offsetUltimaOcorrencia=posAchada;
  inicioProximaBusca=posAchada+1;
  temOcorrenciaDaBusca=true;
  Serial.printf("PERF BUSCA_ARTIGO: %lu ms (offset=%lu, bloco=%d)\n",
                (micros()-t0)/1000,(unsigned long)posAchada,bloco);
  return true;
}

void limparDestaqueTexto()
{
  if(!destaqueTextoAtivo) return;
  destaqueTextoAtivo=false;
  if(telaAtual==TELA_LEITOR) desenharViewportLeitor();
}

void executarBusca()
{
  if(artigoDigitado.length()==0) return;
  limparDestaqueTexto();

  String n=artigoDigitado;
  if(numeroBuscaEditado || n!=numeroUltimaBusca){
    reiniciarEstadoBusca();
    numeroUltimaBusca=n;
  }
  bool buscarProxima=temOcorrenciaDaBusca;
  uint32_t inicio=buscarProxima ? inicioProximaBusca : 0;

  tft.fillRect(0,220,320,20,COR_FUNDO);
  tft.drawFastHLine(0,220,320,COR_VERDE_ESCURO);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(4,228); tft.print("Buscando Art. "); tft.print(n); tft.print("...");

  if(pesquisarArtigo(n,inicio)){
    // O viewport atualiza o contexto ativo e somente entao consulta o indice,
    // evitando usar paragrafo/inciso da posicao anterior durante o salto.
    desenharViewportLeitor();
    desenharBarraBusca();
  }else{
    tft.fillRect(0,220,320,20,COR_FUNDO);
    tft.drawFastHLine(0,220,320,COR_VERDE_ESCURO);
    tft.setCursor(4,228);
    if(buscarProxima) tft.print("SEM OUTRA OCORRENCIA");
    else {tft.print("ART. "); tft.print(n); tft.print(" NAO ENCONTRADO");}
    delay(500);
    desenharBarraBusca();
  }
}

// =====================================================
// BUSCA TEXTUAL UTF-8 EM BLOCOS / TECLADO VIRTUAL
// =====================================================
bool ehSeparadorBuscaTexto(uint32_t cp)
{
  if(cp==' ' || cp=='\t' || cp=='\r' || cp=='\n' || cp=='-') return true;
  switch(cp){
    case 0x00A0: // espaco nao separavel
    case 0x00AD: // hifen opcional
    case 0x2010: case 0x2011: case 0x2012: case 0x2013:
    case 0x2014: case 0x2015: case 0x2212:
    case 0xFE58: case 0xFE63: case 0xFF0D:
      return true;
    default:
      return false;
  }
}

char normalizarBuscaTexto(uint32_t cp)
{
  if(ehSeparadorBuscaTexto(cp)) return ' ';
  if(cp>='A' && cp<='Z') return (char)(cp+32);
  if(cp<128) return (char)cp;
  switch(cp){
    case 0x00C0: case 0x00C1: case 0x00C2: case 0x00C3: case 0x00C4:
    case 0x00E0: case 0x00E1: case 0x00E2: case 0x00E3: case 0x00E4: return 'a';
    case 0x00C8: case 0x00C9: case 0x00CA: case 0x00CB:
    case 0x00E8: case 0x00E9: case 0x00EA: case 0x00EB: return 'e';
    case 0x00CC: case 0x00CD: case 0x00CE: case 0x00CF:
    case 0x00EC: case 0x00ED: case 0x00EE: case 0x00EF: return 'i';
    case 0x00D2: case 0x00D3: case 0x00D4: case 0x00D5: case 0x00D6:
    case 0x00F2: case 0x00F3: case 0x00F4: case 0x00F5: case 0x00F6: return 'o';
    case 0x00D9: case 0x00DA: case 0x00DB: case 0x00DC:
    case 0x00F9: case 0x00FA: case 0x00FB: case 0x00FC: return 'u';
    case 0x00C7: case 0x00E7: return 'c';
    default: return 0; // Nao une palavras atraves de simbolos desconhecidos.
  }
}

int normalizarConsultaTexto(const char *entrada, char *saida)
{
  int i=0, n=0;
  bool separadorPendente=false;
  while(entrada[i]){
    uint16_t cp=proximoUnicodeBuffer(entrada,i);
    if(cp>=0x0300 && cp<=0x036F) continue;
    char c=normalizarBuscaTexto(cp);
    if(c==0){saida[0]='\0'; return 0;}
    if(c==' '){
      // Remove margens e adia um unico espaco ate aparecer a proxima palavra.
      if(n>0) separadorPendente=true;
      continue;
    }
    if(separadorPendente){
      if(n>=MAX_CONSULTA_TEXTO){saida[0]='\0'; return 0;}
      saida[n++]=' ';
      separadorPendente=false;
    }
    if(n>=MAX_CONSULTA_TEXTO){saida[0]='\0'; return 0;}
    saida[n++]=c;
  }
  saida[n]='\0';
  return n;
}

bool ehAlfanumericoBuscaTexto(char c)
{
  return (c>='a' && c<='z') || (c>='0' && c<='9');
}

// Todos os termos devem caber nesta janela, em qualquer ordem.
// 1=encontrou, 0=fim sem resultado, -1=erro de leitura.
int localizarTextoEmBlocos(const char *consulta, uint32_t inicio,
                          uint32_t &encontrado, uint32_t &depois)
{
  char consultaNormalizada[MAX_CONSULTA_TEXTO+1];
  int tamanho=normalizarConsultaTexto(consulta,consultaNormalizada);
  if(tamanho<=0) return 0;

  uint8_t inicioTermo[MAX_TERMOS_TEXTO];
  uint8_t tamanhoTermo[MAX_TERMOS_TEXTO];
  int totalTermos=0;
  for(int i=0;i<tamanho;){
    while(i<tamanho && !ehAlfanumericoBuscaTexto(consultaNormalizada[i])) i++;
    if(i>=tamanho) break;
    int primeiro=i;
    while(i<tamanho && ehAlfanumericoBuscaTexto(consultaNormalizada[i])) i++;
    int comprimento=i-primeiro;
    bool repetido=false;
    for(int t=0;t<totalTermos;t++){
      if(tamanhoTermo[t]==comprimento &&
         memcmp(consultaNormalizada+inicioTermo[t],
                consultaNormalizada+primeiro,comprimento)==0){
        repetido=true;
        break;
      }
    }
    if(repetido) continue;
    if(totalTermos>=MAX_TERMOS_TEXTO) return 0;
    inicioTermo[totalTermos]=(uint8_t)primeiro;
    tamanhoTermo[totalTermos]=(uint8_t)comprimento;
    totalTermos++;
  }
  if(totalTermos<=0) return 0;

  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f) return -1;
  if(inicio>=f.size()){f.close(); return 0;}
  if(!f.seek(inicio)){f.close(); return -1;}

  // Uma palavra e acumulada entre dois limites nao alfanumericos. Isso valida
  // simultaneamente os limites esquerdo e direito, sem copiar o TXT para RAM.
  static uint8_t blocoTexto[1024];
  char palavra[MAX_CONSULTA_TEXTO+1];
  int tamanhoPalavra=0;
  bool palavraLonga=false;
  uint32_t palavraInicioLogico=0, palavraFimLogico=0;
  uint32_t palavraInicioByte=0, palavraFimByte=0;
  bool termoEncontrado[MAX_TERMOS_TEXTO]={false};
  uint32_t ultimoInicioLogico[MAX_TERMOS_TEXTO]={0};
  uint32_t ultimoFimLogico[MAX_TERMOS_TEXTO]={0};
  uint32_t ultimoInicioByte[MAX_TERMOS_TEXTO]={0};
  uint32_t ultimoFimByte[MAX_TERMOS_TEXTO]={0};

  auto concluirPalavra=[&]()->bool {
    if(tamanhoPalavra<=0){palavraLonga=false; return false;}
    if(!palavraLonga){
      palavra[tamanhoPalavra]='\0';
      for(int t=0;t<totalTermos;t++){
        if(tamanhoTermo[t]==tamanhoPalavra &&
           memcmp(palavra,consultaNormalizada+inicioTermo[t],tamanhoPalavra)==0){
          ultimoInicioLogico[t]=palavraInicioLogico;
          ultimoFimLogico[t]=palavraFimLogico;
          ultimoInicioByte[t]=palavraInicioByte;
          ultimoFimByte[t]=palavraFimByte;
          termoEncontrado[t]=true;
        }
      }
    }
    tamanhoPalavra=0;
    palavraLonga=false;

    bool todos=true;
    uint32_t menorInicio=0, maiorFim=0;
    int termoInicial=0, termoFinal=0;
    for(int t=0;t<totalTermos;t++){
      if(!termoEncontrado[t]){todos=false; break;}
      if(t==0 || ultimoInicioLogico[t]<menorInicio){
        menorInicio=ultimoInicioLogico[t];
        termoInicial=t;
      }
      if(t==0 || ultimoFimLogico[t]>maiorFim){
        maiorFim=ultimoFimLogico[t];
        termoFinal=t;
      }
    }
    if(todos && maiorFim-menorInicio+1<=JANELA_TERMOS_TEXTO){
      encontrado=ultimoInicioByte[termoInicial];
      depois=ultimoFimByte[termoFinal];
      return true;
    }
    return false;
  };

  bool ultimoLogicoFoiSeparador=false;
  uint32_t posicaoLogica=0;
  uint32_t inicioCP=inicio, cp=0, minimoCP=0;
  uint8_t faltam=0;
  while(f.available()){
    uint32_t baseBloco=f.position(); // Byte absoluto real ANTES da leitura SD.
    int n=f.read(blocoTexto,sizeof(blocoTexto));
    if(n<=0){f.close(); return -1;}
    for(int i=0;i<n;i++){
      uint32_t absoluto=baseBloco+(uint32_t)i;
      uint8_t b=blocoTexto[i];
      if(faltam>0 && (b & 0xC0)==0x80){
        cp=(cp<<6)|(b & 0x3F);
        if(--faltam>0) continue;
        if(cp<minimoCP || cp>0x10FFFF || (cp>=0xD800 && cp<=0xDFFF)){
          if(concluirPalavra()){f.close(); return 1;}
          if(!ultimoLogicoFoiSeparador) posicaoLogica++;
          ultimoLogicoFoiSeparador=true;
          continue;
        }
      }else{
        if(faltam>0){
          faltam=0;
          if(concluirPalavra()){f.close(); return 1;}
          if(!ultimoLogicoFoiSeparador) posicaoLogica++;
          ultimoLogicoFoiSeparador=true;
        }
        inicioCP=absoluto;
        if(b<0x80) cp=b;
        else if(b>=0xC2 && b<=0xDF){cp=b & 0x1F; faltam=1; minimoCP=0x80; continue;}
        else if(b>=0xE0 && b<=0xEF){cp=b & 0x0F; faltam=2; minimoCP=0x800; continue;}
        else if(b>=0xF0 && b<=0xF4){cp=b & 0x07; faltam=3; minimoCP=0x10000; continue;}
        else {
          if(concluirPalavra()){f.close(); return 1;}
          if(!ultimoLogicoFoiSeparador) posicaoLogica++;
          ultimoLogicoFoiSeparador=true;
          continue;
        }
      }
      // Acentos decompostos (NFD) tambem nao alteram a comparacao.
      if(cp>=0x0300 && cp<=0x036F){
        if(tamanhoPalavra>0) palavraFimByte=absoluto+1;
        continue;
      }
      char c=normalizarBuscaTexto(cp);
      if(ehAlfanumericoBuscaTexto(c)){
        if(tamanhoPalavra==0){
          palavraInicioLogico=posicaoLogica;
          palavraInicioByte=inicioCP;
        }
        if(tamanhoPalavra<MAX_CONSULTA_TEXTO) palavra[tamanhoPalavra++]=c;
        else palavraLonga=true;
        palavraFimLogico=posicaoLogica;
        palavraFimByte=absoluto+1;
        ultimoLogicoFoiSeparador=false;
        posicaoLogica++;
      }else{
        // Qualquer pontuacao, espaco, hifen ou simbolo encerra a palavra.
        if(concluirPalavra()){f.close(); return 1;}
        if(!ultimoLogicoFoiSeparador){
          ultimoLogicoFoiSeparador=true;
          posicaoLogica++;
        }
      }
    }
    yield();
  }
  if(concluirPalavra()){f.close(); return 1;} // Limite direito: fim do arquivo.
  f.close();
  return 0;
}

void desenharCampoBuscaTexto()
{
  tft.fillRect(0,0,320,83,COR_FUNDO);
  imprimirUTF8(6,4,"BUSCA POR TEXTO",COR_VERDE,COR_FUNDO,40);
  tft.drawRect(4,19,312,43,COR_VERDE_SUAVE);
  // Duas linhas de 50 caracteres: toda consulta de 80 permanece visivel.
  int tamanho=strlen(consultaTexto);
  for(int i=0;i<tamanho;i++)
    desenharCaractereUnicode(8+(i%50)*6,24+(i/50)*15,consultaTexto[i],COR_VERDE,COR_FUNDO);
  if(cursorBuscaTexto<0) cursorBuscaTexto=0;
  if(cursorBuscaTexto>tamanho) cursorBuscaTexto=tamanho;
  // A fonte padrao usada neste campo e monoespacada: cada caractere ocupa 6 px.
  int cursorX=8+(cursorBuscaTexto%50)*6;
  int cursorY=24+(cursorBuscaTexto/50)*15;
  tft.drawFastVLine(cursorX,cursorY,9,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE_SUAVE,COR_FUNDO);
  tft.setCursor(270,6); tft.print(tamanho); tft.print("/80");
  imprimirUTF8(6,68,statusBuscaTexto,COR_VERDE_SUAVE,COR_FUNDO,51);
}

void desenharTeclaTexto(int x, int y, int w, const char *rotulo)
{
  tft.drawRoundRect(x,y,w,32,3,COR_VERDE);
  tft.setTextSize(1); tft.setTextColor(COR_VERDE,COR_FUNDO);
  tft.setCursor(x+(w-(int)strlen(rotulo)*6)/2,y+12);
  tft.print(rotulo);
}

void desenharTelaBuscaTexto()
{
  tft.fillScreen(COR_FUNDO);
  desenharCampoBuscaTexto();
  const char *linhas[]={"QWERTYUIOP","ASDFGHJKL","ZXCVBNM"};
  for(int l=0;l<3;l++){
    int total=strlen(linhas[l]);
    int x0=(320-total*32)/2;
    for(int c=0;c<total;c++){
      char rotulo[2]={linhas[l][c],0};
      desenharTeclaTexto(x0+c*32+1,86+l*36,30,rotulo);
    }
  }
  const char *comandos[]={"ESPACO","APAGAR","ENTER","FECHAR"};
  for(int i=0;i<4;i++) desenharTeclaTexto(1+i*80,202,78,comandos[i]);
}

void abrirBuscaTexto()
{
  buscaAtiva=BUSCA_TEXTO;
  telaAtual=TELA_BUSCA_TEXTO;
  desenharTelaBuscaTexto();
}

void fecharBuscaTexto()
{
  telaAtual=TELA_LEITOR;
  desenharTelaLeitor(); // Sem reiniciar indice ou estado de qualquer busca.
}

void mostrarStatusBuscaTexto()
{
  if(telaAtual==TELA_BUSCA_TEXTO) desenharCampoBuscaTexto();
  else if(telaAtual==TELA_LEITOR){
    tft.fillRect(0,220,320,20,COR_FUNDO);
    tft.drawFastHLine(0,220,320,COR_VERDE_ESCURO);
    imprimirUTF8(4,226,statusBuscaTexto,COR_VERDE,COR_FUNDO,51);
  }
}

bool posicionarResultadoTexto(uint32_t ocorrencia)
{
  File f=SD.open(caminhoArquivoAtual.c_str(),FILE_READ);
  if(!f) return false;
  uint32_t inicioParagrafo=0, cursor=ocorrencia;
  uint8_t bloco[256];
  bool achou=false;
  while(cursor>0 && !achou){
    uint32_t base=cursor>sizeof(bloco)?cursor-sizeof(bloco):0;
    int n=(int)(cursor-base);
    if(!f.seek(base) || f.read(bloco,n)!=n){f.close(); return false;}
    for(int i=n-1;i>=0;i--){
      if(bloco[i]=='\n'){inicioParagrafo=base+i+1; achou=true; break;}
    }
    cursor=base;
    yield();
  }
  const int CONTEXTO=LEITOR_LINHAS_VISIVEIS/2;
  uint32_t recentes[CONTEXTO+1];
  int total=0, slot=0;
  uint32_t atual=inicioParagrafo;
  while(true){
    recentes[slot]=atual;
    slot=(slot+1)%(CONTEXTO+1);
    if(total<CONTEXTO+1) total++;
    uint32_t seguinte=atual;
    avancarUmaLinhaVisual(f,atual,seguinte);
    if(seguinte<=atual){f.close(); return false;}
    if(seguinte>ocorrencia) break;
    atual=seguinte;
    yield();
  }
  f.close();
  int primeiro=total==CONTEXTO+1?slot:0;
  reiniciarIndice(recentes[primeiro]);
  // Limites naturais produzidos pelo mesmo word-wrap do leitor.
  for(int i=1;i<total;i++) offsetsLinhas[i]=recentes[(primeiro+i)%(CONTEXTO+1)];
  linhasIndexadas=total;
  linhaTopo=total-1;
  while(linhaTopo<CONTEXTO && offsetsLinhas[0]>0){
    if(indexarAntesDaJanela()==0) break;
  }
  linhaTopo=max(0,linhaTopo-CONTEXTO);
  cacheLeitorValido=false;
  cacheLeitorTopo=-1;
  return true;
}

void invalidarBuscaTextoPorEdicao()
{
  limparDestaqueTexto();
  offsetUltimoTexto=0;
  offsetFinalTexto=0;
  inicioProximoTexto=0;
  totalHistoricoTexto=0;
  indiceHistoricoTexto=0;
  temResultadoTexto=false;
  consultaTextoEditada=true;
  statusBuscaTexto="Digite palavra ou frase";
}

void inserirConsultaTexto(char c)
{
  int tamanho=strlen(consultaTexto);
  if(tamanho>=MAX_CONSULTA_TEXTO){
    statusBuscaTexto="LIMITE: 80 CARACTERES";
    return;
  }
  if(cursorBuscaTexto<0) cursorBuscaTexto=0;
  if(cursorBuscaTexto>tamanho) cursorBuscaTexto=tamanho;
  memmove(consultaTexto+cursorBuscaTexto+1,consultaTexto+cursorBuscaTexto,
          tamanho-cursorBuscaTexto+1); // Inclui o terminador NUL.
  consultaTexto[cursorBuscaTexto++]=c;
  invalidarBuscaTextoPorEdicao();
}

void apagarAntesCursorBuscaTexto()
{
  int tamanho=strlen(consultaTexto);
  if(cursorBuscaTexto<=0 || tamanho<=0) return;
  if(cursorBuscaTexto>tamanho) cursorBuscaTexto=tamanho;
  memmove(consultaTexto+cursorBuscaTexto-1,consultaTexto+cursorBuscaTexto,
          tamanho-cursorBuscaTexto+1);
  cursorBuscaTexto--;
  invalidarBuscaTextoPorEdicao();
  if(telaAtual==TELA_BUSCA_TEXTO) desenharCampoBuscaTexto();
}

void posicionarCursorBuscaTexto(int x, int y)
{
  int tamanho=strlen(consultaTexto);
  int linha=(y>=36)?1:0;
  int inicio=linha*50;
  if(inicio>tamanho){
    cursorBuscaTexto=tamanho;
  }else{
    int fim=min(tamanho,inicio+50);
    // Soma meia celula para escolher o ponto de insercao mais proximo.
    int coluna=(x-8+3)/6;
    if(coluna<0) coluna=0;
    if(coluna>fim-inicio) coluna=fim-inicio;
    cursorBuscaTexto=inicio+coluna;
  }
  desenharCampoBuscaTexto();
}

bool apresentarResultadoTexto(uint32_t inicio, uint32_t fim)
{
  offsetUltimoTexto=inicio;
  offsetFinalTexto=fim;
  temResultadoTexto=true;
  statusBuscaTexto="ENTER: proxima ocorrencia";
  destaqueTextoAtivo=posicionarResultadoTexto(inicio);
  if(!destaqueTextoAtivo){
    statusBuscaTexto="ERRO AO POSICIONAR TEXTO";
    if(telaAtual==TELA_LEITOR) desenharViewportLeitor();
    mostrarStatusBuscaTexto();
    return false;
  }
  fecharBuscaTexto();
  return true;
}

void adicionarHistoricoTexto(uint32_t inicio, uint32_t fim)
{
  if(totalHistoricoTexto>=MAX_HISTORICO_TEXTO){
    memmove(historicoInicioTexto,historicoInicioTexto+1,
            (MAX_HISTORICO_TEXTO-1)*sizeof(historicoInicioTexto[0]));
    memmove(historicoFimTexto,historicoFimTexto+1,
            (MAX_HISTORICO_TEXTO-1)*sizeof(historicoFimTexto[0]));
    totalHistoricoTexto=MAX_HISTORICO_TEXTO-1;
  }
  historicoInicioTexto[totalHistoricoTexto]=inicio;
  historicoFimTexto[totalHistoricoTexto]=fim;
  indiceHistoricoTexto=totalHistoricoTexto;
  totalHistoricoTexto++;
}

void ocorrenciaAnteriorTexto()
{
  if(buscaAtiva!=BUSCA_TEXTO || telaAtual!=TELA_LEITOR) return;
  if(totalHistoricoTexto==0 || indiceHistoricoTexto==0){
    statusBuscaTexto="SEM OCORRENCIA ANTERIOR";
    mostrarStatusBuscaTexto();
    return;
  }
  indiceHistoricoTexto--;
  apresentarResultadoTexto(historicoInicioTexto[indiceHistoricoTexto],
                           historicoFimTexto[indiceHistoricoTexto]);
}

void executarBuscaTexto()
{
  if(buscaAtiva!=BUSCA_TEXTO) return;
  int tamanho=strlen(consultaTexto);
  bool temLetra=false;
  for(int i=0;i<tamanho;i++) if(consultaTexto[i]!=' ') temLetra=true;
  if(!temLetra){statusBuscaTexto="Digite palavra ou frase"; mostrarStatusBuscaTexto(); return;}
  if(consultaTextoEditada || strcmp(consultaTexto,ultimaConsultaTexto)!=0){
    limparDestaqueTexto();
    strcpy(ultimaConsultaTexto,consultaTexto);
    offsetUltimoTexto=0;
    offsetFinalTexto=0;
    inicioProximoTexto=0;
    totalHistoricoTexto=0;
    indiceHistoricoTexto=0;
    temResultadoTexto=false;
    consultaTextoEditada=false;
  }
  // Depois de BACK, ENTER percorre primeiro os resultados ja conhecidos.
  if(totalHistoricoTexto>0 && indiceHistoricoTexto+1<totalHistoricoTexto){
    indiceHistoricoTexto++;
    apresentarResultadoTexto(historicoInicioTexto[indiceHistoricoTexto],
                             historicoFimTexto[indiceHistoricoTexto]);
    return;
  }
  statusBuscaTexto="BUSCANDO...";
  mostrarStatusBuscaTexto();
  uint32_t encontrado=0, depois=0;
  int resultado=localizarTextoEmBlocos(ultimaConsultaTexto,inicioProximoTexto,encontrado,depois);
  if(resultado==1){
    inicioProximoTexto=depois;
    adicionarHistoricoTexto(encontrado,depois-1);
    apresentarResultadoTexto(encontrado,depois-1);
  }else{
    statusBuscaTexto=resultado<0 ? "ERRO AO LER TXT" :
                     (temResultadoTexto ? "SEM OUTRA OCORRENCIA" : "TEXTO NAO ENCONTRADO");
    mostrarStatusBuscaTexto(); // Nao altera o byte atual do leitor.
  }
}

void processarTeclaTexto(int x, int y)
{
  if(y>=19 && y<62){
    posicionarCursorBuscaTexto(x,y);
    return;
  }
  char inserir=0;
  const char *linhas[]={"QWERTYUIOP","ASDFGHJKL","ZXCVBNM"};
  for(int l=0;l<3;l++){
    int total=strlen(linhas[l]), x0=(320-total*32)/2;
    if(y>=86+l*36 && y<118+l*36 && x>=x0 && x<x0+total*32){
      int col=(x-x0)/32;
      inserir=(char)(linhas[l][col]+32);
    }
  }
  if(y>=202 && y<234){
    if(x<80) inserir=' ';
    else if(x<160){
      apagarAntesCursorBuscaTexto();
      return;
    }else if(x<240){solicitarBuscaTexto(); return;}
    else {fecharBuscaTexto(); return;}
  }
  if(inserir){
    inserirConsultaTexto(inserir);
    desenharCampoBuscaTexto();
  }
}

// =====================================================
// TOUCH COM ARRASTO
// =====================================================
// Gancho para uma futura etapa de potencia GPIO/MOSFET.
// Nesta montagem o backlight esta no 3V3: nao tocar em nenhum GPIO.
void aplicarBacklight(bool ligado)
{
  (void)ligado;
}

void definirDisplayLigado(bool ligado)
{
  // DISPOFF preserva RAM/configuracao do ILI9341. Nao usamos SLPIN,
  // portanto DISPON basta e nao ha espera de SLPOUT no loop.
  tft.sendCommand(ligado ? ILI9341_DISPON : ILI9341_DISPOFF);
  aplicarBacklight(ligado);
}

void redesenharTelaAtual()
{
  switch(telaAtual){
    case TELA_PASTAS: desenharTelaPastas(); break;
    case TELA_LEITOR: desenharTelaLeitor(); break;
    case TELA_BUSCA_TEXTO: desenharTelaBuscaTexto(); break;
    case TELA_SPLASH: desenharSplashLexMachina(); break;
    case TELA_RELACOES: desenharTelaRelacoes(); break;
    case TELA_JURIS_CATEGORIAS: desenharTelaCategoriasJuris(); break;
    case TELA_REFERENCIAS: desenharTelaReferenciasProvisoria(); break;
  }
}

void atualizarInatividadeDisplay()
{
  // Comandos SPI e desenho somente no loop, nunca nos callbacks HID.
  if(pedirAcordarDisplay){
    definirDisplayLigado(true);
    redesenharTelaAtual();
    displayApagado=false;
    pedirAcordarDisplay=false;
  }else if(!displayApagado &&
           (uint32_t)((uint32_t)millis()-ultimaInteracaoMs)>=TIMEOUT_TELA_MS){
    displayApagado=true;
    definirDisplayLigado(false);
  }
}

void processarTouch()
{
  int rx,ry;
  bool tocando=lerTouchRaw(rx,ry);
  if(tocando && registrarAtividadeUsuario()) ignorarTouchAteSoltar=true;
  if(ignorarTouchAteSoltar){
    // Consome o gesto inteiro, inclusive a soltura que normalmente abre itens.
    touchAtivo=false;
    touchAnterior=false;
    touchConsumido=true;
    acumuladorTouch=0;
    itemTouch=-1;
    if(!tocando) ignorarTouchAteSoltar=false;
    return;
  }
  int x=0,y=0;
  if(tocando) converterTouch(rx,ry,x,y);
  if(tocando && !touchAtivo){
    touchAtivo=true;
    ultimoTouchY=y;
    inicioTouchX=x;
    inicioTouchY=y;
    acumuladorTouch=0;
    touchArrastou=false;
    touchConsumido=false;
    itemTouch=-1;
    if(telaAtual==TELA_SPLASH){
      pedirFecharSplash=true;
      touchConsumido=true; // Consome todo o toque que fecha a splash.
    }else if(telaAtual==TELA_BUSCA_TEXTO){
      touchConsumido=true; // Uma tecla por contato, ate soltar o dedo.
      processarTeclaTexto(x,y);
    }else if(telaAtual==TELA_LEITOR && x>=264 && y<=20){
      touchConsumido=true;
      abrirBuscaTexto();
    }else if((telaAtual==TELA_LEITOR || telaAtual==TELA_PASTAS || telaAtual==TELA_RELACOES || telaAtual==TELA_JURIS_CATEGORIAS) && x<=71 && y<=25){
      pedirVoltar=true;
      touchConsumido=true;
    }else if(telaAtual==TELA_LEITOR && y>=220 && menuRelacoesAtivo && !modoDigitacaoArtigo){
      if(x>=4 && x<104 && totalCorrelatasArtigo>0) pedirCategoriaRelacao=REL_CORRELATAS;
      else if(x>=110 && x<210 && totalCategoriasJuris>0) pedirCategoriaRelacao=255;
      touchConsumido=true;
    }else if(telaAtual==TELA_JURIS_CATEGORIAS && y>=43 && y<43+6*28){
      int idx=(y-43)/28;
      if(idx>=0 && idx<totalCategoriasJuris){
        int velho=categoriaJurisSelecionada;
        categoriaJurisSelecionada=idx;
        itemTouch=idx;
        desenharLinhaCategoriaJuris(velho);
        desenharLinhaCategoriaJuris(idx);
      }
    }else if(telaAtual==TELA_RELACOES && y>=43 && y<43+RELACOES_VISIVEIS*28){
      int idx=primeiraRelacaoVisivel+(y-43)/28;
      if(idx>=0 && idx<totalRelacoesCategoria){
        itemTouch=idx;
        int velho=relacaoSelecionada;
        relacaoSelecionada=idx;
        desenharLinhaRelacao(velho-primeiraRelacaoVisivel);
        desenharLinhaRelacao(idx-primeiraRelacaoVisivel);
      }
    }else if(telaAtual==TELA_PASTAS && y>=PASTA_Y0 && y<PASTA_Y0+PASTAS_VISIVEIS*PASTA_H){
      int idx=primeiraPastaVisivel+(y-PASTA_Y0)/PASTA_H;
      if(idx>=0 && idx<totalPastas){
        itemTouch=idx;
        int velho=pastaSelecionada;
        pastaSelecionada=idx;
        desenharLinhaPasta(velho-primeiraPastaVisivel);
        desenharLinhaPasta(idx-primeiraPastaVisivel);
      }
    }
  }
  if(tocando && touchAtivo && !touchConsumido){
    int dy=y-ultimoTouchY;
    ultimoTouchY=y;
    acumuladorTouch+=dy;
    if(abs(y-inicioTouchY)>=10 || abs(x-inicioTouchX)>=10) touchArrastou=true;
    // Mantem os passos de arrasto de 10 px do firmware original.
    while(acumuladorTouch<=-10){
      if(telaAtual==TELA_LEITOR) deltaLeitor++;
      else if(telaAtual==TELA_PASTAS) deltaPastas++;
      else if(telaAtual==TELA_RELACOES) deltaRelacoes++;
      else if(telaAtual==TELA_JURIS_CATEGORIAS) deltaRelacoes++;
      acumuladorTouch+=10;
    }
    while(acumuladorTouch>=10){
      if(telaAtual==TELA_LEITOR) deltaLeitor--;
      else if(telaAtual==TELA_PASTAS) deltaPastas--;
      else if(telaAtual==TELA_RELACOES) deltaRelacoes--;
      else if(telaAtual==TELA_JURIS_CATEGORIAS) deltaRelacoes--;
      acumuladorTouch-=10;
    }
  }
  if(!tocando && touchAtivo){
    // Toque curto abre ao soltar; arrastar nao abre itens acidentalmente.
    if(!touchConsumido && !touchArrastou){
      if(telaAtual==TELA_PASTAS && itemTouch>=0 && itemTouch==pastaSelecionada)
        pedirAbrir=true;
      else if(telaAtual==TELA_RELACOES && itemTouch>=0 && itemTouch==relacaoSelecionada)
        pedirAbrirRelacao=true;
      else if(telaAtual==TELA_JURIS_CATEGORIAS && itemTouch>=0 && itemTouch==categoriaJurisSelecionada)
        pedirCategoriaRelacao=(uint8_t)categoriasJurisDisponiveis[categoriaJurisSelecionada];
    }
    touchAtivo=false;
    acumuladorTouch=0;
    itemTouch=-1;
  }
  touchAnterior=tocando;
}

// =====================================================
// BLUETOOTH
// =====================================================
void iniciarBluetooth()
{
  Serial.println("Inicializando BLE...");
  auto &keyboard=ble.hidHost();

  keyboard.onDiscovered([](const EspBleHidKeyboardHostDiscovery &result){
    if(!result.success){
      Serial.print("Falha HID: "); Serial.println(result.detail.c_str()); return;
    }
    tecladoConectado=true;
    Serial.println("TECLADO HID PRONTO!");
  });

  keyboard.setKeyboardLayout(EspBleKeyboardLayout::EnUs);

  keyboard.onKeyboard([](const EspBleHidKeyboardEvent &event){
#if DIAGNOSTICO_HID
    Serial.printf("[HID KEY] page=0x0007 usage=0x%02X modifier=0x%02X pressed=%u released=%u\n",
                  (unsigned)event.usage,(unsigned)event.modifiers,
                  (unsigned)event.pressed,(unsigned)event.released);
#endif
    if(!event.pressed){
      if(event.usage==enterTextoPressionado) enterTextoPressionado=0;
      if(event.usage==backTextoPressionado) backTextoPressionado=0;
      if(event.usage==enterSplashPressionado) enterSplashPressionado=0;
      if(event.usage==teclaDespertar) teclaDespertar=0;
      return;
    }
    bool consumida=registrarAtividadeUsuario();
    if(consumida){teclaDespertar=event.usage; return;}
    if(teclaDespertar!=0 && event.usage==teclaDespertar) return;
    // Nao deixe repeticoes da mesma pressao executar outra acao apos o resultado.
    if(enterTextoPressionado!=0 && event.usage==enterTextoPressionado) return;
    if(backTextoPressionado!=0 && event.usage==backTextoPressionado) return;
    if(enterSplashPressionado!=0 && event.usage==enterSplashPressionado) return;
    if(telaAtual==TELA_SPLASH){
      if(ehEnterFisico(event.usage)){
        enterSplashPressionado=event.usage;
        pedirFecharSplash=true;
      }
      return; // Na splash manual, somente ENTER executa uma acao.
    }
    if(buscaAtiva==BUSCA_TEXTO &&
       (telaAtual==TELA_BUSCA_TEXTO || telaAtual==TELA_LEITOR) && event.usage==0x2A){
      backTextoPressionado=event.usage;
      pedirBackTexto=true;
      return;
    }
    if(buscaAtiva==BUSCA_TEXTO &&
       (telaAtual==TELA_BUSCA_TEXTO || telaAtual==TELA_LEITOR) && ehEnterFisico(event.usage)){
      enterTextoPressionado=event.usage;
      solicitarBuscaTexto();
      return;
    }

    // ESC retorna um nivel no navegador ou no leitor.
    if(event.usage==0x29){
      pedirVoltar=true;
      return;
    }

    if(telaAtual==TELA_PASTAS){
      if(event.usage==0x2A){
        backTextoPressionado=event.usage;
        pedirVoltar=true;
        return;
      }
      if(event.usage==0x52){deltaPastas--; return;}
      if(event.usage==0x51){deltaPastas++; return;}
      if(event.usage==0x4B){deltaPastas-=PASTAS_VISIVEIS; return;}
      if(event.usage==0x4E){deltaPastas+=PASTAS_VISIVEIS; return;}
      if(event.usage==0x28){pedirAbrir=true; return;}
      return;
    }

    if(telaAtual==TELA_RELACOES){
      if(event.usage==0x2A){ pedirVoltar=true; return; }
      if(event.usage==0x52){deltaRelacoes--; return;}
      if(event.usage==0x51){deltaRelacoes++; return;}
      if(event.usage==0x4B){deltaRelacoes-=RELACOES_VISIVEIS; return;}
      if(event.usage==0x4E){deltaRelacoes+=RELACOES_VISIVEIS; return;}
      if(event.usage==0x28){pedirAbrirRelacao=true; return;}
      if(event.ascii>='1' && event.ascii<='9'){
        int alvo=(int)(event.ascii-'1');
        if(alvo<totalRelacoesCategoria){
          relacaoSelecionada=alvo;
          pedirAbrirRelacao=true;
        }
        return;
      }
      return;
    }

    if(telaAtual==TELA_JURIS_CATEGORIAS){
      if(event.usage==0x2A){pedirVoltar=true; return;}
      if(event.usage==0x52){deltaRelacoes--; return;}
      if(event.usage==0x51){deltaRelacoes++; return;}
      if(event.usage==0x28 && totalCategoriasJuris>0){
        pedirCategoriaRelacao=(uint8_t)categoriasJurisDisponiveis[categoriaJurisSelecionada];
        return;
      }
      return;
    }

    if(telaAtual==TELA_LEITOR){
      if(visualizandoReferencia){
        if(event.usage==0x2A){pedirVoltar=true; return;}
        if(event.usage==0x52){deltaLeitor--; return;}
        if(event.usage==0x51){deltaLeitor++; return;}
        if(event.usage==0x4B){deltaLeitor-=LEITOR_LINHAS_VISIVEIS/2; return;}
        if(event.usage==0x4E){deltaLeitor+=LEITOR_LINHAS_VISIVEIS/2; return;}
        return;
      }

      if(event.ascii>='0' && event.ascii<='9'){
        // Depois de uma busca bem-sucedida, o rodape entra em modo de atalhos.
        // 0 continua sendo o atalho oculto para "novo artigo"; 1, 2 e 3 abrem as categorias exibidas.
        if(menuRelacoesAtivo && !modoDigitacaoArtigo){
          if(event.ascii=='0'){
            artigoDigitado="";
            buscaAtiva=BUSCA_ARTIGO;
            numeroBuscaEditado=true;
            modoDigitacaoArtigo=true;
            menuRelacoesAtivo=false;
            pedirRedesenharBusca=true;
            return;
          }
          if(event.ascii=='1' && totalCorrelatasArtigo>0){
            pedirCategoriaRelacao=REL_CORRELATAS;
            return;
          }
          if(event.ascii=='2' && totalCategoriasJuris>0){
            pedirCategoriaRelacao=255;
            return;
          }
          // 4..9 iniciam diretamente uma nova busca; para artigos iniciados em
          // 1, 2 ou 3, use 0 ART antes, evitando ambiguidade com os atalhos.
          if(event.ascii>='4' && event.ascii<='9'){
            artigoDigitado=""; artigoDigitado+=(char)event.ascii;
            buscaAtiva=BUSCA_ARTIGO;
            numeroBuscaEditado=true;
            modoDigitacaoArtigo=true;
            menuRelacoesAtivo=false;
            pedirRedesenharBusca=true;
          }
          return;
        }

        if(buscaAtiva!=BUSCA_ARTIGO){
          // Nova entrada numerica nao deve concatenar um artigo antigo oculto.
          artigoDigitado="";
          numeroBuscaEditado=true;
        }
        buscaAtiva=BUSCA_ARTIGO;
        pedirBuscaTexto=false;
        if(artigoDigitado.length()<8){
          artigoDigitado+=(char)event.ascii;
          numeroBuscaEditado=true;
          pedirRedesenharBusca=true;
        }
        return;
      }

      if(event.usage==0x2A){
        if(artigoDigitado.length()>0){
          artigoDigitado.remove(artigoDigitado.length()-1);
          numeroBuscaEditado=true;
          pedirRedesenharBusca=true;
        }
        return;
      }

      if(event.usage==0x28){
        if(artigoDigitado.length()>0) pedirBuscar=true;
        return;
      }

      if(event.usage==0x52){deltaLeitor--; return;}
      if(event.usage==0x51){deltaLeitor++; return;}
      if(event.usage==0x4B){deltaLeitor-=LEITOR_LINHAS_VISIVEIS/2; return;}
      if(event.usage==0x4E){deltaLeitor+=LEITOR_LINHAS_VISIVEIS/2; return;}
    }
  });

  // Controles especiais podem usar outra usage page, em vez de tecla comum.
  // Apenas diagnostico: nenhum codigo foi escolhido para o atalho TEXTO.
#if DIAGNOSTICO_HID
  keyboard.onConsumerControl([](const EspBleHidConsumerControlEvent &event){
    Serial.printf("[HID CONSUMER] page=0x000C usage=0x%04X modifier=N/A pressed=%u released=%u\n",
                  (unsigned)event.usage,(unsigned)event.pressed,(unsigned)event.released);
    if(event.pressed) registrarAtividadeUsuario();
  });
  keyboard.onSystemControl([](const EspBleHidSystemControlEvent &event){
    Serial.printf("[HID SYSTEM] page=0x0001 usage=0x%02X modifier=N/A pressed=%u released=%u\n",
                  (unsigned)event.usage,(unsigned)event.pressed,(unsigned)event.released);
    if(event.pressed) registrarAtividadeUsuario();
  });
#endif

  keyboard.onMouse([](const EspBleHidMouseEvent &event){
#if DIAGNOSTICO_HID
    if(event.buttons!=event.previousButtons){
      Serial.printf("[HID MOUSE] page=0x0009 modifier=N/A pressedMask=0x%02X releasedMask=0x%02X\n",
                    (unsigned)(event.buttons & ~event.previousButtons),
                    (unsigned)(event.previousButtons & ~event.buttons));
    }
#endif
    if(event.wheel==0) return;
    if(registrarAtividadeUsuario()) return;
    int d=(event.wheel>0)?-1:1;
    if(telaAtual==TELA_PASTAS) deltaPastas += (d<0?-1:1);
    else if(telaAtual==TELA_LEITOR) deltaLeitor += d;
    else if(telaAtual==TELA_RELACOES) deltaRelacoes += d;
    else if(telaAtual==TELA_JURIS_CATEGORIAS) deltaRelacoes += d;
  });

  EspBleConfig config;
  config.deviceName="Lex Machina";
  config.security.enabled=true;
  config.security.bonding=true;

  if(!ble.begin(config)){
    Serial.print("Erro BLE: "); Serial.println(ble.lastErrorDetail().c_str()); return;
  }

  ble.onConnected([](const EspBleConnection &connection){
    keyboardConnectionId=connection.id;
    Serial.println("MINI-KEYBOARD CONECTADO");
  });

  ble.onSecurityChanged([](const EspBleSecurityChanged &event){
    if(event.success) ble.hidHost().discover(event.connection.id);
  });

  ble.onDisconnected([](const EspBleConnection &){
    keyboardConnectionId=0;
    tecladoConectado=false;
    teclaDespertar=0;
    enterTextoPressionado=0;
    backTextoPressionado=0;
    enterSplashPressionado=0;
    ble.scanner().start();
  });

  ble.scanner().onResult([](const EspBleScanResult &result){
    if(!result.connectable) return;
    if(!result.advertisesService("1812")) return;
    if(result.name!=NOME_TECLADO) return;
    ble.scanner().stop();
    ble.connect(result);
  });

  ble.scanner().start();
}

// =====================================================
// SETUP
// =====================================================
void setup()
{
  Serial.begin(115200);
  delay(800);

  Serial.println();
  Serial.println("================================");
  int falhasContexto=validarRotinaContextoJuridico();
  Serial.print("TESTE CONTEXTO JURIDICO: ");
  if(falhasContexto==0) Serial.println("OK");
  else { Serial.print(falhasContexto); Serial.println(" FALHA(S)"); }
  Serial.println("LEX MACHINA V7.12.0 JURIS CF EXPANDIDA");
  Serial.print("Motivo do reset: ");
  Serial.println((int)esp_reset_reason());
  Serial.print("Heap ao iniciar: ");
  Serial.println(ESP.getFreeHeap());
  Serial.println("================================");

  pinMode(TFT_CS,OUTPUT);
  pinMode(SD_CS,OUTPUT);
  digitalWrite(TFT_CS,HIGH);
  digitalWrite(SD_CS,HIGH);

  pinMode(TOUCH_RST,OUTPUT);
  pinMode(TOUCH_INT,INPUT_PULLUP);
  digitalWrite(TOUCH_RST,LOW); delay(50);
  digitalWrite(TOUCH_RST,HIGH); delay(250);

  Wire.begin(TOUCH_SDA,TOUCH_SCL);
  Wire.setClock(100000);

  spiBus.begin(TFT_SCK,TFT_MISO,TFT_MOSI,-1);

  tft.begin(40000000);
  tft.setRotation(3);

#if PAINEL_PRECISA_INVON
  tft.invertDisplay(true);
#else
  tft.invertDisplay(false);
#endif
  delay(30);

  desenharTransicaoSplash(true);
  delay(3500);

  iniciarSDUmaVez();
  carregarPastas("/");
  telaAtual=TELA_PASTAS;
  desenharTransicaoSplash(false);

  Serial.print("Heap antes do BLE: ");
  Serial.println(ESP.getFreeHeap());
  iniciarBluetooth();
  Serial.print("Heap depois do BLE: ");
  Serial.println(ESP.getFreeHeap());
  inicializarCachesGrandes();
  carregarCacheJurisCF();
#if LEX_DEVICE_V1_ENABLED
  lexV1DiagnosticoBoot();
#endif
  ultimaInteracaoMs=(uint32_t)millis();
}

#if LEX_DEVICE_V1_ENABLED
// ---------------- DEVICE V1: adaptador, controle de handles e diagnostico ----------------
// Politica (FILE_DESCRIPTOR_POLICY.md): SD montado com LEXV1_SD_MAX_FILES; DEVICE V1 mantem no maximo LEXV1_FD_STEADY_MAX
// arquivos abertos em regime (TARGETS, ENTENDA_LOOKUP, REF_LOOKUP) e no maximo LEXV1_FD_PEAK_MAX no diagnostico. LEXV1.VER,
// CF88_RUNTIME e hashes: abre -> le -> fecha. Payloads (ENTENDA/REF): abertos so quando ha bloco a ler e fechados ao fim da
// consulta. Todo arquivo e aberto com FILE_READ; toda falha de abertura imprime FAIL_IO|tipo|caminho|stage|open|max_open.
static int lexV1FdOpen=0, lexV1FdMax=0;

struct LexV1FileReader : LexV1Reader {
  File f;
  const char *tipo="", *caminho="", *etapa="";
  bool sobDemanda=false, tentou=false, falhaIo=false;
  bool abrir(const char *t,const char *c,const char *e){
    tipo=t; caminho=c; etapa=e; tentou=true;
    f=SD.open(c,FILE_READ);
    if(!f){
      falhaIo=true;
      Serial.printf("LEXV1: FAIL_IO|%s|%s|stage=%s|open=%d|max_open=%d\n",t,c,e,lexV1FdOpen,lexV1FdMax);
      return false;
    }
    lexV1FdOpen++; if(lexV1FdOpen>lexV1FdMax) lexV1FdMax=lexV1FdOpen;
    Serial.printf("LEXV1: OPEN %s %s stage=%s OPEN_COUNT=%d MAX_OPEN_COUNT=%d\n",t,c,e,lexV1FdOpen,lexV1FdMax);
    return true;
  }
  // Payload: nada e aberto ate a 1a leitura (lookup sem linha -> arquivo nunca aberto).
  void preparar(const char *t,const char *c,const char *e){ tipo=t; caminho=c; etapa=e; sobDemanda=true; tentou=false; }
  bool garantir(){ if(f) return true; if(!sobDemanda || tentou) return false; return abrir(tipo,caminho,etapa); }
  void fechar(){
    if(f){ f.close(); lexV1FdOpen--; Serial.printf("LEXV1: CLOSE %s OPEN_COUNT=%d\n",caminho,lexV1FdOpen); }
    tentou=false;
  }
  bool seek(uint32_t pos) override { return garantir() && f.seek(pos); }
  int read(uint8_t *buf,int n) override { return garantir() ? f.read(buf,n) : -1; }
  uint32_t size() override { return garantir() ? (uint32_t)f.size() : 0; }
  uint32_t position() override { return f ? (uint32_t)f.position() : 0; }
  ~LexV1FileReader(){ fechar(); }
};

// sha256 (hex minusculo) do arquivo inteiro, em blocos de 1 KB: abre -> le -> fecha. Somente leitura.
bool lexV1Sha256Arquivo(const char *tipo, const char *caminho, const char *etapa, uint32_t &bytes, char hex[65])
{
  LexV1FileReader r;
  if(!r.abrir(tipo,caminho,etapa)) return false;
  bytes=r.size();
  mbedtls_sha256_context ctx;
  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts(&ctx,0);
  uint8_t buf[1024];
  int n;
  while((n=r.read(buf,sizeof(buf)))>0) mbedtls_sha256_update(&ctx,buf,(size_t)n);
  r.fechar();
  uint8_t out[32];
  mbedtls_sha256_finish(&ctx,out);
  mbedtls_sha256_free(&ctx);
  for(int i=0;i<32;i++) snprintf(hex+2*i,3,"%02x",out[i]);
  hex[64]='\0';
  return true;
}

// Leitor em memoria (autoteste do parser de LEXV1.VER no proprio ESP32; nenhum acesso ao SD).
struct LexV1MemReader : LexV1Reader {
  const char *s; uint32_t n, p;
  explicit LexV1MemReader(const char *txt) : s(txt), n((uint32_t)strlen(txt)), p(0) {}
  bool seek(uint32_t pos) override { if(pos>n) return false; p=pos; return true; }
  int read(uint8_t *buf,int k) override { int m=0; while(m<k && p<n) buf[m++]=(uint8_t)s[p++]; return m; }
  uint32_t size() override { return n; }
  uint32_t position() override { return p; }
};

static void lexV1Mem(const char *etapa)
{
  Serial.printf("LEXV1: MEM %s heap_livre=%lu heap_min=%lu heap_maior_bloco=%lu psram_total=%lu psram_livre=%lu psram_min=%lu\n",etapa,
                (unsigned long)ESP.getFreeHeap(),(unsigned long)ESP.getMinFreeHeap(),(unsigned long)ESP.getMaxAllocHeap(),
                (unsigned long)ESP.getPsramSize(),(unsigned long)ESP.getFreePsram(),(unsigned long)ESP.getMinFreePsram());
}

// Categorias de falha: FAIL_SCHEMA, FAIL_HASH, FAIL_IO, FAIL_PARSE, FAIL_TARGET, FAIL_REFERENCE (a categoria so e impressa se falhar).
static uint16_t lexV1Pass=0, lexV1Fail=0;
static void lexV1Check(bool ok,const char *categoria,const char *nome,const char *detalhe)
{
  if(ok) lexV1Pass++; else lexV1Fail++;
  Serial.printf("LEXV1: CHECK %s%s%s %s %s\n",ok?"PASS":"FAIL",ok?"":" ",ok?"":categoria,nome,detalhe?detalhe:"");
}

// Offset (inicio de linha) da 1a ocorrencia de "\n<b>" depois da 1a ocorrencia de "\n<a>" no texto exibido. So rotulos
// estruturais ("Art. 114." / "VIII - "), nenhum conteudo editorial. Abre -> leitura sequencial em blocos de 512 B -> fecha.
static bool lexV1OffsetEstrutural(const char *caminho,const char *a,const char *b,uint32_t &offset,bool &falhaIo)
{
  LexV1FileReader r;
  falhaIo=false;
  if(!r.abrir("CF88_RUNTIME",caminho,"text_position")){ falhaIo=true; return false; }
  const char *pad[2]={a,b};
  int fase=0; size_t k=0; uint32_t pos=0; uint8_t buf[512]; int n;
  bool achou=false;
  while(!achou && (n=r.read(buf,sizeof(buf)))>0){
    for(int i=0;i<n && !achou;i++,pos++){
      const char *p=pad[fase];
      char c=(char)buf[i];
      if(k==0){ if(c=='\n') k=1; continue; }
      if(c==p[k-1]){ k++; if(p[k-1]=='\0'){ if(fase==0){ fase=1; k=0; } else { offset=pos+1-(uint32_t)strlen(p); achou=true; } } }
      else k=(c=='\n')?1:0;
    }
  }
  r.fechar();
  return achou;
}

struct LexV1Caso {
  const char *tid;
  bool existe;
  LexV1Resolution res;
  const char *ancora;          // "" = sem ENTENDA
  uint16_t refs, visiveis;
};

void lexV1DiagnosticoBoot()
{
  lexV1Pass=lexV1Fail=0;
  lexV1FdOpen=lexV1FdMax=0;
  char det[192];
  Serial.printf("LEXV1: diagnostico A3B (somente leitura) schema_esperado=%d sd_max_files=%d fd_steady_max=%d fd_peak_max=%d\n",
                LEX_DEVICE_SCHEMA_VERSION,LEXV1_SD_MAX_FILES,LEXV1_FD_STEADY_MAX,LEXV1_FD_PEAK_MAX);
  lexV1Mem("antes_device_v1");

  // 0) autoteste do parser de versao (memoria)
  {
    const char *v2="#LEXMACHINA|DEVICE_VERSION|2\nBUILD_ID|x\nENTENDA_COUNT|1\n";
    const char *v3="#LEXMACHINA|DEVICE_VERSION|3\nBUILD_ID|x\nENTENDA_COUNT|1\n";
    const char *v4="#LEXMACHINA|DEVICE_VERSION|4\nBUILD_ID|x\nENTENDA_COUNT|1\n";
    const char *v30="#LEXMACHINA|DEVICE_VERSION|30\nBUILD_ID|x\nENTENDA_COUNT|1\n";
    const char *v3x="#LEXMACHINA|DEVICE_VERSION|3|X\nBUILD_ID|x\nENTENDA_COUNT|1\n";
    LexV1Version t;
    LexV1MemReader r2(v2), r3(v3), r4(v4), r30(v30), r3x(v3x);
    lexV1Check(lexv1ReadVersion(&r2,t)==LEXV1_FAIL_VERSION,"FAIL_SCHEMA","schema_2_rejeitado",nullptr);
    lexV1Check(lexv1ReadVersion(&r3,t)==LEXV1_OK && t.schemaVersion==3,"FAIL_SCHEMA","schema_3_aceito",nullptr);
    lexV1Check(lexv1ReadVersion(&r4,t)==LEXV1_FAIL_VERSION,"FAIL_SCHEMA","schema_4_rejeitado",nullptr);
    lexV1Check(lexv1ReadVersion(&r30,t)==LEXV1_FAIL_VERSION && lexv1ReadVersion(&r3x,t)==LEXV1_FAIL_VERSION,"FAIL_SCHEMA",
               "schema_30_e_3X_rejeitados",nullptr);
  }

  if(!sdOK){ Serial.println("LEXV1: SD indisponivel -> camadas V1 desativadas"); lexV1Check(false,"FAIL_IO","sd_montado",nullptr); return; }

  // 1) LEXV1.VER: abre -> le -> valida -> fecha
  LexV1Version v;
  LexV1Status sv;
  {
    LexV1FileReader ver;
    sv=ver.abrir("LEXV1_VER","/99_LEX_V1/00_SYS/LEXV1.VER","version")?lexv1ReadVersion(&ver,v):LEXV1_FAIL_IO;
    ver.fechar();
  }
  snprintf(det,sizeof(det),"status=%s lido=%d esperado=%d",lexv1StatusName(sv),v.schemaVersion,LEX_DEVICE_SCHEMA_VERSION);
  lexV1Check(sv==LEXV1_OK,sv==LEXV1_FAIL_IO?"FAIL_IO":"FAIL_SCHEMA","lexv1_ver_device_version",det);
  if(sv!=LEXV1_OK){ Serial.println("LEXV1: LEXV1.VER ausente/invalido -> camadas V1 desativadas (fail closed)"); return; }
  Serial.printf("LEXV1: build=%s commit=%s entenda=%u pilotos=%u runtime_cf=%s map=%s ref=%s\n",v.buildId,v.gitCommit,v.entendaCount,
                v.entendaPilots,v.runtimeCf,v.textMapRuntimeStatus,v.referenceEngine);
  const char *rtPath=v.runtimeCfPath[0]?v.runtimeCfPath:LEXV1_RUNTIME_CF_PATH;

  // 2) runtime exibido: abre -> sha256 em streaming -> fecha (antes de abrir qualquer indice)
  char sha[65]={0};
  uint32_t bytesTexto=0;
  uint32_t t0=micros();
  bool lido=lexV1Sha256Arquivo("CF88_RUNTIME",rtPath,"runtime_sha256",bytesTexto,sha);
  Serial.printf("LEXV1: TIME runtime_sha256_us=%lu\n",(unsigned long)(micros()-t0));
  Serial.printf("LEXV1: runtime esperado bytes=%lu sha256=%s\n",(unsigned long)v.runtimeCfBytes,v.runtimeCfSha256);
  Serial.printf("LEXV1: runtime lido     bytes=%lu sha256=%s (%s)\n",(unsigned long)bytesTexto,lido?sha:"-",lido?"OK":"FAIL_IO");
  bool runtimeOk=lido && bytesTexto==v.runtimeCfBytes && strcmp(sha,v.runtimeCfSha256)==0;
  Serial.printf("LEXV1: runtime hash %s\n",runtimeOk?"CONFERE":"DIVERGE -> resolucao por posicao desativada (fail closed)");
  lexV1Check(runtimeOk,lido?"FAIL_HASH":"FAIL_IO","RUNTIME_HASH_MATCH",nullptr);
  bool pinOk=v.runtimeCfBytes==LEXV1_PINNED_RUNTIME_BYTES && strcmp(v.runtimeCfSha256,LEXV1_PINNED_RUNTIME_SHA256)==0;
  Serial.printf("LEXV1: runtime do predeploy (compilado) bytes=%lu sha256=%s -> VER %s\n",LEXV1_PINNED_RUNTIME_BYTES,
                LEXV1_PINNED_RUNTIME_SHA256,pinOk?"IGUAL":"DIFERENTE (overlay de outro build)");
  lexV1Check(pinOk,"FAIL_HASH","pinned_runtime_vs_ver",nullptr);

  // 3) TEXT_MAP: sha256 do arquivo (abre -> le -> fecha), depois o indice so durante as consultas por posicao
  {
    char shaMap[65]={0}; uint32_t bytesMap=0;
    bool mapLido=lexV1Sha256Arquivo("TEXT_MAP","/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX","text_map_sha256",bytesMap,shaMap);
    lexV1Check(mapLido && !strcmp(shaMap,LEXV1_PINNED_TEXT_MAP_SHA256),mapLido?"FAIL_HASH":"FAIL_IO","text_map_sha256_pinned",shaMap);
  }
  uint32_t off114=0; bool falhaRt=false;
  bool achou=lexV1OffsetEstrutural(rtPath,"Art. 114.","VIII - ",off114,falhaRt);
  {
    LexV1FileReader map;
    LexV1Index textMap;
    LexV1Status s2=map.abrir("TEXT_MAP","/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX","text_map_index")?
                   lexv1OpenIndex(textMap,&map,"TEXT_MAP",LEXV1_TEXT_MAP_VERSION):LEXV1_FAIL_IO;
    lexV1Check(s2==LEXV1_OK,s2==LEXV1_FAIL_IO?"FAIL_IO":"FAIL_PARSE","text_map_idx",lexv1StatusName(s2));
    if(s2==LEXV1_OK){
      snprintf(det,sizeof(det),"status=%s source_bytes=%lu registros=%lu adct=%lu",textMap.runtimeStatus,(unsigned long)textMap.sourceBytes,
               (unsigned long)textMap.recordCount,(unsigned long)textMap.adctStart);
      lexV1Check(!strcmp(textMap.runtimeStatus,"RUNTIME") && textMap.sourceBytes==bytesTexto && !strcmp(textMap.sourceSha256,sha),
                 lido?"FAIL_HASH":"FAIL_IO","text_map_runtime_guard",det);
      char tid[LEXV1_KEY_MAX];
      LexV1Status g=lexv1TargetAtOffset(textMap,bytesTexto,"0000000000000000000000000000000000000000000000000000000000000000",
                                        textMap.adctStart,tid,sizeof(tid));
      lexV1Check(g==LEXV1_FAIL_SOURCE_MISMATCH && !tid[0],"FAIL_HASH","text_map_guard_sha_errado",lexv1StatusName(g));
      t0=micros();
      LexV1Status sm=achou?lexv1TargetAtOffset(textMap,bytesTexto,lido?sha:nullptr,off114,tid,sizeof(tid)):LEXV1_NOT_FOUND;
      uint32_t us=micros()-t0;
      snprintf(det,sizeof(det),"offset=%lu -> %s %s us=%lu",(unsigned long)off114,lexv1StatusName(sm),tid,(unsigned long)us);
      Serial.printf("LEXV1: TIME text_map_lookup_us=%lu\n",(unsigned long)us);
      lexV1Check(sm==LEXV1_OK && !strcmp(tid,"CF88:ART.114:INC.VIII"),falhaRt?"FAIL_IO":"FAIL_TARGET","text_to_target_114_VIII",det);
      sm=lexv1TargetAtOffset(textMap,bytesTexto,lido?sha:nullptr,textMap.adctStart,tid,sizeof(tid));
      snprintf(det,sizeof(det),"offset=%lu -> %s %s",(unsigned long)textMap.adctStart,lexv1StatusName(sm),tid);
      lexV1Check(sm==LEXV1_OK && !strcmp(tid,"ADCT"),"FAIL_TARGET","text_to_target_inicio_adct",det);
    }
    map.fechar();
  }

  // 4) regime: 3 indices pequenos abertos (TARGETS, ENTENDA_LOOKUP, REF_LOOKUP); payloads sob demanda
  LexV1FileReader tgt, lk, rl, pl, rp;
  LexV1Index targets, lookup, refLookup;
  t0=micros();
  LexV1Status s1=tgt.abrir("TARGETS","/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX","steady")?lexv1OpenIndex(targets,&tgt,"TARGETS",LEXV1_TARGETS_VERSION):LEXV1_FAIL_IO;
  LexV1Status s3=lk.abrir("ENTENDA_LOOKUP","/99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX","steady")?lexv1OpenIndex(lookup,&lk,"ENTENDA_LOOKUP",2):LEXV1_FAIL_IO;
  LexV1Status s4=rl.abrir("REF_LOOKUP","/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX","steady")?lexv1OpenIndex(refLookup,&rl,"REF_LOOKUP",1):LEXV1_FAIL_IO;
  pl.preparar("ENTENDA_PAYLOAD","/99_LEX_V1/30_ENTENDA/ENTENDA_PAYLOAD.DAT","entenda_payload");
  rp.preparar("REF_PAYLOAD","/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX","reference_payload");
  Serial.printf("LEXV1: TIME open_indices_us=%lu\n",(unsigned long)(micros()-t0));
  lexV1Check(s1==LEXV1_OK,s1==LEXV1_FAIL_IO?"FAIL_IO":"FAIL_PARSE","targets_idx",lexv1StatusName(s1));
  lexV1Check(s3==LEXV1_OK,s3==LEXV1_FAIL_IO?"FAIL_IO":"FAIL_PARSE","entenda_lookup_idx",lexv1StatusName(s3));
  lexV1Check(s4==LEXV1_OK,s4==LEXV1_FAIL_IO?"FAIL_IO":"FAIL_PARSE","references_lookup_idx",lexv1StatusName(s4));
  snprintf(det,sizeof(det),"OPEN_COUNT=%d limite=%d",lexV1FdOpen,LEXV1_FD_STEADY_MAX);
  lexV1Check(lexV1FdOpen<=LEXV1_FD_STEADY_MAX,"FAIL_IO","fd_steady_state",det);

  // 5) consultas: target table, ENTENDA (DIRECT/BLOCK/NONE), Reference Engine
  if(s1==LEXV1_OK && s3==LEXV1_OK && s4==LEXV1_OK){
    static const LexV1Caso casos[]={
      {"CF88:ART.5:INC.V",true,LEXV1_RES_COVERED_BY_BLOCK,"CF88:ART.5:INC.IV",1,1},
      {"CF88:ART.21:INC.XXIV",true,LEXV1_RES_DIRECT,"CF88:ART.21:INC.XXIV",0,0},
      {"CF88:ART.22:INC.XXIX",true,LEXV1_RES_DIRECT,"CF88:ART.22:INC.XXIX",0,0},
      {"CF88:ART.24:PAR.4",true,LEXV1_RES_COVERED_BY_BLOCK,"CF88:ART.24:PAR.3",0,0},
      {"CF88:ART.37:PAR.6",true,LEXV1_RES_DIRECT,"CF88:ART.37:PAR.6",5,5},
      {"CF88:ART.60:PAR.4:INC.IV",true,LEXV1_RES_DIRECT,"CF88:ART.60:PAR.4:INC.IV",0,0},
      {"ADCT:ART.10:INC.II",true,LEXV1_RES_DIRECT,"ADCT:ART.10:INC.II",0,0},
      {"CF88:ART.114:INC.VIII",true,LEXV1_RES_NONE,"",2,0},   // known issue: 2 referencias historicas ocultas
      {"CF88:ART.25",true,LEXV1_RES_NONE,"",1,1},
      {"CF88:ART.999",false,LEXV1_RES_NONE,"",0,0},
    };
    for(const LexV1Caso &c: casos){
      LexV1Target t; LexV1Entenda e; LexV1Refs rf;
      char linha[LEXV1_LINE_MAX];
      pl.falhaIo=rp.falhaIo=false;
      uint32_t a=micros();
      LexV1Status st=lexv1TargetInfo(targets,c.tid,t);
      uint32_t usTarget=micros()-a;
      a=micros();
      LexV1Status sl=(st==LEXV1_OK)?lexv1Find(lookup,c.tid,linha,sizeof(linha),false):LEXV1_NOT_FOUND;
      uint32_t usLookup=micros()-a;
      a=micros();
      LexV1Status se=(st==LEXV1_OK)?lexv1Entenda(lookup,&pl,c.tid,e):LEXV1_NOT_FOUND;   // abre o payload so se houver linha
      uint32_t usEntenda=micros()-a;
      uint32_t usPayload=0, lidos=0;
      if(se==LEXV1_OK){
        uint8_t buf[512]; a=micros();
        if(pl.seek(e.offset)) while(lidos<e.length){ int k=pl.read(buf,(int)min((uint32_t)sizeof(buf),e.length-lidos)); if(k<=0) break; lidos+=k; }
        usPayload=micros()-a;
      }
      bool plAberto=(bool)pl.f;
      pl.fechar();
      a=micros();
      LexV1Status sr=(st==LEXV1_OK)?lexv1References(refLookup,&rp,c.tid,rf):LEXV1_NOT_FOUND;   // abre REF_PAYLOAD so se QUANTIDADE>0
      uint32_t usRefs=micros()-a;
      bool rpAberto=(bool)rp.f;
      rp.fechar();
      Serial.printf("LEXV1: Q %s target=%s status=%s flags=%s entenda=%s res=%s anchor=%s off=%lu len=%lu lidos=%lu refs=%u/%u visiveis=%u "
                    "ref_bytes=%lu entenda_payload_aberto=%d ref_payload_aberto=%d us_target=%lu us_lookup=%lu us_entenda=%lu us_payload=%lu us_refs=%lu\n",
                    c.tid,lexv1StatusName(st),t.legalStatus,t.flags,lexv1StatusName(se),lexv1ResolutionName(e.resolution),e.anchor,
                    (unsigned long)e.offset,(unsigned long)e.length,(unsigned long)lidos,rf.parsed,rf.count,rf.visible,(unsigned long)rf.bytes,
                    plAberto,rpAberto,(unsigned long)usTarget,(unsigned long)usLookup,(unsigned long)usEntenda,(unsigned long)usPayload,
                    (unsigned long)usRefs);
      bool okE, okR;
      if(!c.existe) okE=(st==LEXV1_NOT_FOUND && se==LEXV1_NOT_FOUND);
      else if(c.res==LEXV1_RES_NONE) okE=(st==LEXV1_OK && se==LEXV1_NOT_FOUND && sl==LEXV1_NOT_FOUND && !plAberto);
      else okE=(st==LEXV1_OK && se==LEXV1_OK && e.resolution==c.res && !strcmp(e.anchor,c.ancora) && lidos==e.length);
      okR=c.existe ? (sr==LEXV1_OK && rf.count==c.refs && rf.parsed==c.refs && rf.visible==c.visiveis && rpAberto==(c.refs>0)) : true;
      const char *cat=(pl.falhaIo||rp.falhaIo)?"FAIL_IO":(!okE && st!=LEXV1_OK && c.existe)?"FAIL_TARGET":!okE?"FAIL_PARSE":"FAIL_REFERENCE";
      lexV1Check(okE && okR,cat,c.tid,c.existe?(c.res==LEXV1_RES_COVERED_BY_BLOCK?"BLOCK":c.res==LEXV1_RES_DIRECT?"DIRECT":"NONE"):"INVALID_OR_UNKNOWN_TARGET");
      if(c.res==LEXV1_RES_COVERED_BY_BLOCK && se==LEXV1_OK){
        // BLOCK: o alvo usa o MESMO bloco do payload da ancora (sem duplicar payload)
        LexV1Entenda ea;
        a=micros();
        LexV1Status sa=lexv1Entenda(lookup,&pl,c.ancora,ea);
        uint32_t usAnc=micros()-a;
        pl.fechar();
        Serial.printf("LEXV1: TIME block_resolution_us=%lu (%s)\n",(unsigned long)usEntenda,c.tid);
        snprintf(det,sizeof(det),"%s -> %s off=%lu/%lu len=%lu/%lu anchor_us=%lu",c.tid,c.ancora,(unsigned long)e.offset,(unsigned long)ea.offset,
                 (unsigned long)e.length,(unsigned long)ea.length,(unsigned long)usAnc);
        lexV1Check(sa==LEXV1_OK && ea.resolution==LEXV1_RES_DIRECT && ea.offset==e.offset && ea.length==e.length,
                   pl.falhaIo?"FAIL_IO":"FAIL_PARSE","block_sem_payload_duplicado",det);
      }
    }
    // Reference Engine: zero / um / varios resultados (so contagem, offset e parse; nenhum conteudo editorial)
    LexV1Refs z,u,m;
    rp.falhaIo=false;
    LexV1Status a1=lexv1References(refLookup,&rp,"CF88:ART.21:INC.XXIV",z);
    bool zAberto=(bool)rp.f; rp.fechar();
    LexV1Status a2=lexv1References(refLookup,&rp,"CF88:ART.25",u);
    bool uAberto=(bool)rp.f; rp.fechar();
    LexV1Status a3=lexv1References(refLookup,&rp,"CF88:ART.37:PAR.6",m);
    bool mAberto=(bool)rp.f; rp.fechar();
    const char *catR=rp.falhaIo?"FAIL_IO":"FAIL_REFERENCE";
    snprintf(det,sizeof(det),"count=%u payload_aberto=%d",z.count,zAberto);
    lexV1Check(a1==LEXV1_OK && z.count==0 && z.parsed==0 && !zAberto,catR,"references_zero_result",det);
    snprintf(det,sizeof(det),"count=%u offset=%lu parsed=%u payload_aberto=%d",u.count,(unsigned long)u.offset,u.parsed,uAberto);
    lexV1Check(a2==LEXV1_OK && u.count==1 && u.parsed==1 && uAberto,catR,"references_single_result",det);
    snprintf(det,sizeof(det),"count=%u offset=%lu parsed=%u bytes=%lu payload_aberto=%d",m.count,(unsigned long)m.offset,m.parsed,
             (unsigned long)m.bytes,mAberto);
    lexV1Check(a3==LEXV1_OK && m.count==5 && m.parsed==5 && mAberto,catR,"references_multiple_result",det);
  }
  pl.fechar(); rp.fechar(); tgt.fechar(); lk.fechar(); rl.fechar();
  snprintf(det,sizeof(det),"MAX_OPEN_COUNT=%d limite=%d OPEN_COUNT_FINAL=%d",lexV1FdMax,LEXV1_FD_PEAK_MAX,lexV1FdOpen);
  lexV1Check(lexV1FdMax<=LEXV1_FD_PEAK_MAX && lexV1FdOpen==0,"FAIL_IO","fd_pico_e_fechamento",det);
  lexV1Mem("depois_device_v1");
  Serial.printf("LEXV1: DIAG RESULT %s pass=%u fail=%u MAX_OPEN_COUNT=%d\n",lexV1Fail==0?"PASS":"FAIL",lexV1Pass,lexV1Fail,lexV1FdMax);
}
#endif

// =====================================================
// LOOP
// =====================================================
void loop()
{
  ble.update();
  processarTouch();

  if(pedirFecharSplash){
    pedirFecharSplash=false;
    pedirVoltar=false;
    pedirAbrir=false;
    fecharSplashManual();
  }

  int dp=deltaPastas;
  if(dp!=0){
    deltaPastas=0;
    if(telaAtual==TELA_PASTAS) moverSelecaoPasta(dp);
  }

  int dl=deltaLeitor;
  if(dl!=0){
    deltaLeitor=0;
    if(telaAtual==TELA_LEITOR) rolarLeitor(dl);
  }

  int dr=deltaRelacoes;
  if(dr!=0){
    deltaRelacoes=0;
    if(telaAtual==TELA_RELACOES) moverSelecaoRelacao(dr);
    else if(telaAtual==TELA_JURIS_CATEGORIAS) moverSelecaoCategoriaJuris(dr);
  }

  if(pedirCategoriaRelacao!=0){
    uint8_t categoria=pedirCategoriaRelacao;
    pedirCategoriaRelacao=0;
    if(categoria==255 && telaAtual==TELA_LEITOR && menuRelacoesAtivo && !visualizandoReferencia){
      if(arquivoAtualPertenceACF() && totalCategoriasJuris==1 &&
         categoriasJurisDisponiveis[0]==REL_JURIS_TODAS)
        abrirCategoriaRelacao(REL_JURIS_TODAS);
      else
        abrirTelaCategoriasJuris();
    }
    else if((telaAtual==TELA_LEITOR || telaAtual==TELA_JURIS_CATEGORIAS) &&
            menuRelacoesAtivo && !visualizandoReferencia)
      abrirCategoriaRelacao((CategoriaRelacao)categoria);
  }

  if(pedirAbrirRelacao){
    pedirAbrirRelacao=false;
    if(telaAtual==TELA_RELACOES) abrirRelacaoSelecionada();
  }

  if(pedirVoltar){
    pedirVoltar=false;
    pedirAbrir=false;
    pedirBuscar=false;
    pedirBuscaTexto=false;
    pedirBackTexto=false;
    pedirRedesenharBusca=false;
    touchConsumido=true;
    if(telaAtual==TELA_BUSCA_TEXTO) fecharBuscaTexto();
    else voltarPastas();
  }else if(pedirAbrir){
    pedirAbrir=false;
    touchConsumido=true;
    if(telaAtual==TELA_PASTAS) abrirPastaSelecionada();
  }

  if(pedirRedesenharBusca){
    pedirRedesenharBusca=false;
    if(telaAtual==TELA_LEITOR) desenharBarraBusca();
  }

  if(pedirBuscar){
    pedirBuscar=false;
    if(telaAtual==TELA_LEITOR) executarBusca();
  }

  if(pedirBuscaTexto){
    pedirBuscaTexto=false;
    if(buscaAtiva==BUSCA_TEXTO &&
       (telaAtual==TELA_BUSCA_TEXTO || telaAtual==TELA_LEITOR) &&
       !displayApagado && !pedirAcordarDisplay) executarBuscaTexto();
  }

  if(pedirBackTexto){
    pedirBackTexto=false;
    if(buscaAtiva==BUSCA_TEXTO && !displayApagado && !pedirAcordarDisplay){
      if(telaAtual==TELA_BUSCA_TEXTO) apagarAntesCursorBuscaTexto();
      else if(telaAtual==TELA_LEITOR) ocorrenciaAnteriorTexto();
    }
  }

  atualizarInatividadeDisplay();
  delay(1);
}
