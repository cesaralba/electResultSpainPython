from collections.abc import Iterable
from itertools import product

import geopandas as gpd
import numpy as np
import pandas as pd


def leeContornoSeccionesCensales(fname):
    result = gpd.read_file(fname)

    # Pasada a limpio (hasta que lo arreglen en INE, reportado).
    # Esto es feo pero dado que sólo existe un fichero de contornos da un poco igual
    result.loc[result.CCA == "16", 'NCA'] = "País Vasco"
    result.loc[result.CPRO == "20", 'NPRO'] = "Gipuzkoa"
    result.loc[result.CUMUN == "20069", 'NMUN'] = "Donostia-San Sebastián"
    result.loc[result.CUMUN == "28092", 'NMUN'] = "Móstoles"

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

    result['numcell'] = 1  # Se usa para contar secciones para agrupación mayor

    return result


def agrupaContornos(df, claveAgr, extraCols=None):
    merged = df.dissolve(by=claveAgr, aggfunc=sum)

    # Si no hay que poner etiqueta, our job is done
    if extraCols is None:
        return merged

    auxClave = claveAgr if isinstance(claveAgr, Iterable) else [claveAgr]
    auxExtra = extraCols if isinstance(extraCols, Iterable) else [extraCols]

    resto = df[auxClave + auxExtra].drop_duplicates().set_index(auxClave)

    result = merged.join(resto)

    return result


def creaNumCols(df, cols):
    auxCols = cols if isinstance(cols, Iterable) else [cols]
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
