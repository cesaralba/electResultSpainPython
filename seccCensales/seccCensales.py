import logging
from argparse import ArgumentParser
from builtins import object
from collections.abc import Iterable
from itertools import product
from pickle import dump, load
from time import time

import geopandas as gpd
import pandas as pd
import psutil
from scipy.sparse import dok_matrix

from utils.operations.retocaDF import applyDFtransforms, passDFvalidators, applyDFerrorFix
from utils.zipfiles import fileOpener
from seccCensales.operDF import manipSecCensales, validacionesSecCensales
from seccCensales.fixINE import fixesINE

#Fuente de datos:

secNIV = ['CCAA', 'PRO', 'MUN', 'DIS', 'SEC']
# secNIV = ['CCAA', 'PRO']

resultBase = {'PAIS': {'claveAgr': None, 'abrev': 'p'},
              'CCAA': {'claveAgr': 'CCA', 'extraCols': ['NCA', 'nCCA'], 'abrev': 'a'},
              'PRO': {'claveAgr': 'CPRO', 'extraCols': ['CCA', 'NCA', 'NPRO', 'nCCA', 'nCPRO'], 'abrev': 'r'},
              'MUN': {'claveAgr': 'CUMUN', 'abrev': 'm',
                      'extraCols': ['CCA', 'CPRO', 'CMUN', 'NCA', 'NPRO', 'NMUN', 'nCCA', 'nCPRO', 'nCMUN', 'nCUMUN']},
              'DIS': {'claveAgr': 'CUDIS', 'abrev': 'd',
                      'extraCols': ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CUMUN', 'NCA', 'NPRO', 'NMUN', 'nCCA', 'nCPRO',
                                    'nCMUN', 'nCDIS', 'nCUMUN', 'nCUDIS']},
              'SEC': {'claveAgr': 'CUSEC', 'abrev': 's',
                      'extraCols': ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CUMUN', 'CUDIS', 'NCA', 'NPRO', 'NMUN', 'nCCA',
                                    'nCPRO', 'nCMUN', 'nCDIS', 'nCUMUN', 'nCUDIS', 'nCUSEC']}
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


def leeContornoSeccionesCensales(fname):
    timeIn = time()
    logger.info("Loading SC file: %s", fname)

    baregdf = gpd.read_file(fname)

    primPass = passDFvalidators(baregdf,validacionesSecCensales)
    if primPass:
        logger.error(f"Fichero: {fname}. Errores detectados. Aplicando arreglos.{primPass}")
        fixedDF = applyDFerrorFix(baregdf, fixesINE)
        segPass = passDFvalidators(baregdf,validacionesSecCensales)
        if segPass:
            logger.error(f"Fichero: {fname}. Errores detectados {segPass}")
            raise ValueError(f"Problemas en fichero {fname}")
    else:
        fixedDF = baregdf
    result = applyDFtransforms(fixedDF, manipSecCensales)
    # result = creaNumCols(baregdf, ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CSEC', 'CUMUN', 'CUDIS', 'CUSEC'])
    result['numcell'] = 1  # Se usa para contar secciones para agrupación mayor

    timeOut = time()
    durac = timeOut - timeIn
    logger.info("Loaded SC file: %s. %.3f", fname, durac)

    return result


def agrupaContornos(df, claveAgr, extraCols=None):
    auxClave = claveAgr if checkList(claveAgr) else [claveAgr]
    merged = df[set(auxClave + ['geometry', 'numcell'])].dissolve(by=claveAgr, aggfunc=sum)

    # Si no hay que poner etiqueta, our job is done
    if extraCols is None:
        return merged

    auxExtra = extraCols if checkList(extraCols) else [extraCols]

    resto = df[auxClave + auxExtra].drop_duplicates().set_index(auxClave)

    result = merged.join(resto)

    return result


def creaNumCols(df, cols):
    auxCols = cols if checkList(cols) else [cols]

    indexCol = None
    if isinstance(df.index, pd.core.indexes.base.Index):
        indexCol = df.index.name
    elif isinstance(df.index, pd.core.indexes.multi.MultiIndex):
        indexCol = df.index.names

    result = df.reset_index()

    for c in auxCols:
        if c in result.columns:
            result['n' + c] = pd.to_numeric(result[c])

    return result.set_index(indexCol) if indexCol else result


