import network
import time
import utime
import ujson

from app.current.Network_Credentials_Manager import SSID_PASSW
from app.current.config import Config
from app.current.PrinterController import PrinterController
from app.current.SDController import SDController
from app.current import AP_server

# ----------------------------------------------------------------------------------
# VARIABLES AREA:
# ----------------------------------------------------------------------------------

sta_if = None
ssid = None
password = None
end_state_flag = None
first_conn = None                           
source = None
state = None

# ----------------------------------------------------------------------------------
# STATES AREA:
# ----------------------------------------------------------------------------------
class AccessPoint():
    def __init__(self):
        pass

    def process(self):
        global source
        global ssid
        global password

        ssid, password = AP_server.iniciar_servidor()

        source = "AP"
        result = STAConnect()

        return result

class save_wifi_certif:

    def __init__(self):
        pass

    def process(self):
        global source
        global ssid
        global password

        self.config = Config()

        print("\n>>> FSM-STATE: save_wifi_certif")
        print(">>> ssid     = " + str(ssid))
        print(">>> password = " + str(password))
        print(">>> source   = " + str(source))

        # Anti-coder way to save to flash priority SSID connection
        if source == "SD" or source == "AP":

            self.networks = self.config.load_config('networks')

            self.config.save_config( 'ssid_4' , self.networks['ssid_3'])
            self.config.save_config( 'ssid_3' , self.networks['ssid_2'])
            self.config.save_config( 'ssid_2' , self.networks['ssid_1'])
            self.config.save_config( 'ssid_1' , self.networks['ssid_0'])
            self.config.save_config( 'ssid_0' , ssid)
            
            self.config.save_config( 'password_4' , self.networks['password_3'])
            self.config.save_config( 'password_3' , self.networks['password_2'])
            self.config.save_config( 'password_2' , self.networks['password_1'])
            self.config.save_config( 'password_1' , self.networks['password_0'])
            self.config.save_config( 'password_0' , password)
        
        result = End_State()

        return result


class logging:

    def __init__(self):
        pass

    def process(self):
        global source
        global sta_if

        self.sta_if = sta_if
        self.PrinterController = PrinterController()
        self.SDController = SDController()

        print("\n>>> FSM-STATE: logging")
        print(">>> source   = " + str(source))
        print(">>> sta_if   = " + str(type(sta_if)))

        if self.sta_if.isconnected():
           
            if source == "SD":
                self.PrinterController.send_command("M117 Conectada a WIFI\n")  # LCD logging
                self.SDController.save_wifi_log("success_connection")    # SD logging
                print(">>> Connected using SD certificates")
                result = save_wifi_certif()

                return result
                
            elif source == "FLASH":
                self.PrinterController.send_command("M117 Conectada a WIFI\n")
                print(">>> Connected using FLASH certificates")
                result = End_State()

                return result

            elif source == "AP":
                self.PrinterController.send_command("M117 Conectada a WIFI\n")
                print(">>> Connected using AP certificates")
                result = save_wifi_certif()

                return result

            else: 
                source == "VARIABLE"
                print(">>> REConnected using input VARIABLE certificates")
                result = End_State()

                return result
        
        else:
            if source == "SD":
                # Writes log message in UART.
                self.PrinterController.send_command("M117 ERROR:Sin conexion\n")  # LCD logging
                self.SDController.save_wifi_log("wrong_password")
                print(">>> Wrong password from SD")
                result = End_State()

                return result

            elif source == "FLASH":
                self.PrinterController.send_command("M117 ERROR:Sin conexion...\n")  # LCD logging
                print(">>> Wrong password from FLASH. Password has changed?")
                result = End_State()

                return result

            elif source == "AP":
                self.PrinterController.send_command("M117 ERROR:Sin conexion...\n")  # LCD logging
                print(">>> Wrong password from AP. Password has changed?")
                result = AccessPoint()

                return result

            else:
                source == "VARIABLE"
                self.PrinterController.send_command("M117 ERROR:Sin conexion...\n")  # LCD logging
                print(">>> Maybe poor wifi signal strength")
                result = End_State()

                return result

