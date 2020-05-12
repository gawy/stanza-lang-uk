import unittest
from src.bsf_to_beios import convert_bsf_2_beios, parse_bsf, BsfMeta


class TestBsf2Beios(unittest.TestCase):
    def setUp(self) -> None:
        self.data = ''
        self.markup = ''

    def test_empty_markup(self):
        res = convert_bsf_2_beios(self.data, '')
        self.assertEqual(res, '')


class TestBsf(unittest.TestCase):

    def test_empty_bsf(self):
        self.assertEqual(parse_bsf(''), [])

    def test_empty2_bsf(self):
        self.assertEqual(parse_bsf(' \n \n'), [])

    def test_1line_bsf(self):
        bsf = 'T1	PERS 103 118	Василь Нагірний'
        res = parse_bsf(bsf)
        expected = BsfMeta('T1', 'PERS', 103, 118, 'Василь Нагірний')
        self.assertEqual(len(res), 1)
        self.assertEqual(res, [expected])

    def test_2line_bsf(self):
        bsf = '''T9	PERS 778 783	Карла
T10	MISC 814 819	міста'''
        res = parse_bsf(bsf)
        expected = [BsfMeta('T9', 'PERS', 778, 783, 'Карла'),
                    BsfMeta('T10', 'MISC', 814, 819, 'міста')]
        self.assertEqual(len(res), 2)
        self.assertEqual(res, expected)

    def test_multiline_bsf(self):
        bsf = '''T3	PERS 220 235	Андрієм Кіщуком
T4	MISC 251 285	А .
Kubler .
Світло і тіні маестро
T5	PERS 363 369	Кіблер'''
        res = parse_bsf(bsf)
        expected = [BsfMeta('T3', 'PERS', 220, 235, 'Андрієм Кіщуком'),
                    BsfMeta('T4', 'MISC', 251, 285, '''А .
Kubler .
Світло і тіні маестро'''),
                    BsfMeta('T5', 'PERS', 363, 369, 'Кіблер')]
        self.assertEqual(len(res), len(expected))
        self.assertEqual(res, expected)



if __name__ == '__main__':
    unittest.main()
