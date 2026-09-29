#pragma once
// LEX MACHINA DEVICE V1 (candidato A3B) - leitura do overlay /99_LEX_V1 conforme DEVICE_DATA_CONTRACT_V1.
// Texto exibido pelo runtime V1: /99_LEX_V1/05_TEXT/CF88_RUNTIME.txt (exatamente os bytes indexados no CF88_TEXT_MAP.IDX).
// Portavel (sem Arduino): o sketch fornece um LexV1Reader sobre fs::File; o PC fornece um sobre FILE* (teste host).
// Buffers fixos, busca binaria direto no arquivo, nenhum indice/payload inteiro em RAM. Qualquer inconsistencia -> FAIL CLOSED.

#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#ifndef LEX_DEVICE_V1_ENABLED
#define LEX_DEVICE_V1_ENABLED 0
#endif

#define LEXV1_KEY_MAX 48
#define LEXV1_LINE_MAX 256
#define LEXV1_TITLE_MAX 160
#define LEXV1_WINDOW 512
#define LEXV1_PAYLOAD_HEAD 512
#define LEXV1_RUNTIME_CF_PATH "/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt"
// Predeploy (V1-A2C): runtime canonico para o qual este candidato foi preparado. Informativo no diagnostico; a guarda de
// seguranca continua sendo tamanho+sha256 do arquivo exibido contra LEXV1.VER e o cabecalho do TEXT_MAP (fail closed).
#define LEXV1_PINNED_RUNTIME_BYTES 587133UL
#define LEXV1_PINNED_RUNTIME_SHA256 "7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a"
#define LEXV1_PINNED_TEXT_MAP_SHA256 "889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96"
// Contrato do overlay: versao EXATA do LEXV1.VER (#LEXMACHINA|DEVICE_VERSION|<n>). Deve ser igual a SCHEMA de
// DEVICE_INTEGRATION/tools/build_sd_staging.py (teste cruzado em test_a3b_prep.py). Qualquer outra versao -> FAIL_VERSION.
#define LEX_DEVICE_SCHEMA_VERSION 3
#define LEXV1_TARGETS_VERSION 3
#define LEXV1_TEXT_MAP_VERSION 2

enum LexV1Status {
  LEXV1_OK = 0,
  LEXV1_NOT_FOUND,                   // chave valida sem linha (ex.: target sem ENTENDA)
  LEXV1_FAIL_IO,                     // arquivo ausente/erro de leitura
  LEXV1_FAIL_HEADER,                 // cabecalho #LEXMACHINA|TIPO|versao desconhecido
  LEXV1_FAIL_LINE_TOO_LONG,
  LEXV1_FAIL_BAD_ROW,                // linha corrompida
  LEXV1_FAIL_OUT_OF_RANGE,           // OFFSET+BYTES fora do payload
  LEXV1_FAIL_PAYLOAD_ID,             // bloco nao comeca por @<EXPLANATION_ID> do lookup
  LEXV1_FAIL_TEXT_MAP_NOT_RUNTIME,   // mapa marcado como nao-runtime
  LEXV1_FAIL_SOURCE_MISMATCH,        // tamanho OU sha256 do texto exibido != SOURCE_BYTES/SOURCE_SHA256 do mapa
  LEXV1_FAIL_VERSION                 // LEXV1.VER invalido
};

enum LexV1Resolution { LEXV1_RES_NONE = 0, LEXV1_RES_DIRECT, LEXV1_RES_COVERED_BY_BLOCK };

struct LexV1Reader {
  virtual bool seek(uint32_t pos) = 0;
  virtual int read(uint8_t *buf, int n) = 0;   // bytes lidos (0 = EOF, <0 = erro)
  virtual uint32_t size() = 0;
  virtual uint32_t position() = 0;
  virtual ~LexV1Reader() {}
};

// ---------- utilitarios de linha/campo ----------