class STAConnect:
    def __init__(self):
        global sta_if
        global ssid
        global password
        global source

        self.ssid = ssid
        self.password = password
        self.sta_if = sta_if

        print("\n>>> FSM-STATE: STAConnect")
        print(">>> ssid     = " + str(ssid))
        print(">>> password = " + str(password))
        print(">>> source   = " + str(source))
        print(">>> sta_if   = " + str(type(sta_if)) + "\n")

    def process(self):
        start = utime.time()
        timed_out = False
        self.sta_if.active(True)
        self.sta_if.connect(self.ssid, self.password)
        self.PrinterController = PrinterController()
        self.PrinterController.send_command("M117 Conectando...")

        while self.sta_if.status() == network.STAT_CONNECTING and not timed_out:   

            if utime.time() - start >= 20:      
                timed_out = True

            utime.sleep_ms(1000)
            print(">>> Waiting for connection: " + str(utime.time() - start) + " seg ...")
        
        result = logging()

        return result
        
      
class SSID_FLASH:
    def __init__(self):
        pass

    def process(self):
        global sta_if
        global ssid
        global password
        global source

        self.SSID_Passw =  SSID_PASSW()
        self.__ssid_passw = self.SSID_Passw.get_from_FLASH(sta_if)

        print("\n>>> FSM-STATE: SSID_FLASH")
        print(">>> ssid     = " + str(ssid))
        print(">>> password = " + str(password))
        print(">>> source   = " + str(source))
        print(">>> sta_if   = " + str(type(sta_if)))

        if self.__ssid_passw:
            ssid     = self.__ssid_passw[0]
            password = self.__ssid_passw[1]
            source   = "FLASH"
            result = STAConnect()

            return result

        else:
            ssid     = None
            password = None
            source   = None 
            result = AccessPoint()

            return result

            
class SSID_SD:
    def __init__(self):
        pass

    def process(self):
        global sta_if
        global ssid
        global password
        global source

        self.SSID_Passw =  SSID_PASSW()
        self.__ssid_passw = self.SSID_Passw.get_from_SD(sta_if)

        print("\n>>> FSM-STATE: SSID_SD")
        print(">>> ssid     = " + str(ssid))
        print(">>> password = " + str(password))
        print(">>> source   = " + str(source))
        print(">>> sta_if   = " + str(type(sta_if)))

        if self.__ssid_passw:
            ssid     = self.__ssid_passw[0]
            password = self.__ssid_passw[1]
            source   = "SD"
            result = STAConnect()

            return result

        else:
            ssid     = None
            password = None
            source   = None
            result = SSID_FLASH()

            return result


class Check_First_Connection:
    def __init__(self):
        pass

    def process(self):
        """
        # Case where we have to look for ssid & password from SD, then FLASH and at end AP Web server
        # This case is when the ESP32 have been connected and lose it's connection, so it is retrying to connect to know ssid & passwords
        # In the case of self.first_conn == False, then the source where you get the ssid & password is from mqtt_as stored variables
        """

        global first_conn
        global source

        self.first_conn = first_conn

        print("\n>>> FSM-STATE: Check_First_Connection")
        print(">>> first_conn = " + str(first_conn))
        print(">>> source     = " + str(source))

        if self.first_conn == True:
            print(">>> is first_connection...")
            result = SSID_SD()      

            return result

        else:
            print(">>> not first_connection...")
            source = "VARIABLE"       
            result = STAConnect()

            return result


class End_State:
    def __init__(self):
        pass
             

    def process(self): 
        global end_state_flag

        print("\n>>> FSM-STATE: End_State")
       
        end_state_flag = True


def start(network_object , ssid_in , password_in, first_connection):
    global state
    global sta_if 
    global ssid 
    global password 
    global first_conn 

    global end_state_flag 
    global source 

    sta_if = network_object
    ssid = ssid_in
    password = password_in
    first_conn = first_connection

    print(">>>> FIRST CONNECTION: " + str(first_conn))

    end_state_flag = False
    source = None

    state = Check_First_Connection()

    while True:
        state = state.process()
        if end_state_flag == True:
            return ssid , password