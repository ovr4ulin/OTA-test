import machine
import time

flash = machine.Pin(4, machine.Pin.OUT)

while True:
    print("Hola Mati")
    flash.off()
    time.sleep(0.5)
    flash.on()
    time.sleep(0.5)
    flash.off()
    print("Hola Mati")
    time.sleep(2)
    flash.on()
    time.sleep(2)
