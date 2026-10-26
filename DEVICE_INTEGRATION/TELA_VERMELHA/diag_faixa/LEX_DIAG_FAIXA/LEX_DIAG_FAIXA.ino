// =====================================================
// LEX MACHINA - LEX_DIAG_FAIXA v2 (tela vermelha 3,2" SPI)
// Firmware de diagnostico SEPARADO do firmware principal: sem conteudo juridico, sem SD (CS do SD fica em HIGH e o SD
// nunca e iniciado), sem BLE, sem touch. Pinos, barramento FSPI e lib identicos ao firmware INVON=0 da branch.
// Ciclo automatico (repete), cada etapa com rotulo na tela e log no Serial USB 115200:
//   ROT 0..3 : cores cheias (preto, vermelho, verde, azul, branco, preto) -> geometria -> limites -> blocos de 80 px
//   INV      : invertDisplay(true) por 3 s e volta a false (so diagnostico)
//   SPI      : geometria ROT 3 a 10 MHz (unica variavel) e volta a 40 MHz
//   RAW      : MADCTL sem troca de eixos (0x08/0x48/0x88/0xC8) com geometria logica 320x240 forcada
//              (hipotese: painel nativo em paisagem). So escreve na tela; nada fora dos buffers do ESP32.
// Ao fim de cada ciclo volta ao estado conhecido: setRotation(3), INVOFF, 40 MHz.
// =====================================================
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

// Pinos copiados do firmware principal (LEX_MACHINA_DEVICE_V1_CANDIDATE.ino, secao PINOS)
#define TFT_CS    10
#define TFT_DC     9
#define TFT_RST   14
#define TFT_MOSI  11
#define TFT_SCK   12
#define TFT_MISO  13
#define SD_CS      4

#define SPI_ESCRITA 40000000   // mesma frequencia de tft.begin() no firmware principal
#define SPI_LENTO   10000000
#define T_COR       1800
#define T_GEOMETRIA 8000
#define T_LIMITES   7000
#define T_BLOCOS    5000

static const uint16_t VERDE_ESCURO = 0x0180, CINZA = 0x4208;

// Acesso de diagnostico: geometria logica e MADCTL crus (estado volta ao normal com setRotation)
class TftDiag : public Adafruit_ILI9341 {
public:
  using Adafruit_ILI9341::Adafruit_ILI9341;
  void forcarGeometria(int16_t w, int16_t h) { _width = w; _height = h; }
  void madctlCru(uint8_t m) { sendCommand(ILI9341_MADCTL, &m, 1); }
};

SPIClass spiBus(FSPI);
TftDiag tft(&spiBus, TFT_DC, TFT_CS, TFT_RST);
static uint32_t ciclo = 0;
static char etapa[128] = "";

void marcar(const char *fmt, ...)
{
  va_list ap; va_start(ap, fmt); vsnprintf(etapa, sizeof(etapa), fmt, ap); va_end(ap);
  Serial.printf("[%7lu ms] %s\n", (unsigned long)millis(), etapa);
}

void rotuloCentro(const char *s, uint16_t frente, uint16_t fundo, uint8_t tam)
{
  int16_t w = strlen(s) * 6 * tam, h = 8 * tam;
  int16_t x = (tft.width() - w) / 2, y = (tft.height() - h) / 2;
  tft.fillRect(x - 4, y - 4, w + 8, h + 8, fundo);
  tft.setTextSize(tam); tft.setTextColor(frente, fundo); tft.setCursor(x, y); tft.print(s);
}

void lerIdentificacao()
{
  uint8_t d3[3] = {tft.readcommand8(0xD3, 1), tft.readcommand8(0xD3, 2), tft.readcommand8(0xD3, 3)};
  Serial.printf("[ID] RDID4 0xD3 (indice 0xD9) : %02X %02X %02X   (ILI9341 documenta 00 93 41)\n", d3[0], d3[1], d3[2]);
  Serial.printf("[ID] 0x0A modo energia        : %02X\n", tft.readcommand8(0x0A));
  Serial.printf("[ID] 0x0B MADCTL              : %02X\n", tft.readcommand8(0x0B));
  Serial.printf("[ID] 0x0C formato de pixel    : %02X\n", tft.readcommand8(0x0C));
  Serial.printf("[ID] 0x0D modo de imagem      : %02X\n", tft.readcommand8(0x0D));
  Serial.printf("[ID] 0x0F autodiagnostico     : %02X\n", tft.readcommand8(0x0F));
  bool vazio = (d3[0] == d3[1] && d3[1] == d3[2] && (d3[0] == 0x00 || d3[0] == 0xFF));
  Serial.printf("[ID] leitura %s\n", vazio ? "SEM RESPOSTA UTIL (SDO/MISO do LCD pode nao estar ligado): inconclusiva"
                                            : "respondeu; ainda assim nao prova sozinha o modelo do controlador");
}

