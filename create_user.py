from flask import Flask
from database.db import db
from database.config import DATABASE_CONNECTION_URI
from database.models import User
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def create_user(email, name, password):
    """
    Crea un nuevo usuario con la contraseña correctamente hasheada
    """
    with app.app_context():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"Error: El usuario con email '{email}' ya existe.")
            return

        # Crear nuevo usuario
        new_user = User(email=email, name=name)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"Usuario '{name}' creado exitosamente con email '{email}'")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python create_user.py <email> <nombre> <contraseña>")
    else:
        email = sys.argv[1]
        name = sys.argv[2]
        password = sys.argv[3]
        create_user(email, name, password)
