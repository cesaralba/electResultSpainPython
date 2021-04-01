import logging
from argparse import ArgumentParser
from builtins import object
from collections.abc import Iterable
from itertools import product
from time import strftime, time
from pickle import dump

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import dok_matrix

from seccCensales.seccCensales import leeContornoSeccionesCensales, agrupaContornos

secNIV = ['CCAA', 'PRO', 'MUN', 'DIS', 'SEC']
# secNIV = ['CCAA', 'PRO']

resultBase = {'PAIS': {'claveAgr': None},
              'CCAA': {'claveAgr': 'CCA', 'extraCols': ['NCA', 'nCCA']},
              'PRO': {'claveAgr': 'nCPRO', 'extraCols': ['CCA', 'NCA', 'NPRO', 'nCCA', 'nCPRO']},
              'MUN': {'claveAgr': 'CUMUN',
                      'extraCols': ['CCA', 'nCPRO', 'CMUN', 'NCA', 'NPRO', 'NMUN', 'nCCA', 'nCPRO', 'nCMUN', 'nCUMUN']},
              'DIS': {'claveAgr': 'CUDIS',
                      'extraCols': ['CCA', 'nCPRO', 'CMUN', 'CDIS', 'CUMUN', 'NCA', 'NPRO', 'NMUN', 'nCCA', 'nCPRO',
                                    'nCMUN', 'codDistr', 'nCUMUN', 'nCUDIS']},
              'SEC': {'claveAgr': 'CUSEC',
                      'extraCols': ['CCA', 'nCPRO', 'CMUN', 'CDIS', 'CUMUN', 'CUDIS', 'NCA', 'NPRO', 'NMUN', 'nCCA',
                                    'nCPRO', 'nCMUN', 'codDistr', 'nCUMUN', 'nCUDIS', 'nCUSEC']}
              }

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s [%(process)d:@%(name)s %(levelname)s %(relativeCreated)12dms]: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)





def creaMatriz(df, clave=None, matricesMR=None):
    """
    A partir de un geodataframe devuelve un dataframe con la matriz de adyacencias entre sus filas
    :param df: geodataframe (geopandas)
    :param clave: columna del dataframe original que se va a usar como clave (filas y columnas del DF resultante)
    :param matricesMR: diccionario de pares { columnaDF:matrizADJ } para reducir cálculos. Ej: 2 provincias no pueden
                       ser adyacentes si sus respectivas CCAA no lo son
    :return: dataframe con la matriz resultante

    """
    dimdf = len(df)
    matriz = np.zeros_like(np.arange(dimdf * dimdf).reshape((dimdf, dimdf)), dtype=bool)

    idx = df.index.to_list()
    ridx = list(range(dimdf))
    estads = {'simetria': 0, 'matriz': 0, 'inters': 0}

    for ix, iy in product(ridx, ridx):

        if iy < ix:
            estads['simetria'] += 1
            continue

        x = idx[ix]
        y = idx[iy]

        d0 = df.loc[x]
        d1 = df.loc[y]

        if matricesMR:
            flag = False
            for k, matAux in matricesMR.items():
                if not matAux.loc[d0[k], d1[k]]:
                    flag = True
                    break
            if flag:
                estads['matriz'] += 1
                continue

        estads['inters'] += 1
        g0 = d0.geometry
        g1 = d1.geometry

        if g0.intersects(g1):
            matriz[ix, iy] = True
            if ix != iy:
                matriz[iy, ix] = True

    targNames = df[clave] if clave else df.index

    result = pd.DataFrame(matriz, index=targNames, columns=targNames)

    print(estads)
    return result


def creaMatrizJoblib(df, clave=None, matricesMR=None, JLconfig=None):
    from joblib import Parallel, delayed
    from scipy.sparse import dok_matrix

    if JLconfig is None:
        JLconfig = {}
    configParallel = {'verbose': 20}
    # TODO: Control de calidad con los parámetros
    configParallel['n_jobs'] = JLconfig.get('nproc', 2)
    configParallel['prefer'] = JLconfig.get('joblibmode', 'threads')

    dimdf = len(df)
    # matriz = np.zeros_like(np.arange(dimdf * dimdf).reshape((dimdf, dimdf)), dtype=bool)

    idx = df.index.to_list()
    ridx = list(range(dimdf))

    # estads = {'simetria': 0, 'matriz': 0, 'inters': 0}

    def checkAdjacency(ix, iy):
        if iy < ix:
            return None

        x = idx[ix]
        y = idx[iy]

        d0 = df.loc[x]
        d1 = df.loc[y]

        if matricesMR:
            flag = False
            for k, matAux in matricesMR.items():
                if not matAux.loc[d0[k], d1[k]]:
                    flag = True
                    break
            if flag:
                return None

        g0 = d0.geometry
        g1 = d1.geometry

        if g0.intersects(g1):
            return (ix, iy)

    resultJL = Parallel(**configParallel)(delayed(checkAdjacency)(x, y) for x, y in product(ridx, ridx))

    matriz = dok_matrix((dimdf, dimdf), dtype=bool)
    for x in resultJL:
        if x is None:
            continue
        print(x)
        matriz[x[0], x[1]] = True
        matriz[x[1], x[0]] = True

    targNames = df[clave] if clave else df.index

    result = pd.DataFrame(matriz.todense(), index=targNames, columns=targNames)

    return result


