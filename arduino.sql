#include <SPI.h>
#include <Ethernet.h>

// Definindo os pinos aos quais os sensores PIR estão conectados
const int sensorEntradaPin = 10; // Sensor de entrada conectado ao pino 10
const int sensorSaidaPin = 9;    // Sensor de saída conectado ao pino 9

// Inicializando os contadores
int contadorEntrada = 0;
int contadorSaida = 0;

// Variáveis para rastrear o estado anterior dos sensores
int estadoAnteriorEntrada = LOW;
int estadoAnteriorSaida = LOW;

// Configuração de rede
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };  // MAC Address do Arduino
IPAddress ip(192, 168, 1, 177);                        // IP fixo do Arduino
EthernetServer server(80);                             // Servidor na porta 80

void setup() {
  // Inicializa a comunicação serial
  Serial.begin(9600);
  // Define os pinos dos sensores como entrada
  pinMode(sensorEntradaPin, INPUT);
  pinMode(sensorSaidaPin, INPUT);
  
  // Inicializa a Ethernet
  Ethernet.begin(mac, ip);
  server.begin();  // Inicia o servidor
  Serial.print("Servidor Ethernet iniciado em: ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  // Verifica se o sensor de entrada foi acionado
  int estadoAtualEntrada = digitalRead(sensorEntradaPin);
  if (estadoAtualEntrada == HIGH && estadoAnteriorEntrada == LOW) {
    contadorEntrada++;
    Serial.print("Entrada detectada: ");
    Serial.println(contadorEntrada);
  }
  estadoAnteriorEntrada = estadoAtualEntrada;

  // Verifica se o sensor de saída foi acionado
  int estadoAtualSaida = digitalRead(sensorSaidaPin);
  if (estadoAtualSaida == HIGH && estadoAnteriorSaida == LOW) {
    contadorSaida++;
    Serial.print("Saída detectada: ");
    Serial.println(contadorSaida);
  }
  estadoAnteriorSaida = estadoAtualSaida;

  // Atende clientes conectados
  EthernetClient client = server.available();
  if (client) {
    Serial.println("Cliente conectado");
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n' && currentLineIsBlank) {
          // Envia a resposta HTTP ao cliente
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          client.println("<head><title>Arduino Ethernet</title></head>");
          client.println("<body>");
          client.println("<h1>Status do Sensor PIR</h1>");
          client.println("<p>Entrada: " + String(contadorEntrada) + "</p>");
          client.println("<p>Saída: " + String(contadorSaida) + "</p>");
          client.println("</body></html>");
          break;
        }
        if (c == '\n') {
          currentLineIsBlank = true;
        } else if (c != '\r') {
          currentLineIsBlank = false;
        }
      }
    }
    delay(1);
    client.stop();
    Serial.println("Cliente desconectado");
  }
}
