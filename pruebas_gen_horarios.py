import unittest
import gen_horarios as gh
import json
def cargar_datos_cursos(cursos_path, solapamientos_path):
    with open(cursos_path, 'r') as f:
        cursos_datos_obl = json.load(f)
    with open(solapamientos_path, 'r') as f:
        solapamientos_obl = json.load(f)
    return cursos_datos_obl, solapamientos_obl


class TestGenHorarios(unittest.TestCase):

    def test_cargar_datos_cursos(self):
        cursos_datos_obl, solapamientos_obl = gh.cargar_datos_cursos('cursos_datos_obl.json', 'solapamientos_obl.json')
        self.assertIsInstance(cursos_datos_obl, dict)
        self.assertIsInstance(solapamientos_obl, dict)
        self.assertTrue('APY4461-018D' in cursos_datos_obl)
        self.assertTrue('APY4461-018D' in solapamientos_obl)

class TestFiltrarSeccionesOptimas(unittest.TestCase):

    def test_filtrar_secciones_optimas(self):
        cursos_datos_obl, solapamientos_obl = gh.cargar_datos_cursos('cursos_datos_obl.json', 'solapamientos_obl.json')
        secciones_optimas = gh.filtrar_secciones_optimas(cursos_datos_obl, solapamientos_obl)

        # Asegurarse de que el resultado es un diccionario
        self.assertTrue(isinstance(secciones_optimas, dict))

        # Verificar que el diccionario no esté vacío (esto puede variar según los datos)
        self.assertGreater(len(secciones_optimas), 0)

        # Comprobar que las secciones no tienen solapamientos (esto depende de los datos de prueba)
        for secciones in secciones_optimas.values():
            for seccion in secciones:
                self.assertNotIn(seccion, solapamientos_obl)


class TestGenerarHorariosOptimos(unittest.TestCase):

    def setUp(self):
        # Cargar datos de prueba
        self.cursos_datos_obl, self.solapamientos_obl = gh.cargar_datos_cursos('cursos_datos_obl.json', 'solapamientos_obl.json')

    def test_generar_horarios_optimos(self):
        # Generar los horarios óptimos
        horarios_optimos = gh.generar_horarios_optimos(self.cursos_datos_obl, self.solapamientos_obl)

        # Verificar que horarios_optimos es una lista
        self.assertIsInstance(horarios_optimos, list)

        # Verificar que la lista no esté vacía
        self.assertGreater(len(horarios_optimos), 0)

        # Verificar que los horarios no se solapen con otros cursos según los solapamientos definidos
        for item in horarios_optimos:
            seccion = item['seccion']
            horarios = item['horarios']
            self.assertIsInstance(horarios, list)

            # Verificación de no solapamiento con cursos listados en solapamientos_obl
            for horario in horarios:
                if horario != 'Online':
                    if seccion in self.solapamientos_obl:
                        for solapamiento in self.solapamientos_obl[seccion]:
                            curso_solapado = solapamiento['curso']
                            horario_2 = solapamiento['horario_2']
                            if curso_solapado in self.cursos_datos_obl:
                                self.assertNotIn(horario, self.cursos_datos_obl[curso_solapado]['Horarios'],
                                    f"El horario {horario} de la sección {seccion} solapa con {horario_2} de {curso_solapado}")

    def test_horarios_online(self):
        # Verificar que los horarios 'Online' se manejan correctamente
        horarios_optimos = gh.generar_horarios_optimos(self.cursos_datos_obl, self.solapamientos_obl)
        for item in horarios_optimos:
            seccion = item['seccion']
            horarios = item['horarios']
            for horario in horarios:
                if horario == 'Online':
                    self.assertIn('Online', self.cursos_datos_obl[seccion]['Horarios'],
                        f"El horario 'Online' no está registrado correctamente en la sección {seccion}")

    def test_estructura_horarios_optimos(self):
        # Verificar que la estructura de horarios_optimos es la esperada
        horarios_optimos = gh.generar_horarios_optimos(self.cursos_datos_obl, self.solapamientos_obl)
        for item in horarios_optimos:
            self.assertIn('seccion', item)
            self.assertIn('horarios', item)
            self.assertIsInstance(item['horarios'], list)
            self.assertIsInstance(item['seccion'], str)


















if __name__ == '__main__':
    unittest.main()
