# Proyecto para evaluación del VATT 

from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def ipc(year):
    driver_path = 'C:/Users/QV6522/Workspace/IngresosRegulados/msedgedriver/msedgedriver.exe'
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

        return df[['Periodo', 'IPC']]
    else:
        return pd.DataFrame()


def dolar(year):
    url = f"https://www.sii.cl/valores_y_fechas/dolar/dolar{year}.htm"

    driver_path = r'C:/Users/QV6522/Workspace/IngresosRegulados/msedgedriver/msedgedriver.exe'
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


def cpi(year):
    driver_path = r'C:/Users/QV6522/Workspace/IngresosRegulados/msedgedriver/msedgedriver.exe'
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
        return None
    except NoSuchElementException:
        print("Error: No se encontró uno de los elementos especificados en la página.")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None
    finally:
        driver.quit()

    df_cpi = pd.DataFrame(data[1:], columns=data[0])
    df_cpi = df_cpi.drop(['HALF1', 'HALF2'], axis=1)
    df_cpi_filtered = df_cpi[df_cpi['Year'].astype(int) == year]
    df_cpi_transposed = df_cpi_filtered.T
    df_cpi_reset = df_cpi_transposed.reset_index()

    meses = df_cpi_reset['index'][1:]
    año = year

    fechas = pd.to_datetime(meses.apply(lambda x: f"{x} {año}"), format='%b %Y')

    df_cpi_reset['Periodo'] = fechas

    cpi_values = df_cpi_reset.iloc[1:, 1]

    df_cpi = pd.DataFrame({
        'Periodo': fechas,
        'CPI': cpi_values.values
    }).reset_index(drop=True)

    return df_cpi


def macroeconomicos(year):
    current_year = datetime.now().year
    years = range(year, current_year + 1)

    dfs_ipc = [ipc(y) for y in years]
    dfs_dolar = [dolar(y) for y in years]
    dfs_cpi = [cpi(y) for y in years]

    df_ipc_concat = pd.concat(dfs_ipc).reset_index(drop=True)
    df_dolar_concat = pd.concat(dfs_dolar).reset_index(drop=True)
    df_cpi_concat = pd.concat(dfs_cpi).reset_index(drop=True)

    df_combinado = pd.merge(df_ipc_concat, df_dolar_concat, on='Periodo', how='outer', suffixes=('_ipc', '_dolar'))
    df_combinado_final = pd.merge(df_combinado, df_cpi_concat, on='Periodo', how='outer')
    df_combinado_final.sort_values(by='Periodo', inplace=True)

    inicio_mes_actual = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    df_combinado_final = df_combinado_final[df_combinado_final['Periodo'] < inicio_mes_actual]

    return df_combinado_final


