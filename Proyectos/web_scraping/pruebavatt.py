import pandas as pd
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


# ----------------------------------------------------------------------------------------------------------------------
def vatt(df_itd, fecha):
    IPC_0 = 97.89
    CPI_0 = 246.663
    D_0 = 629.55
    Ta_0 = 0.06
    t_0 = 0.255
    Ta_k = 0.06
    t_k = 0.27

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


df_itd = itd()


# ----------------------------------------------------------------------------------------------------------------------
def itd_amp():
    ruta_itd = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\BBDD\Resultados_ITD_rec.xlsx"

    df_amp = pd.read_excel(ruta_itd, sheet_name='Ampliaciones', engine='openpyxl')

    df_index = pd.read_excel(ruta_itd, sheet_name='Indexacion', engine='openpyxl')
    df_itd_amp = pd.merge(df_amp, df_index, on=['Sistema', 'Zona', 'Tipo Tramo (*)'], how='left')

    return df_itd_amp


# ----------------------------------------------------------------------------------------------------------------------
def calcular_vatt_por_tramo(df_itd_amp, fecha):
    # Asumiendo que esta función devuelve correctamente los índices
    D_k, CPI_k, IPC_k, D, CPI, IPC = k_index(fecha)

    # Extraer el mes de la fecha de interés
    mes_fecha_interes = int(fecha[4:6])

    def aplicar_calculo(row):
        # Definir las categorías
        categoria_1 = ["Mejillones - Transformador 220/23 kV - 30 MVA (A)",
                       "Antofagasta - Seccionamiento Barra 110 kV (A)"]

        categoria_2 = ["Normalización Laberinto 220->El Cobre 220 (A)",
                       "Normalización el Cobre (A)",
                       "Ampliación y configuración Pozo Almonte (A)"]

        categoria_3 = ["Ampliación Nueva Crucero (A)"]

        categoria_4 = ["NUEVA SE EL ROSAL (A)",
                       "NUEVA SE CHUQUICAMATA (A)"]

        categoria_5 = ["NUEVA SE ALGARROBAL (A)"]

        # Calcular el indexador para cada categoría
        indexador_cat1 = row['alfa'] * (IPC / 84.7) * (500.81 / D) + row['beta'] * (CPI / 233.546)
        indexador_cat2 = row['alfa'] * (IPC / 95.93) * (668.63 / D) + row['beta'] * (CPI / 241.43)
        indexador_cat3 = row['alfa'] * (IPC / 94.47) * (682.07 / D) + row['beta'] * (CPI / 238.13)

        if mes_fecha_interes == 5:
            indexador_cat4 = (CPI / 249.554)
        else:
            indexador_cat4 = 1

        if mes_fecha_interes == 3:
            indexador_cat5 = (CPI / 249.554)
        else:
            indexador_cat5 = 0

        # Calcular AVI y COMA indexado
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


        # Calcular VATT en USD y en CLP usando el índice D_k
        vatt_usd = avi_usd + coma_usd
        avi_clp = avi_usd * D_k
        coma_clp = coma_usd * D_k
        vatt_clp = avi_clp + coma_clp

        # Retorna los valores calculados
        return pd.Series([avi_usd, coma_usd, vatt_usd, avi_clp, coma_clp, vatt_clp],
                         index=['AVI USD', 'COMA USD', 'VATT USD', 'AVI CLP', 'COMA CLP', 'VATT CLP'])

    # Aplicar los cálculos a cada fila del DataFrame
    calculated_columns = df_itd_amp.apply(aplicar_calculo, axis=1)
    df_resultado = df_itd_amp.join(calculated_columns)

    return df_resultado


# ----------------------------------------------------------------------------------------------------------------------
df_itd_amp = itd_amp()
fecha_interes = "202401"
df_vatt_calculado = calcular_vatt_por_tramo(df_itd_amp, fecha_interes)
ruta_salida_excel = r"C:\Users\QV6522\workspace\IngresosRegulados\Proyectos\informes\cargosunicos\Ampliaciones.xlsx"
df_vatt_calculado.to_excel(ruta_salida_excel, index=False, engine='openpyxl')
print(f"Archivo '{ruta_salida_excel}' creado exitosamente.")