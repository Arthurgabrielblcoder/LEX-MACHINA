# Auditoria — tela BRANCA no repouso (2026-10-26)

Somente auditoria: nenhum firmware foi modificado, compilado ou gravado. O aparelho continua com o candidato `22367f3` (`1bb3deb0…`).

## Sintoma
Após ~3 min sem interação, a tela fica **branca** (antes, com a tela antiga, ficava escura). Ao apertar uma tecla, a legislação volta normalmente.

## Rotina de repouso (candidato `candidate_painel/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`)
- `TIMEOUT_TELA_MS = 180000UL` (linha 680); `displayApagado` / `pedirAcordarDisplay` (682–683).
- `registrarAtividadeUsuario()` (687–697): a tecla que acorda serve **apenas** para acordar (é consumida).
- `atualizarInatividadeDisplay()` (5375–5389):
  - **entrar em repouso:** `displayApagado=true; definirDisplayLigado(false);`
  - **acordar:** `definirDisplayLigado(true); redesenharTelaAtual(); displayApagado=false;`
- `definirDisplayLigado()` (5352–5358): envia **apenas** `ILI9341_DISPOFF (0x28)` ao apagar e `ILI9341_DISPON (0x29)` ao acordar, depois `aplicarBacklight()`.
- `aplicarBacklight()` (5347–5350): **vazio**. O comentário diz "Nesta montagem o backlight esta no 3V3: nao tocar em nenhum GPIO".
  Não há nenhum `#define` de pino de LED ou backlight no firmware.
- Não há `SLPIN (0x10)`, `fillScreen` nem mudança de MADCTL no repouso.

## Comparação com o firmware anterior
`aplicarBacklight`, `definirDisplayLigado` e `redesenharTelaAtual` são **idênticos** no aprovado `f7e6b190` (Content V2) e no candidato.
O patch do painel (`painel.patch`) não tocou nessas rotinas. **A regressão não é de código: é do painel.**

## Causa provável
- `DISPOFF` desliga a saída da GRAM para o vidro, e o controlador passa a mostrar uma "página em branco".
  A cor que essa página assume depende do tipo de cristal líquido:
  - **tela antiga:** precisava de `INVON` para mostrar preto e verde, comportamento típico de painel IPS/"normally black".
    Com DISPOFF, os pixels sem tensão ficavam **escuros**;
  - **tela vermelha:** mostra cores corretas com `INVOFF` e já ficou **branca** quando o controlador não estava inicializado (RST errado no GPIO8),
    comportamento típico de painel TN **"normally white"**. Com DISPOFF, os pixels sem tensão ficam **brancos**.
- O backlight está ligado direto no 3,3 V (sem GPIO). Em nenhum dos dois casos a luz desligava: na tela antiga, o "apagado" era só
  o cristal bloqueando a luz.
- **MADCTL 0x40 não tem relação:** DISPOFF/DISPON não dependem da orientação, e o reset e as cores não interferem.
  `SLPIN` também não resolveria: em painel normally white, ele também resulta em branco.

## Apagar pixels × desligar a iluminação
- **Apagar pixels (software):** pintar a GRAM de preto com o display ligado. O cristal bloqueia a luz e a tela fica preta, mas o
  backlight continua aceso (TN deixa algum brilho residual, e o consumo do LED continua).
- **Desligar a iluminação (hardware):** exige que o pino LED do módulo seja comandado por um GPIO, com transistor/MOSFET se a corrente pedir.
  Hoje não existe esse controle; seria uma alteração elétrica, fora do escopo desta etapa.

## Menor correção proposta (uma função, sem mexer em orientação, cores, reset ou timeout)
```cpp
void definirDisplayLigado(bool ligado)
{
  // Tela vermelha (TN, normally white): DISPOFF mostra BRANCO. Repouso = GRAM preta com o display ligado.
  // O despertar ja chama redesenharTelaAtual() (atualizarInatividadeDisplay), entao a GRAM nao precisa ser preservada.
  if(ligado) tft.sendCommand(ILI9341_DISPON);
  else tft.fillScreen(COR_FUNDO);   // COR_FUNDO = ILI9341_BLACK
  aplicarBacklight(ligado);
}
```
- `fillScreen` cobre 320×240 (geometria do `Adafruit_ILI9341_PainelLex`) em ~31 ms a 40 MHz. O despertar não muda: DISPON (inócuo) e redesenho completo, como hoje.
- O retorno imediato pelo teclado é preservado: a primeira tecla continua sendo consumida só para acordar.

## Riscos
1. **Desenho durante o repouso ficaria visível.** Com DISPOFF, qualquer desenho feito enquanto `displayApagado` era invisível; com a GRAM preta e o display
   ligado, ele apareceria. Auditoria: as entradas durante o repouso são consumidas por `registrarAtividadeUsuario()`; o rodapé dinâmico checa
   `!displayApagado`; os callbacks BLE (`onConnected`/`onDisconnected`) não desenham; o touch FT6336U não está presente. Não foi encontrado desenho
   em segundo plano, mas uma corrida rara (tecla processada no mesmo ciclo do timeout) poderia pintar um trecho até a próxima tecla.
2. **Backlight continua aceso** no repouso (consumo do LED e leve brilho do preto). Só o hardware resolve.
3. **Flashes brancos curtos em transições:** `desenharTransicaoSplash()` (2797–2804) e o boot usam DISPOFF enquanto desenham. Na tela vermelha,
   isso aparece como um breve **branco** (algumas dezenas de ms) em vez de escuro. Não faz parte desta correção; pode ser tratado depois, se incomodar.

## Teste reversível proposto (após aprovação)
1. Gerar `candidate_painel_repouso/` pelo builder (uma 7ª edição só em `definirDisplayLigado`), compilar com o FQBN aprovado e rodar os `--check`.
2. Backup do app0 e das regiões protegidas → gravar **só app0** → readback byte a byte → conferir boot, tabela e otadata.
3. No aparelho: aguardar 3 min sem tocar → a tela deve ficar **preta**, não branca → apertar uma tecla → a legislação volta, sem ação extra.
   Repetir na tela de pastas, no leitor e numa camada (ENTENDER, correlatas).
4. Rollback (só app0): regravar `candidate_painel/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin` (`1bb3deb0…`, versionado).
