#------------------------------------------------------------------
# boot.py
#------------------------------------------------------------------

############################# IMPORT #############################

import firmware_updater_FSM
import app.main
import machine

############################## BOOT ##############################

led_rojo = machine.Pin(14, machine.Pin.OUT)
led_rojo.off()

firmware_updater_FSM.start()
app.main.start_main()