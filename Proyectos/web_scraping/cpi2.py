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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd


def cpi(year):
    driver_path = r"C:\workspace\IngresosRegulados\msedgedriver\msedgedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Edge(service=service)

    try:
        driver.get("https://data.bls.gov/cgi-bin/surveymost?cu")

        checkbox = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "series_id"))
        )
        checkbox.click()

        submit_button = driver.find_element(By.XPATH, "//input[@type='Submit']")
        submit_button.click()

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "table0"))
        )

        table = driver.find_element(By.ID, "table0")
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td") if row.find_elements(By.TAG_NAME, "td") else row.find_elements(
                By.TAG_NAME, "th")
            data.append([col.text for col in cols])

    except TimeoutException:
        print("Error: La página tardó demasiado en responder o un elemento no se cargó a tiempo.")
        return pd.DataFrame()
    except NoSuchElementException:
        print("Error: No se encontró uno de los elementos especificados en la página.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error inesperado: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()

    if not data:
        return pd.DataFrame()

    df_cpi = pd.DataFrame(data[1:], columns=data[0])
    df_cpi = df_cpi.drop(['HALF1', 'HALF2'], axis=1)
    df_cpi_filtered = df_cpi[df_cpi['Year'].astype(int) == year]
    df_cpi_transposed = df_cpi_filtered.T
    df_cpi_reset = df_cpi_transposed.reset_index()

    meses = df_cpi_reset['index'][1:]
    año = year

    fechas = pd.to_datetime(meses.apply(lambda x: f"{x} {año}"), format='%b %Y')
    cpi_values = pd.to_numeric(df_cpi_reset.iloc[1:, 1], errors='coerce')

    # Retorna directamente el DataFrame construido
    return pd.DataFrame({
        'Periodo': fechas,
        'CPI': cpi_values
    }).reset_index(drop=True)


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd


def cpi(year):
    driver_path = r"C:\workspace\IngresosRegulados\msedgedriver\msedgedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Edge(service=service)

    try:
        driver.get("https://data.bls.gov/cgi-bin/surveymost?cu")

        checkbox = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "series_id"))
        )
        checkbox.click()

        submit_button = driver.find_element(By.XPATH, "//input[@type='Submit']")
        submit_button.click()

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "table0"))
        )

        table = driver.find_element(By.ID, "table0")
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td") if row.find_elements(By.TAG_NAME, "td") else row.find_elements(
                By.TAG_NAME, "th")
            data.append([col.text for col in cols])

    except TimeoutException:
        print("Error: La página tardó demasiado en responder o un elemento no se cargó a tiempo.")
        return pd.DataFrame()
    except NoSuchElementException:
        print("Error: No se encontró uno de los elementos especificados en la página.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error inesperado: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()

    if not data:
        return pd.DataFrame()

    df_cpi = pd.DataFrame(data[1:], columns=data[0])
    df_cpi = df_cpi.drop(['HALF1', 'HALF2'], axis=1)
    df_cpi_filtered = df_cpi[df_cpi['Year'].astype(int) == year]
    df_cpi_transposed = df_cpi_filtered.T
    df_cpi_reset = df_cpi_transposed.reset_index()

    meses = df_cpi_reset['index'][1:]
    año = year

    fechas = pd.to_datetime(meses.apply(lambda x: f"{x} {año}"), format='%b %Y')
    cpi_values = pd.to_numeric(df_cpi_reset.iloc[1:, 1], errors='coerce')

    # Retorna directamente el DataFrame construido
    return pd.DataFrame({
        'Periodo': fechas,
        'CPI': cpi_values
    }).reset_index(drop=True)


# Ejemplo de llamada a la función
df_cpi_resultante = cpi(2022)
print(df_cpi_resultante)

