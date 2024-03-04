from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pandas as pd
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

    return pd.DataFrame({
        'Periodo': fechas,
        'CPI': cpi_values
    }).reset_index(drop=True)


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

        df = pd.DataFrame(data[1:], columns=['Día'] + [f'{month}' for month in range(1, 13)])

        for column in df.columns[1:]:
            df[column] = df[column].apply(lambda x: x.replace(',', '.').strip() if isinstance(x, str) else x)
            df[column] = pd.to_numeric(df[column], errors='coerce')

        promedio_por_columna = df.iloc[:, 1:].mean().reset_index()
        promedio_por_columna.columns = ['Mes', 'Dólar']

        promedio_por_columna['Mes'] = pd.to_datetime(promedio_por_columna['Mes'].apply(lambda x: f"{year}-{x}-01"))

        promedio_por_columna.rename(columns={'Mes': 'Periodo'}, inplace=True)

        return promedio_por_columna

    except Exception as e:
        print("Se produjo un error: ", e)
    finally:
        driver.quit()


def indices(year):
    df_dolar = dolar(year)
    df_cpi = cpi(year)
    df_ipc = ipc(year)

    df_dolar['Periodo'] = df_dolar['Periodo'].dt.to_period('M').dt.to_timestamp()
    df_cpi['Periodo'] = df_cpi['Periodo'].dt.to_period('M').dt.to_timestamp()
    df_ipc['Periodo'] = df_ipc['Periodo'].dt.to_period('M').dt.to_timestamp()

    df_merge1 = pd.merge(df_dolar, df_cpi, on='Periodo', how='outer')
    df_final = pd.merge(df_merge1, df_ipc, on='Periodo', how='outer')

    df_final['Periodo'] = pd.to_datetime(df_final['Periodo'])

    df_final = df_final.sort_values(by='Periodo')

    filename = f"C:\\workspace\\IngresosRegulados\\Proyectos\\indices_macroeconomicos\\indices_macroeconomicos_{year}.xlsx"
    df_final.to_excel(filename, index=False, engine='openpyxl', sheet_name='indices')

    return df_final








