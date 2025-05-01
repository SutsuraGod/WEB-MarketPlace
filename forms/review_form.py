from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired


class ReviewForm(FlaskForm):
    '''Форма добавления отзыва'''
    comment = TextAreaField("Комментарий", validators=[DataRequired()])
    rating = RadioField('Оценка', choices=[('5', '5'), ('4', '4'), ('3', '3'), ('2', '2'), ('1', '1')],
                        validators=[DataRequired()])
    submit = SubmitField("Отправить")