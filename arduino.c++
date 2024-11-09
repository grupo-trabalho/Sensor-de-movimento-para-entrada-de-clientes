int sensorPin = 2;
int sensorState = 0;
int lastSensorState = 0;
int count = 0;
int tempCount = 0;          // Contador temporário para pico
unsigned long startTime = 0; // Tempo inicial para o pico
const unsigned long peakInterval = 60000; // 1 minuto em milissegundos


void setup() {
  pinMode(sensorPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  sensorState = digitalRead(sensorPin);

  if (sensorState == HIGH && lastSensorState == LOW) {
    count++;
    tempCount++;
    Serial.print("Contagem de passagens: ");
    Serial.println(count);

    // Verifica se tempCount alcançou 5 dentro do tempo limite
    if (tempCount >= 5 && (millis() - startTime <= peakInterval)) {
      Serial.println("PICO DE MOVIMENTO DETECTADO!");
      tempCount = 0; // Reseta o contador temporário
      startTime = millis(); // Reseta o tempo inicial para o próximo pico
    }

    // Atualiza o tempo inicial no primeiro movimento detectado
    if (tempCount == 1) {
      startTime = millis();
    }
  }

  // Reseta o contador temporário após o intervalo de tempo
  if (millis() - startTime > peakInterval) {
    tempCount = 0;
  }

  lastSensorState = sensorState;
  delay(50);
}
