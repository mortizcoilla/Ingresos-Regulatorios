# Análisis de Cadena de Pagos y Seguimiento
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
from datetime import datetime

import dash
from dash import dcc, html
from dash import dash_table




def leer_CDP(fecha):
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


def calcular_porcentaje_acumulado_deuda(df_empresas):
    df_filtrado = df_empresas[df_empresas['Deuda'] > 0].copy()
    df_filtrado.sort_values(by='Deuda', ascending=False, inplace=True)
    total_deuda = df_filtrado['Deuda'].sum()

    df_filtrado['Deuda (M)'] = (df_filtrado['Deuda'] / 1000000).round(1)
    df_filtrado['Porcentaje Acumulado'] = ((df_filtrado['Deuda'].cumsum() / total_deuda) * 100).round(1)

    df_filtrado['Porcentaje del Total (%)'] = ((df_filtrado['Deuda'] / total_deuda) * 100).round(1)

    def asignar_categoria(porcentaje):
        if porcentaje < 80:
            return 'A'
        elif 80 <= porcentaje < 95:
            return 'B'
        else:
            return 'C'

    df_filtrado['Categoria'] = df_filtrado['Porcentaje Acumulado'].apply(asignar_categoria)
    df_filtrado['Cantidad Disconformidades'] = df_empresas['Q_Deuda']
    df_resultado = df_filtrado[['Categoria', 'RUT', 'RS', 'Deuda (M)', 'Cantidad Disconformidades', 'Porcentaje del Total (%)', 'Porcentaje Acumulado']]
    df_resultado.columns = ['Categoria', 'RUT', 'Razon Social', 'Total Deuda (M)', 'Cantidad Disconformidades', 'Porcentaje del Total (%)', 'Porcentaje Acumulado (%)']

    return df_resultado


# --------------------

app = dash.Dash(__name__)

fecha = '202310'
df_original = leer_CDP(fecha)
if df_original is not None:
    df_transformado = transformaciones_cdp(df_original)
    df_empresas = empresas(df_transformado)
    df_resultado = calcular_porcentaje_acumulado_deuda(df_empresas)
else:
    print("No se pudo cargar el DataFrame original.")
    df_resultado = pd.DataFrame()

app.layout = html.Div([
    html.H1('Detalle de Deuda por Empresa'),
    dash_table.DataTable(
        id='tabla_deuda',
        columns=[{"name": i, "id": i} for i in df_resultado.columns],
        data=df_resultado.to_dict('records'),
        style_table={'overflowX': 'scroll'},
        page_size=10,
        style_cell={'textAlign': 'left'},
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)