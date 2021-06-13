from umqtt.robust import MQTTClient
import machine as m
import machine, onewire, time, max30100
from machine import Pin
from time import sleep
from machine import I2C
import ssd1306


ubidotsToken = "BBFF-0kXKM5Xt4hg2I6cALmQt2WxLvBuQWL"

clientID = "myclient1"

client = MQTTClient("clientID", "industrial.api.ubidots.com", 1883, user = ubidotsToken, password = ubidotsToken)
# ESP32 Pin assignment 
sda=Pin(4)
scl=Pin(5)          
i2c = I2C(scl=scl,sda=sda)

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

print('Scanning I2C devices...')
print(i2c.scan())

sensor = max30100.MAX30100(i2c=i2c)

print('Reading MAX30100 registers...')
print(sensor.get_registers())

sensor.enable_spo2()
#sensor.set_mode(max30100.MODE_SPO2)

def checkwifi():

    while not sta_if.isconnected():

        time.sleep_ms(500)

        print(".")

        sta_if.connect()

pin13 = m.Pin(13, m.Pin.IN, m.Pin.PULL_UP)

def publish(spo2,heartrate):

  checkwifi()

  client.connect()

  lat = "17.3850"

  lng = "78.4867"

  var = repr(pin13.value())

  msg = b'{"location": {"value":%s, "context":{"lat":%s, "lng":%s}}, "SPO2": {"value":%s, "context":{"name" : "John"}}, "Heartrate": {"value":%s, "context":{"name" : "John"}}}' % (var, lat, lng, spo2, heartrate)

  print(msg)

  client.publish(b"/v1.6/devices/oxygen-monitor", msg)

  time.sleep(2)
  read_sensors()

def read_sensors():
  print('Reading sensor...')
  while True:
    sensor.read_sensor()
    #print(sensor.ir, sensor.red)
    rawspo2 = sensor.ir
    rawheartrate = sensor.red
    spo2 = rawspo2/100
    heartrate = rawheartrate/200
    if spo2 > 100 :
      spo2 = 99.9
    elif spo2 < 93.0 and spo2 > 50.0 :
      spo2 = 93.0
    elif spo2 < 49 :
      spo2 = 0.0
    else :
      spo2 = spo2

    if heartrate > 130 :
      heartrate = 150
    elif heartrate < 65 and heartrate > 50 :
      heartrate = 65.0
    elif heartrate < 49 :
      heartrate = 0.0
    else :
      heartrate = heartrate
    
    print(spo2, heartrate)
    break
  spo2_string = str(spo2)
  heartrate_string = str(heartrate)
  oled.fill(0)
  oled.show()
  oled.text('Pulse Oximeter', 0, 0)
  oled.text('SpO2 %', 0, 20)
  oled.text(spo2_string, 64, 20)
  oled.text('Heart Rate', 0, 40)
  oled.text(heartrate_string, 85, 40)
  oled.text('by EI', 60, 55)
  oled.show()
    
  publish(spo2,heartrate)

read_sensors()