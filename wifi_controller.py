import boot_logger
import machine
import uos
import ujson

class WifiController:

    def __init__(self):
        self.boot_logger = boot_logger.BootLogger("upload_wifi_credentials.txt")
        self.SD_MOUNT_PATH = "/sd"
        self.SD_FILENAME = "wifi_credentials.txt"
        self.SD_FILENAME_READY = "wifi_credentials.ready"
        self.FILENAME_WIFI_CREDENTIALS = "wifi.json"

    def upload_wifi_credentials(self):
        try:
            self.files = None
            self.sd = machine.SDCard()
            self.boot_logger.log_write(">>> Mounting SD card on {}".format(self.SD_MOUNT_PATH))
            uos.mount(self.sd, self.SD_MOUNT_PATH)
            self.boot_logger.log_write(">>> SD mounted successfully")
            self.files = uos.listdir(self.SD_MOUNT_PATH)
            self.boot_logger.log_write(">>> '{}' files: ".format(self.SD_MOUNT_PATH) + str(self.files))

            if not self.SD_FILENAME in self.files:
                self.boot_logger.log_write(">>> Credentials not found on sd")
                self.boot_logger.log_write(">>> Unmounting SD")
                uos.umount(self.SD_MOUNT_PATH)
                return
            
            self.boot_logger.log_write(">>> Credentials found on SD")
            self.append_wifi_credentials()
        except Exception as e:
            self.boot_logger.log_write_exception(e)
            self.boot_logger.log_write(">>> No SD inserted")

    def append_wifi_credentials(self):
        credentials_sd = None
        credentials_json = None

        self.boot_logger.log_write(">>> Reading credentials file on SD")

        with open("{}/{}".format(self.SD_MOUNT_PATH, self.SD_FILENAME), "r") as sd_file:
            lines = sd_file.readlines()
            ssid = lines[0].rstrip()
            password = lines[1].rstrip()
            credentials_sd = (ssid, password)

        uos.rename("{}/{}".format(self.SD_MOUNT_PATH, self.SD_FILENAME), "{}/{}".format(self.SD_MOUNT_PATH, self.SD_FILENAME_READY))

        uos.umount(self.SD_MOUNT_PATH)
        self.boot_logger.log_write(">>> Unmounting SD")
        self.boot_logger.log_write(">>> Reading json file")
        
        with open("/{}".format(self.FILENAME_WIFI_CREDENTIALS), "r") as json_file:
            credentials_json = ujson.load(json_file)
            credentials_json.insert(0, credentials_sd)
            credentials_json = credentials_json[:-1]

        self.boot_logger.log_write(">>> Writing json file")

        with open("/{}".format(self.FILENAME_WIFI_CREDENTIALS), "w") as json_file:
            ujson.dump(credentials_json, json_file)

    def get_credentials(self):
        with open("/{}".format(self.FILENAME_WIFI_CREDENTIALS), "r") as json_file:
            credentials_json = ujson.load(json_file)
            return credentials_json