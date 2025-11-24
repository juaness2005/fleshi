from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from appfleshi.models import User

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")

class RegisterForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    username = StringField("Nome do Usuário", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField("Confirmar senha", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Criar Conta")

def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        return ValidationError("E-mail já cadastrado!")

    return None