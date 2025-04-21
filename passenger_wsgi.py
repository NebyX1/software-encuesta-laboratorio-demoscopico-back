import sys
import os

# Añadir el directorio actual al path para encontrar los módulos
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación desde wsgi.py
from wsgi import application