import unittest
import json
from datetime import datetime, time
from generacion_datos import parse_horario

class TestGeneracionDatos(unittest.TestCase):

    def setUp(self):
        # Cargar los datos desde los archivos JSON generados
        with open('cursos_datos.json', 'r') as f:
            self.data = json.load(f)

    def test_parse_horario_online(self):
        """Test para horarios 'Online'."""
        horario = parse_horario("Online")
        self.assertEqual(horario, ('Online', None, None))

    def test_parse_horario_normal(self):
        """Test para horarios normales."""
        horario = parse_horario("Lu 10:01:00 - 11:20:00")
        expected_start = time(10, 1)
        expected_end = time(11, 20)
        self.assertEqual(horario, ('Lu', expected_start, expected_end))

    def test_cursos_dict_not_empty(self):
        """Verificar que cursos_dict no esté vacío."""
        self.assertTrue(len(self.data) > 0)

    def test_cursos_dict_obligatorio_not_empty(self):
        """Verificar que cursos_dict_obligatorio no esté vacío."""
        with open('cursos_datos_obl.json', 'r') as f:
            data_obligatorio = json.load(f)
        self.assertTrue(len(data_obligatorio) > 0)

    def test_datos_curso_completos(self):
        """Verificar que los datos del curso incluyan todas las claves necesarias."""
        for curso, detalles in self.data.items():
            self.assertIn('Horarios', detalles)
            self.assertIn('Datos', detalles)
            self.assertIn('Sigla', detalles['Datos'])
            self.assertIn('Asignatura', detalles['Datos'])
            self.assertIn('Docente', detalles['Datos'])

    def test_horarios_procesados_correctamente(self):
        """Verificar que los horarios se procesen correctamente."""
        for curso, detalles in self.data.items():
            for horario_str in detalles['Horarios']:
                horario = parse_horario(horario_str)
                self.assertIsNotNone(horario)

if __name__ == '__main__':
    unittest.main()
