from sqlalchemy import create_engine, MetaData


server = 'siindependenceserver.database.windows.net'
database = 'AnaliticaSKH'
username = 'indsii'
password = '1nd3p3nd3nc32019*'
driver = '{ODBC Driver 17 for SQL Server}'

engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}')

engine = create_engine(
    f"mssql+pyodbc://{username}:{password}@{server}/{database}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

meta = MetaData()

conn = engine.connect()