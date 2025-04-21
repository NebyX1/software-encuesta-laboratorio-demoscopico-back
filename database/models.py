from flask_login import UserMixin
from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import uuid


# --- User Model (formerly Admin) ---
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Aumentado a 255 caracteres
    name = db.Column(db.String(1000))

    def set_password(self, password):
        # Usar método 'pbkdf2:sha256' que es compatible con Werkzeug
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        # Exclude password_hash from serialization
        return {"id": self.id, "name": self.name, "email": self.email}


# --- ValidToken Model ---
class ValidToken(db.Model):
    __tablename__ = 'valid_tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    used = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationship back to SurveyResponse (one-to-one)
    survey_response = db.relationship('SurveyResponse', back_populates='valid_token', uselist=False)

    def __repr__(self):
        return f'<ValidToken {self.token} Used: {self.used}>'


# --- SurveyResponse Model ---
class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)

    # Fields from the form
    genero = db.Column(db.String(50))
    localidad = db.Column(db.String(100))
    edad = db.Column(db.String(50))
    intendente = db.Column(db.String(150))
    balotaje = db.Column(db.String(100))
    estado = db.Column(db.String(150))
    partido_vs_persona = db.Column(db.String(150))
    percepcion_mario = db.Column(db.String(50))
    percepcion_daniel = db.Column(db.String(50))
    problemas = db.Column(db.String(150))
    auditoria = db.Column(db.String(250))
    telefono = db.Column(db.String(20))

    # Metadata fields
    submission_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    device_type = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))

    # Foreign Key to ValidToken
    token_id = db.Column(db.Integer, db.ForeignKey('valid_tokens.id'), unique=True, nullable=False)

    # Relationship to ValidToken
    valid_token = db.relationship('ValidToken', back_populates='survey_response')

    def __repr__(self):
        return f'<SurveyResponse {self.id} - Token ID: {self.token_id}>'

    # Optional: Serialization method for API responses
    def serialize(self):
        return {
            "id": self.id,
            "genero": self.genero,
            "localidad": self.localidad,
            "edad": self.edad,
            "intendente": self.intendente,
            "balotaje": self.balotaje,
            "estado": self.estado,
            "partido_vs_persona": self.partido_vs_persona,
            "percepcion_mario": self.percepcion_mario,
            "percepcion_daniel": self.percepcion_daniel,
            "problemas": self.problemas,
            "auditoria": self.auditoria,
            "telefono": self.telefono,
            "submission_timestamp": self.submission_timestamp.isoformat() if self.submission_timestamp else None,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "token_id": self.token_id
        }
