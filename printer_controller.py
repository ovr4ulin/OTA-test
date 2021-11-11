#------------------------------------------------------------------
# PrinterController.py
#------------------------------------------------------------------

############################# IMPORT ##############################

import machine

######################## PRINTERCONTROLLER ########################

class PrinterController(object):
    """
    Esta clase permite inicializar, recibir y enviar mensajes a traves de la UART.
    """

    def __init__(self):
        self.__BAUDRATE = 115200                    
        self.__UART_NUMBER = 1
        self.__BITS = 8
        self.__PARITY = None
        self.__STOP = 1
        self.__PIN_TX = 13
        self.__PIN_RX = 12
        self.__IS_BUSY = False
        self.__RXBUF = 1024
        self.__TXBUF = 1024
        self.__UART = machine.UART(
            self.__UART_NUMBER,
            self.__BAUDRATE,
            tx=self.__PIN_TX,
            rx=self.__PIN_RX,
            rxbuf=self.__RXBUF,
            txbuf=self.__TXBUF
            )
        try:
            self.__UART.init(
                self.__BAUDRATE,
                self.__BITS,
                self.__PARITY,
                self.__STOP                               
                )                   
            print(">>> UART succesfully initialized")
        except:
            print(">>> Something went south with UART init call MacGyver")

    def send_command(self, command):
        """
        Envia <command> a traves de la UART. 

        Args:
            command (str): Cadena de texto para enviar a traves de la UART.
        """

        written_chars = self.__UART.write(command)
        print(">>> Written chars to UART = {} / message = {}".format(written_chars, command))

    def kill(self):
        """
        Cierra la comunicacion a traves de la UART
        """

        self.__UART.deinit()