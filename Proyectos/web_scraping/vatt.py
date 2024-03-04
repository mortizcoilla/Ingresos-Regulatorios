import pandas as pd


def k_index(fecha_entrada):
    fecha_formato_completo = f"{fecha_entrada}01"
    fecha_datetime = pd.to_datetime(fecha_formato_completo, format='%Y%m%d')
    fecha_tres_meses_antes = fecha_datetime - pd.DateOffset(months=3)
    año_tres_meses_antes = fecha_tres_meses_antes.year
    mes_tres_meses_antes = fecha_tres_meses_antes.month
    fecha_tres_meses_antes_yyyymm = f"{año_tres_meses_antes}{mes_tres_meses_antes:02d}"

    def leer_y_filtrar(fecha):
        año = fecha[:4]
        ruta_archivo = f"C:\\workspace\\IngresosRegulados\\Proyectos\\indices_macroeconomicos\\indices_macroeconomicos_{año}.xlsx"
        df = pd.read_excel(ruta_archivo, sheet_name='indices', engine='openpyxl')
        df['Periodo'] = pd.to_datetime(df['Periodo']).dt.to_period('M')
        fecha_filtrado = pd.Period(f"{fecha}01", freq='M')
        df_filtrado = df[df['Periodo'] == fecha_filtrado]

        D_k_temp = df_filtrado['Dólar'].values[0] if not df_filtrado['Dólar'].empty else None
        CPI_k_temp = df_filtrado['CPI'].values[0] if not df_filtrado['CPI'].empty else None
        IPC_k_temp = df_filtrado['IPC'].values[0] if not df_filtrado['IPC'].empty else None

        return D_k_temp, CPI_k_temp, IPC_k_temp

    D_k, CPI_k, IPC_k = leer_y_filtrar(fecha_entrada)
    D, CPI, IPC = leer_y_filtrar(fecha_tres_meses_antes_yyyymm)

    return D_k, CPI_k, IPC_k, D, CPI, IPC


def itd():
    ruta_itd = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Resultados_ITD_rec.xlsx"

    df_anexo1 = pd.read_excel(ruta_itd, sheet_name='TablaAnexo1', engine='openpyxl')
    df_anexo1_filtrado = df_anexo1.loc[df_anexo1['Empresa Propietaria'].isin(['E-CL'])]
    df_anexo1_filtrado = df_anexo1_filtrado.loc[~df_anexo1_filtrado['NombreTramo'].eq('Iquique 066->Pozo Almonte 066')]
    # ASUNTO DE LAS OBRAS DE AMPLIACION
    df_indexacion = pd.read_excel(ruta_itd, sheet_name='Indexacion', engine='openpyxl')
    df_itd = pd.merge(df_anexo1_filtrado, df_indexacion, on=['Sistema', 'Zona', 'Tipo Tramo (*)'], how='left')

    return df_itd


def vatt(df_itd, fecha):
    # Valores Base
    IPC_0 = 97.89
    CPI_0 = 246.663
    D_0 = 629.55
    Ta_0 = 0.06
    t_0 = 0.255
    Ta_k = 0.06
    t_k = 0.27

    # Obtener los valores del periodo y n-2
    D_k, CPI_k, IPC_k, D, CPI, IPC = k_index(fecha)

    # Realizar cálculos
    df_vatt = df_itd.copy()
    df_vatt['AVI USD'] = df_vatt['AVI US$'] * (
                df_vatt['alfa'] * (IPC / IPC_0) * (D_0 / D) + df_vatt['beta'] * (CPI / CPI_0) * (
                    (1 + Ta_k) / (1 + Ta_0)))
    df_vatt['COMA USD'] = df_vatt['COMA US$'] * (IPC / IPC_0) * (D_0 / D)
    df_vatt['AEIR USD'] = df_vatt['AEIR US$'] * (
                df_vatt['gama'] * (IPC / IPC_0) * (D_0 / D) + df_vatt['delta'] * (CPI / CPI_0) * (
                    (1 + Ta_k) / (1 + Ta_0))) * ((t_k / t_0) * ((1 - t_0) / (1 - t_k)))
    df_vatt['VATT USD'] = df_vatt['AVI USD'] + df_vatt['COMA USD'] + df_vatt['AEIR USD']

    # Convertir a CLP
    df_vatt['AVI CLP'] = df_vatt['AVI USD'] * D_k
    df_vatt['COMA CLP'] = df_vatt['COMA USD'] * D_k
    df_vatt['AEIR CLP'] = df_vatt['AEIR USD'] * D_k
    df_vatt['VATT CLP'] = df_vatt['VATT USD'] * D_k

    # Retornar el DataFrame con VATT calculado
    return df_vatt