def itd_vatt(ruta_itd, fecha):
    df_anexo1 = pd.read_excel(ruta_itd, sheet_name='TablaAnexo1', engine='openpyxl')
    df_anexo1_filtrado = df_anexo1.loc[df_anexo1['Empresa Propietaria'].isin(['E-CL'])]
    # ASUNTO DE LAS OBRAS DE AMPLIACION
    df_indexacion = pd.read_excel(ruta_itd, sheet_name='Indexacion', engine='openpyxl')
    df_itd = pd.merge(df_anexo1_filtrado, df_indexacion, on=['Sistema', 'Zona', 'Tipo Tramo (*)'], how='left')

    fecha_dt = datetime.strptime(fecha, '%Y%m')
    target_month = (fecha_dt.month - 3) % 12 + 1
    target_year = fecha_dt.year if fecha_dt.month > 2 else fecha_dt.year - 1
    if target_month > fecha_dt.month: target_year -= 1
    fecha_inicio = datetime(target_year, target_month, 1)

    df_macro = macroeconomicos(target_year)
    df_macro['Periodo'] = pd.to_datetime(df_macro['Periodo'])
    df_macro_filtrado = df_macro[df_macro['Periodo'] == fecha_inicio]

    if df_macro_filtrado.empty:
        print(f"No se encontraron datos para el periodo {fecha_inicio.strftime('%Y-%m')}")
        return df_itd

    fecha_exacta = datetime.strptime(fecha, '%Y%m')
    df_macro_exacto = df_macro[df_macro['Periodo'] == pd.to_datetime(fecha_exacta)]
    if not df_macro_exacto.empty:
        D_P = float(df_macro_exacto.iloc[0]['Dólar'])
    else:
        D_P = None

    IPC_0 = 97.89
    CPI_0 = 246.663
    D_0 = 629.55
    Ta_0 = 0.06
    t_0 = 0.255
    Ta_k = 0.06
    t_k = 0.27

    """
    df_itd['IPC_k'] = float(df_macro_filtrado.iloc[0]['IPC'])
    df_itd['IPC_0'] = IPC_0

    df_itd['D_0'] = D_0
    df_itd['D_k'] = float(df_macro_filtrado.iloc[0]['Dólar'])
    df_itd['D_P'] = D_P

    df_itd['CPI_k'] = float(df_macro_filtrado.iloc[0]['CPI'])
    df_itd['CPI_0'] = CPI_0

    df_itd['Ta_k'] = Ta_k
    df_itd['Ta_O'] = Ta_0

    df_itd['t_O'] = t_0
    df_itd['t_k'] = t_k

    df_itd['R_IPC'] = float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0
    df_itd['R_D'] = D_0 / float(df_macro_filtrado.iloc[0]['Dólar'])
    df_itd['R_CPI'] = float(df_macro_filtrado.iloc[0]['CPI']) / CPI_0
    df_itd['R_Ta'] = (1+Ta_k)/(1+Ta_0)
    df_itd['R_t'] = (t_k/t_0)*((1-t_0)/(1-t_k))
    """

    df_itd['AVI USD'] = df_itd['AVI US$'] * (df_itd['alfa'] * (float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0) * (
            D_0 / float(df_macro_filtrado.iloc[0]['Dólar'])) + df_itd['beta'] * (
                                                     float(df_macro_filtrado.iloc[0]['CPI']) / CPI_0) * (
                                                     (1 + Ta_k) / (1 + Ta_0)))

    df_itd['COMA USD'] = df_itd['COMA US$'] * (float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0) * (
            D_0 / float(df_macro_filtrado.iloc[0]['Dólar']))

    df_itd['AEIR USD'] = df_itd['AEIR US$'] * (df_itd['gama'] * (float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0) * (
            D_0 / float(df_macro_filtrado.iloc[0]['Dólar'])) + df_itd['delta'] * (
                                                       float(df_macro_filtrado.iloc[0]['CPI']) / CPI_0) * (
                                                       (1 + Ta_k) / (1 + Ta_0))) * (
                                     (t_k / t_0) * ((1 - t_0) / (1 - t_k)))

    df_itd['VATT USD'] = df_itd['AVI USD'] + df_itd['COMA USD'] + df_itd['AEIR USD']

    df_itd['AVI CLP'] = D_P * df_itd['AVI US$'] * (
                df_itd['alfa'] * (float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0) * (
                D_0 / float(df_macro_filtrado.iloc[0]['Dólar'])) + df_itd['beta'] * (
                        float(df_macro_filtrado.iloc[0]['CPI']) / CPI_0) * (
                        (1 + Ta_k) / (1 + Ta_0)))

    df_itd['COMA CLP'] = D_P * df_itd['COMA US$'] * (float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0) * (
            D_0 / float(df_macro_filtrado.iloc[0]['Dólar']))

    df_itd['AEIR CLP'] = D_P * df_itd['AEIR US$'] * (
                df_itd['gama'] * (float(df_macro_filtrado.iloc[0]['IPC']) / IPC_0) * (
                D_0 / float(df_macro_filtrado.iloc[0]['Dólar'])) + df_itd['delta'] * (
                        float(df_macro_filtrado.iloc[0]['CPI']) / CPI_0) * (
                        (1 + Ta_k) / (1 + Ta_0))) * ((t_k / t_0) * ((1 - t_0) / (1 - t_k)))

    df_itd['VATT CLP'] = df_itd['AVI CLP'] + df_itd['COMA CLP'] + df_itd['AEIR CLP']

    return df_itd