def checkList(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, str)


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

    for kx, ky in product(idx1, idx2):

        dx = datos.contornos[cat]['contAgr'].loc[kx]
        dy = datos.contornos[cat]['contAgr'].loc[ky]

        if intra and (dy.idx < dx.idx):
            continue

        gx = dx.geometry
        gy = dy.geometry

        if (kx == ky) or gx.intersects(gy):
            result[cat].append((dx['idx'], dy['idx']))

            if restoCats:
                deeperResult = encuentraVecinos(restoCats[0], restoCats[1:], datos,
                                                datos.contornos[cat]['sup2k'].loc[kx],
                                                datos.contornos[cat]['sup2k'].loc[ky], intra=(kx == ky))

                for k in deeperResult:
                    result[k] += deeperResult[k]

    return result


def vecinos2DF(resVecinosList, secCensales, listaNiv):
    """
    A partir del resultado de encuentraVecinos crea un diccionario de dataframes dispersos con las adyacencias en el
    nivel correspondiente

    :param resVecinos: resultado de encuentraVecinos
    :param secCensales: resultado de preparaAgrupacion
    :return: diccionario de DF dispersos. Los DF corresponden a las adyacencias al nivel indicado y tienen como índice
    el de los DF en datos.
    """

    nivSet = set()
    auxMat = {
        k: dok_matrix((len(secCensales.contornos[k]['contAgr']), len(secCensales.contornos[k]['contAgr'])), dtype=bool)
        for k
        in secCensales.claveNiveles}
    result = dict()

    for resVecinos in resVecinosList:
        for niv, sols in resVecinos.items():
            nivSet.add(niv)
            for s in sols:
                auxMat[niv][s[0], s[1]] = True
                if s[0] != s[1]:
                    auxMat[niv][s[1], s[0]] = True

    for niv in nivSet:
        auxDF = pd.DataFrame.sparse.from_spmatrix(auxMat[niv])
        auxDF.index = secCensales.contornos[niv]['contAgr'].index
        auxDF.columns = secCensales.contornos[niv]['contAgr'].index
        secCensales.contornos[niv]['matAdj'] = auxDF
        result[niv] = auxDF

    return result


# Solución con JobLib
def creaMatrizRecJL(seccCensales, listaNiv, JLconfig=None):
    """
    A partir de un geodataframe devuelve un dataframe con la matriz de adyacencias entre sus filas
    :param df: geodataframe (geopandas)
    :param clave: columna del dataframe original que se va a usar como clave (filas y columnas del DF resultante)
    :param matricesMR: diccionario de pares { columnaDF:matrizADJ } para reducir cálculos. Ej: 2 provincias no pueden
                       ser adyacentes si sus respectivas CCAA no lo son
    :return: dataframe con la matriz resultante

    """

    if not listaNiv:
        logging.info("No hay niveles para calcular. Saliendo.")
        return {}

    from joblib import Parallel, delayed

    def encuentraVecinosJL(kx, ky):
        cat = listaNiv[0]
        restoCats = listaNiv[1:]
        result = {k: [] for k in ([cat] + restoCats)}

        dx = seccCensales.contornos[cat]['contAgr'].loc[kx]
        dy = seccCensales.contornos[cat]['contAgr'].loc[ky]

        if (dy.idx < dx.idx):
            return result

        if (kx == ky) or dx.geometry.intersects(dy.geometry):
            result[cat].append((dx['idx'], dy['idx']))

            if restoCats:
                indx = seccCensales.contornos[cat]['sup2k'].loc[kx]
                indy = seccCensales.contornos[cat]['sup2k'].loc[ky]
                deeperResult = encuentraVecinos(restoCats[0], restoCats[1:], seccCensales, indx, indy, intra=(kx == ky))
                for k in deeperResult:
                    result[k] += deeperResult[k]

        return result

        pass

    if JLconfig is None:
        JLconfig = {}
    configParallel = {'verbose': 20}
    # TODO: Control de calidad con los parámetros
    configParallel['n_jobs'] = JLconfig.get('nproc', 2)
    configParallel['prefer'] = JLconfig.get('joblibmode', 'threads')

    indexNiv = seccCensales.contornos[listaNiv[0]]['contAgr'].index
    print(indexNiv)

    resultJL = Parallel(**configParallel)(delayed(encuentraVecinosJL)(x, y) for x, y in product(indexNiv, indexNiv))

    resDF = vecinos2DF(resultJL, seccCensales, listaNiv)

    return resDF


