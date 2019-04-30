from argparse import ArgumentParser
from collections.abc import Iterable
from itertools import product

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import dok_matrix

secNIV = ['CCAA', 'PRO', 'MUN', 'DIS', 'SEC']
# secNIV = ['CCAA', 'PRO']

resultBase = {'CCAA': {'claveAgr': 'CCA', 'extraCols': ['NCA', 'nCCA']},
              'PRO': {'claveAgr': 'CPRO', 'extraCols': ['CCA', 'NCA', 'NPRO', 'nCCA', 'nCPRO'], 'nSUP': 'CCAA'},
              'MUN': {'claveAgr': 'CUMUN',
                      'extraCols': ['CCA', 'CPRO', 'CMUN', 'NCA', 'NPRO', 'NMUN', 'nCCA', 'nCPRO', 'nCMUN', 'nCUMUN'],
                      'nSUP': 'PRO'},
              'DIS': {'claveAgr': 'CUDIS',
                      'extraCols': ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CUMUN', 'NCA', 'NPRO', 'NMUN', 'nCCA', 'nCPRO',
                                    'nCMUN', 'nCDIS', 'nCUMUN', 'nCUDIS'], 'nSUP': 'MUN'},
              'SEC': {'claveAgr': 'CUSEC',
                      'extraCols': ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CUMUN', 'CUDIS', 'NCA', 'NPRO', 'NMUN', 'nCCA',
                                    'nCPRO', 'nCMUN', 'nCDIS', 'nCUMUN', 'nCUDIS', 'nCUSEC'], 'nSUP': 'DIS'}
              }


def leeContornoSeccionesCensales(fname):
    baregdf = gpd.read_file(fname)

    # Pasada a limpio (hasta que lo arreglen en INE, reportado).
    # Esto es feo pero dado que sólo existe un fichero de contornos da un poco igual
    baregdf.loc[baregdf.CCA == "16", 'NCA'] = "País Vasco"
    baregdf.loc[baregdf.CPRO == "20", 'NPRO'] = "Gipuzkoa"
    baregdf.loc[baregdf.CUMUN == "20069", 'NMUN'] = "Donostia-San Sebastián"
    baregdf.loc[baregdf.CUMUN == "28092", 'NMUN'] = "Móstoles"

    # Control de calidad de etiquetas (ya corregido en       leeContornoSeccionesCensales
    # Encuentra nombres mal puestos
    # reCA = pd.DataFrame(gdf.groupby('CCA').apply(lambda x: x['NCA'].value_counts()))
    # reCA[(reCA.droplevel(1,axis=0).index.duplicated(keep=False))]
    #
    # reProv = gdf.groupby('CPRO').apply(lambda x: x['NPRO'].value_counts())
    # reProv[(reProv.droplevel(1,axis=0).index.duplicated(keep=False))]
    #
    # reMun = gdf.groupby('CUMUN').apply(lambda x: x['NMUN'].value_counts())
    # reMun[(reMun.droplevel(1,axis=0).index.duplicated(keep=False))]

    result = creaNumCols(baregdf, ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CSEC', 'CUMUN', 'CUDIS', 'CUSEC'])

    result['numcell'] = 1  # Se usa para contar secciones para agrupación mayor

    return result


def checkList(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def agrupaContornos(df, claveAgr, extraCols=None):
    auxClave = claveAgr if checkList(claveAgr) else [claveAgr]
    merged = df[auxClave + ['geometry', 'numcell']].dissolve(by=claveAgr, aggfunc=sum)

    # Si no hay que poner etiqueta, our job is done
    if extraCols is None:
        return merged

    auxExtra = extraCols if checkList(extraCols) else [extraCols]

    resto = df[auxClave + auxExtra].drop_duplicates().set_index(auxClave)

    result = merged.join(resto)

    return result


def creaNumCols(df, cols):
    auxCols = cols if checkList(cols) else [cols]
    result = df.reset_index()

    indexCol = None
    if isinstance(df.index, pd.core.indexes.base.Index):
        indexCol = df.index.name
    elif isinstance(df.index, pd.core.indexes.multi.MultiIndex):
        indexCol = df.index.names

    for c in auxCols:
        if c in result.columns:
            result['n' + c] = pd.to_numeric(result[c])

    return result.set_index(indexCol) if indexCol else result


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


def preparaAgrupacionConts(df):
    """

    :param df:
    :return:
    """
    result = {k: resultBase[k] for k in secNIV}
    # Prepara los agregados de contornos y datos auxiliares
    for k in secNIV:
        aux = agrupaContornos(df, claveAgr=result[k]['claveAgr'], extraCols=result[k]['extraCols'])
        aux['idx'] = range(len(aux))

        if result[k].get('nSUP', None):
            supLevel = result[k]['nSUP']
            kSupLevel = result[supLevel]['claveAgr']

            result[supLevel]['sup2k'] = aux.reset_index().groupby(kSupLevel)[result[k]['claveAgr']].apply(list)

        result[k]['contAgr'] = aux

    return result


def creaMatrizRec(contAggsEst, listaNiv):
    """
    A partir de un geodataframe devuelve un dataframe con la matriz de adyacencias entre sus filas
    :param df: geodataframe (geopandas)
    :param clave: columna del dataframe original que se va a usar como clave (filas y columnas del DF resultante)
    :param matricesMR: diccionario de pares { columnaDF:matrizADJ } para reducir cálculos. Ej: 2 provincias no pueden
                       ser adyacentes si sus respectivas CCAA no lo son
    :return: dataframe con la matriz resultante

    """

    resMat = encuentraVecinos(listaNiv[0], listaNiv[1:], contAggsEst, contAggsEst[listaNiv[0]]['contAgr'].index,
                              contAggsEst[listaNiv[0]]['contAgr'].index)

    resDF = vecinos2DF(resMat, contAggsEst)

    return resDF


def encuentraVecinos(cat, restoCats, datos, idx1, idx2, intra=True):
    """

    :param cat:
    :param restoCats:
    :param datos:
    :param idx1:
    :param idx2:
    :param intra:
    :return:
    """
    result = {k: [] for k in ([cat] + restoCats)}

    print("encuentraVecinos: cat %s rem cats: %i ( %s ) parejas: %i * %i" % (
        cat, len(restoCats), restoCats, len(idx1), len(idx2)))
    for kx, ky in product(idx1, idx2):

        dx = datos[cat]['contAgr'].loc[kx]
        dy = datos[cat]['contAgr'].loc[ky]

        if intra and (dy.idx < dx.idx):
            continue

        gx = dx.geometry
        gy = dy.geometry

        if (kx == ky) or gx.intersects(gy):
            result[cat].append((dx['idx'], dy['idx']))
            if (kx != ky):
                result[cat].append((dy['idx'], dx['idx']))

            if restoCats:
                deeperResult = encuentraVecinos(restoCats[0], restoCats[1:], datos, datos[cat]['sup2k'].loc[kx],
                                                datos[cat]['sup2k'].loc[ky], intra=(kx == ky))

                for k in deeperResult:
                    result[k] += deeperResult[k]

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
    matricesAdj = creaMatrizRec(contAgs,['CCAA', 'PRO', 'MUN', 'DIS', 'SEC'])

    


pass


