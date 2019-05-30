import numpy as np
import pandas as pd

from .deepdict import serie2deepdict, index2deepdict
from .traducPartidos import traducPartidos, asignaTradsKS


def aplicaTraducciones(serie, trads):
    """
    Dado una serie (de PERIODO) con indice (['vot','carg'],[sigla de partido])
    :param df: DF (de PERIODO) con clave (['vot','carg'],[sigla de partido]). SIN el ['ant','act']
    :param trads: traducciones conocidas. Diccionario con
    :return:
    """

    result = serie.copy()

    dictSerie = serie2deepdict(serie)

    for cat in dictSerie:
        for porig in trads.listaPartidos():
            if porig in dictSerie[cat]:
                pdest = trads.traduce(porig)
                if pdest not in dictSerie[cat]:
                    raise ValueError("aplicaTraducciones: '%s' no está en '%s'" % (pdest, cat))

                result[cat][pdest] += result[cat][porig]
                result[cat][porig] -= result[cat][porig]

    return result


def consolidaPartidosIntraperiodo(df, claveDisc=None, trads=None):
    if trads is None:
        trads = {per: traducPartidos() for per in index2deepdict(df.partidos.columns)}

    if len(df) < 2:
        return trads

    # p* son porcentaje
    targKeys = [x for x in df.partidos.columns.to_list() if not x[1].startswith('p')]

    dfAux = df.partidos[targKeys].copy()

    # print(dfAux)
    # print(dfAux[df[claveDisc] != 99])

    # El codigo 99 (o 999) es la agregación
    filAgr = dfAux[df[claveDisc] == 99].sum(axis=0)
    filInd = dfAux[df[claveDisc] != 99].sum(axis=0)
    difFil = filAgr - filInd

    actDifs = difFil[difFil != 0]

    if (len(actDifs) == 0):
        return trads

    dictDif = serie2deepdict(actDifs)

    for per in dictDif:
        difPer = actDifs[per]
        trasTrad = aplicaTraducciones(difPer, trads[per])
        realDifs = trasTrad[trasTrad != 0]

        if len(realDifs) == 0:
            continue

        realPos = realDifs[realDifs > 0]
        realNeg = realDifs[realDifs < 0]

        for cat in ['vot']:
            if cat not in realPos:
                continue

            realPosCat = realPos[cat]
            realNegCat = realNeg[cat]

            tentTrad = asignaTradsKS(realPosCat, -realNegCat, trads[per])

            aux = aplicaTraducciones(actDifs[per].copy(), tentTrad)
            if len(aux[aux != 0]) != 0:
                raise Exception("Problem")
            else:
                trads[per] = tentTrad

    for per in trads:
        trads[per].eliminaTraduccionesIntermedias()

    return trads


def consolidaDFesp(df):
    trad = None
    for g in df.groupby(df.idTerr.codAut.iloc[:, 0]):
        aux = g[1].copy()

        trad = consolidaPartidosIntraperiodo(aux, claveDisc=('idTerr', 'codProv', np.nan, np.nan), trads=trad)

    trad = consolidaPartidosIntraperiodo(df[df.idTerr.codProv.iloc[:, 0] == 99],
                                         claveDisc=('idTerr', 'codAut', np.nan, np.nan), trads=trad)

    newCols = sorted(list(set([(per, cat, trad[per].traduce(sigla)) for per, cat, sigla in df.partidos])))
    auxResult = pd.DataFrame(data=np.zeros((df.shape[0], len(newCols)), dtype=np.float64),
                             columns=pd.MultiIndex.from_tuples(newCols), index=df.partidos.index, dtype=np.float)

    for c in df.partidos.columns:
        if c in auxResult:
            auxResult[c] += df.partidos[c].copy().fillna(0)
        else:
            tCol = (c[0], c[1], trad[c[0]].traduce(c[2]))
            auxResult[tCol] += df.partidos[c].copy().fillna(0)

    dfColsSinPartidos = [x for x in df.columns.to_list() if x[0] != 'partidos']

    auxResult = pd.concat([auxResult], keys=['partidos'], axis=1)
    result = pd.concat([df[dfColsSinPartidos], auxResult], axis=1)

    return result
