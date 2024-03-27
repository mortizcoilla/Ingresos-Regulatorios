import os
import pandas as pd
from datetime import datetime


def procesar_cdp(ruta_directorio, fechas):
    dfs = []

    mapeo_hojas_objetivo = {
        "202212": "Base",
        "202301": "Base",
        "202302": "Base",
        "202303": "Base",
        "202304": "Lista",
        "202305": "Base",
        "202306": "MCP",
        "202307": "MCP",
        "202308": "MCP",
        "202309": "MCP",
        "202310": "MCP",
        "202311": "Base",
        "202312": "MCP"
    }

    mapeo_columnas = {
        'Número del caso': 'ND',
        'Número de Disconformidad': 'ND',
        'Fecha creación caso': 'FCC',
        'Fecha Creación del caso hasta': 'FCC',
        'Rut Acreedor': 'RA',
        'Rut Acreedor Final': 'RA',
        'Monto Disconformidad': 'MD',
        'Monto bruto instrucción de pago': 'MD',
        'Nemotécnico': 'NM',
        'Mercado Corto Plazo (MCP)': 'MCP',
        'Razón Social Acreedor': 'RSA',
        'Razón Social Deudor': 'RSD',
        'Tipo de Disconformidad': 'TD',
        '¿Disconformidad Abierta por?': 'ORGN',
        'Rut Deudor': 'RD',
        'Concepto': 'CON'
    }

    for fecha in fechas:
        archivo = f"cdp_{fecha}.xlsx"
        nombre_hoja_objetivo = mapeo_hojas_objetivo.get(fecha)
        periodo = datetime.strptime(fecha, "%Y%m").strftime("01-%m-%Y")
        if nombre_hoja_objetivo:
            ruta_archivo = os.path.join(ruta_directorio, archivo)
            try:
                df = pd.read_excel(ruta_archivo, sheet_name=nombre_hoja_objetivo)
                df.rename(columns=mapeo_columnas, inplace=True)
                df['MES'] = periodo

                dfs.append(df)
            except Exception as e:
                print(f"No se pudo leer la hoja '{nombre_hoja_objetivo}' en el archivo {archivo}: {e}")

    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        df_final['FCC'] = pd.to_datetime(df_final['FCC']).dt.date
        df_final.drop(['NM', 'MCP'], axis=1, inplace=True, errors='ignore')
        df_final['RSA'] = df_final['RSA'].str.lower()
        df_final['RSD'] = df_final['RSD'].str.lower()

        terminaciones_dict = {
            ' spa': '', ' spa.': '', ' sa': '', ' ltda': '', ' s.a.': '', ',': '',
            ' sa:': '', ' limitada': '', ' sa ': '', ' spa ': '', ' s.p.a.': '',
            ' s.a': '', '.': '', ':': '', '  ': ' '
        }

        for terminacion, correccion in terminaciones_dict.items():
            df_final['RSA'] = df_final['RSA'].str.replace(terminacion, correccion, regex=False)
            df_final['RSD'] = df_final['RSD'].str.replace(terminacion, correccion, regex=False)

        # Mostrar los nombres de las columnas
        print("\n", "Nombres de las columnas del DataFrame final:", "\n")
        print(df_final.columns.tolist())

        # Crear y mostrar el resumen según 'MES'
        resumen = df_final.groupby('MES').agg({'MD': 'sum', 'ND': 'count'}).rename(
            columns={'MD': 'Monto', 'ND': 'Casos'})
        resumen['Monto'] = (resumen['Monto'] / 1000000).round(1)
        resumen.index = pd.to_datetime(resumen.index)
        resumen.sort_index(ascending=False, inplace=True)

        print("\n", "Resumen por MES:", "\n")
        print(resumen)

        empresas_df = empresas(df_final)

        nombre_archivo_salida = os.path.join(ruta_directorio, 'df_final_cdp.xlsx')
        with pd.ExcelWriter(nombre_archivo_salida) as writer:
            df_final.to_excel(writer, sheet_name='hist', index=False)
            empresas_df.to_excel(writer, sheet_name='empresas', index=False)

        print(f"\nDataFrame concatenado exportado exitosamente a {nombre_archivo_salida}")

        return df_final
    else:
        print("No se encontraron DataFrames para concatenar.")
        return None


def normalizar_rut(rut):
    rut_str = str(rut)
    rut_sin_puntos = rut_str.replace('.', '').replace(' ', '')
    partes = rut_sin_puntos.split('-')
    if len(partes) == 2:
        numero, dv = partes
        rut_normalizado = f"{numero}-{dv}"
    else:
        rut_normalizado = rut_str
    return rut_normalizado


def empresas(df):
    df['RD'] = df['RD'].apply(normalizar_rut)
    df['RA'] = df['RA'].apply(normalizar_rut)

    deudores = df[['RD', 'RSD']].rename(columns={'RD': 'RUT', 'RSD': 'RS'})
    acreedores = df[['RA', 'RSA']].rename(columns={'RA': 'RUT', 'RSA': 'RS'})
    empresas_df = pd.concat([deudores, acreedores])
    empresas_df = empresas_df.groupby('RUT')['RS'].agg(lambda x: ' / '.join(x.unique())).reset_index()

    return empresas_df


ruta_directorio = r"C:\workspace\cdp"
fechas = ["202212", "202301", "202302", "202303", "202304", "202305", "202306", "202307", "202308", "202309", "202310",
          "202311", "202312"]
df_final = procesar_cdp(ruta_directorio, fechas)