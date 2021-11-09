import machine
import time

flash = machine.Pin(4, machine.Pin.OUT)

while True:
    flash.off()
    time.sleep(1)
    flash.on()
    time.sleep(1)
