import pandas as pd

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






hola = itp_def('202401')
print(hola)

"""
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
    """