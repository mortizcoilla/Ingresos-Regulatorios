import os

def listar_estructura_directorios(ruta, max_depth=2):
    root_depth = ruta.rstrip(os.sep).count(os.sep) - 1
    for root, dirs, files in os.walk(ruta):
        depth = root.count(os.sep) - root_depth
        if depth > max_depth:
            continue
        sangria = ' ' * 4 * depth
        print(f'{sangria}{os.path.basename(root)}/')
        sub_sangria = ' ' * 4 * (depth + 1)
        for f in files:
            print(f'{sub_sangria}{f}')

# Ruta del directorio del proyecto
ruta_proyecto = 'C:\\Users\\QV6522\\Documents\\InformesRecurrentes'

listar_estructura_directorios(ruta_proyecto)