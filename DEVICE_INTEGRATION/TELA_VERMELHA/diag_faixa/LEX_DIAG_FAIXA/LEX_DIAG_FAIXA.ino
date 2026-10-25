// =====================================================
// LEX MACHINA - DIAGNOSTICO DA FAIXA (tela vermelha 3,2")
// Firmware de teste SEPARADO: nao contem recursos juridicos, nao inicia SD, BLE nem touch.
// Mesmos pinos, mesmo barramento FSPI, mesma lib Adafruit_ILI9341, begin(40 MHz), rotacao 3 e INVOFF do firmware INVON=0.
// Fases (repetem em ciclo, ~15 s cada; titulo na tela + log no Serial USB a 115200):
//   A  GEOMETRIA 40MHz : grade 40 px, borda 320x240, cantos coloridos (como o firmware desenha)
//   B  GRAM ESTENDIDA  : janela 480x480 em MAGENTA e depois a grade A por cima
//                        -> faixa MAGENTA = memoria fora de 320x240 (geometria); faixa ainda aleatoria = nao enderecavel
//   C  LEITURA GRAM    : escreve e le de volta 1 pixel no centro de cada celula 40x40 (precisa de MISO do LCD)
//   D  GEOMETRIA 10MHz : igual a A, so o clock SPI muda
//   E  REDESENHO 40MHz : grade A redesenhada 30x seguidas (procura flicker/instabilidade)
// Nao grava nada na flash alem do proprio upload; nao escreve no SD.
// =====================================================
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

#define TFT_CS    10
#define TFT_DC     9
#define TFT_RST   14
#define TFT_MOSI  11
#define TFT_SCK   12
#define TFT_MISO  13
#define SD_CS      4

#define SPI_ESCRITA 40000000
#define SPI_LENTO   10000000
#define SPI_LEITURA  4000000   // ILI9341: ciclo de leitura serial ~150 ns
#define FASE_MS     15000

SPIClass spiBus(FSPI);
Adafruit_ILI9341 tft(&spiBus, TFT_DC, TFT_CS, TFT_RST);

static const uint16_t VERDE = ILI9341_GREEN, VERDE_ESCURO = 0x0180, MAGENTA = 0xF81F;
static bool misoResponde = false;
static uint32_t ciclo = 0;

// Leitura bruta (sem o indice 0xD9): le n+1 bytes e descarta 'dummyBits' bits iniciais
void lerBruto(uint8_t cmd, uint8_t *out, uint8_t n, uint8_t dummyBits)
{
  uint8_t buf[8] = {0};
  spiBus.beginTransaction(SPISettings(SPI_LEITURA, MSBFIRST, SPI_MODE0));
  digitalWrite(TFT_CS, LOW);
  digitalWrite(TFT_DC, LOW);
  spiBus.transfer(cmd);
  digitalWrite(TFT_DC, HIGH);
  for (uint8_t i = 0; i <= n && i < sizeof(buf); i++) buf[i] = spiBus.transfer(0x00);
  digitalWrite(TFT_CS, HIGH);
  spiBus.endTransaction();
  for (uint8_t i = 0; i < n; i++)
    out[i] = dummyBits ? (uint8_t)((buf[i] << dummyBits) | (buf[i + 1] >> (8 - dummyBits))) : buf[i];
}

void imprimirHex(const char *rotulo, const uint8_t *b, uint8_t n)
{
  Serial.printf("[ID] %-28s", rotulo);
  for (uint8_t i = 0; i < n; i++) Serial.printf(" %02X", b[i]);
  Serial.println();
}

