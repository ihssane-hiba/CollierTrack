CREATE DATABASE BaggageManagement;
USE BaggageManagement;

-- Cr�er la table Utilisateurs
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL
);

-- Cr�er la table Colis
CREATE TABLE parcels (
    id INT PRIMARY KEY IDENTITY(1,1),
    reference NVARCHAR(50) NOT NULL UNIQUE,
    description NVARCHAR(255),
    status NVARCHAR(20),
    date_enregistrement DATETIME DEFAULT GETDATE()
);