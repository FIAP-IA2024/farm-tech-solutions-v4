/*
  Comparativo entre código base e código modificado.
  Abaixo está o código atualizado e com comentários de otimização colocados diretamente
  nas linhas modificadas em relação ao código base fornecido.

  Apenas as linhas que sofreram otimizações de memória
  (uso de PROGMEM, uso de F(),alteração de tipos de variaveis float para int,
  e remoção de String) terão comentários.
  */

// Linhas normais de includes
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <pgmspace.h> // [Otimização: inclusão para uso de PROGMEM]

// Definição dos pinos
#define pinoDHT 12
#define botaoP 23
#define botaoK 22
#define pinoLDR 14
#define pinoRele 27
#define ledP 17
#define ledK 16

// Constantes do LDR (pH)
const float GAMMA = 0.7065;
const float RL10 = 85.0;

// Variáveis globais
int umidade = 0;         // [Otimização: alteração de float para int]
int umidadeMin = 40;     // [Otimização: alteração de float para int]
int temperatura = 0;     // [Otimização: alteração de float para int]
int temperaturaMax = 30; // [Otimização: alteração de float para int]
float valorPH = 0.0;

// Definição do sensor DHT
#define tipoDHT DHT22
DHT dht(pinoDHT, tipoDHT);

// LCD
LiquidCrystal_I2C lcd(0x27, 20, 4);

bool estadoSensorP = false;
bool estadoSensorK = false;

unsigned long tempoUltimaLeituraP = 0;
unsigned long tempoUltimaLeituraK = 0;
unsigned long atrasoDebounce = 200;

unsigned long tempoUltimaLeitura = 0;
unsigned long intervaloLeitura = 2000;

// Controle da irrigação
unsigned long tempoIrrigacao = 0;
unsigned long tempoInicioIrrigacao = 0;
bool irrigacaoAtiva = false;

unsigned long ultimaAtualizacaoTempoRestante = 0;
unsigned long intervaloAtualizacao = 1000;
int tempoRestante = 0;

// Variável String removida, antes havia: String ultimoEstadoIrrigacao;
// [Otimização: remoção da variável String para evitar uso de heap e fragmentação]

// Armazenamento de textos no PROGMEM
const char linhaInicial[] PROGMEM = "Inicializando...";    // [Otimização: texto no PROGMEM]
const char estadoLigada[] PROGMEM = "Ligada ";             // [Otimização: texto no PROGMEM]
const char estadoDeslig[] PROGMEM = "Deslig.";             // [Otimização: texto no PROGMEM]
const char estadoOn[] PROGMEM = "ON";                      // [Otimização: texto no PROGMEM]
const char estadoOff[] PROGMEM = "OFF";                    // [Otimização: texto no PROGMEM]
const char linhaNPK[] PROGMEM = "NPK (P):%-5s(K):%-5s   "; // [Otimização: texto no PROGMEM]
const char linhaIrrig[] PROGMEM = "Irrigacao: %-7s      "; // [Otimização: texto no PROGMEM]
const char linhaRepouso[] PROGMEM = "Sistema em Repouso "; // [Otimização: texto no PROGMEM]

void setup()
{
  Serial.begin(9600);
  dht.begin();

  Wire.begin(21, 19);
  lcd.init();
  lcd.backlight();

  pinMode(botaoP, INPUT_PULLUP);
  pinMode(botaoK, INPUT_PULLUP);
  pinMode(pinoRele, OUTPUT);
  pinMode(ledP, OUTPUT);
  pinMode(ledK, OUTPUT);

  digitalWrite(pinoRele, LOW);
  digitalWrite(ledP, LOW);
  digitalWrite(ledK, LOW);

  char bufferInicial[21];
  strcpy_P(bufferInicial, linhaInicial); // [Otimização: leitura de texto do PROGMEM]
  lcd.setCursor(0, 0);
  lcd.print(bufferInicial);
}

void loop()
{
  unsigned long tempoAtual = millis();

  if (tempoAtual - tempoUltimaLeitura >= intervaloLeitura)
  {
    tempoUltimaLeitura = tempoAtual;

    lerSensorDHT22();
    lerSensorLDR();

    tempoIrrigacao = calcularTempoIrrigacao(estadoSensorP, estadoSensorK, valorPH, temperatura);

    if (umidade < umidadeMin && (estadoSensorP || estadoSensorK) && !irrigacaoAtiva)
    {
      digitalWrite(pinoRele, HIGH);
      irrigacaoAtiva = true;
      tempoInicioIrrigacao = millis();
      Serial.println(F("Irrigacao LIGADA")); // [Otimização: uso de F()]
    }

    enviarDadosSerialPlotter();
  }

  if (irrigacaoAtiva)
  {
    tempoRestante = (tempoIrrigacao - (millis() - tempoInicioIrrigacao)) / 1000;
    if (millis() - tempoInicioIrrigacao >= tempoIrrigacao)
    {
      digitalWrite(pinoRele, LOW);
      irrigacaoAtiva = false;
      tempoRestante = 0;
      Serial.println(F("Irrigacao DESLIGADA")); // [Otimização: uso de F()]
    }
  }

  debounceBotao(botaoP, estadoSensorP, tempoUltimaLeituraP);
  debounceBotao(botaoK, estadoSensorK, tempoUltimaLeituraK);

  digitalWrite(ledP, estadoSensorP ? HIGH : LOW);
  digitalWrite(ledK, estadoSensorK ? HIGH : LOW);

  updateLCD();
}

