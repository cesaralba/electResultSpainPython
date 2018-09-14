
from collections import Sequence

import numpy as np
import pandas as pd

colsControl = dict(votCand='votCands', numPersElegidas='numEscs')

colsIDProc = ['tipoElec', 'yearElec', 'mesElec', 'numVuelta']
colsIDEnt = ['codAut', 'codProv', 'codMunic', 'numDistr', 'codSeccion', 'codMesa']
columnsIdent = colsIDProc + colsIDEnt


def clavesParaIndexar(dataframe):
    """
    Devuelve una lista con las columnas de un dataframe que pueden servir para forar un Index.

    :param dataframe: del que se sacaran las cadenas
    :return: lista de cadenas con Indice
    """

    result = [x for x in columnsIdent if x in dataframe.columns]

    return result


def uniformizaCands(datosCands):
    """
    En un dataframe de informac�n de candidaturas, asocia a cada na la informaci�n (nombre y siglas) que corresponde
    a la agrupaci�n de acumulaci�n nacional seg�n incluye el propio dataframe

    :param datosCands: dataframe de informaci�n de candidaturas (resultado del fichero 03 o datosCandidatura si se ha
                       empleado readFileZIP
    :return: datraframe de candidaturas con informaci�n de acumulaci�n nacional
    """

    columnsCands = ['tipoElec', 'yearElec', 'mesElec', 'codCand', 'codCandAcumNac']
    columnsCandsNac = ['tipoElec', 'yearElec', 'mesElec', 'codCand', 'siglaCand', 'nombreCand']

    dfCand = datosCands[columnsCands]
    dfCandNac = datosCands[columnsCandsNac]

    cands2Merge = dfCand.merge(dfCandNac, left_on=['tipoElec', 'yearElec', 'mesElec', 'codCandAcumNac'],
                               right_on=['tipoElec', 'yearElec', 'mesElec', 'codCand']
                               ).drop(columns=['codCand_y']).rename(columns={'codCand_x': 'codCand'})

    return cands2Merge


def uniformizaIndices(dfdatos, dfresultados):
    """
    Dados 2 dataframes, uno de datos de circunscripción y otro de resultados, realiza los cambios para que los 2 tengan
    los mismos índices (columnas empleadas para la identificación de filas) copiando columnas de uno a otro
    :param dfdatos:
    :param dfresultados:
    :return: dfdatosNuevo, dfresultadosNuevo dataframes con los mismos índices y las filas ordenadas.
    """

    nombresDatos = set(dfdatos.index.names)
    nombresResultados = set(dfresultados.index.names)

    nombresTotal = nombresDatos.union(nombresResultados)
    finalOrder = [x for x in columnsIdent if x in nombresTotal]
    faltanDatos = list(nombresTotal - nombresDatos)
    faltanResultados = list(nombresTotal - nombresResultados)

    if nombresDatos == nombresResultados:
        return dfdatos.reorder_levels(order=finalOrder).sort_index(), \
            dfresultados.reorder_levels(order=finalOrder).sort_index()

    if faltanDatos:
        auxResultados = dfresultados.reset_index(level=faltanDatos)
        auxDatos = dfdatos.copy()
        auxDatos[faltanDatos] = auxResultados[faltanDatos]
        resultDatos = auxDatos.set_index(keys=faltanDatos, append=True)
    else:
        resultDatos = dfdatos

    if faltanResultados:
        auxDatos = dfdatos.reset_index(level=faltanResultados)
        auxResultados = dfresultados.copy()
        auxResultados[faltanResultados] = auxDatos[faltanResultados]
        resultResultados = auxResultados.set_index(keys=faltanResultados, append=True)
    else:
        resultResultados = dfresultados

    return resultDatos.reorder_levels(order=finalOrder).sort_index(), \
        resultResultados.reorder_levels(order=finalOrder).sort_index()


