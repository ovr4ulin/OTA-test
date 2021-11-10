import machine
import time

from app.current.SDController import SDController as SDCont
from app.current.config import Config



class SSID_PASSW:

    def __init__(self):
        self.ssid_pass_source = None
        self.__sta_if = None
        self.__SSID = 0
        self.__SSID_KEYS = ['ssid_0','ssid_1','ssid_2','ssid_3','ssid_4']
        self.__settings_flash = Config().load_config('networks')    # Get stored SSIDs and passwords into flash

    def __available_nets(self):
        """
        Scans the WiFi networks and returns a list with them.

        Parameters:
        - None
        
        Return:
        - NETS <list of tuples>: (b'Trimaker Router', b'$\xf5\xa2\xe9nV', 1, -50, 4, False)
        """
        nets = self.__sta_if.scan() 

        print("\n>>> Available Networks:")
        time.sleep_ms(1000)

        for net in nets:
            ssid_scanned = str(net[self.__SSID].decode("utf-8"))
            print (">>> " + ssid_scanned)
            time.sleep_ms(50)
            
        time.sleep_ms(3000)
        print("\n")

        return nets
        
    def __are_ssids_in_nets(self, ssids, nets):
        """
        Search if any ssid in <SSIDS> are in <NETS>, and return dictionary key in which is the name of the networks.

        Parameters:
        - SSIDS <dictionary>: {ssid0:password0, ssid1:password1, ssid2:password2, ssid3:password3, ssid4:password4}
        - NETS <list of tuples>: [(b'Trimaker Router', b'$\xf5\xa2\xe9nV', 1, -50, 4, False) ...]
        
        Return:
        - DICTIONARY_KEY <str>: Returns the dictionary key in which is the name of the networks found in nets. If not found return None
        """
        for index , ssid_key in enumerate(self.__SSID_KEYS):                
            print(">>> Checking stored SSID_" + str(index) + ": " + ssids[ssid_key] )
            time.sleep_ms(200)          # Used to read REPL
        
            for net in nets:
                ssid_scanned = str(net[self.__SSID].decode("utf-8"))
                # Searching ssid into networks avaible scanned
                if ssid_scanned == ssids[ssid_key]:
                    return ssid_key
        
        return None

    def __is_ssid_in_nets(self, ssid , nets):
        """
        Search if <SSID> is in <NETS>, if has, return <SSID>, else return False.

        Parameters:
        - SSID <str>: Is an string with the name of the net to find into nets
        - NETS <list of tuples>: [(b'Trimaker Router', b'$\xf5\xa2\xe9nV', 1, -50, 4, False) ...]
        
        Return:
        - SSID or False
        """
        for net in nets:
            ssid_scanned = str(net[self.__SSID].decode("utf-8"))
            # If ssid into avaible scanned networks
            if ssid_scanned == ssid:
                return ssid

        return False

    def __get_password(self, ssid_key):
        """
        Search password saved in memory flash associate to ssid_key, and return it.

        Parameters:
        - SSID_KEY <str>: Is the string key of the dictionary where passwords and ssids are stored
        
        Return:
        - PASSWORD <str>: Returns an string with the password 
        """
        index = ssid_key.split('_')
        password = self.__settings_flash[ 'password_'+ index[1] ]
        
        return password
    
    def get_from_SD(self, sta_if):
        """
        Search wifi credentials file on SD, return ssid and password saved in this file.

        Parameters:
        - SSID_IF <object>: WLAN network interface object.
        
        Return:
        - CREDENTIALS <tuple>: (ssid, password) /// None
        """
        self.__sta_if = sta_if
        self.SDCont = SDCont()
        nets = self.__available_nets()

        if self.SDCont.is_SD:                                           # Is inserted any SD ?
            self.__settings_sd = self.SDCont.is_ssid_into_SD()          # If is inserted, is there any wifi_confi.txt file ? If yes, return tuple with ssid and pass
            
            if self.__settings_sd:
                ssid      = self.__settings_sd[0]
                password  = self.__settings_sd[1]

                # Case where ssid is wrong
                if not self.__is_ssid_in_nets(ssid,nets):
                    self.SDCont.save_wifi_log('wrong_ssid')
                    return None
                
                else:
                    self.ssid_pass_source = 'SD'
                    print(">>> SD source credentials found")
                    print(">>> SSID    : " + ssid )
                    print(">>> Password: " + password )
                    return (ssid , password)    # Retun tuple with ssid & password
            
            else:
                return None
        
        else:
            return None


    def get_from_FLASH(self, sta_if):
        # -----------------------------------------------------
        # 2 - Get SSID and password from flash memory
        # -----------------------------------------------------

        self.__sta_if = sta_if
        nets = self.__available_nets()

        # Check if exist any ssids readed from flash in scannes networks
        ssid_key = self.__are_ssids_in_nets( self.__settings_flash , nets)    
        
        if ssid_key:
            ssid      = self.__settings_flash[ssid_key]
            password  = self.__get_password(ssid_key)
            self.ssid_pass_source = 'FLASH'
            print("\n>>> FLASH source credentials")
            print(">>> SSID    : " + ssid )
            print(">>> Password: " + password )
            return (ssid , password)    # Retun tuple with ssid & password
        
        else:
            return None