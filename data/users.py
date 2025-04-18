from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    # отношения между остальными таблицами
    ads = relationship("Ads", back_populates="author")
    reviews = relationship("Reviews", back_populates="author")

    def __repr__(self):
        '''Изменение формата вывода пользователя в консоль'''
        return f"<User> {self.id} {self.username}"

    def set_password(self, password):
        '''Хеширование и сохранение пароля'''
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        '''Проверка на валидность введенного пароля'''
        return check_password_hash(self.hashed_password, password)
