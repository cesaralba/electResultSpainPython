import pandas as pd
import yaml
from schema import Schema, Optional, Or

from .zipfiles import fileOpener

SEPARATOR = "\n- "

errorFixSchema = Schema([{'condition': {str: object}, 'fix': {str: object}}], ignore_extra_keys=True)
transformDFschema = Schema(
    [Or({'2numeric': {'cols': [str], Optional('prefix', default='n'): str}},
        {'concat': {str: [str]}},
        {str: object}  # Cosas que no sabemos qué son
        )
     ]
)


def readFileAndValidateSchema(fname, schema=None):
    with fileOpener(fname, "r") as handle:
        operations = yaml.safe_load(handle)

    return operations if schema is not None else schema.validate(operations)


def readDFerrorFixFile(fname, df=None):
    operations = readFileAndValidateSchema(fname, errorFixSchema)

    if df is not None:
        if not validateDFerrorFix(operations, df):
            raise ValueError(f"readDFerrorFixFile: incorrect fixes on {fname}")
    return operations


def validateDFerrorFix(errorDataFix, df):
    badRules = []

    for fix in errorDataFix:
        reqSections = {'condition', 'fix'}

        SHPcolumns = set(df.columns)
        ruleColumns = {col for k in reqSections for col in fix[k].keys()}
        unknownCols = ruleColumns.difference(SHPcolumns)
        if unknownCols:
            badRules.append("errors on fix '%s'. Unknown columns: %s " % (fix, ",".join(sorted(unknownCols))))
            continue
    if badRules:
        raise KeyError(f"validateDFerrorFix: error on fixes: \n - {SEPARATOR.join(badRules)}")


def applyDFerrorFix(df, errorDataFnane):
    try:
        fixesList = readDFerrorFixFile(errorDataFnane)
        validateDFerrorFix(fixesList, df)
    except Exception as exc:
        raise ValueError(f"applyDFerrorFix: incorrect fixes on {errorDataFnane}: {exc}")

    def fixer(row, fields2fix):
        for col, value in fields2fix.items():
            row[col] = value
        return row

    for rule in fixesList:
        # https://stackoverflow.com/a/34162576
        condition = rule['condition']
        fields2fix = rule['fix']
        filter = pd.Series(condition)
        condList = (df[list(condition)] == filter).all(axis=1)
        df[condList] = df[condList].apply(lambda x: fixer(x, fields2fix), axis=1)

    return df


def readDFtransformFile(fname, df=None):
    operations = readFileAndValidateSchema(fname, transformDFschema)

    if df is not None:
        if not validateDFtransform(operations, df):
            raise ValueError(f"readDFtransformFile: incorrect fixes on {fname}")
    return operations


def validateDFtransform(operations, df):
    badOps = []

    currCols = set(df.columns.to_list())

    for op in operations:
        manip, params = list(op.items())[0]
        if manip == '2numeric':
            unknownCols = set()
            alreadyExistingCols = set()

            prefix = params.get('prefix', 'n')
            for col in params.get('cols', []):
                newCol = prefix + col
                if col not in currCols:
                    unknownCols.add(col)
                    continue
                if newCol in currCols:
                    alreadyExistingCols.add(newCol)
                    continue
                currCols.add(newCol)
            if unknownCols.union(alreadyExistingCols):
                msg = f'Problem with transform {op}. Unknown columns {sorted(unknownCols)}. Already existing columns: {sorted(alreadyExistingCols)}'
                badOps.append(msg)
        elif manip == 'concat':
            badConcats = list()

            for concat in params.items():
                flag = False
                newCol, cols2add = concat
                unknownCols = set()
                alreadyExistingCols = set()

                if newCol in currCols:
                    alreadyExistingCols.add(newCol)
                    flag = True

                auxUnknown = {col for col in cols2add if col not in currCols}
                if auxUnknown:
                    unknownCols.update(auxUnknown)
                    flag = True

                if flag:
                    msg = f'concat: {concat}. Already existing column: {sorted(alreadyExistingCols)}. Unknown columns {sorted(unknownCols)}.'
                    badConcats.append(msg)
                    continue

                currCols.add(newCol)
            if badConcats:
                msg = f'Problem with concats: {", ".join(badConcats)}'
                badOps.append(msg)
        else:
            print(f"validateDFtransform: operacion desconocida '{manip}': {op}")

    if badOps:
        raise ValueError(f"validateDFtransform: Problems with some transforms:\n- {SEPARATOR.join(badOps)}")


def applyDFtransforms(df, operations):
    validateDFtransform(operations, df)

    for op in operations:
        manip, params = list(op.items())[0]

        if manip == "2numeric":
            prefix = params.get('prefix', 'n')
            for col in params.get('cols', []):
                newCol = prefix + col
                df[newCol] = pd.to_numeric(df[col])
        elif manip == 'concat':
            for newCol, cols2add in params.items():
                nameMerger = lambda x: "".join([x[label] for label in cols2add])
                df[newCol] = df.apply(nameMerger, axis=1)
        else:
            print(f"applyDFtransforms: operación desconocida '{manip}': {op}")

    return df