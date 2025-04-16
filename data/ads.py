from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Ads(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    city = Column(String, nullable=False)
    modified_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    author = relationship("Users", back_populates="ads")