def vatt_calc(df_vatt):
    df_vatt_agg = df_vatt.groupby('Sistema', as_index=False)['VATT CLP'].sum()

    return df_vatt_agg


def cu_coordinador(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')

    ruta_archivo_zonal_y_dedicado = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"
    ruta_archivo_nacional = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

    # Leer Prorrata_Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Zonal', usecols='B:AA', skiprows=4)
    df_zonal_filtrado = df_zonal[df_zonal['PROPIETARIO'] == 'ENGIE'].copy()
    df_zonal_filtrado['MES'] = pd.to_datetime(df_zonal_filtrado['MES'])
    df_zonal_filtrado = df_zonal_filtrado[df_zonal_filtrado['MES'] == fecha_filtrado]
    df_zonal_filtrado['Sistema'] = 'Zonal'

    # Leer Prorrata_Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Dedicado', usecols='B:U',
                                skiprows=5)
    df_dedicado_filtrado = df_dedicado[df_dedicado['PROPIETARIO'] == 'ENGIE'].copy()
    df_dedicado_filtrado['MES'] = pd.to_datetime(df_dedicado_filtrado['MES'])
    df_dedicado_filtrado = df_dedicado_filtrado[df_dedicado_filtrado['MES'] == fecha_filtrado]
    df_dedicado_filtrado['Sistema'] = 'Dedicado'

    # Leer Saldos 25T
    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)
    df_25t_filtrado = df_25t[df_25t['PROPIETARIO'] == 'ETSA'].copy()
    df_25t_filtrado['MES'] = pd.to_datetime(df_25t_filtrado['MES'])
    df_25t_filtrado = df_25t_filtrado[df_25t_filtrado['MES'] == fecha_filtrado]
    df_25t_filtrado['Sistema'] = '25T'

    # Leer Saldos CU
    df_cu = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos CU', usecols='B:S', skiprows=5)
    df_cu_filtrado = df_cu[df_cu['PROPIETARIO'] == 'ETSA'].copy()
    df_cu_filtrado['MES'] = pd.to_datetime(df_cu_filtrado['MES'])
    df_cu_filtrado = df_cu_filtrado[df_cu_filtrado['MES'] == fecha_filtrado]
    df_cu_filtrado['Sistema'] = 'CU'

    df_concatenado = pd.concat([df_zonal_filtrado, df_dedicado_filtrado, df_25t_filtrado, df_cu_filtrado], ignore_index=True)
    cols = ['Sistema', 'MES', 'PROPIETARIO', 'VATT [$]']
    df_concatenado = df_concatenado[cols]

    return df_concatenado


def vatt_coord(df):
    # Separar los datos entre Zonal/Dedicado y Nacional (25T, CU)
    df_zonal_dedicado = df[df['Sistema'].isin(['Zonal', 'Dedicado'])][['Sistema', 'VATT [$]']]
    df_nacional = df[df['Sistema'].isin(['25T', 'CU'])][['Sistema', 'VATT [$]']]

    # Sumar los valores de 'VATT [$]' para los registros nacionales y crear una nueva fila para el total nacional
    suma_nacional = df_nacional['VATT [$]'].sum()
    # Crear un DataFrame para la suma nacional con la etiqueta 'Nacional'
    suma_nacional_df = pd.DataFrame({'Sistema': ['Nacional'], 'VATT [$]': [suma_nacional]})

    # Concatenar los datos Zonal/Dedicado con la suma Nacional
    df_final = pd.concat([df_zonal_dedicado, suma_nacional_df], ignore_index=True)

    # Ordenar el DataFrame final por 'VATT [$]' de forma descendente
    df_final = df_final.sort_values(by='VATT [$]', ascending=False)

    return df_final
# ---------------------------------------------------------------------------------------------------------------------


def vatt_final(fecha):
    df_itd_preparado = itd()
    df_vatt = vatt(df_itd_preparado, fecha)
    df_vatt_agg = vatt_calc(df_vatt)

    df_inicial = cu_coordinador(fecha)
    df_final = vatt_coord(df_inicial)

    df_merged = pd.merge(df_vatt_agg, df_final, on='Sistema', how='left')
    df_merged.rename(columns={'VATT CLP': 'VATT Calculado', 'VATT [$]': 'VATT Informado'}, inplace=True)
    return df_merged


print("\n202311")
fecha = '202311'
df_merged_final = vatt_final(fecha)
print(df_merged_final)

# Uso de la función
print("\n202401")
fecha2 = '202401'
df_merged_final2 = vatt_final(fecha2)
print(df_merged_final2)

