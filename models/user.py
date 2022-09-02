from enum import unique
from tokenize import String
from sqlalchemy import Table, Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

users = Table("users", meta, Column("id", Integer, primary_key=True),
    Column("name", String(255)), 
    Column("email", String(255), unique = True), 
    Column("password", String(255)),
    Column("company", String(255)),
    Column("role", String(255)),
    Column("accessLevel", Integer))

meta.create_all(engine)