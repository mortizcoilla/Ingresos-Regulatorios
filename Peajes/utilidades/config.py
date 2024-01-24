# Config
from datetime import datetime, timedelta


def generate_automatic_url():
    current_date = datetime.now()
    year, month = current_date.year, current_date.month
    url = f"https://www.coordinador.cl/wp-content/uploads/{year}/{month:02d}/Liquidacion-de-Peajes-preliminar.zip"
    return url

def previous_excel_name():
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    return f"Liquidación de Peajes - preliminar/Liquidación de Peajes {last_month.strftime('%y%m')}.xlsm"


# Parámetros scraper
SCRAPER_URL = generate_automatic_url()
DRIVER_PATH = 'C:\\Users\\QV6522\\OneDrive - ENGIE\\2023\\202311\\InformesRecurrentes\\msedgedriver.exe'
DOWNLOAD_PATH = 'C:\\Users\\QV6522\\Downloads'

# Parámetros procesador
ZIP_PATH = 'C:\\Users\\QV6522\\Downloads\\Liquidacion-de-Peajes-preliminar.zip'
EXTRACTION_PATH = 'C:\\Users\\QV6522\\Downloads'
EXCEL_FILE_NAME = previous_excel_name()
BBDD_PATH = '../BBDD/InformesRecurrentesBBDD.xlsx'

# Parámetros visualizaciones
GRAFICO_PATH = '/graficos'

# Parámetros email_sender
DESTINATARIOS = 'miguel.ortiz@external.engie.com'
# DESTINATARIOS = 'paul.baillarie@engie.com;francisco.bas@engie.com;claudio.troncoso@engie.com;cristian.jorquera@engie.com;reinaldo.rupallan@engie.com'
DESTINATARIOS_CC = 'miguel.ortiz@external.engie.com'
ASUNTO_BASE = 'Informes Recurrentes - '
