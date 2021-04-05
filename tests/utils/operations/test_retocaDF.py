import unittest

import pandas as pd
from jsonschema import ValidationError

from utils.operations.retocaDF import applyDFtransforms, validateDFtransform

DFin = pd.DataFrame(
    data={
        1: {"c1": "a", "c2": "b", "c3": "c", "c4": "1", "c5": "1", "c6": "A", "nc6": "X"},
        2: {"c1": "d", "c2": "e", "c3": "f", "c4": "2", "c5": "2", "c6": "D", "nc6": "Y"},
    }
).T


class Test_applyDFtransforms(unittest.TestCase):
    # Happy paths
    def test_TransformConcat(self):
        trf = [{"concat": {"r1": ["c1", "c3"]}}]
        expectedR1 = pd.Series({1: "ac", 2: "df"})

        result = applyDFtransforms(DFin, trf)

        self.assertTrue(result["r1"].eq(expectedR1).all())

    def test_Transform2Numeric(self):
        trf = [
            {"2numeric": {"prefix": "n", "cols": ["c4"]}},
            {"2numeric": {"cols": ["c5"]}},
        ]
        expectedR1 = pd.Series({1: 1, 2: 2})

        result = applyDFtransforms(DFin, trf)

        print(result)

        self.assertTrue(result["nc4"].eq(expectedR1).all())
        self.assertTrue(result["c5"].eq(expectedR1).all())

    def test_TransformCase(self):
        trf = [
            {"upper": {"prefix": "r", "cols": ["c1"]}},
            {"lower": {"prefix": "r", "cols": ["c6"]}},
        ]

        result = applyDFtransforms(DFin, trf)

        print(result)

        self.assertTrue(result["rc1"].eq(DFin["c6"]).all())
        self.assertTrue(result["rc6"].eq(DFin["c1"]).all())


class Test_validateDFtransform(unittest.TestCase):
    def test_EmptyTransform(self):
        trf = []
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def test_BadColName1(self):
        trf = [{"2numeric": {"cols": []}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def test_BadColName2(self):
        trf = [{"2numeric": {"cols": ['+']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def test_BadColName3(self):
        trf = [{"2numeric": {"cols": ['1']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def test_BadColName4(self):
        trf = [{"2numeric": {"cols": ['a+']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def test_UnknownOp(self):
        trf = [{"XXX": {"cols": ['c1']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def test_TooManyOpsAtOnce(self):
        trf = [{"2numeric": {"cols": ['c1']}, "lower": {"cols": ['c1']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def testMonoOpsBadParameters(self):
        trf = [{"2numeric": {"_cols": ['c1']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def testMonoOpsTooManyParams(self):
        trf = [{"2numeric": {"cols": ['c1'], "prefix": 'a', "XXXX": ['a']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def testMonoOpsMissingCols(self):
        trf = [{"2numeric": {"prefix": 'a'}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def testMonoOpsPrefixBadTypeCols(self):
        trf = [{"2numeric": {"prefix": ['a']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)

    def testMonoOpsMissingCols(self):
        trf = [{"2numeric": {"prefix": ['a']}}]
        with self.assertRaises(ValidationError):
            validateDFtransform(trf, DFin)


    def testMonoOpsExistingCols(self):
        trf = [{"lower": {"prefix": 'n', "cols": ['c6']}}]
        with self.assertRaises(ValueError):
            validateDFtransform(trf, DFin)


if __name__ == "__main__":
    unittest.main()
