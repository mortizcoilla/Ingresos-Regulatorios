import os
import glob
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def cdp(codigo_fecha):
    chrome_driver_path = r"C:\Users\QV6522\Workspace\DRIVERS\chromedriver.exe"
    download_path = r"C:\Users\QV6522\Workspace\BBDD\CadenaDePagos"

    options = Options()
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    año, mes = divmod(codigo_fecha, 100)
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    mes_texto = meses[mes - 1]
    titulo_informe = f"Reporte Disconformidades PPagos {mes_texto}{str(año)[2:]}"

    try:
        url_base = (f"https://www.coordinador.cl/mercados/documentos/seguimiento-de-la-cadena-de-pago/reporte"
                    f"-disconformidades-sec/{año}-informe-mensual-sec/")
        driver.get(url_base)
        print(f"Navegando a {url_base}")

        elemento_titulo = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, f"//span[@title='{titulo_informe}']"))
        )
        print(f"Elemento '{titulo_informe}' encontrado en la página.")

        boton_descarga = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//span[@title='{titulo_informe}']/following::a[contains(@href, '.xlsx')]"))
        )
        boton_descarga.click()
        print("Botón de descarga clickeado.")

        time.sleep(30)

        lista_de_archivos = glob.glob(download_path + '/*')
        archivo_reciente = max(lista_de_archivos, key=os.path.getctime)
        nuevo_nombre = os.path.join(download_path, titulo_informe + ".xlsx")
        os.rename(archivo_reciente, nuevo_nombre)
        print(f"Archivo renombrado a {nuevo_nombre}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        driver.quit()


cdp(202310)
