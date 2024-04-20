#include <Arduino.h>
#include "heltec.h"
#include "NeoPixelBus.h"
#include "NeoPixelAnimator.h"
#include "WiFi.h"
#include "ESPAsyncWebServer.h"
#include "secrets.h"

const char *ssid = WIFI_SSID;
const char *secret = WIFI_SECRET;
const int numLEDs = 36;
const int pinLED = 15;

NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> strip(numLEDs, pinLED);
AsyncWebServer server(80);

void setup()
{
  char status[512];

  // init serial
  Serial.begin(9600);
  Serial.println("Starting system ...");

  // init Display
  Heltec.begin(true, false, false);
  Heltec.display->init();

  // connect to wifi
  Serial.printf("Connecting to wifi %s ", ssid);
  WiFi.begin(ssid, secret);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.print("connected.");

  // display wifi status
  sprintf(status, "WiFi: %s\nIP: %s\n", WiFi.SSID(), WiFi.localIP().toString().c_str());
  Heltec.display->clear();
  Heltec.display->drawString(0, 0, status);
  Heltec.display->display();

  // init ws2812 and show default color
  strip.Begin();
  for (int i = 0; i < numLEDs; i++)
    strip.SetPixelColor(i, RgbColor(96, 32, 0));
  strip.Show();

  // config webserver
  server.on("/api/hue", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (request->hasArg("color"))
    {
      int r, g, b;
      sscanf(request->arg("color").c_str(), "%d,%d,%d", &r, &g, &b);
      if (request->hasArg("id")) {
        int i = request->arg("id").toInt();
        strip.SetPixelColor(i, RgbColor(r, g, b));
      } else {
        for (int i = 0; i < numLEDs; i++)
        {
          strip.SetPixelColor(i, RgbColor(r, g, b));
        }
      }
      strip.Show();
      request->send(200, "application/json", "{\"status\": 0}");      
    } else {
      request->send(400, "application/json", "{\"errmsg\": \"Missing color parameter\", \"status\": 400}");
    } });

  // start webserver
  server.begin();
}

void loop()
{
  int button = digitalRead(0);
  if (button == LOW)
  {
    for (int i = 0; i < numLEDs; i++)
    {
      strip.SetPixelColor(i, RgbColor(0, 0, 0));
    }
    strip.Show();
  }
}
