import geopandas as gpd

from seccCensales.operDF import validaciones, manipSecCensales
from utils.operations.retocaDF import applyDFtransforms, passDFvalidators


def validaSeccionesCensalesINE(scDict):
    result = {y: {'fname': fname} for y, fname in scDict.items()}

    for y, fname in scDict.items():
        auxDF = gpd.read_file(fname)
        trfDF = applyDFtransforms(auxDF, manipSecCensales)

        result[y]['df'] = trfDF
        result[y]['checks'] = passDFvalidators(trfDF, validaciones)

    return result
