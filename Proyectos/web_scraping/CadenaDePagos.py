import pandas as pd

def leer_CDP(fecha):
    nombre_archivo = f"Reporte Disconformidades PPagos I {fecha}.xlsx"
    ruta_archivo = f"C:\\workspace\\BBDD\\CadenaDePagos\\{nombre_archivo}"
    
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
    df['MBIP'] = df['MBIP'].apply(lambda x: "${:,.2f}".format(x))
    df.drop(['NEM', 'MCP'], axis=1, inplace=True)
    df['RSA'] = df['RSA'].str.lower()
    df['RSD'] = df['RSD'].str.lower()

    terminaciones_dict = {
        ' spa': '',
        ' spa.': '',
        ' sa': '',
        ' ltda': '',
        ' s.a.': '',
        ',':'',
        ' sa:':'',
        ' limitada':'',
        ' sa ':'',
        ' spa ':'',
        ' s.p.a.':'',
        ' s.a':'',
        '.':'',
        ':':'',
        '  ':''   
    }
    
    for terminacion, correccion in terminaciones_dict.items():
        df['RSA'] = df['RSA'].str.replace(terminacion, correccion, regex=False)
        df['RSD'] = df['RSD'].str.replace(terminacion, correccion, regex=False)
    
    return df

def empresas(df):
    df['MBIP'] = df['MBIP'].replace('[\$,]', '', regex=True).astype(float)
    deudores = df[['RD', 'RSD', 'MBIP', 'ND']].rename(columns={'RD': 'RUT', 'RSD': 'RS', 'MBIP': 'Deuda', 'ND': 'ND_Deuda'})
    acreedores = df[['RA', 'RSA', 'MBIP', 'ND']].rename(columns={'RA': 'RUT', 'RSA': 'RS', 'MBIP': 'Crédito', 'ND': 'ND_Crédito'})
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
        'Tipos de Disconformidad como Acreedor': df_filtrado[df_filtrado['RA'] == rut_focal]['TDC'].value_counts().to_dict(),
        'Tipos de Disconformidad como Deudor': df_filtrado[df_filtrado['RD'] == rut_focal]['TDC'].value_counts().to_dict(),
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
import pandas as pd
from pandas_profiling import ProfileReport

# Crear un DataFrame simple como ejemplo
data = {
    'Nombre': ['Ana', 'Luis', 'Carlos', 'Teresa'],
    'Edad': [32, 45, 23, 36],
    'Ciudad': ['Madrid', 'Barcelona', 'Madrid', 'Valencia'],
    'Ingresos': [3000, 4000, 3500, 2800]
}

df = pd.DataFrame(data)

# Generar el reporte de Pandas Profiling
profile = ProfileReport(df, title='Reporte de Pandas Profiling', explorative=True)

# Guardar el reporte como un archivo HTML
profile.to_file("reporte_ejemplo.html")
