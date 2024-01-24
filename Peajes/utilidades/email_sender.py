# email_sender
import os
import win32com.client as win32
import datetime

from Peajes.utilidades.visualizaciones import graficar_datos_preliminar, graficar_datos_definitivo



def fecha_actual():
    fecha_actual = datetime.date.today()
    return fecha_actual.strftime("%d/%m/%Y")

def fecha_mes_anterior():
    hoy = datetime.date.today()
    primer_dia_del_mes = datetime.date(hoy.year, hoy.month, 1)
    ultimo_dia_del_mes_anterior = primer_dia_del_mes - datetime.timedelta(days=1)
    return ultimo_dia_del_mes_anterior.strftime("%B %Y")

def saludo():
    hora_actual = datetime.datetime.now()
    if hora_actual.hour < 12:
        return "Buenos días,"
    else:
        return "Buenas tardes,"

def evaluar_pago_total(pago_total_preliminar, maximo, minimo):
    if minimo <= pago_total_preliminar <= maximo:
        return "Valor dentro de lo esperado"
    else:
        return "Valor fuera de lo esperado"

def enviar_email_con_resultados(suma_pago_total, grafico_path, destinatarios, asunto, cuerpo_html):
    # Iniciar la aplicación de Outlook
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)

    # Configurar destinatarios y asunto
    mail.To = destinatarios
    # mail.CC = destinatarios_cc
    mail.Subject = asunto

    # Comprobar archivo gráfico
    if not os.path.exists(grafico_path):
        print(f"El archivo {grafico_path} no existe.")
        return

    # Adjuntar el archivo gráfico con un Content ID
    attachment = mail.Attachments.Add(grafico_path)
    cid = "MyGraphCID"
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001E", cid)

    # Configurar el cuerpo HTML del correo electrónico
    mail.HTMLBody = cuerpo_html.replace('cid:MyGraphCID', f'cid:{cid}')

    # Enviar el correo
    mail.Send()

def seleccionar_y_enviar_email(df_preliminar, df_historico, estadisticas, destinatarios, asunto_base, valor_minimo, valor_maximo):
    eleccion = input("Para preliminar presione 1, Para definitivo, presione 2: ")

    pago_total_preliminar = df_preliminar['PagoTotal'].iloc[0]
    if eleccion == '1':
        ruta_grafico = graficar_datos_preliminar(df_historico, estadisticas, df_preliminar)
        mensaje_valor = evaluar_pago_total(pago_total_preliminar, valor_maximo, valor_minimo)
        cuerpo_email = f"""
        <html>
          <body>
            <p>{saludo()}</p>
            <p>ETSA - Pago Total Preliminar: {pago_total_preliminar:.1f} MM de CLP - {mensaje_valor}</p>
            <img src="cid:MyGraphCID"><br>
            <p>Saludos Cordiales</p>
          </body>
        </html>
        """
        asunto = asunto_base + " - Informe Preliminar - " + fecha_mes_anterior()
    elif eleccion == '2':
        ruta_grafico = graficar_datos_definitivo(df_historico, estadisticas)
        cuerpo_email = f"""
        <html>
          <body>
            <p>{saludo()}</p>
            <p>A Continuación se presenta un resumen del proceso de Peajes Periodo {fecha_mes_anterior()} para pago.</p>
            <p>ETSA recibe {pago_total_preliminar:.1f} MM de CLP por este concepto.</p>
            <img src="cid:MyGraphCID"><br>
            <p>Saludos Cordiales.</p>
          </body>
        </html>
        """
        asunto = asunto_base + " - Informe Definitivo - " + fecha_mes_anterior()
    else:
        print("Selección no válida.")
        return

    enviar_email_con_resultados(pago_total_preliminar, ruta_grafico, destinatarios, asunto, cuerpo_email)

