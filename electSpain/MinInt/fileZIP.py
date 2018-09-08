
from utils.zipfiles import unzipfile
from pandas import read_fwf
from io import StringIO
from collections import defaultdict

from electSpain.MinInt.fileDescriptions import fieldDescriptions, tipoEleccion, tipoFichero

import re

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
    tipoCols = {x[1]: x[2] for x in fileDescr}

    return anchos, nombreCols, tipoCols


def readPandaFWF(ziphandle, filenameInfo, elType, fileType):
    anchos, colnames, tipos = tipoFich2fwfParams(fileType, fieldDescriptions)

    try:
        filename = filenameInfo['ficheros'][elType][fileType]
    except KeyError:
        print("No existe el fichero '%s'(%s) '%s'(%s) " % (elType, tipoEleccion[elType],
                                                           fileType, tipoFichero[fileType]))
        return

    data = StringIO(ziphandle.read(filename).decode('cp1252'))

    try:
        result = read_fwf(data, header=None, widths=anchos, names=colnames, dtype=tipos,
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
        result['datosCandidatura'] = readPandaFWF(zh, files, elType, '03')

    if setInfo['adjuntaFich04']:
        result['datosCandidatos'] = readPandaFWF(zh, files, elType, '04')

    if setInfo['adjuntaFich05']:
        result['datosMunic'] = readPandaFWF(zh, files, elType, '05')

    if setInfo['adjuntaFich06']:
        result['datosMunicResult'] = readPandaFWF(zh, files, elType, '06')

    if setInfo['adjuntaFich07']:
        result['datosSupMunic'] = readPandaFWF(zh, files, elType, '07')

    if setInfo['adjuntaFich08']:
        result['datosSupMunicResult'] = readPandaFWF(zh, files, elType, '08')

    if setInfo['adjuntaFich09']:
        result['datosMesas'] = readPandaFWF(zh, files, elType, '09')

    if setInfo['adjuntaFich10']:
        result['datosMesasResult'] = readPandaFWF(zh, files, elType, '10')

    if setInfo['tipoElec'] == '04':
        if setInfo['adjuntaFich1104']:
            result['datosMunicPeq'] = readPandaFWF(zh, files, elType, '11')

        if setInfo['adjuntaFich1204']:
            result['datosMunicPeqResult'] = readPandaFWF(zh, files, elType, '12')

    if setInfo['adjuntaFich0510']:
        result['datosDipMunic'] = readPandaFWF(zh, files, '10', '05')

    if setInfo['adjuntaFich0610']:
        result['datosDipMunicResult'] = readPandaFWF(zh, files, '10', '06')

    if setInfo['adjuntaFich0710']:
        result['datosDipSupMunic'] = readPandaFWF(zh, files, '10', '07')

    if setInfo['adjuntaFich0810']:
        result['datosDipSupMunicResult'] = readPandaFWF(zh, files, '10', '08')

    # Elimina entradas que han dado problema con la carga
    return {clave: result[clave] for clave in result if result[clave] is not None}


################################################################################################################

if __name__ == "__main__":
    readFileZIP('/home/calba/Datasets/Elec/Congreso/02201512_MESA.zip')