void lerIdentificacao()
{
  uint8_t b[4];
  uint8_t d3[3] = {tft.readcommand8(0xD3, 1), tft.readcommand8(0xD3, 2), tft.readcommand8(0xD3, 3)};
  imprimirHex("RDID4 D3 (D9 idx1..3)", d3, 3);          // ILI9341 genuino: 00 93 41
  uint8_t st[5] = {tft.readcommand8(0x0A), tft.readcommand8(0x0B), tft.readcommand8(0x0C),
                   tft.readcommand8(0x0D), tft.readcommand8(0x0F)};
  imprimirHex("0A PWR 0B MADCTL 0C PIX 0D 0F", st, 5);   // esperado: 9C 28 05 00 C0 (aprox.) com rot3/BGR
  lerBruto(0x04, b, 3, 1); imprimirHex("RDDID 04 bruto (1 bit dummy)", b, 3);   // ST7789: 85 85 52
  lerBruto(0x09, b, 4, 1); imprimirHex("RDDST 09 bruto (1 bit dummy)", b, 4);
  lerBruto(0xDA, b, 1, 0); imprimirHex("RDID1 DA bruto", b, 1);
  lerBruto(0xDB, b, 1, 0); imprimirHex("RDID2 DB bruto", b, 1);
  lerBruto(0xDC, b, 1, 0); imprimirHex("RDID3 DC bruto", b, 1);
  bool tudo00 = true, tudoFF = true;
  for (uint8_t i = 0; i < 3; i++) { tudo00 &= d3[i] == 0x00; tudoFF &= d3[i] == 0xFF; }
  for (uint8_t i = 0; i < 5; i++) { tudo00 &= st[i] == 0x00; tudoFF &= st[i] == 0xFF; }
  misoResponde = !(tudo00 || tudoFF);
  Serial.printf("[ID] MISO do LCD %s\n", misoResponde ? "RESPONDE" : "SEM RESPOSTA (SDO desligado ou MISO preso) - leitura inconclusiva");
  if (d3[1] == 0x93 && d3[2] == 0x41) Serial.println("[ID] CONTROLADOR = ILI9341 (RDID4 00 93 41)");
}

void titulo(const char *fase, const char *linha2)
{
  tft.fillRect(41, 41, 238, 38, ILI9341_BLACK);
  tft.setTextColor(VERDE, ILI9341_BLACK);
  tft.setTextSize(2); tft.setCursor(46, 44); tft.print(fase);
  tft.setTextSize(1); tft.setCursor(46, 66); tft.print(linha2);
}

// Grade de referencia: borda 320x240, linhas a cada 40 px rotuladas, cantos 12x12 (TL vermelho, TR azul, BL branco, BR amarelo)
void desenharGrade()
{
  tft.fillScreen(ILI9341_BLACK);
  for (int x = 40; x < 320; x += 40) tft.drawFastVLine(x, 0, 240, VERDE_ESCURO);
  for (int y = 40; y < 240; y += 40) tft.drawFastHLine(0, y, 320, VERDE_ESCURO);
  tft.drawRect(0, 0, 320, 240, VERDE);
  tft.setTextSize(1); tft.setTextColor(VERDE, ILI9341_BLACK);
  for (int x = 40; x < 320; x += 40) { tft.setCursor(x + 2, 14); tft.print(x); }
  for (int y = 40; y < 240; y += 40) { tft.setCursor(14, y + 2); tft.print(y); }
  tft.fillRect(0, 0, 12, 12, ILI9341_RED);
  tft.fillRect(308, 0, 12, 12, ILI9341_BLUE);
  tft.fillRect(0, 228, 12, 12, ILI9341_WHITE);
  tft.fillRect(308, 228, 12, 12, ILI9341_YELLOW);
}

void preencherGramEstendida()
{
  tft.startWrite();
  tft.writeCommand(ILI9341_CASET); tft.SPI_WRITE16(0); tft.SPI_WRITE16(479);
  tft.writeCommand(ILI9341_PASET); tft.SPI_WRITE16(0); tft.SPI_WRITE16(479);
  tft.writeCommand(ILI9341_RAMWR);
  tft.writeColor(MAGENTA, 480UL * 480UL);
  tft.endWrite();
}

// RAMRD serial: 1 byte dummy + R,G,B (6 bits em [7:2]). Aceita ordem RGB ou BGR.
bool lerPixel(int16_t x, int16_t y, uint8_t rgb[3])
{
  tft.startWrite(); tft.setAddrWindow(x, y, 1, 1); tft.endWrite();
  uint8_t b[4];
  lerBruto(ILI9341_RAMRD, b, 4, 0);
  rgb[0] = b[1]; rgb[1] = b[2]; rgb[2] = b[3];
  return true;
}

