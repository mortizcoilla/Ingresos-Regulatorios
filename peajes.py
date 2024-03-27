import os
import zipfile
import pandas as pd

import win32com.client as win32
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import warnings
warnings.filterwarnings("ignore", message="Slicer List extension is not supported and will be removed")


def fecha_actual():
    fecha_actual = datetime.date.today()
    return fecha_actual.strftime("%d/%m/%Y")


def fecha_mes_anterior():
    hoy = datetime.date.today()
    primer_dia_del_mes = datetime.date(hoy.year, hoy.month, 1)
    ultimo_dia_del_mes_anterior = primer_dia_del_mes - datetime.timedelta(days=1)
    return ultimo_dia_del_mes_anterior.strftime("%B %Y")


def names_paths(fecha_entrada):
    yy = fecha_entrada[2:4]
    yyyy = fecha_entrada[0:4]
    mm = fecha_entrada[4:6]
    zip_path = f"C:/Users/QV6522/workspace/BBDD/04_Peajes/{yyyy}/{yyyy}{mm}/Liquidacion-de-Peajes-preliminar.zip"
    extraction_path = f"C:/Users/QV6522/workspace/BBDD/04_Peajes/Preliminares"
    excel_file_name = f"Liquidación de Peajes - preliminar/Liquidación de Peajes {yy}{mm}.xlsm"
    return zip_path, extraction_path, excel_file_name


