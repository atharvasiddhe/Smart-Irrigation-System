#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN 4        // DHT11 sensor pin
#define DHTTYPE DHT11   
#define MOISTURE_PIN 34 // Soil moisture sensor pin
#define PUMP_PIN 5      // Relay module for pump

const char* ssid = "DESKTOP-FDVFAKP 7854";  
const char* password = "2g#9H210";
const char* serverURL = "http://192.168.153.226:5000/update_data";  // Flask server IP

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  Serial.println("\n🌐 Connecting to WiFi...");

  WiFi.begin(ssid, password);
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);  // Ensure pump is OFF initially
  
  dht.begin();

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    retries++;
    if (retries > 15) {  // Give up after 15 seconds
      Serial.println("\n❌ WiFi Connection Failed! Restart ESP32.");
      return;
    }
  }

  Serial.println("\n✅ Connected to WiFi!");
  Serial.print("📶 ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int moisture = analogRead(MOISTURE_PIN);

    Serial.println("\n📡 Reading Sensors...");
    Serial.print("🌡️ Temperature: "); Serial.println(temperature);
    Serial.print("💧 Humidity: "); Serial.println(humidity);
    Serial.print("🌱 Soil Moisture: "); Serial.println(moisture);

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("⚠️ Sensor Read Error! Skipping this cycle.");
      return;
    }

    String postData = "temperature=" + String(temperature) + 
                      "&humidity=" + String(humidity) + 
                      "&moisture=" + String(moisture);

    Serial.println("📤 Sending Data to Flask Server...");
    Serial.println("🔄 Data: " + postData);
    
    int httpResponseCode = http.POST(postData);
    
    Serial.print("📡 HTTP Response Code: ");
    Serial.println(httpResponseCode);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("✅ Server Response: ");
      Serial.println(response);
      
      if (response == "ON") {
        digitalWrite(PUMP_PIN, HIGH); 
        Serial.println("💦 Pump Turned ON");
      } else {
        digitalWrite(PUMP_PIN, LOW);  
        Serial.println("💧 Pump Turned OFF");
      }
    } else {
      Serial.println("❌ Server Not Responding! Check Flask or IP.");
    }

    http.end();
  } else {
    Serial.println("⚠️ WiFi Disconnected! Trying to reconnect...");
    WiFi.begin(ssid, password);
  }

  delay(5000);  // Wait 5 seconds before sending next data
}
