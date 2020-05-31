#
# Descripcion de los ficheros incluidos en un .ZIP del Ministerio del Interior
#

import numpy as np

tipoEleccion = {
    '01': 'Referéndum',
    '02': 'Congreso',
    '03': 'Senado',
    '04': 'Municipales, Partidos Judiciales y Diputaciones Provinciales',
    '05': 'Autonómicas',
    '06': 'Cabildos Insulares',
    '07': 'Parlamento Europeo',
    '15': 'Juntas Generales'
}

tipoFichero = {
    '01': 'Fichero de control',
    '02': 'Fichero de identificación del proceso electoral',
    '03': 'Fichero de candidaturas',
    '04': 'Fichero de candidatos',
    '05': 'Fichero de datos globales de ámbito municipal',
    '06': 'Fichero de datos de candidaturas de ámbito municipal',
    '07': 'Fichero de datos globales de ámbito superior al municipio',
    '08': 'Fichero de datos de candidaturas de ámbito superior al municipio',
    '09': 'Fichero de datos globales de mesas',
    '10': 'Fichero de datos de candidaturas de mesas',
    '11': 'Fichero de datos globales de municipios menores de 250 habitantes (en elecciones municipales)',
    '12': 'Fichero de datos de candidaturas de municipios menores de 250 habitantes (en elecciones municipales)'
}

codAut2nombre = {
    '01': 'Andalucía',
    '02': 'Aragón',
    '03': 'Asturias',
    '04': 'Baleares',
    '05': 'Canarias',
    '06': 'Cantabria',
    '07': 'Castilla - La Mancha',
    '08': 'Castilla y León',
    '09': 'Cataluña',
    '10': 'Extremadura',
    '11': 'Galicia',
    '12': 'Madrid',
    '13': 'Navarra',
    '14': 'País Vasco',
    '15': 'Región de Murcia',
    '16': 'La Rioja',
    '17': 'Comunidad Valenciana',
    '18': 'Ceuta',
    '19': 'Melilla'
}

