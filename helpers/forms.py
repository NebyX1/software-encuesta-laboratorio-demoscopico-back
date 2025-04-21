from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField(label="Email:", validators=[InputRequired(), Email(), Length(max=250)])
    password = PasswordField(label="Password:", validators=[InputRequired(), Length(min=8, max=100)])
    submit = SubmitField(label="Sign in")


class SurveyResponseForm(FlaskForm):
    genero = StringField(label="Género", validators=[Length(max=50)])
    localidad = StringField(label="Localidad", validators=[Length(max=100)])
    edad = StringField(label="Edad", validators=[Length(max=50)])
    intendente = StringField(label="Intendente", validators=[Length(max=150)])
    balotaje = StringField(label="Balotaje", validators=[Length(max=100)])
    estado = StringField(label="Estado", validators=[Length(max=150)])
    partido_vs_persona = StringField(label="Partido vs Persona", validators=[Length(max=150)])
    percepcion_mario = StringField(label="Percepción Mario", validators=[Length(max=50)])
    percepcion_daniel = StringField(label="Percepción Daniel", validators=[Length(max=50)])
    problemas = TextAreaField(label="Problemas", validators=[Length(max=150)])
    auditoria = TextAreaField(label="Auditoría", validators=[Length(max=250)])
    telefono = StringField(label="Teléfono", validators=[Length(max=20)])
    submit = SubmitField(label="Enviar Encuesta")
