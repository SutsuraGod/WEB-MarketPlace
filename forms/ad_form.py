from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, TextAreaField, IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from data import db_session
from data.categories import Categories
from wtforms.validators import ValidationError


def file_required_if_not_existing(form, field):
    has_valid_file = any(file and file.filename for file in field.data)
    if not has_valid_file and not getattr(form, 'images_paths', []):
        raise ValidationError('Пожалуйста, загрузите хотя бы один файл.')


class AdForm(FlaskForm):
    '''Форма для создания объявления'''
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    price = IntegerField("Цена, руб.", validators=[DataRequired()])
    categories = SelectField("Выберите категорию", validators=[DataRequired()])
    city = StringField("Город", validators=[DataRequired()])
    images = MultipleFileField("Загрузите до 5 фотографий", render_kw={'multiple': True}, validators=[
        file_required_if_not_existing,
        FileAllowed(['jpg', 'jpeg', 'png'], "Только изображения!")
    ])
    submit = SubmitField("Отправить")

    def __init__(self, *args, **kwargs):
        super(AdForm, self).__init__(*args, **kwargs)
        session = db_session.create_session()
        cats = session.query(Categories).all()
        self.categories.choices = [(str(cat.id), cat.category) for cat in cats]