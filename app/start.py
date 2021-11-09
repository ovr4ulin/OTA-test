import machine
import time

flash = machine.Pin(4, machine.Pin.OUT)

while True:
    print("Hola Maxi")
    flash.off()
    time.sleep(0.5)
    flash.on()
    time.sleep(0.5)
    flash.off()
    print("Chau Maxi")
    time.sleep(2)
    flash.on()
    time.sleep(2)
