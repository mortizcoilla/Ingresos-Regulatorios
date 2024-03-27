def generar_rutas(fecha_entrada):
    meses = {
        "01": "Enero", "02": "Febrero", "03": "Marzo",
        "04": "Abril", "05": "Mayo", "06": "Junio",
        "07": "Julio", "08": "Agosto", "09": "Septiembre",
        "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    anio = fecha_entrada[:4]
    mes = fecha_entrada[4:]
    mes_nombre = meses[mes]

    ruta_archivo_indices = f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\indices_macroeconomicos\\indices_macroeconomicos_{anio}.xlsx"

    ruta_archivo_nacional = f"C:\\Users\\QV6522\\workspace\\BBDD\\02_Cargos Unicos\\Preliminares\\{anio[2:]}{mes}-Preliminar\\Saldos Transmisión Nacional D7T {anio[2:]}{mes}-pre.xlsx"

    ruta_archivo_zonal_y_dedicado = f"C:\\Users\\QV6522\\workspace\\BBDD\\02_Cargos Unicos\\Preliminares\\{anio[2:]}{mes}-Preliminar\\Saldos Transmisión Zonal y Dedicado D7T {anio[2:]}{mes}-pre.xlsx"

    ruta_archivo_ivt_preliminar = f"C:\\Users\\QV6522\\workspace\\BBDD\\03_IVT\\preliminares\\IVT_{mes_nombre}_{anio}_Pre\\Anexo 02.a Cuadros de Pago_Balances_SEN_{mes_nombre[:3]}{anio[2:]}_pre.xlsb"

    ruta_archivo_ivt_definitivo = f"C:\\Users\\QV6522\\workspace\\BBDD\\03_IVT\\preliminares\\IVT_{mes_nombre}_{anio}_Def\\Anexo 02.b Cuadros de Pago_Potencia_SEN_{mes_nombre[:3]}{anio[2:]}_pre.xlsb"

    return (ruta_archivo_indices,
            ruta_archivo_nacional,
            ruta_archivo_zonal_y_dedicado,
            ruta_archivo_ivt_preliminar,
            ruta_archivo_ivt_definitivo)


rutas = generar_rutas("202401")
for ruta in rutas:
    print(ruta)







