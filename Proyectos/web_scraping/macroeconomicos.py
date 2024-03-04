
def itd_vatt(ruta_itd, fecha):
    df_anexo1 = pd.read_excel(ruta_itd, sheet_name='TablaAnexo1', engine='openpyxl')
    df_anexo1_filtrado = df_anexo1.loc[df_anexo1['Empresa Propietaria'].isin(['E-CL'])]
    df_anexo1_filtrado = df_anexo1_filtrado.loc[~df_anexo1_filtrado['NombreTramo'].eq('Iquique 066->Pozo Almonte 066')]

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


def itd_agg(df_resultante):
    df_agregado = df_resultante.groupby('Sistema')['VATT CLP'].sum().reset_index()
    df_agregado = df_agregado.sort_values(by='VATT CLP', ascending=False)
    return df_agregado


def leer_datos_transmision_y_dedicado():
    ruta_archivo_zonal_y_dedicado = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Zonal y Dedicado D7T 2401-pre.xlsx"
    ruta_archivo_nacional = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

    # Leer Prorrata_Zonal
    df_zonal = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Zonal', usecols='B:AA', skiprows=4)
    df_zonal_filtrado = df_zonal[df_zonal['PROPIETARIO'] == 'ENGIE'].copy()
    df_zonal_filtrado.loc[:, 'MES'] = pd.to_datetime(df_zonal_filtrado['MES'])
    df_zonal_filtrado = df_zonal_filtrado[df_zonal_filtrado['MES'] == '2023-11-01']
    df_zonal_filtrado = df_zonal_filtrado.sort_values(by='MES', ascending=False)
    df_zonal_filtrado = df_zonal_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_zonal_filtrado['Sistema'] = 'Zonal'

    # Leer Prorrata_Dedicado
    df_dedicado = pd.read_excel(ruta_archivo_zonal_y_dedicado, sheet_name='Prorrata_Dedicado', usecols='B:U', skiprows=5)
    df_dedicado_filtrado = df_dedicado[df_dedicado['PROPIETARIO'] == 'ENGIE'].copy()
    df_dedicado_filtrado.loc[:, 'MES'] = pd.to_datetime(df_dedicado_filtrado['MES'])
    df_dedicado_filtrado = df_dedicado_filtrado[df_dedicado_filtrado['MES'] == '2023-11-01']
    df_dedicado_filtrado = df_dedicado_filtrado.sort_values(by='MES', ascending=False)
    df_dedicado_filtrado = df_dedicado_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_dedicado_filtrado['Sistema'] = 'Dedicado'

    # Leer Saldos 25T
    df_25t = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos 25T', usecols='B:AL', skiprows=4)
    df_25t_filtrado = df_25t[df_25t['PROPIETARIO'] == 'ETSA'].copy()
    df_25t_filtrado.loc[:, 'MES'] = pd.to_datetime(df_25t_filtrado['MES'])
    df_25t_filtrado = df_25t_filtrado[df_25t_filtrado['MES'] == '2023-11-01']
    df_25t_filtrado = df_25t_filtrado.sort_values(by='MES', ascending=False)
    df_25t_filtrado = df_25t_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_25t_filtrado['Sistema'] = '25T'

    # Leer Saldos CU
    df_cu = pd.read_excel(ruta_archivo_nacional, sheet_name='Saldos CU', usecols='B:S', skiprows=5)
    df_cu_filtrado = df_cu[df_cu['PROPIETARIO'] == 'ETSA'].copy()
    df_cu_filtrado.loc[:, 'MES'] = pd.to_datetime(df_cu_filtrado['MES'])
    df_cu_filtrado = df_cu_filtrado[df_cu_filtrado['MES'] == '2023-11-01']
    df_cu_filtrado = df_cu_filtrado.sort_values(by='MES', ascending=False)
    df_cu_filtrado = df_cu_filtrado[['VATT [$]', 'ITE [$]', 'ITP [$]']]
    df_cu_filtrado['Sistema'] = 'CU'

    # Concatenar todos los DataFrames filtrados
    df_concatenado = pd.concat([df_zonal_filtrado, df_dedicado_filtrado, df_25t_filtrado, df_cu_filtrado], ignore_index=True)
    cols = ['Sistema'] + [col for col in df_concatenado.columns if col != 'Sistema']
    df_concatenado = df_concatenado[cols]

    return df_concatenado


def agregar_datos_nacionales(df):
    df_zonal_dedicado = df[df['Sistema'].isin(['Zonal', 'Dedicado'])]
    df_nacional = df[df['Sistema'].isin(['25T', 'CU'])]
    suma_nacional = df_nacional[['VATT [$]', 'ITE [$]', 'ITP [$]']].sum().to_frame().T
    suma_nacional['Sistema'] = 'Nacional'
    suma_nacional = suma_nacional[df.columns.tolist()]
    df_final = pd.concat([df_zonal_dedicado, suma_nacional], ignore_index=True)
    df_final = df_final.sort_values(by='VATT [$]', ascending=False)

    return df_final


# --------------------------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------------------------

# -- Esta llamada trae los datos macro economicos desde el año de interes hasta hoy -- #

# año_de_interés = 2013
# df_indices_macroeconomicos = macroeconomicos(año_de_interés)
# print(df_indices_macroeconomicos)
# df_indices_macroeconomicos.to_excel(r"C:\Users\QV6522\Workspace\indices_macro.xlsx", index=False)

# --------------------------------------------------------------------------------------------------------------------------------------------------
ruta_itd = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Resultados_ITD_rec.xlsx"
fecha = '202401'

df_resultante = itd_vatt(ruta_itd, fecha)
print(df_resultante)
ruta_exportacion = r'C:\workspace\IngresosRegulados\Proyectos\informes\cargosunicos\resultados_itd_vatt.xlsx'
df_resultante.to_excel(ruta_exportacion, index=False, engine='openpyxl')
print(f"DataFrame exportado con éxito a {ruta_exportacion}")
# --------------------------------------------------------------------------------------------------------------------------------------------------


