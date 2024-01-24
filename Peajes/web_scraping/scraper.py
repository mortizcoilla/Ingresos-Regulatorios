# scraper
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service


def open_website(url, driver_path, download_path):
    service = Service(driver_path)
    service.start()

    options = webdriver.EdgeOptions()
    prefs = {"download.default_directory": download_path}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Edge(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(180)
    finally:
        driver.quit()