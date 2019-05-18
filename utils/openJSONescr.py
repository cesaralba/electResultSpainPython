import argparse
import json
import os.path
import re
from collections import defaultdict, Counter
from datetime import datetime

import numpy as np
import pandas as pd
from babel.numbers import parse_decimal, decimal


def ambito2campos(codambito):
    REambito = r'(?P<codAut>\d{2})(?P<codProv>\d{2})(?P<codMun>\d{3})(?P<codDistr>\d{2})(?P<codSeccion>\d{2})?'

    ambMatch = re.match(REambito, codambito)

    result = ambMatch.groupdict()

    return {k: int(result[k]) for k in result if result[k] is not None}


def mdhm2timestamp(valmdhm, year=2019):
    REmdhm = r'(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})'

    ambMDHM = re.match(REmdhm, valmdhm)

    result = {k: int(v) for k, v in ambMDHM.groupdict().items()}
    result['year'] = year

    return datetime(**result)


def porc2val(valor):
    REnumero = r'(?P<valor>[+-]?\d+(,\d+)?)%'

    valMatch = re.match(REnumero, valor)

    result = valMatch.groupdict()

    return parse_decimal(result['valor'], locale='de')


def totales2dict(totales):
    keyToexclude = ['gancodpar']

    result = dict()

    for k in totales:
        if k in keyToexclude or k.startswith('d'):
            continue

        if k.startswith('p') and k != 'padron':
            result[k] = porc2val(totales[k])
            #    print("Porcentaje", k, totales[k])
        else:
            result[k] = int(totales[k])

    return result


def partido2dict(datopartido, periodo, nomenclator=None):
    keyToexclude = ['codpar']

    result = dict()

    for k in datopartido:
        if k in keyToexclude or k.startswith('d'):
            continue

        if k.startswith('p') and k != 'padron':
            result[k] = porc2val(datopartido[k])
            #    print("Porcentaje", k, totales[k])
        else:
            result[k] = int(datopartido[k])

    if nomenclator:
        result['siglapar'] = nomenclator['partidos'][periodo][datopartido['codpar']]['siglas']
    return result


def process_cli_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--base-dir', dest='basedir', action='store', help='location of test results',
                        required=True, default=".")
    parser.add_argument('-o', '--output-file', dest='destfile', help='output file name', required=False)
    parser.add_argument('-n', '--nomenclator', dest='nomenclator', help='lista de entidades (partidos, lugares...)',
                        required=False)
    parser.add_argument('-y', '--year', dest='year', help='year of election', required=False, default=2019)

    args = vars(parser.parse_args())

    return args


def readJSONfile(fname):
    with open(fname, "r") as file:
        data = json.load(file)

    return data


def processNomenclator(fname):
    """
    Lee el fichero de nomenclator (diccionario con todas las etiquetas, partidos, localidades (con contorno)

    nomenc.keys()
       'v': version
       'constantes':
            'level': {
                '1': 'ESPAÑA',
                '2': 'COMUNIDAD',
                '3': 'TRAMO MUNI. POBLACIÓN EN PAIS',
                '4': 'PROVINCIA',
                '5': 'TRAMO MUNI. POBLACIÓN EN COMUNIDAD',
                '6': 'COMARCA/ZONA',
                '7': 'VEGUERIA',
                '8': 'CIRCUNSCRIPCIÓN ELECTORAL',
                '9': 'TRAMO MUNI. POBLACIÓN EN CIRCUNSCRIPCION',
                '10': 'ISLA',
                '11': 'MUNICIPIO',
                '12': 'DISTRITO MUNICIPAL'
       'ambitos':
            co|se:
                    [{  'n': 'Total nacional', #Nombre ambito
                        'c': '99999999999', #Clave (la usa el fichero específico)
                        's': 'Total-nacional', #Nombre tuneado
                        'l': 1, #Tipo de ámbito (constantes[level])
                        'p': -1, #Padre
                        'i': 0, #i del array?
                        'r': 0, #Valor al que se va a referir
                        'h': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] #Hijos (valores de R)
                        }
                        ...


       'partidos':
            co|se: { act | ant } : []
                    {'codpar': '0013',
                     'siglas': 'C 21',
                     'nombre': 'CONVERXENCIA 21',
                     'color': '#FABE46',
                     'cir': '99',
                     'i': '10',
                     's': 'C-21'} #Sigla retocada

    Tras investigar en los resultados, el bueno es el CO. Los códigos que aparecen son los de CO, no los de SE


    :param fname:
    :return:
    """
    result = {'partidos': {}, 'ambitos': {}}

    data = readJSONfile(fname)

    result['constantes'] = {int(k): v for k, v in data['constantes']['level'].items()}
    result['ambitos'] = {x['c']: x for x in data['ambitos']['co']}
    for amb in result['ambitos']:
        result['ambitos'][amb].update(ambito2campos(amb))

    for per in data['partidos']['co']:
        result['partidos'][per] = {p['codpar']: p for p in data['partidos']['co'][per]}

    return result


