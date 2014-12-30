from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
entrata = Table('entrata', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('entrata', DATETIME),
)

entrata = Table('entrata', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('data', Date),
    Column('ora', Time),
)

uscita = Table('uscita', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('uscita', DATETIME),
)

uscita = Table('uscita', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('data', Date),
    Column('ora', Time),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['entrata'].columns['entrata'].drop()
    post_meta.tables['entrata'].columns['data'].create()
    post_meta.tables['entrata'].columns['ora'].create()
    pre_meta.tables['uscita'].columns['uscita'].drop()
    post_meta.tables['uscita'].columns['data'].create()
    post_meta.tables['uscita'].columns['ora'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['entrata'].columns['entrata'].create()
    post_meta.tables['entrata'].columns['data'].drop()
    post_meta.tables['entrata'].columns['ora'].drop()
    pre_meta.tables['uscita'].columns['uscita'].create()
    post_meta.tables['uscita'].columns['data'].drop()
    post_meta.tables['uscita'].columns['ora'].drop()
