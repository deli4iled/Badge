from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
presenza = Table('presenza', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('entrata', DATETIME),
    Column('uscita', DATETIME),
)

entrata = Table('entrata', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('entrata', DateTime),
    Column('uscita', DateTime),
)

uscita = Table('uscita', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('entrata', DateTime),
    Column('uscita', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['presenza'].drop()
    post_meta.tables['entrata'].create()
    post_meta.tables['uscita'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['presenza'].create()
    post_meta.tables['entrata'].drop()
    post_meta.tables['uscita'].drop()
