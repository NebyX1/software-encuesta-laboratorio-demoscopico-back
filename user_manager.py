#!/usr/bin/env python
from flask import Flask
from database.db import db
from database.config import DATABASE_CONNECTION_URI
from database.models import User
import sys
import getpass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def list_users():
    """
    Listar todos los usuarios existentes
    """
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No hay usuarios registrados en la base de datos.")
            return

        print("\n--- Usuarios registrados ---")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Nombre: {user.name}")
            print(f"Password hash: {user.password_hash[:30]}...")
            print(f"Longitud del hash: {len(user.password_hash)}\n")


def create_user(email, name, password):
    """
    Crear un nuevo usuario con la contraseña correctamente hasheada
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
            print(f"Longitud del hash: {len(new_user.password_hash)} caracteres")
            print(f"Hash: {new_user.password_hash[:30]}...")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {e}")


def update_password(email, password):
    """
    Actualizar la contraseña de un usuario existente
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
            print(f"Contraseña actualizada exitosamente para '{user.name}' ({email}).")
            print(f"Longitud del hash: {len(user.password_hash)} caracteres.")
            print(f"Hash: {user.password_hash[:30]}...")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar la contraseña: {e}")
            return False


def verify_password(email, password):
    """
    Verificar si una combinación de email/contraseña es correcta
    """
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"Error: No se encontró un usuario con email '{email}'.")
            return False

        is_valid = user.check_password(password)
        if is_valid:
            print(
                f"✅ La contraseña es correcta para el usuario '{user.name}' ({email})."
            )
        else:
            print(
                f"❌ La contraseña NO es correcta para el usuario '{user.name}' ({email})."
            )
            print(f"Hash almacenado: {user.password_hash[:30]}...")
            print(f"Longitud del hash: {len(user.password_hash)} caracteres.")

        return is_valid


def show_help():
    print("\nUtilidad de gestión de usuarios para Survey Master Backend")
    print("----------------------------------------------------------")
    print("Comandos disponibles:")
    print("  list                           - Listar todos los usuarios")
    print("  create <email> <nombre>        - Crear un nuevo usuario")
    print("  update <email>                 - Actualizar contraseña de usuario")
    print("  verify <email>                 - Verificar contraseña de usuario")
    print("  help                           - Mostrar este mensaje de ayuda")
    print("----------------------------------------------------------")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    else:
        command = sys.argv[1].lower()

        if command == "list":
            list_users()

        elif command == "create" and len(sys.argv) >= 4:
            email = sys.argv[2]
            name = sys.argv[3]
            password = getpass.getpass("Ingrese la contraseña: ")
            create_user(email, name, password)

        elif command == "update" and len(sys.argv) >= 3:
            email = sys.argv[2]
            password = getpass.getpass("Ingrese la nueva contraseña: ")
            update_password(email, password)

        elif command == "verify" and len(sys.argv) >= 3:
            email = sys.argv[2]
            password = getpass.getpass("Ingrese la contraseña a verificar: ")
            verify_password(email, password)

        elif command == "help":
            show_help()

        else:
            print("Comando no reconocido o faltan argumentos.")
            show_help()
