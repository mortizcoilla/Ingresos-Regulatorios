# Procesador
import os
import pandas as pd
import zipfile
from datetime import datetime, timedelta


def extract_dataframes(zip_path, extraction_path, excel_file_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extract(excel_file_name, path=extraction_path)

    extracted_data = []
    with pd.ExcelFile(os.path.join(extraction_path, excel_file_name)) as xls:
        for sheet_name in ['Pago Total', 'Peaje Retiro CI', 'Peaje Inyección', 'Exenciones a CI']:
            df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=11, nrows=719)
            extracted_data.append(df['ETSA'].sum() / 1000000)
    return extracted_data


def create_dataframe(extracted_data):
    current_date = datetime.now()
    first_day_last_month = current_date.replace(day=1) - timedelta(days=1)
    first_day_last_month = pd.Timestamp(first_day_last_month.replace(day=1).date())  # Convertir a Timestamp

    preliminar = pd.DataFrame({
        'Periodo': [first_day_last_month],
        'PagoTotal': [round(extracted_data[0], 1)],
        'PeajeRetiro': [round(extracted_data[1], 1)],
        'PeajeInyeccion': [round(extracted_data[2], 1)],
        'PagoExención': [round(extracted_data[3], 1)]
    })
    return preliminar


def procesar_datos_historicos(ruta_bbdd):
    df_bbdd = pd.read_excel(ruta_bbdd, sheet_name='Peajes')
    df_bbdd['Periodo'] = pd.to_datetime(df_bbdd['Periodo'])

    columnas = ['PagoTotal', 'PeajeRetiro', 'PeajeInyeccion', 'PagoExención']
    for col in columnas:
        df_bbdd[col] = pd.to_numeric(df_bbdd[col], errors='coerce')

    df_agrupado = df_bbdd.groupby('Periodo')[columnas].sum()
    df_agrupado = df_agrupado / 1000000
    df_agrupado = df_agrupado.round(1)

    # Obtener la última fecha del campo 'Periodo' y convertir a Timestamp
    ultima_fecha = df_agrupado.index.max()
    fecha_inicio = ultima_fecha - pd.DateOffset(months=11)  # Últimos 12 meses

    df_historico = df_agrupado[df_agrupado.index >= fecha_inicio]
    return df_historico


def unir_dataframes(df_preliminar, df_historico):
    df_historico.reset_index(inplace=True)
    datos = pd.concat([df_preliminar, df_historico], ignore_index=True)
    datos.sort_values(by='Periodo', inplace=True)
    return datos

