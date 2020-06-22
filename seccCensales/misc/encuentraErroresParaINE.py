from collections import defaultdict

import geopandas as gpd

from seccCensales.operDF import validaciones, manipSecCensales
from utils.operations.retocaDF import applyDFtransforms, passDFvalidators


def validaSeccionesCensalesINE(scDict):
    """
    Dado un diccionario cuyos valores son los ficheros de secciones censales (la clave puede ser cualquier cosa pero por
    simplicidad el año) devuelve otro diccionario con las mismas claves y cuyos valores incluyen el geodataframe del
    fichero y las validaciones aplicadas sobre él.

    :param scDict: dict {'2018':'ficheroSecCensales2018'}
    :return: dict { '2018': {'df':geoDataFrame2018, 'checks': resultado validaciones GDF }}

    """
    result = {y: {'fname': fname} for y, fname in scDict.items()}

    for y, fname in scDict.items():
        auxDF = gpd.read_file(fname)
        trfDF = applyDFtransforms(auxDF, manipSecCensales)

        result[y]['df'] = trfDF
        result[y]['checks'] = passDFvalidators(trfDF, validaciones)
        result[y]['cadChecks'] = checks2str(result[y]['checks'], 'CUSEC')

    return result


def checks2str(resChecks, colClave=None):
    #cellProblems = lambda: {'valorMayoritario': defaultdict(defaultdict(set))}
    cellProblems = lambda: {'valorMayoritario': defaultdict(lambda: defaultdict(set)), 'fuentes':defaultdict(set)}
    secProblematicas = defaultdict(lambda: defaultdict(cellProblems))
    secEmpate = defaultdict(lambda: defaultdict(cellProblems))
    divergentes = dict()

    def infoSC(x, comb, clave=None):
        nameROW = x.name if clave is None else x[clave]
        result = (nameROW, comb['claveIDX'], x[comb['claveIDX']], comb['claveVAL'], x[comb['claveVAL']])
        return result

    for res in resChecks:
        for comb in res['combs']:
            if 'valorMayoria' in comb:
                valMay = comb['valorMayoria'][0] if isinstance(comb['valorMayoria'], list) else comb['valorMayoria']
                aux = comb['divergentes'].apply(infoSC, axis=1, comb=comb, clave=colClave).tolist()
                for name, IDX, valIDX, VAL, valVAL in aux:
                    secProblematicas[name][VAL]['valorUsado'] = valVAL
                    secProblematicas[name][VAL]['valorMayoritario'][valMay][IDX].add(valIDX)
                    divergentes[name] = comb['divergentes']
            else:
                nombres = comb['divergentes'].index.to_list() if colClave is None else comb['divergentes'][colClave].to_list()
                clave = "_".join(sorted(nombres))
                divergentes[clave] = comb['divergentes']
                secEmpate[clave][comb['claveVAL']]['valores']=comb['cuentas']
                secEmpate[clave][comb['claveVAL']]['nombres']=sorted(nombres)
                secEmpate[clave][comb['claveVAL']]['fuentes'][comb['claveIDX']].add(comb['valorIDX'])


    resultAUX = []
    NEWLINE = "\n"
    nameCLAVE = "index" if colClave is None else colClave
    for probSEC in secProblematicas:
        valoresDiferentes = []
        for clave, valor in secProblematicas[probSEC].items():
            newMayoritarios = []
            valorUsado = valor['valorUsado']
            for valorMay, usadoEN in valor['valorMayoritario'].items():
                cadenasEN = [f"{claveEN}=({','.join(usosEN)})" for claveEN, usosEN in usadoEN.items()]
                mayoritarioSTR = f"'{valorMay}' usado en {','.join(cadenasEN)}"
                newMayoritarios.append(mayoritarioSTR)

            newValorDif = f"{clave} dice '{valorUsado}'. El valor mayoritario en campos similares es {';'.join(newMayoritarios)}"
            valoresDiferentes.append(newValorDif)

        nuevoDato = f"""Sección {nameCLAVE}={probSEC}.\n{NEWLINE.join(valoresDiferentes)}\nReg divergentes\n{divergentes[probSEC].T}\n"""
        resultAUX.append(nuevoDato)

    for claveEMP,secData in secEmpate.items():
        valoresDiferentes = []
        nombres = ""
        for clave, valorClave in secData.items():
            cadena2add=f"""{clave} tiene valores {sorted(list(valorClave['valores'].keys()))}. No hay mayoritario."""
            nombres = valorClave['nombres']
            valoresDiferentes.append(cadena2add)

        nuevoDato = f"""Secciones {nameCLAVE}={",".join(nombres)}.\n{NEWLINE.join(valoresDiferentes)}\nReg divergentes\n{divergentes[claveEMP].T}"""
        resultAUX.append(nuevoDato)


    result = NEWLINE.join(resultAUX)

    return result
