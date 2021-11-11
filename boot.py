#------------------------------------------------------------------
# boot.py
#------------------------------------------------------------------

############################# IMPORT #############################

def connectToWifiAndUpdate():
    import time, machine, network, gc, secrets
    time.sleep(1)
    print('Memory free', gc.mem_free())
    from ota_updater import OTAUpdater

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    otaUpdater = OTAUpdater('https://github.com/ovr4ulin/OTA-test', main_dir='app')
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        machine.reset()
    else:
        del(otaUpdater)
        gc.collect()

def boot():
    # Actualizo el firmware por OTA si es que hay una nueva version
    connectToWifiAndUpdate() 
    # Actualizo el firmware por SD
    import app.firmware_updater_FSM as firmware_updater_FSM
    firmware_updater_FSM.start()
    # Inicializo el firmware
    import app.current.main as main
    main.start_main()

boot()