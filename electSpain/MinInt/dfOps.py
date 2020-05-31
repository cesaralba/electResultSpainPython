
from collections import defaultdict

import numpy as np
import pandas as pd

colsControl = dict(votCand='votCands', numPersElegidas='numEscs')

colsIDProc = ['tipoElec', 'yearElec', 'mesElec', 'numVuelta']
colsIDEnt = ['CCA', 'CPRO', 'CMUN', 'CDIS', 'CSEC', 'codMesa']
columnsIdent = colsIDProc + colsIDEnt
col2remove = ['codDP', 'codCom']


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


def aplanaResultados(reselect, columnaDato='votCand'):
    """
    A partir de un diccionario con todos los datos cargados del ZIP, devuelve un diccionario con dataframes que
    tienen combinado el dataframe de información de "circunscripción" (sean mesa, municipio o "entidades superiores al
    municipio") con los resultados obtenidos por las candidaturas para dicha circunscripción (con las candidaturas
    empleando la sigla que corresponde a la agrupación nacional según uno de los ficheros incluidos en el ZIP, el 03).
    El diccionario también descompone los DF "nativos" del resultado en las agrupaciones definidas en él. Ejemplo:
    mesas incluye datos CERA

    :param reselect: diccionario de dataframes con los datos cargados del ZIP
    :param columnaDato: valor del fichero de resultados que poner como resultado de la candidatura: pueden ser 'votCand'
            o 'numPersElegidas'. OJO! 'datosMesasResult' no tiene la columna 'numPersElegidas'.
    :return: Si se pasa un unico fichero a tratar, el dataframe que corresponde a ese fichero; si hay más de uno, un
             diccionario con los dataframes indexados por la clave del fichero
    """
    result = dict()

    if 'datosCandidatura' not in reselect:
        raise KeyError("aplanaResultados: Datos de candidaturas 'datosCandidatura' no disponibles en parametro")

    if columnaDato not in colsControl:
        raise KeyError("aplanaResultados: columnaDato suministrada '%s' no soportada." % columnaDato)

    infoCands = uniformizaCands(reselect['datosCandidatura'])

    # Aplana los resultados a partir de los datos en el ZIP
    for clave in reselect:
        if clave not in reselect:
            print("aplanaResultados: clave '%s' no conocida." % clave)
            continue
        if not clave.endswith('Result'):
            continue

        claveSinResult = clave.replace("Result", "")

        if claveSinResult not in reselect:
            print("aplanaResultados: clave '%s' (datos territorio) no conocida." % clave)
            continue

        dfDatos = reselect[claveSinResult]
        actRemoval = [x for x in col2remove if x in dfDatos.columns]

        dfDatosIndexed = dfDatos.set_index(clavesParaIndexar(dfDatos)).drop(labels=actRemoval, axis=1).sort_index()
        if colsControl[columnaDato] not in dfDatosIndexed:
            print("aplanaResultados: columna de control '%s' no est� en dataframe de datos '%s'" %
                  (colsControl[columnaDato], claveSinResult))
            continue
        dfDatosIndexed.columns = pd.MultiIndex.from_tuples(
            [(tipoClaveDatos(x, 'datosTerr'), x) for x in dfDatosIndexed.columns])

        # Añade la informaci�n de cand nacional a los resultados
        dfResults = reselect[clave].merge(infoCands)
        if columnaDato not in dfResults:
            print("aplanaResultados: columna de datos '%s' no est� en dataframe de resultados '%s'" % (columnaDato,
                                                                                                       clave))
            continue

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

        result[clave] = recolocaTerrColumns(
            pd.concat([dfDatosIndexed, resultPlanos], axis=1).reset_index(level=colsIDProc, col_level=1,
                                                                          col_fill="idProc"))

    # Separa los dataframes "planos" nativos en otros con las entidades que contienen
    if 'datosSupMunicResult' in result:
        clave = 'datosSupMunicResult'
        auxDF = result[clave]

        result['provResult'] = recolocaTerrColumns(auxDF[~auxDF.index.isin(values=[99], level='CPRO')])
        result['autResult'] = recolocaTerrColumns(
            auxDF[auxDF.index.isin(values=[99], level='CPRO') & ~ auxDF.index.isin(values=[99], level='CCA')])
        result['totResult'] = recolocaTerrColumns(auxDF[auxDF.index.isin(values=[99], level='CCA')])

    if 'datosMunicResult' in result:
        clave = 'datosMunicResult'
        auxDF = result[clave]

        result['municResult'] = recolocaTerrColumns(auxDF[auxDF.index.isin(values=[99], level='CDIS')])
        result['distrResult'] = recolocaTerrColumns(auxDF[~auxDF.index.isin(values=[99], level='CDIS')])

    if 'datosMesasResult' in result:
        clave = 'datosMesasResult'
        auxDF = result[clave]

        result['mesaResult'] = recolocaTerrColumns(auxDF[~auxDF.index.isin(values=[999], level='CMUN')])
        result['totCERA'] = recolocaTerrColumns(auxDF[auxDF.index.isin(values=[99], level='CCA')])
        result['autCERA'] = recolocaTerrColumns(
            auxDF[auxDF.index.isin(values=[999], level='CMUN') & auxDF.index.isin(values=[99], level='CPRO')])
        result['provCERA'] = recolocaTerrColumns(
            auxDF[auxDF.index.isin(values=[999], level='CMUN') & ~auxDF.index.isin(values=[99], level='CPRO')])

    return result


