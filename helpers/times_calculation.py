import pandas as pd
import numpy as np
import datetime
import tabula


# Función para calcular las pruebas de presión
def pruebas_presion(fecha_inicio, fecha_fin, cliente, rig, pozo, actividad, detalle_tuberia):    
    #Se resta 1 dia al inicio del viaje para tomar pruebas realizadas antes de iniciar
    InicioViajePruebas= fecha_inicio - datetime.timedelta(days=1)
    # Se suman dos dias al fin del viaje para tomar pruebas realizadas al finalizar el viaje
    FinViajePruebas= fecha_fin + datetime.timedelta(days=1)
    
    
    if cliente == 'ECOPETROL':
        
        from config.db_ecop import engine as engine_op
        
        # Consulta SQL para solicitar los datos operacionales
        query = '''SELECT presion_bomba, barriles_por_minuto, fecha_hora, deviceId, profundidad
        FROM tlc.Ecopetrol_Operational_data_SH
        WHERE (fecha_hora BETWEEN '{}' AND '{}') AND deviceID ='{}' '''.format(InicioViajePruebas, FinViajePruebas, rig)
    
    else:
        
        from config.db_oxy import engine as engine_op
        # Consulta SQL para solicitar los datos operacionales
        query = '''SELECT presion_bomba, barriles_por_minuto, fecha_hora, deviceId
            FROM Oxy.Oxy_Operational_data
            WHERE (fecha_hora BETWEEN '{}' AND '{}') AND deviceID ='{}' '''.format(InicioViajePruebas, FinViajePruebas, rig)

    # Se crea un DataFrame con los datos de la consulta SQL.
    datasetPruebas = pd.read_sql(query, engine_op)

    
    profundidad_pozo=0
    numeroPrueba=0
    bandera=0
    # Se crea la variable df_final en la cual se registran los datos correspondiente a cada inicio y fin de una prueba presion
    df_final = pd.DataFrame(columns = ['presion_bomba' , 'profundidad', 'fecha_hora','barriles_por_minuto','numeroPrueba'])
    # Se itera datasetPruebas con el fin de escoger los datos que corresponden a una prueba de presion
    for index, row in datasetPruebas.iterrows():
        # Condicional para revisar el inicio de una prueba de presion
        # (Una prueba de presion inicia con caudal, con presion en la bomba superior a 100 y con un cambio en la profundidad al registrado en la prueba anterior)
        if row["barriles_por_minuto"] > 0 and row["presion_bomba"]>100 and row["profundidad"] != profundidad_pozo:
            numeroPrueba=numeroPrueba+1
            # Se toman 10 datos de iniciada la prueba para una grafica mas exacta
            df_final= df_final.append({'presion_bomba': datasetPruebas["presion_bomba"][index-10],'profundidad': datasetPruebas["profundidad"][index-10],'fecha_hora': datasetPruebas["fecha_hora"][index-10],'barriles_por_minuto': datasetPruebas["barriles_por_minuto"][index-10],'numeroPrueba': numeroPrueba}, ignore_index=True)     
            profundidad_pozo = row["profundidad"]
        # Condicional para revisar si la prueba termino
        # (Una prueba termina cuando ya no se registra caudal y la presion decae, adicionalmente la profundidad se tiene que mantener para que sea parte de la misma prueba)
        elif row["barriles_por_minuto"] == 0 and row["presion_bomba"]>50 and ((profundidad_pozo-10) < row["profundidad"] < (profundidad_pozo+10) ):
            profundidad_pozo = row["profundidad"]
            # Se toman 20 datos despues de finalizada la prueba con el fin de observar el descenso de la prueba
            df_final= df_final.append({'presion_bomba': datasetPruebas["presion_bomba"][index+20],'profundidad': datasetPruebas["profundidad"][index+20],'fecha_hora': datasetPruebas["fecha_hora"][index+20],'barriles_por_minuto': datasetPruebas["barriles_por_minuto"][index+20],'numeroPrueba': numeroPrueba}, ignore_index=True)
    # Se eliman datos que pudieron quedar duplicados a tomar +- datos de los de un inicio y fin de prueba
    df_final=df_final.drop_duplicates(['fecha_hora'], keep='first')
    # Con esta expresion lambda se toman unicamente los registros permitentes al primer y ultimo dato de la prueba
    df_final=df_final.groupby('numeroPrueba', as_index=False).apply(lambda x: x if len(x)==1 else x.iloc[[0, -1]]).reset_index(level=0, drop=True)
    # Se restauran los indices del dataset despues del filtrado
    df_final=df_final.reset_index(drop=True)
    # Creacion del dataFrame final, correspondiente a todos los registros de las pruebas
    df_prueba= pd.DataFrame()
    # Iteracion de las fechas de cada prueba registrada
    # Se itera de dos en dos para ahorrar tiempo de ejecucion y por medio del index se accede a la posicion que nos saltamos
    for index in range (0, len(df_final),2):
        if(index != (len(df_final)-1)):                            
            # Se hace una mascara de filtro en el dataSet traido de la base de datos donde se obtiene unicamente los registros definidos por cada prueba
            mask = (datasetPruebas['fecha_hora'] >= df_final['fecha_hora'][index]) & (datasetPruebas['fecha_hora'] <= df_final['fecha_hora'][index+1])
            filtered_df=datasetPruebas.loc[mask]
            # Se asigna el numero de prueba a los registros
            filtered_df=filtered_df.assign(Prueba=df_final['numeroPrueba'][index])
            # Concatenamos el dataframe con todos los registros que se necesitan para guardar la prueba
            df_prueba = pd.concat([df_prueba, filtered_df], axis=0)
    return df_prueba