// Le uma linha (sem LF). Retorna comprimento, -1 em EOF sem dados, -2 se nao cabe no buffer (consome ate o LF).
static inline int lexv1ReadLine(LexV1Reader &r, char *buf, int cap)
{
  int n = 0; bool any = false; bool overflow = false;
  uint8_t c;
  while (r.read(&c, 1) == 1) {
    any = true;
    if (c == '\n') break;
    if (n + 1 < cap) buf[n++] = (char)c; else overflow = true;
  }
  buf[n] = '\0';
  if (!any) return -1;
  if (n > 0 && buf[n - 1] == '\r') buf[--n] = '\0';
  return overflow ? -2 : n;
}

static inline bool lexv1Field(const char *line, int idx, char *out, int cap)
{
  const char *p = line;
  for (int i = 0; i < idx; i++) { p = strchr(p, '|'); if (!p) { out[0] = '\0'; return false; } p++; }
  const char *e = strchr(p, '|');
  int n = e ? (int)(e - p) : (int)strlen(p);
  if (n >= cap) n = cap - 1;
  memcpy(out, p, n); out[n] = '\0';
  return true;
}

static inline int lexv1KeyCmp(const char *line, const char *key)
{
  // compara o primeiro campo (bytewise) com a chave
  size_t i = 0;
  for (;; i++) {
    unsigned char a = (unsigned char)line[i];
    if (a == '|' || a == '\0') a = 0;
    unsigned char b = (unsigned char)key[i];
    if (a != b) return (int)a - (int)b;
    if (a == 0) return 0;
  }
}

// ---------- indice ordenado ----------

struct LexV1Index {
  LexV1Reader *r = nullptr;
  uint32_t dataStart = 0;
  uint32_t fileSize = 0;
  char type[24] = {0};
  int version = 0;
  // cabecalhos usados pelo TEXT_MAP
  char runtimeStatus[40] = {0};
  uint32_t sourceBytes = 0;
  char sourceSha256[65] = {0};
  uint32_t adctStart = 0xFFFFFFFFu;
  uint32_t recordCount = 0;
};

static inline LexV1Status lexv1OpenIndex(LexV1Index &ix, LexV1Reader *r, const char *expectedType, int expectedVersion)
{
  ix = LexV1Index();
  ix.r = r;
  if (!r) return LEXV1_FAIL_IO;
  ix.fileSize = r->size();
  if (!r->seek(0)) return LEXV1_FAIL_IO;
  char line[LEXV1_LINE_MAX], f[LEXV1_TITLE_MAX];
  bool first = true;
  for (;;) {
    uint32_t start = r->position();
    int n = lexv1ReadLine(*r, line, sizeof(line));
    if (n == -2) return LEXV1_FAIL_LINE_TOO_LONG;
    if (n < 0 || line[0] != '#') { ix.dataStart = start; break; }
    lexv1Field(line + 1, 0, f, sizeof(f));
    if (first) {
      if (strcmp(f, "LEXMACHINA") != 0) return LEXV1_FAIL_HEADER;
      lexv1Field(line + 1, 1, ix.type, sizeof(ix.type));
      lexv1Field(line + 1, 2, f, sizeof(f));
      ix.version = atoi(f);
      first = false;
    } else if (strcmp(f, "RUNTIME_STATUS") == 0) {
      lexv1Field(line + 1, 1, ix.runtimeStatus, sizeof(ix.runtimeStatus));
    } else if (strcmp(f, "SOURCE_BYTES") == 0) {
      lexv1Field(line + 1, 1, f, sizeof(f)); ix.sourceBytes = (uint32_t)strtoul(f, nullptr, 10);
    } else if (strcmp(f, "SOURCE_SHA256") == 0) {
      lexv1Field(line + 1, 1, ix.sourceSha256, sizeof(ix.sourceSha256));
    } else if (strcmp(f, "RECORD_COUNT") == 0) {
      lexv1Field(line + 1, 1, f, sizeof(f)); ix.recordCount = (uint32_t)strtoul(f, nullptr, 10);
    } else if (strncmp(f, "NAMESPACE_START_ADCT", 20) == 0) {
      lexv1Field(line + 1, 1, f, sizeof(f)); ix.adctStart = (uint32_t)strtoul(f, nullptr, 10);
    }
  }
  if (first || strcmp(ix.type, expectedType) != 0 || ix.version != expectedVersion) return LEXV1_FAIL_HEADER;
  return LEXV1_OK;
}

