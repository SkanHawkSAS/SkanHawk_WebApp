from sqlite3 import Date
from sre_parse import FLAGS
from tokenize import String
from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime
from config.db import meta, engine

opsData = Table("operational_data", meta, Column("id", Integer, primary_key=True),
    Column("fechaHora", DateTime), 
    Column("deviceId", String(255)), 
    Column("cargaGancho", Float),
    Column("posicionBloque", Float),
    Column("velocidadBloque", Float),
    Column("profundidad", Float),
    Column("contadorTuberia", Integer)
)

meta.create_all(engine)