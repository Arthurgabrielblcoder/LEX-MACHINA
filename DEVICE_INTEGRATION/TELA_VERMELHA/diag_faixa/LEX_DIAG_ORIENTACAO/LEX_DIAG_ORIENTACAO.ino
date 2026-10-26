// =====================================================
// LEX MACHINA - LEX_DIAG_ORIENTACAO v1 (tela vermelha 3,2" SPI)
// Variante de diagnostico do LEX_DIAG_FAIXA com SELECAO MANUAL pelo Monitor Serial (115200).
// Separado do firmware principal: sem conteudo juridico, sem SD (CS do SD em HIGH, SD nunca iniciado), sem BLE, sem touch.
// Cada configuracao fica na tela ate chegar um comando:
//   n = proxima   p = anterior   0..9 + Enter = ir direto   b = alterna BGR/RGB   i = alterna INVON/INVOFF
//   r = redesenhar   ? = lista de configuracoes
// O padrao identifica esquerda/direita, cima/baixo, espelhamento (texto e "F" assimetrico), 4 cantos, preenchimento
// total (bordas coloridas nos 4 lados), cores RGB e legibilidade. Nao depende da leitura de ID do controlador.
// =====================================================
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

// Pinos iguais ao LEX_DIAG_FAIXA (7f63042): RESET fisicamente no GPIO15
#define TFT_CS    10
#define TFT_DC     9
#define TFT_RST   15
#define TFT_MOSI  11
#define TFT_SCK   12
#define TFT_MISO  13
#define SD_CS      4

#define SPI_ESCRITA 40000000   // mesma frequencia do firmware principal e do LEX_DIAG_FAIXA

#define MADCTL_MY  0x80
#define MADCTL_MX  0x40
#define MADCTL_MV  0x20
#define MADCTL_BGR 0x08

static const uint16_t VERDE_ESCURO = 0x0180, LARANJA = 0xFD20;

class TftDiag : public Adafruit_ILI9341 {
public:
  using Adafruit_ILI9341::Adafruit_ILI9341;
  void forcarGeometria(int16_t w, int16_t h) { _width = w; _height = h; }
  void madctlCru(uint8_t m) { sendCommand(ILI9341_MADCTL, &m, 1); }
};

struct Config { const char *nome; uint8_t madctl; int16_t w, h; const char *origem; };

// MADCTL com BGR (0x08) ligado, como na lib. Primeiro as candidatas em paisagem 320x240.
static const Config CONFIGS[] = {
  {"LIB ROT1",   MADCTL_MV | MADCTL_BGR,                          320, 240, "setRotation(1) da lib"},
  {"LIB ROT3",   MADCTL_MX | MADCTL_MY | MADCTL_MV | MADCTL_BGR,  320, 240, "setRotation(3) da lib = firmware principal"},
  {"MV+MX",      MADCTL_MX | MADCTL_MV | MADCTL_BGR,              320, 240, "troca de eixos + espelho X"},
  {"MV+MY",      MADCTL_MY | MADCTL_MV | MADCTL_BGR,              320, 240, "troca de eixos + espelho Y"},
  {"RAW 08",     MADCTL_BGR,                                      320, 240, "LEX_DIAG_FAIXA RAW 08 (sem MV, 320x240 forcado)"},
  {"RAW 48",     MADCTL_MX | MADCTL_BGR,                          320, 240, "LEX_DIAG_FAIXA RAW 48 (sem MV, 320x240 forcado)"},
  {"RAW 88",     MADCTL_MY | MADCTL_BGR,                          320, 240, "LEX_DIAG_FAIXA RAW 88 (sem MV, 320x240 forcado)"},
  {"RAW C8",     MADCTL_MX | MADCTL_MY | MADCTL_BGR,              320, 240, "LEX_DIAG_FAIXA RAW C8 (sem MV, 320x240 forcado)"},
  {"LIB ROT0",   MADCTL_MX | MADCTL_BGR,                          240, 320, "setRotation(0) da lib (retrato, referencia)"},
  {"LIB ROT2",   MADCTL_MY | MADCTL_BGR,                          240, 320, "setRotation(2) da lib (retrato, referencia)"},
};
static const uint8_t N_CONFIGS = sizeof(CONFIGS) / sizeof(CONFIGS[0]);

