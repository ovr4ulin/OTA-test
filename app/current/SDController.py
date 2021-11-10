import machine
import uos
import time
from app.current.PrinterController import PrinterController


def singleton(cls):
    instances = dict()

    def wrap(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    
    return wrap


@singleton
class SDController:
    """
    This class is responsable for:

    - Mount SD card
    - Search ssid on SD card
    - Write log on SD card
    """

    def __init__(self):
        """
        This is the constructor of SDController objects, is responsible for:

        - Mount SD card
        
        Parameters:
        - None
        """

        print("\n>>> ------------------ SD INIT -----------------")
        time.sleep_ms(3000) # Wait for read logs into REPL

        try:
            self.is_SD = False
            self.ssid_sd = None
            self.password_sd = None
            self.files = None            
            self.__sd = machine.SDCard()

            print(">>> Mounting SD card...")
            uos.mount(self.__sd, '/sd');                    time.sleep_ms(100)
            uos.chdir('/sd');                               time.sleep_ms(100)
            self.files = uos.listdir();                     time.sleep_ms(100)
            print (">>> SD FILES: " + str(self.files));     time.sleep_ms(100)

            self.is_SD = True
            print(">>> SD Inicializada exitosamente...")

        except Exception as e:
            print(">>> No SD inserted ?: " + str(e))
            time.sleep_ms(3000)

    # ----------------------------------------------------------------------------------
    # METHODS AREA:
    # ----------------------------------------------------------------------------------

    def is_ssid_into_SD(self):
        """
        Looks for 'wifi_config.txt' to obtain SSID and password. 
        Returns tuple (self.ssid_sd , self.password_sd) or NONE if not file

        Parameters:
        - None
        
        Return:
        - Credentials <tuple> or <None>: tuple (self.ssid_sd , self.password_sd) or NONE if not file.
        """
        # Search 'wifi_config.txt' into SD
        for f in self.files:
            
            if f == 'wifi_config.txt':

                uos.chdir('/sd')

                with open('wifi_config.txt','r') as wifi_conf:

                    self.ssid_sd = wifi_conf.readline()
                    self.password_sd = wifi_conf.readline()

                    #Remove whitespace from the end 
                    self.ssid_sd     = self.ssid_sd.rstrip()
                    self.password_sd = self.password_sd.rstrip()

                    #Remove whitespace from the start
                    self.ssid_sd     = self.ssid_sd.lstrip()
                    self.password_sd = self.password_sd.lstrip()

                    return self.ssid_sd , self.password_sd
                
            # No wifi_config.txt in SD
            elif f == self.files[-1] and not self.ssid_sd:        # Last element in list 
                print ("\n>>> No wifi configuration file into SD card...\n")
                return False

    def save_wifi_log(self, result="success_connection"):
        """
        Use this function to give feedback to user of the entered configuration_wifi.txt file saved into SD card.
        It save into SD "WIFI_CONFIG_OK.txt" or "wifi_config_ERROR.txt"
        Remmember that this file contains the SSID and wifi pasword.

        Results availables:
        - 'success_connection'
        - 'wrong_ssid'
        - 'wrong_password'

        Parameters:
        - Result <str> <defult = "success_connection">: Result of connection 
        
        Return:
        - None
        """
        
        self.PrinterController = PrinterController()

        try:
            if result == "success_connection":
                # Delete 'wifi_config.txt' file from SD and create new file called 'WIFI_CONFIG_OK.txt'

                uos.chdir('/sd')
                time.sleep_ms(100)
                log_file = open('/sd/WIFI_CONFIG_OK.txt','w')            # Add new file with process response
                time.sleep_ms(100)
                log_file.write("TRIMAKER Nebula dice: Wifi configurado exitosamente...!!!")
                time.sleep_ms(100)
                log_file.close()
                time.sleep_ms(100)

                uos.remove('/sd/wifi_config.txt')               # Delete original user wifi_config file
                time.sleep_ms(100)
                uos.chdir('/')
                time.sleep_ms(100)
            
            elif result == "wrong_ssid" or result == "wrong_password":
                
                uos.chdir('/sd')
                uos.rename('/sd/wifi_config.txt', '/sd/wifi_config_ERROR.txt')  # Change original name to 'wifi_config.txt'
                time.sleep_ms(100)
                file = open('/sd/wifi_config_ERROR.txt','a')            # Append message to new file with process failure
                time.sleep_ms(100)
                
                if result == "wrong_ssid":
                    file.write("\n\nTRIMAKER Nebula dice: El NOMBRE de la RED es INCORRECTO, verifique los datos. NO se pudo conectar a WIFI. ")
                elif result == "wrong_password":
                    file.write("\n\nTRIMAKER Nebula dice: El PASSWORD es INCORRECTO, verifique los datos. NO se pudo conectar a WIFI. ")
                
                time.sleep_ms(100)
                file.close()
                time.sleep_ms(100)
                uos.chdir('/')
                time.sleep_ms(100)

                # ESCRIBIR EN UART EL MISMO MENSAJE
                print("Conexion Fallida. Credenciales Incorrectas")
                self.PrinterController.send_command("M117 Conexion Fallida. Credenciales Incorrectas\n")

        except Exception as e:
            print(">>> SD log could not be saved: " + str(e))
            time.sleep_ms(3000)



        