class SeccionesCensales(object):
    def __init__(self, fname, niveles=secNIV):
        self.fname = fname
        auxClaveNiveles = [k for k in resultBase if k in niveles]

        if len(auxClaveNiveles) == 0:
            raise ValueError(f'Niveles suministrados {niveles} no están entre los aceptables {secNIV}')
        self.claveNiveles = auxClaveNiveles

        self.contornos = {k: resultBase[k] for k in self.claveNiveles}
        self.gdf = None

    def lazyLoad(self, permisivo=False):
        if self.gdf is None:
            self.gdf = leeContornoSeccionesCensales(self.fname)
            # self.controlCalidad(permisivo)

        return self.gdf

    def controlCalidad(self, permisivo=False):

        nomPairs = [('CCA', 'NCA'), ('CPRO', 'NPRO'), ('CUMUN', 'NMUN'), ('CUMUN', 'CMUN'), ('CUDIS', 'CDIS'),
                    ('CUSEC', 'CSEC')]

        comps = [(c, n) for c, n in nomPairs if self.gdf[c].nunique() != len(self.gdf[[c, n]].drop_duplicates())]

        if comps:
            result = False
            # problemPairs = [str(pair) for pair, compRes in zip(nomPairs, comps) if not compRes]
            logger.error("Control de calidad: fichero %s tiene problemas en los nombres: %s", self.fname,
                         ",".join(map(str, comps)))
            for c, n in comps:
                pairCounts = self.gdf[[c, n]].drop_duplicates()[c].value_counts()
                claveProblem = pairCounts[pairCounts > 1].reset_index()['index']
                for cp in claveProblem:
                    nombresProb = self.gdf[self.gdf[c] == cp][n].value_counts().to_dict()
                    logger.error("Problemas en datos de origen. %s:%s -> %s:%s", c, cp, n, nombresProb)

            if callable(permisivo):
                # TODO: funcion que corrija
                pass
            elif permisivo:
                logger.info("Modo permisivo: ignorando errores en datos suministrados")
                result = True
            else:
                logger.info("Modo no permisivo: no puedo seguir si hay errores en datos suministrados")
                raise ValueError("Dataframe '%s' contiene errores. Bye" % self.fname)
        else:
            result = True

        return result

    def agrupaCosas(self, permisivo=False):

        self.lazyLoad(permisivo=permisivo)

        for k in self.claveNiveles[::-1]:
            timeIn = time()
            logger.info("Agrupando nivel %s", k)
            if 'contAgr' in self.contornos[k]:
                logger.info("Nivel %s ya hecho. Paso al siguiente.", k)
                continue
            # Calcula cosas relativas al nivel inferior
            prevCont = self.gdf
            prevK = 'ORIG'
            for auxK in self.claveNiveles[::-1]:
                if auxK == k:
                    logger.debug("Nivel inferior: %s", prevK)
                    break
                prevCont = self.contornos[auxK]['contAgr']
                prevK = auxK

            if 'claveAgr' in self.contornos[k] and self.contornos[k]['claveAgr']:
                aux = agrupaContornos(prevCont, claveAgr=self.contornos[k]['claveAgr'],
                                      extraCols=self.contornos[k].get('extraCols', None))
            else:
                auxDF = pd.DataFrame(data=['PAIS'] * len(prevCont), index=prevCont.index, columns=['auxKey'])
                aux = agrupaContornos(prevCont.join(auxDF), claveAgr='auxKey',
                                      extraCols=self.contornos[k].get('extraCols', None))
            aux['idx'] = range(len(aux))
            self.contornos[k]['contAgr'] = aux

            # Calcula cosas relativas al nivel superior
            supK = None
            for auxK in self.claveNiveles:
                if auxK == k:
                    logger.debug("Nivel superior: %s", supK)
                    break
                supK = auxK

            if supK:
                kSupLevel = resultBase[supK].get('claveAgr', None)
                curKagr = self.contornos[k]['claveAgr']
                self.contornos[supK]['nInf'] = k
                self.contornos[k]['nSup'] = supK

                if kSupLevel in aux.reset_index().columns:
                    self.contornos[supK]['sup2k'] = aux.reset_index().groupby(kSupLevel)[curKagr].apply(list)
                else:
                    self.contornos[supK]['sup2k'] = pd.Series([aux.index.to_list()], index=['PAIS'])
            timeOut = time()
            durac = timeOut - timeIn

            logger.info("Agrupado nivel %s. Entran: %i. Salen %i. Tiempo %.3f", k, len(prevCont),
                        len(self.contornos[k]['contAgr']), durac)

    def calculaMatrizAdyacencia(self, permisivo=False, JLconfig=None):

        self.agrupaCosas(permisivo=permisivo)

        listaNiv = [niv for niv in self.contornos if
                    (len(self.contornos[niv]['contAgr']) > 1 and 'matAdj' not in self.contornos[niv])]

        # result = creaMatrizRec(self, listaNiv)

        result = creaMatrizRecJL(self, listaNiv, JLconfig=JLconfig)

        for niv, mat in result.items():
            self.contornos[niv]['matAdj'] = mat

        return result

    def graba(self, fname):
        handler = fileOpener(fname, "wb")

        timeIn = time()
        logger.info("Saving file: %s", fname)

        dump(self, handler)
        handler.close()

        timeOut = time()
        durac = timeOut - timeIn
        logger.info("Saved file: %s. %.3f", fname, durac)

    @classmethod
    def carga(self, fname):
        with fileOpener(fname, "rb") as handler:
            obj = load(handler)
        return obj
        pass


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

