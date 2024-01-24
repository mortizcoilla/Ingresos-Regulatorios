# visualizaciones
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.dates import DateFormatter
import os
from Peajes.utilidades.config import GRAFICO_PATH


def graficar_datos_preliminar(df_historico, estadisticas, df_preliminar):
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))

    df_historico['Periodo'] = pd.to_datetime(df_historico['Periodo'])

    sns.lineplot(ax=ax, data=df_historico, x='Periodo', y='PagoTotal', marker='o', color='blue', linewidth=1,
                 label='Pago Total')

    if not df_preliminar.empty:
        ax.scatter(df_preliminar['Periodo'], df_preliminar['PagoTotal'], color='red', marker='*', s=100,
                   label='Preliminar')

        ax.set_xticks(df_historico['Periodo'], [x.strftime('%b-%y') for x in df_historico['Periodo']], rotation=45)
        ax.set_xlabel('Periodo', fontsize=14)

    # Agregar líneas de estadísticas
    ax.axhline(estadisticas['PagoTotal']['máximo'], color='red', linestyle='--', label='Máximo')
    ax.axhline(estadisticas['PagoTotal']['minimo'], color='red', linestyle='--', label='Mínimo')
    ax.axhline(estadisticas['PagoTotal']['promedio'], color='green', linestyle='-', label='Promedio')

    # Formatear el eje x
    ax.xaxis.set_major_formatter(DateFormatter('%b-%y'))
    plt.xticks(df_historico['Periodo'], [x.strftime('%b-%y') for x in df_historico['Periodo']], rotation=45)

    # Personalizar título y etiquetas
    ax.set_title('Evolución del Pago Total (Últimos 12 Meses)', fontweight='bold', fontsize=16)
    ax.set_xlabel('Periodo', fontsize=14)
    ax.set_ylabel('PagoTotal (MM de CLP)', fontsize=14)

    # Ajustar leyenda y mostrar
    plt.legend(title='Referencias', title_fontsize='13', fontsize='12')
    plt.tight_layout()

    ruta_grafico = guardar_grafico_preliminar(fig, df_preliminar)

    return ruta_grafico


def guardar_grafico_preliminar(figura, df_preliminar):
    if not df_preliminar.empty and 'Periodo' in df_preliminar.columns:
        ultimo_periodo = pd.to_datetime(df_preliminar['Periodo'].iloc[-1]).strftime('%b-%y')
        nombre_archivo = f'Preliminar_{ultimo_periodo}.png'
        ruta_completa = os.path.join(GRAFICO_PATH, nombre_archivo)
        figura.savefig(ruta_completa)
        print(f'Gráfico guardado como: {ruta_completa}')
        return ruta_completa
    else:
        print('No se pudo guardar el gráfico: df_preliminar no tiene datos válidos.')
        return None


def graficar_datos_definitivo(df_historico, estadisticas):
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))

    df_historico['Periodo'] = pd.to_datetime(df_historico['Periodo'])

    # Creación del gráfico lineal para df_historico
    sns.lineplot(ax=ax, data=df_historico, x='Periodo', y='PagoTotal', marker='o', color='blue', linewidth=1, label='Pago Total')

    # Agregar líneas de estadísticas
    ax.axhline(estadisticas['PagoTotal']['máximo'], color='red', linestyle='--', label='Máximo')
    ax.axhline(estadisticas['PagoTotal']['minimo'], color='red', linestyle='--', label='Mínimo')
    ax.axhline(estadisticas['PagoTotal']['promedio'], color='green', linestyle='-', label='Promedio')

    # Formatear el eje x
    ax.xaxis.set_major_formatter(DateFormatter('%b-%y'))
    plt.xticks(df_historico['Periodo'], [x.strftime('%b-%y') for x in df_historico['Periodo']], rotation=45)

    # Personalizar título y etiquetas
    ax.set_title('Evolución del Pago Total (Últimos 12 Meses)', fontweight='bold', fontsize=16)
    ax.set_xlabel('Periodo', fontsize=14)
    ax.set_ylabel('PagoTotal (MM de CLP)', fontsize=14)

    # Ajustar leyenda y mostrar
    plt.legend(title='Referencias', title_fontsize='13', fontsize='12')
    plt.tight_layout()

    # Guardar el gráfico y obtener la ruta del archivo
    ruta_grafico = guardar_grafico_definitivo(fig, df_historico)

    return ruta_grafico


def guardar_grafico_definitivo(figura, df_historico):
    if not df_historico.empty and 'Periodo' in df_historico.columns:
        ultimo_periodo = pd.to_datetime(df_historico['Periodo'].iloc[-1]).strftime('%b-%y')
        nombre_archivo = f'Definitivo_{ultimo_periodo}.png'
        ruta_completa = os.path.join(GRAFICO_PATH, nombre_archivo)
        figura.savefig(ruta_completa)
        print(f'Gráfico guardado como: {ruta_completa}')
        return ruta_completa
    else:
        print('No se pudo guardar el gráfico: df_historico no tiene datos válidos.')
        return None
