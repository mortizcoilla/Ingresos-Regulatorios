import pandas as pd
import warnings
warnings.filterwarnings("ignore", message="Slicer List extension is not supported and will be removed")



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


# ----------------------------------------------------------------------------------------------------------------------
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

    # Agregar las variables como campos en el DataFrame
    df_vatt['D_k'] = D_k
    df_vatt['CPI_k'] = CPI_k
    df_vatt['IPC_k'] = IPC_k
    df_vatt['D'] = D
    df_vatt['CPI'] = CPI
    df_vatt['IPC'] = IPC

    # Agregar valores base como campos en el DataFrame
    df_vatt['IPC_0'] = IPC_0
    df_vatt['CPI_0'] = CPI_0
    df_vatt['D_0'] = D_0
    df_vatt['Ta_0'] = Ta_0
    df_vatt['t_0'] = t_0
    df_vatt['Ta_k'] = Ta_k
    df_vatt['t_k'] = t_k

    # Retornar el DataFrame con VATT calculado
    return df_vatt


def vatt_calc(df_vatt):
    df_vatt_agg = df_vatt.groupby('Sistema', as_index=False)['VATT CLP'].sum()

    return df_vatt_agg


# ----------------------------------------------------------------------------------------------------------------------
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
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')
    archivo_ite_nacional = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Anexo 02.a Cuadros de Pago_Balances_SEN_Ene24_def.xlsb"
    archivo_ite_zonal_dedicado = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Balance_2401_BD01.xlsm"

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
    df_ite_coord_resultado = ite_coord(cu_coordinador(fecha)).rename(columns={'ITE [$]': 'ITE [$] Inf_Preliminar CU'})
    df_ite_final = pd.merge(df_ite_def_resultado, df_ite_coord_resultado, on='Sistema', how='left')

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
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')
    archivo_itp_nacional = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Anexo 02.b Cuadros de Pago_Potencia_SEN_Ene24_def.xlsb"
    archivo_itp_zonal_dedicado = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\BPre Cuadro de Pago_ene24_def.xls"

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
    df_itp_coord_resultado = itp_coord(cu_coordinador(fecha)).rename(columns={'ITP [$]': 'ITP [$] Inf_Preliminar CU'})
    df_itp_final = pd.merge(df_itp_def_resultado, df_itp_coord_resultado, on='Sistema', how='left')

    return df_itp_final


# ---------------------------------------------------------------------------------------------------------------------
def vatt_final(fecha):
    df_itd_preparado = itd()
    df_vatt = vatt(df_itd_preparado, fecha)
    df_vatt_agg = vatt_calc(df_vatt)

    df_inicial = cu_coordinador(fecha)
    df_final_vatt = vatt_coord(df_inicial)

    df_merged = pd.merge(df_vatt_agg, df_final_vatt, on='Sistema', how='left')
    df_merged.rename(columns={'VATT CLP': 'VATT Calculado', 'VATT [$]': 'VATT Preliminar'}, inplace=True)
    return df_merged


def peajes_def(fecha):
    fecha_filtrado = pd.to_datetime(fecha + "01", format='%Y%m%d')
    inf_peaje_def = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Liquidación de Peajes 2401.xlsm"

    # Lee los datos del archivo Excel
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
    ruta_archivo_nacional = r"C:\workspace\IngresosRegulados\Proyectos\BBDD\Saldos Transmisión Nacional D7T 2401-pre.xlsx"

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
    df_peajes_def = peajes_def(fecha)
    df_cu_peajes = cu_peajes(fecha)

    resultado_final = pd.concat([df_peajes_def, df_cu_peajes], ignore_index=True)

    return resultado_final


# ---------------------------------------------------------------------------------------------------------------------
fecha_entrada = "202401"

# Obtención de los índices necesarios mediante k_index
resultado = k_index(fecha_entrada)
D_k, CPI_k, IPC_k, D, CPI, IPC = resultado

# Cálculo de la fecha tres meses antes
fecha_formato_completo = f"{fecha_entrada}01"
fecha_datetime = pd.to_datetime(fecha_formato_completo, format='%Y%m%d')
fecha_tres_meses_antes = fecha_datetime - pd.DateOffset(months=3)
año_tres_meses_antes = fecha_tres_meses_antes.year
mes_tres_meses_antes = fecha_tres_meses_antes.month
fecha_tres_meses_antes_yyyymm = f"{año_tres_meses_antes}{mes_tres_meses_antes:02d}"

# Crear un DataFrame para mostrar los resultados tabulados
datos = {
    "Índice": ["Dólar", "CPI", "IPC"],
    f"{fecha_entrada}": [D_k, CPI_k, IPC_k],
    f"{fecha_tres_meses_antes_yyyymm}": [D, CPI, IPC]
}

df_resultados = pd.DataFrame(datos)

# Impresión de los resultados finales y tabulados
print("\nResultados tabulados de índices económicos:")
print(df_resultados.to_string(index=False))

# Procesamiento y cálculo de VATT
df_itd = itd()
df_vatt_resultado = vatt(df_itd, fecha_entrada)

# Cálculo del resultado final de VATT
resultado_final = vatt_final(fecha_entrada)

# Guardado de los DataFrames "VATT Calculado" y "VATT FINAL" en diferentes hojas del mismo archivo Excel
nombre_archivo = f"C:\\workspace\\IngresosRegulados\\Proyectos\\informes\\cargosunicos\\vatt_calculado_{fecha_entrada}.xlsx"

with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
    df_vatt_resultado.to_excel(writer, sheet_name='VATT Calculado')
    resultado_final.to_excel(writer, sheet_name='VATT FINAL')
    df_resultados.to_excel(writer, sheet_name='Indices')

# Asumiendo que la función `vatt_final` devuelve un DataFrame, imprimir el "Resultado Final"
print("\nPaso 1, Comparación VATT Calculado con Informe Preliminar CU:")
print(resultado_final.to_string(index=False))

resultado_concatenado = obtener_resultados_concatenados(fecha_entrada)
print("\nPaso 2, Comparación de Peajes: Informe Definitivo vs Informe Preliminar CU:")
print(resultado_concatenado)

print("\nPaso 3, Compara Ingresos Tarifarios de Energia y Potencia con Informe Preliminar CU:")

print("Resultado ITE: Informe IVT Definitivo vs Inf_Preliminar CU:")
resultado_ite_final = ite_final(fecha_entrada)
print(resultado_ite_final, "\n")
print("Resultado ITP: Informe IVT Definitivo vs Preliminar CU:")
resultado_itp_final = itp_final(fecha_entrada)
print(resultado_itp_final, "\n")

print("\nPaso 4, Ingresos mensuales por Cargos Unicos y Reasignación CU:")
print("\nPaso 5, La gran verificacion que aun no cacho ;(")


# Mensaje de éxito de exportación al archivo
print(f"\nArchivo exportado exitosamente en: {nombre_archivo}")



