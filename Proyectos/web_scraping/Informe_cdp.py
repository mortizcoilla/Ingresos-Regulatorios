
import plotly.graph_objects as go
from plotly.offline import plot

fig = go.Figure(data=[go.Bar(x=['A', 'B', 'C'],
                             y=[10, 20, 30],
                             marker_color='#01ACFB')])

grafico_div = plot(fig, output_type='div', include_plotlyjs=True)

titulo = "Transferencias económicas entre empresas"
subtitulo = "Cadena de pago – Incumplimientos de pago no acordado"

pie_de_pagina = """
<div class="pie-de-pagina">
    <p>&copy; 2024 Engie. Gerencia de Negocios de Transmisión.</p>
    <p>Información adicional, contactos, enlaces a redes sociales, etc.</p>
</div>
"""

html_contenido = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{titulo}</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            margin-left: 5%;
            margin-right: 5%;
            background-color: #F5F5F5;
            color: #034E7B;
        }}
        h1 {{
            color: #034E7B; /* Azul Oscuro para el título principal */
            margin-bottom: 0;
        }}
        h2 {{
            color: #647A8E; /* Gris Azulado para el subtítulo */
            margin-top: 5px;
        }}
        .plotly-graph-div {{
            margin-top: 20px;
        }}
        .pie-de-pagina {{
            margin-top: 50px;
            text-align: center;
            color: #A8B07A; /* Verde Oliva Suave para el texto del pie de página */
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>{titulo}</h1>
    <h2>{subtitulo}</h2>
    {grafico_div} <!-- Aquí se incrusta el gráfico de Plotly -->
    {pie_de_pagina} <!-- Aquí se agrega el pie de página -->
</body>
</html>
"""

nombre_archivo = r"C:\Users\QV6522\Workspace\IngresosRegulados\Proyectos\informes\cadenadepagos\informe_cdp.html"

with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
    archivo.write(html_contenido)

print(f"El informe con gráfico dinámico ha sido guardado como {nombre_archivo}.")
