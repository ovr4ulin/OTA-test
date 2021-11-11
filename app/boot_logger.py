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
    
    def __init__(self):
        self.LOG_NAME = 'update_firmware_from_sd_log.txt'
        self.SRC_LOG = '/{}'.format(self.LOG_NAME)
        self.DST_LOG = '/sd/{}'.format(self.LOG_NAME)
        self.BUFFER_SIZE = 1000

        self.create_log = True
        self.print_uart = True
        self.send_log_to_sd = True
            
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

        - Si <self.send_log_to_sd> == True: Envia archivo <self.LOG_NAME> ubicado en <self.SRC_LOG> a la ruta donde se encuentra
        montada la SD <self.DST_LOG>.
        """
        
        if not self.send_log_to_sd: return

        with open(self.SRC_LOG, 'rb') as src:
            with open(self.DST_LOG, 'wb') as dst:
                while True:
                    buf = src.read(self.BUFFER_SIZE)
                    if len(buf) > 0:
                        dst.write(buf)
                    if len(buf) < self.BUFFER_SIZE:
                        break
