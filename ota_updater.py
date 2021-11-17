#------------------------------------------------------------------
# ota_updater.py
#------------------------------------------------------------------

############################# IMPORT ##############################

import os, gc
from time import sleep
from httpclient import HttpClient
import boot_logger

########################### OTA UPDATER ############################

class OTAUpdater:
    """
    A class to update your MicroController with the latest version from a GitHub tagged release,
    optimized for low power usage.
    """

    def __init__(self, github_repo, github_src_dir='', module='', main_dir='main', new_version_dir='next', secrets_file=None, headers={}):
        self.http_client = HttpClient(headers=headers)
        self.github_repo = github_repo.rstrip('/').replace('https://github.com/', '')
        self.github_src_dir = '' if len(github_src_dir) < 1 else github_src_dir.rstrip('/') + '/'
        self.module = module.rstrip('/')
        self.main_dir = main_dir
        self.old_main_dir = "{}_old".format(main_dir)
        self.new_version_dir = new_version_dir
        self.secrets_file = secrets_file
        self.logger = boot_logger.BootLogger("/ota_update_log.txt")

    def __del__(self):
        self.http_client = None

    # ------------------------ UPDATE FUNCTIONS ------------------------

    def check_for_update_to_install_during_next_reboot(self) -> bool:
        """Function which will check the GitHub repo if there is a newer version available.
        
        This method expects an active internet connection and will compare the current 
        version with the latest version available on GitHub.
        If a newer version is available, the file 'next/.version' will be created 
        and you need to call machine.reset(). A reset is needed as the installation process 
        takes up a lot of memory (mostly due to the http stack)

        Returns
        -------
            bool: true if a new version is available, false otherwise
        """

        (current_version, latest_version) = self._check_for_new_version()
        self.logger.log_write("Current_version = {}".format(current_version))
        self.logger.log_write("Latest_version = {}".format(latest_version))
        if latest_version > current_version:
            self.logger.log_write('New version available')
            self._create_new_version_file(latest_version)
            return True

        self.logger.log_write('New version not available')

        return False

    def install_update_if_available_after_boot(self, ssid, password) -> bool:
        """This method will install the latest version if out-of-date after boot.
        
        This method, which should be called first thing after booting, will check if the 
        next/.version' file exists. 

        - If yes, it initializes the WIFI connection, downloads the latest version and installs it
        - If no, the WIFI connection is not initialized as no new known version is available
        """

        if self.new_version_dir in os.listdir(self.module):
            if '.version' in os.listdir(self.modulepath(self.new_version_dir)):
                latest_version = self.get_version(self.modulepath(self.new_version_dir), '.version')
                print('New update found: ', latest_version)
                OTAUpdater._using_network(ssid, password)
                self.install_update_if_available()
                return True
            
        print('No new updates found...')
        return False

    def install_update_if_available(self) -> bool:
        """
        Instala inmediatamente la nueva version en caso de existir.
        Para ejecutar este metodo se requiere conexion a internet.
        Es necesario correr este metodo inmediatamente luego de bootear el microcontrolador (por razones de memoria).

        Returns:
            bool: booleano que indica si una nueva version fue instalada
        """

        # Obtiene la version actual y la correspondiente al ultimo release de github
        (current_version, latest_version) = self._check_for_new_version()

        if latest_version > current_version:
            self.logger.log_write('> Updating to version {}'.format(latest_version))
            import uart_controller
            uart = uart_controller.UartController()
            
            # Envia tres M198 A para indicar por pantalla que se esta actualizando el firmware
            sleep(1)
            uart.send_command("M198 A\n")
            self.logger.log_write('> Send M198 A to printer')
            sleep(0.1)
            uart.send_command("M198 A\n")
            self.logger.log_write('> Send M198 A to printer')
            sleep(0.1)
            uart.send_command("M198 A\n")
            self.logger.log_write('> Send M198 A to printer')
    
            self._create_new_version_file(latest_version)
            self._download_new_version(latest_version)
            self._copy_secrets_file()
            self._rename_old_version()
            self._install_new_version()            
            self._delete_old_version()

            # Envia tres M198 D para quitar el cartel de "Actualizando" de la pantalla
            uart.send_command("M198 D\n")
            self.logger.log_write('> Send M198 D to printer')
            sleep(0.1)
            uart.send_command("M198 D\n")
            self.logger.log_write('> Send M198 D to printer')
            sleep(0.1)
            uart.send_command("M198 D\n")
            self.logger.log_write('> Send M198 D to printer')
            sleep(0.1)
            
            uart.kill()
            return True
            
        return False

    # ----------------------------- STATES -----------------------------

    @staticmethod
    def _using_network(ssid, password):
        """
        Intenta conectar a la red <ssid> con la contraseña <password>.

        Args:
            ssid (str): Cadena de texto con el nombre de la red wifi
            password (str): Cadena de texto con la contraseña de la red wifi.
        """
        import network
        sta_if = network.WLAN(network.STA_IF)

        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(ssid, password)
            while not sta_if.isconnected():
                pass

        print('network config:', sta_if.ifconfig())

    def _check_for_new_version(self): 
        """
        Obtiene la version actual y la ultima version del repositorio y las devuelve en forma de tupla.

        Returns:
            tuple: Tupla con ambas versiones (version actual, ultima version repositorio).
        """        
        self.logger.log_write('>>> STATE: Check for new version')

        current_version = self.get_version(self.modulepath(self.main_dir))
        latest_version = self.get_latest_version()
    
        self.logger.log_write("> Current_version = {}".format(current_version))
        self.logger.log_write("> Latest_version = {}".format(latest_version))
        return (current_version, latest_version)

    def _create_new_version_file(self, latest_version):
        """
        Crea/sobreescribe el archivo oculto que contiene la version actual del sistema. Escribe en su interior <latest_version>.

        Args:
            latest_version (str): Nueva version del sistema con el formato XX.XX.XX
        """
        self.logger.log_write('>>> STATE: Create new version file')
        
        self.mkdir(self.modulepath(self.new_version_dir))

        self.logger.log_write("> Abriendo archivo de versiones: {}".format(self.new_version_dir + '/.version'))
        with open(self.modulepath(self.new_version_dir + '/.version'), 'w') as versionfile:
            self.logger.log_write("> Escribiendo nueva version: {}".format(latest_version))
            versionfile.write(latest_version)
            versionfile.close()

    def _download_new_version(self, version):
        """
        Descarga los archivos de la release <version> de github.

        Args:
            version (str): Version de la release que se desea descargar
        """
        self.logger.log_write('>>> STATE: Download new version')

        self.logger.log_write('> Downloading version {}'.format(version))
        self._download_all_files(version)
        self.logger.log_write('> Version {} downloaded to {}'.format(version, self.modulepath(self.new_version_dir)))

    
    def _copy_secrets_file(self):
        """
        En caso de tener archivos secretos, copia los archivos secretos del directorio principal al directorio que contiene la nueva version del firmware.
        """
        self.logger.log_write('>>> STATE: Copy secrets files')

        if self.secrets_file:
            fromPath = self.modulepath(self.main_dir + '/' + self.secrets_file)
            toPath = self.modulepath(self.new_version_dir + '/' + self.secrets_file)

            self.logger.log_write('> Copying secrets file from {} to {}'.format(fromPath, toPath))
            self._copy_file(fromPath, toPath)
            self.logger.log_write('> Copied secrets file from {} to {}'.format(fromPath, toPath))

    def _rename_old_version(self):
        """
        Renombra el firmware actual, es una manera de "desinstalarlo".
        """
        self.logger.log_write('>>> STATE: Rename old version')

        self.logger.log_write('> Renaming old version to {}'.format(self.modulepath(self.old_main_dir)))
        if self._os_supports_rename():
            os.rename(self.modulepath(self.main_dir), self.modulepath(self.old_main_dir))
        else:
            self._copy_directory(self.modulepath(self.main_dir), self.modulepath(self.old_main_dir))
            self._rmtree(self.modulepath(self.main_dir))
        self.logger.log_write('> Renamed old version to {}'.format(self.modulepath(self.old_main_dir)))

    def _install_new_version(self):
        """
        Renombra el nuevo firmware, asignandole el nombre del firmware principal. Es una manera de "Instalarlo".
        """
        self.logger.log_write('>>> STATE: Install new version')

        self.logger.log_write('> Installing new version at {}'.format(self.modulepath(self.main_dir)))
        if self._os_supports_rename():
            os.rename(self.modulepath(self.new_version_dir), self.modulepath(self.main_dir))
        else:
            self._copy_directory(self.modulepath(self.new_version_dir), self.modulepath(self.main_dir))
            self._rmtree(self.modulepath(self.new_version_dir))
        # print('Update installed, please reboot now')

    def _delete_old_version(self):
        """
        Elimina el firmware que habia sido renombrado en self._rename_old_version().
        """
        self.logger.log_write('>>> STATE: Delete old version')

        self.logger.log_write('> Deleting old version at {}'.format(self.modulepath(self.old_main_dir)))
        self._rmtree(self.modulepath(self.old_main_dir))
        self.logger.log_write('> Deleted old version at {}'.format(self.modulepath(self.old_main_dir)))

    # -------------------------- AUX FUNCTIONS -------------------------

    def get_version(self, directory, version_file_name='.version'):
        """
        Devuelve la version actual, contenida en el archivo oculto <version_file_name> en el directorio <directory>

        Args:
            directory (str): Directorio donde se aloja el archivo que contiene la version actual
            version_file_name (str, optional): Nombre del archivo que contiene la version actual. Por defecto '.version'.

        Returns:
            str: Version actual
        """
        if version_file_name in os.listdir(directory):
            with open(directory + '/' + version_file_name) as f:
                version = f.read()
                return version
        return '0.0'

    def get_latest_version(self):
        """
        Obtiene la version del ultimo release realizado en el repositorio

        Returns:
            str: Version ultimo release
        """
        latest_release = self.http_client.get('https://api.github.com/repos/{}/releases/latest'.format(self.github_repo))
        version = latest_release.json()['tag_name']
        latest_release.close()
        return version

    def _download_all_files(self, version, sub_dir=''):
        """
        Metodo recursivo que permite descargar todos los archivos de la release <version> de github.

        Args:
            version (str): Version de la release de la cual se desea descargar todos los archivos
            sub_dir (str, optional): Directorio donde alojar los archivos descargados. Por defecto ''.
        """
        url = 'https://api.github.com/repos/{}/contents{}{}{}?ref=refs/tags/{}'.format(self.github_repo, self.github_src_dir, self.main_dir, sub_dir, version)
        gc.collect() 
        file_list = self.http_client.get(url)
        for file in file_list.json():
            path = self.modulepath(self.new_version_dir + '/' + file['path'].replace(self.main_dir + '/', '').replace(self.github_src_dir, ''))
            if file['type'] == 'file':
                gitPath = file['path']
                print('\tDownloading: ', gitPath, 'to', path)
                self._download_file(version, gitPath, path)
            elif file['type'] == 'dir':
                print('Creating dir', path)
                self.mkdir(path)
                self._download_all_files(version, sub_dir + '/' + file['name'])
            gc.collect()

        file_list.close()

    def _download_file(self, version, gitPath, path):
        """
        Descarga el archivo de la release <version> ubicado en el path de github <gitpath> y lo almacena en <path>

        Args:
            version (str): Version de la release a la cual pertenece el archivo a descargar
            gitPath (str): Path de github donde se encuentra el archivo
            path (str): Path en el cual se desea guardar el archivo descargado
        """
        self.http_client.get('https://raw.githubusercontent.com/{}/{}/{}'.format(self.github_repo, version, gitPath), saveToFile=path)

    def _rmtree(self, directory):
        """
        Remueve el directorio <directory> y todos los archivos que contiene.

        Args:
            directory (str): Directorio que se desea eliminar
        """
        for entry in os.ilistdir(directory):
            is_dir = entry[1] == 0x4000
            if is_dir:
                self._rmtree(directory + '/' + entry[0])
            else:
                os.remove(directory + '/' + entry[0])
        os.rmdir(directory)

    def _os_supports_rename(self) -> bool:
        """
        Corrobora si el sistema permite el renombramiento de archivos/directorios.

        Returns:
            bool: booleano que indica si el sistema permite renombrar archivos/directorios.
        """
        self._mk_dirs('otaUpdater/osRenameTest')
        os.rename('otaUpdater', 'otaUpdated')
        result = len(os.listdir('otaUpdated')) > 0
        self._rmtree('otaUpdated')
        return result

    def _copy_directory(self, fromPath, toPath):
        """
        Copia el directorio <fromPath> en <toPath>.

        Args:
            fromPath (str): Path del directorio original.
            toPath (str): Path en el cual se desea pegar la copia del directorio.
        """
        if not self._exists_dir(toPath):
            self._mk_dirs(toPath)

        for entry in os.ilistdir(fromPath):
            is_dir = entry[1] == 0x4000
            if is_dir:
                self._copy_directory(fromPath + '/' + entry[0], toPath + '/' + entry[0])
            else:
                self._copy_file(fromPath + '/' + entry[0], toPath + '/' + entry[0])

    def _copy_file(self, fromPath, toPath):
        """
        Copia el archivo <fromPath> en <toPath>.

        Args:
            fromPath (str): Path del archivo original.
            toPath (str): Path en el cual se desea pegar la copia del archivo.
        """
        with open(fromPath) as fromFile:
            with open(toPath, 'w') as toFile:
                CHUNK_SIZE = 512 # bytes
                data = fromFile.read(CHUNK_SIZE)
                while data:
                    toFile.write(data)
                    data = fromFile.read(CHUNK_SIZE)
            toFile.close()
        fromFile.close()

    def _exists_dir(self, path) -> bool:
        """
        Corrobora si un directorio existe.

        Args:
            path (str): Path del directorio que se quiere corroborar.

        Returns:
            bool: Booleano que indica si el directorio existe o no.
        """
        try:
            os.listdir(path)
            return True
        except:
            return False

    def _mk_dirs(self, path:str):
        """
        Crea el arbol de directorios para que <path> sea un directorio valido.

        Args:
            path (str): Path que se desea que exista.
        """
        paths = path.split('/')

        pathToCreate = ''
        for x in paths:
            self.mkdir(pathToCreate + x)
            pathToCreate = pathToCreate + x + '/'

    def mkdir(self, path:str):
        """
        Crea el directorio <path> y contiene la excepcion en caso de existir.

        Args:
            path (str): Directorio a ser creado.
        """
        try:
            os.mkdir(path)
        except OSError as exc:
            if exc.args[0] == 17: 
                pass

    def modulepath(self, path):
        return self.module + '/' + path if self.module else path