def tipoClaveDatos(k, defaultvalue):

    iTerr = ['CCA', 'CPRO', 'codDistrElect', 'codPJ', 'CMUN', 'CDIS', 'CSEC', 'codMesa', 'nomAmbito',
             'nomMunic']

    result = 'idTerr' if k in iTerr else defaultvalue

    return result


def recolocaTerrColumns(df):
    """
    Dado un dataframe, reordena las columnas y reasigna, si es necesario las columnas de datosTerr a idTerr

    :param df: dataframe a manipulas
    :return: dataframe nuevo con las columnas recolocadas
    """

    iTerr = ['CCA', 'CPRO', 'codDistrElect', 'codPJ', 'CMUN', 'CDIS', 'CSEC', 'codMesa', 'nomAmbito',
             'nomMunic']

    groupKeys = defaultdict(list)
    renamedColumns = [(('idTerr' if t[1] in iTerr else t[0]), t[1]) for t in df.columns.tolist()]

    df.columns = pd.MultiIndex.from_tuples(renamedColumns)

    for t in renamedColumns:
        groupKeys[t[0]].append(t[1])

    columnList = list()

    for k in iTerr:
        if k in groupKeys['idTerr']:
            columnList.append(('idTerr', k))

    for g in ['idProc', 'datosTerr', 'numPersElegidas', 'votCand']:
        if g in groupKeys:
            columnList = columnList + [(g, x) for x in groupKeys[g]]

    return df[columnList]


def getExtraInfo(reselect):
    """
    Extrae información adicional (nombres, datos partido judicial, distrito electoral...) de los resultados electorales
    para devolver un diccionario con dataframes que puedan mergear con los resultados aplanados.

    :param reselect: resultado de readFileZIP
    :return: Diccionario con dataframes (NO INDEXADOS). Las claves son:
            municData: datos de los municipios (partido judicial, distrito electoral, nombre)
            municDistrData: nombre del distrito electoral para los casos en los que hay distrito reconocido
            provData: nombre de la provincia
            autData: nombre de la comunidad autónoma
            totData: Total nacional
    """
    result = dict()

    if 'datosMunic' in reselect:
        dfwrk = reselect['datosMunic']
        result['municData'] = dfwrk[dfwrk['CDIS'] == 99][['CPRO', 'CMUN', 'codPJ', 'codDistrElect', 'nomMunic']]
        result['municDistrData'] = dfwrk[dfwrk['CDIS'] != 99][
            ['CPRO', 'CMUN', 'CDIS', 'nomMunic']].rename({'nomMunic': 'nomDistr'}, axis=1)

    if 'datosSupMunic' in reselect:
        dfwrk = reselect['datosSupMunic']
        result['provData'] = dfwrk[dfwrk['CPRO'] != 99][['CPRO', 'nomAmbito']].rename({'nomAmbito': 'nomProv'},
                                                                                            axis=1)
        result['autData'] = dfwrk[(dfwrk['CPRO'] == 99) & (dfwrk['CCA'] != 99)][['CCA', 'nomAmbito']].rename(
            {'nomAmbito': 'nomAut'}, axis=1)
        result['totData'] = dfwrk[dfwrk['CCA'] == 99][['CCA', 'nomAmbito']].rename({'nomAmbito': 'nomTot'},
                                                                                         axis=1)

    return result


################################################################################################################

if __name__ == "__main__":
    from electSpain.MinInt.fileZIP import readFileZIP

    resAux = readFileZIP('/home/calba/Datasets/Elec/Congreso/02201512_MESA.zip')

    aplanaResultados(resAux)