# Función para detectar los momentos del bloque y el numero de tuberia correspondiente
def deteccion_momentos_bloque(data, actividad, tuberia):
    
    # Convierto la columna de fecha_hora a formato datetime
    data["fecha_hora"] = pd.to_datetime(data["fecha_hora"])
    
    # Creo una columna nueva para asignar los momentos del bloque al que pertenece el registro
    data["Momento"] = np.zeros(len(data)) 
    
    # Calculo los delta de la posicion bloque entre el registro actual y el anterior
    delta_bloque = np.zeros(len(data))
    for i in range(len(data)):
        if i != 0:
            pos = data.iloc[i, 2]
            pos_bef = data.iloc[i-1, 2]
            delta = pos-pos_bef
            delta_bloque[i] = delta
    # Creo una columna para guardar los deltas de la posicion bloque
    data["delta_bloque"] = delta_bloque
    peso_default = 6500
    if 'ESP' in actividad or 'BES' in actividad or 'TUBING' in tuberia:
        peso_default = 4900
    
    if 'POOH' in actividad:
        # Se definen algunas condiciones de operacion
        filter1 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] == 0) & (data["Posición Bloque [ft]"] > 20) # Cuando el peso del gancho es menor a 6500 lb y el bloque no se está moviendo y el bloque se encuentra arriba
        filter2 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] < 0) # Cuando el peso del gancho es menor a 6500 lb y el bloque se está moviendo con un delta negativo
        filter3 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] > 0) # Cuando el peso del gancho es menor a 6500 lb y el bloque se está moviendo con un delta positivo
        filter4 = (data["Carga Gancho [lb]"]>peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] < 0) # Cuando el peso del gancho es mayor a 6500 lb y el bloque se está moviendo con un delta negativo
        filter5 = (data["Carga Gancho [lb]"]>peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] > 0) # Cuando el peso del gancho es mayor a 6500 lb y el bloque se está moviendo con un delta positivo
        filter6 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] == 0) & (data["Posición Bloque [ft]"] < 20) # Cuando el peso del gancho es menor a 6500 lb y el bloque no se está moviendo y el bloque se encuentra abajo
        filter7 = (data["Carga Gancho [lb]"]>peso_default) & (data["Velocidad Bloque [ft/min]"] == 0) # Cuando el bloque no se está moviendo y tiene peso 
        
        # Defino los momentos dependiendo las condiciones definidas anteriormente
        data.loc[filter1, "Momento"] = "Desconexión"
        data.loc[filter2, "Momento"] = "Bajando Libre"
        data.loc[filter3, "Momento"] = "Subiendo Libre"
        data.loc[filter4, "Momento"] = "Entrando en cuña"
        data.loc[filter5, "Momento"] = "Subiendo con Peso"
        data.loc[filter6, "Momento"] = "En cuña"
        data.loc[filter7, "Momento"] = "Quieto con peso"
        
        # Se hacen algunas correciones 
        for i in range(len(data)):
            try:
                if i != 0:
                    op = data.iloc[i, -2]
                    op_next = data.iloc[i+1, -2]
                    op_bef = data.iloc[i-1, -2]
                    
                    if op == "Bajando Libre" and op_bef == "Entrando en cuña":
                        data.iloc[i, -2] = "Entrando en cuña"

                    elif str(op) == "0.0":
                        data.iloc[i, -2] = op_bef            
            except:
                pass
    elif 'RIH' in actividad:
        # Se definen algunas condiciones de operacion
        filter1 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] == 0) & (data["Posición Bloque [ft]"] > 20) & (data["delta_bloque"] == 0)# Si el peso del gancho está es menor a 6500 lb y el bloque no se está moviendo
        filter2 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] < 0) #Si el peso del gancho es menor a 6500 lb y el bloque se está moviendo con un delta negativo
        filter3 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] > 0) #Si el peso del gancho es menor a 6500 lb y el bloque se está moviendo con un delta positivo
        filter4 = (data["Carga Gancho [lb]"]>peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] < 0) # Si el peso del gancho es mayor a 6500 lb y el bloque se está moviendo con un delta negativo
        filter5 = (data["Carga Gancho [lb]"]>peso_default) & (data["Velocidad Bloque [ft/min]"] != 0) & (data["delta_bloque"] > 0) # Si el peso del gancho es mayor a 6500 lb y el bloque se está moviendo con un delta positivo
        filter6 = (data["Carga Gancho [lb]"]<peso_default) & (data["Velocidad Bloque [ft/min]"] == 0) & (data["Posición Bloque [ft]"] < 20) # Cuando el peso del gancho es menor a 6500 lb y el bloque no se está moviendo y el bloque se encuentra abajo
        filter7 = (data["Carga Gancho [lb]"]>peso_default) & (data["Velocidad Bloque [ft/min]"] == 0) # Cuando el bloque no se está moviendo y tiene peso 

        data.loc[filter1, "Momento"] = "Conexión"
        data.loc[filter2, "Momento"] = "Bajando Libre"
        data.loc[filter3, "Momento"] = "Subiendo Libre"
        data.loc[filter4, "Momento"] = "Bajando con Peso"
        data.loc[filter5, "Momento"] = "Saliendo de cuña"
        data.loc[filter6, "Momento"] = "En cuña"
        data.loc[filter7, "Momento"] = "Quieto con peso"
        
        # Se hace algunas correcciones
        for i in range(len(data)):
            try:
                if i != 0:
                    op = data.iloc[i, -2]
                    op_next = data.iloc[i+1, -2]
                    op_bef = data.iloc[i-1, -2]

                    if op == "Conexión" and op_next == "Subiendo Libre":
                        data.iloc[i+1, -2] = "Conexión"
                    elif op == "Conexión" and op_next == "Bajando Libre":
                        data.iloc[i+1, -2] = "Conexión"
                    elif op == "Conexión" and op_bef == "Subiendo Libre":
                        data.iloc[i, -2] = "Bajando Libre"
                    elif op == "Saliendo de cuña" and op_bef == "Subiendo Libre":
                        data.iloc[i, -2] = "Subiendo Libre"
                    elif op == "Bajando Libre" and op_bef == "Subiendo Libre":
                        data.iloc[i, -2] = "Subiendo Libre"
                    elif op == "Subiendo Libre" and op_bef == "Saliendo de cuña":
                        data.iloc[i-1, -2] = "Subiendo Libre"
                    elif str(op) == "0.0":
                        data.iloc[i, -2] = op_bef
            except:
                pass    
    else:
        print('Operación desconocida.')
        
    # Se procede a calcular el numero de juntas
    
    # Obtengo donde empiezan y termina cada uno de los momentos
    date_begin = []
    steps = []
    indexs = []
    curr_step = ""
    
    for i in range(len(data)):
        if curr_step != data.iloc[i, -2]:
            date_begin.append(data.iloc[i, 1])
            curr_step = data.iloc[i, -2]
            indexs.append(i)
            steps.append(curr_step)
    
    # Creo un dataframe con los inicios de cada actividad        
    s = pd.DataFrame()
    s["indexs"] = indexs
    s["date_time"] = date_begin
    s["ops"] = steps
    
    
    # Calculo los tubos y el inicio de cada una de las conexiones
    indx = []
    for i in range(len(s)):
        try:
            op_bef = s.iloc[i-1, -1]
            op = s.iloc[i, -1]
            op_bef_bef = s.iloc[i-2, -1]
            op_next = s.iloc[i+1, -1]
            op_next_next = s.iloc[i+2, -1]
            
            if 'POOH' in actividad:

                if op == "Desconexión" and op_next == "Subiendo Libre" :
                    
                    if s.iloc[i-2, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-2, -3])
                    elif s.iloc[i-3, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-3, -3])
                    elif s.iloc[i-4, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-4, -3])
                    elif s.iloc[i-5, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-5, -3])
                    elif s.iloc[i-6, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-6, -3])
                    elif s.iloc[i-7, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-7, -3])
                    elif s.iloc[i-8, -1] == "Subiendo con Peso":
                        indx.append(s.iloc[i-8, -3])
                    
            elif 'RIH' in actividad:
                if (op_bef == "Bajando Libre" or op_bef == "Subiendo Libre") and op == "Conexión" and op_bef_bef != "Conexión" and s.iloc[i-3, -1] != "Conexión":
                    
                    
                    if s.iloc[i-1, -1] == "Subiendo Libre" and (s.iloc[i-2, -1] == "Bajando con Peso" or s.iloc[i-3, -1] == "Bajando con Peso" or s.iloc[i-4, -1] == "Bajando con Peso" or s.iloc[i-5, -1] == "Bajando con Peso" or s.iloc[i-6, -1] == "Bajando con Peso" or s.iloc[i-7, -1] == "Bajando con Peso" or s.iloc[i-8, -1] == "Bajando con Peso" or s.iloc[i-9, -1] == "Bajando con Peso" or s.iloc[i-10, -1] == "Bajando con Peso" or s.iloc[i-11, -1] == "Bajando con Peso" or s.iloc[i-12, -1] == "Bajando con Peso"):
                        indx.append(s.iloc[i-1, -3])
                    elif s.iloc[i-2, -1] == "Subiendo Libre" and (s.iloc[i-3, -1] == "Bajando con Peso" or s.iloc[i-4, -1] == "Bajando con Peso" or s.iloc[i-5, -1] == "Bajando con Peso" or s.iloc[i-6, -1] == "Bajando con Peso" or s.iloc[i-7, -1] == "Bajando con Peso" or s.iloc[i-8, -1] == "Bajando con Peso" or s.iloc[i-9, -1] == "Bajando con Peso" or s.iloc[i-10, -1] == "Bajando con Peso" or s.iloc[i-11, -1] == "Bajando con Peso" or s.iloc[i-12, -1] == "Bajando con Peso"):
                        indx.append(s.iloc[i-2, -3])
                    elif s.iloc[i-3, -1] == "Subiendo Libre" and s.iloc[i-5, -1] == "Bajando con Peso":
                        indx.append(s.iloc[i-3, -3] )
                    elif s.iloc[i-4, -1] == "Subiendo Libre" and s.iloc[i-6, -1] == "Bajando con Peso":
                        indx.append(s.iloc[i-4, -3] )
                    elif s.iloc[i-5, -1] == "Subiendo Libre" and s.iloc[i-7, -1] == "Bajando con Peso":
                        indx.append(s.iloc[i-5, -3] )
                    elif s.iloc[i-6, -1] == "Subiendo Libre" and s.iloc[i-8, -1] == "Bajando con Peso":
                        indx.append(s.iloc[i-6, -3] )
                    elif s.iloc[i-7, -1] == "Subiendo Libre" and s.iloc[i-9, -1] == "Bajando con Peso":
                        indx.append(s.iloc[i-7, -3] )
                    elif s.iloc[i-8, -1] == "Subiendo Libre" and s.iloc[i-10, -1] == "Bajando con Peso":
                        indx.append(s.iloc[i-8, -3])
                    elif s.iloc[i-1, -1] == "Subiendo Libre":
                        indx.append(s.iloc[i-1, -3])
                    
                    
        except:
            pass
        
    data.reset_index(drop=True, inplace=True)
    ids = len(data)-1
    indx2 = []
    for item in indx:
        if item not in indx2:
            indx2.append(item)
    indx2.sort()
    indx = indx2
    # Asigno el numero de tubo correspondiente a cada registro
    ind = 0
    tuberia = []
    contador = 0
    for i in indx:
        multip = i - ind
        if multip > 10:
            ind = i
            tubs = [contador]*multip
            contador += 1
            tuberia += tubs
    diff = ids - len(tuberia) +1
    tubs = [contador]*diff
    tuberia += tubs
    len(tuberia)
    
    data["Tuberia #"] = tuberia
    
    # Basado en promedio de posición bloque determino si el viaje fue en sencillos o dobles
    if data["Posición Bloque [ft]"].mean() < 25:
        data["Tipo de Conexión"] = ["Sencillos"]*len(data)
    else:
        data["Tipo de Conexión"] = ["Dobles"]*len(data)
    
    return data