def processResultados(fname, year=2019, nomenclator=None):
    """
    'amb': codigo de la región
    'numact': versión del cambio
    'mdhm': hora del cambio
    'totales': act|ant: datos generales
        'metota': '60038', Mesas totales
        'mesesc': '6890', Mesas escrutadas
        'pmesesc': '11,48%', Porcentaje de ...
        'padron': '46722980', Padron (pob total)
        'centota': '34816238', Censo (pob derecho a voto) (votantes + abs)
        'cenes': '2381206', Censo escrutado
        'pcenes': '6,84%', Porc de ...
        'votant': '1746978', Votantes
        'pvotant': '73,37%', Porc de...
        'dpvotant': '+6,89%', Variación de porc de ...
        'absten': '634228', Abstencion
        'pabsten': '26,63%', Porc de Abst
        'dpabsten': '-6,89%', Var de porc de ...
        'votnul': '19062', Nulos
        'pvotnul': '1,09%', Porc de ..
        'dpvotnul': '+0,16%', Variación de porc...
        'votbla': '14281', Blancos
        'pvotbla': '0,83%', Porc de ...
        'dpvotbla': '+0,09%', Var de porc ...
        'votcan': '1713626', Votos a cands (votantes - blancos - nulos)
        'pvotcan': '99,17%', Porc de ...
        'dpvotcan': '-0,09%', Var de porc ...
        'votval': '1727907', Votos validos (vot a cand + blabcos)
        'pvotval': '98,91%', Porc de ...
        'dpvotval': '-0,16%', Var de porc de...
        'pexclus': '3,00%', Umbral de exclusion (para entrar a reparto una cand debe tener >= pexc * validos (EN CIRC)
        'carg': '350', (plazas a repartir)
        'gancodpar': '0096', codigo part ganador
    'ultimo': ultimo escaño asignado?
    'otros': el mitico resto de partidos. No tengo claro donde se usa
    'partotabla': lista de resultado de partidos
        {'act'|'ant': { 'codpar': '0042', #Codigo de partido (en nomenclator)
                        'vot': '5286', #Votos obtenidos en circ
                        'dvot': '+5286', #Diferencia de...
                        'pvot': '0,31%', #Porcentaje de votos
                        'dpvot': '+0,31%', #Dif de porc de ...
                        'carg': '0', #Escaños obtenidos
                        'dcarg': '0'}, #Dif de ...

    :param fname:
    :return:
    """

    auxTotales = {'ant': {}, 'act': {}}

    data = readJSONfile(fname)
    result = {'partidos': {'ant': {}, 'act': {}}}
    result['totales'] = {'ant': {}, 'act': {}}
    result['idTerr'] = {'amb': data['amb']}
    result['idTerr'].update(ambito2campos(data['amb']))
    if nomenclator:
        result['idTerr']['nombre'] = nomenclator['ambitos'][data['amb']]['n']
        result['idTerr']['tipo'] = nomenclator['constantes'][nomenclator['ambitos'][data['amb']]['l']]

    result['metadata'] = {'numact': data['numact'], 'datesample': mdhm2timestamp(data['mdhm'], year=year),
                          'filename': fname
                          }

    for k in data['totales']:
        auxTotales[k] = totales2dict(data['totales'][k])

    keysInAct = ['metota', 'centota']
    keysInBoth = []
    for k in auxTotales['act']:
        if k in auxTotales['ant']:
            keysInBoth.append(k)
        else:
            keysInAct.append(k)

    for k in keysInBoth:
        for per in auxTotales:
            result['totales'][per][k] = auxTotales[per][k]

    result['escrutinio'] = {k: auxTotales['act'][k] for k in keysInAct}

    for part in data['partotabla']:
        for per in part:
            datopart = part[per]
            if datopart['codpar'] == '0000':
                continue
            resultPart = partido2dict(datopart, per, nomenclator)
            if 'siglapar' in resultPart:
                labelPart = resultPart['siglapar']
                resultPart.pop('siglapar')
            else:
                labelPart = datopart['codpar']
            for cat, v in resultPart.items():
                if cat not in result['partidos'][per]:
                    result['partidos'][per][cat] = dict()
                result['partidos'][per][cat][labelPart] = v

    return result


def processResultsDir(dirbase, **kwargs):
    result = defaultdict(dict)

    for d in os.listdir(dirbase):
        subdir = os.path.join(dirbase, d)
        if not os.path.isdir(subdir):
            continue

        for fich in os.listdir(subdir):

            if not fich.endswith('.json'):
                continue
            file2work = os.path.join(subdir, fich)

            aux = processResultados(file2work, **kwargs)

            result[aux['idTerr']['amb']][aux['metadata']['datesample']] = aux

    return result