void lerSensorDHT22()
{
  umidade = dht.readHumidity();
  temperatura = dht.readTemperature();

  if (isnan(umidade) || isnan(temperatura))
  {
    Serial.println(F("Falha ao ler o DHT!")); // [Otimização: uso de F()]
    umidade = 0;
    temperatura = 0;
  }
}

void lerSensorLDR()
{
  int analogValue = analogRead(pinoLDR);
  float voltage = analogValue / 4095.0 * 3.3;

  if (voltage >= 3.3)
  {
    voltage = 3.29;
  }

  float resistance = 5000 * voltage / (1 - voltage / 3.3);
  int valorLDR = (int)pow(RL10 * 1000 * pow(10, GAMMA) / resistance, (1 / GAMMA));

  valorPH = ((float)valorLDR * 20.0) / 100000.0;

  if (isnan(valorPH) || valorPH < 0.0f || valorPH > 20.0f)
  {
    Serial.println(F("Erro na leitura do sensor de pH!")); // [Otimização: uso de F()]
    valorPH = 10.0f;
  }
}

void debounceBotao(int pinoBotao, bool &estadoSensor, unsigned long &tempoUltimaLeitura)
{
  int leitura = digitalRead(pinoBotao);
  if (leitura == LOW)
  {
    if ((millis() - tempoUltimaLeitura) > atrasoDebounce)
    {
      estadoSensor = !estadoSensor;
      tempoUltimaLeitura = millis();
    }
  }
}

unsigned long calcularTempoIrrigacao(bool sensorP, bool sensorK, float valorPH, float temperatura)
{
  unsigned long tempoBase = 5000;
  if (sensorP)
    tempoBase += 2000;
  if (sensorK)
    tempoBase += 2000;

  if (valorPH < 5.5)
  {
    tempoBase += 1000;
  }
  else if (valorPH > 7.5)
  {
    tempoBase -= 1000;
  }

  if (temperatura > temperaturaMax)
    tempoBase += 2000;

  return tempoBase;
}

void enviarDadosSerialPlotter()
{
  int estadoIrrigacaoValor = digitalRead(pinoRele) == HIGH ? 1 : 0;

  // [Otimização: uso de F() para todas as strings do Serial]
  Serial.print(F("Temperatura: "));
  Serial.print(temperatura);
  Serial.print("\t");
  Serial.print(F("Umidade: "));
  Serial.print(umidade);
  Serial.print("\t");
  Serial.print(F("pH: "));
  Serial.print(valorPH);
  Serial.print("\t");
  Serial.print(F("Fosforo: "));
  Serial.print(estadoSensorP);
  Serial.print("\t");
  Serial.print(F("Potassio: "));
  Serial.print(estadoSensorK);
  Serial.print("\t");
  Serial.print(F("Irrig: "));
  Serial.print(estadoIrrigacaoValor);
  Serial.print("\t");
  Serial.print(F("TempoRestante: "));
  Serial.println(tempoRestante);
}

void updateLCD()
{
  char line0[21];
  char line1[21];
  char line2[21];
  char line3[21];

  // pH com 1 casa decimal, mantém float apenas para exibição
  snprintf(line0, 21, "T:%2dC H:%3d%% pH:%2.1f",
           (int)temperatura,
           (int)umidade,
           valorPH);

  char npkStr[30];
  strcpy_P(npkStr, linhaNPK); // [Otimização: texto do PROGMEM, copiado com strcpy_P]

  char estadoPBuf[6];
  if (estadoSensorP)
  {
    strcpy_P(estadoPBuf, estadoOn); // [Otimização: texto no PROGMEM]
  }
  else
  {
    strcpy_P(estadoPBuf, estadoOff); // [Otimização: texto no PROGMEM]
  }

  char estadoKBuf[6];
  if (estadoSensorK)
  {
    strcpy_P(estadoKBuf, estadoOn); // [Otimização: texto no PROGMEM]
  }
  else
  {
    strcpy_P(estadoKBuf, estadoOff); // [Otimização: texto no PROGMEM]
  }

  snprintf(line1, 21, npkStr, estadoPBuf, estadoKBuf);

  char irrStr[30];
  strcpy_P(irrStr, linhaIrrig); // [Otimização: texto no PROGMEM]

  char estadoIrrigacaoBuf[8];
  if (digitalRead(pinoRele) == HIGH)
  {
    strcpy_P(estadoIrrigacaoBuf, estadoLigada); // [Otimização: texto no PROGMEM]
  }
  else
  {
    strcpy_P(estadoIrrigacaoBuf, estadoDeslig); // [Otimização: texto no PROGMEM]
  }

  snprintf(line2, 21, irrStr, estadoIrrigacaoBuf);

  if (irrigacaoAtiva)
  {
    snprintf(line3, 21, "Tempo Restante:%2ds", tempoRestante);
    int len = (int)strlen(line3);
    for (int i = len; i < 20; i++)
      line3[i] = ' ';
    line3[20] = '\0';
  }
  else
  {
    char repousoBuf[21];
    strcpy_P(repousoBuf, linhaRepouso); // [Otimização: texto no PROGMEM]
    snprintf(line3, 21, "%s", repousoBuf);
  }

  lcd.setCursor(0, 0);
  lcd.print(line0);
  lcd.setCursor(0, 1);
  lcd.print(line1);
  lcd.setCursor(0, 2);
  lcd.print(line2);
  lcd.setCursor(0, 3);
  lcd.print(line3);
}