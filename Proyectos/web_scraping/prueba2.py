# Proyecto para evaluación del VATT

from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def dolar(year):
    url = f"https://www.sii.cl/valores_y_fechas/dolar/dolar{year}.htm"

    driver_path = r"C:\workspace\IngresosRegulados\msedgedriver\msedgedriver.exe"
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-id='sel_mes']"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Todos los meses')]"))).click()
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "table_export")))
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_element(By.ID, "table_export").find_elements(By.TAG_NAME, "tr")) > 1
        )

        table = driver.find_element(By.ID, "table_export")
        rows = table.find_elements(By.TAG_NAME, "tr")
        table_data = [[cell.text for cell in row.find_elements(By.TAG_NAME, "td")] for row in rows[1:]]
    except TimeoutException as e:
        print("Se produjo un error al cargar la página o al interactuar con los elementos de la página: ", e)
        return None
    finally:
        driver.quit()

    df = pd.DataFrame(table_data)
    df_promedio = df.tail(1)
    df_promedio_transpuesto = df_promedio.T
    df_promedio_transpuesto.columns = ['Dólar']
    df_promedio_transpuesto.reset_index(inplace=True, drop=True)
    fechas = pd.date_range(start=str(year) + '-01-01', periods=len(df_promedio_transpuesto), freq='MS')
    df_promedio_transpuesto['Periodo'] = fechas
    df_dólar = df_promedio_transpuesto[['Periodo', 'Dólar']].copy()
    df_dólar['Dólar'] = pd.to_numeric(df_dólar['Dólar'].str.replace(',', ''), errors='coerce')
    df_dólar['Dólar'] = pd.to_numeric(df_dólar['Dólar'], errors='coerce') / 100

    return df_dólar


prueba = dolar(2023)
print(prueba)