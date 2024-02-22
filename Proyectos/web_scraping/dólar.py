from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd


def dolar(year):
    url = f"https://www.sii.cl/valores_y_fechas/dolar/dolar{year}.htm"

    # Asegúrate de que el path al driver sea correcto y corresponda a tu sistema
    driver_path = 'C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\msedgedriver\\msedgedriver.exe'
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
    df_promedio_transpuesto.columns = ['Dólar_Obs']
    df_promedio_transpuesto.reset_index(inplace=True)
    df_promedio_transpuesto.rename(columns={'index': 'Mes'}, inplace=True)
    fechas = pd.date_range(start=str(year) + '-01-01', periods=12, freq='MS')
    df_promedio_transpuesto['Periodo'] = fechas
    df_dólar = df_promedio_transpuesto[['Periodo', 'Dólar_Obs']]

    return df_dólar

dólar_2023 = dolar(2023)
dólar_2024 = dolar(2024)

dólar2324 = pd.concat([dólar_2023, dólar_2024]).reset_index(drop=True)

print(dólar2324)


