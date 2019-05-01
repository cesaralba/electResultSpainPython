import argparse
import json
import os.path


# from csv import DictWriter


def process_cli_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--base-dir', dest='basedir', action='store', help='location of test results',
                        required=True)
    parser.add_argument('-o', '--output-file', dest='destfile', help='output file name', required=False)

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

    for per in data['partidos']['co']:
        result['partidos'][per] = {p['codpar']: p for p in data['partidos']['co'][per]}

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

if __name__ == "__main__":

    results = dict()
    args = process_cli_arguments()

    if not os.path.isdir(args['basedir']):
        print("Provided argument -d '%s' is not a directory" % args['basedir'])
        exit(1)

    results_dir = os.path.join(args['basedir'], 'results')

    if not os.path.exists(results_dir) or not os.path.isdir(results_dir):
        print("Provided argument -d '%s' does not contain a results directory '%s'" % (args['basedir'], results_dir))
        exit(1)

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
