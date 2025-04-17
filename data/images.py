from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Images(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ad_id = Column(Integer, ForeignKey('ads.id'))
    image_path = Column(String, nullable=False)

    ad = relationship('Ads', backref='images')