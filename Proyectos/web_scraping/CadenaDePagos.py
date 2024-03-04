# Análisis de Cadena de Pagos y Seguimiento
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
from datetime import datetime


def leer_CDP(fecha):
    nombre_archivo = f"Reporte Disconformidades PPagos I {fecha}.xlsx"
    # ruta_archivo = f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\BBDD\\{nombre_archivo}"
    ruta_archivo = f"C:\\workspace\\IngresosRegulados\\Proyectos\\BBDD\\{nombre_archivo}"

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
    
    df_resultado = df_filtrado[['Categoria', 'RUT', 'RS', 'Deuda (M)', 'Cantidad Disconformidades',
                                'Porcentaje del Total (%)', 'Porcentaje Acumulado']]
    
    df_resultado.columns = ['Categoria', 'RUT', 'Razon Social', 'Total Deuda (M)', 'Cantidad Disconformidades',
                            'Porcentaje del Total (%)', 'Porcentaje Acumulado (%)']

    return df_resultado


def crear_grafico_deuda(resultado_df):
    suma_deuda_A = resultado_df[resultado_df['Categoria'] == 'A']['Total Deuda (M)'].sum()
    suma_deuda_B = resultado_df[resultado_df['Categoria'] == 'B']['Total Deuda (M)'].sum()
    suma_deuda_C = resultado_df[resultado_df['Categoria'] == 'C']['Total Deuda (M)'].sum()

    fig = go.Figure(data=[go.Bar(
        x=['A', 'B', 'C'],
        y=[suma_deuda_A, suma_deuda_B, suma_deuda_C],
        marker_color='#01ACFB',
        text=[f"{suma_deuda_A:,.1f}M", f"{suma_deuda_B:,.1f}M", f"{suma_deuda_C:,.1f}M"],
        textposition='outside'
    )])

    fig.update_layout(
        title_text='Deuda por Categoría (en millones)',
        xaxis_title='Categoría',
        yaxis_title='Total Deuda Sistema (M)',
        template='plotly_white',
        margin=dict(t=60)
    )

    return fig


def crear_tabla_deuda(df_resultado):
    if df_resultado.empty:
        print("El DataFrame está vacío.")
        return None

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df_resultado.columns),
                    fill_color='#01ACFB',
                    align='left'),
        cells=dict(values=[df_resultado[col] for col in df_resultado.columns],
                   fill_color='white',
                   align='left'))
    ])

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5)
    )

    return fig


# ---------------------------------------------------------------------------------------------------------------------
fecha = '202310'
fecha_objeto = datetime.strptime(fecha, '%Y%m')
periodo = fecha_objeto.strftime('%B de %Y')
df_original = leer_CDP(fecha)
# ---------------------------------------------------------------------------------------------------------------------

if df_original is not None:
    df_transformado = transformaciones_cdp(df_original)
    empresas_df = empresas(df_transformado)
    resultado_df = calcular_porcentaje_acumulado_deuda(empresas_df)

    # Usando la función para crear el gráfico
    fig = crear_grafico_deuda(resultado_df)
    grafico_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Generar la tabla
    fig_tabla = crear_tabla_deuda(resultado_df)
    if fig_tabla is not None:
        tabla_div = plot(fig_tabla, output_type='div', include_plotlyjs=True)
    else:
        tabla_div = "No se pudo generar la tabla."

    titulo = "Transferencias económicas entre empresas"
    subtitulo = "Cadena de pago – Incumplimientos de pago no acordado"

    pie_de_pagina = """
    <div class="pie-de-pagina">
        <p>&copy; 2024 Engie. Gerencia de Negocios de Transmisión.</p>
    </div>
    """
# ----------------------------------------------------------------------------------------------------------------------
    html_contenido = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{titulo}</title>
        <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                margin-left: 2%;
                margin-right: 2%;
                background-color: #F5F5F5;
                color: #034E7B;
            }}
            h1 {{
                color: #034E7B; /* Azul Oscuro para el título principal */
                margin-bottom: 0;
            }}
            h2 {{
                color: #647A8E; /* Gris Azulado para el subtítulo */
                margin-top: 5px;
            }}
            .contenido-flex {{
                display: flex;
                justify-content: space-around; /* Ajusta la distribución de los elementos */
                align-items: flex-start; /* Alinea los elementos al inicio de su contenedor */
                flex-wrap: wrap; /* Permite que los elementos se envuelvan si no caben en una sola línea */
            }}
            .plotly-graph-div, .plotly-table-div {{
                margin-top: 20px;
                flex: 1;
                min-width: 48%; /* Controla el ancho mínimo de cada elemento */
                margin-right: 0; /* Elimina el margen derecho para reducir el espacio */
            }}
            /* Elimina el margen adicional en los elementos finales */
            .plotly-graph-div:last-child, .plotly-table-div:last-child {{
                margin-right: 0;
            }}
            .pie-de-pagina {{
                margin-top: 20px; /* Reduce el espacio antes del pie de página */
                text-align: center;
                color: #A8B07A; /* Verde Oliva Suave para el texto del pie de página */
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <h1>{titulo}</h1>
        <h2>{subtitulo}</h2>
        <h3>{periodo}</h3>
        <div class="contenido-flex">
            <div>{grafico_div}</div> <!-- Contenedor para el gráfico de Plotly -->
            <div>{tabla_div}</div> <!-- Contenedor para la tabla de Plotly -->
        </div>
        {pie_de_pagina} <!-- Aquí se agrega el pie de página -->
    </body>
    </html>
    """
# ---------------------------------------------------------------------------------------------------------------------
    # Ajusta la ruta del archivo según tu entorno
    nombre_archivo = r"C:\workspace\IngresosRegulados\Proyectos\informes\cadenadepagos\informe_cdp.html"

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write(html_contenido)

    print(f"El informe con gráfico dinámico ha sido guardado como {nombre_archivo}.")
else:
    print("No se pudo cargar el DataFrame original.")