// Busca binaria no arquivo: linha exata (floor=false) ou ultima linha com chave <= key (floor=true).
static inline LexV1Status lexv1Find(LexV1Index &ix, const char *key, char *out, int cap, bool floor, uint16_t *seeks = nullptr)
{
  LexV1Reader &r = *ix.r;
  uint32_t lo = ix.dataStart, hi = ix.fileSize;
  char line[LEXV1_LINE_MAX];
  uint16_t s = 0;
  while (hi - lo > LEXV1_WINDOW) {
    uint32_t mid = lo + (hi - lo) / 2;
    if (!r.seek(mid)) return LEXV1_FAIL_IO;
    s++;
    if (lexv1ReadLine(r, line, sizeof(line)) == -1) { hi = mid; continue; }   // descarta linha parcial
    uint32_t p = r.position();
    if (p >= hi) { hi = mid; continue; }
    int n = lexv1ReadLine(r, line, sizeof(line));
    if (n == -2) return LEXV1_FAIL_LINE_TOO_LONG;
    if (n < 0) { hi = mid; continue; }
    if (lexv1KeyCmp(line, key) < 0) lo = p; else hi = p;
  }
  if (!r.seek(lo)) return LEXV1_FAIL_IO;
  s++;
  bool havePrev = false;
  char prev[LEXV1_LINE_MAX];
  for (;;) {
    int n = lexv1ReadLine(r, line, sizeof(line));
    if (n == -2) return LEXV1_FAIL_LINE_TOO_LONG;
    if (n < 0) break;
    if (n == 0) continue;
    int c = lexv1KeyCmp(line, key);
    if (c == 0) { strncpy(out, line, cap - 1); out[cap - 1] = '\0'; if (seeks) *seeks = s; return LEXV1_OK; }
    if (c > 0) break;
    memcpy(prev, line, n + 1); havePrev = true;
    if (r.position() > hi + LEXV1_WINDOW) break;
  }
  if (seeks) *seeks = s;
  if (floor && havePrev) { strncpy(out, prev, cap - 1); out[cap - 1] = '\0'; return LEXV1_OK; }
  return LEXV1_NOT_FOUND;
}

// ---------- LEXV1.VER ----------

struct LexV1Version {
  int schemaVersion = -1;            // versao lida da 1a linha (mesmo quando rejeitada), para diagnostico
  char buildId[24] = {0};
  char gitCommit[48] = {0};
  uint16_t entendaCount = 0;
  uint16_t entendaPilots = 0;
  char textMapSourceSha256[65] = {0};
  uint32_t textMapSourceBytes = 0;
  char textMapRuntimeStatus[40] = {0};
  char runtimeCf[48] = {0};
  char runtimeCfPath[64] = {0};
  uint32_t runtimeCfBytes = 0;
  char runtimeCfSha256[65] = {0};
  char referenceEngine[48] = {0};
};

// 1a linha do LEXV1.VER: exatamente "#LEXMACHINA|DEVICE_VERSION|<n>" (n decimal, sem campos extras). Devolve n ou -1.
static inline int lexv1ParseDeviceVersionLine(const char *line)
{
  static const char prefix[] = "#LEXMACHINA|DEVICE_VERSION|";
  const size_t lp = sizeof(prefix) - 1;
  if (strncmp(line, prefix, lp) != 0) return -1;
  const char *d = line + lp;
  if (!*d || strlen(d) > 4) return -1;
  int n = 0;
  for (const char *c = d; *c; c++) {
    if (*c < '0' || *c > '9') return -1;
    n = n * 10 + (*c - '0');
  }
  return n;
}

