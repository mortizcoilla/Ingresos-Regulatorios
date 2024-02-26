from pandas import DataFrame
from pandas_profiling import ProfileReport

# Crear un DataFrame simple
data = {
  "Nombre": ["Ana", "Luis", "Carlos", "Teresa"],
  "Edad": [32, 45, 23, 36],
  "Ciudad": ["Madrid", "Barcelona", "Madrid", "Valencia"],
  "Ingresos": [3000, 4000, 3500, 2800],
  "FechaNacimiento": pd.to_datetime(["1990-01-01", "1977-05-12", "1999-11-20", "1986-03-08"])
}

df = DataFrame(data)

# Generar un reporte de Pandas Profiling con configuración personalizada
profile = ProfileReport(df, title="Reporte de Pandas Profiling", 
                        minimal=True, 
                        interactions=True, 
                        sort=False)

# Guardar el reporte como un archivo HTML
profile.to_file("reporte_evaluacion.html")

# Mostrar un resumen del reporte en la consola
print(profile.to_html())
