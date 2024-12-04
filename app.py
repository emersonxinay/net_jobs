from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_bcrypt import Bcrypt
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import secrets
# rutas para perfil de usuario


# fin para ruta de perfil de usuario

# actualizar usuario


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
app.config['SECRET_KEY'] = 'tu_secreto'
socketio = SocketIO(app)
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
    def __init__(self, id, username, password, email=None, phone_number=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email  # Añadimos el atributo email
        self.phone_number = phone_number  # Añadimos el atributo phone_number


# Cargar usuario


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, username, password, email, phone_number FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return User(
            id=user['id'],
            username=user['username'],
            password=user['password'],
            email=user['email'],  # Cargar el email
            phone_number=user['phone_number']  # Cargar el teléfono
        )
    return None


# ruta raiz dasboard publico


@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM jobs ORDER BY urgent DESC, date_posted DESC LIMIT 5")
    jobs1 = get_jobs()
    conn.close()
    return render_template('public_dashboard.html', jobs=jobs1)
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

# perfil de usuario


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Conexión a la base de datos
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Consulta para obtener los datos del usuario
    cur.execute(
        "SELECT email, username, phone_number FROM users WHERE id = %s", (current_user.id,))
    user_data = cur.fetchone()

    # Si el formulario ha sido enviado con método POST, actualizamos los datos
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        phone_number = request.form['phone_number']

        # Actualizamos los datos en la base de datos
        cur.execute("""
            UPDATE users 
            SET email = %s, username = %s, phone_number = %s 
            WHERE id = %s
        """, (email, username, phone_number, current_user.id))

        conn.commit()  # Confirmamos los cambios
        flash('Tus datos han sido actualizados exitosamente.', 'success')
        # Redirigimos para evitar reenvío del formulario
        return redirect(url_for('profile'))

    conn.close()

    # Pasar los datos del usuario a la plantilla
    return render_template('profile.html', user=user_data)


# ruta dashboard publico


# Ruta para el dashboard privado de empleos


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY urgent DESC, date_posted DESC")
    jobs1 = get_jobs()
    conn.close()
    return render_template('dashboard.html', jobs=jobs1)

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
        contact_number = request.form['contact_number']
        price = request.form['price']  # Obtenemos el precio

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
                INSERT INTO jobs (title, description, urgent, locationn, exact_date, start_time, end_time, user_id, contact_number, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, description, urgent, locationn, exact_date, start_time, end_time, current_user.id, contact_number, price))
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


