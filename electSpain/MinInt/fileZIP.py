import re
from collections import defaultdict
from io import StringIO

from pandas import read_fwf

from electSpain.MinInt.fileDescriptions import fieldDescriptions, tipoEleccion, tipoFichero, fieldTypes
from utils.zipfiles import unzipfile

minIntPattern = "(:?.*/)?(\d{2})(\d{2})(\d{2})(\d{2})\.DAT"


def getFilenames(fileList):
    result = dict()
    elTypeSet = set()
    elYear = set()
    elMes = set()
    result['ficheros'] = defaultdict(dict)

    for i in fileList:
        reData = re.match(minIntPattern, i)
        if reData:
            fileType = reData.group(2)
            elYear.add(reData.group(4))
            elMes.add(reData.group(5))

            elType = reData.group(3)
            if elType != '10':  # El tipo 10 es uno que se da en municipales y que tiene metadata (que no funciona)
                elTypeSet.add(elType)
            result['ficheros'][elType][fileType] = i

    # Comprueba la integridad de los ficheros
    if (len(elTypeSet) > 1) or (len(elYear) > 1) or (len(elMes) > 1):
        raise ValueError

    result['tipoEleccion'] = elTypeSet.pop()
    result['yearEleccion'] = elYear.pop()
    result['mesEleccion'] = elMes.pop()

    return result


def tipoFich2fwfParams(fileType, fileDescrs):
    fileDescr = fileDescrs[fileType]

    anchos = [x[0] for x in fileDescr]
    nombreCols = [x[1] for x in fileDescr]
    tipoCols = {x[1]: (x[2] if len(x) == 3 else fieldTypes[x[1]]) for x in fileDescr}

    converters = {nc: tc for nc, tc in tipoCols.items()}
    return anchos, nombreCols, tipoCols, converters


def readPandaFWF(ziphandle, filenameInfo, elType, fileType):
    anchos, colnames, tipos, convFunctions = tipoFich2fwfParams(fileType, fieldDescriptions)

    try:
        filename = filenameInfo['ficheros'][elType][fileType]
    except KeyError:
        print("No existe el fichero '%s'(%s) '%s'(%s) " % (elType, tipoEleccion[elType],
                                                           fileType, tipoFichero[fileType]))
        return

    data = StringIO(ziphandle.read(filename).decode('cp1252'))

    try:
        result = read_fwf(data, header=None, widths=anchos, names=colnames, converters=convFunctions,
                          iterator=False, index_col=False, debug=True, error_bad_lines=False,
                          warn_bad_lines=True)
    except ValueError as exc:
        print("Problemas leyendo el fichero %s: %s" % (filename, exc))
        return None

    return result



def readFileZIP(filename):
    result = dict()

    zh, zi = unzipfile(filename)

    files = getFilenames(zi)
    elType = files['tipoEleccion']

    setInfo = dict(readPandaFWF(zh, files, elType, '01').T[0])
    result['archInfo'] = setInfo

    if setInfo['adjuntaFich02']:
        result['elecInfo'] = dict(readPandaFWF(zh, files, elType, '02').T[0])

    if setInfo['adjuntaFich03']:
        aux = readPandaFWF(zh, files, elType, '03')
        result['datosCandidatura'] = aux

    if setInfo['adjuntaFich04']:
        aux = readPandaFWF(zh, files, elType, '04')
        print(aux.columns)
        result['datosCandidatos'] = aux

    if setInfo['adjuntaFich05']:
        aux = readPandaFWF(zh, files, elType, '05')
        print(aux.columns)
        result['datosMunic'] = aux

    if setInfo['adjuntaFich06']:
        aux = readPandaFWF(zh, files, elType, '06')
        print(aux.columns)
        result['datosMunicResult'] = aux

    if setInfo['adjuntaFich07']:
        aux = readPandaFWF(zh, files, elType, '07')
        print(aux.columns)
        result['datosSupMunic'] = aux

    if setInfo['adjuntaFich08']:
        aux = readPandaFWF(zh, files, elType, '08')
        print(aux.columns)
        result['datosSupMunicResult'] = aux

    if setInfo['adjuntaFich09']:
        aux = readPandaFWF(zh, files, elType, '09')
        print(aux.columns)
        result['datosMesas'] = aux

    if setInfo['adjuntaFich10']:
        aux = readPandaFWF(zh, files, elType, '10')
        print(aux.columns)
        result['datosMesasResult'] = aux

    if setInfo['tipoElec'] == '04':
        if setInfo['adjuntaFich1104']:
            aux = readPandaFWF(zh, files, elType, '11')
            print(aux.columns)
            result['datosMunicPeq'] = aux

        if setInfo['adjuntaFich1204']:
            aux = readPandaFWF(zh, files, elType, '12')
            print(aux.columns)
            result['datosMunicPeqResult'] = aux

    if setInfo['adjuntaFich0510']:
        aux = readPandaFWF(zh, files, '10', '05')
        print(aux.columns)
        result['datosDipMunic'] = aux

    if setInfo['adjuntaFich0610']:
        aux = readPandaFWF(zh, files, '10', '06')
        print(aux.columns)
        result['datosDipMunicResult'] = aux

    if setInfo['adjuntaFich0710']:
        aux = readPandaFWF(zh, files, '10', '07')
        print(aux.columns)
        result['datosDipSupMunic'] = aux

    if setInfo['adjuntaFich0810']:
        aux = readPandaFWF(zh, files, '10', '08')
        print(aux.columns)
        result['datosDipSupMunicResult'] = aux

    # Elimina entradas que han dado problema con la carga
    return {clave: result[clave] for clave in result if result[clave] is not None}


################################################################################################################

if __name__ == "__main__":
    readFileZIP('/home/calba/Datasets/Elec/Congreso/02201512_MESA.zip')
