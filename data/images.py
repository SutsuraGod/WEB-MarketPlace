from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Images(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ad_id = Column(Integer, ForeignKey('ads.id'))
    image_path = Column(String, nullable=False)

    # отношения между остальными таблицами
    ad = relationship('Ads', backref='images')