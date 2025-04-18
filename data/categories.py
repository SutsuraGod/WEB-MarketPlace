from sqlalchemy import Column, Integer, String, ForeignKey, Table
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

association_table = Table(
    'ads_to_categories',
    SqlAlchemyBase.metadata,
    Column('ad_id', ForeignKey('ads.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True)
)


class Categories(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category = Column(String, nullable=False)
