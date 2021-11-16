#------------------------------------------------------------------
# boot.py
#------------------------------------------------------------------

def connect_wifi():
    import network
    import wifi
    from time import sleep
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected(): return True
    for SSID, PASSWORD in wifi.WIFI_CREDENTIALS:
        if not SSID: continue
        if sta_if.isconnected(): break
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        counter = 0
        while not sta_if.isconnected() and counter < 10:
            counter += 1 
            sleep(1)
    if sta_if.isconnected(): 
        print('network config:', sta_if.ifconfig())
        return True
    return False
    
def connectToWifiAndUpdate():
    import time, machine, gc
    time.sleep(1)
    print('Memory free', gc.mem_free())
    from ota_updater import OTAUpdater
    connect_wifi()
    otaUpdater = OTAUpdater('https://github.com/ovr4ulin/OTA-test', main_dir='app')
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        machine.reset()
    else:
        del(otaUpdater)
        gc.collect()

def boot():
    # Actualizo el firmware por OTA si es que hay una nueva version
    try:
        #connectToWifiAndUpdate()
        pass

    except Exception as e:
        import boot_logger
        print(e)
        ota_logger = boot_logger.BootLogger("/ota_update_log.txt")
        ota_logger.log_write_exception(e)

        if connect_wifi():
            ota_logger.send_log_through_http()
        else:
            ota_logger.write_log_on_sd()

    # Actualizo el firmware por SD
    try:
        pass
        #import app.firmware_updater_FSM as firmware_updater_FSM
        #firmware_updater_FSM.start()

    except Exception as e:
        import boot_logger
        print(e)
        sd_update_logger = boot_logger.BootLogger("/sd_update_log.txt")
        sd_update_logger.log_write_exception(e)

        if connect_wifi():
            sd_update_logger.send_log_through_http()
        else:
            sd_update_logger.write_log_on_sd()

    # Inicializo el firmware
    try:
        import app.current.main as main
        main.start_main()

    except Exception as e:
        import os
        print(os.getcwd())
        import boot_logger
        print(e)
        main_logger = boot_logger.BootLogger("/main_log.txt")
        main_logger.log_write_exception(e)

        if connect_wifi():
            main_logger.send_log_through_http()
        else:
            main_logger.write_log_on_sd()

boot()