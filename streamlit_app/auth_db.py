import re
from datetime import datetime

import bcrypt
import mysql.connector
from email_validator import EmailNotValidError, validate_email
import streamlit as st


def get_connection():
    """Ouvre une connexion MySQL en utilisant Streamlit secrets."""
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        charset="utf8mb4",
        use_pure=True,
    )


def creer_table_users():
    """Crée la table users si elle n'existe pas."""
    requete = """
    CREATE TABLE IF NOT EXISTS users (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(120) NOT NULL,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP,
        last_login DATETIME NULL
    ) ENGINE=InnoDB
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(requete)
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def valider_donnees_inscription(full_name, username, email, password, confirmation):
    """Vérifie les données saisies avant inscription."""
    erreurs = []

    full_name = full_name.strip()
    username = username.strip()
    email = email.strip()

    if len(full_name) < 3:
        erreurs.append("Le nom complet doit contenir au moins 3 caractères.")

    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", username):
        erreurs.append(
            "Le nom d'utilisateur doit contenir entre 3 et 50 caractères : "
            "lettres, chiffres, _, - ou ."
        )

    try:
        email = validate_email(
            email,
            check_deliverability=False
        ).normalized
    except EmailNotValidError:
        erreurs.append("Veuillez entrer une adresse e-mail valide.")

    if len(password) < 8:
        erreurs.append(
            "Le mot de passe doit contenir au moins 8 caractères."
        )

    if password != confirmation:
        erreurs.append("La confirmation du mot de passe ne correspond pas.")

    return erreurs


def creer_utilisateur(full_name, username, email, password):
    """
    Crée un nouveau compte utilisateur.
    La base ne reçoit jamais le mot de passe clair, seulement son hash bcrypt.
    """
    full_name = full_name.strip()
    username = username.strip().lower()

    email = validate_email(
        email.strip(),
        check_deliverability=False
    ).normalized.lower()

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email)
        )

        utilisateur_existant = cursor.fetchone()

        if utilisateur_existant:
            return False, (
                "Ce nom d'utilisateur ou cette adresse e-mail est déjà utilisé."
            )

        cursor.execute("""
            INSERT INTO users (
                full_name,
                username,
                email,
                password_hash,
                role
            )
            VALUES (%s, %s, %s, %s, 'user')
        """, (
            full_name,
            username,
            email,
            password_hash
        ))

        connection.commit()

        return True, "Compte créé avec succès. Vous pouvez vous connecter."

    except mysql.connector.Error as erreur:
        connection.rollback()
        return False, f"Erreur MySQL : {erreur}"

    finally:
        cursor.close()
        connection.close()


def authentifier_utilisateur(login, password):
    """
    Vérifie email/username + mot de passe bcrypt.
    Retourne les données utilisateur en cas de succès, sinon None.
    """
    login = login.strip().lower()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                full_name,
                username,
                email,
                password_hash,
                role,
                is_active
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
        """, (login, login))

        user = cursor.fetchone()

        if user is None:
            return None, "Identifiants incorrects."

        if not user["is_active"]:
            return None, "Ce compte est désactivé."

        password_correct = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not password_correct:
            return None, "Identifiants incorrects."

        cursor.execute("""
            UPDATE users
            SET last_login = %s
            WHERE id = %s
        """, (
            datetime.now(),
            user["id"]
        ))

        connection.commit()

        user.pop("password_hash", None)

        return user, None

    except mysql.connector.Error:
        return None, "Impossible de se connecter à la base de données."

    finally:
        cursor.close()
        connection.close()


def obtenir_utilisateurs():
    """Fonction réservée pour une future page administrateur."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                full_name,
                username,
                email,
                role,
                is_active,
                created_at,
                last_login
            FROM users
            ORDER BY created_at DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()