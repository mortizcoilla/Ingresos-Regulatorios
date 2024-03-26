import pandas as pd
pd.set_option('display.max_columns', None)


def cu_coordinador(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')
    ruta_archivo_zonal_y_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"
    ruta_archivo_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

    # Leer Prorrata_Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado,
                             sheet_name='Prorrata_Zonal',
                             usecols='B:AA',
                             skiprows=4)

    df_zonal_filtrado = df_zonal[df_zonal['PROPIETARIO'] == 'ENGIE'].copy()
    df_zonal_filtrado['MES'] = pd.to_datetime(df_zonal_filtrado['MES'])
    df_zonal_filtrado = df_zonal_filtrado[df_zonal_filtrado['MES'] == fecha_filtrado]
    df_zonal_filtrado['Sistema'] = 'Zonal'

    # Leer Prorrata_Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado,
                                sheet_name='Prorrata_Dedicado',
                                usecols='B:U',
                                skiprows=5)

    df_dedicado_filtrado = df_dedicado[df_dedicado['PROPIETARIO'] == 'ENGIE'].copy()
    df_dedicado_filtrado['MES'] = pd.to_datetime(df_dedicado_filtrado['MES'])
    df_dedicado_filtrado = df_dedicado_filtrado[df_dedicado_filtrado['MES'] == fecha_filtrado]
    df_dedicado_filtrado['Sistema'] = 'Dedicado'

    # Leer Saldos 25T
    df_25t = pd.read_excel(ruta_archivo_nacional,
                           sheet_name='Saldos 25T',
                           usecols='B:AL',
                           skiprows=4)

    df_25t_filtrado = df_25t[df_25t['PROPIETARIO'] == 'ETSA'].copy()
    df_25t_filtrado['MES'] = pd.to_datetime(df_25t_filtrado['MES'])
    df_25t_filtrado = df_25t_filtrado[df_25t_filtrado['MES'] == fecha_filtrado]
    df_25t_filtrado['Sistema'] = '25T'

    # Leer Saldos CU
    df_cu = pd.read_excel(ruta_archivo_nacional,
                          sheet_name='Saldos CU',
                          usecols='B:S',
                          skiprows=5)

    df_cu_filtrado = df_cu[df_cu['PROPIETARIO'] == 'ETSA'].copy()
    df_cu_filtrado['MES'] = pd.to_datetime(df_cu_filtrado['MES'])
    df_cu_filtrado = df_cu_filtrado[df_cu_filtrado['MES'] == fecha_filtrado]
    df_cu_filtrado['Sistema'] = 'CU'

    df_concatenado = pd.concat([df_zonal_filtrado,
                                df_dedicado_filtrado,
                                df_25t_filtrado,
                                df_cu_filtrado],
                               ignore_index=True)
    cols = ['Sistema',
            'VATT/12 [$]',
            'ITE [$]',
            'ITP [$]',
            'Ingreso Repartición CT [$]',
            'Saldo Mensual [$]']

    df_concatenado = df_concatenado[cols]

    df_concatenado['Prueba'] = (df_concatenado['VATT/12 [$]'] -
                                (df_concatenado['ITE [$]'] +
                                df_concatenado['ITP [$]'] +
                                df_concatenado['Ingreso Repartición CT [$]'])
                                )

    return df_concatenado


fecha_entrada = "202401"
saldos = cu_coordinador(fecha_entrada)
print(saldos)

# SALDO = VATT MENSUAL - (ITE + ITP + PEAJE + CU + REASIGNACION) preliminar