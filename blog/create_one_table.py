from blog.model import Base, engine


def create_tables(tables=None):
    Base.metadata.create_all(engine, tables)


# model中有新增实体类，可能通过此函数单独创建表
create_tables(tables=[Base.metadata.tables['dig']])