def preparaAgrupacionConts(df, listaNiveles=secNIV):
    """

    :param df:
    :return:
    """
    clavesAUsar = [k for k in secNIV if k in listaNiveles]
    result = {k: resultBase[k] for k in clavesAUsar}
    # Prepara los agregados de contornos y datos auxiliares
    for k in clavesAUsar:
        aux = agrupaContornos(df, claveAgr=result[k]['claveAgr'], extraCols=result[k]['extraCols'])
        aux['idx'] = range(len(aux))

        if result[k].get('nSUP', None):
            supLevel = result[k]['nSUP']
            kSupLevel = result[supLevel]['claveAgr']

            result[supLevel]['sup2k'] = aux.reset_index().groupby(kSupLevel)[result[k]['claveAgr']].apply(list)

        result[k]['contAgr'] = aux

    return result


def vecinos2DF(resVecinos, datos):
    """
    A partir del resultado de encuentraVecinos crea un diccionario de dataframes dispersos con las adyacencias en el
    nivel correspondiente

    :param resVecinos: resultado de encuentraVecinos
    :param datos: resultado de preparaAgrupacion
    :return: diccionario de DF dispersos. Los DF corresponden a las adyacencias al nivel indicado y tienen como índice
    el de los DF en datos.
    """
    auxMat = {k: dok_matrix((len(datos[k]['contAgr']), len(datos[k]['contAgr'])), dtype=bool) for k in resVecinos}
    result = dict()

    for k, sols in resVecinos.items():
        print(k, len(sols))
        for s in sols:
            auxMat[k][s[0], s[1]] = True
        result[k] = pd.SparseDataFrame(auxMat[k], index=datos[k]['contAgr'].index, columns=datos[k]['contAgr'].index,
                                       dtype=bool, default_fill_value=False)

    return result


def setDFLabels(df, datos, clave, etiqueta):
    """
    Cambia las etiquetas (index y columnas) de un DF (ojo, creaMatrizRec devuelve un dict de DFs) por otras que puedan
    ser más claras (nombres en lugar de números)
    :param df: DF a modificar
    :param datos: resultado de preparaAgrupacion
    :param clave: Clave para sacar el DF correspondiente en datos (sólo tiene sentido para 'CCAA','PRO' y quizás 'MUN')
    :param etiqueta: Columna que contiene la etiqueta de la agregación (resp. 'NCA','NPRO','NMUN'.
    :return: DF con los indices (vert y horiz) cambiados


    """
    return df.set_axis(datos[clave]['contAgr'][etiqueta], axis=1, inplace=False).set_axis(
        datos[clave]['contAgr'][etiqueta], axis=0, inplace=False)


def controlCalidad(df):
    """
    Busca entidades con el nombre mal puesto. Más que mal puesto, duplicado:
    :param df:
    :return:
    """
    # Encuentra nombres mal puestos
    reCA = pd.DataFrame(df.groupby('CCA').apply(lambda x: x['NCA'].value_counts()))
    print("Comunidades\n", reCA[(reCA.droplevel(1, axis=0).index.duplicated(keep=False))])

    reProv = pd.DataFrame(df.groupby('nCPRO').apply(lambda x: x['NPRO'].value_counts()))
    print("Provincias\n", reProv[(reProv.droplevel(1, axis=0).index.duplicated(keep=False))])

    reMun = pd.DataFrame(df.groupby('CUMUN').apply(lambda x: x['NMUN'].value_counts()))
    print("Municipios\n", reMun[(reMun.droplevel(1, axis=0).index.duplicated(keep=False))])


def procesaArgumentos():
    parser = ArgumentParser()

    parser.add('-i', dest='infile', type=str, required=True)
    parser.add('-o', dest='outfile', type=str, required=True)

    parser.add('-l', dest='categs', type=str, required=True)

    args = parser.parse_args()

    result = vars(args)

    return result


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

if __name__ == "__main__":
    args = procesaArgumentos()

    gdf = leeContornoSeccionesCensales(args.infile)

    contAgs = preparaAgrupacionConts(gdf)
    matricesAdj = creaMatrizRec(contAgs, ['CCAA', 'PRO', 'MUN', 'DIS', 'SEC'])

pass
