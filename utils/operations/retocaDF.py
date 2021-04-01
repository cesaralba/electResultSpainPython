import pandas as pd
import yaml
from jsonschema import validate, Draft7Validator

from utils.zipfiles import fileOpener
from .retocaDFschemas import errorFixSchema, transformDFschema, validatorDFschema

SEPARATOR = "\n- "
SINGLECOLTRANSFORMNAMES = {'2numeric', 'upper', 'lower'}


# TODO: Cambiar los print por logging

def readFileAndValidateSchema(fname, schema=None, semanticValidator=None, *args, **kwargs):
    with fileOpener(fname, "r") as handle:
        operations = yaml.safe_load(handle)

    if schema is not None:
        validate(operations, schema=schema, cls=Draft7Validator)

    if semanticValidator is not None:
        semanticValidator(operations, *args, **kwargs)

    return operations


def readDFerrorFixFile(fname, df=None):
    operations = readFileAndValidateSchema(fname, schema=errorFixSchema, semanticValidator=validateDFerrorFix, df=df)

    if df is not None and not validateDFerrorFix(operations, df):
        raise ValueError(f"readDFerrorFixFile: incorrect fixes on {fname}")
    return operations


def validateDFerrorFix(errorDataFix, df):
    validate(errorDataFix, schema=errorFixSchema, cls=Draft7Validator)
    if df is None:
        return False

    badRules = []

    for fix in errorDataFix:
        reqSections = {'condition', 'fix'}

        ruleColumns = {col for k in reqSections for col in fix[k].keys()}
        unknownCols = checkColList(ruleColumns, df=df)
        if unknownCols:
            badRules.append("errors on fix '%s'. Unknown columns: %s " % (fix, ",".join(sorted(unknownCols))))

    if badRules:
        raise KeyError(f"validateDFerrorFix: error on fixes:{SEPARATOR}{SEPARATOR.join(badRules)}")

    return True


def applyDFerrorFix(df, fixesList):
    try:
        validateDFerrorFix(fixesList, df)
    except Exception as exc:
        raise ValueError(f"applyDFerrorFix: incorrect fixes: {exc}")

    def fixer(row, fix):
        for col, value in fix.items():
            row[col] = value
        return row

    for rule in fixesList:
        # https://stackoverflow.com/a/34162576
        condition = rule['condition']
        fields2fix = rule['fix']
        filterCond = pd.Series(condition)
        condList = (df[list(condition)] == filterCond).all(axis=1)

        if df[condList].shape[0] > 0:
            print(f"Condition: {condition} -> Fix: {fields2fix}. Applied to {df[condList].shape[0]} row(s)")
            df[condList] = df[condList].apply(lambda x: fixer(x, fields2fix), axis=1)

    return df


def readDFtransformFile(fname, df=None):
    operations = readFileAndValidateSchema(fname, transformDFschema)

    if df is not None:
        if not validateDFtransform(operations, df):
            raise ValueError(f"readDFtransformFile: incorrect fixes on {fname}")
    return operations


def validateDFtransform(operations, df):
    validate(operations, schema=transformDFschema, cls=Draft7Validator)

    if df is None:
        return False

    badOps = []

    currCols = set(df.columns.to_list())

    for op in operations:
        manip, params = list(op.items())[0]
        if manip in SINGLECOLTRANSFORMNAMES:
            unknownCols = set()
            alreadyExistingCols = set()

            prefix = params.get('prefix', None)

            if prefix:  # We are adding new columns so we must check new ones aren't already there
                for col in params.get('cols', []):
                    newCol = prefix + col
                    if col not in currCols:
                        unknownCols.add(col)
                        continue
                    if newCol in currCols:
                        alreadyExistingCols.add(newCol)
                        continue
                    currCols.add(newCol)
            else:  # Just check columns exist
                unknownCols = checkColList(params.get('cols', []), colset=currCols)

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

                auxUnknown = checkColList(cols2add, colset=currCols)
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
        raise ValueError(f"validateDFtransform: Problems with some transforms:{SEPARATOR}{SEPARATOR.join(badOps)}")

    return True


