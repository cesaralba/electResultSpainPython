import numpy as np

from utils.deepdict import serie2deepdict, index2deepdict
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


def procesaGrCircs(df, claveDisc=None, trads=None):
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