bool confere(uint16_t c, const uint8_t rgb[3])
{
  uint8_t r5 = c >> 11, g6 = (c >> 5) & 0x3F, b5 = c & 0x1F;
  bool g = (rgb[1] >> 2) == g6;
  bool rgbOk = (rgb[0] >> 3) == r5 && (rgb[2] >> 3) == b5;
  bool bgrOk = (rgb[0] >> 3) == b5 && (rgb[2] >> 3) == r5;
  return g && (rgbOk || bgrOk);
}

void testeLeituraGram()
{
  static const uint16_t PADROES[2] = {0xA5D2, 0x5A2D};
  Serial.println("[C] mapa 8x6 de celulas 40x40 (linha = y, coluna = x): . = le o que escreveu, X = diverge");
  uint16_t falhas = 0;
  for (int cy = 0; cy < 6; cy++) {
    char linha[9];
    for (int cx = 0; cx < 8; cx++) {
      int16_t x = cx * 40 + 20, y = cy * 40 + 20;
      bool ok = true;
      for (uint8_t p = 0; p < 2; p++) {
        tft.drawPixel(x, y, PADROES[p]);
        uint8_t rgb[3]; lerPixel(x, y, rgb);
        if (!confere(PADROES[p], rgb)) {
          ok = false;
          Serial.printf("[C] x=%3d y=%3d escrito=%04X lido=%02X %02X %02X\n", x, y, PADROES[p], rgb[0], rgb[1], rgb[2]);
        }
      }
      linha[cx] = ok ? '.' : 'X';
      if (!ok) falhas++;
      tft.fillRect(x - 5, y - 5, 10, 10, ok ? VERDE : ILI9341_RED);
    }
    linha[8] = 0;
    Serial.printf("[C] y=%3d  %s\n", cy * 40, linha);
  }
  Serial.printf("[C] celulas divergentes: %u/48\n", falhas);
}

void segurar(const char *fase)
{
  uint32_t t0 = millis();
  while (millis() - t0 < FASE_MS) delay(50);
  Serial.printf("[%s] fim\n", fase);
}

void setup()
{
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 2000) delay(10);
  pinMode(SD_CS, OUTPUT); digitalWrite(SD_CS, HIGH);   // SD nunca e selecionado
  pinMode(TFT_CS, OUTPUT); digitalWrite(TFT_CS, HIGH);
  spiBus.begin(TFT_SCK, TFT_MISO, TFT_MOSI, -1);
  tft.begin(SPI_ESCRITA);
  tft.setRotation(3);
  tft.invertDisplay(false);
  Serial.println("\n[DIAG] LEX_DIAG_FAIXA v1 - init identico ao firmware INVON=0 (begin 40MHz, rot3, INVOFF)");
  Serial.printf("[DIAG] tft.width=%d height=%d\n", tft.width(), tft.height());
  lerIdentificacao();
}

void loop()
{
  ciclo++;
  Serial.printf("\n[DIAG] ciclo %lu\n", (unsigned long)ciclo);

  desenharGrade(); titulo("A 40MHz", "grade 320x240, cantos R/B/W/Y");
  Serial.println("[A] grade a 40 MHz"); segurar("A");

  preencherGramEstendida(); desenharGrade(); titulo("B GRAM 480x480", "faixa MAGENTA = memoria extra");
  Serial.println("[B] janela 480x480 MAGENTA + grade por cima"); segurar("B");

  desenharGrade(); titulo("C LEITURA GRAM", misoResponde ? "verde=ok vermelho=diverge" : "MISO sem resposta");
  if (misoResponde) testeLeituraGram(); else Serial.println("[C] pulada: MISO sem resposta");
  segurar("C");

  tft.setSPISpeed(SPI_LENTO);
  desenharGrade(); titulo("D 10MHz", "so o clock SPI mudou");
  Serial.println("[D] grade a 10 MHz"); segurar("D");
  tft.setSPISpeed(SPI_ESCRITA);

  Serial.println("[E] 30 redesenhos a 40 MHz");
  for (int i = 0; i < 30; i++) {
    desenharGrade();
    char s[24]; snprintf(s, sizeof(s), "redesenho %d/30", i + 1);
    titulo("E 40MHz", s);
  }
  segurar("E");
}