static inline LexV1Status lexv1ReadVersion(LexV1Reader *r, LexV1Version &v)
{
  v = LexV1Version();
  if (!r || !r->seek(0)) return LEXV1_FAIL_IO;
  char line[LEXV1_LINE_MAX], k[40], val[96];
  int n = lexv1ReadLine(*r, line, sizeof(line));
  if (n < 0) return LEXV1_FAIL_VERSION;
  v.schemaVersion = lexv1ParseDeviceVersionLine(line);
  if (v.schemaVersion != LEX_DEVICE_SCHEMA_VERSION) return LEXV1_FAIL_VERSION;   // exatamente a versao do contrato, sem fallback
  while ((n = lexv1ReadLine(*r, line, sizeof(line))) >= 0) {
    if (n == 0 || line[0] == '#') continue;
    lexv1Field(line, 0, k, sizeof(k)); lexv1Field(line, 1, val, sizeof(val));
    if (!strcmp(k, "BUILD_ID")) strncpy(v.buildId, val, sizeof(v.buildId) - 1);
    else if (!strcmp(k, "GIT_COMMIT")) strncpy(v.gitCommit, val, sizeof(v.gitCommit) - 1);
    else if (!strcmp(k, "ENTENDA_COUNT")) v.entendaCount = (uint16_t)atoi(val);
    else if (!strcmp(k, "ENTENDA_PILOTS")) v.entendaPilots = (uint16_t)atoi(val);
    else if (!strcmp(k, "TEXT_MAP_SOURCE_SHA256")) strncpy(v.textMapSourceSha256, val, 64);
    else if (!strcmp(k, "TEXT_MAP_SOURCE_BYTES")) v.textMapSourceBytes = (uint32_t)strtoul(val, nullptr, 10);
    else if (!strcmp(k, "TEXT_MAP_RUNTIME_STATUS")) strncpy(v.textMapRuntimeStatus, val, sizeof(v.textMapRuntimeStatus) - 1);
    else if (!strcmp(k, "RUNTIME_CF")) strncpy(v.runtimeCf, val, sizeof(v.runtimeCf) - 1);
    else if (!strcmp(k, "RUNTIME_CF_PATH")) strncpy(v.runtimeCfPath, val, sizeof(v.runtimeCfPath) - 1);
    else if (!strcmp(k, "RUNTIME_CF_BYTES")) v.runtimeCfBytes = (uint32_t)strtoul(val, nullptr, 10);
    else if (!strcmp(k, "RUNTIME_CF_SHA256")) strncpy(v.runtimeCfSha256, val, 64);
    else if (!strcmp(k, "REFERENCE_ENGINE")) strncpy(v.referenceEngine, val, sizeof(v.referenceEngine) - 1);
  }
  if (!v.buildId[0] || v.entendaCount == 0) return LEXV1_FAIL_VERSION;
  return LEXV1_OK;
}

// ---------- target_id ----------

// ContextoJuridicoAtivo -> target_id canonico ("unico" -> PAR.UNICO).
static inline bool lexv1TargetFromContext(const char *ns, const char *artigo, const char *paragrafo, const char *inciso,
                                          const char *alinea, char *out, int cap)
{
  if (!artigo || !artigo[0]) return false;
  int n = snprintf(out, cap, "%s:ART.%s", ns, artigo);
  if (paragrafo && paragrafo[0]) n += snprintf(out + n, cap > n ? cap - n : 0, ":PAR.%s", strcmp(paragrafo, "unico") == 0 ? "UNICO" : paragrafo);
  if (inciso && inciso[0]) n += snprintf(out + n, cap > n ? cap - n : 0, ":INC.%s", inciso);
  if (alinea && alinea[0]) n += snprintf(out + n, cap > n ? cap - n : 0, ":AL.%s", alinea);
  return n > 0 && n < cap;
}

