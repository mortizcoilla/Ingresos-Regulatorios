# estadisticas.py
import pandas as pd


def calcular_estadisticas(df_historico):
    estadisticas = {}
    for columna in df_historico.columns:
        if pd.api.types.is_numeric_dtype(df_historico[columna]):
            estadisticas[columna] = {
                'promedio': round(df_historico[columna].mean(), 1),
                'desvest': round(df_historico[columna].std(), 1),
                'máximo': df_historico[columna].max(),
                'minimo': df_historico[columna].min()
            }
    return estadisticas