void cores(uint8_t r)
{
  static const uint16_t C[6] = {ILI9341_BLACK, ILI9341_RED, ILI9341_GREEN, ILI9341_BLUE, ILI9341_WHITE, ILI9341_BLACK};
  static const char *N[6] = {"PRETO", "VERMELHO", "VERDE", "AZUL", "BRANCO", "PRETO"};
  for (uint8_t i = 0; i < 6; i++) {
    marcar("ROT %u cor %s fillScreen 0,0..%d,%d", r, N[i], tft.width() - 1, tft.height() - 1);
    tft.fillScreen(C[i]);
    char s[24]; snprintf(s, sizeof(s), "ROT%u %s", r, N[i]);
    uint16_t txt = (C[i] == ILI9341_WHITE || C[i] == ILI9341_GREEN) ? ILI9341_BLACK : ILI9341_WHITE;
    rotuloCentro(s, txt, C[i], 1);
    delay(T_COR);
  }
}

void geometria(const char *titulo)
{
  int16_t W = tft.width(), H = tft.height();
  tft.fillScreen(ILI9341_BLACK);
  for (int x = 20; x < W; x += 20) tft.drawFastVLine(x, 0, H, (x % 40) ? CINZA : VERDE_ESCURO);
  for (int y = 20; y < H; y += 20) tft.drawFastHLine(0, y, W, (y % 40) ? CINZA : VERDE_ESCURO);
  tft.drawRect(0, 0, W, H, ILI9341_GREEN);                 // borda externa 1 px
  tft.drawRect(5, 5, W - 10, H - 10, ILI9341_CYAN);        // borda interna a 5 px
  // cantos: L de 30 px (sup-esq vermelho, sup-dir azul, inf-esq branco, inf-dir amarelo)
  tft.fillRect(0, 0, 30, 3, ILI9341_RED);          tft.fillRect(0, 0, 3, 30, ILI9341_RED);
  tft.fillRect(W - 30, 0, 30, 3, ILI9341_BLUE);    tft.fillRect(W - 3, 0, 3, 30, ILI9341_BLUE);
  tft.fillRect(0, H - 3, 30, 3, ILI9341_WHITE);    tft.fillRect(0, H - 30, 3, 30, ILI9341_WHITE);
  tft.fillRect(W - 30, H - 3, 30, 3, ILI9341_YELLOW); tft.fillRect(W - 3, H - 30, 3, 30, ILI9341_YELLOW);
  tft.drawFastHLine(W / 2 - 20, H / 2, 41, ILI9341_MAGENTA); tft.drawFastVLine(W / 2, H / 2 - 20, 41, ILI9341_MAGENTA);
  tft.setTextSize(1); tft.setTextColor(ILI9341_GREEN, ILI9341_BLACK);
  for (int x = 40; x < W; x += 40) { tft.setCursor(x + 2, 9); tft.print(x); }
  for (int y = 40; y < H; y += 40) { tft.setCursor(9, y + 2); tft.print(y); }
  char wh[24]; snprintf(wh, sizeof(wh), "W=%d H=%d", W, H);
  tft.setTextColor(ILI9341_GREEN, ILI9341_BLACK);
  tft.setTextSize(4); tft.setCursor(W / 2 - (int)strlen(titulo) * 12, H / 2 - 52); tft.print(titulo);
  tft.setTextSize(2); tft.setCursor(W / 2 - (int)strlen(wh) * 6, H / 2 + 28); tft.print(wh);
  marcar("%s geometria: borda 0,0..%d,%d; borda interna 5; grade 20/40; cruz %d,%d", titulo, W - 1, H - 1, W / 2, H / 2);
}

void linhaV(int16_t x, uint16_t c) { if (x >= 0 && x < tft.width()) { tft.drawFastVLine(x, 0, tft.height(), c); Serial.printf("   x=%d\n", x); } }
void linhaH(int16_t y, uint16_t c) { if (y >= 0 && y < tft.height()) { tft.drawFastHLine(0, y, tft.width(), c); Serial.printf("   y=%d\n", y); } }

void limites(uint8_t r)
{
  int16_t W = tft.width(), H = tft.height();
  tft.fillScreen(ILI9341_BLACK);
  marcar("ROT %u limites (W=%d H=%d); linhas desenhadas:", r, W, H);
  // Cores: 0 e ultimo = branco; 1 = ciano; 79 = vermelho; 80 = verde; 239 = azul; 240 = amarelo; 319 = magenta
  linhaV(0, ILI9341_WHITE); linhaV(W - 1, ILI9341_WHITE); linhaV(1, ILI9341_CYAN);
  linhaV(79, ILI9341_RED); linhaV(80, ILI9341_GREEN); linhaV(239, ILI9341_BLUE); linhaV(240, ILI9341_YELLOW); linhaV(319, ILI9341_MAGENTA);
  linhaH(0, ILI9341_WHITE); linhaH(H - 1, ILI9341_WHITE); linhaH(1, ILI9341_CYAN);
  linhaH(79, ILI9341_RED); linhaH(80, ILI9341_GREEN); linhaH(239, ILI9341_BLUE); linhaH(240, ILI9341_YELLOW); linhaH(319, ILI9341_MAGENTA);
  char s[64]; snprintf(s, sizeof(s), "ROT%u LIMITES W=%d H=%d", r, W, H);
  rotuloCentro(s, ILI9341_GREEN, ILI9341_BLACK, 1);
  delay(T_LIMITES);
}

