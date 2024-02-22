import pandas as pd
from sqlalchemy import create_engine

def crear_conexion():
    server = 'WHJ1TN13\\SQLEXPRESS'
    database = 'i_rec'
    # Cadena de conexión
    conexion_str = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    return create_engine(conexion_str)


def obtener_dataframe(conexion, consulta_sql):
    try:
        # Ejecutar la consulta y obtener un DataFrame
        return pd.read_sql(consulta_sql, conexion)
    except Exception as e:
        print("Error en la conexión o ejecución de la consulta:", e)
        return None


engine = crear_conexion()

consulta_def = "SELECT * FROM [i_rec].[dbo].[peajes_etsa_def]"
df_definitivos = obtener_dataframe(engine, consulta_def)

consulta_pre = "SELECT * FROM [i_rec].[dbo].[peajes_etsa_pre]"
df_preliminares = obtener_dataframe(engine, consulta_pre)

cu_zonal_y_dedicado = "SELECT * FROM cu_zyd"
df_cu_zyd = obtener_dataframe(engine, cu_zonal_y_dedicado)

print(df_cu_zyd)