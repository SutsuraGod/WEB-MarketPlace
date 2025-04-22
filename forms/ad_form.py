from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, TextAreaField, IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from data import db_session
from data.categories import Categories


class AdForm(FlaskForm):
    '''Форма для создания объявления'''
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    price = IntegerField("Цена, руб.", validators=[DataRequired()])
    categories = SelectField("Выберите категорию", validators=[DataRequired()])
    city = StringField("Город", validators=[DataRequired()])
    images = MultipleFileField("Загрузите до 5 фотографий", render_kw={'multiple': True}, validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], "Только изображения!")
    ])
    submit = SubmitField("Создать объявление")

    def __init__(self, *args, **kwargs):
        super(AdForm, self).__init__(*args, **kwargs)
        session = db_session.create_session()
        cats = session.query(Categories).all()
        self.categories.choices = [(str(cat.id), cat.category) for cat in cats]