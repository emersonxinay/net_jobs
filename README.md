# Que es trabajo al dia?
Hola quien leea esto, Trabajo al dia es una pagina de una red social de empleabilidad rapida y eficiente, donde todos puedan buscar y publicar trabajos rapidos
Trabajo al dia permite contactar y buscar trabajos para realizar y a si ganar dinero o buscar gente quien quiera ganarlos a traves del trabajo 
que se le asigne.



# Mision
Lograr que la gente pueda obtener dinero de una buena manera acceptando trabajos 

Bajar la cesantia del pais con los trabajos que suelen ser remplazos
ya que permiten abrir una puerta hacia ser contratado como puede ser la experiencia

Ayudar a los universitarios que no pueden trabajar todo el tiempo a pagar sus gastos

Ayudar a la gente sin trabajo a generar un ingreso

Crear oportunidades laborales 

Saber a traves del sistema de calificaciones quien es bueno en su trabajo y quien no

# Vision
Globalizar la pagina y hacerla famosa para que todos puedan generar un salario en el mundo

Incluir a los mayores de 15 - 18 a la pagina para que tambien puedan generar ingresos sin perjudicarles

Ser una gran fuente de apoyo para quien lo necesite



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

### Para recuperar contraseña:
- para crear un servidor de correo local 
primero correr este comando
```bash
python -m smtpd -n -c DebuggingServer localhost:8025
```
- correr desde la ruta para recuperar correo en 
```bash
http://127.0.0.1:5000/forgot_password
```
volvemos a la terminal donde esta corriendo el servidor email local, y veremos algo asi:
```bash
---------- MESSAGE FOLLOWS ----------
b'Content-Type: text/plain; charset="utf-8"'
b'MIME-Version: 1.0'
b'Content-Transfer-Encoding: 7bit'
b'Subject: =?utf-8?q?Recuperaci=C3=B3n_de_password?='
b'From: tu_correo@example.com'
b'To: xinayespinoza@gmail.com'
b'Date: Mon, 02 Dec 2024 20:06:43 -0300'
b'Message-ID:'
b' <173318080355.53585.11486209017628377374@124.0.168.192.in-addr.arpa>'
b'X-Peer: ::1'
b''
b'Para restablecer tu password, haz clic en el siguiente enlace: http://127.0.0.1:5000/reset_password/ZUn-LEKhAsR1OMH6lOYpFgaGnYACxOwz0nVV8pB9ixU'
------------ END MESSAGE ------------
```
y copiar o hacer click en el enlace para restablecer la contraseña

- img demo
Dashboard
<img src="./static/img/dashboard.png">

Perfil
<img src="./static/img/perfil.png">

conversaciones
<img src="./static/img/conversaciones.png">

Nuevo Empleo
<img src="./static/img/nuevo_empleo.png">



