from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import secrets
from math import ceil
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pusher
from flask_wtf.csrf import CSRFProtect

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
csrf = CSRFProtect(app)


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
            port=os.getenv('POSTGRES_PORT'),
            sslmode='disable'  # Forzamos explícitamente a deshabilitar SSL
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
    conn = None
    try:
        message = request.form.get('message')

        if not message or not message.strip():
            return jsonify({'error': 'El mensaje no puede estar vacío'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Obtener información del trabajo
        cur.execute("""
            SELECT title, user_id 
            FROM jobs 
            WHERE id = %s
        """, (job_id,))
        job = cur.fetchone()

        if not job:
            return jsonify({'error': 'El trabajo no existe'}), 404

        # Insertar el mensaje
        cur.execute("""
            INSERT INTO messages 
                (sender_id, receiver_id, message, job_id, timestamp) 
            VALUES 
                (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING 
                id, 
                timestamp AT TIME ZONE 'UTC' as timestamp
        """, (current_user.id, receiver_id, message, job_id))

        message_data = cur.fetchone()
        conn.commit()

        # Preparar payload para el mensaje de chat
        message_payload = {
            'message_id': message_data[0],
            'timestamp': message_data[1].isoformat(),
            'sender_id': current_user.id,
            'receiver_id': receiver_id,
            'message': message,
            'job_id': job_id
        }

        # Enviar mensaje de chat
        pusher_client.trigger(
            [f'private-chat-{receiver_id}', f'private-chat-{current_user.id}'],
            'new_message',
            message_payload
        )

        # Enviar notificación solo al receptor
        notification_payload = {
            'sender_id': current_user.id,
            'sender_name': current_user.username,
            'job_id': job_id,
            'job_title': job[0],
            'message': message[:50] + '...' if len(message) > 50 else message
        }

        pusher_client.trigger(
            f'private-notifications-{receiver_id}',
            'new_message_notification',
            notification_payload
        )

        return jsonify({
            'status': 'success',
            'message': message_payload
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error en send_message: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if conn:
            cur.close()
            conn.close()


@app.route('/chat/<int:user_id>/<int:job_id>')
@login_required
def chat(user_id, job_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Obtener información del usuario del chat
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        chat_user = cur.fetchone()

        # Obtener información del trabajo
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        job = cur.fetchone()

        if not chat_user:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for('dashboard'))

        # Obtener mensajes existentes con ORDER BY timestamp
        cur.execute("""
            SELECT 
                m.id,
                m.message,
                m.timestamp AT TIME ZONE 'UTC' as timestamp,
                m.sender_id,
                m.receiver_id,
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
                               job=job,
                               config={
                                   'PUSHER_KEY': os.getenv('PUSHER_KEY'),
                                   'PUSHER_CLUSTER': os.getenv('PUSHER_CLUSTER')
                               })

    except Exception as e:
        print(f"Error en chat: {e}")
        flash(f"Error al cargar la conversación: {e}", "danger")
        return redirect(url_for('dashboard'))


@app.route('/unread_messages_count')
@login_required
def unread_messages_count():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Contar mensajes no leídos
        cur.execute("""
            SELECT COUNT(DISTINCT m.id) 
            FROM messages m
            LEFT JOIN read_messages rm ON m.id = rm.message_id AND rm.user_id = %s
            WHERE 
                m.receiver_id = %s 
                AND rm.id IS NULL
        """, (current_user.id, current_user.id))

        count = cur.fetchone()[0]

        cur.close()
        conn.close()

        return jsonify({'count': count})
    except Exception as e:
        print(f"Error al obtener mensajes no leídos: {e}")
        return jsonify({'count': 0})


@app.route('/mark_messages_read/<int:other_user_id>/<int:job_id>')
@login_required
def mark_messages_read(other_user_id, job_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Marcar mensajes como leídos
        cur.execute("""
            INSERT INTO read_messages (user_id, message_id)
            SELECT %s, m.id
            FROM messages m
            LEFT JOIN read_messages rm ON m.id = rm.message_id AND rm.user_id = %s
            WHERE 
                m.job_id = %s
                AND m.receiver_id = %s
                AND m.sender_id = %s
                AND rm.id IS NULL
        """, (current_user.id, current_user.id, job_id, current_user.id, other_user_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error al marcar mensajes como leídos: {e}")
        return jsonify({'status': 'error'})
# conversaciones


@app.route('/conversations', methods=['GET'])
@login_required
def conversations():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Consulta corregida
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
                    message as last_message,
                    timestamp as last_message_time
                FROM messages m
                WHERE 
                    (sender_id = %s OR receiver_id = %s)
                    AND NOT EXISTS (
                        SELECT 1 
                        FROM deleted_conversations dc
                        WHERE dc.user_id = %s
                        AND dc.job_id = m.job_id
                        AND dc.other_user_id = CASE 
                            WHEN m.sender_id = %s THEN m.receiver_id 
                            ELSE m.sender_id 
                        END
                    )
                ORDER BY 
                    other_user_id, 
                    job_id, 
                    timestamp DESC
            ),
            UnreadCounts AS (
                SELECT 
                    CASE 
                        WHEN sender_id = %s THEN receiver_id 
                        ELSE sender_id 
                    END as other_user_id,
                    job_id,
                    COUNT(*) as unread_count
                FROM messages m
                LEFT JOIN read_messages rm ON m.id = rm.message_id AND rm.user_id = %s
                WHERE 
                    receiver_id = %s
                    AND rm.id IS NULL
                GROUP BY 
                    CASE 
                        WHEN sender_id = %s THEN receiver_id 
                        ELSE sender_id 
                    END,
                    job_id
            )
            SELECT 
                lm.other_user_id,
                u.username,
                j.title AS job_title,
                j.exact_date AS job_date,
                j.price AS job_payment,
                j.id AS job_id,
                EXTRACT(EPOCH FROM (j.end_time - j.start_time)) / 3600 AS job_hours,
                lm.last_message_time,
                lm.last_message,
                COALESCE(uc.unread_count, 0) as unread_count
            FROM LastMessages lm
            JOIN users u ON u.id = lm.other_user_id
            JOIN jobs j ON j.id = lm.job_id
            LEFT JOIN UnreadCounts uc ON 
                uc.other_user_id = lm.other_user_id 
                AND uc.job_id = lm.job_id
            WHERE j.id IS NOT NULL
            ORDER BY lm.last_message_time DESC
        """, (
            current_user.id, current_user.id,  # Para el primer CASE
            current_user.id, current_user.id,  # Para el WHERE de mensajes
            current_user.id, current_user.id,  # Para el NOT EXISTS
            current_user.id, current_user.id,  # Para UnreadCounts
            current_user.id, current_user.id   # Para el último CASE
        ))

        conversations = cur.fetchall()

        # Asegurarse de que last_message_time sea un objeto datetime
        for conv in conversations:
            if isinstance(conv['last_message_time'], str):
                conv['last_message_time'] = datetime.strptime(
                    conv['last_message_time'], '%Y-%m-%d %H:%M:%S.%f'
                )

        cur.close()
        conn.close()

        return render_template('conversations.html',
                               conversations=conversations,
                               config={
                                   'PUSHER_KEY': os.getenv('PUSHER_KEY'),
                                   'PUSHER_CLUSTER': os.getenv('PUSHER_CLUSTER')
                               })

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

        # Marcar la conversación como eliminada solo para el usuario actual
        cur.execute("""
            INSERT INTO deleted_conversations (user_id, job_id, other_user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, job_id, other_user_id) DO NOTHING
        """, (current_user.id, job_id, user_id))

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
        print(f"Intentando eliminar trabajo {job_id}")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Obtener información del trabajo antes de eliminarlo
        cur.execute("""
            SELECT title, 
                   (SELECT COUNT(*) FROM messages WHERE job_id = jobs.id) as message_count
            FROM jobs 
            WHERE id = %s
        """, (job_id,))
        job_info = cur.fetchone()

        if not job_info:
            flash('El trabajo no existe.', 'error')
            return jsonify({
                'status': 'error',
                'message': 'El trabajo no existe.'
            }), 404

        try:
            # Obtener todos los IDs de mensajes relacionados
            cur.execute("""
                SELECT id FROM messages WHERE job_id = %s
            """, (job_id,))
            message_ids = [row['id'] for row in cur.fetchall()]

            # Eliminar read_messages
            if message_ids:
                cur.execute("""
                    DELETE FROM read_messages 
                    WHERE message_id = ANY(%s)
                """, (message_ids,))

            # Eliminar mensajes
            cur.execute("DELETE FROM messages WHERE job_id = %s", (job_id,))

            # Eliminar conversaciones
            cur.execute(
                "DELETE FROM deleted_conversations WHERE job_id = %s", (job_id,))

            # Eliminar el trabajo
            cur.execute("DELETE FROM jobs WHERE id = %s", (job_id,))

            conn.commit()

            # Crear mensaje detallado
            message = f'Se ha eliminado exitosamente la publicación "{
                job_info["title"]}"'
            if job_info['message_count'] > 0:
                message += f' y {job_info["message_count"]
                                 } mensaje(s) relacionado(s)'

            flash(message, 'success')

            return jsonify({
                'status': 'success',
                'message': message
            })

        except Exception as db_error:
            conn.rollback()
            print(f"Error en la base de datos: {db_error}")
            flash('Error al eliminar el trabajo. Por favor, intente nuevamente.', 'error')
            raise

    except Exception as e:
        print(f"Error al eliminar trabajo {job_id}: {str(e)}")
        flash(f'Error al eliminar el trabajo: {str(e)}', 'error')
        return jsonify({
            'status': 'error',
            'message': f'Error al eliminar el trabajo: {str(e)}'
        }), 500

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


@app.context_processor
def utility_processor():
    return {
        'current_year': datetime.utcnow().year
    }


@app.route('/pusher/auth', methods=['POST'])
@login_required
def pusher_authentication():
    auth = pusher_client.authenticate(
        channel=request.form['channel_name'],
        socket_id=request.form['socket_id']
    )
    return jsonify(auth)


# Configuración de Pusher desde variables de entorno
pusher_client = pusher.Pusher(
    app_id=os.getenv('PUSHER_APP_ID'),
    key=os.getenv('PUSHER_KEY'),
    secret=os.getenv('PUSHER_SECRET'),
    cluster=os.getenv('PUSHER_CLUSTER'),
    ssl=True
)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=os.getenv(
        'FLASK_ENV') == 'development')
