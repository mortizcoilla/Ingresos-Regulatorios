from datetime import datetime

import pandas as pd
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time

def ipc(year):
    driver_path = r"C:\workspace\IngresosRegulados\msedgedriver\msedgedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Edge(service=service)

    url = f"https://www.sii.cl/valores_y_fechas/utm/utm{year}.htm"

    try:
        driver.get(url)
        table = driver.find_element(By.XPATH, '//table')
        rows = table.find_elements(By.TAG_NAME, "tr")

        table_data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells if cell.text]
            if row_data:
                table_data.append(row_data)

    except NoSuchElementException:
        print(f"No se encontró un elemento esperado en la página del año {year}.")
        return pd.DataFrame()
    except WebDriverException as e:
        print(f"Se produjo un error con el WebDriver: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error inesperado: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()

    if table_data:
        column_names = ['UTM', 'UTA', 'IPC', 'VPM', 'VPA', 'U12M']
        df = pd.DataFrame(table_data, columns=column_names)
        df['Periodo'] = pd.date_range(start=f'{year}-01-01', periods=len(df), freq='MS')
        df = df[['Periodo'] + [col for col in df.columns if col != 'Periodo']]
        df['IPC'] = pd.to_numeric(df['IPC'].str.replace(',', '.'), errors='coerce')
        df['Periodo'] = pd.to_datetime(df['Periodo'])

        return df[['Periodo', 'IPC']]
    else:
        return pd.DataFrame()


df_ipc = ipc(2024)
print(df_ipc)
print(df_ipc.dtypes)

