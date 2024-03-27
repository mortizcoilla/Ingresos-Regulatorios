import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", message="Slicer List extension is not supported and will be removed")


def k_index(fecha_entrada):
    fecha_formato_completo = f"{fecha_entrada}01"
    fecha_datetime = pd.to_datetime(fecha_formato_completo, format='%Y%m%d')
    fecha_tres_meses_antes = fecha_datetime - pd.DateOffset(months=2)
    año_tres_meses_antes = fecha_tres_meses_antes.year
    mes_tres_meses_antes = fecha_tres_meses_antes.month
    fecha_tres_meses_antes_yyyymm = f"{año_tres_meses_antes}{mes_tres_meses_antes:02d}"

    def leer_y_filtrar(fecha):
        año = fecha[:4]
        ruta_archivo = f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\indices_macroeconomicos\\indices_macroeconomicos_{año}.xlsx"
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


# ----------------------------------------------------------------------------------------------------------------------
def itd():
    ruta_itd = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Resultados_ITD_rec.xlsx"

    df_anexo1 = pd.read_excel(ruta_itd, sheet_name='TablaAnexo1', engine='openpyxl')
    df_anexo1_filtrado = df_anexo1.loc[df_anexo1['Empresa Propietaria'].isin(['E-CL'])]
    df_anexo1_filtrado = df_anexo1_filtrado.loc[~df_anexo1_filtrado['NombreTramo'].eq('Iquique 066->Pozo Almonte 066')]

    df_index = pd.read_excel(ruta_itd, sheet_name='Indexacion', engine='openpyxl')
    df_itd = pd.merge(df_anexo1_filtrado, df_index, on=['Sistema', 'Zona', 'Tipo Tramo (*)'], how='left')

    return df_itd


def itd_amp():
    ruta_itd = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Resultados_ITD_rec.xlsx"

    df_amp = pd.read_excel(ruta_itd, sheet_name='Ampliaciones', engine='openpyxl')

    df_index = pd.read_excel(ruta_itd, sheet_name='Indexacion', engine='openpyxl')
    df_itd_amp = pd.merge(df_amp, df_index, on=['Sistema', 'Zona', 'Tipo Tramo (*)'], how='left')

    return df_itd_amp


def vatt(df_itd, fecha):
    IPC_0 = 97.89
    CPI_0 = 246.663
    D_0 = 629.55
    Ta_0 = 0.06
    t_0 = 0.255
    Ta_k = 0.06
    t_k = 0.27

    D_k, CPI_k, IPC_k, D, CPI, IPC = k_index(fecha)

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

    return df_vatt


def calcular_vatt_por_tramo(df_itd_amp, fecha):
    D_k, CPI_k, IPC_k, D, CPI, IPC = k_index(fecha)

    mes_fecha_interes = int(fecha[4:6])

    def aplicar_calculo(row):
        categoria_1 = ["Mejillones - Transformador 220/23 kV - 30 MVA (A)",
                       "Antofagasta - Seccionamiento Barra 110 kV (A)"]

        categoria_2 = ["Normalización Laberinto 220->El Cobre 220 (A)",
                       "Normalización el Cobre (A)",
                       "Ampliación y configuración Pozo Almonte (A)"]

        categoria_3 = ["Ampliación Nueva Crucero (A)"]

        categoria_4 = ["NUEVA SE EL ROSAL (A)",
                       "NUEVA SE CHUQUICAMATA (A)"]

        categoria_5 = ["NUEVA SE ALGARROBAL (A)"]

        categoria_6 = ["Ampliación en S/E Algarrobal (102)"]

        indexador_cat1 = (row['alfa'] * (IPC / 84.7) * (500.81 / D) + row['beta'] * (CPI / 233.546)) * 0.99988
        indexador_cat2 = row['alfa'] * (IPC / 95.93) * (668.63 / D) + row['beta'] * (CPI / 241.43)
        indexador_cat3 = row['alfa'] * (IPC / 94.47) * (682.07 / D) + row['beta'] * (CPI / 238.13)

        if mes_fecha_interes == 5:
            indexador_cat4 = (CPI / 249.554)
        else:
            indexador_cat4 = 1

        if mes_fecha_interes == 3:
            indexador_cat5 = (CPI / 249.554)
        else:
            indexador_cat5 = 0.94925

        avi_usd = 0
        coma_usd = 0
        if row['NombreTramo'] in categoria_1:
            avi_usd = row['AVI US$'] * indexador_cat1
            coma_usd = row['COMA US$'] * indexador_cat1
        elif row['NombreTramo'] in categoria_2:
            avi_usd = row['AVI US$'] * indexador_cat2
            coma_usd = row['COMA US$'] * indexador_cat2
        elif row['NombreTramo'] in categoria_3:
            avi_usd = row['AVI US$'] * indexador_cat3
            coma_usd = row['COMA US$'] * indexador_cat3
        elif row['NombreTramo'] in categoria_4:
            avi_usd = row['AVI US$'] * indexador_cat4
            coma_usd = row['COMA US$'] * indexador_cat4
        elif row['NombreTramo'] in categoria_5:
            avi_usd = row['AVI US$'] * indexador_cat5
            coma_usd = row['COMA US$'] * indexador_cat5
        elif row['NombreTramo'] in categoria_6:
            avi_usd = row['AVI US$'] * 1
            coma_usd = row['COMA US$'] * 1

        vatt_usd = avi_usd + coma_usd
        avi_clp = avi_usd * D_k
        coma_clp = coma_usd * D_k
        vatt_clp = avi_clp + coma_clp

        return pd.Series([avi_usd, coma_usd, vatt_usd, avi_clp, coma_clp, vatt_clp],
                         index=['AVI USD', 'COMA USD', 'VATT USD', 'AVI CLP', 'COMA CLP', 'VATT CLP'])

    calculated_columns = df_itd_amp.apply(aplicar_calculo, axis=1)
    df_vatt_amp = df_itd_amp.join(calculated_columns)

    return df_vatt_amp


