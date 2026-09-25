import sqlite3
import hashlib
import secrets


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

AUTH_DATABASE = "users.db"


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )

    return salt, password_hash.hex()


# =========================================================
# VERIFY PASSWORD
# =========================================================

def verify_password(password, salt, stored_hash):

    _, password_hash = hash_password(
        password,
        salt
    )

    return password_hash == stored_hash


# =========================================================
# CREATE AUTH DATABASE
# =========================================================

def create_auth_database():

    connection = sqlite3.connect(
        AUTH_DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            salt TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


# =========================================================
# CREATE USER
# =========================================================

def create_user(username, password):

    create_auth_database()

    username = username.strip()

    if not username or not password:

        return False, "Username and password are required."

    salt, password_hash = hash_password(
        password
    )

    connection = sqlite3.connect(
        AUTH_DATABASE
    )

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password_hash,
                salt
            )

            VALUES (?, ?, ?)
            """,
            (
                username,
                password_hash,
                salt
            )
        )

        connection.commit()

        return True, "User created successfully."

    except sqlite3.IntegrityError:

        return False, "Username already exists."

    finally:

        connection.close()


# =========================================================
# LOGIN USER
# =========================================================

def login_user(username, password):

    create_auth_database()

    connection = sqlite3.connect(
        AUTH_DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            username,
            password_hash,
            salt

        FROM users

        WHERE username = ?
        """,
        (username.strip(),)
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:

        return False

    stored_username = user[0]
    stored_hash = user[1]
    salt = user[2]

    if verify_password(
        password,
        salt,
        stored_hash
    ):

        return True

    return False


# =========================================================
# GET ALL USERS
# =========================================================

def get_users():

    create_auth_database()

    connection = sqlite3.connect(
        AUTH_DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            created_at

        FROM users

        ORDER BY id DESC
        """
    )

    users = cursor.fetchall()

    connection.close()

    return users


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    create_auth_database()

    success, message = create_user(
        "admin",
        "Admin@12345"
    )

    print(message)

    if login_user(
        "admin",
        "Admin@12345"
    ):

        print("Login test successful.")

    else:

        print("Login test failed.")