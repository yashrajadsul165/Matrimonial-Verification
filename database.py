import sqlite3
from datetime import datetime


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_NAME = "matrimonial.db"


# =========================================================
# CREATE DATABASE AND TABLE
# =========================================================

def create_database():
    """
    Create the SQLite database and verification table.
    """

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS verifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            photo_name TEXT,

            face_similarity REAL,

            face_result TEXT,

            deepfake_score REAL,

            deepfake_result TEXT,

            liveness_score REAL,

            liveness_result TEXT,

            document_result TEXT,

            document_name_match INTEGER,

            feedback_score REAL,

            feedback_result TEXT,

            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# =========================================================
# SAVE VERIFICATION
# =========================================================

def save_verification(
    name,
    photo_name="",
    face_similarity=None,
    face_result="",
    deepfake_score=None,
    deepfake_result="",
    liveness_score=None,
    liveness_result="",
    document_result="",
    document_name_match=False,
    feedback_score=None,
    feedback_result=""
):
    """
    Save a complete verification record.
    """

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO verifications (

            name,
            photo_name,
            face_similarity,
            face_result,
            deepfake_score,
            deepfake_result,
            liveness_score,
            liveness_result,
            document_result,
            document_name_match,
            feedback_score,
            feedback_result,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            photo_name,
            face_similarity,
            face_result,
            deepfake_score,
            deepfake_result,
            liveness_score,
            liveness_result,
            document_result,
            int(document_name_match),
            feedback_score,
            feedback_result,
            created_at
        )
    )

    connection.commit()

    record_id = cursor.lastrowid

    connection.close()

    return record_id


# =========================================================
# GET ALL VERIFICATIONS
# =========================================================

def get_all_verifications():
    """
    Return all verification records.
    """

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM verifications
        ORDER BY id DESC
        """
    )

    records = cursor.fetchall()

    connection.close()

    return [
        dict(record)
        for record in records
    ]


# =========================================================
# GET ONE VERIFICATION
# =========================================================

def get_verification(record_id):
    """
    Return a single verification record.
    """

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM verifications
        WHERE id = ?
        """,
        (record_id,)
    )

    record = cursor.fetchone()

    connection.close()

    if record:

        return dict(record)

    return None


# =========================================================
# DELETE VERIFICATION
# =========================================================

def delete_verification(record_id):
    """
    Delete a verification record.
    """

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM verifications
        WHERE id = ?
        """,
        (record_id,)
    )

    connection.commit()

    deleted = cursor.rowcount

    connection.close()

    return deleted > 0


# =========================================================
# DATABASE TEST
# =========================================================

if __name__ == "__main__":

    create_database()

    print(
        "Database created successfully."
    )