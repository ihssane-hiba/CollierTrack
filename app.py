from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuration de la connexion à MySQL
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",          # Nom du serveur MySQL
        database="BaggageManagement",  # Nom de la base de données MySQL
        user="root",               # Nom d'utilisateur MySQL
        password=""                # Mot de passe MySQL
    )
    return conn

# Initialiser la base de données et créer les tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Créer la table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50),
            password VARCHAR(50),
            role VARCHAR(20)
        )
    ''')

    # Créer la table parcels
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

# Route pour la page de connexion
@app.route('/')
def login():
    return render_template('login.html')

# Route pour la page d'administration
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Route pour la page de formulaire
@app.route('/form', methods=['GET', 'POST'])
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
        
        return redirect(url_for('list_parcels'))
    
    return render_template('form.html')

# Route pour afficher tous les articles
@app.route('/list', methods=['GET'])
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
        
        return redirect(url_for('list_parcels'))
    
    cursor.execute("SELECT * FROM parcels WHERE id = %s", (id,))
    parcel = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit_parcel.html', parcel=parcel)

# Route pour supprimer un article
@app.route('/delete/<int:id>', methods=['POST'])
def delete_parcel(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM parcels WHERE id = %s", (id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('list_parcels'))

# Route pour signaler un article perdu
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

@app.route('/report_lost', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        reference = request.form['reference']
        description = request.form['description']
        
        # Envoyer l'email
        msg = Message('Article Perdu Signalé', sender='your_email@example.com', recipients=['admin@example.com'])
        msg.body = f'Article perdu:\nRéférence: {reference}\nDescription: {description}'
        mail.send(msg)
        
        return "Article perdu signalé avec succès."

    return render_template('report_lost.html')

# Initialiser la base de données au démarrage de l'application
if __name__ == '__main__':
    init_db()  # Créer les tables à l'initialisation
    app.run(debug=True)