# Función para calcular los tiempos del viaje
def tiempos_tuberia(data, actividad):
    
    maxTub = data.iloc[-1, -2]
    fecha_hora_inicio = []
    fecha_hora_fin = []
    tiempo_cuna = []
    tiempo_carga_mov = []
    tiempo_carga_stop = []
    tiempo_libre_total = []
    tiempo_bajando_libre = []
    tiempo_subiendo_libre = []
    tiempo_conexion_desconexion = []
    tiempo_manipulacion = []
    conexion = []
    velocidad_subiendo_libre = []
    velocidad_bajando_libre = []
    velocidad_carga = []
    carga_maxima = []
    carga_minima = []
    carga_promedio = []
    profundidad_maxima = []
    TQ_pot = []
    TQ_hid = []
    
    peso_default = 6500
    if 'ESP' in actividad or 'BES' in actividad:
        peso_default = 4900
    
    if 'POOH' in actividad:

        for i in range(1, maxTub+1):
            try: 
                filter_tub = (data["Tuberia #"] == i)
                data_tub = data.loc[filter_tub]
                
                
                fecha_hora_inicio.append(data_tub.iloc[0, 1])
                fecha_hora_fin.append(data_tub.iloc[-1, 1])
                conexion.append(i)
                # Obtengo cuantos minutos se gastaron en cada operacion en total
                times = {}

                t = data_tub["Momento"].value_counts()
                counter = 0
                flagConex = False
                flagSubLib = False
                flagBajPes = False
                flagBajLib = False
                flagStopPes = False
                flagCuna = False
                tiempo_libre_unit = 0

                pos_max = 0
                pos_min = 0

                data_tq_hid = data_tub["TQ. Llave Hid.  Max [lb*ft]"]
                data_tq_pot = data_tub["TQ. Llave Pot.  Max [lb*ft]2"]
                data_prof = data_tub["Profundidad [ft]"]

                tq_hid_max = data_tq_hid.max()

                tq_pot_max = data_tq_pot.max()
                
                prof_max = data_prof.max()

                TQ_hid.append(tq_hid_max)
                TQ_pot.append(tq_pot_max)
                profundidad_maxima.append(prof_max)

                
                for index, value in t.items():
                    time = np.around((value * 4)/60, 2)
                    
                    data_pos = data_tub["Posición Bloque [ft]"].loc[data_tub["Momento"] == index]
                    
                    pos_max = data_pos.max()
                    pos_min = data_pos.min()                

                    if index == "Desconexión":
                        tiempo_conexion_desconexion.append(time)
                        flagConex = True

                    elif index == "Subiendo con Peso":

                        tiempo_carga_mov.append(time)
                        vel = (pos_max - pos_min)/time
                        velocidad_carga.append(vel)
                        

                        ## ANALISIS DE CARGA
                        data_carg = data_tub["Carga Gancho [lb]"].loc[data_tub["Momento"] == index]
                        data_carg = data_carg.loc[data_carg>peso_default]
                        carga_max = data_carg.max()
                        carga_min = data_carg.min()
                        carga_mean = data_carg.mean()

                        carga_maxima.append(carga_max)
                        carga_minima.append(carga_min)
                        carga_promedio.append(carga_mean)

                        flagBajPes = True

                    elif index == "Quieto con peso":
                        tiempo_carga_stop.append(time)
                        flagStopPes = True

                    elif index == "En cuña":
                        tiempo_cuna.append(time)
                        flagCuna = True
                    
                    elif index == "Subiendo Libre":
                        tiempo_libre_unit += time
                        vel = (pos_max - pos_min)/time
                        tiempo_subiendo_libre.append(time)
                        velocidad_subiendo_libre.append(vel)
                        flagSubLib = True

                    elif index == "Bajando Libre":
                        tiempo_libre_unit += time
                        vel = (pos_max - pos_min)/time
                        tiempo_bajando_libre.append(time)
                        velocidad_bajando_libre.append(vel)
                        flagBajLib = True
                
                tiempo_libre_total.append(tiempo_libre_unit)
                    
                # Verifico que haya entrado a agregar algun valor a los arrays. Si no, no hay tiempos de esa actividad entonces se agrega un 0
                if not flagConex:
                    tiempo_conexion_desconexion.append(0)
                if not flagBajPes:
                    velocidad_carga.append(0)
                    tiempo_carga_mov.append(0)
                if not flagStopPes:
                    tiempo_carga_stop.append(0)
                if not flagCuna:
                    tiempo_cuna.append(0)
                if not flagBajLib:
                    velocidad_bajando_libre.append(0)
                    tiempo_bajando_libre.append(0)
                if not flagSubLib:
                    velocidad_subiendo_libre.append(0)
                    tiempo_subiendo_libre.append(0)
            except Exception as e:
                print(i) 
                print(e)

    elif 'RIH' in actividad:
        for i in range(1, maxTub+1):
            try: 
                filter_tub = (data["Tuberia #"] == i)
                data_tub = data.loc[filter_tub]
                
                
                fecha_hora_inicio.append(data_tub.iloc[0, 1])
                fecha_hora_fin.append(data_tub.iloc[-1, 1])
                conexion.append(i)
                
                times = {}

                t = data_tub["Momento"].value_counts()
                counter = 0
                flagConex = False
                flagSubLib = False
                flagBajPes = False
                flagBajLib = False
                flagStopPes = False
                flagCuna = False
                tiempo_libre_unit = 0
                
                pos_max = 0
                pos_min = 0

                data_tq_hid = data_tub["TQ. Llave Hid.  Max [lb*ft]"]
                data_tq_pot = data_tub["TQ. Llave Pot.  Max [lb*ft]2"]
                data_prof = data_tub["Profundidad [ft]"]

                tq_hid_max = data_tq_hid.max()

                tq_pot_max = data_tq_pot.max()
                
                prof_max = data_prof.max()

                TQ_hid.append(tq_hid_max)
                TQ_pot.append(tq_pot_max)
                profundidad_maxima.append(prof_max)
                
                for index, value in t.items():
                    
                    time = np.round((value * 4)/60, 2)
                    
                    data_pos = data_tub["Posición Bloque [ft]"].loc[data_tub["Momento"] == index]
                    
                    pos_max = data_pos.max()
                    pos_min = data_pos.min()

                    if index == "Conexión":
                        tiempo_conexion_desconexion.append(time)
                        flagConex = True

                    elif index == "Bajando con Peso":

                        tiempo_carga_mov.append(time)
                        vel = (pos_max - pos_min)/time
                        velocidad_carga.append(vel)
                        
                        ## ANALISIS DE CARGA
                        data_carg = data_tub["Carga Gancho [lb]"].loc[data_tub["Momento"] == index]
                        data_carg = data_carg.loc[data_carg>peso_default]
                        carga_max = data_carg.max()
                        carga_min = data_carg.min()
                        carga_mean = data_carg.mean()

                        carga_maxima.append(carga_max)
                        carga_minima.append(carga_min)
                        carga_promedio.append(carga_mean)

                        flagBajPes = True

                    elif index == "Quieto con peso":
                        tiempo_carga_stop.append(time)
                        flagStopPes = True

                    elif index == "En cuña":
                        tiempo_cuna.append(time)
                        flagCuna = True
                    
                    elif index == "Subiendo Libre":
                        tiempo_libre_unit += time
                        vel = (pos_max - pos_min)/time
                        tiempo_subiendo_libre.append(time)
                        velocidad_subiendo_libre.append(vel)
                        flagSubLib = True

                    elif index == "Bajando Libre":
                        tiempo_libre_unit += time
                        vel = (pos_max - pos_min)/time
                        tiempo_bajando_libre.append(time)
                        velocidad_bajando_libre.append(vel)
                        flagBajLib = True
                
                tiempo_libre_total.append(tiempo_libre_unit)
                    
                # Verifico que haya entrado a agregar algun valor a los arrays. Si no, no hay tiempos de esa actividad entonces se agrega un 0
                if not flagConex:
                    tiempo_conexion_desconexion.append(0)
                if not flagBajPes:
                    velocidad_carga.append(0)
                    tiempo_carga_mov.append(0)
                        
                    ## ANALISIS DE CARGA
                    data_carg = data_tub["Carga Gancho [lb]"].loc[data_tub["Momento"] == index]
                    data_carg = data_carg.loc[data_carg>peso_default]
                    carga_max = data_carg.max()
                    carga_min = data_carg.min()
                    carga_mean = data_carg.mean()

                    carga_maxima.append(carga_max)
                    carga_minima.append(carga_min)
                    carga_promedio.append(carga_mean)
                if not flagStopPes:
                    tiempo_carga_stop.append(0)
                if not flagCuna:
                    tiempo_cuna.append(0)
                if not flagBajLib:
                    velocidad_bajando_libre.append(0)
                    tiempo_bajando_libre.append(0)
                if not flagSubLib:
                    velocidad_subiendo_libre.append(0)
                    tiempo_subiendo_libre.append(0)  
            except Exception as e: 
                print(i)
                print(e)
    
    data_tiempos = pd.DataFrame()
    data_tiempos["fecha_hora_inicio"] = fecha_hora_inicio 
    data_tiempos["fecha_hora_fin"] = fecha_hora_fin

    data_tiempos["conexion"] = conexion

    data_tiempos["carga_maxima"] = carga_maxima
    data_tiempos["carga_minima"] = carga_minima
    data_tiempos["carga_promedio"] = carga_promedio
    data_tiempos["profundidad_maxima"] = profundidad_maxima

    data_tiempos["tiempo_cuna [min]"] = np.round(tiempo_cuna, 2)
    data_tiempos["tiempo_carga_mov [min]"] = np.round(tiempo_carga_mov,2)
    data_tiempos["tiempo_conexion_desconexion [min]"] = np.round(tiempo_conexion_desconexion,2)
    data_tiempos["tiempo_carga_stop [min]"] = np.round(tiempo_carga_stop,2)
    data_tiempos["tiempo_subiendo_libre [min]"] = np.round(tiempo_subiendo_libre,2)
    data_tiempos["tiempo_bajando_libre [min]"] = np.round(tiempo_bajando_libre,2)
    data_tiempos["tiempo_libre_total [min]"] = np.round(tiempo_libre_total,2)

    data_tiempos["velocidad_subiendo_libre [ft/min]"] = np.round(velocidad_subiendo_libre,2)
    data_tiempos["velocidad_bajando_libre [ft/min]"] = np.round(velocidad_bajando_libre,2)
    data_tiempos["velocidad_carga [ft/min]"] = np.round(velocidad_carga,2)

    data_tiempos["torque_potencia_max [lb*ft]"] = np.round(TQ_pot,2)
    data_tiempos["torque_hidrahulica_max [lb*ft]"] = np.round(TQ_hid,2)

    data_tiempos["tiempo_total [min]"] = data_tiempos[["tiempo_cuna [min]", "tiempo_carga_mov [min]", "tiempo_libre_total [min]", "tiempo_conexion_desconexion [min]", "tiempo_carga_stop [min]"]].sum(axis=1)

    
    return data_tiempos