SPIClass spiBus(FSPI);
TftDiag tft(&spiBus, TFT_DC, TFT_CS, TFT_RST);
static uint8_t atual = 0;
static bool bgr = true, invon = false;

uint8_t madctlAtual() { uint8_t m = CONFIGS[atual].madctl; return bgr ? (m | MADCTL_BGR) : (m & ~MADCTL_BGR); }

void texto(int16_t x, int16_t y, const char *s, uint8_t tam, uint16_t frente, uint16_t fundo)
{
  tft.setTextSize(tam); tft.setTextColor(frente, fundo); tft.setCursor(x, y); tft.print(s);
}

void desenhar()
{
  const Config &c = CONFIGS[atual];
  uint8_t m = madctlAtual();
  tft.madctlCru(m);
  tft.forcarGeometria(c.w, c.h);
  tft.invertDisplay(invon);
  int16_t W = tft.width(), H = tft.height();

  tft.fillScreen(ILI9341_BLACK);
  for (int x = 40; x < W; x += 40) tft.drawFastVLine(x, 0, H, VERDE_ESCURO);
  for (int y = 40; y < H; y += 40) tft.drawFastHLine(0, y, W, VERDE_ESCURO);

  // Bordas de 4 px, uma cor por lado: preenchimento total = as quatro aparecem inteiras
  tft.fillRect(0, 0, W, 4, ILI9341_RED);          // CIMA
  tft.fillRect(0, H - 4, W, 4, ILI9341_BLUE);     // BAIXO
  tft.fillRect(0, 0, 4, H, ILI9341_GREEN);        // ESQUERDA
  tft.fillRect(W - 4, 0, 4, H, ILI9341_YELLOW);   // DIREITA
  // Cantos 18x18 numerados no sentido de leitura: 1 sup-esq, 2 sup-dir, 3 inf-esq, 4 inf-dir
  tft.fillRect(0, 0, 18, 18, ILI9341_MAGENTA);       texto(6, 5, "1", 1, ILI9341_BLACK, ILI9341_MAGENTA);
  tft.fillRect(W - 18, 0, 18, 18, ILI9341_CYAN);     texto(W - 12, 5, "2", 1, ILI9341_BLACK, ILI9341_CYAN);
  tft.fillRect(0, H - 18, 18, 18, ILI9341_WHITE);    texto(6, H - 13, "3", 1, ILI9341_BLACK, ILI9341_WHITE);
  tft.fillRect(W - 18, H - 18, 18, 18, LARANJA);     texto(W - 12, H - 13, "4", 1, ILI9341_BLACK, LARANJA);

  texto(W / 2 - 24, 8, "CIMA", 2, ILI9341_RED, ILI9341_BLACK);
  texto(W / 2 - 30, H - 24, "BAIXO", 2, ILI9341_BLUE, ILI9341_BLACK);
  texto(8, H / 2 - 8, "ESQ", 2, ILI9341_GREEN, ILI9341_BLACK);
  texto(W - 44, H / 2 - 8, "DIR", 2, ILI9341_YELLOW, ILI9341_BLACK);
  // Seta para a direita (texto deve ler da esquerda para a direita, na mesma direcao)
  tft.fillTriangle(W - 60, H / 2 + 20, W - 60, H / 2 + 36, W - 46, H / 2 + 28, ILI9341_YELLOW);
  tft.fillRect(W - 100, H / 2 + 26, 40, 5, ILI9341_YELLOW);

  // Identificacao
  char l1[40], l2[48];
  snprintf(l1, sizeof(l1), "CFG %u %s", atual, c.nome);
  snprintf(l2, sizeof(l2), "MADCTL=0x%02X W=%d H=%d %s %s", m, W, H, bgr ? "BGR" : "RGB", invon ? "INVON" : "INVOFF");
  texto(24, 30, l1, 2, ILI9341_GREEN, ILI9341_BLACK);
  texto(24, 52, l2, 1, ILI9341_GREEN, ILI9341_BLACK);
  texto(24, 64, "LEX MACHINA leia normal?", 1, ILI9341_WHITE, ILI9341_BLACK);

  // "F" grande assimetrico: espelho X vira a perna para a esquerda; espelho Y poe a barra curta em cima/baixo
  int16_t fx = W / 2 - 40, fy = H / 2 - 30;
  tft.fillRect(fx, fy, 10, 60, ILI9341_WHITE);
  tft.fillRect(fx, fy, 36, 10, ILI9341_WHITE);
  tft.fillRect(fx, fy + 24, 24, 9, ILI9341_WHITE);

  // Barras RGB rotuladas
  int16_t by = H / 2 + 44;
  if (by + 26 < H - 26) {
    tft.fillRect(W / 2 - 75, by, 50, 26, ILI9341_RED);   texto(W / 2 - 56, by + 9, "R", 1, ILI9341_BLACK, ILI9341_RED);
    tft.fillRect(W / 2 - 25, by, 50, 26, ILI9341_GREEN); texto(W / 2 - 6, by + 9, "G", 1, ILI9341_BLACK, ILI9341_GREEN);
    tft.fillRect(W / 2 + 25, by, 50, 26, ILI9341_BLUE);  texto(W / 2 + 44, by + 9, "B", 1, ILI9341_WHITE, ILI9341_BLUE);
  }

  Serial.printf("[SEL] CFG %u/%u  %-9s MADCTL=0x%02X geometria=%dx%d %s %s SPI=%luHz  (%s)\n", atual, N_CONFIGS - 1, c.nome, m,
                W, H, bgr ? "BGR" : "RGB", invon ? "INVON" : "INVOFF", (unsigned long)SPI_ESCRITA, c.origem);
}

