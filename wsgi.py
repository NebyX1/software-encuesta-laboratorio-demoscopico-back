import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio de tu aplicación al path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
