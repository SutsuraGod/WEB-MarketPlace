from sqlalchemy import Column, Integer, String, ForeignKey, Table
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Categories(SqlAlchemyBase, SerializerMixin):
    '''Таблица категорий'''
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category = Column(String, nullable=False)
