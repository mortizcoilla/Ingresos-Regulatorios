# Análisis de Cadena de Pagos y Seguimiento
import pandas as pd
import plotly.express as px


def leer_CDP(fecha):
    """
    nombre_archivo = f"Reporte Disconformidades PPagos I {fecha}.xlsx"
    ruta_archivo = f"C:\\workspace\\BBDD\\CadenaDePagos\\{nombre_archivo}"
    """

    nombre_archivo = f"Reporte Disconformidades PPagos I {fecha}.xlsx"
    ruta_archivo = f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\BBDD\\{nombre_archivo}"

    nombre_hoja = "MCP"
    try:
        df = pd.read_excel(ruta_archivo, sheet_name=nombre_hoja, engine='openpyxl')
        return df
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return None


def transformaciones_cdp(df):
    df.rename(columns={
        'Número de Disconformidad': 'ND',
        'Fecha Creación del caso hasta': 'FCC',
        'Nemotécnico': 'NEM',
        'Concepto': 'CON',
        'Mercado Corto Plazo (MCP)': 'MCP',
        'Rut Acreedor': 'RA',
        'Razón Social Acreedor': 'RSA',
        'Rut Deudor': 'RD',
        'Razón Social Deudor': 'RSD',
        'Tipo de Disconformidad': 'TDC',
        'Monto bruto instrucción de pago': 'MBIP',
        '¿Disconformidad Abierta por?': 'DAP'
    }, inplace=True)

    df['FCC'] = pd.to_datetime(df['FCC']).dt.date
    df.drop(['NEM', 'MCP'], axis=1, inplace=True)
    df['RSA'] = df['RSA'].str.lower()
    df['RSD'] = df['RSD'].str.lower()

    terminaciones_dict = {
        ' spa': '',
        ' spa.': '',
        ' sa': '',
        ' ltda': '',
        ' s.a.': '',
        ',': '',
        ' sa:': '',
        ' limitada': '',
        ' sa ': '',
        ' spa ': '',
        ' s.p.a.': '',
        ' s.a': '',
        '.': '',
        ':': '',
        '  ': ''
    }

    for terminacion, correccion in terminaciones_dict.items():
        df['RSA'] = df['RSA'].str.replace(terminacion, correccion, regex=False)
        df['RSD'] = df['RSD'].str.replace(terminacion, correccion, regex=False)

    return df


def empresas(df):
    df['MBIP'] = df['MBIP'].replace('[\$,]', '', regex=True).astype(float)
    deudores = df[['RD', 'RSD', 'MBIP', 'ND']].rename(
        columns={'RD': 'RUT', 'RSD': 'RS', 'MBIP': 'Deuda', 'ND': 'ND_Deuda'})
    acreedores = df[['RA', 'RSA', 'MBIP', 'ND']].rename(
        columns={'RA': 'RUT', 'RSA': 'RS', 'MBIP': 'Crédito', 'ND': 'ND_Crédito'})
    deudores['Deuda'] = deudores.groupby('RUT')['Deuda'].transform('sum')
    deudores['Q_Deuda'] = deudores.groupby('RUT')['ND_Deuda'].transform('nunique')
    acreedores['Crédito'] = acreedores.groupby('RUT')['Crédito'].transform('sum')
    acreedores['Q_Crédito'] = acreedores.groupby('RUT')['ND_Crédito'].transform('nunique')
    deudores = deudores[['RUT', 'RS', 'Deuda', 'Q_Deuda']].drop_duplicates('RUT').reset_index(drop=True)
    acreedores = acreedores[['RUT', 'RS', 'Crédito', 'Q_Crédito']].drop_duplicates('RUT').reset_index(drop=True)
    empresas_df = pd.merge(deudores, acreedores, on=['RUT', 'RS'], how='outer').fillna(0)
    empresas_df = empresas_df.sort_values(by='Deuda', ascending=False).reset_index(drop=True)

    return empresas_df


def generar_resumen(df, rut_focal):
    df_filtrado = df[(df['RA'] == rut_focal) | (df['RD'] == rut_focal)].copy()
    df_filtrado['MBIP_limpio'] = df_filtrado['MBIP'].replace('[\$,]', '', regex=True).astype(float)

    resumen = {
        'Casos como Acreedor': df_filtrado[df_filtrado['RA'] == rut_focal].shape[0],
        'Casos como Deudor': df_filtrado[df_filtrado['RD'] == rut_focal].shape[0],
        'Monto Total como Acreedor': df_filtrado[df_filtrado['RA'] == rut_focal]['MBIP_limpio'].sum(),
        'Monto Total como Deudor': df_filtrado[df_filtrado['RD'] == rut_focal]['MBIP_limpio'].sum(),
        'Tipos de Disconformidad como Acreedor': df_filtrado[df_filtrado['RA'] == rut_focal][
            'TDC'].value_counts().to_dict(),
        'Tipos de Disconformidad como Deudor': df_filtrado[df_filtrado['RD'] == rut_focal][
            'TDC'].value_counts().to_dict(),
        'Contrapartes como Acreedor': df_filtrado[df_filtrado['RA'] == rut_focal]['RD'].value_counts().to_dict(),
        'Contrapartes como Deudor': df_filtrado[df_filtrado['RD'] == rut_focal]['RA'].value_counts().to_dict(),
    }

    return resumen


# ------------------------------------------------------------------------------------------------------------
"""
fecha = '202310'
df = leer_CDP(fecha)

if df is not None:
    df_transformado = transformaciones_cdp(df)
    df_transformado['MBIP_limpio'] = df_transformado['MBIP'].replace('[\$,]', '', regex=True).astype(float)
    rut_focal = '88.006.900-4'
    resumen_para_rut_focal = generar_resumen(df_transformado, rut_focal)

    print("Resumen para el RUT:", rut_focal)
    for key, value in resumen_para_rut_focal.items():
        print(f"{key}: {value}")
else:
    print("El DataFrame no pudo ser cargado. Por favor, verifica la ruta y el nombre del archivo.")
"""
# -----------------------------------------------------------------------------------------------------------
# fecha = '202310'
# df_original = leer_CDP(fecha)

# if df_original is not None:
#    df_transformado = transformaciones_cdp(df_original)
#    df_empresas = empresas(df_transformado)

#    ruta_salida = r"C:\Users\QV6522\Workspace\BBDD\01_Cadena De Pagos\Resumen_Empresas.xlsx"

#    df_empresas.to_excel(ruta_salida, index=False)
#    print(f"El archivo Excel ha sido exportado con éxito a {ruta_salida}")
# else:
#    print("No se pudo cargar el DataFrame original.")
# -----------------------------------------------------------------------------------------------------------
# fecha = "202310"
# df_original = leer_CDP(fecha)
# df_transformado = transformaciones_cdp(df_original)
# ruta_exportacion_transformaciones = "C:\\Users\\QV6522\\Workspace\\BBDD\\01_Cadena De Pagos\\datos_transformados.xlsx"
# df_transformado.to_excel(ruta_exportacion_transformaciones, index=False)
# -----------------------------------------------------------------------------------------------------------

df = leer_CDP("202310")
df_transformado = transformaciones_cdp(df)
deuda_total = df_transformado['MBIP'].sum()
deuda_total_formateada = f"${deuda_total:,}"

print(f"La deuda total del sistema es de {deuda_total_formateada} Millones de CLP")