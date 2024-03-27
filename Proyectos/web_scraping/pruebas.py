def generar_rutas(fecha_entrada):
    # Mapeo de números de mes a nombres de mes
    meses = {
        "01": "Enero", "02": "Febrero", "03": "Marzo",
        "04": "Abril", "05": "Mayo", "06": "Junio",
        "07": "Julio", "08": "Agosto", "09": "Septiembre",
        "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    anio = fecha_entrada[:4]
    mes = fecha_entrada[4:]

    ruta_archivo_indices = (f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\indices_macroeconomicos"
                            f"\\indices_macroeconomicos_{anio}.xlsx")

    # Corrección aplicada aquí para el formato de la carpeta
    ruta_archivo_nacional = (f"C:\\Users\\QV6522\\workspace\\BBDD\\02_Cargos Unicos\\Preliminares\\{mes}{anio[-2:]}-Preliminar"
                             f"\\Saldos Transmisión Nacional D7T {mes}{anio[-2:]}-pre.xlsx")

    ruta_archivo_zonal_y_dedicado = (f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\BBDD\\Saldos "
                                     f"Transmisión Zonal y Dedicado D7T {anio + mes}-pre.xlsx")

    nombre_mes = meses[mes]
    ruta_archivo_ivt_preliminar = (f"C:\\Users\\QV6522\\workspace\\BBDD\\03_IVT\\preliminares\\"
                                   f"IVT_{nombre_mes}_{anio}_Pre\\Anexo 02.a Cuadros de Pago_Balances_SEN_{nombre_mes[:3]}{anio[2:]}_pre.xlsb")

    ruta_archivo_ivt_definitivo = (f"C:\\Users\\QV6522\\workspace\\BBDD\\03_IVT\\definitivos\\"
                                   f"IVT_{nombre_mes}_{anio}_Def\\Anexo 02.b Cuadros de Pago_Potencia_SEN_{nombre_mes[:3]}{anio[2:]}_Def.xlsb")

    return (ruta_archivo_indices, ruta_archivo_nacional, ruta_archivo_zonal_y_dedicado,
            ruta_archivo_ivt_preliminar, ruta_archivo_ivt_definitivo)

# Ejemplo de uso
rutas = generar_rutas("202304")
for ruta in rutas:
    print(ruta)