def leer_datos_transmision_y_dedicado():
    ruta_archivo_zonal_y_dedicado = ("C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\BBDD\\Saldos "
                                     "Transmisión Zonal y Dedicado D7T 2311-def.xlsx")

    ruta_archivo_nacional = ("C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\BBDD\\Saldos Transmisión "
                             "Nacional D7T 2311-def.xlsx")

    # Leer Prorrata_Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Zonal', usecols='B:AA', skiprows=4)
    df_zonal_filtrado = df_zonal[df_zonal['PROPIETARIO'] == 'ENGIE']
    df_zonal_filtrado['MES'] = pd.to_datetime(df_zonal_filtrado['MES'])
    df_zonal_filtrado = df_zonal_filtrado[df_zonal_filtrado['MES'] == '2023-11-01']
    df_zonal_filtrado = df_zonal_filtrado.sort_values(by='MES', ascending=False)
    df_zonal_filtrado = df_zonal_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_zonal_filtrado['Sistema'] = 'zonal'

    # Leer Prorrata_Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Dedicado', usecols='B:U',
                                skiprows=5)
    df_dedicado_filtrado = df_dedicado[df_dedicado['PROPIETARIO'] == 'ENGIE']
    df_dedicado_filtrado['MES'] = pd.to_datetime(df_dedicado_filtrado['MES'])
    df_dedicado_filtrado = df_dedicado_filtrado[df_dedicado_filtrado['MES'] == '2023-11-01']
    df_dedicado_filtrado = df_dedicado_filtrado.sort_values(by='MES', ascending=False)
    df_dedicado_filtrado = df_dedicado_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_dedicado_filtrado['Sistema'] = 'dedicado'

    # Leer Saldos 25T
    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)
    df_25t_filtrado = df_25t[df_25t['PROPIETARIO'] == 'ETSA']
    df_25t_filtrado['MES'] = pd.to_datetime(df_25t_filtrado['MES'])
    df_25t_filtrado = df_25t_filtrado[df_25t_filtrado['MES'] == '2023-11-01']
    df_25t_filtrado = df_25t_filtrado.sort_values(by='MES', ascending=False)
    df_25t_filtrado = df_25t_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_25t_filtrado['Sistema'] = '25T'

    # Leer Saldos CU
    df_cu = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos CU', usecols='B:S', skiprows=5)
    df_cu_filtrado = df_cu[df_cu['PROPIETARIO'] == 'ETSA']
    df_cu_filtrado['MES'] = pd.to_datetime(df_cu_filtrado['MES'])
    df_cu_filtrado = df_cu_filtrado[df_cu_filtrado['MES'] == '2023-11-01']
    df_cu_filtrado = df_cu_filtrado.sort_values(by='MES', ascending=False)
    df_cu_filtrado = df_cu_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_cu_filtrado['Sistema'] = 'CU'

    # Concatenar todos los DataFrames filtrados
    df_concatenado = pd.concat([df_zonal_filtrado, df_dedicado_filtrado, df_25t_filtrado, df_cu_filtrado],
                               ignore_index=True)
    cols = ['Sistema'] + [col for col in df_concatenado.columns if col != 'Sistema']
    df_concatenado = df_concatenado[cols]

    return df_concatenado


# --------------------------------------------------------------------------------------------------------------------------------------------------
# Llamada a la función y asignación de los resultados
df_total = leer_datos_transmision_y_dedicado()
print(df_total)
# --------------------------------------------------------------------------------------------------------------------------------------------------
# año_de_interés = 2013
# df_indices_macroeconomicos = macroeconomicos(año_de_interés)
# print(df_indices_macroeconomicos)
# df_indices_macroeconomicos.to_excel(r"C:\Users\QV6522\Workspace\indices_macro.xlsx", index=False)
# --------------------------------------------------------------------------------------------------------------------------------------------------
# ruta_itd = r'C:/Users/QV6522/Workspace/IngresosRegulados/Proyectos/BBDD/Resultados_ITD_rec.xlsx'
# fecha = '202311'
# df_resultante = itd_vatt(ruta_itd, fecha)
# print(df_resultante)
# ruta_exportacion = r'C:\Users\QV6522\Workspace\resultados_itd_vatt.xlsx'
# df_resultante.to_excel(ruta_exportacion, index=False, engine='openpyxl')
# print(f"DataFrame exportado con éxito a {ruta_exportacion}")
# --------------------------------------------------------------------------------------------------------------------------------------------------