// TEXT_OFFSET -> target_id. Fail closed se o mapa nao for de runtime ou se tamanho OU sha256 (hex minusculo, calculado uma vez
// por boot sobre o arquivo exibido) nao corresponderem ao cabecalho do mapa.
static inline LexV1Status lexv1TargetAtOffset(LexV1Index &textMap, uint32_t displayedFileBytes, const char *displayedSha256Hex,
                                              uint32_t offset, char *tid, int cap)
{
  tid[0] = '\0';
  if (strcmp(textMap.runtimeStatus, "RUNTIME") != 0) return LEXV1_FAIL_TEXT_MAP_NOT_RUNTIME;
  if (textMap.sourceBytes == 0 || displayedFileBytes != textMap.sourceBytes) return LEXV1_FAIL_SOURCE_MISMATCH;
  if (!displayedSha256Hex || strlen(textMap.sourceSha256) != 64 || strcmp(displayedSha256Hex, textMap.sourceSha256) != 0)
    return LEXV1_FAIL_SOURCE_MISMATCH;
  char key[16], line[LEXV1_LINE_MAX];
  snprintf(key, sizeof(key), "%010lu", (unsigned long)offset);
  LexV1Status st = lexv1Find(textMap, key, line, sizeof(line), true);
  if (st != LEXV1_OK) return st;
  if (!lexv1Field(line, 2, tid, cap) || !tid[0]) return LEXV1_FAIL_BAD_ROW;
  return LEXV1_OK;
}

struct LexV1Target {
  char kind[20] = {0};
  char legalStatus[20] = {0};
  char flags[8] = {0};
};

static inline LexV1Status lexv1TargetInfo(LexV1Index &targets, const char *tid, LexV1Target &t)
{
  t = LexV1Target();
  char line[LEXV1_LINE_MAX];
  LexV1Status st = lexv1Find(targets, tid, line, sizeof(line), false);
  if (st != LEXV1_OK) return st;
  lexv1Field(line, 1, t.kind, sizeof(t.kind));
  lexv1Field(line, 2, t.legalStatus, sizeof(t.legalStatus));
  lexv1Field(line, 3, t.flags, sizeof(t.flags));
  return strlen(t.flags) == 6 ? LEXV1_OK : LEXV1_FAIL_BAD_ROW;
}

// ---------- ENTENDA ----------

struct LexV1Entenda {
  LexV1Resolution resolution = LEXV1_RES_NONE;
  char anchor[LEXV1_KEY_MAX] = {0};
  char explanationId[64] = {0};
  char title[LEXV1_TITLE_MAX] = {0};
  uint32_t offset = 0;
  uint32_t length = 0;
};

static inline LexV1Status lexv1Entenda(LexV1Index &lookup, LexV1Reader *payload, const char *tid, LexV1Entenda &e)
{
  e = LexV1Entenda();
  char line[LEXV1_LINE_MAX], f[64];
  LexV1Status st = lexv1Find(lookup, tid, line, sizeof(line), false);
  if (st != LEXV1_OK) return st;   // NOT_FOUND = target sem ENTENDA aprovado
  lexv1Field(line, 1, f, sizeof(f)); e.offset = (uint32_t)strtoul(f, nullptr, 10);
  lexv1Field(line, 2, f, sizeof(f)); e.length = (uint32_t)strtoul(f, nullptr, 10);
  lexv1Field(line, 3, e.explanationId, sizeof(e.explanationId));
  lexv1Field(line, 7, f, sizeof(f));
  if (!strcmp(f, "DIRECT")) e.resolution = LEXV1_RES_DIRECT;
  else if (!strcmp(f, "COVERED_BY_BLOCK")) e.resolution = LEXV1_RES_COVERED_BY_BLOCK;
  else return LEXV1_FAIL_BAD_ROW;
  if (!payload || e.length == 0 || e.offset + e.length > payload->size()) return LEXV1_FAIL_OUT_OF_RANGE;
  if (!payload->seek(e.offset)) return LEXV1_FAIL_IO;
  // so os metadados do inicio do bloco (T|, D|); as secoes sao lidas sob demanda pela UI
  uint32_t end = e.offset + e.length;
  int n = lexv1ReadLine(*payload, line, sizeof(line));
  if (n < 2 || line[0] != '@' || strcmp(line + 1, e.explanationId) != 0) return LEXV1_FAIL_PAYLOAD_ID;
  while (payload->position() < end && (n = lexv1ReadLine(*payload, line, sizeof(line))) >= 0) {
    if (n == -2) continue;
    if (line[0] == '#') break;
    if (line[0] == 'T' && line[1] == '|') strncpy(e.anchor, line + 2, sizeof(e.anchor) - 1);
    else if (line[0] == 'D' && line[1] == '|') strncpy(e.title, line + 2, sizeof(e.title) - 1);
  }
  if (!e.anchor[0]) return LEXV1_FAIL_BAD_ROW;
  return LEXV1_OK;
}