fieldDescriptions = {
    # 1.- Fichero de CONTROL de los ficheros que componen el proceso electoral
    '01': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (1, "adjuntaFich01"),  # Siempre 1
        (1, "adjuntaFich02"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich03"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich04"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich05"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich06"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich07"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich08"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich09"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich10"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich1104"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich1204"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0510"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0610"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0710"),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0810")  # 1/0 (se adjunta/no se adjunta el fichero
    ],
    # 2.- Fichero de IDENTIFICACION del proceso electoral
    '02': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),  # (en procesos a una sola vuelta o Referéndum = 1)
        (1, "ambito"),  # (N=nacional, A=autonómico)
        (2, "codAmbito"),  # del proceso electoral
        (2, "fechaDIA"),
        (2, "fechaMES"),
        (4, "fechaYEAR"),
        (5, "horaApert"),  # (en formato ‘HH:MM’ de 24 horas)
        (5, "horaCierre"),  # (en formato ‘HH:MM’ de 24 horas)
        (5, "horaAvance1"),  # (en formato ‘HH:MM’ de 24 horas)
        (5, "horaAvance2")  # (en formato ‘HH:MM’ de 24 horas)
    ],
    # 3.- Fichero de CANDIDATURAS
    '03': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (6, "codCand"),
        (50, "siglaCand"),
        (150, "nombreCand"),
        (6, "codCandAcumProv"),
        (6, "codCandAcumAut"),
        (6, "codCandAcumNac")
    ],
    # 4.- Fichero de RELACION DE CANDIDATOS
    '04': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CPRO"),  # (99 en elecciones al Parlamento Europeo)
        (1, "codDistrElect"),  # Distrito electoral 9 en elecciones que no tienen este tipo de circunscripción
        (3, "CMUN"),  # (elecciones municipales) o del Senador (Senado). En el resto de procesos 999
        (6, "codCand"),
        (3, "numOrdenPersCand"),
        (1, "tipoPersCand"),  # (T = Titular, " S = Suplente)
        (25, "nomPersCand"),
        (25, "ape1PersCand"),
        (25, "ape2PersCand"),
        (1, "sexPersCand"),  # (Masculino/Femenino)
        (2, "fecNacDiaPersCand"),
        (2, "fecNacMesPersCand"),
        (4, "fecNacYearPersCand"),
        (10, "dniPersCand"),
        (1, "elegidaPersCand")  # (S/N)
    ],
    # 5.- Fichero de DATOS COMUNES DE MUNICIPIOS
    '05': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CCA"),
        (2, "CPRO"),
        (3, "CMUN"),
        (2, "CDIS"),  # Distrito municipal 99 si es el total municipal
        (100, "nomMunic"),  # o del distrito municipal
        (1, "codDistrElect"),  # Distrito electoral 0 en elecciones que no tienen este tipo de circunscripción
        (3, "codPJ"),
        (3, "codDP"),
        (3, "codCom"),  # Comarca
        (8, "pobDerecho"),
        (5, "numMesas"),
        (8, "censINE"),
        (8, "censEscr"),
        (8, "censCEREescr"),  # (Residentes Extranjeros)
        (8, "totVotCERE"),
        (8, "votAvance1"),
        (8, "votAvance2"),
        (8, "votBlanco"),
        (8, "votNulo"),
        (8, "votCands"),
        (3, "numEscs"),  # cuando el municipio es la circunscripción electoral. Ceros en otros casos
        (8, "votSI"),  # o ceros en otros procesos electorales
        (8, "votNO"),  # o ceros en otros procesos electorales
        (1, "datOfic")  # (S/N)
    ],
    # 6.- Fichero de DATOS DE CANDIDATURAS DE MUNICIPIOS
    '06': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CPRO"),
        (3, "CMUN"),
        (2, "CDIS"),  # Distrito municipal 99 si es el total municipal
        (6, "codCand"),
        (8, "votCand"),
        (3, "numPersElegidas")
    ],
    # 7.- Fichero de DATOS COMUNES DE AMBITO SUPERIOR AL MUNICIPIO
    '07': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CCA"),  # En el caso de Total Nacional, llevará 99
        (2, "CPRO"),  # 99 si se trata de datos a nivel Total Comunidad o Total Nacional
        (1, "codDistrElect"),  # Distrito electoral 9 en datos a nivel Total Provincial, Comunidad o Nacional
        (50, "nomAmbito"),
        (8, "pobDerecho"),
        (5, "numMesas"),
        (8, "censINE"),
        (8, "censEscr"),
        (8, "censCEREescr"),  # (Residentes Extranjeros)
        (8, "totVotCERE"),
        (8, "votAvance1"),
        (8, "votAvance2"),
        (8, "votBlanco"),
        (8, "votNulo"),
        (8, "votCands"),
        (6, "numEscs"),  # cuando el municipio es la circunscripción electoral. Ceros en otros casos
        (8, "votSI"),  # o ceros en otros procesos electorales
        (8, "votNO"),  # o ceros en otros procesos electorales
        (1, "datOfic")  # (S/N)
    ],
    # 8.- Fichero de DATOS DE CANDIDATURAS DE AMBITO SUPERIOR AL MUNICIPIO
    '08': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CCA"),  # En el caso de Total Nacional, llevará 99
        (2, "CPRO"),  # 99 si se trata de datos a nivel Total Comunidad o Total Nacional
        (1, "codDistrElect"),  # Distrito electoral 9 en datos a nivel Total Provincial, Comunidad o Nacional
        (6, "codCand"),
        (8, "votCand"),
        (5, "numPersElegidas")
    ],
    # 9.- Fichero de DATOS COMUNES DE MESAS y del C.E.R.A
    '09': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CCA"),  # 99 si se trata del Total Nacional del C.E.R.A
        (2, "CPRO"),  # 99 si se trata del Total Nacional o Autonómico del C.E.R.A
        (3, "CMUN"),  # (999 = C.E.R.A.)
        (2, "CDIS"),  # 01 si distrito único. En C.E.R.A., núm del ‘Distrito Electoral’ o 09 si provincia
        (4, "CSEC"),  # (tres dígitos seguidos de un espacio, letra mayúscula u otro dígito)
        (1, "codMesa"),  # (una letra mayúscula identificando la mesa o una ‘U’ en caso de mesa única)
        (7, "censINE"),
        (7, "censEscr"),
        (7, "censCEREescr"),  # (Residentes Extranjeros)
        (7, "totVotCERE"),
        (7, "votAvance1"),
        (7, "votAvance2"),
        (7, "votBlanco"),
        (7, "votNulo"),
        (7, "votCands"),
        (7, "votSI"),  # o ceros en otros procesos electorales
        (7, "votNO"),  # o ceros en otros procesos electorales
        (1, "datOfic")  # (S/N)
    ],
    # 10.- Fichero de DATOS DE CANDIDATURAS DE MESAS y del C.E.R.A
    '10': [
        (2, "tipoElec"),
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CCA"),  # 99 si se trata del Total Nacional del C.E.R.A
        (2, "CPRO"),  # 99 si se trata del Total Nacional o Autonómico del C.E.R.A
        (3, "CMUN"),  # (999 = C.E.R.A.)
        (2, "CDIS"),  # 01 si distrito único. En C.E.R.A., núm del ‘Distrito Electoral’ o 09 si provincia
        (4, "CSEC"),  # (tres dígitos seguidos de un espacio, letra mayúscula u otro dígito)
        (1, "codMesa"),  # (una letra mayúscula identificando la mesa o una ‘U’ en caso de mesa única)
        (6, "codCand"),  # Código de la candidatura o del Senador en elecciones al Senado
        (7, "votCand")
    ],
    # 11.- Fichero de DATOS COMUNES DE MUNICIPIOS menores de 250 habitantes. (Solo en Elecciones Municipales)
    '11': [
        (2, "tipoMunic"),  # 08 = entre 100 y 250 habitantes, 09 = menores de 100 habitantes
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CCA"),
        (2, "CPRO"),
        (3, "CMUN"),
        (100, "nomMunic"),  # o del distrito municipal
        (3, "codPJ"),
        (3, "codDP"),
        (3, "codCom"),  # Comarca
        (3, "pobDerecho"),
        (2, "numMesas"),
        (3, "censINE"),
        (3, "censEscr"),
        (3, "censCEREescr"),  # (Residentes Extranjeros)
        (3, "totVotCERE"),
        (3, "votAvance1"),
        (3, "votAvance2"),
        (3, "votBlanco"),
        (3, "votNulo"),
        (3, "votCands"),
        (2, "numEscs"),  # cuando el municipio es la circunscripción electoral. Ceros en otros casos
        (1, "datOfic")  # (S/N)
    ],
    # 12.- Fichero de DATOS DE CANDIDATURAS DE MUNICIPIOS menores de 250 hab. (Solo en Elecciones Municipales)
    '12': [
        (2, "tipoMunic"),  # 08 = entre 100 y 250 habitantes, 09 = menores de 100 habitantes
        (4, "yearElec"),
        (2, "mesElec"),
        (1, "numVuelta"),
        (2, "CPRO"),
        (3, "CMUN"),
        (6, "codCand"),
        (3, "votCand"),
        (2, "numCandsObten"),
        (25, "nomPersCand"),
        (25, "ape1PersCand"),
        (25, "ape2PersCand"),
        (1, "sexPersCand"),  # (Masculino/Femenino)
        (2, "fecNacDiaPersCand"),
        (2, "fecNacMesPersCand"),
        (4, "fecNacYearPersCand"),
        (10, "dniPersCand"),
        (3, "votPersCand"),
        (1, "elegidaPersCand"),  # (S/N)
    ]

}

