from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Avatars(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'avatars'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_path = Column(String, nullable=False)

    # отношения между остальными таблицами
    user = relationship('Users', back_populates='avatars')