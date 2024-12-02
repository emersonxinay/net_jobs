from flask_mail import Mail, Message
from flask import Flask


class Config:
    SECRET_KEY = 'tu_secreto'
    MAIL_SERVER = 'localhost'  # Servidor local para pruebas
    MAIL_PORT = 8025           # Puerto local para el servidor SMTP de pruebas
    MAIL_USE_TLS = False       # No es necesario TLS en pruebas locales
    MAIL_USERNAME = None       # No se requiere autenticación
    MAIL_PASSWORD = None


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)


@app.route('/send_test_email')
def send_test_email():
    msg = Message('Correo de prueba',
                  sender='test@example.com',
                  recipients=['destinatario@example.com'])
    msg.body = 'Este es un correo de prueba enviado desde Flask.'
    mail.send(msg)
    return "Correo enviado (ver terminal SMTP)"


if __name__ == "__main__":
    app.run(debug=True)