def extract_dataframes(zip_path, excel_file_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_contents = zip_ref.namelist()

        excel_file_path = None
        for file_path in zip_contents:
            if file_path.startswith('Liquidación de Peajes - preliminar/') and file_path.endswith(excel_file_name):
                excel_file_path = file_path
                break

        if excel_file_path is None:
            raise FileNotFoundError(f"No se pudo encontrar el archivo Excel '{excel_file_name}' dentro del archivo ZIP.")

        zip_ref.extract(excel_file_path)

    with pd.ExcelFile(excel_file_path) as xls:
        df_pago_total = pd.read_excel(xls, sheet_name='Pago Total', usecols='C:AN', skiprows=11)
        df_pago_filtrado = df_pago_total[df_pago_total['Empresa Generación'] == 'Total general'].copy()
        df_pago_filtrado = df_pago_filtrado[['ETSA']].copy()
        df_pago_filtrado.rename(columns={'ETSA': 'PagoTotal'}, inplace=True)
        df_pago_filtrado.reset_index(drop=True, inplace=True)

        df_retiro = pd.read_excel(xls, sheet_name='Peaje Retiro CI', usecols='B:AN', skiprows=11)
        df_retiro_filtrado = df_retiro[df_retiro['Empresa generación'] == 'Total general'].copy()
        df_retiro_filtrado = df_retiro_filtrado[['ETSA']].copy()
        df_retiro_filtrado.rename(columns={'ETSA': 'PeajeRetiro'}, inplace=True)
        df_retiro_filtrado.reset_index(drop=True, inplace=True)

        df_inyeccion = pd.read_excel(xls, sheet_name='Peaje Inyección', usecols='B:AN', skiprows=11)
        df_inyeccion_filtrado = df_inyeccion[df_inyeccion['Empresa Generación'] == 'Total general'].copy()
        df_inyeccion_filtrado = df_inyeccion_filtrado[['ETSA']].copy()
        df_inyeccion_filtrado.rename(columns={'ETSA': 'PeajeInyeccion'}, inplace=True)
        df_inyeccion_filtrado.reset_index(drop=True, inplace=True)

        df_exenciones = pd.read_excel(xls, sheet_name='Exenciones a CI', usecols='B:AN', skiprows=11)
        df_exenciones_filtrado = df_exenciones[df_exenciones['Empresa Generación'] == 'Total general'].copy()
        df_exenciones_filtrado = df_exenciones_filtrado[['ETSA']].copy()
        df_exenciones_filtrado.rename(columns={'ETSA': 'PagoExención'}, inplace=True)
        df_exenciones_filtrado.reset_index(drop=True, inplace=True)

        df_pago_filtrado['PagoTotal'] = (df_pago_filtrado['PagoTotal'] / 1000000).round(1)
        df_retiro_filtrado['PeajeRetiro'] = (df_retiro_filtrado['PeajeRetiro'] / 1000000).round(1)
        df_inyeccion_filtrado['PeajeInyeccion'] = (df_inyeccion_filtrado['PeajeInyeccion'] / 1000000).round(1)
        df_exenciones_filtrado['PagoExención'] = (df_exenciones_filtrado['PagoExención'] / 1000000).round(1)

        df_preliminar = pd.concat([df_pago_filtrado, df_retiro_filtrado, df_inyeccion_filtrado, df_exenciones_filtrado], axis=1)

        periodo = fecha_entrada[:4] + '-' + fecha_entrada[4:] + '-01'
        df_preliminar['Periodo'] = periodo
        df_preliminar = df_preliminar[
            ['Periodo', 'PagoTotal', 'PeajeRetiro', 'PeajeInyeccion', 'PagoExención']]

    os.remove(excel_file_path)

    print("DataFrame Peajes Preliminar:")
    print(df_preliminar)

    return df_preliminar


def procesar_datos_historicos():
    ruta_bbdd = r"C:\Users\QV6522\workspace\IngresosRegulados\Proyectos\BBDD\InformesRecurrentesBBDD.xlsx"
    df_bbdd = pd.read_excel(ruta_bbdd, sheet_name='Peajes')
    df_bbdd['Periodo'] = pd.to_datetime(df_bbdd['Periodo'])

    columnas = ['PagoTotal', 'PeajeRetiro', 'PeajeInyeccion', 'PagoExención']
    for col in columnas:
        df_bbdd[col] = pd.to_numeric(df_bbdd[col], errors='coerce')

    df_agrupado = df_bbdd.groupby('Periodo')[columnas].sum()
    df_agrupado = df_agrupado / 1000000
    df_agrupado = df_agrupado.round(1)

    ultima_fecha = df_agrupado.index.max()
    fecha_inicio = ultima_fecha - pd.DateOffset(months=11)

    df_historico = df_agrupado[df_agrupado.index >= fecha_inicio].reset_index()

    print("Datos históricos procesados:")
    print(df_historico)

    return df_historico


def unir_dataframes(df_preliminar, df_historico):
    df_historico.reset_index(inplace=True)
    df_historico_preliminar = pd.concat([df_preliminar, df_historico], ignore_index=True)
    df_historico_preliminar.sort_values(by='Periodo', inplace=True)
    return df_historico_preliminar


def calcular_estadisticas(df_historico):
    estadisticas = {}
    for columna in df_historico.columns:
        if pd.api.types.is_numeric_dtype(df_historico[columna]):
            estadisticas[columna] = {
                'promedio': round(df_historico[columna].mean(), 1),
                'desvest': round(df_historico[columna].std(), 1),
                'máximo': df_historico[columna].max(),
                'minimo': df_historico[columna].min()
            }
    return estadisticas


def graficar_datos_preliminar(df_historico, estadisticas, df_preliminar, fecha_entrada):
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))

    df_historico['Periodo'] = pd.to_datetime(df_historico['Periodo'])

    sns.lineplot(ax=ax, data=df_historico, x='Periodo', y='PagoTotal', marker='o', color='blue', linewidth=1,
                 label='Pago Total')

    if not df_preliminar.empty:
        ax.scatter(df_preliminar['Periodo'], df_preliminar['PagoTotal'], color='red', marker='*', s=100,
                   label='Preliminar')

        ax.set_xticks(df_historico['Periodo'], [x.strftime('%b-%y') for x in df_historico['Periodo']], rotation=45)
        ax.set_xlabel('Periodo', fontsize=14)

    ax.axhline(estadisticas['PagoTotal']['máximo'], color='red', linestyle='--', label='Máximo')
    ax.axhline(estadisticas['PagoTotal']['minimo'], color='red', linestyle='--', label='Mínimo')
    ax.axhline(estadisticas['PagoTotal']['promedio'], color='green', linestyle='-', label='Promedio')

    ax.xaxis.set_major_formatter(DateFormatter('%b-%y'))
    plt.xticks(df_historico['Periodo'], [x.strftime('%b-%y') for x in df_historico['Periodo']], rotation=45)

    ax.set_title('Evolución del Pago Total (Últimos 12 Meses)', fontweight='bold', fontsize=16)
    ax.set_xlabel('Periodo', fontsize=14)
    ax.set_ylabel('PagoTotal (MM de CLP)', fontsize=14)

    plt.legend(title='Referencias', title_fontsize='13', fontsize='12')
    plt.tight_layout()

    nombre_archivo = f"peajes_preliminar_{fecha_entrada}.jpg"
    ruta_grafico = os.path.join(r"C:\Users\QV6522\workspace\IngresosRegulados\graficos", nombre_archivo)

    plt.savefig(ruta_grafico)

    return ruta_grafico


