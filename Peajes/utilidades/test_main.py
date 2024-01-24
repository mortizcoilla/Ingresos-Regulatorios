import unittest
import sys

# Añadir los subdirectorios al path
sys.path.append('../procesamiento_datos')
sys.path.append('../web_scraping')
sys.path.append('')

from email_sender import enviar_email_con_resultados

# Añadir los subdirectorios al path
sys.path.append('../procesamiento_datos')
sys.path.append('../web_scraping')
sys.path.append('')


class TestMainFunctions(unittest.TestCase):
    """
    def test_scraper(self):
        print("Probando scraper...")
        try:
            open_website(config.SCRAPER_URL, config.DRIVER_PATH, config.DOWNLOAD_PATH)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"open_website falló con la excepción {e}")

    def test_procesador(self):
        print("Probando funciones del procesador...")
        try:
            extracted_data = extract_dataframes(config.ZIP_PATH, config.EXTRACTION_PATH, config.EXCEL_FILE_NAME)
            df_preliminar = create_dataframe(extracted_data)
            df_historico = procesar_datos_historicos(config.BBDD_PATH)
            df_datos = unir_dataframes(df_preliminar, df_historico)
            self.assertTrue(isinstance(df_datos, pd.DataFrame))
        except Exception as e:
            self.fail(f"Funciones del procesador fallaron con la excepción {e}")

    def test_calculo_estadisticas(self):
        print("Probando cálculo de estadísticas...")
        data = {'Columna1': [1, 2, 3, 4, 5], 'Columna2': [2, 3, 4, 5, 6], 'NoNumerica': ['a', 'b', 'c', 'd', 'e']}
        df_prueba = pd.DataFrame(data)

        try:
            resultado = calcular_estadisticas(df_prueba)
            self.assertTrue(isinstance(resultado, dict))
            self.assertIn('Columna1', resultado)
            self.assertIn('Columna2', resultado)
            self.assertNotIn('NoNumerica', resultado)

            for columna in ['Columna1', 'Columna2']:
                self.assertIn('promedio', resultado[columna])
                self.assertIn('desvest', resultado[columna])
                self.assertIn('máximo', resultado[columna])
                self.assertIn('minimo', resultado[columna])
        except Exception as e:
            self.fail(f"calcular_estadisticas falló con la excepción {e}")

    def test_graficar_datos(self):
        print("Probando la generación de gráficos...")
        data_historico = {'Periodo': ['2023-01-01', '2023-02-01', '2023-03-01'], 'PagoTotal': [100, 200, 150]}
        df_historico = pd.DataFrame(data_historico)
        df_historico['Periodo'] = pd.to_datetime(df_historico['Periodo'])

        data_preliminar = {'Periodo': ['2023-04-01'], 'PagoTotal': [180]}
        df_preliminar = pd.DataFrame(data_preliminar)
        df_preliminar['Periodo'] = pd.to_datetime(df_preliminar['Periodo'])

        estadisticas = {'PagoTotal': {'promedio': 150, 'desvest': 50, 'máximo': 200, 'minimo': 100}}

        try:
            ruta_grafico = graficar_datos(df_historico, estadisticas, df_preliminar)
            self.assertTrue(isinstance(ruta_grafico, str))
            self.assertTrue(os.path.exists(ruta_grafico))
        except Exception as e:
            self.fail(f"graficar_datos falló con la excepción {e}")
    """
    def test_enviar_email_con_resultados_error_archivo_grafico(self):
        # Definir los parámetros de entrada
        suma_pago_total = 100000
        grafico_path = "/tmp/archivo_no_existente.png"
        destinatarios = ["destinatario1@example.com", "destinatario2@example.com"]
        asunto = "Informe de pago total"
        mensaje_valor = "Valor dentro de lo esperado"
        valor_minimo = 90000
        valor_maximo = 110000

        # Llamar a la función a probar
        with self.assertRaises(Exception):
            enviar_email_con_resultados(suma_pago_total, grafico_path, destinatarios, asunto, mensaje_valor,
                                        valor_minimo, valor_maximo)

        # Assertear que la función de prueba devuelve el mensaje de error esperado
        self.assertEqual(mail.Subject, "Informe de pago total")
        self.assertIn(f"El archivo {grafico_path} no existe.", mail.HTMLBody)


if __name__ == '__main__':
    unittest.main()
