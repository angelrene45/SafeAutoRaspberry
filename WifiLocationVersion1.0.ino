#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include "WifiLocation.h" //Api de google Maps

//Conexion a WIFI
#define SSID "LabRedes" // SSID de tu red WiFi
#define PASSWD "987654312." // Clave de tu red WiFi

//Conexion y variables a SDK google maps
#define GOOGLE_KEY "AIzaSyCLVQxS6AmHRhs6jXt_N4rUG79-sFAyT90" // Clave API Google Geolocation
#define LOC_PRECISION 7 // Precisión de latitud y longitud

//Conexion a Firebase
#define HOSTFIREBASE "safeauto-65aa8.firebaseio.com"

// Llamada a la API de Google Maps para obtener la localizacion
WifiLocation location(GOOGLE_KEY);
location_t loc; // Estructura de datos que devuelve la librería WifiLocation



// Cliente WiFi
WiFiClientSecure client;

// Variables
byte mac[6];
String macStr = "2C:3A:E8:06:F6:D4";


void setup() {
  Serial.begin(115200);

  // connect to wifi.
  WiFi.begin(SSID, PASSWD);
  Serial.print("connecting");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("connected: ");
  Serial.println(WiFi.localIP());

}


void loop() {

  // Obtenemos la geolocalización WiFi
  loc = location.getGeoFromWiFi();

  // Hacemos la petición HTTP mediante el método PUT
  peticionPutFirebase();
  
  delay(1500);
}

void peticionPutFirebase(){
   // Cerramos cualquier conexión antes de enviar una nueva petición
  client.stop();
  client.flush();
  // Enviamos una petición por SSL
  if (client.connect(HOSTFIREBASE, 443)) {
    // Petición PUT JSON
     String toSend = "PUT /devices/";
    toSend += macStr+"/location";
    toSend += ".json HTTP/1.1\r\n";
    toSend += "Host:";
    toSend += HOSTFIREBASE;
    toSend += "\r\n" ;
    toSend += "Content-Type: application/json\r\n";
    String payload = "{\"lat\":";
    payload += String(loc.lat, LOC_PRECISION);
    payload += ",";
    payload += "\"lon\":";
    payload += String(loc.lon, LOC_PRECISION);
    payload += ",";
    payload += "\"prec\":";
    payload += String(loc.accuracy);
    payload += "}";
    payload += "\r\n";
    toSend += "Content-Length: " + String(payload.length()) + "\r\n";
    toSend += "\r\n";
    toSend += payload;
    Serial.println(toSend);
    client.println(toSend);
    client.println();
    client.flush();
    client.stop();
    Serial.println("Todo OK");
  } else {
    // Si no podemos conectar
    client.flush();
    client.stop();
    Serial.println("Algo ha ido mal");
  }
}