def saludo():
    hora_actual = datetime.datetime.now()
    if hora_actual.hour < 12:
        return "Buenos días,"
    else:
        return "Buenas tardes,"


def evaluar_pago_preliminar(pago_total_preliminar, maximo, minimo):
    if minimo <= pago_total_preliminar <= maximo:
        return "Valor dentro de lo esperado."
    else:
        return "Valor fuera de lo esperado."


def configurar_cuerpo_email(df_preliminar, cid_grafico, maximo, minimo):
    pago_total_preliminar = df_preliminar['PagoTotal'].iloc[0]
    mensaje_saludo = saludo()
    mensaje_evaluacion = evaluar_pago_preliminar(pago_total_preliminar, maximo, minimo)

    cuerpo_html = f"""
    <html>
      <body>
        <p>{mensaje_saludo}</p>
        <p>ETSA - Pago Total Preliminar: {pago_total_preliminar} MM de CLP - {mensaje_evaluacion}</p>
        <img src="cid:{cid_grafico}" alt="Gráfico del Pago Total Preliminar"><br>
        <p>Saludos Cordiales,</p>
      </body>
    </html>
    """
    return cuerpo_html


def send_email(ruta_grafico, destinatarios, asunto, cuerpo_html, destinatarios_cc):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = destinatarios
    mail.CC = destinatarios_cc
    mail.Subject = asunto

    if not os.path.exists(ruta_grafico):
        print(f"El archivo {ruta_grafico} no existe.")
        return

    attachment = mail.Attachments.Add(ruta_grafico)
    cid = "MyGraphCID"
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001E", cid)
    mail.HTMLBody = cuerpo_html.replace('cid:MyGraphCID', f'cid:{cid}')
    mail.Send()


# ---------------------------------------------------------------------------------------------------------------------
fecha_entrada = "202402"
zip_path, extraction_path, excel_file_name = names_paths(fecha_entrada)
df_preliminar = extract_dataframes(zip_path, excel_file_name)
df_historico = procesar_datos_historicos()
estadisticas = calcular_estadisticas(df_historico)
ruta_grafico = graficar_datos_preliminar(df_historico, estadisticas, df_preliminar, fecha_entrada)
valor_maximo = estadisticas['PagoTotal']['máximo']
valor_minimo = estadisticas['PagoTotal']['minimo']
destinatarios = ('paul.baillarie@engie.com;francisco.bas@engie.com;claudio.troncoso@engie.com;cristian.jorquera@engie'
                 '.com;reinaldo.rupallan@engie.com')
destinatarios_cc = 'miguel.ortiz@external.engie.com'
asunto = f"Informe Preliminar Peajes {fecha_mes_anterior()}"
cid_grafico = "MyGraphCID"
cuerpo_html = configurar_cuerpo_email(df_preliminar, cid_grafico, valor_maximo, valor_minimo)
send_email(ruta_grafico, destinatarios, asunto, cuerpo_html, destinatarios_cc)







