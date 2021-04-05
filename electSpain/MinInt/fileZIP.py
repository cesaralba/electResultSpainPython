import re
from collections import defaultdict
from io import StringIO

from pandas import read_fwf

from electSpain.MinInt.fileDescriptions import (
    fieldDescriptions,
    tipoEleccion,
    tipoFichero,
    fieldTypes,
    CPRO2CCA,
)
from utils.zipfiles import unzipfile

minIntPattern = r"(:?.*/)?(\d{2})(\d{2})(\d{2})(\d{2})\.DAT"


def getFilenames(fileList):
    result = dict()
    elTypeSet = set()
    elYear = set()
    elMes = set()
    result["ficheros"] = defaultdict(dict)

    for i in fileList:
        reData = re.match(minIntPattern, i)
        if reData:
            fileType = reData.group(2)
            elYear.add(reData.group(4))
            elMes.add(reData.group(5))

            elType = reData.group(3)
            if (
                    elType != "10"
            ):  # El tipo 10 es uno que se da en municipales y que tiene metadata (que no funciona)
                elTypeSet.add(elType)
            result["ficheros"][elType][fileType] = i

    # Comprueba la integridad de los ficheros
    if (len(elTypeSet) > 1) or (len(elYear) > 1) or (len(elMes) > 1):
        raise ValueError

    result["tipoEleccion"] = elTypeSet.pop()
    result["yearEleccion"] = elYear.pop()
    result["mesEleccion"] = elMes.pop()

    return result


def tipoFich2fwfParams(fileType, fileDescrs):
    fileDescr = fileDescrs[fileType]

    anchos = [x[0] for x in fileDescr]
    nombreCols = [x[1] for x in fileDescr]
    tipoCols = {x[1]: (x[2] if len(x) == 3 else fieldTypes[x[1]]) for x in fileDescr}

    converters = {nc: tc for nc, tc in tipoCols.items()}
    return anchos, nombreCols, tipoCols, converters


def readPandaFWF(ziphandle, filenameInfo, elType, fileType):
    anchos, colnames, tipos, convFunctions = tipoFich2fwfParams(
        fileType, fieldDescriptions
    )

    try:
        filename = filenameInfo["ficheros"][elType][fileType]
    except KeyError:
        print(
            "No existe el fichero '%s'(%s) '%s'(%s) "
            % (elType, tipoEleccion[elType], fileType, tipoFichero[fileType])
        )
        return

    data = StringIO(ziphandle.read(filename).decode("cp1252"))

    try:
        result = read_fwf(
            data,
            header=None,
            widths=anchos,
            names=colnames,
            converters=convFunctions,
            iterator=False,
            index_col=False,
            debug=True,
            error_bad_lines=False,
            warn_bad_lines=True,
        )
    except ValueError as exc:
        print("Problemas leyendo el fichero %s: %s" % (filename, exc))
        return None

    return result


buildCUs = {
    "CUMUN": {"reqCols": ["nCPRO", "nCMUN"], "frmStr": "{nCPRO:02d}{nCMUN:03d}"},
    "CUDIS": {
        "reqCols": ["nCPRO", "nCMUN", "nCDIS"],
        "frmStr": "{nCPRO:02d}{nCMUN:03d}{nCDIS:02d}",
    },
    "CUSEC": {
        "reqCols": ["nCPRO", "nCMUN", "nCDIS", "nCSEC"],
        "frmStr": "{nCPRO:02d}{nCMUN:03d}{nCDIS:02d}{nCSEC:03d}",
    },
}


def retocaColumnas(df):
    col2numerize = [
        "CCA",
        "CPRO",
        "CMUN",
        "CDIS",
        "CSEC",
    ]
    result = df

    for c in result.columns:
        if result[c].dtype == "object":
            result[c] = result[c].map(lambda x: x.strip()).astype("string")

    if "CPRO" in result and "CCA" not in result:
        result["CCA"] = result["CPRO"].map(CPRO2CCA).astype("string")

    for c in col2numerize:
        if c in result.columns:
            newCOL = "n" + c
            result[newCOL] = result[c].astype("int32")

    for newCU, cuSpecs in buildCUs.items():
        if all([x in result.columns for x in cuSpecs["reqCols"]]):
            result[newCU] = result.apply(
                lambda x, specs=cuSpecs: specs["frmStr"].format(**{k: x[k] for k in specs["reqCols"]}), axis=1, )
            result["n" + newCU] = result[newCU].astype("int32")

    return result


def readFileZIP(filename):
    result = dict()

    zh, zi = unzipfile(filename)

    files = getFilenames(zi)
    elType = files["tipoEleccion"]

    setInfo = dict(readPandaFWF(zh, files, elType, "01").T[0])
    result["archInfo"] = setInfo

    if setInfo["adjuntaFich02"]:
        result["elecInfo"] = dict(readPandaFWF(zh, files, elType, "02").T[0])

    datosFicheros1 = [(3, "datosCandidatura"),
                      (4, "datosCandidatos"),
                      (5, "datosMunic"),
                      (6, "datosMunicResult"),
                      (7, "datosSupMunic"),
                      (8, "datosSupMunicResult"),
                      (9, "datosMesas"),
                      (10, "datosMesasResult")
                      ]

    for i, clave in datosFicheros1:
        claveSet = "adjuntaFich%02i" % i
        tipoFich = "%02i" % i

        if setInfo[claveSet]:
            aux = readPandaFWF(zh, files, elType, tipoFich)
            aux = retocaColumnas(aux)
            result[clave] = aux

    if setInfo["tipoElec"] == "04":
        for i, clave in [(11, "datosMunicPeq"), (12, "datosMunicPeqResult")]:
            claveSet = "adjuntaFich%02i04" % i
            tipoFich = "%02i" % i

            if setInfo[claveSet]:
                aux = readPandaFWF(zh, files, elType, tipoFich)
                aux = retocaColumnas(aux)
                result[clave] = aux

    for iEle, iFich, clave in [(5, 10, "datosDipMunic"), (6, 10, "datosDipMunicResult"), (7, 10, "datosDipSupMunic"),
                               (8, 10, "datosDipSupMunicResult")]:
        claveSet = "adjuntaFich%02i%02i" % (iEle, iFich)
        tipoEle = "%02i" % iEle
        tipoFich = "%02i" % iFich

        if setInfo[claveSet]:
            aux = readPandaFWF(zh, files, tipoFich, tipoEle)
            aux = retocaColumnas(aux)
            result[clave] = aux

    # Elimina entradas que han dado problema con la carga
    return {clave: result[clave] for clave in result if result[clave] is not None}


################################################################################################################

if __name__ == "__main__":
    readFileZIP("/home/calba/Datasets/Elec/Congreso/02201512_MESA.zip")