fieldTypes = {
    'adjuntaFich01': np.uint32,
    'adjuntaFich02': np.uint32,
    'adjuntaFich03': np.uint32,
    'adjuntaFich04': np.uint32,
    'adjuntaFich05': np.uint32,
    'adjuntaFich0510': np.uint32,
    'adjuntaFich06': np.uint32,
    'adjuntaFich0610': np.uint32,
    'adjuntaFich07': np.uint32,
    'adjuntaFich0710': np.uint32,
    'adjuntaFich08': np.uint32,
    'adjuntaFich0810': np.uint32,
    'adjuntaFich09': np.uint32,
    'adjuntaFich10': np.uint32,
    'adjuntaFich1104': np.uint32,
    'adjuntaFich1204': np.uint32,
    'ambito': str,
    'ape1PersCand': str,
    'ape2PersCand': str,
    'censCEREescr': np.uint32,
    'censEscr': np.uint32,
    'censINE': np.uint32,
    'codAmbito': np.uint32,
    'CCA': str,
    'codCand': np.uint32,
    'codCandAcumAut': np.uint32,
    'codCandAcumNac': np.uint32,
    'codCandAcumProv': np.uint32,
    'codCom': np.uint32,
    'codDP': np.uint32,
    'codDistrElect': str,
    'codMesa': str,
    'CMUN': str,
    'codPJ': np.uint32,
    'CPRO': str,
    'CSEC': str,
    'datOfic': str,
    'dniPersCand': str,
    'elegidaPersCand': str,
    'fecNacDiaPersCand': np.uint32,
    'fecNacMesPersCand': np.uint32,
    'fecNacYearPersCand': np.uint32,
    'fechaDIA': np.uint32,
    'fechaMES': np.uint32,
    'fechaYEAR': np.uint32,
    'horaApert': str,
    'horaAvance1': str,
    'horaAvance2': str,
    'horaCierre': str,
    'mesElec': np.uint32,
    'nomAmbito': str,
    'nomMunic': str,
    'nomPersCand': str,
    'nombreCand': str,
    'numCandsObten': np.uint32,
    'CDIS': str,
    'numEscs': np.uint32,
    'numMesas': np.uint32,
    'numOrdenPersCand': np.uint32,
    'numPersElegidas': np.uint32,
    'numVuelta': np.uint32,
    'pobDerecho': np.uint32,
    'sexPersCand': str,
    'siglaCand': str,
    'tipoElec': np.uint32,
    'tipoMunic': np.uint32,
    'tipoPersCand': str,
    'totVotCERE': np.uint32,
    'votAvance1': np.uint32,
    'votAvance2': np.uint32,
    'votBlanco': np.uint32,
    'votCand': np.uint32,
    'votCands': np.uint32,
    'votNO': np.uint32,
    'votNulo': np.uint32,
    'votPersCand': np.uint32,
    'votSI': np.uint32,
    'yearElec': np.uint32
}