def procesaArgumentos():
    JOBLIBCHOICES = ['threads', 'processes']

    def ayudaNiveles():
        result = ", ".join([f"{k} -> {resultBase[k].get('abrev')}" for k in resultBase])
        return result

    parser = ArgumentParser(description="Procesa fichero de secciones censales del INE")

    parser.add_argument('-i', '--input', dest='infile', action='store', type=str, required=True,
                        help='Fichero de entrada con secciones censales')
    parser.add_argument('-o', '--output', dest='outfile', action='store', type=str, required=True,
                        help='Fichero de salida')
    parser.add_argument('-n', '--niveles', dest='niveles', action='store', type=str, default='armds',
                        help="Niveles a procesar: " + ayudaNiveles(), required=False)
    parser.add_argument('-a', '--adyacencia', dest='adyacencia', action='store_true',
                        help="Calcula matriz de adyacencia")
    parser.add_argument('-p', '--permisivo', dest='permisivo', action='store_true',
                        help="Acepta errores en dataframe")

    parser.add_argument('-j', '--numjobs', dest='nproc', action='store', type=int, required=False, default=2,
                        help='Numero de procesos')
    parser.add_argument('-t', '--joblibmode', dest='joblibmode', choices=JOBLIBCHOICES, required=False,
                        default='threads', help='Modo de procesamiento paralelo')

    args = parser.parse_args()

    return args


def procesaArgNiveles(nivParam):
    result = []

    paramSet = set(list(nivParam))
    for k in resultBase:
        if resultBase[k]['abrev'] in paramSet:
            result.append(k)
            paramSet.remove(resultBase[k]['abrev'])

    if paramSet:
        logger.error("Niveles desconocidos en parámetro -n")

    return result


def procesaArgsJobLib(args):
    result = dict()

    result['nproc'] = min(args.nproc, max(psutil.cpu_count() - 1, 1))
    result['joblibmode'] = args.joblibmode

    return result


if __name__ == "__main__":
    args = procesaArgumentos()

    nivelesReq = procesaArgNiveles(args.niveles)

    clsSC = SeccionesCensales(fname=args.infile, niveles=nivelesReq)

    if args.adyacencia:
        clsSC.calculaMatrizAdyacencia(args.permisivo, JLconfig=procesaArgsJobLib(args))
    else:
        clsSC.agrupaCosas(args.permisivo)

    clsSC.graba(args.outfile)
pass
