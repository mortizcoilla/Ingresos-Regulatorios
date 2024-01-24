import pandas as pd
from sqlalchemy import create_engine


def main():
    # Parámetros de conexión
    server = 'WHJ1TN13\\SQLEXPRESS'
    database = 'i_rec'

    # Cadena de conexión para SQLAlchemy
    conexion_str = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

    try:
        # Crear motor de conexión utilizando SQLAlchemy
        engine = create_engine(conexion_str)

        # Utilizar Pandas para ejecutar la consulta y obtener un DataFrame
        consulta_sql = "SELECT * FROM [i_rec].[dbo].[ETSA]"
        df = pd.read_sql(consulta_sql, engine)

        # Imprimir el DataFrame
        print(df)

    except Exception as e:
        print("Error en la conexión o ejecución de la consulta:", e)


