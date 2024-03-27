def generar_rutas(fecha_entrada):
    anio = fecha_entrada[:4]
    mes = fecha_entrada[4:]

    ruta_archivo_nacional = "C:\\Users\\QV6522\\workspace\\BBDD\\02_Cargos Unicos\\Preliminares\\{}-Preliminar\\Saldos Transmisión Nacional D7T {}-pre.xlsx".format(
        anio + mes, anio + mes)

    ruta_archivo_zonal_y_dedicado = "C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\BBDD\\Saldos Transmisión Zonal y Dedicado D7T {}-pre.xlsx".format(
        anio + mes)

    return ruta_archivo_nacional, ruta_archivo_zonal_y_dedicado


fecha_entrada = "202401"
rutas = generar_rutas(fecha_entrada)
print("Ruta nacional:", rutas[0])
print("Ruta zonal y dedicado:", rutas[1])