def well_planning(file):
    
    data = pd.ExcelFile(file)
    
    try:
        df = data.parse('Well Planning')
        df = df.drop(range(8))
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header
        df = df.reset_index()
        df = df[['Step', 'Initial Date', 'PHASE', 'Code ', 'Subcode', 'Target Duration', 'Description']]
        df = df.dropna()
    except:
        try:
            df = data.parse('Hoja1')
            df = df.drop(range(30))
            new_header = df.iloc[0] #grab the first row for the header
            df = df[1:] #take the data less the header row
            df.columns = new_header #set the header row as the df header
            df = df.reset_index()
            df = df[['No', 'Fecha y Hora de Inicio', 'Fase*', 'Código*', 'Subcódigo*', 'Duración\n(Hr)', 'Operación*']]
            df = df.dropna()
        except:
            try:
                df = data.parse('WP')
                df = df.drop(range(30))
                new_header = df.iloc[0] #grab the first row for the header
                df = df[1:] #take the data less the header row
                df.columns = new_header #set the header row as the df header
                df = df.reset_index()
                df = df[['No', 'Fecha y Hora de Inicio', 'Fase*', 'Código*', 'Subcódigo*', 'Duración\n(Hr)', 'Operación*']]
                df = df.dropna()
            except:
                try:
                    sheets = data.sheet_names
                    sheetWp = ''
                    for sheet in sheets:
                        if 'WELL PLANING' in sheet:
                            sheetWp = sheet

                    df = data.parse(sheetWp)
                    df = df.drop(range(25))

                    new_header = df.iloc[0] #grab the first row for the header
                    df = df[1:] #take the data less the header row
                    df.columns = new_header #set the header row as the df header
                    df = df.reset_index()
                    df = df[['No', 'Activity Start Date/Time','Fase','Code','Subcode', 'Duracion (hr)', 'Operation']]
                    df = df.dropna()

                except:
                    print('Formato desconocido')

    return df

