from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

# Configuration de la connexion à MySQL
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        database="BaggageManagement",
        user="root",
        password=""
    )
    return conn

# Initialiser la base de données et créer les tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255),
            role VARCHAR(20)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parcels (
            id INT PRIMARY KEY AUTO_INCREMENT,
            reference VARCHAR(50) UNIQUE,
            description VARCHAR(255),
            status VARCHAR(20),
            date_enregistrement DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

# Configuration de l'email
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Décorateur pour vérifier la connexion de l'utilisateur
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route pour la page de connexion
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Connexion réussie !', 'success')
            return redirect(('file:///C:/xampp/htdocs/dashboard/CollierTrack/templates/form.html'))  # Redirect to the '/form' route
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')

    return render_template('login.html')

# Route pour afficher le formulaire après connexion
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        reference = request.form['reference']
        description = request.form['description']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO parcels (reference, description, status)
            VALUES (%s, %s, %s)
        ''', (reference, description, status))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Colis ajouté avec succès !', 'success')
        return redirect(url_for('list_parcels'))

    return render_template('form.html')

# Route pour afficher tous les articles
@app.route('/list')
@login_required
def list_parcels():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parcels")
    parcels = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('list_parcels.html', parcels=parcels)

# Route pour modifier un article
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_parcel(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        reference = request.form['reference']
        description = request.form['description']
        status = request.form['status']

        cursor.execute('''
            UPDATE parcels
            SET reference = %s, description = %s, status = %s
            WHERE id = %s
        ''', (reference, description, status, id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Colis modifié avec succès !', 'success')
        return redirect(url_for('list_parcels'))

    cursor.execute("SELECT * FROM parcels WHERE id = %s", (id,))
    parcel = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_parcel.html', parcel=parcel)

# Route pour supprimer un article
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_parcel(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parcels WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Colis supprimé avec succès !')
    return redirect(url_for('list_parcels'))

if __name__ == '__main__':
    app.run(debug=True)