# editar trabajo
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Obtener el trabajo por su ID
    cur.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
    job = cur.fetchone()

    if job is None:
        flash('Trabajo no encontrado.', 'danger')
        return redirect(url_for('dashboard'))

    # Verificar que el trabajo pertenece al usuario actual
    if job[5] != current_user.id:  # Verifica que el campo `user_id` coincide
        flash('No tienes permiso para editar este trabajo.', 'danger')
        return redirect(url_for('dashboard'))

    # Si el formulario se envió
    if request.method == 'POST':
        # Recoger los datos del formulario
        title = request.form['title']
        description = request.form['description']
        urgent = 'urgent' in request.form  # Checkbox
        locationn = request.form['locationn']
        exact_date = request.form['exact_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        contact_number = request.form['contact_number']
        price = request.form['price']

        # Actualizar los datos en la base de datos
        cur.execute('''
            UPDATE jobs 
            SET title = %s, description = %s, urgent = %s, locationn = %s, exact_date = %s, 
                start_time = %s, end_time = %s, contact_number = %s, price = %s
            WHERE id = %s
        ''', (title, description, urgent, locationn, exact_date, start_time, end_time, contact_number, price, job_id))

        conn.commit()

        flash('Trabajo actualizado con éxito.', 'success')
        return redirect(url_for('dashboard'))

    # Convertir los datos del trabajo en un diccionario para usar en el template
    job_dict = {
        'title': job[1],
        'description': job[2],
        'urgent': job[3],
        'locationn': job[6],
        'exact_date': job[7],
        'start_time': job[8],
        'end_time': job[9],
        'contact_number': job[10],
        'price': job[11],
    }

    # Renderizar el template con los datos del trabajo
    return render_template('edit_job.html', job=job_dict)


# fin de editar trabajo


@app.route('/send_message/<int:receiver_id>/<int:job_id>', methods=['POST'])
@login_required
def send_message(receiver_id, job_id):
    message = request.form['message']

    if not message.strip():
        flash("El mensaje no puede estar vacío.", "warning")
        return redirect(url_for('chat', user_id=receiver_id, job_id=job_id))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, job_id)
            VALUES (%s, %s, %s, %s)
        """, (current_user.id, receiver_id, message, job_id))
        conn.commit()
        cur.close()
        conn.close()

        # Emitir el mensaje en tiempo real a través de SocketIO
        socketio.emit('new_message', {
            'sender_id': current_user.id,
            'message': message,
            'timestamp': 'Ahora mismo',
            'receiver_id': receiver_id,
            'job_id': job_id  # Incluir job_id
        }, room=receiver_id)  # Emitir solo a ese usuario

        flash("Mensaje enviado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al enviar el mensaje: {e}", "danger")

    return redirect(url_for('chat', user_id=receiver_id, job_id=job_id))


@app.route('/chat/<int:user_id>/<int:job_id>', methods=['GET'])
@login_required
def chat(user_id, job_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Obtener la información del usuario con el que se está chateando y su empleo
        cur.execute("""
            SELECT u.id, u.username, j.title AS job_title
            FROM users u
            LEFT JOIN jobs j ON u.id = j.user_id
            WHERE u.id = %s AND j.id = %s
        """, (user_id, job_id))
        chat_user = cur.fetchone()

        if not chat_user:
            flash("Usuario o trabajo no encontrado.", "danger")
            return redirect(url_for('dashboard'))

        # Obtener todos los mensajes entre el usuario actual y el chat_user para ese trabajo
        cur.execute("""
            SELECT * FROM messages
            WHERE (sender_id = %s AND receiver_id = %s AND job_id = %s)
               OR (sender_id = %s AND receiver_id = %s AND job_id = %s)
            ORDER BY timestamp ASC
        """, (current_user.id, user_id, job_id, user_id, current_user.id, job_id))

        messages = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('chat.html', chat_user=chat_user, messages=messages)
    except Exception as e:
        flash(f"Error al cargar la conversación: {e}", "danger")
        return redirect(url_for('dashboard'))


@socketio.on('send_message')
def handle_send_message(data):
    print(f"Recibido mensaje: {data}")  # Para depurar

    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    message = data['message']
    # Asegúrate de que el job_id se pase desde el frontend
    job_id = data.get('job_id')
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    # Verificar si job_id es válido
    if not job_id:
        print("Error: El job_id es necesario para enviar el mensaje.")
        return  # Si no hay job_id, no guardamos el mensaje

    # Guardar el mensaje en la base de datos
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Inserta el mensaje con job_id en la base de datos
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, job_id, message, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (sender_id, receiver_id, job_id, message, timestamp))

        conn.commit()
        cur.close()
        conn.close()

        # Emitir el mensaje a la sala correspondiente
        emit('new_message', {
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'job_id': job_id,  # Incluir job_id en el mensaje emitido
            'message': message,
            'timestamp': timestamp
        }, room=str(receiver_id))  # Enviar solo al usuario receptor
    except Exception as e:
        print(f"Error al guardar el mensaje: {e}")


@socketio.on('connect')
def handle_connect():
    """Se ejecuta cuando un cliente se conecta"""
    print(f"Cliente {current_user.id} conectado")
    join_room(current_user.id)


@socketio.on('disconnect')
def handle_disconnect():
    """Se ejecuta cuando un cliente se desconecta"""
    leave_room(current_user.id)


@socketio.on('new_message')
def handle_new_message(data):
    """Recibe un nuevo mensaje de un cliente"""
    # Podrías hacer más cosas aquí como validar o almacenar los mensajes
    print(f"Nuevo mensaje de {data['sender_id']}: {data['message']}")


# conversaciones
@app.route('/conversations', methods=['GET'])
@login_required
def conversations():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Recuperar todas las conversaciones con mensajes relacionados al usuario actual
        cur.execute("""
            SELECT DISTINCT ON (other_user.id, j.id) 
                other_user.id AS other_user_id, 
                other_user.username, 
                j.title AS job_title, 
                j.exact_date AS job_date, 
                j.price AS job_payment, 
                j.id AS job_id, 
                EXTRACT(EPOCH FROM (j.end_time - j.start_time)) / 3600 AS job_hours,
                m.timestamp AS last_message_time
            FROM messages m
            INNER JOIN users other_user 
                ON (m.sender_id = other_user.id AND m.receiver_id = %s) 
                OR (m.receiver_id = other_user.id AND m.sender_id = %s)
            LEFT JOIN jobs j 
                ON m.job_id = j.id
            ORDER BY other_user.id, j.id, m.timestamp DESC
        """, (current_user.id, current_user.id))

        conversations = cur.fetchall()

        cur.close()
        conn.close()

        # Retornar el template con las conversaciones ordenadas
        return render_template('conversations.html', conversations=conversations)

    except Exception as e:
        flash(f"Error al cargar las conversaciones: {e}", "danger")
        return redirect(url_for('dashboard'))


# fin de conversations

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
    socketio.run(app, debug=True)
