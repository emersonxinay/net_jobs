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
from math import ceil
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno

# rutas para perfil de usuario


# fin para ruta de perfil de usuario

# actualizar usuario


# Configuración de la aplicación


class Config:
    # Mejor usar variable de entorno
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_secreto')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 8025))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'tu_correo@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv(
        'MAIL_DEFAULT_SENDER', 'tu_correo@example.com')


# Inicialización de Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_secreto'
socketio = SocketIO(app, cors_allowed_origins="*",
                    logger=True, engineio_logger=True)
app.config.from_object(Config)


# Inicialización de extensiones
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        raise

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
    # Obtener parámetros de filtro y paginación
    page = request.args.get('page', 1, type=int)
    per_page = 5  # empleos por página
    search = request.args.get('search', '')
    filter_urgent = request.args.get('urgent', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Construir la consulta base
    query = """
        SELECT j.*, u.username, u.phone_number
        FROM jobs j
        JOIN users u ON j.user_id = u.id
        WHERE 1=1
    """
    params = []

    # Agregar filtros si existen
    if search:
        query += " AND (j.title ILIKE %s OR j.description ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    if filter_urgent:
        query += " AND j.urgent = TRUE"

    # Contar total de registros para paginación
    count_query = f"SELECT COUNT(*) FROM ({query}) as count_query"
    cur.execute(count_query, params)
    total_jobs = cur.fetchone()['count']
    total_pages = ceil(total_jobs / per_page)

    # Agregar ordenamiento y paginación
    query += " ORDER BY j.urgent DESC, j.date_posted DESC LIMIT %s OFFSET %s"
    offset = (page - 1) * per_page
    params.extend([per_page, offset])

    # Ejecutar consulta final
    cur.execute(query, params)
    jobs = cur.fetchall()

    cur.close()
    conn.close()

    # Si es una petición AJAX, devolver solo el contenido parcial
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/job_list.html',
                               jobs=jobs,
                               page=page,
                               total_pages=total_pages,
                               search=search,
                               filter_urgent=filter_urgent)

    # Si no es AJAX, devolver la página completa
    return render_template('public_dashboard.html',
                           jobs=jobs,
                           page=page,
                           total_pages=total_pages,
                           search=search,
                           filter_urgent=filter_urgent)

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
    # Obtener parámetros de filtro y paginación
    page = request.args.get('page', 1, type=int)
    per_page = 5  # empleos por página
    search = request.args.get('search', '')
    filter_urgent = request.args.get('urgent', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Construir la consulta base
    query = """
        SELECT j.*, u.username, u.phone_number
        FROM jobs j
        JOIN users u ON j.user_id = u.id
        WHERE 1=1
    """
    params = []

    # Agregar filtros si existen
    if search:
        query += " AND (j.title ILIKE %s OR j.description ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    if filter_urgent:
        query += " AND j.urgent = TRUE"

    # Contar total de registros para paginación
    count_query = f"SELECT COUNT(*) FROM ({query}) as count_query"
    cur.execute(count_query, params)
    total_jobs = cur.fetchone()['count']
    total_pages = ceil(total_jobs / per_page)

    # Agregar ordenamiento y paginación
    query += " ORDER BY j.urgent DESC, j.date_posted DESC LIMIT %s OFFSET %s"
    offset = (page - 1) * per_page
    params.extend([per_page, offset])

    # Ejecutar consulta final
    cur.execute(query, params)
    jobs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('dashboard.html',
                           jobs=jobs,
                           page=page,
                           total_pages=total_pages,
                           search=search,
                           filter_urgent=filter_urgent)

# Ruta para crear un empleo


@app.route('/new_job', methods=['GET', 'POST'])
@login_required
def new_job():
    if request.method == 'POST':
        try:
            # Validación de datos
            if not all([request.form['title'], request.form['description'],
                       request.form['locationn'], request.form['exact_date']]):
                flash("Todos los campos obligatorios deben estar completos.", "danger")
                return redirect(url_for('new_job'))

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
            flash(f"Error al publicar el trabajo: {str(e)}", "danger")
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
        # Evitar que un usuario chatee consigo mismo
        if current_user.id == user_id:
            flash("No puedes iniciar un chat contigo mismo.", "danger")
            return redirect(url_for('dashboard'))

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Verificar que el trabajo existe y obtener información
        cur.execute("""
            SELECT j.*, u.username as job_owner_username
            FROM jobs j 
            JOIN users u ON j.user_id = u.id 
            WHERE j.id = %s
        """, (job_id,))
        job = cur.fetchone()

        if not job:
            flash("El trabajo no existe o ha sido eliminado.", "danger")
            return redirect(url_for('dashboard'))

        # Verificar que el usuario actual sea el dueño del trabajo o esté chateando con el dueño
        # job['user_id'] es el ID del dueño del trabajo
        if not (current_user.id == job['user_id'] or user_id == job['user_id']):
            flash("No tienes permiso para acceder a esta conversación.", "danger")
            return redirect(url_for('dashboard'))

        # Obtener la información del usuario con quien se chatea
        cur.execute("""
            SELECT id, username, phone_number 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        chat_user = cur.fetchone()

        if not chat_user:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for('dashboard'))

        # Obtener mensajes existentes
        cur.execute("""
            SELECT m.*, 
                   sender.username as sender_username,
                   receiver.username as receiver_username
            FROM messages m
            JOIN users sender ON m.sender_id = sender.id
            JOIN users receiver ON m.receiver_id = receiver.id
            WHERE m.job_id = %s AND (
                (m.sender_id = %s AND m.receiver_id = %s) OR 
                (m.sender_id = %s AND m.receiver_id = %s)
            )
            ORDER BY m.timestamp ASC
        """, (job_id, current_user.id, user_id, user_id, current_user.id))
        messages = cur.fetchall()

        # Agregar información del trabajo al chat_user
        chat_user['job_title'] = job['title']

        cur.close()
        conn.close()

        return render_template('chat.html',
                               chat_user=chat_user,
                               messages=messages,
                               job=job)

    except Exception as e:
        print(f"Error en chat: {e}")
        flash(f"Error al cargar la conversación: {e}", "danger")
        return redirect(url_for('dashboard'))


@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        # Crear una sala única para el usuario
        room = str(current_user.id)
        join_room(room)
        print(f"Usuario {current_user.id} conectado y unido a la sala {room}")


@socketio.on('send_message')
def handle_send_message(data):
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    message = data['message']
    job_id = data.get('job_id')
    timestamp = datetime.utcnow()

    # Log adicional
    print(
        f"Procesando mensaje - De: {sender_id} Para: {receiver_id} Mensaje: {message}")

    try:
        # Guardar mensaje en la base de datos
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, job_id, message, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING timestamp
        """, (sender_id, receiver_id, job_id, message, timestamp))

        timestamp = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # Emitir el mensaje tanto al remitente como al destinatario
        message_data = {
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'job_id': job_id,
            'message': message,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

        print(f"Emitiendo mensaje a sala {sender_id}")  # Log adicional
        emit('new_message', message_data, room=str(sender_id))

        print(f"Emitiendo mensaje a sala {receiver_id}")  # Log adicional
        emit('new_message', message_data, room=str(receiver_id))

    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")


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

        # Recuperar conversaciones no eliminadas por el usuario actual
        cur.execute("""
            WITH LastMessages AS (
                SELECT 
                    DISTINCT ON (
                        CASE 
                            WHEN sender_id = %s THEN receiver_id 
                            ELSE sender_id 
                        END,
                        job_id
                    )
                    CASE 
                        WHEN sender_id = %s THEN receiver_id 
                        ELSE sender_id 
                    END as other_user_id,
                    job_id,
                    timestamp as last_message_time
                FROM messages 
                WHERE (sender_id = %s OR receiver_id = %s)
                AND NOT EXISTS (
                    SELECT 1 FROM deleted_conversations dc
                    WHERE dc.user_id = %s
                    AND dc.job_id = messages.job_id
                    AND dc.other_user_id = CASE 
                        WHEN sender_id = %s THEN receiver_id 
                        ELSE sender_id 
                    END
                )
                ORDER BY other_user_id, job_id, timestamp DESC
            )
            SELECT 
                lm.other_user_id,
                u.username,
                j.title AS job_title,
                j.exact_date AS job_date,
                j.price AS job_payment,
                j.id AS job_id,
                EXTRACT(EPOCH FROM (j.end_time - j.start_time)) / 3600 AS job_hours,
                lm.last_message_time
            FROM LastMessages lm
            JOIN users u ON u.id = lm.other_user_id
            JOIN jobs j ON j.id = lm.job_id
            WHERE j.id IS NOT NULL
            ORDER BY lm.last_message_time DESC
        """, (current_user.id, current_user.id, current_user.id, current_user.id,
              current_user.id, current_user.id))

        conversations = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('conversations.html', conversations=conversations)

    except Exception as e:
        print(f"Error en conversations: {e}")
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
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.body = f'Para restablecer tu password, haz clic en el siguiente enlace: {
                reset_url}'
            msg.charset = 'utf-8'

            try:
                mail.send(msg)
                flash(
                    'Se ha enviado un correo con instrucciones para restablecer tu password.', 'success')
            except ConnectionRefusedError:
                flash('El servidor de correo no está disponible en este momento. Por favor, intenta más tarde o contacta al administrador.', 'warning')
            except Exception as e:
                flash(
                    'Hubo un error al enviar el correo. Por favor, intenta más tarde.', 'warning')
                print(f"Error al enviar correo: {str(e)}")
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


@app.route('/delete_chat/<int:user_id>/<int:job_id>', methods=['POST'])
@login_required
def delete_chat(user_id, job_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Verificar que el trabajo existe
        cur.execute("SELECT user_id FROM jobs WHERE id = %s", (job_id,))
        job = cur.fetchone()

        if not job:
            flash("El trabajo no existe o ha sido eliminado.", "danger")
            return redirect(url_for('conversations'))

        # Verificar que el usuario actual es parte de la conversación
        if not (current_user.id == job['user_id'] or current_user.id == user_id):
            flash("No tienes permiso para eliminar esta conversación.", "danger")
            return redirect(url_for('conversations'))

        # Marcar la conversación como eliminada para el usuario actual
        cur.execute("""
            INSERT INTO deleted_conversations (user_id, job_id, other_user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, job_id, other_user_id) DO NOTHING
        """, (current_user.id, job_id, user_id))

        # Eliminar mensajes más antiguos de un mes
        cur.execute("""
            DELETE FROM messages 
            WHERE job_id = %s 
            AND timestamp < NOW() - INTERVAL '1 month'
            AND EXISTS (
                SELECT 1 FROM deleted_conversations dc1
                WHERE dc1.job_id = messages.job_id
                AND dc1.user_id = messages.sender_id
            )
            AND EXISTS (
                SELECT 1 FROM deleted_conversations dc2
                WHERE dc2.job_id = messages.job_id
                AND dc2.user_id = messages.receiver_id
            )
        """, (job_id,))

        conn.commit()
        cur.close()
        conn.close()

        flash("La conversación ha sido eliminada de tu lista.", "success")
        return redirect(url_for('conversations'))

    except Exception as e:
        print(f"Error al eliminar chat: {e}")
        flash(f"Error al eliminar la conversación: {e}", "danger")
        return redirect(url_for('conversations'))


@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Verificar que el trabajo existe y pertenece al usuario actual
        cur.execute("SELECT user_id FROM jobs WHERE id = %s", (job_id,))
        job = cur.fetchone()

        if not job:
            flash("El trabajo no existe.", "danger")
            return redirect(url_for('dashboard'))

        if job['user_id'] != current_user.id:
            flash("No tienes permiso para eliminar este trabajo.", "danger")
            return redirect(url_for('dashboard'))

        # Eliminar los mensajes relacionados con el trabajo
        cur.execute("DELETE FROM messages WHERE job_id = %s", (job_id,))

        # Eliminar las conversaciones eliminadas relacionadas
        cur.execute(
            "DELETE FROM deleted_conversations WHERE job_id = %s", (job_id,))

        # Eliminar el trabajo
        cur.execute("DELETE FROM jobs WHERE id = %s", (job_id,))

        conn.commit()
        cur.close()
        conn.close()

        flash("Trabajo eliminado exitosamente.", "success")
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Error al eliminar trabajo: {e}")
        flash(f"Error al eliminar el trabajo: {e}", "danger")
        return redirect(url_for('dashboard'))


@app.context_processor
def utility_processor():
    return {
        'current_year': datetime.utcnow().year
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    if os.getenv('FLASK_ENV') == 'development':
        socketio.run(app, host=host, port=port, debug=True)
    else:
        socketio.run(app, host=host, port=port, debug=False)
