import json
import multiprocessing
from datetime import datetime

# Cargar datos desde un archivo JSON
def cargar_datos(archivo):
    with open(archivo, 'r') as f:
        return json.load(f)

# Función para verificar solapamientos y devolver combinaciones válidas
def verificar_solapamientos_detalles(combinacion, datos_horarios):
    formato_hora = "%H:%M:%S"
    horarios_por_dia = {}

    for seccion in combinacion:
        if seccion in datos_horarios:
            dias = datos_horarios[seccion]["dias"]
            horarios = datos_horarios[seccion]["horario"]
            for dia, horario in zip(dias, horarios):
                if dia not in horarios_por_dia:
                    horarios_por_dia[dia] = []
                inicio, fin = horario.split(' - ')
                inicio = datetime.strptime(inicio.strip(), formato_hora)
                fin = datetime.strptime(fin.strip(), formato_hora)
                horarios_por_dia[dia].append((inicio, fin))

    for dia, horarios in horarios_por_dia.items():
        horarios.sort()  # Ordenar por hora de inicio
        for i in range(len(horarios) - 1):
            _, fin_anterior = horarios[i]
            inicio_siguiente, _ = horarios[i + 1]
            if inicio_siguiente < fin_anterior:
                return False  # Hay un solapamiento
    return True

def filtrar_combinaciones(combinaciones, datos_horarios):
    combinaciones_validas = []
    for sub_combinacion in combinaciones:
        for combinacion in sub_combinacion:
            if verificar_solapamientos_detalles(combinacion, datos_horarios):
                combinaciones_validas.append(combinacion)
    return combinaciones_validas

def main():
    # Cargar los datos de horarios y combinaciones
    datos_horarios = cargar_datos('datos_horarios_transformados_completo.json')
    combinaciones_validas = cargar_datos('combinaciones_validas.json')

    # Preparar para procesamiento paralelo
    num_cpus = max(1, multiprocessing.cpu_count() - 1)  # Usar todos menos 1 CPU
    chunk_size = max(1, len(combinaciones_validas) // num_cpus)

    # Dividir combinaciones en trozos para cada proceso
    chunks = [combinaciones_validas[i:i + chunk_size] for i in range(0, len(combinaciones_validas), chunk_size)]

    # Ejecutar verificación de solapamientos en paralelo
    with multiprocessing.Pool(processes=num_cpus) as pool:
        results = pool.starmap(filtrar_combinaciones, [(chunk, datos_horarios) for chunk in chunks])

    # Combinar resultados
    combinaciones_sin_solapamientos = [comb for sublist in results for comb in sublist]

    # Guardar las combinaciones válidas en un nuevo archivo
    with open('combinaciones_sin_solapamientos.json', 'w') as f:
        json.dump(combinaciones_sin_solapamientos, f, indent=4)

    print(f"Total de combinaciones sin solapamientos: {len(combinaciones_sin_solapamientos)}")
    print("Resultados guardados en 'combinaciones_sin_solapamientos.json'")

if __name__ == "__main__":
    main()
