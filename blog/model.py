from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT, TINYINT
from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from . import config


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=True, comment='用户名称或昵称，不是登陆名称')
    email = Column(String(64), nullable=False, unique=True)
    password = Column(String(128), nullable=False)

    def __repr__(self):
        return '<User (id={}, name={}, email={})>'.format(self.id, self.name, self.email)


class Post(Base):
    __tablename__ = 'post'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=True)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='作者id，是user.id的外键')
    postdate = Column(DateTime, nullable=False)
    hits = Column(Integer, default=0, nullable=False, index=True)

    author = relationship('User')   # 写类名称的字符串
    content = relationship('Content', uselist=False)  # 一对一设置为False，表示在post这个表中如果想查询信息，一个文章id只能对应一个文章的内容，反之也是，所以这种关系使用False

    def __repr__(self):
        return '<Post (id={}, title={}, author_id={})>'.format(self.id, self.title, self.author_id)


class Content(Base):
    __tablename__ = 'content'

    id = Column(BigInteger, ForeignKey('post.id'), primary_key=True, comment='是post.id的外键')
    content = Column(LONGTEXT, nullable=False)

    def __repr__(self):
        return '<Content (id={}, content={})>'.format(self.id, self.content[:20])


class Dig(Base):
    """
    赞，踩表
    """
    __tablename__ = 'dig'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    post_id = Column(BigInteger, ForeignKey('post.id'), nullable=False)
    state = Column(TINYINT, default=0, nullable=False)
    pubdate = Column(DateTime, nullable=False)

    user = relationship('User')

    # __table_args__ 是为字段增加一些复杂的约束，UniqueConstraint 表示是唯一键约束，这里用了联合唯一键，__table_args__参数是一个元组
    # 文档：https://docs.sqlalchemy.org/en/13/core/constraints.html#unique-constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_user_id_post_id'),
    )


# 数据为连接
engine = create_engine(config.URL, echo=config.DATABASE_DEBUG)


# 创建删除表
def create_tables():
    Base.metadata.create_all(engine)  # 调用此方法可以创建定义的所有实体类对应的表


def drop_tables():
    Base.metadata.drop_all(engine)  # 调用此方法可以删除定义的所有实体类对应的表


# 获取session
Session = sessionmaker(engine)
session = Session()



