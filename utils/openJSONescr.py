import argparse
import json
import os.path
import re
from datetime import datetime
from collections import defaultdict
from babel.numbers import parse_decimal


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


def partido2dict(datopartido):
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

    return result


def process_cli_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--base-dir', dest='basedir', action='store', help='location of test results',
                        required=True, default=".")
    parser.add_argument('-o', '--output-file', dest='destfile', help='output file name', required=False)
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

    result['ambitos'] = {x['c']: x for x in data['ambitos']['co']}
    for amb in result['ambitos']:
        result['ambitos'][amb].update(ambito2campos(amb))

    for per in data['partidos']['co']:
        result['partidos'][per] = {p['codpar']: p for p in data['partidos']['co'][per]}

    return result


def processResultados(fname, year=2019):
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
        'pexclus': '3,00%', Umbral de exclusion (para entrar a reparto una cand debe tener >= pexc * validos (EN CIRCUNSCRIPCION)
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
    data = readJSONfile(fname)
    result = {'totales': {'ant': {}, 'act': {}}, 'partidos': {'ant': {}, 'act': {}}}

    result['amb'] = data['amb']
    result['numact'] = data['numact']

    result.update(ambito2campos(data['amb']))
    result['datesample'] = mdhm2timestamp(data['mdhm'], year=year)

    for k in data['totales']:
        result['totales'][k] = totales2dict(data['totales'][k])

    for part in data['partotabla']:
        for per in part:
            datopart = part[per]
            if datopart['codpar'] == '0000':
                continue
            result['partidos'][per][datopart['codpar']] = partido2dict(datopart)

    return result


def processResultsDir(dirbase):

    result = defaultdict(dict)

    for d in os.listdir(dirbase):
        subdir = os.path.join(dirbase,d)
        if not os.path.isdir(subdir):
            continue

        for fich in os.listdir(subdir):

            if not fich.endswith('.json'):
                continue
            file2work = os.path.join(subdir, fich)

            aux = processResultados(file2work)
            aux['filename'] = file2work
            result[aux['amb']][aux['datesample']] = aux

    return result


# def table_results_to_dict(tab):
#     result = []
#     rows = tab.findAll('tr')
#
#     header = [x.text for x in rows[0].findAll('th')]
#     for row in rows[1:]:
#         data = [x.text for x in row.findAll('td')]
#         aux = dict(zip(header, data))
#         result.append(aux)
#
#     return result
#
#
# def process_test_dir(dirresults):
#
#     result = dict()
#
#     testresults_file = os.path.join(dirresults, 'results.html')
#     json_files = {
#         'config': os.path.join(dirresults, 'api_config.json'),
#         'mmech': os.path.join(dirresults, 'consolidatedConf.json'),
#         'toolium': os.path.join(dirresults, 'toolium_config.json'),
#         'environment': os.path.join(dirresults, 'environment_config.json')
#     }
#
#     if not os.path.isfile(testresults_file):
#         print("Directory '%s' does not contain a results file '%s'" % (dirresults, 'results.html'))
#         return None
#
#     result['timers'] = process_results_html(testresults_file)
#
#     for key, conffile in json_files.items():
#
#     return result
#
#
# def infer_test_params_from_dir(dirname):
#     # 10u_24h_1_1ps_results_2019.04.05_09.14.10_month
#     PATTERN = r"^(?P<concurrent_users>\d+)u_(?P<hour_interval>\d+)h_(?P<whatever>.*)_results_(?P<date>\d{4}\.\d{2}\.\d{2}_\d{2}\.\d{2}\.\d{2})_(?P<day_interval>\w+)"
#
#     m = re.match(PATTERN, dirname)
#
#     return m.groupdict()
#
#

def main():


    args = process_cli_arguments()

    if not os.path.isdir(args['basedir']):
        print("Provided argument -d '%s' is not a directory" % args['basedir'])
        exit(1)

    sourcedir = os.path.relpath(args['basedir'])

    allMerged=processResultsDir(sourcedir)


    if args['destfile']:
        outputfile = args['destfile']
    else:
        outputfile = os.path.join(results_dir, "combined_results.csv")

    for d in os.listdir(results_dir):
        dirtomatch = os.path.join(results_dir, d)

        if not os.path.isdir(dirtomatch):
            print("Ignoring %s" % dirtomatch)
            continue

        print("Accepting %s" % dirtomatch)

        procdir = process_test_dir(dirtomatch)

        if procdir:
            results[d] = procdir


if __name__ == "__main__":
    main()

    final_data = prepare_data_for_csv(results, include_all_trans=args['includeAllTr'])

    fieldorder = ['concurrent_users', 'hour_interval', 'day_interval', 'flat', 'label', 'measure', 'script_name',
                  'test:api_server', 'api:release', 'api:backend_profile', 'api:backend_audiences', 'api:els:hosts',
                  'api:els:index', 'test_start', 'duration', 'transactions', 'errors', u'count', u'avg', u'stdev',
                  u'min', u'max', u'80pct', u'90pct', u'95pct']

    with open(outputfile, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=fieldorder)

        writer.writeheader()
        for r in final_data:
            finalrow = {k: v for k, v in r.items() if k in fieldorder}
            writer.writerow(finalrow)
