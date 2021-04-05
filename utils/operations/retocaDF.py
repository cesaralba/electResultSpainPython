"""
This module provides a mean to declare operations to perform on a dataframe using YAML files or plain variables

Operations are:
* Fixes: on rows that matches a condition (a column has a certain value), replaces the content of a column (may not be
    the same).
* Transformations: perform generic operations to columns. Operations covered are:
  * Conversion to numeric. Inplace or creating a new column
  * Change to upper case. Inplace or creating a new column
  * Change to lower case. Inplace or creating a new column
  * Concatenation of the content of several columns into a new one.
* Validations: checks that the content of a column or a pair of columns meet some condition

The operations come in a file (or variable) are lists of items of a single type (operation, validation or fix). The have the following formats:

FIXES
- condition: { colName1: value}
  fix:       { colName2: newValue }

The columns in both fields can be different
The values can be either string or numeric

TRANSFORMATIONS
There are 4 operations covered:
- 2numeric: #Converts to numeric
    prefix: "myPrefix" #Optional if not provided transformation will be in place
    cols: [listOfColumns]
- upper: #Changes string to upper case
    prefix: "myPrefix" #Optional if not provided transformation will be in place
    cols: [listOfColumns]
- lower: #Changes string to lower case
    prefix: "myPrefix" #Optional if not provided transformation will be in place
    cols: [listOfColumns]
- concat:
    newCol1: [cols2concat]
    newCol2: [cols2concat]

if a prefix is provided for the transformation, a new column named prefix + colName will be created. If it is not, transformation will be made inplace.

VALIDATIONS:




"""
import pandas as pd
import yaml
from jsonschema import validate, Draft7Validator

from utils.zipfiles import fileOpener
from .retocaDFschemas import errorFixSchema, transformDFschema, validatorDFschema

SEPARATOR = "\n- "
SINGLECOLTRANSFORMNAMES = {"2numeric", "upper", "lower"}


# TODO: Cambiar los print por logging


def readFileAndValidateSchema(fname, schema=None, semanticValidator=None, *args, **kwargs):
    """
    Reads a YAML file, validates the format against an schema and, if provided the function, validates
    the meaning of the file against the subject it will be used for.
    :param fname: filename with data
    :param schema: schema to validate the format of data against
    :param semanticValidator: function to validate the content of the file against
    :param args: parameters passed to semanticValidator
    :param kwargs:  parameters passed to semanticValidator
    :return: content of data

    Raise an Exception something is wrong with the file
    """
    with fileOpener(fname, "r") as handle:
        operations = yaml.safe_load(handle)

    if schema is not None:
        validate(operations, schema=schema, cls=Draft7Validator)

    if semanticValidator is not None:
        semanticValidator(operations, *args, **kwargs)

    return operations


def readDFerrorFixFile(fname, df=None):
    """
    Reads a file with fixes to the content of a dataframe and validates it.
    :param fname:
    :param df:
    :return:
    """
    operations = readFileAndValidateSchema(
        fname, schema=errorFixSchema, semanticValidator=validateDFerrorFix, df=df
    )

    if df is not None and not validateDFerrorFix(operations, df):
        raise ValueError(f"readDFerrorFixFile: incorrect fixes on {fname}")
    return operations


def validateDFerrorFix(errorDataFix, df):
    validate(errorDataFix, schema=errorFixSchema, cls=Draft7Validator)
    if df is None:
        return False

    badRules = []

    for fix in errorDataFix:
        reqSections = {"condition", "fix"}

        ruleColumns = {col for k in reqSections for col in fix[k].keys()}
        unknownCols = checkColList(ruleColumns, df=df)
        if unknownCols:
            badRules.append(
                "errors on fix '%s'. Unknown columns: %s "
                % (fix, ",".join(sorted(unknownCols)))
            )

    if badRules:
        raise KeyError(
            f"validateDFerrorFix: error on fixes:{SEPARATOR}{SEPARATOR.join(badRules)}"
        )

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
        condition = rule["condition"]
        fields2fix = rule["fix"]
        filterCond = pd.Series(condition)
        condList = (df[list(condition)] == filterCond).all(axis=1)

        if df[condList].shape[0] > 0:
            print(
                f"Condition: {condition} -> Fix: {fields2fix}. Applied to {df[condList].shape[0]} row(s)"
            )
            df[condList] = df[condList].apply(
                lambda x, fieldList=fields2fix: fixer(x, fieldList), axis=1
            )

    return df


def readDFtransformFile(fname, df=None):
    operations = readFileAndValidateSchema(fname, transformDFschema)

    if df is not None and not validateDFtransform(operations, df):
        raise ValueError(f"readDFtransformFile: incorrect fixes on {fname}")
    return operations


def validateDFtransform(operations, df):
    validate(operations, schema=transformDFschema, cls=Draft7Validator)

    if df is None:
        return False

    badOps = []

    currCols = set(df.columns)

    for op in operations:
        manip, params = list(op.items())[0]
        if manip in SINGLECOLTRANSFORMNAMES:
            currCols, errMsgs = trfValidMonocolOp(op, params, currCols)
            badOps = badOps + errMsgs

        elif manip == "concat":
            currCols, errMsgs = trfValidConcatOp(params, currCols)
            badOps = badOps + errMsgs

        else:
            print(f"validateDFtransform: operacion desconocida '{manip}': {op}")

    if badOps:
        raise ValueError(
            f"validateDFtransform: Problems with some transforms:{SEPARATOR}{SEPARATOR.join(badOps)}"
        )

    return True


