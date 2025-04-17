from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Reviews(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ad_id = Column(Integer, ForeignKey('ads.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    author = relationship('Users', back_populates='reviews')
    ad = relationship('Ads', back_populates='reviews')