def vatt_calc(df_vatt, df_vatt_amp):
    df_vatt_agg = df_vatt.groupby('Sistema', as_index=False)['VATT CLP'].sum()
    df_vatt_amp_agg = df_vatt_amp.groupby('Sistema', as_index=False)['VATT CLP'].sum()

    df_concat = pd.concat([df_vatt_agg, df_vatt_amp_agg])

    df_agg_vatt = df_concat.groupby('Sistema', as_index=False)['VATT CLP'].sum()

    return df_agg_vatt


# ----------------------------------------------------------------------------------------------------------------------
def cu_coordinador(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')

    ruta_archivo_zonal_y_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"
    ruta_archivo_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

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
    cols = ['Sistema', 'MES', 'PROPIETARIO', 'VATT [$]', 'ITE [$]', 'ITP [$]']
    df_concatenado = df_concatenado[cols]

    return df_concatenado


def vatt_coord(df):
    df_zonal_dedicado = df[df['Sistema'].isin(['Zonal', 'Dedicado'])][['Sistema', 'VATT [$]']]
    df_nacional = df[df['Sistema'].isin(['25T', 'CU'])][['Sistema', 'VATT [$]']]
    suma_nacional = df_nacional['VATT [$]'].sum()
    suma_nacional_df = pd.DataFrame({'Sistema': ['Nacional'], 'VATT [$]': [suma_nacional]})
    df_final_vatt = pd.concat([df_zonal_dedicado, suma_nacional_df], ignore_index=True)
    df_final_vatt = df_final_vatt.sort_values(by='VATT [$]', ascending=False)

    return df_final_vatt


def ite_coord(df):
    df_zonal_dedicado = df[df['Sistema'].isin(['Zonal', 'Dedicado'])][['Sistema', 'ITE [$]']]
    df_nacional = df[df['Sistema'].isin(['25T', 'CU'])][['Sistema', 'ITE [$]']]
    suma_nacional = df_nacional['ITE [$]'].sum()
    suma_nacional_df = pd.DataFrame({'Sistema': ['Nacional'], 'ITE [$]': [suma_nacional]})
    df_final_ite = pd.concat([df_zonal_dedicado, suma_nacional_df], ignore_index=True)
    df_final_ite = df_final_ite.sort_values(by='ITE [$]', ascending=False)

    return df_final_ite


def ite_def(fecha):

    archivo_ite_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Anexo 02.a Cuadros de Pago_Balances_SEN_Ene24_def.xlsb"
    archivo_ite_zonal_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Balance_2401_BD01.xlsm"

    # Leer ite_Nacional
    df_ite_nacional = pd.read_excel(archivo_ite_nacional, sheet_name='02.IT ENERGIA Ene-24 Def', usecols='B:DA', skiprows=9)
    df_ite_nacional = df_ite_nacional[df_ite_nacional['USUARIOS'] != 'Total']
    df_ite_nacional = df_ite_nacional.rename(columns={'EDELNOR_TRANSMISION': 'ITE [$]'})
    suma_ite_nac = df_ite_nacional['ITE [$]'].sum()
    resultado_ite_nacional = pd.DataFrame({'Sistema': ['Nacional'], 'ITE [$]': [suma_ite_nac]})

    # Leer ite_zonal
    df_ite_zonal= pd.read_excel(archivo_ite_zonal_dedicado, sheet_name='DEV_IT_VATT_Z', usecols='N:Q', skiprows=19)
    df_ite_zonal = df_ite_zonal[df_ite_zonal['Nombre Empresa'] == 'ENGIE']
    df_ite_zonal = df_ite_zonal.rename(columns={'Valorizado Total': 'ITE [$]'})
    valor_ite_zon = df_ite_zonal['ITE [$]'].iloc[0]
    resultado_ite_zonal = pd.DataFrame({'Sistema': ['Zonal'], 'ITE [$]': [valor_ite_zon]})

    # Leer ite_dedicado
    df_ite_dedicado= pd.read_excel(archivo_ite_zonal_dedicado, sheet_name='DEV_IT_VATT_DR', usecols='T:X', skiprows=12)
    df_ite_dedicado = df_ite_dedicado[df_ite_dedicado['Nombre Balance'] == 'ENGIE']
    df_ite_dedicado = df_ite_dedicado.rename(columns={'Valorizado': 'ITE [$]'})
    valor_ite_ded = df_ite_dedicado['ITE [$]'].iloc[0]
    resultado_ite_dedicado = pd.DataFrame({'Sistema': ['Dedicado'], 'ITE [$]': [valor_ite_ded]})

    resultado_ite_concatenado = pd.concat([resultado_ite_nacional, resultado_ite_zonal, resultado_ite_dedicado],
                                          ignore_index=True)

    return resultado_ite_concatenado


def ite_final(fecha):
    df_ite_def_resultado = ite_def(fecha).rename(columns={'ITE [$]': 'ITE [$] Informado'})
    df_ite_coord_resultado = ite_coord(cu_coordinador(fecha)).rename(columns={'ITE [$]': 'ITE [$] Inf_Pre CU'})
    df_ite_final = pd.merge(df_ite_def_resultado, df_ite_coord_resultado, on='Sistema', how='left')
    df_ite_final['Diferencia ITE'] = df_ite_final['ITE [$] Informado'] - df_ite_final['ITE [$] Inf_Pre CU']
    df_ite_final['Diferencia %'] = (df_ite_final['Diferencia ITE'] / df_ite_final['ITE [$] Informado']) * 100
    df_ite_final['Diferencia ITE'] = df_ite_final['Diferencia ITE'].apply(lambda x: "${:,.2f}".format(x))
    df_ite_final['Diferencia %'] = df_ite_final['Diferencia %'].apply(lambda x: "{:.2f}%".format(x))

    return df_ite_final


def itp_coord(df):
    df_zonal_dedicado = df[df['Sistema'].isin(['Zonal', 'Dedicado'])][['Sistema', 'ITP [$]']]
    df_nacional = df[df['Sistema'].isin(['25T', 'CU'])][['Sistema', 'ITP [$]']]
    suma_nacional = df_nacional['ITP [$]'].sum()
    suma_nacional_df = pd.DataFrame({'Sistema': ['Nacional'], 'ITP [$]': [suma_nacional]})
    df_final_itp = pd.concat([df_zonal_dedicado, suma_nacional_df], ignore_index=True)
    df_final_itp = df_final_itp.sort_values(by='ITP [$]', ascending=False)

    return df_final_itp


def itp_def(fecha):
    archivo_itp_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Anexo 02.b Cuadros de Pago_Potencia_SEN_Ene24_def.xlsb"
    archivo_itp_zonal_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\BPre Cuadro de Pago_ene24_def.xls"

    # Leer itp_Nacional
    df_itp_nacional = pd.read_excel(archivo_itp_nacional, sheet_name='02.IT POTENCIA Ene-24 def', usecols='B:DH', skiprows=6)
    df_itp_nacional = df_itp_nacional[df_itp_nacional['USUARIOS'] != 'Total']
    df_itp_nacional = df_itp_nacional.rename(columns={'EDELNOR_TRANSMISION': 'ITP [$]'})
    suma_ite_nac = df_itp_nacional['ITP [$]'].sum()
    resultado_itp_nacional = pd.DataFrame({'Sistema': ['Nacional'], 'ITP [$]': [suma_ite_nac]})

    # Leer itp_zonal
    df_itp_zonal = pd.read_excel(archivo_itp_zonal_dedicado, sheet_name='02. DEVOLUCIÓN IT Ene-24', usecols='L:P', skiprows=5)
    df_itp_zonal = df_itp_zonal[df_itp_zonal['Transmisor Zonal Final'] == 'ENGIE']
    df_itp_zonal = df_itp_zonal.rename(columns={'Monetario [$]': 'ITP [$]'})
    valor_itp_zon = df_itp_zonal['ITP [$]'].iloc[0]
    resultado_itp_zonal = pd.DataFrame({'Sistema': ['Zonal'], 'ITP [$]': [valor_itp_zon]})

    # Leer itp_dedicado
    df_itp_dedicado = pd.read_excel(archivo_itp_zonal_dedicado, sheet_name='02. DEVOLUCIÓN IT Ene-24', usecols='AK:AP', skiprows=5)
    df_itp_dedicado = df_itp_dedicado[df_itp_dedicado['Transmisor Dedicado'] == 'ENGIE']
    df_itp_dedicado = df_itp_dedicado.rename(columns={'Monetario ($).1': 'ITP [$]'})
    valor_itp_ded = df_itp_dedicado['ITP [$]'].iloc[0]
    resultado_itp_dedicado = pd.DataFrame({'Sistema': ['Dedicado'], 'ITP [$]': [valor_itp_ded]})

    resultado_itp_concatenado = pd.concat([resultado_itp_nacional, resultado_itp_zonal, resultado_itp_dedicado],
                                          ignore_index=True)

    return resultado_itp_concatenado


def itp_final(fecha):
    df_itp_def_resultado = itp_def(fecha).rename(columns={'ITP [$]': 'ITP [$] Informado'})
    df_itp_coord_resultado = itp_coord(cu_coordinador(fecha)).rename(columns={'ITP [$]': 'ITP [$] Inf_Pre CU'})
    df_itp_final = pd.merge(df_itp_def_resultado, df_itp_coord_resultado, on='Sistema', how='left')
    df_itp_final['Diferencia ITP'] = df_itp_final['ITP [$] Informado'] - df_itp_final['ITP [$] Inf_Pre CU']
    df_itp_final['Diferencia %'] = (df_itp_final['Diferencia ITP'] / df_itp_final['ITP [$] Informado']) * 100
    df_itp_final['Diferencia ITP'] = df_itp_final['Diferencia ITP'].apply(lambda x: "${:,.2f}".format(x))
    df_itp_final['Diferencia %'] = df_itp_final['Diferencia %'].apply(lambda x: "{:.2f}%".format(x))

    return df_itp_final


# ---------------------------------------------------------------------------------------------------------------------
def vatt_final(fecha):
    df_itd_preparado = itd()
    df_vatt = vatt(df_itd_preparado, fecha)
    df_itd_amp = itd_amp()
    df_vatt_amp = calcular_vatt_por_tramo(df_itd_amp, fecha)
    df_agg_vatt = vatt_calc(df_vatt, df_vatt_amp)

    df_inicial = cu_coordinador(fecha)
    df_final_vatt = vatt_coord(df_inicial)

    df_merged = pd.merge(df_agg_vatt, df_final_vatt, on='Sistema', how='left')
    df_merged.rename(columns={'VATT CLP': 'VATT Calculado', 'VATT [$]': 'VATT Preliminar'}, inplace=True)
    df_merged['Diferencia VATT'] = df_merged['VATT Preliminar'] - df_merged['VATT Calculado']
    df_merged['Diferencia VATT/12'] = df_merged['Diferencia VATT'] / 12
    df_merged['Diferencia %'] = (df_merged['Diferencia VATT'] / df_merged['VATT Preliminar']) * 100
    df_merged['Diferencia VATT'] = df_merged['Diferencia VATT'].apply(lambda x: f"${x:,.0f}")
    df_merged['Diferencia VATT/12'] = df_merged['Diferencia VATT/12'].apply(lambda x: f"${x:,.0f}")
    df_merged['Diferencia %'] = df_merged['Diferencia %'].apply(lambda x: f"{x:.2f}%")

    return df_merged


def peajes_def(fecha):
    inf_peaje_def = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Liquidación de Peajes 2401.xlsm"

    df = pd.read_excel(inf_peaje_def, sheet_name='Pago Total', usecols='C:AN', skiprows=11)
    df = df[df['Empresa Generación'] != 'Total general']

    if 'ETSA' in df.columns:
        suma_etsa = df['ETSA'].sum()
    else:
        print("La columna 'ETSA' no se encuentra en el DataFrame.")
        suma_etsa = 0

    resultado_peajes_def = pd.DataFrame({
        'Fuente': ['Inf_Definitivo'],
        'VATT Peajes': [suma_etsa]
    })
    return resultado_peajes_def


def cu_peajes(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')
    ruta_archivo_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"


    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)

    df_25t_filtrado = df_25t[df_25t['PROPIETARIO'] == 'ETSA'].copy()
    df_25t_filtrado['MES'] = pd.to_datetime(df_25t_filtrado['MES'])
    df_25t_filtrado = df_25t_filtrado[df_25t_filtrado['MES'] == fecha_filtrado]

    df_25t_filtrado['Fuente'] = 'Inf_Preliminar CU'

    df_cu_peajes = df_25t_filtrado[['Fuente', 'VATT Recibido por Liquidación de Peajes [$]']].rename(
        columns={'VATT Recibido por Liquidación de Peajes [$]': 'VATT Peajes [$]'}).reset_index(drop=True)
    df_cu_peajes['VATT Peajes'] = df_cu_peajes.pop('VATT Peajes [$]')

    return df_cu_peajes


def obtener_resultados_concatenados(fecha):
    pd.set_option('display.float_format', '{:.2e}'.format)

    df_peajes_def = peajes_def(fecha)
    df_cu_peajes = cu_peajes(fecha)
    resultado_final = pd.concat([df_peajes_def, df_cu_peajes], ignore_index=True)
    resultado_final = resultado_final.T
    resultado_final.columns = resultado_final.iloc[0]
    resultado_final = resultado_final.iloc[1:]
    resultado_final.reset_index(drop=True, inplace=True)

    resultado_final['Diferencia'] = resultado_final['Inf_Definitivo'].astype(float) - resultado_final['Inf_Preliminar CU'].astype(float)
    resultado_final['Diferencia %'] = (resultado_final['Diferencia'] / resultado_final['Inf_Definitivo'].astype(float)) * 100

    resultado_final['Diferencia'] = resultado_final['Diferencia'].apply(lambda x: "${:,.2f}".format(x))
    resultado_final['Diferencia %'] = resultado_final['Diferencia %'].apply(lambda x: "{:.2f}%".format(x))

    return resultado_final


# ----------------------------------------------------------------------------------------------------------------------
def saldo_mensual(fecha):
    df_itd_preparado = itd()
    df_vatt = vatt(df_itd_preparado, fecha)
    df_itd_amp = itd_amp()
    df_vatt_amp = calcular_vatt_por_tramo(df_itd_amp, fecha)
    df_agg_vatt = vatt_calc(df_vatt, df_vatt_amp)

    df_inicial = cu_coordinador(fecha)
    df_final_vatt = vatt_coord(df_inicial)

    df_merged_vatt = pd.merge(df_agg_vatt, df_final_vatt, on='Sistema', how='left')
    df_merged_vatt.rename(columns={'VATT CLP': 'VATT Calculado'}, inplace=True)
    df_merged_vatt['VATT/12[$]'] = df_merged_vatt['VATT Calculado'] / 12

    df_ite_final = ite_final(fecha)[['Sistema', 'ITE [$] Informado']]
    df_itp_final = itp_final(fecha)[['Sistema', 'ITP [$] Informado']]

    df_ite_final.rename(columns={'ITE [$] Informado': 'ITE [$]'}, inplace=True)
    df_itp_final.rename(columns={'ITP [$] Informado': 'ITP [$]'}, inplace=True)

    df_merged = pd.merge(df_merged_vatt[['Sistema', 'VATT/12[$]']], df_ite_final, on='Sistema', how='left')
    df_merged_final = pd.merge(df_merged, df_itp_final, on='Sistema', how='left')

    df_peaje_valor = peajes_def(fecha)
    valor_peaje = df_peaje_valor['VATT Peajes'].iloc[0] if not df_peaje_valor.empty else 0

    df_merged_final['Peajes [$]'] = 0.0
    df_merged_final.loc[df_merged_final['Sistema'] == 'Nacional', 'Peajes [$]'] = valor_peaje
    df_merged_final = df_merged_final[['Sistema', 'VATT/12[$]', 'ITE [$]', 'ITP [$]', 'Peajes [$]']]

    return df_merged_final


def cu(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')
    ruta_archivo_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"
    ruta_archivo_zonal_y_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"

    # Procesar Nacional (Saldos 25T y Saldos CU)
    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)
    df_25t_filtrado = df_25t[df_25t['PROPIETARIO'] == 'ETSA'].copy()
    df_25t_filtrado['MES'] = pd.to_datetime(df_25t_filtrado['MES'])
    df_25t_filtrado = df_25t_filtrado[df_25t_filtrado['MES'] == fecha_filtrado]
    df_25t_filtrado['Sistema'] = 'Nacional'
    df_25t_filtrado['Ingreso Repartición CT [$]'] = df_25t_filtrado['Ingreso Repartición CT Exención [$]'] + df_25t_filtrado['Ingreso Repartición CT Pago Retiro[$]']
    df_25t_filtrado['Saldo Mensual [$]'] = df_25t_filtrado['Saldo Mensual  Excención [$]'] + df_25t_filtrado['Saldo Mensual  Pago Retiro [$]']
    df_nacional = df_25t_filtrado[['Sistema', 'Ingreso Repartición CT [$]', 'Saldo Mensual [$]']]

    df_cu = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos CU', usecols='B:S', skiprows=5)
    df_cu_filtrado = df_cu[df_cu['PROPIETARIO'] == 'ETSA'].copy()
    df_cu_filtrado['MES'] = pd.to_datetime(df_cu_filtrado['MES'])
    df_cu_filtrado = df_cu_filtrado[df_cu_filtrado['MES'] == fecha_filtrado]
    df_cu_filtrado['Sistema'] = 'Nacional'
    df_nacional_cu = df_cu_filtrado[['Sistema', 'Ingreso Repartición CT [$]', 'Saldo Mensual [$]']]

    # Sumar Nacional (25T + CU)
    df_nacional_total = pd.concat([df_nacional, df_nacional_cu], ignore_index=True)
    df_nacional_total = df_nacional_total.groupby('Sistema', as_index=False).sum()

    # Procesar Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Zonal', usecols='B:AA', skiprows=4)
    df_zonal_filtrado = df_zonal[df_zonal['PROPIETARIO'] == 'ENGIE'].copy()
    df_zonal_filtrado['MES'] = pd.to_datetime(df_zonal_filtrado['MES'])
    df_zonal_filtrado = df_zonal_filtrado[df_zonal_filtrado['MES'] == fecha_filtrado]
    df_zonal_filtrado['Sistema'] = 'Zonal'
    df_zonal_final = df_zonal_filtrado[['Sistema', 'Ingreso Repartición CT [$]', 'Saldo Mensual [$]']]

    # Procesar Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Dedicado', usecols='B:U', skiprows=5)
    df_dedicado_filtrado = df_dedicado[df_dedicado['PROPIETARIO'] == 'ENGIE'].copy()
    df_dedicado_filtrado['MES'] = pd.to_datetime(df_dedicado_filtrado['MES'])
    df_dedicado_filtrado = df_dedicado_filtrado[df_dedicado_filtrado['MES'] == fecha_filtrado]
    df_dedicado_filtrado['Sistema'] = 'Dedicado'
    df_dedicado_final = df_dedicado_filtrado[['Sistema', 'Ingreso Repartición CT [$]', 'Saldo Mensual [$]']]

    # Combinar resultados de Nacional, Zonal y Dedicado
    df_concatenado = pd.concat([df_nacional_total, df_zonal_final, df_dedicado_final], ignore_index=True)

    return df_concatenado


def saldos(fecha):
    df_cu_total = cu(fecha)
    df_saldo_mensual = saldo_mensual(fecha)

    df_cu_total = df_cu_total.rename(columns={
        'Ingreso Repartición CT [$]': 'Ingresos  [$]',
        'Saldo Mensual [$]': 'Saldo preliminar [$]'
    })

    df_merged = pd.merge(df_cu_total, df_saldo_mensual, on='Sistema', how='outer')

    column_order = ['Sistema', 'VATT/12[$]', 'ITE [$]', 'ITP [$]', 'Peajes [$]', 'Ingresos  [$]', 'Saldo preliminar [$]']
    df_merged_final = df_merged.reindex(columns=column_order)

    df_merged_final['Saldo Calculado [$]'] = (df_merged_final['ITE [$]'] + df_merged_final['ITP [$]'] +
                                              df_merged_final['Peajes [$]'] + df_merged_final['Ingresos  [$]'] -
                                              df_merged_final['VATT/12[$]'])

    df_merged_final.fillna(0, inplace=True)

    # Calcular 'Diferencia Saldo' y 'Diferencia %'
    df_merged_final['Diferencia Saldo'] = df_merged_final['Saldo preliminar [$]'] - df_merged_final['Saldo Calculado [$]']
    df_merged_final['Diferencia %'] = (df_merged_final['Diferencia Saldo'] / df_merged_final['Saldo preliminar [$]'].replace({0: np.nan})) * 100

    # Formatear 'Diferencia Saldo' en formato moneda
    df_merged_final['Diferencia Saldo'] = df_merged_final['Diferencia Saldo'].apply(lambda x: "${:,.2f}".format(x))

    # Formatear 'Diferencia %' en formato porcentual con dos decimales
    df_merged_final['Diferencia %'] = df_merged_final['Diferencia %'].apply(lambda x: "{:.2f}%".format(x) if not pd.isnull(x) else x)

    column_order_final = ['Sistema', 'VATT/12[$]', 'ITE [$]', 'ITP [$]', 'Peajes [$]', 'Ingresos  [$]',
                          'Saldo Calculado [$]', 'Saldo preliminar [$]', 'Diferencia Saldo', 'Diferencia %']
    df_merged_final = df_merged_final[column_order_final]

    return df_merged_final


def saldo_anterior(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d') - pd.offsets.MonthBegin(1)

    ruta_archivo_zonal_y_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"
    ruta_archivo_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

    # Procesamiento para Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Zonal', skiprows=4)
    df_zonal['MES'] = pd.to_datetime(df_zonal['MES'])
    df_zonal_filtrado = df_zonal[(df_zonal['PROPIETARIO'] == 'ENGIE') & (df_zonal['MES'] == fecha_filtrado)]
    df_zonal_filtrado = df_zonal_filtrado.assign(Sistema='Zonal', **{'Ac. Mes Anterior [$]': df_zonal_filtrado['Saldo Acumulado sin Reasignación [$]']})

    # Procesamiento para Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Dedicado', skiprows=5)
    df_dedicado['MES'] = pd.to_datetime(df_dedicado['MES'])
    df_dedicado_filtrado = df_dedicado[(df_dedicado['PROPIETARIO'] == 'ENGIE') & (df_dedicado['MES'] == fecha_filtrado)]
    df_dedicado_filtrado = df_dedicado_filtrado.assign(Sistema='Dedicado', **{'Ac. Mes Anterior [$]': df_dedicado_filtrado['Saldo Acumulado [$]']})

    # Procesamiento para Nacional (Saldos 25T)
    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)
    df_25t['MES'] = pd.to_datetime(df_25t['MES'])
    df_25t_filtrado = df_25t[(df_25t['PROPIETARIO'] == 'ETSA') & (df_25t['MES'] == fecha_filtrado)]
    df_25t_filtrado = df_25t_filtrado.assign(Sistema='Nacional', **{'Ac. Mes Anterior [$]': df_25t_filtrado['Saldo Acumulado Exención [$]'] + df_25t_filtrado['Saldo Acumulado Pago Retiro [$]']})

    # Procesamiento para Nacional (Saldos CU)
    df_cu = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos CU', usecols='B:S', skiprows=5)
    df_cu['MES'] = pd.to_datetime(df_cu['MES'])
    df_cu_filtrado = df_cu[(df_cu['PROPIETARIO'] == 'ETSA') & (df_cu['MES'] == fecha_filtrado)]
    df_cu_filtrado = df_cu_filtrado.assign(Sistema='Nacional', **{'Ac. Mes Anterior [$]': df_cu_filtrado['Saldo Acumulado sin Reasingación [$]']})

    # Combinar los DataFrames filtrados de Zonal, Dedicado y Nacional
    df_concatenado = pd.concat([df_zonal_filtrado[['Sistema', 'Ac. Mes Anterior [$]']], df_dedicado_filtrado[['Sistema', 'Ac. Mes Anterior [$]']], df_25t_filtrado[['Sistema', 'Ac. Mes Anterior [$]']], df_cu_filtrado[['Sistema', 'Ac. Mes Anterior [$]']]], ignore_index=True)

    # Sumar 'Ac. Mes Anterior [$]' por 'Sistema'
    df_sumado = df_concatenado.groupby('Sistema', as_index=False)['Ac. Mes Anterior [$]'].sum()

    return df_sumado


def saldo_actual(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')

    ruta_archivo_zonal_y_dedicado = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"
    ruta_archivo_nacional = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

    # Procesamiento para Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Zonal', skiprows=4)
    df_zonal['MES'] = pd.to_datetime(df_zonal['MES'])
    df_zonal_filtrado = df_zonal[(df_zonal['PROPIETARIO'] == 'ENGIE') & (df_zonal['MES'] == fecha_filtrado)]
    df_zonal_filtrado = df_zonal_filtrado.assign(Sistema='Zonal', **{'Ac. Actual [$]': df_zonal_filtrado['Saldo Acumulado sin Reasignación [$]']})

    # Procesamiento para Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Dedicado', skiprows=5)
    df_dedicado['MES'] = pd.to_datetime(df_dedicado['MES'])
    df_dedicado_filtrado = df_dedicado[(df_dedicado['PROPIETARIO'] == 'ENGIE') & (df_dedicado['MES'] == fecha_filtrado)]
    df_dedicado_filtrado = df_dedicado_filtrado.assign(Sistema='Dedicado', **{'Ac. Actual [$]': df_dedicado_filtrado['Saldo Acumulado [$]']})

    # Procesamiento para Nacional (Saldos 25T)
    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)
    df_25t['MES'] = pd.to_datetime(df_25t['MES'])
    df_25t_filtrado = df_25t[(df_25t['PROPIETARIO'] == 'ETSA') & (df_25t['MES'] == fecha_filtrado)]
    df_25t_filtrado = df_25t_filtrado.assign(Sistema='Nacional', **{'Ac. Actual [$]': df_25t_filtrado['Saldo Acumulado Exención [$]'] + df_25t_filtrado['Saldo Acumulado Pago Retiro [$]']})

    # Procesamiento para Nacional (Saldos CU)
    df_cu = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos CU', usecols='B:S', skiprows=5)
    df_cu['MES'] = pd.to_datetime(df_cu['MES'])
    df_cu_filtrado = df_cu[(df_cu['PROPIETARIO'] == 'ETSA') & (df_cu['MES'] == fecha_filtrado)]
    df_cu_filtrado = df_cu_filtrado.assign(Sistema='Nacional', **{'Ac. Actual [$]': df_cu_filtrado['Saldo Acumulado sin Reasingación [$]']})

    # Combinar los DataFrames filtrados de Zonal, Dedicado y Nacional
    df_concatenado = pd.concat([df_zonal_filtrado[['Sistema', 'Ac. Actual [$]']], df_dedicado_filtrado[['Sistema', 'Ac. Actual [$]']], df_25t_filtrado[['Sistema', 'Ac. Actual [$]']], df_cu_filtrado[['Sistema', 'Ac. Actual [$]']]], ignore_index=True)
    df_sumado = df_concatenado.groupby('Sistema', as_index=False)['Ac. Actual [$]'].sum()

    return df_sumado


def acumulados(fecha):
    df_saldo_actual = saldo_actual(fecha)
    df_saldo_anterior = saldo_anterior(fecha)
    df_acumulados = pd.merge(df_saldo_actual, df_saldo_anterior, on='Sistema', how='outer',
                             suffixes=(' Ac. Actual [$]', ' Ac. Mes Anterior [$]'))
    df_saldos = saldos(fecha)
    df_acumulados_final = pd.merge(df_acumulados, df_saldos[['Sistema', 'Saldo preliminar [$]']], on='Sistema',
                                   how='left')
    df_acumulados_final.fillna(0, inplace=True)
    df_acumulados_final['verificacion'] = df_acumulados_final['Ac. Mes Anterior [$]'] + df_acumulados_final[
        'Saldo preliminar [$]']

    df_acumulados_final['Diferencia'] = df_acumulados_final['Ac. Actual [$]'] - df_acumulados_final['verificacion']
    df_acumulados_final['Diferencia'] = df_acumulados_final['Diferencia'].apply(lambda x: "${:,.2f}".format(x))

    df_acumulados_final['Diferencia %'] = (df_acumulados_final['Ac. Actual [$]'] - df_acumulados_final[
        'verificacion']) / df_acumulados_final['Ac. Actual [$]'].replace({0: np.nan}) * 100

    df_acumulados_final['Diferencia %'] = df_acumulados_final['Diferencia %'].apply(
        lambda x: "{:.2f}%".format(x) if not pd.isnull(x) else "0.00%")

    return df_acumulados_final


# ----------------------------------------------------------------------------------------------------------------------
fecha_entrada = "202401"
resultado = k_index(fecha_entrada)
D_k, CPI_k, IPC_k, D, CPI, IPC = resultado
fecha_formato_completo = f"{fecha_entrada}01"
fecha_datetime = pd.to_datetime(fecha_formato_completo, format='%Y%m%d')
fecha_tres_meses_antes = fecha_datetime - pd.DateOffset(months=2)
año_tres_meses_antes = fecha_tres_meses_antes.year
mes_tres_meses_antes = fecha_tres_meses_antes.month
fecha_tres_meses_antes_yyyymm = f"{año_tres_meses_antes}{mes_tres_meses_antes:02d}"

datos = {
    "Índice": ["Dólar", "CPI", "IPC"],
    f"{fecha_entrada}": [D_k, CPI_k, IPC_k],
    f"{fecha_tres_meses_antes_yyyymm}": [D, CPI, IPC]
}

df_resultados = pd.DataFrame(datos)

# Impresión de los resultados finales y tabulados
print("\nIndices económicos:")
print(df_resultados.to_string(index=False))

# Procesamiento y cálculo de VATT
df_itd = itd()
df_itd_amp = itd_amp()
df_vatt_resultado = vatt(df_itd, fecha_entrada)
df_vatt_amp = calcular_vatt_por_tramo(df_itd_amp, fecha_entrada)
resultado_final = vatt_final(fecha_entrada)


# Paso 1
print("\nPaso 1, Comparación VATT Calculado con Informe Preliminar CU:")
print(resultado_final.to_string(index=False))

# Paso 2
resultado_concatenado = obtener_resultados_concatenados(fecha_entrada)
print("\nPaso 2, Comparación de Peajes: Informe Definitivo vs Informe Preliminar CU:")
print(resultado_concatenado)

# Paso 3.a
print("\nPaso 3, Compara Ingresos Tarifarios de Energia y Potencia con Informe Preliminar CU:")
print("Resultado ITE: Informe IVT Definitivo vs Inf_Preliminar CU:")
resultado_ite_final = ite_final(fecha_entrada)
print(resultado_ite_final, "\n")

# Paso 3.b
print("Resultado ITP: Informe IVT Definitivo vs Preliminar CU:")
resultado_itp_final = itp_final(fecha_entrada)
print(resultado_itp_final)

# Paso 4
print("\nPaso 4, Compara Saldos:")
print(saldos(fecha_entrada), "\n")

print("\nPaso 5, Saldo Acumulado")
print(acumulados(fecha_entrada))


nombre_archivo = f"C:\\Users\\QV6522\\Workspace\\IngresosRegulados\\Proyectos\\informes\\cargosunicos\\vatt_calculado_{fecha_entrada}.xlsx"

with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
    df_resultados.to_excel(writer, sheet_name='Indices Macroeconomicos')
    df_vatt_resultado.to_excel(writer, sheet_name='VATT Calculado')
    df_vatt_amp.to_excel(writer, sheet_name='VATT Ampliaciones')
    resultado_final.to_excel(writer, sheet_name='VATT FINAL')

print(f"\nArchivo exportado exitosamente en: {nombre_archivo}")



