import mysql.connector
import streamlit as st


def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        charset="utf8mb4",
        use_pure=True,
    )


def creer_table_candidatures():
    """Crée la table candidatures si elle n'existe pas."""

    requete = """
    CREATE TABLE IF NOT EXISTS candidatures (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

        user_id INT UNSIGNED NOT NULL,

        entreprise_id INT NULL,

        entreprise_nom VARCHAR(255) NOT NULL,

        entreprise_email VARCHAR(255) NULL,

        poste VARCHAR(255) NOT NULL,

        message TEXT NULL,

        cv_filename VARCHAR(255) NOT NULL,

        cv_data LONGBLOB NOT NULL,

        cv_mimetype VARCHAR(100) NOT NULL DEFAULT 'application/pdf',

        statut ENUM(
            'Brouillon',
            'Envoyée',
            'En attente',
            'Entretien',
            'Acceptée',
            'Refusée'
        ) NOT NULL DEFAULT 'Brouillon',

        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP,

        CONSTRAINT fk_candidatures_user
            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE,

        INDEX idx_candidatures_user (user_id),
        INDEX idx_candidatures_entreprise (entreprise_id)
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


def creer_candidature(
    user_id,
    entreprise_id,
    entreprise_nom,
    entreprise_email,
    poste,
    message,
    cv_filename,
    cv_data,
    cv_mimetype="application/pdf"
):
    """Enregistre une candidature et son CV PDF dans MySQL."""

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO candidatures (
                user_id,
                entreprise_id,
                entreprise_nom,
                entreprise_email,
                poste,
                message,
                cv_filename,
                cv_data,
                cv_mimetype,
                statut
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Brouillon')
        """, (
            user_id,
            entreprise_id,
            entreprise_nom,
            entreprise_email,
            poste,
            message,
            cv_filename,
            cv_data,
            cv_mimetype
        ))

        connection.commit()

        return True, "Candidature enregistrée avec succès."

    except mysql.connector.Error as erreur:
        connection.rollback()
        return False, f"Erreur MySQL : {erreur}"

    finally:
        cursor.close()
        connection.close()


def obtenir_candidatures_utilisateur(user_id):
    """Retourne les candidatures de l'utilisateur connecté."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                entreprise_nom,
                entreprise_email,
                poste,
                message,
                cv_filename,
                statut,
                created_at,
                updated_at
            FROM candidatures
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()