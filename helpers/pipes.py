from config.analytic_db import conn
from config.analytic_db import engine
import pandas as pd


def addPipe(name, tq_min, tq_optimum, tq_max):
    query = f''' INSERT INTO [dbo].[pipe_details]
           ([name]
           ,[torque_min]
           ,[torque_optimum]
           ,[torque_max])
     VALUES
           ('{name}', {tq_min}, {tq_optimum}, {tq_max})  '''
    conn.execute(query)

def updatePipe(id_pipe, name, tq_min, tq_optimum, tq_max):
    query = f''' UPDATE [dbo].[pipe_details]
                SET [name] = '{name}'
                    ,[torque_min] = {tq_min}
                    ,[torque_optimum] = {tq_optimum}
                    ,[torque_max] = {tq_max}
                WHERE id = {id_pipe} '''
                
    conn.execute(query)

def deletePipe(id_pipe):
    query = f''' DELETE FROM [dbo].[pipe_details]
      WHERE id = '{id_pipe}' '''
    
    conn.execute(query)