def getDictKeys(dictList):
    """
    Construye una lista de tuplas con claves para acceder a los valores de un dict anidado.
    :param dictList: LISTA (use .values() si es preciso) de diccionarios.
    :return: lista ordenada de tuplas con las claves
    """

    def recursFindKeys(datadict, keysf, result):
        for k in datadict:
            newkeys = keysf.copy()
            newkeys.append(k)

            if isinstance(datadict[k], dict):
                recursFindKeys(datadict[k], newkeys, result)
            else:
                result.append(newkeys)
        return result

    result = []
    keysfound = []

    for dictitem in dictList:
        result = recursFindKeys(dictitem, keysfound, result)

    return sorted(Counter(map(tuple, result)).keys())


def colNames2String(df, sep='_'):
    return [sep.join([field for field in col if field not in ('', np.nan)]) for col in df.columns.to_list()]


def deepDict(dic, keys):
    if dic is None:
        return None
    if len(keys) == 0:
        return dic
    if keys[0] not in dic and len(keys) >= 1:
        return None
        # dic[keys[0]] = None

    return deepDict(dic.get(keys[0], None), keys[1:])


def getColTypes(valList, keyList, typeConverter=None):
    if typeConverter is None:
        typeConverter = {str: np.object, int: pd.Int64Dtype(), decimal.Decimal: np.float64, datetime: np.datetime64}
    aux = defaultdict(lambda: defaultdict(int))
    result = dict()
    for val in valList:
        for k in keyList:
            v = deepDict(val, k)
            if v is None:
                continue
            aux[k][type(v)] += 1

    for k in aux:
        if len(aux[k]) != 1:
            raise ValueError("%s tiene más de 1 tipo (%i)" % (k, len(aux[k])))

        tipoConocido = list(aux[k].keys())[0]

        result[k] = typeConverter[tipoConocido]

    return result

def padTupleList(myList, padItem=None):
    """
    Pads each tuple of the list by appending padItem to make all items to have same length
    :param myList:
    :param padItem:
    :return:
    """
    aux = [(x,len(x)) for x in myList]
    maxLen= max([x[1] for x in aux])
    result = [tuple(list(t)+ [padItem]*(maxLen-l)) for t,l in aux]

    return result



def createDataframe(bigDict):
    auxAll = {(i, j): bigDict[i][j].copy()
              for i in bigDict.keys()
              for j in bigDict[i].keys()}

    # print([(i, j) for i in bigDict.keys() for j in bigDict[i].keys()])
    # print(list(auxAll.keys()))
    filAll = sorted(list(auxAll.keys()))
    colNames = getDictKeys(auxAll.values())

    data2PD = []

    for k in filAll:
        newRow = []
        for col in colNames:
            newVal = deepDict(auxAll[k], col)
            newRow.append(newVal)
        data2PD.append(newRow)

    colTypes = getColTypes(auxAll.values(),colNames)
    auxColTypes= [colTypes[x] for x in colNames]


    auxResult= pd.DataFrame(data=data2PD, index=pd.MultiIndex.from_tuples(filAll, names=['amb', 'tstamp']),
                        columns=pd.MultiIndex.from_tuples(colNames), copy=True)
    result= auxResult.astype(dict(zip(pd.MultiIndex.from_tuples(padTupleList(colNames,np.nan)),auxColTypes)),copy=True)

    return result



def df2Parquet(df, fname, sep='_'):
    cols2retype= dict()
    dfColRenamed = df.copy()
    dfColRenamed.columns = pd.Index(colNames2String(df, sep=sep))

    for c in dfColRenamed.columns:
        if not isinstance(dfColRenamed[c].dtype,pd.core.arrays.integer.Int64Dtype):
            continue
        if sum(dfColRenamed[c].isna()) > 0:
            cols2retype[c] = np.float64
        else:
            cols2retype[c] = np.int64

    if cols2retype:
        dfColRetyped=dfColRenamed.astype(cols2retype,copy=True)
    else:
        dfColRetyped=dfColRenamed

    dfColRetyped.to_parquet(fname)


def parquet2DF(fname, sep='_'):
    df = pd.read_parquet(fname)

    newCols = [tuple(x.split(sep)) for x in list(df.columns.to_list())]

    df.columns = pd.MultiIndex.from_tuples(newCols)

    return df


def main():
    args = process_cli_arguments()

    if not os.path.isdir(args['basedir']):
        print("Provided argument -d '%s' is not a directory" % args['basedir'])
        exit(1)

    sourcedir = os.path.relpath(args['basedir'])

    if 'nomenclator' in args and args['nomenclator'] is not None:
        if os.path.isfile(args['nomenclator']):
            nomenclatorData = processNomenclator(args['nomenclator'])
        else:
            nomenclatorData = None

    allMerged = processResultsDir(sourcedir, year=args['year'], nomenclator=nomenclatorData)
    allDF = createDataframe(allMerged)


if __name__ == "__main__":
    main()
