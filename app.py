from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from flask_mail import Mail, Message
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

# Configuration de la connexion à MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="BaggageManagement",
            user="root",
            password=""
        )
        if conn.is_connected():
            print("Connexion réussie à la base de données.")
            return conn
    except mysql.connector.Error as err:
        flash(f"Erreur de connexion à la base de données: {err}", 'danger')
        return None

# Initialiser la base de données et créer les tables
def init_db():
    conn = get_db_connection()
    if conn:
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

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'warning')
            return redirect(url_for('index'))  # Redirection vers la page d'accueil
        return f(*args, **kwargs)
    return decorated_function

# Route pour afficher la liste des colis
@app.route('/list_parcels.html')
@login_required
def list_parcels():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM parcels")
            parcels = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('parcels.html', parcels=parcels)
    except mysql.connector.Error as err:
        flash(f'Erreur de connexion à la base de données : {err}', 'danger')
        return redirect(url_for('index'))

# Route pour modifier un article
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_parcel(id):
    try:
        conn = get_db_connection()
        if conn:
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
    except mysql.connector.Error as err:
        flash(f'Erreur de connexion à la base de données : {err}', 'danger')
        return redirect(url_for('index'))

# Route pour supprimer un article
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_parcel(id):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM parcels WHERE id = %s", (id,))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Colis supprimé avec succès !', 'success')
            return redirect(url_for('list_parcels'))
    except mysql.connector.Error as err:
        flash(f'Erreur de connexion à la base de données : {err}', 'danger')
        return redirect(url_for('index'))

# Route vers la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()  # Assurez-vous que la base de données est initialisée
    app.run(debug=True)