def aplanaResultados(reselect, columnaDato='votCand', ficherosATratar=None):
    """
    A partir de un diccionario con todos los datos cargados del ZIP, devuelve un diccionario (*) con dataframes que
    tienen combinado el dataframe de información de "circunscripción" (sean mesa, municipio o "entidades superiores al
    municipio") con los resultados obtenidos por las candidaturas para dicha circunscripción (con las candidaturas
    empleando la sigla que corresponde a la agrupación nacional según uno de los ficheros incluidos en el ZIP, el 03).

    :param reselect: diccionario de dataframes con los datos cargados del ZIP
    :param columnaDato: valor del fichero de resultados que poner como resultado de la candidatura: pueden ser 'votCand'
            o 'numPersElegidas'
    :param ficherosATratar: Uno de los siguientes: datosMunicResult, datosSupMunicResult, datosMesasResult
                            Lista con alguna combinación de los anteriores
                            None -> Todos los ficheros que esten contenidos en el ZIP
    :return: Si se pasa un unico fichero a tratar, el dataframe que corresponde a ese fichero; si hay más de uno, un
             diccionario con los dataframes indexados por la clave del fichero
    """
    result = dict()

    if 'datosCandidatura' not in reselect:
        raise KeyError("aplanaResultados: Datos de candidaturas 'datosCandidatura' no disponibles en parametro")

    if columnaDato not in colsControl:
        raise KeyError("aplanaResultados: columnaDato suministrada '%s' no soportada." % columnaDato)

    infoCands = uniformizaCands(reselect['datosCandidatura'])

    if ficherosATratar is None:
        listaClaves = list(reselect.keys())
    elif isinstance(ficherosATratar, str):
        listaClaves = list()
        listaClaves.append(ficherosATratar)
    elif isinstance(ficherosATratar, Sequence):
        listaClaves = ficherosATratar
    else:
        raise TypeError("aplanaResultados: valor de parametro ficherosATratar no aceptable")

    for clave in listaClaves:
        if clave not in reselect:
            print("aplanaResultados: clave '%s' no conocida." % clave)
            continue
        if not clave.endswith('Result'):
            continue

        claveSinResult = clave.replace("Result", "")

        dfDatos = reselect[claveSinResult]
        dfDatosIndexed = dfDatos.set_index(clavesParaIndexar(dfDatos)).sort_index()
        if colsControl[columnaDato] not in dfDatosIndexed:
            raise KeyError("aplanaResultados: columna de control '%s' no est� en dataframe de datos '%s'" %
                           (colsControl[columnaDato], claveSinResult))
        dfDatosIndexed.columns = pd.MultiIndex.from_tuples([('datosTerr', x) for x in dfDatosIndexed.columns])

        # Añade la informaci�n de cand nacional a los resultados
        dfResults = reselect[clave].merge(infoCands)
        if columnaDato not in dfResults:
            raise KeyError("aplanaResultados: columna de datos '%s' no est� en dataframe de resultados '%s'" %
                           (columnaDato, clave))

        claves2index = clavesParaIndexar(dfResults) + ['siglaCand']
        claves2filter = claves2index + [columnaDato]

        # Cheap pivoting
        resultPlanos = dfResults[claves2filter].set_index(claves2index).unstack(-1)

        # Hace que los indices tengan las mismas columnas
        dfDatosIndexed, resultPlanos = uniformizaIndices(dfDatosIndexed, resultPlanos)

        controlVotosCands = resultPlanos.apply(np.sum, axis=1).astype(np.uint32)
        datosRef = dfDatosIndexed[('datosTerr', colsControl[columnaDato])]

        if not controlVotosCands.equals(datosRef):
            print("aplanaResultados: clave '%s' suma de votos de candidaturas en resultados no casa con DF de datos" %
                  clave)

        result[clave] = pd.concat([dfDatosIndexed, resultPlanos], axis=1).reset_index(level=colsIDProc,
                                                                                      col_level=1, col_fill="idProc")

        if isinstance(ficherosATratar, str):
            return result[clave]

    return result


################################################################################################################

if __name__ == "__main__":
    from electSpain.MinInt.fileZIP import readFileZIP

    resAux = readFileZIP('/home/calba/Datasets/Elec/Congreso/02201512_MESA.zip')

    aplanaResultados(resAux)
