# Main
# Importaciones desde subdirectorios
from Peajes.procesamiento_datos.procesador import extract_dataframes, create_dataframe, procesar_datos_historicos, unir_dataframes
from Peajes.utilidades.estadisticas import calcular_estadisticas

from Peajes.utilidades.email_sender import evaluar_pago_total, seleccionar_y_enviar_email

# Importar configuraciones
from Peajes.utilidades.config import (
    ZIP_PATH,
    EXTRACTION_PATH,
    EXCEL_FILE_NAME,
    BBDD_PATH,
    DESTINATARIOS,
    ASUNTO_BASE
)

def main():
    """
    try:
        # Ejecutar el scraper
        open_website(SCRAPER_URL, DRIVER_PATH, DOWNLOAD_PATH)
    except Exception as e:
        print(f"Error en el scraper: {e}")
        return
    """
    try:
        # Procesar los datos descargados
        extracted_data = extract_dataframes(ZIP_PATH, EXTRACTION_PATH, EXCEL_FILE_NAME)
        df_preliminar = create_dataframe(extracted_data)
        df_historico = procesar_datos_historicos(BBDD_PATH)
        datos = unir_dataframes(df_preliminar, df_historico)
        estadisticas = calcular_estadisticas(df_historico)

        # Evaluar PagoTotal de df_preliminar
        pago_total_preliminar = df_preliminar['PagoTotal'].iloc[0]
        maximo = estadisticas['PagoTotal']['máximo']
        minimo = estadisticas['PagoTotal']['minimo']
        mensaje_valor = evaluar_pago_total(pago_total_preliminar, maximo, minimo)

        # Preparar para enviar el correo electrónico
        asunto = ASUNTO_BASE + " Resultados del Mes"

        # Seleccionar y enviar el correo electrónico según la elección del usuario
        seleccionar_y_enviar_email(df_preliminar, df_historico, estadisticas, DESTINATARIOS, ASUNTO_BASE, minimo, maximo)

    except Exception as e:
        print(f"Error en el procesamiento de datos: {e}")
        return


if __name__ == "__main__":
    main()
