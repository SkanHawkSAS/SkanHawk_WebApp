from sqlalchemy import create_engine, MetaData
import os

PORT = os.environ['PORT']
DATABASE = os.environ['DATABASE']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST= os.environ['DB_HOST']




engine = create_engine(f'postgresql+pygresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{PORT}/{DATABASE}')

meta = MetaData()

conn = engine.connect()