def find_first_row(dataframe, column):
        index = []
        for i in range(len(dataframe)):
            key = column[i]
            if "hr" in str(key):
                index.append(i)
        return index

def delete_first_cells(dataframe, column):
    rows = find_first_row(dataframe, column)
    df = dataframe.drop(rows)
    return df

def reports(file):

    # Se detectan las tablas
    tables = tabula.read_pdf(file, pages='all')

    new_tables = []
    tables_correct=[]
    tmb = 0
    del tables[0:2]

    cols = ['Date', 'Time', 'Duracion', 'Fase', 'Codigo', 'Subcodigo', 'P/N', 'MD From', 'Operacion']

    for table in tables:
        if len(table.columns) == 9:
            table.columns = ['Date', 'Time', 'Duracion', 'Fase', 'Codigo', 'Subcodigo', 'P/N', 'MD From', 'Operacion']
        else:
            # Corrijo columna extra
            
            # Concateno Unnamed y Operacion
            
            table['Operación*'].fillna(' ', inplace=True)        
            table['Operacion'] = table['Unnamed: 0'].str.cat(table['Operación*'])
            table.drop(['Unnamed: 0'], axis=1, inplace=True)
            table.drop(['Operación*'], axis=1, inplace=True)
            
            table.columns = ['Date', 'Time', 'Duracion', 'Fase', 'Codigo', 'Subcodigo', 'P/N', 'MD From', 'Operacion']
            
        
        
    for i in range(len(tables)):
        table = delete_first_cells(tables[i],  tables[i]["Duracion"])
        new_tables.append(table)


    table = pd.concat(new_tables, ignore_index=True)

    i = 0
    for row in table.itertuples():
        if str(row.Operacion) == 'nan':
            table.iloc[i] = table.iloc[i].shift(1) # Desplazo las columnas hacia la derecha
        i+=1        
    table.drop(["MD From"], axis=1, inplace=True)


    rows_na = []

    for i, row in table.iterrows():
        time_col = row['Time']
        if str(time_col) == "nan":
            rows_na.append(1)
            
        else:
            rows_na.append(0)


    # Concateno los strings de operaciones
    index_sup = 0
    for i, row in table.iterrows():
        
    
        value = rows_na[i]
        if value == 0:
            index_sup = i
            try:
                string_prov = row["Operacion"]
            except:
                pass
        else:
            string_prov = str(string_prov) + " " + str(row["Operacion"])
            
            table['Operacion'][index_sup] = string_prov
            table.drop(i, inplace=True)

    # Asigno la fecha a los filas vacias
    rows_na = []
    for i, row in table.iterrows():
        date_col = row['Date']
        if str(date_col) == "nan":
            rows_na.append(1)
            
        else:
            rows_na.append(0)
    table.reset_index(inplace=True)
    table.drop(["index"], axis=1, inplace=True)

    fecha_inicio = []
    fecha_fin = []

    index_sup = 0
    for i, row in table.iterrows():
        value = rows_na[i]
        
        hora = row["Time"]
        ind = row["Time"].index(':')
        hora = hora[:ind+3] + ' ' + hora[ind+3:]
        
        if value == 0:
            index_sup = i
            horas = hora.split(" ")
            fecha_ini = table['Date'][index_sup] + " " + horas[0]
            fecha_f = table['Date'][index_sup] + " " + horas[-1]
            
            fecha_inicio.append(fecha_ini)
            fecha_fin.append(fecha_f)
        else:
            # Dividir horas
            
            horas = hora.split(" ")
            
            fecha_ini = table['Date'][index_sup] + " " + horas[0]
            fecha_f = table['Date'][index_sup] + " " + horas[-1]
            
            fecha_inicio.append(fecha_ini)
            fecha_fin.append(fecha_f)
            
            table['Date'][i] = table['Date'][index_sup]

    table.index += 1
    table.columns = table.columns.str.replace('index', 'step')
    table["fecha_inicio"] = fecha_inicio
    table["fecha_fin"] = fecha_fin
    table.drop(["Time"], axis=1, inplace=True)

    #IMPORTANTE: HAY QUE VALIDAR EN EXCEL LOS DATOS POR LA INTERPRETACION DE LAS
    # ',' y '.' en los numeros
    index = file.rfind('Operations')
    table.to_csv(f'{file[index:-4]}.csv', sep=';', decimal=",")

    #IMPORTANTE: HAY QUE VALIDAR EN EXCEL LOS DATOS POR LA INTERPRETACION DE LAS
    # ',' y '.' en los numeros
    return table

