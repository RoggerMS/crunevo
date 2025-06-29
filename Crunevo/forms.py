from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from models import User

class RegistrationForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    career = SelectField('Carrera', choices=[
        ('', 'Selecciona tu carrera'),
        ('ingenieria-sistemas', 'Ingeniería de Sistemas'),
        ('medicina', 'Medicina'),
        ('derecho', 'Derecho'),
        ('administracion', 'Administración'),
        ('psicologia', 'Psicología'),
        ('educacion', 'Educación'),
        ('matematicas', 'Matemáticas'),
        ('fisica', 'Física'),
        ('quimica', 'Química'),
        ('biologia', 'Biología'),
        ('arquitectura', 'Arquitectura'),
        ('economia', 'Economía'),
        ('contabilidad', 'Contabilidad'),
        ('comunicaciones', 'Comunicaciones'),
        ('arte', 'Arte'),
        ('otro', 'Otro')
    ])
    university = StringField('Universidad', validators=[Length(max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor elige otro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado. Por favor usa otro.')

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario o Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])

class NoteUploadForm(FlaskForm):
    title = StringField('Título del apunte', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descripción', validators=[Length(max=1000)])
    subject = StringField('Materia', validators=[DataRequired(), Length(max=100)])
    career = SelectField('Carrera', choices=[
        ('', 'Selecciona la carrera'),
        ('ingenieria-sistemas', 'Ingeniería de Sistemas'),
        ('medicina', 'Medicina'),
        ('derecho', 'Derecho'),
        ('administracion', 'Administración'),
        ('psicologia', 'Psicología'),
        ('educacion', 'Educación'),
        ('matematicas', 'Matemáticas'),
        ('fisica', 'Física'),
        ('quimica', 'Química'),
        ('biologia', 'Biología'),
        ('arquitectura', 'Arquitectura'),
        ('economia', 'Economía'),
        ('contabilidad', 'Contabilidad'),
        ('comunicaciones', 'Comunicaciones'),
        ('arte', 'Arte'),
        ('general', 'General')
    ])
    file = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 'Solo se permiten archivos PDF, imágenes y documentos de Word.')
    ])
    is_public = BooleanField('Hacer público', default=True)

class PostForm(FlaskForm):
    content = TextAreaField('¿Qué quieres compartir?', validators=[DataRequired(), Length(min=1, max=1000)])
    post_type = SelectField('Tipo de publicación', choices=[
        ('general', 'General'),
        ('question', 'Pregunta'),
        ('discussion', 'Discusión')
    ], default='general')
    subject = StringField('Materia (opcional)', validators=[Length(max=100)])

class CommentForm(FlaskForm):
    content = TextAreaField('Escribe tu comentario...', validators=[DataRequired(), Length(min=1, max=500)])

class MessageForm(FlaskForm):
    content = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=1, max=1000)])

class ProfileEditForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=50)])
    bio = TextAreaField('Biografía', validators=[Length(max=500)])
    career = SelectField('Carrera', choices=[
        ('', 'Selecciona tu carrera'),
        ('ingenieria-sistemas', 'Ingeniería de Sistemas'),
        ('medicina', 'Medicina'),
        ('derecho', 'Derecho'),
        ('administracion', 'Administración'),
        ('psicologia', 'Psicología'),
        ('educacion', 'Educación'),
        ('matematicas', 'Matemáticas'),
        ('fisica', 'Física'),
        ('quimica', 'Química'),
        ('biologia', 'Biología'),
        ('arquitectura', 'Arquitectura'),
        ('economia', 'Economía'),
        ('contabilidad', 'Contabilidad'),
        ('comunicaciones', 'Comunicaciones'),
        ('arte', 'Arte'),
        ('otro', 'Otro')
    ])
    university = StringField('Universidad', validators=[Length(max=100)])

class MarketplaceItemForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10, max=1000)])
    price_crolars = IntegerField('Precio en Crolars', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    item_type = SelectField('Tipo de artículo', choices=[
        ('digital', 'Digital'),
        ('physical', 'Físico'),
        ('service', 'Servicio')
    ])
    stock = IntegerField('Stock disponible', validators=[DataRequired(), NumberRange(min=1, max=1000)], default=1)
