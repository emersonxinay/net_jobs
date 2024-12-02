# red de trabajos jóvenes 

## Verificar la configuración para correr el proyecto

versión de python
```bash
Python 3.12.5
```
instalar el virtualenv si no tiene instalado
```bash
pip install virtualenv
```
crear el entorno virtual
```bash
python -m venv nombre_entorno
```
en ese caso se llama
```bash
python -m venv venv 
```
activar el entorno virtual 
- en windows 
```bash
venv/Scripts/activate
```
si en windows te sale error:
ejecutar los permisos 
```bash
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
```
y vuelve activar el entorno virtual

- en MacOS o Linux 
```bash
source venv/bin/activate
```

Instalar todos los paquetes desde el archivo requirements.txt 
```bash
pip install requirements.txt
```
o sino instalar independientemente cada libreria que se necesita 
```bash
pip install nombre_paquete
```
ejemplo:
```bash
pip install flask
```

correr el programa
```bash
python nombre-archivo-python.py
```
ejemplo:
```bash
python app.py
```




