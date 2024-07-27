import unittest
from datetime import time
from event_processor import parse_time, check_overlap

class TestEventProcessor(unittest.TestCase):

    def test_parse_horario_valid(self):
        # Pruebas con formatos de horarios válidos
        self.assertEqual(parse_time("Lu 08:30:00 - 09:10:00"),
                         {'day': 'Lu', 'start': time(8, 30), 'end': time(9, 10), 'raw': "Lu 08:30:00 - 09:10:00"})
        self.assertEqual(parse_time("Vi 16:00:00 - 17:30:00"),
                         {'day': 'Vi', 'start': time(16, 0), 'end': time(17, 30), 'raw': "Vi 16:00:00 - 17:30:00"})

    def test_parse_horario_online(self):
        # Prueba con el caso especial 'Online'
        self.assertIsNone(parse_time("Online"))

    def test_parse_horario_invalid(self):
        # Pruebas con formatos de horarios inválidos
        self.assertIsNone(parse_time("Invalid format"))
        self.assertIsNone(parse_time("Lu 25:00:00 - 26:00:00"))
        self.assertIsNone(parse_time("Lu 08:00 - 09:00"))

    def test_verificar_solapamiento_no_solapamiento(self):
        # Prueba sin solapamiento
        horario1 = {'day': 'Lu', 'start': time(8, 0), 'end': time(9, 0)}
        horario2 = {'day': 'Lu', 'start': time(9, 0), 'end': time(10, 0)}
        self.assertFalse(check_overlap(horario1, horario2))

    def test_verificar_solapamiento_con_solapamiento(self):
        # Prueba con solapamiento
        horario1 = {'day': 'Lu', 'start': time(8, 0), 'end': time(10, 0)}
        horario2 = {'day': 'Lu', 'start': time(9, 0), 'end': time(11, 0)}
        self.assertTrue(check_overlap(horario1, horario2))

    def test_verificar_solapamiento_dias_diferentes(self):
        # Prueba con horarios en días diferentes (no debe haber solapamiento)
        horario1 = {'day': 'Lu', 'start': time(8, 0), 'end': time(9, 0)}
        horario2 = {'day': 'Ma', 'start': time(8, 0), 'end': time(9, 0)}
        self.assertFalse(check_overlap(horario1, horario2))

if __name__ == '__main__':
    unittest.main()
