import machine, network, time, urequests
from machine import Pin, I2C, ADC
from MQ2 import MQ2
from aht10 import AHT10
from bmp180 import BMP180
import time

busI2C = I2C(1,scl=Pin(22),sda=Pin(21),freq=100000) # CREAMOS UN BUS I2C PARA LOS SENSORES
bmp180 = BMP180(busI2C) # INSTANCIAMOS LA CLASE BMP180
bmp180.oversample_sett = 2
aht10 = AHT10(busI2C) # INSTANCIAMOS LA CLASE AHT10

pinDigital = Pin(14, Pin.IN)  # CONFIGURAMOS EL PIN DE ENTRADA DIGITAL MQ2
pinAnalogo = Pin(34, Pin.IN) # CONFIGURAMOS EL PIN DE ENTRADA ANALOGO MQ2
mq2 = MQ2(pinAnalogo)

LedRojo = Pin(19, Pin.OUT) # CONFIGURAMOS LEDS DE ADVERTENCIA
LedAmar = Pin(18, Pin.OUT)
LedRojo.off()
LedAmar.off()

ssid = 'UNAL'
password = ''
url = "https://api.thingspeak.com/update?api_key=UKWS0R5RMD7VFX6Z&field1=0" 

red = network.WLAN(network.STA_IF)

red.active(True)
red.connect(ssid,password)

while red.isconnected() == False:
  pass

print('Conexión correcta')
print(red.ifconfig())

ultima_peticion = 0
intervalo_peticiones = 30

def reconectar():
    print('Fallo de conexión. Reconectando...')
    time.sleep(10)
    machine.reset()
    
# Función para leer la entrada digital del sensor MQ2
def leer_entrada_digital_mq2():
    return pinDigital.value()

while True:
    try:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
            temp = round((bmp180.temperature + aht10.temperature())/2, 1) # OBTENEMOS TEMPERATURA ACTUAL (C)
            pres = round((bmp180.pressure)/100, 1) # OBTENEMOS PRESION ACTUAL (hPa)
            hume = round(aht10.humidity(), 1) # OBTENEMOS PORCENTAJE DE HUMEDAD ACTUAL (%)
            ppm = mq2.readSmoke() # OBTENEMOS PPM DE CO ACTUAL (ppm)
            humo = leer_entrada_digital_mq2() # OBTENEMOS PRESENCIA DE HUMO (1: No, 0: Si)
            print("Temperatura: "+str(temp)+"\nPresion: "+str(pres)+"\nHumedad: "+str(hume)+"\nPPM: "+str(ppm)+"\nPresencia de humo: "+str(humo))
            if humo == 1:
                LedAmar.on()
                LedRojo.off()
            else:
                LedAmar.off()
                LedRojo.on()
            respuesta = urequests.get(url + "&field1=" + str(temp) + "&field2=" + str(pres) + "&field3=" + str(hume) + "&field4=" + str(ppm) + "&field5=" + str(humo))
            print ("Respuesta: " + str(respuesta.status_code))
            respuesta.close ()
            ultima_peticion = time.time()
    except OSError as e:
        reconectar() 