// ---------- Reference Engine ----------

struct LexV1Refs {
  uint32_t offset = 0;
  uint16_t count = 0;                // QUANTIDADE do REF_LOOKUP (inclui historicas ocultas)
  uint16_t parsed = 0;               // linhas do payload lidas e validadas (TARGET_ID igual, 7 campos)
  uint16_t visible = 0;              // VISIBILIDADE == CURRENT_VISIBLE
  uint32_t bytes = 0;
};

// Sem linha no REF_LOOKUP = zero referencias (LEXV1_OK, count 0). Payload lido so em leitura, linha a linha.
static inline LexV1Status lexv1References(LexV1Index &refLookup, LexV1Reader *payload, const char *tid, LexV1Refs &out)
{
  out = LexV1Refs();
  char line[LEXV1_LINE_MAX], f[40];
  LexV1Status st = lexv1Find(refLookup, tid, line, sizeof(line), false);
  if (st == LEXV1_NOT_FOUND) return LEXV1_OK;
  if (st != LEXV1_OK) return st;
  lexv1Field(line, 1, f, sizeof(f)); out.offset = (uint32_t)strtoul(f, nullptr, 10);
  lexv1Field(line, 2, f, sizeof(f)); out.count = (uint16_t)atoi(f);
  if (!payload || out.count == 0 || out.offset >= payload->size()) return LEXV1_FAIL_OUT_OF_RANGE;
  if (!payload->seek(out.offset)) return LEXV1_FAIL_IO;
  for (uint16_t i = 0; i < out.count; i++) {
    uint32_t p0 = payload->position();
    int n = lexv1ReadLine(*payload, line, sizeof(line));
    if (n < 0) return n == -2 ? LEXV1_FAIL_LINE_TOO_LONG : LEXV1_FAIL_BAD_ROW;
    out.bytes += payload->position() - p0;
    if (lexv1KeyCmp(line, tid) != 0) return LEXV1_FAIL_BAD_ROW;
    int bars = 0;
    for (const char *c = line; *c; c++) bars += (*c == '|');
    if (bars != 6) return LEXV1_FAIL_BAD_ROW;
    lexv1Field(line, 2, f, sizeof(f));
    if (!strcmp(f, "CURRENT_VISIBLE")) out.visible++;
    out.parsed++;
  }
  return LEXV1_OK;
}

static inline const char *lexv1StatusName(LexV1Status s)
{
  switch (s) {
    case LEXV1_OK: return "OK";
    case LEXV1_NOT_FOUND: return "NOT_FOUND";
    case LEXV1_FAIL_IO: return "FAIL_IO";
    case LEXV1_FAIL_HEADER: return "FAIL_HEADER";
    case LEXV1_FAIL_LINE_TOO_LONG: return "FAIL_LINE_TOO_LONG";
    case LEXV1_FAIL_BAD_ROW: return "FAIL_BAD_ROW";
    case LEXV1_FAIL_OUT_OF_RANGE: return "FAIL_OUT_OF_RANGE";
    case LEXV1_FAIL_PAYLOAD_ID: return "FAIL_PAYLOAD_ID";
    case LEXV1_FAIL_TEXT_MAP_NOT_RUNTIME: return "FAIL_TEXT_MAP_NOT_RUNTIME";
    case LEXV1_FAIL_SOURCE_MISMATCH: return "FAIL_SOURCE_MISMATCH";
    case LEXV1_FAIL_VERSION: return "FAIL_VERSION";
  }
  return "?";
}

static inline const char *lexv1ResolutionName(LexV1Resolution r)
{
  return r == LEXV1_RES_DIRECT ? "DIRECT" : r == LEXV1_RES_COVERED_BY_BLOCK ? "COVERED_BY_BLOCK" : "NONE";
}
