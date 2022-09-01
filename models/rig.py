from tokenize import String
from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

users = Table("rigs", meta, Column("id", Integer, primary_key=True),
    Column("number", String(255)), 
    Column("zone", String(255)), 
    Column("operator", String(255)),
    Column("owner", String(255)))

meta.create_all(engine)