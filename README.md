# Sistema Remoto Trimaker

* Este repositorio posee el desarrollo del sistema IOT de bajo nivel para las impresoras Trimaker. Se ha desarrollado con el objetivo de que el software sea ejecutado en un ESP32 CAM con micropython.

## Estructura Repositorio:
En el repositorio se encontraran los siguientes directorios:

* documents: Documentacion de algunas librerias que pueden resultar utiles para el desarrolo del software.

* encrypter: Dentro de esta carpeta se encuentran los archivos para convertir multiples archivos .py en un unico archivo .bin, con la intension de que el mismo sea distribuido para la actualizacion del firmware. 

* firmware: Aqui se encuentran todos los archivos y directorios que deben ir almacenados dentro del ESP32cam

* micropython_esp32cam: Dentro de esta carpeta se encuentra el MicroPython que se debe flashear con ayuda del "Thonny IDE" en el ESP32cam

* suscriber_publisher: En esta carpeta se encuentran dos archivos para la comunicacion con el servidor MQTT, para el testeo del correcto funcionamiento del software.

## Entorno Recomendado:

* **IDE:** Se recomienda utilizar Thonny IDE para el desarrollo del proyecto, ya que permite subir, descargar y editar, directorios dentro del ESP32cam.

    Link Thonny: https://thonny.org

## Git Workflow:

El flujo de trabajo que se utiliza es el propuesto por Vincent Driessen en [a successful git branching model](https://nvie.com/posts/a-successful-git-branching-model/). Se sugiere leerlo.

* **master**   
    Contiene la última versión estable.   

* **develop**  
    En esta rama se agregan cambios incrementales, bugs o mejoras, hasta que se considera que es el momento de hacer una release nueva.   
    Antes de hacer la release comprobar el funcionamiento integral del sistema.

* **release_xx**  
    Se utiliza para renombrar archivos que contienen en su nombre algún indicador de la versión de release.  
    Por ejemplo:  
    - **Nombre inicial**: 1.1.8\1.0.py
    - **Nombre final**: 1.1.8\1.1.py
    
    Puede no ser necesaria esta branch. Ver la [descripión](https://nvie.com/posts/a-successful-git-branching-model/?#release-branches)

* **feature_xx**  
    En estas ramas se implementan mejoras o correcciones de bugs.  
    El flow es el siguiente:  
    1. Se agrega una [issue acá](https://gitlab.com/tiwanacote/trimaker_wifi_esp32/-/issues), donde se describe el tipo ~"Type: Bug" o ~"Type: New Feature":   
        - Si es ~"Type: New Feature", breve descripción, qué es lo que se espera que modifique, posible forma de implementación, etc.
        - Si es ~"Type: Bug", describirlo, explicar los pasos para reproducirlo, cuál es el funcionamiento esperado y cuál es el que sucede.
    1. Asignar la issue a la persona encargada de resolverla.
    1. Asignar etiqueta ~"Status: Doing" cuando se comience a desarrollar.
    1. Crear una rama desde develop para implementarla:
    
        ```    
        $ git checkout develop  
        $ git checkout -b feature_xx
        ```
    1. Una vez testeada mergear a develop y luego borrarla: 
    
        ```
        $ git checkout develop  
        $ git merge --no-ff feature_xx  
        $ git -d feature_xx  
        $ git push
        ```
    NOTA: Con `$ git -d feature_xx` se elimina la rama localmente, en caso de que se haya pusheado dicha rama a origin (repo en la nube) eliminarla de allí también mediante  `$ git push origin --delete the_remote_branch`  
    1. Cambiar la etiqueta de ~"Status: Doing" a ~"Status: Fixed/Solved"