void blocos(const char *nome, bool verticais)
{
  static const uint16_t C[4] = {ILI9341_RED, ILI9341_GREEN, ILI9341_BLUE, ILI9341_YELLOW};
  static const char *N[4] = {"0-79", "80-159", "160-239", "240-319"};
  int16_t W = tft.width(), H = tft.height(), lim = verticais ? W : H;
  tft.fillScreen(ILI9341_BLACK);
  marcar("%s blocos de 80 px em %s (eixo de 0 a %d)", nome, verticais ? "colunas (X)" : "linhas (Y)", lim - 1);
  for (uint8_t i = 0; i < 4 && i * 80 < lim; i++) {
    int16_t a = i * 80, n = min<int16_t>(80, lim - a);
    if (verticais) tft.fillRect(a, 0, n, H, C[i]); else tft.fillRect(0, a, W, n, C[i]);
    tft.setTextSize(2); tft.setTextColor(ILI9341_BLACK, C[i]);
    if (verticais) tft.setCursor(a + 4, H / 2 - 30); else tft.setCursor(W / 2 - 30, a + 30);
    tft.print(N[i]);
  }
  char s[32]; snprintf(s, sizeof(s), "%s BLOCOS %s", nome, verticais ? "X" : "Y");
  rotuloCentro(s, ILI9341_WHITE, ILI9341_BLACK, 1);
  delay(T_BLOCOS);
}

void setup()
{
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 3000) delay(10);
  pinMode(SD_CS, OUTPUT); digitalWrite(SD_CS, HIGH);    // SD desselecionado; nunca iniciado
  pinMode(TFT_CS, OUTPUT); digitalWrite(TFT_CS, HIGH);
  spiBus.begin(TFT_SCK, TFT_MISO, TFT_MOSI, -1);
  tft.begin(SPI_ESCRITA);
  tft.setRotation(3);
  tft.invertDisplay(false);
  Serial.println("\n[DIAG] LEX_DIAG_FAIXA v2 - diagnostico da faixa e da orientacao (tela vermelha 3,2\")");
  Serial.printf("[DIAG] pinos TFT CS=%d DC=%d RST=%d MOSI=%d SCK=%d MISO=%d; SD_CS=%d (HIGH, SD nao iniciado)\n",
                TFT_CS, TFT_DC, TFT_RST, TFT_MOSI, TFT_SCK, TFT_MISO, SD_CS);
  Serial.printf("[DIAG] SPI FSPI %lu Hz; lib Adafruit_ILI9341 (init ILI9341); INVOFF\n", (unsigned long)SPI_ESCRITA);
  for (uint8_t r = 0; r < 4; r++) { tft.setRotation(r); Serial.printf("[DIAG] setRotation(%u): width=%d height=%d\n", r, tft.width(), tft.height()); }
  tft.setRotation(3);
  lerIdentificacao();
}

void loop()
{
  ciclo++;
  Serial.printf("\n[DIAG] ===== ciclo %lu =====\n", (unsigned long)ciclo);
  for (uint8_t r = 0; r < 4; r++) {
    tft.setRotation(r);
    cores(r);
    char t[8]; snprintf(t, sizeof(t), "ROT %u", r);
    geometria(t); delay(T_GEOMETRIA);
    limites(r);
    blocos(t, true);
    blocos(t, false);
  }

  tft.setRotation(3);
  geometria("INV");
  marcar("INV invertDisplay(true) por 3 s (diagnostico)"); tft.invertDisplay(true); delay(3000);
  marcar("INV invertDisplay(false) - estado conhecido"); tft.invertDisplay(false); delay(2000);

  tft.setSPISpeed(SPI_LENTO);
  geometria("10MHz"); marcar("SPI geometria ROT 3 a 10 MHz"); delay(T_GEOMETRIA);
  tft.setSPISpeed(SPI_ESCRITA); marcar("SPI de volta a 40 MHz");

  static const uint8_t RAW[4] = {0x08, 0x48, 0x88, 0xC8};   // BGR, sem MV; variam MX/MY
  for (uint8_t i = 0; i < 4; i++) {
    tft.madctlCru(RAW[i]);
    tft.forcarGeometria(320, 240);
    char t[12]; snprintf(t, sizeof(t), "RAW %02X", RAW[i]);
    marcar("RAW MADCTL=0x%02X geometria logica forcada 320x240", RAW[i]);
    geometria(t); delay(T_GEOMETRIA);
    blocos(t, true);
  }

  tft.setRotation(3); tft.invertDisplay(false); tft.setSPISpeed(SPI_ESCRITA);
  tft.fillScreen(ILI9341_BLACK);
  rotuloCentro("FIM DO CICLO - REINICIANDO", ILI9341_GREEN, ILI9341_BLACK, 2);
  marcar("fim do ciclo: estado conhecido (ROT 3, INVOFF, 40 MHz)");
  delay(3000);
}
