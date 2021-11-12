#------------------------------------------------------------------
# boot.py
#------------------------------------------------------------------

############################# IMPORT #############################

def connect_wifi():
    import network
    import wifi
    from time import sleep
    sta_if = network.WLAN(network.STA_IF)
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
    print('network config:', sta_if.ifconfig())

def connectToWifiAndUpdate():
    import time, machine, gc
    time.sleep(1)
    print('Memory free', gc.mem_free())
    from ota_updater import OTAUpdater
    connect_wifi()
    token = "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"
    otaUpdater = OTAUpdater('https://github.com/ovr4ulin/OTA-test', headers={'Authorization': 'token {}'.format(token)}, main_dir='app')
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        machine.reset()
    else:
        del(otaUpdater)
        gc.collect()

def send_update_firmware_log_through_email():
    import umail
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
    smtp.login('tomasbalditrimaker@gmail.com', 'k42254216')
    smtp.to('tomasbalditrimaker@gmail.com')
    with open("/update_firmware_from_sd_log.txt") as file:
        for line in file:
            smtp.write(line)        
    smtp.send()
    smtp.quit()

def boot():
    # Actualizo el firmware por OTA si es que hay una nueva version
    try:
        #connectToWifiAndUpdate()
        print("Actualizando Ota")
    except Exception as e:
        print(e)

    # Actualizo el firmware por SD
    try:
        import app.firmware_updater_FSM as firmware_updater_FSM
        firmware_updater_FSM.start()
    except:
        connect_wifi()
        send_update_firmware_log_through_email()

    # Inicializo el firmware
    try:
        import app.current.main as main
        main.start_main()
    except Exception as e:
        print(e)

boot()