def trfValidConcatOp(params, currCols):
    badOps = []
    badConcats = list()
    for concatGroup in params.items():
        newCol, cols2add = concatGroup

        alreadyExistingCols = set(newCol).intersection(currCols)
        unknownCols = set(cols2add).difference(currCols)

        if alreadyExistingCols.union(unknownCols):
            msg = (
                    f"concat: {concatGroup}. Already existing column: {sorted(alreadyExistingCols)}. "
                    + f"Unknown columns {sorted(unknownCols)}."
            )

            badConcats.append(msg)
            continue

        currCols.add(newCol)
    if badConcats:
        msg = f'Problem with concats: {", ".join(badConcats)}'
        badOps.append(msg)

    return currCols, badOps


def trfValidMonocolOp(op, params, currCols):
    badOps = []

    alreadyExistingCols = set()
    prefix = params.get("prefix", "")
    colList = set(params.get("cols", []))
    unknownCols = colList.difference(currCols)
    remainingCols = colList.intersection(currCols)
    if prefix != "":
        newColList = set(map(lambda s, pref=prefix: pref + s, remainingCols))
        alreadyExistingCols.update(newColList.intersection(currCols))
        currCols.update(newColList)
    if unknownCols.union(alreadyExistingCols):
        msg = (
                f"Problem with transform {op}. Unknown columns {sorted(unknownCols)}. "
                + f"Already existing columns: {sorted(alreadyExistingCols)}"
        )
        badOps.append(msg)

    return currCols, badOps


def applyDFtransforms(df, operations):
    try:
        validateDFtransform(operations, df)
    except Exception as exc:
        raise ValueError(f"applyDFtransforms: incorrect fixes: {exc}")

    for op in operations:
        manip, params = list(op.items())[0]

        if manip in SINGLECOLTRANSFORMNAMES:
            prefix = params.get("prefix", "")
            for col in params.get("cols", []):
                newCol = prefix + col

                df[newCol] = trfMonocolOp(manip, df, col)

        elif manip == "concat":
            for newCol, cols2add in params.items():
                nameMerger = lambda x, colList=cols2add: "".join(
                    [x[label] for label in colList]
                )
                df[newCol] = df.apply(nameMerger, axis=1)
        else:
            print(f"applyDFtransforms: operación desconocida '{manip}': {op}")

    return df


def trfMonocolOp(manip: str, df: pd.DataFrame, col: str):
    if manip == "2numeric":
        result = pd.to_numeric(df[col])
    elif manip == "upper":
        result = df[col].str.upper()
    elif manip == "lower":
        result = df[col].str.lower()
    else:
        raise ValueError(f"trfMonocolOp: unknown op {manip}")

    return result


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
            msg = (
                f"Problem with validator {pair}. Unknown columns {sorted(unknownCols)}."
            )
            badPairs.append(msg)

    if badPairs:
        raise ValueError(
            f"validateDFvalidator: Problems with some validators:{SEPARATOR}{SEPARATOR.join(badPairs)}"
        )


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

        failedPair = {"pair": [c, n], "combs": []}
        pairCounts = df[[c, n]].drop_duplicates()[c].value_counts()
        claveProblem = pairCounts[pairCounts > 1].reset_index()["index"]
        for cp in claveProblem:
            comb2add = {"claveIDX": c, "claveVAL": n, "valorIDX": cp}
            subconjunto = df[df[c] == cp]
            valorCounts = subconjunto[n].value_counts()
            nombresProb = valorCounts.to_dict()
            comb2add["cuentas"] = nombresProb

            valorMax = valorCounts.max()

            if valorMax != 1:
                valorMayoritario = valorCounts[valorCounts == valorMax].index.tolist()
                comb2add["valorMayoria"] = valorMayoritario
                subconjuntoDivergente = subconjunto[
                    ~(subconjunto[n].isin(valorMayoritario))
                ]
                comb2add["divergentes"] = subconjuntoDivergente
            else:
                comb2add["divergentes"] = subconjunto

            failedPair["combs"].append(comb2add)

        result.append(failedPair)

    return result


def validatorResult2str(comps, df):
    """ Aqui se mostrará algo cuando falle"""
    pass


def checkColList(collist, df=None, colset=None):
    """
    Comprueba si un dataframe tiene un conjunto de columnas requeridas
    :param collist: columnas deseadas
    :param df: dataframe que comprobar
    :param colset: lista de columnas (alternativo a df, toma precedencia df)
    :return: elementos en collist que no están en las columnas de df (o en colset)
    """
    actColset = colset or {}

    DFcolumns = set(actColset) if df is None else set(df.columns)
    ruleColumns = set(collist)
    unknownCols = ruleColumns.difference(DFcolumns)

    return unknownCols