void listar()
{
  Serial.println("[LISTA] configuracoes (BGR ligado por padrao; 'b' alterna, 'i' alterna inversao):");
  for (uint8_t i = 0; i < N_CONFIGS; i++)
    Serial.printf("[LISTA] %u  %-9s MADCTL=0x%02X  %dx%d  %s\n", i, CONFIGS[i].nome, CONFIGS[i].madctl, CONFIGS[i].w, CONFIGS[i].h, CONFIGS[i].origem);
  Serial.println("[AJUDA] n=proxima p=anterior 0..9+Enter=direto b=BGR/RGB i=INVON/INVOFF r=redesenhar ?=lista");
}

void setup()
{
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 3000) delay(10);
  pinMode(SD_CS, OUTPUT); digitalWrite(SD_CS, HIGH);   // SD desselecionado; nunca iniciado
  pinMode(TFT_CS, OUTPUT); digitalWrite(TFT_CS, HIGH);
  spiBus.begin(TFT_SCK, TFT_MISO, TFT_MOSI, -1);
  tft.begin(SPI_ESCRITA);
  tft.setRotation(3);
  tft.invertDisplay(false);
  Serial.println("\n[DIAG] LEX_DIAG_ORIENTACAO v1 - selecao manual de orientacao (tela vermelha 3,2\")");
  Serial.printf("[DIAG] pinos TFT CS=%d DC=%d RST=%d MOSI=%d SCK=%d MISO=%d; SD_CS=%d (HIGH, SD nao iniciado)\n",
                TFT_CS, TFT_DC, TFT_RST, TFT_MOSI, TFT_SCK, TFT_MISO, SD_CS);
  Serial.printf("[DIAG] SPI FSPI %lu Hz; lib Adafruit_ILI9341 (init ILI9341); INVOFF\n", (unsigned long)SPI_ESCRITA);
  listar();
  desenhar();
}

void loop()
{
  static char num[4]; static uint8_t nNum = 0;
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch >= '0' && ch <= '9') { if (nNum < 3) num[nNum++] = ch; continue; }
    if ((ch == '\n' || ch == '\r') && nNum) {
      num[nNum] = 0; int v = atoi(num); nNum = 0;
      if (v >= 0 && v < N_CONFIGS) { atual = v; desenhar(); }
      else Serial.printf("[ERRO] indice %d fora de 0..%u\n", v, N_CONFIGS - 1);
      continue;
    }
    nNum = 0;
    switch (ch) {
      case 'n': case 'N': atual = (atual + 1) % N_CONFIGS; desenhar(); break;
      case 'p': case 'P': atual = (atual + N_CONFIGS - 1) % N_CONFIGS; desenhar(); break;
      case 'b': case 'B': bgr = !bgr; desenhar(); break;
      case 'i': case 'I': invon = !invon; desenhar(); break;
      case 'r': case 'R': desenhar(); break;
      case '?': listar(); break;
      default: break;   // \r, \n e espacos sao ignorados
    }
  }
  delay(10);
}
