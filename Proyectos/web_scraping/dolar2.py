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


def dolar(year):
    url = "https://si3.bcentral.cl/indicadoressiete/secure/Serie.aspx?gcode=PRE_TCO&param=RABmAFYAWQB3AGYAaQBuAEkALQAzADUAbgBNAGgAaAAkADUAVwBQAC4AbQBYADAARwBOAGUAYwBjACMAQQBaAHAARgBhAGcAUABTAGUAdwA1ADQAMQA0AE0AawBLAF8AdQBDACQASABzAG0AXwA2AHQAawBvAFcAZwBKAEwAegBzAF8AbgBMAHIAYgBDAC4ARQA3AFUAVwB4AFIAWQBhAEEAOABkAHkAZwAxAEEARAA%3d"

    driver_path = r"C:\workspace\IngresosRegulados\msedgedriver\msedgedriver.exe"
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service)

    try:
        driver.get(url)
        driver.maximize_window()

        select_element = Select(driver.find_element(By.ID, "DrDwnFechas"))
        select_element.select_by_value(str(year))

        time.sleep(3)

        table = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div[6]/div/div/table/tbody/tr/td/div/div/table")

        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            data.append(row_data)

        headers = ['Día'] + [f'01-{str(i).zfill(2)}-{year}' for i in range(1, 13)]

        df = pd.DataFrame(data[1:], columns=headers)

        for column in df.columns[1:]:
            df[column] = df[column].apply(lambda x: x.replace(',', '.').strip() if isinstance(x, str) else x)
            df[column] = pd.to_numeric(df[column], errors='coerce')

        promedio_por_columna = df.iloc[:, 1:].mean()
        df_dólar = promedio_por_columna.to_frame().reset_index()
        df_dólar.columns = ['Periodo', 'Dólar']
        df_dólar['Periodo'] = pd.to_datetime(df_dólar['Periodo'])

        return df_dólar

    except Exception as e:
        print("Se produjo un error: ", e)
    finally:
        driver.quit()


df_dolar = dolar(2024)
print(df_dolar)
print(df_dolar.dtypes)