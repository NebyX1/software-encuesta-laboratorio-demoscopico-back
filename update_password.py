from flask import Flask
from database.db import db
from database.config import DATABASE_CONNECTION_URI
from database.models import User
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def update_user_password(email, password):
    """
    Actualiza la contraseña de un usuario existente
    """
    with app.app_context():
        # Buscar el usuario
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"Error: No se encontró un usuario con email '{email}'.")
            return False

        # Actualizar la contraseña
        try:
            user.set_password(password)
            db.session.commit()
            print(
                f"Contraseña actualizada exitosamente para el usuario '{user.name}' con email '{email}'."
            )
            print(f"Longitud del hash: {len(user.password_hash)} caracteres.")
            print(f"Hash: {user.password_hash[:30]}...")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar la contraseña: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python update_password.py <email> <nueva_contraseña>")
    else:
        email = sys.argv[1]
        password = sys.argv[2]
        update_user_password(email, password)
