import unittest

import pandas as pd

from utils.operations.retocaDF import applyDFtransforms

DFin = pd.DataFrame(
    data={1: {'c1': 'a', 'c2': 'b', 'c3': 'c', 'c4': '1', 'c5': '1', 'c6': 'A'},
          2: {'c1': 'd', 'c2': 'e', 'c3': 'f', 'c4': '2', 'c5': '2', 'c6': 'D'}}).T

class TestRetocaDF(unittest.TestCase):
    def test_TransformConcat(self):
        trf = [{'concat': {'r1': ['c1', 'c3']}}]
        expectedR1 = pd.Series({1: 'ac', 2: 'df'})

        result = applyDFtransforms(DFin, trf)

        self.assertTrue(result['r1'].eq(expectedR1).all())

    def test_Transform2Numeric(self):
        trf = [{'2numeric': {'prefix': 'n', 'cols': ['c4']}},
               {'2numeric': {'cols': ['c5']}}
               ]
        expectedR1 = pd.Series({1: 1, 2: 2})

        result = applyDFtransforms(DFin, trf)

        print(result)

        self.assertTrue(result['nc4'].eq(expectedR1).all())
        self.assertTrue(result['c5'].eq(expectedR1).all())

    def test_TransformCase(self):
        trf = [{'upper': {'prefix': 'r', 'cols': ['c1']}},
               {'lower': {'prefix': 'r', 'cols': ['c6']}},
               ]

        result = applyDFtransforms(DFin, trf)

        print(result)

        self.assertTrue(result['rc1'].eq(DFin['c6']).all())
        self.assertTrue(result['rc6'].eq(DFin['c1']).all())


if __name__ == '__main__':
    unittest.main()
