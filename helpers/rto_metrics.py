import pandas as pd
import numpy as np
from config.db_oxy import engine


# FUNCIONES
def identify_block_movement(block_vel, delta) -> str:
    if block_vel == 0 or delta == 0:
        return 'quieto'
    elif delta > 0:
        return 'subiendo'
    elif delta < 0:
        return 'bajando'
    
    
    
def identify_moment(block_pos, hook_weight, label) -> str:
    if label == 'quieto':
        if block_pos >= 15:
            new_label = 'conn/desc'
        else:
            new_label = 'no_work'
    else:
        if hook_weight > 7000:
            new_label = f'{label} con peso'
        else:
            new_label = f'{label} libre'
    return new_label

def get_data(rig: str, variables: list=[], reg: int=0) -> pd.DataFrame: 
    
    variables = str(variables)
    variables = variables[1:-1]
    variables = variables.replace("'", "")
    if reg == 0:
        query = f''' SELECT {variables} 
                    from [Oxy].[Oxy_Operational_data]
                    WHERE deviceId = '{rig}'
                    ORDER BY fecha_hora DESC'''
    else:
        query = f''' SELECT TOP ({reg}) {variables} 
                    from [Oxy].[Oxy_Operational_data]
                    WHERE deviceId = '{rig}' 
                    ORDER BY fecha_hora DESC'''
                 
    data = pd.read_sql(query, engine)
    
    return data
