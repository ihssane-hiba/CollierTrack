from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

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

# Initialiser la base de données au démarrage de l'application
if __name__ == '__main__':
    init_db()  # Créer les tables à l'initialisation
    app.run(debug=True)