def applyDFtransforms(df, operations):
    try:
        validateDFtransform(operations, df)
    except Exception as exc:
        raise ValueError(f"applyDFtransforms: incorrect fixes: {exc}")

    for op in operations:
        manip, params = list(op.items())[0]

        if manip in SINGLECOLTRANSFORMNAMES:
            prefix = params.get('prefix', None)
            for col in params.get('cols', []):
                newCol = col if prefix is None else (prefix + col)

                if manip == "2numeric":
                    df[newCol] = pd.to_numeric(df[col])
                elif manip == "upper":
                    df[newCol] = df[col].str.upper()
                elif manip == "lower":
                    df[newCol] = df[col].str.lower()

        elif manip == 'concat':
            for newCol, cols2add in params.items():
                nameMerger = lambda x: "".join([x[label] for label in cols2add])
                df[newCol] = df.apply(nameMerger, axis=1)
        else:
            print(f"applyDFtransforms: operación desconocida '{manip}': {op}")

    return df


def readDFvalidatorFile(fname, df=None):
    checks = readFileAndValidateSchema(fname, validatorDFschema)

    if df is not None and not validateDFvalidator(checks, df):
        raise ValueError(f"readDFvalidatorFile: incorrect validations on {fname}")
    return checks


def validateDFvalidator(checks, df):
    validate(checks, schema=validatorDFschema, cls=Draft7Validator)

    badPairs = []

    for pair in checks:

        unknownCols = checkColList(pair, df=df)

        if unknownCols:
            msg = f'Problem with validator {pair}. Unknown columns {sorted(unknownCols)}.'
            badPairs.append(msg)

    if badPairs:
        raise ValueError(f"validateDFvalidator: Problems with some validators:{SEPARATOR}{SEPARATOR.join(badPairs)}")


# TODO: Esto cambiará si se hacen más tipos de validaciones pero de momento tira así
def passDFvalidators(df, checks, **kwargs):
    try:
        validateDFvalidator(checks, df)
    except Exception as exc:
        raise ValueError(f"passDFvalidators: incorrect checks: {exc}")

    result = []
    for c, n in checks:
        soloC = df[c]
        subCyN = df[[c, n]]

        if soloC.nunique() == len(subCyN.drop_duplicates()):
            continue

        failedPair = {'pair': [c, n], 'combs': []}
        pairCounts = df[[c, n]].drop_duplicates()[c].value_counts()
        claveProblem = pairCounts[pairCounts > 1].reset_index()['index']
        for cp in claveProblem:
            comb2add = {'claveIDX': c, 'claveVAL': n, 'valorIDX': cp}
            subconjunto = df[df[c] == cp]
            valorCounts = subconjunto[n].value_counts()
            nombresProb = valorCounts.to_dict()
            comb2add['cuentas'] = nombresProb

            valorMax = valorCounts.max()

            if valorMax != 1:
                valorMayoritario = valorCounts[valorCounts == valorMax].index.tolist()
                comb2add['valorMayoria'] = valorMayoritario
                subconjuntoDivergente = subconjunto[~(subconjunto[n].isin(valorMayoritario))]
                comb2add['divergentes'] = subconjuntoDivergente
            else:
                comb2add['divergentes'] = subconjunto

            failedPair['combs'].append(comb2add)

        result.append(failedPair)

    return result


def validatorResult2str(comps, df):
    """ Aqui se mostrará algo cuando falle"""
    pass


def checkColList(collist, df=None, colset=None):
    actColset = {} if colset is None else colset

    DFcolumns = set(actColset) if df is None else set(df.columns)
    ruleColumns = set(collist)
    unknownCols = ruleColumns.difference(DFcolumns)

    return unknownCols
