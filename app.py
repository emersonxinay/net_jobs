from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import secrets

# Configuración de la aplicación


class Config:
    SECRET_KEY = 'tu_secreto'
    MAIL_SERVER = 'localhost'  # Servidor local para pruebas
    MAIL_PORT = 8025           # Puerto local para el servidor SMTP de pruebas
    MAIL_USE_TLS = False       # No es necesario TLS en pruebas locales
    MAIL_USERNAME = 'tu_correo@example.com'  # Remitente por defecto
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'tu_correo@example.com'  # Agrega esto


# Inicialización de Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicialización de extensiones
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


def get_db_connection():
    conn = psycopg2.connect(
        dbname='red_jobs', user='postgres', password='emerson123', host='localhost')
    return conn

# Modelo de Usuario


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Cargar usuario


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

# Ruta para el registro de usuarios


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(
            request.form['password']).decode('utf-8')
        # Verifica que el email no esté vacío antes de proceder
        if not email:
            flash('El email es obligatorio', 'danger')
            return redirect(url_for('register'))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, email, password) 
            VALUES (%s, %s, %s)
        """, (username, email, password))
        conn.commit()
        conn.close()
        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Ruta para el login de usuarios


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(
                User(id=user['id'], username=user['username'], password=user['password']))
            return redirect(url_for('dashboard'))
        else:
            flash('Inicio de sesión inválido.', 'danger')
    return render_template('login.html')

# Ruta para el logout


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ruta para el dashboard de empleos


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY urgent DESC, date_posted DESC")
    jobs = cur.fetchall()
    jobs1 = get_jobs()
    conn.close()
    return render_template('dashboard.html', jobs=jobs, jobs1=jobs1)

# Ruta para crear un empleo


@app.route('/new_job', methods=['GET', 'POST'])
@login_required
def new_job():
    if request.method == 'POST':
        # Obtener los datos del formulario
        title = request.form['title']
        description = request.form['description']
        urgent = 'urgent' in request.form
        locationn = request.form['locationn']
        exact_date = request.form['exact_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        # Obtener el número de contacto
        contact_number = request.form['contact_number']

        # Validación para asegurarse de que la hora de inicio sea anterior a la hora de finalización
        if start_time >= end_time:
            flash(
                "La hora de inicio debe ser anterior a la hora de finalización.", "danger")
            return redirect(url_for('new_job'))

        # Insertar el nuevo trabajo en la base de datos
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO jobs (title, description, urgent, locationn, exact_date, start_time, end_time, user_id, contact_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, description, urgent, locationn, exact_date, start_time, end_time, current_user.id, contact_number))
            conn.commit()
            cur.close()
            conn.close()
            flash("Trabajo publicado exitosamente.", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Error al publicar el trabajo: {e}", "danger")
            return redirect(url_for('new_job'))

    return render_template('new_job.html')


def get_jobs():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT j.*, u.username, u.phone_number
        FROM jobs j
        JOIN users u ON j.user_id = u.id
        ORDER BY j.date_posted DESC
    """)
    jobs = cur.fetchall()
    cur.close()
    conn.close()
    return jobs


# @app.route('/chat/<int:user_id>')
# @login_required
# def chat(user_id):
#     # Aquí puedes implementar la lógica para iniciar una conversación con el usuario con user_id
#     # Por ejemplo, obtener el usuario y renderizar una plantilla de chat
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
#     user = cur.fetchone()
#     cur.close()
#     conn.close()
#     if user:
#         return render_template('chat.html', chat_user=user)
#     else:
#         flash("Usuario no encontrado.", "danger")
#         return redirect(url_for('dashboard'))

# mandar mensajes


@app.route('/send_message/<int:receiver_id>', methods=['POST'])
@login_required
def send_message(receiver_id):
    message = request.form['message']

    if not message.strip():
        flash("El mensaje no puede estar vacío.", "warning")
        return redirect(url_for('chat', user_id=receiver_id))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, message)
            VALUES (%s, %s, %s)
        """, (current_user.id, receiver_id, message))
        conn.commit()
        cur.close()
        conn.close()
        flash("Mensaje enviado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al enviar el mensaje: {e}", "danger")

    return redirect(url_for('chat', user_id=receiver_id))

# chat de conversaciones


@app.route('/chat/<int:user_id>', methods=['GET'])
@login_required
def chat(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Obtener la información del usuario con el que se está chateando
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        chat_user = cur.fetchone()

        if not chat_user:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for('dashboard'))

        # Obtener todos los mensajes entre el usuario actual y el chat_user
        cur.execute("""
            SELECT * FROM messages
            WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """, (current_user.id, user_id, user_id, current_user.id))

        messages = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('chat.html', chat_user=chat_user, messages=messages)
    except Exception as e:
        flash(f"Error al cargar la conversación: {e}", "danger")
        return redirect(url_for('dashboard'))

# conversaciones


@app.route('/conversations', methods=['GET'])
@login_required
def conversations():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Obtener todos los usuarios con los que el usuario actual ha intercambiado mensajes
        cur.execute("""
            SELECT DISTINCT u.id, u.username
            FROM messages m
            JOIN users u ON
                (u.id = m.sender_id OR u.id = m.receiver_id)
            WHERE (m.sender_id = %s OR m.receiver_id = %s)
              AND u.id != %s
        """, (current_user.id, current_user.id, current_user.id))

        users = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('conversations.html', users=users)
    except Exception as e:
        flash(f"Error al cargar las conversaciones: {e}", "danger")
        return redirect(url_for('dashboard'))

# para recuperar password


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        conn.close()

        if user:
            token = secrets.token_urlsafe(32)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE users SET reset_token = %s, reset_expiration = %s WHERE email = %s
            """, (token, datetime.utcnow() + timedelta(hours=1), email))
            conn.commit()
            cur.close()
            conn.close()

            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Recuperación de password',
                          sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
            msg.body = f'Para restablecer tu password, haz clic en el siguiente enlace: {
                reset_url}'
            msg.charset = 'utf-8'
            mail.send(msg)

            flash(
                'Se ha enviado un correo con instrucciones para restablecer tu password.', 'success')
        else:
            flash('No se encontró una cuenta con ese correo electrónico.', 'danger')

        return redirect(url_for('login'))

    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT * FROM users WHERE reset_token = %s AND reset_expiration > %s
    """, (token, datetime.utcnow()))
    user = cur.fetchone()
    conn.close()

    if not user:
        flash('El enlace de restablecimiento no es válido o ha expirado.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = bcrypt.generate_password_hash(
            request.form['password']).decode('utf-8')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET password = %s, reset_token = NULL, reset_expiration = NULL WHERE id = %s
        """, (new_password, user['id']))
        conn.commit()
        cur.close()
        conn.close()
        flash('Tu password ha sido restablecida exitosamente.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


if __name__ == '__main__':
    app.run(debug=True)
