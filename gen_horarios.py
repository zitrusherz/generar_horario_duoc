import json
import os
from datetime import datetime
def convertir_hora_a_minutos(hora):
    formato = '%H:%M'
    dt = datetime.strptime(hora, formato)
    #print(dt)
    return dt.hour * 60 + dt.minute


def calc_vent_tiempo(horarios1, horarios2):
    ventanas_de_tiempo = []
    dia = None
    # Comprobar si alguno de los horarios contiene 'Online'
    if 'Online' in horarios1 and len(horarios1) > 1:
        horarios1 = horarios1[1:]

    if 'Online' in horarios2 and len(horarios2) > 1:
        horarios2 = horarios2[1:]


    # Procesar cada horario
    for horario1 in horarios1:
        #print(horario1)
        dia1, rango_hora1 = horario1[:2], horario1.split()
        #print('dia 1',dia1)
        #print(rango_hora1)
        if len(rango_hora1[1]) == 8:
            inicio1 = rango_hora1[1][0:5]
        else:
            inicio1 = rango_hora1[1][0:4]
        if len(rango_hora1[3]) == 8:
            fin1 = rango_hora1[3][:5]
        else:
            fin1 = rango_hora1[3][:4]
        #print(inicio1, fin1)
        minutos_inicio1 = convertir_hora_a_minutos(inicio1)
        minutos_fin1 = convertir_hora_a_minutos(fin1)
        #print(minutos_inicio1, minutos_fin1)
        for horario2 in horarios2:
            dia2, rango_hora2 = horario2[:2], horario2.split()
            #print('dia 2',dia2)
            #print(rango_hora2)
            if len(rango_hora2[1]) == 8:
                inicio2 = rango_hora2[1][:5]
            else:
                inicio2 = rango_hora2[1][:4]
            if len(rango_hora2[3]) == 8:
                fin2 = rango_hora2[3][:5]
            else:
                fin2 = rango_hora2[3][:4]

            #print(inicio2, fin2)
            minutos_inicio2 = convertir_hora_a_minutos(inicio2)
            minutos_fin2 = convertir_hora_a_minutos(fin2)

            # Calcular la ventana de tiempo si los días coinciden
            #print(dia1 == dia2)
            if dia1 == dia2:
                #print(dia1, dia2)
                if minutos_fin1 <= minutos_inicio2:
                    ventana = minutos_inicio2 - minutos_fin1
                    ventanas_de_tiempo.append(ventana)
                elif minutos_fin2 <= minutos_inicio1:
                    ventana = minutos_inicio1 - minutos_fin2
                    ventanas_de_tiempo.append(ventana)
                dia = dia1


    return tuple([ventanas_de_tiempo,dia])
def cargar_datos_cursos(cursos_file, solapamientos_file):
    with open(cursos_file, 'r') as f:
        cursos_datos_obl = json.load(f)
    with open(solapamientos_file, 'r') as f:
        solapamientos_obl = json.load(f)
    return cursos_datos_obl, solapamientos_obl
cursos_datos_obl, solapamientos_obl = cargar_datos_cursos('cursos_datos_obl.json', 'solapamientos_obl.json')



def gen_lista_vent_tiempo(seccion, solapamientos):
    ventanas_de_tiempo = {}

    for key, value in cursos_datos_obl.items():
        if key == seccion or key in solapamientos or cursos_datos_obl[seccion]['Datos']['Sigla'] == value['Datos']['Sigla']:
            continue

        #print(f'key={key}: value={value}')
       #print(cursos_datos_obl[seccion]['Horarios'])
        #print(value['Horarios'])

        ventana_de_t = calc_vent_tiempo(cursos_datos_obl[seccion]['Horarios'], value['Horarios'])
        #print(ventana_de_t)
        if not None in ventana_de_t:
            ventanas_de_tiempo[(seccion, key)]=ventana_de_t

        #print(ventanas_de_tiempo)
    return ventanas_de_tiempo


def generar_lista_cursos_solapados(seccion):

    dict_cursos_solapados = solapamientos_obl[seccion]
    #print(dict_cursos_solapados)
    lista_cursos_solapados=[elem['curso'] for elem in dict_cursos_solapados]
    #print(lista_cursos_solapados)
    return lista_cursos_solapados
count = 0
#print(f'Cursos datos obligatorios: {cursos_datos_obl}')

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2]
        pivot_value = min(pivot[1][0]) if pivot[1][0] else float('inf')
        left = [x for x in arr if min(x[1][0]) < pivot_value]
        middle = [x for x in arr if min(x[1][0]) == pivot_value]
        right = [x for x in arr if min(x[1][0]) > pivot_value]
        return quick_sort(left) + middle + quick_sort(right)

def gen_horario_optimo(seccion,solapamientos,ventanas_de_tiempo):

    ventanas_ordenadas = ordenar_ventana(ventanas_de_tiempo)
    horario = [seccion]
    horarios = []
    set_solapamientos = set(solapamientos)
    print(set_solapamientos)

    for elemnt in ventanas_ordenadas:

        print(elemnt)
        print(elemnt[0][1])
        print(cursos_datos_obl[elemnt[0][1]])
        if elemnt[0][1] not in horario:
            for i in range(len(horario)):
                #print(horario[i].startswith(cursos_datos_obl[elemnt[0][1]]['Datos']['Sigla']))
                #print(horario[i])
                #print(cursos_datos_obl[elemnt[0][1]]['Datos']['Sigla'])
                guion_indice = horario[i].index('-')
                #print(horario[i][:guion_indice])
                curso_repetido = horario[i][:guion_indice] == cursos_datos_obl[elemnt[0][1]]['Datos']['Sigla']
                #print(curso_repetido)
                if curso_repetido:
                    break

                elif not curso_repetido and i == len(horario)-1:
                    if not elemnt[0][1] in set_solapamientos:
                        horario.append(elemnt[0][1])
                        print('horario', horario)

                        set_solapamientos = set_solapamientos | set(generar_lista_cursos_solapados(elemnt[0][1]))
    horarios.append(horario)

    print('lista_solapamientos', set_solapamientos)
    print('horario', horario)
    print('horarios', horarios)


def ordenar_ventana(ventanas_de_tiempo):
    ventanas_de_tiempo_list = list(ventanas_de_tiempo.items())
    ventanas_ordenadas = quick_sort(ventanas_de_tiempo_list)
    return ventanas_ordenadas
for curso in cursos_datos_obl.items():
    #print(f"Curso: {curso}, tipo: {type(curso)}")
    print(f'seccion: {curso[0]}')
    solapamientos = generar_lista_cursos_solapados(curso[0])
    ventanas_de_tiempo = gen_lista_vent_tiempo(curso[0], solapamientos)
    #print('Ventanas de tiempo ',ventanas_de_tiempo)
    gen_horario_optimo(curso[0], solapamientos, ventanas_de_tiempo)
    count+=1
    if count == 1:
        break



output_folder = 'horarios generados'
os.makedirs(output_folder, exist_ok=True)