def survey(file):
    if file[-4:] == '.pdf':
        # Se detectan las tablas
        tables = tabula.read_pdf(file, pages='all')
        survey = tables[4][['MD', 'Inc.', 'Azi.', 'TVD', 'Dleg']]
        survey.drop(0, inplace=True)
        survey.reset_index(drop=True)
        return survey
    else:
        try:
            data = pd.ExcelFile(file)
            df = data.parse(data.sheet_names[0])
            df = df.drop(range(9))
            MD = ''
            Inc = ''
            VD = ''
            Az = ''
            DSL = ''
            
            new_header = df.iloc[0:3] #grab the first row for the header

            for row in new_header.itertuples():
                if str(row._1) != 'nan':
                    MD = MD + ' ' + str(row._1)
                if str(row._2) != 'nan':
                    Inc = Inc + ' ' + str(row._2)
                if str(row._3) != 'nan':
                    VD = VD + ' ' + str(row._3)
                if str(row._4) != 'nan':
                    Az = Az + ' ' + str(row._4)
                if str(row._13) != 'nan':
                    DSL = DSL + ' ' + str(row._13)

            new_header = [MD, Inc, VD, Az, DSL]
            df = df.reset_index()
            df = df.drop([0, 1, 2])
            df = df.iloc[:, [1,2,3, 4, 12]]
            df.columns = new_header
            df = df.reset_index()
            df = df.drop('index', axis='columns')
            df.columns = ['MD', 'Inc.', 'Azi.', 'TVD', 'Dleg']

            return df
        except:
            try:
                data = pd.ExcelFile(file)

                df = data.parse(data.sheet_names[0])
                df = df.drop(range(76))

                new_header = df.iloc[0] #grab the first row for the header
                df = df[1:] #take the data less the header row
                df.columns = new_header #set the header row as the df header

                df = df[['MD\n(ft)', 'Inc\n(°)', 'Azi (azimuth)\n(°)', 'TVD\n(ft)', 'DLeg\n(°/100ft)']]
                df = df.dropna()

                df = df.reset_index()

                df = df.drop('index', axis='columns')
                df.columns = ['MD', 'Inc.', 'Azi.', 'TVD', 'Dleg']

                return df
            except:
                try:
                    data = pd.ExcelFile(file)

                    df = data.parse(data.sheet_names[0])
                    df = df.drop(range(41))
                    new_header = df.iloc[0] #grab the first row for the header
                    df = df[1:] #take the data less the header row
                    df.columns = new_header #set the header row as the df header

                    df = df[['MD', 'Inc', 'Az', 'TVD', 'DLS']]
                    df = df.dropna()

                    df = df.reset_index()
                    df = df.drop(0)
                    df = df.reset_index()
                    df = df.drop('index', axis='columns')
                    df = df.drop('level_0', axis='columns')
                    df.columns = ['MD', 'Inc.', 'Azi.', 'TVD', 'Dleg']

                    return df
                except:
                    data = pd.ExcelFile(file)

                    df = data.parse(data.sheet_names[0])
                    df = df.drop(range(22))
                    new_header = df.iloc[0] #grab the first row for the header
                    df = df[1:] #take the data less the header row
                    df.columns = new_header #set the header row as the df header


                    df = df[['MD', 'Inclination', 'Azimuth', 'TVD', 'DLS']]
                    df = df.dropna()

                    df = df.reset_index()
                    df = df.drop(0)
                    df = df.reset_index()

                    df = df.drop('index', axis='columns')
                    df = df.drop('level_0', axis='columns')
                    df.columns = ['MD', 'Inc.', 'Azi.', 'TVD', 'Dleg']

                    return df
                                            