from sqlalchemy import create_engine, MetaData
import os

PORT = 3306
DATABASE = 'skh_db'
DB_USER = 'root'
DB_PASSWORD = 'skanhawkpassword'
DB_HOST= 'localhost'

engine = create_engine(f'postgresql+pygresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{PORT}/{DATABASE}')

meta = MetaData()

conn = engine.connect()