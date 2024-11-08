#include <Wire.h>
#include <Adafruit_LiquidCrystal.h>

int contador = 0;
int pinosensor = 4;
int leitura; // Armazena o valor lido pelo sensor

Adafruit_LiquidCrystal lcd(0);

void setup() {
  Serial.begin(9600);

  // Define o pino do sensor como entrada
  pinMode(pinosensor, INPUT);

  // Inicializa o display com o endereço e tamanho
  lcd.begin(16, 2);
  lcd.setBacklight(1); // Liga a luz de fundo

  // Informações iniciais no display
  lcd.setCursor(0, 0);
  lcd.print("Sensor Prox. IR");
  lcd.setCursor(0, 1);
  lcd.print("Contador: 0");
}

void loop() {
  // Lê as informações do sensor de proximidade IR
  leitura = digitalRead(pinosensor);

  if (leitura != 1) { // Verifica se o objeto foi detectado
    // Incrementa o valor do contador
    

    // Mostra o valor do contador no Serial Monitor
    Serial.print("Contador : ");
    Serial.println(contador);

    // Atualiza o valor do contador no display
    lcd.setCursor(10, 1);
    lcd.print("    ");
    lcd.setCursor(10, 1);
    lcd.print(contador);
    contador++;

    // Loop caso o objeto pare em frente ao sensor
    while (digitalRead(pinosensor) != 1) {
      delay(100);
    }
  }
}
