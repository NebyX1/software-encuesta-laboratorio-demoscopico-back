from flask import Flask
from database.db import db
from database.config import DATABASE_CONNECTION_URI
from routes import endpoints
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS to allow requests specifically from localhost:5173
CORS(app, origins=["http://localhost:5173"])

app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

# Aquí se registran las rutas
endpoints.init_app(app)
