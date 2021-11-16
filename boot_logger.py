#------------------------------------------------------------------
# boot_logger.py
#------------------------------------------------------------------

############################ IMPORT ##############################

import uos

########################### BOOTLOGGER ###########################

class BootLogger:
    """
    Esta clase genera permite generar, almacenar e imprimir los logs.

    - Si <create_log> == True: Cuando se llame al metodo <log_write> se escribira el log generado en el archivo <LOG_NAME> ubicado en <SRC_LOG>.
    - Si <print_uart> == True: Cuando se llame al metodo <log_write> se imprimira por UART el log generado.
    - Si <send_log_to_sd> == True: Cuando se llame al metodo <write_log_on_sd> el archivo <LOG_NAME> sera enviado a <DST_LOG>.
    """
    
    def __init__(self, log_name):
        self.LOG_NAME = log_name
        self.SRC_LOG = '/{}'.format(self.LOG_NAME)
        self.DST_LOG = '/sd/{}'.format(self.LOG_NAME)
        self.POST_URL = 'https://www.trimaker.com/send_log.php'
        self.BUFFER_SIZE = 1000

        self.create_log = True
        self.print_uart = True
        self.send_log_to_sd = True

        # Crea el archivo log en caso de no existir    
        with open(self.SRC_LOG, "a+"):
            pass
            
    def log_write(self, message):
        """
        Este metodo varia su funcionamiento en base al estado de dos variables <self.create_log> y <self.print_uart>.

        - Si <self.create_log> == True: Escribe <message> en el archivo <self.LOG_NAME> ubicado en <self.SRC_LOG>.
        - Si <self.print_uart> == True: Imprime <message> a traves de la UART.

        Args:
            message (str): Mensaje para ser enviado a traves de la UART y almacenado en el archivo <self.LOG_NAME>, dependiendo
            el estado de las variables <self.create_log> y <self.print_uart>
        """

        if self.create_log == True:
            log_file = open(self.SRC_LOG, 'a')
            log_file.write('{} \n'.format(message))
            log_file.close()
        
        if self.print_uart == True:
            print(message)

    def log_write_exception(self, e):
        """
        Este metodo escribe en el log el detalle de la expecion pasada por argumento
        """
        import sys

        if self.create_log == True:
            with open(self.SRC_LOG, 'a') as log_file:
                sys.print_exception(e, log_file)

    def log_clear(self):
        """
        Este metodo elimina en caso de existir el archivo <self.LOG_NAME> con el path <self.SRC_LOG>.
        """

        try:
            uos.remove(self.SRC_LOG)
        except:
            pass

    def write_log_on_sd(self):
        """
        Este metodo varia su funcionamiento en base al estado de la variable <self.send_log_to_sd>.

        Envia archivo <self.LOG_NAME> ubicado en <self.SRC_LOG> a la ruta donde se encuentra
        montada la SD <self.DST_LOG>.
        """
        
        if not self.send_log_to_sd: return

        try:
            with open(self.SRC_LOG, 'rb') as src:
                with open(self.DST_LOG, 'wb') as dst:
                    while True:
                        buf = src.read(self.BUFFER_SIZE)
                        if len(buf) > 0:
                            dst.write(buf)
                        if len(buf) < self.BUFFER_SIZE:
                            break

        except Exception as e:
            # En caso de saltar alguna excepcion la imprimo
            print("Error al escribir el log {} en la sd".format(self.SRC_LOG))
            print(e)

    def send_log_through_http(self):
        """
        Envia el log generado junto a la mac en un post-request a <self.POST_URL>
        """
        try:
            import httpclient
            import machine
            
            # Instancio el cliente http
            client = httpclient.HttpClient()

            # Abro el log y lo guardo en una variable
            with open(self.SRC_LOG) as file:
                log_list = file.readlines()
                log_str = "".join(log_list)
            
            # Obtengo la MAC
            unique_id = machine.unique_id()
            list_mac = [x for x in str(unique_id) if x.isalpha() or x.isdigit()]
            str_mac = ''.join(list_mac)
            
            # Posteo la MAC y el log en la pagina correspondiente
            client.post(self.POST_URL, json={"uuid":str_mac,"log":log_str})
        
        except Exception as e:
            # En caso de saltar alguna excepcion la imprimo
            print("Error al enviar el log {} por http".format(self.SRC_LOG))
            print(e)
