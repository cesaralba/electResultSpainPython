#
# Descripcion de los ficheros incluidos en un .ZIP del Ministerio del Interior
#

import pandas as pd

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
        (2, "codProv"),  # (99 en elecciones al Parlamento Europeo)
        (1, "codDistr"),  # Distrito electoral 9 en elecciones que no tienen este tipo de circunscripción
        (3, "codMunic"),  # (elecciones municipales) o del Senador (Senado). En el resto de procesos 999
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
        (2, "codAut"),
        (2, "codProv"),
        (3, "codMunic"),
        (2, "numDistr"),  # Distrito municipal 99 si es el total municipal
        (100, "nomMunic"),  # o del distrito municipal
        (1, "codDistr"),  # Distrito electoral 0 en elecciones que no tienen este tipo de circunscripción
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
        (2, "codProv"),
        (3, "codMunic"),
        (2, "numDistr"),  # Distrito municipal 99 si es el total municipal
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
        (2, "codAut"),  # En el caso de Total Nacional, llevará 99
        (2, "codProv"),  # 99 si se trata de datos a nivel Total Comunidad o Total Nacional
        (1, "codDistr"),  # Distrito electoral 9 en datos a nivel Total Provincial, Comunidad o Nacional
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
        (2, "codAut"),  # En el caso de Total Nacional, llevará 99
        (2, "codProv"),  # 99 si se trata de datos a nivel Total Comunidad o Total Nacional
        (1, "codDistr"),  # Distrito electoral 9 en datos a nivel Total Provincial, Comunidad o Nacional
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
        (2, "codAut"),  # 99 si se trata del Total Nacional del C.E.R.A
        (2, "codProv"),  # 99 si se trata del Total Nacional o Autonómico del C.E.R.A
        (3, "codMunic"),  # (999 = C.E.R.A.)
        (2, "numDistr"),  # 01 si distrito único. En C.E.R.A., núm del ‘Distrito Electoral’ o 09 si provincia
        (4, "codSeccion"),  # (tres dígitos seguidos de un espacio, letra mayúscula u otro dígito)
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
        (2, "codAut"),  # 99 si se trata del Total Nacional del C.E.R.A
        (2, "codProv"),  # 99 si se trata del Total Nacional o Autonómico del C.E.R.A
        (3, "codMunic"),  # (999 = C.E.R.A.)
        (2, "numDistr"),  # 01 si distrito único. En C.E.R.A., núm del ‘Distrito Electoral’ o 09 si provincia
        (4, "codSeccion"),  # (tres dígitos seguidos de un espacio, letra mayúscula u otro dígito)
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
        (2, "codAut"),
        (2, "codProv"),
        (3, "codMunic"),
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
        (2, "codProv"),
        (3, "codMunic"),
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
    'tipoElec': pd.Int32Dtype,
    'yearElec': pd.Int32Dtype,
    'mesElec': pd.Int32Dtype,
    'numVuelta': pd.Int32Dtype,
    'adjuntaFich01': pd.Int32Dtype,
    'adjuntaFich02': pd.Int32Dtype,
    'adjuntaFich03': pd.Int32Dtype,
    'adjuntaFich04': pd.Int32Dtype,
    'adjuntaFich05': pd.Int32Dtype,
    'adjuntaFich06': pd.Int32Dtype,
    'adjuntaFich07': pd.Int32Dtype,
    'adjuntaFich08': pd.Int32Dtype,
    'adjuntaFich09': pd.Int32Dtype,
    'adjuntaFich10': pd.Int32Dtype,
    'adjuntaFich1104': pd.Int32Dtype,
    'adjuntaFich1204': pd.Int32Dtype,
    'adjuntaFich0510': pd.Int32Dtype,
    'adjuntaFich0610': pd.Int32Dtype,
    'adjuntaFich0710': pd.Int32Dtype,
    'adjuntaFich0810': pd.Int32Dtype,
    'ambito': pd.StringDtype,
    'codAmbito': pd.Int32Dtype,
    'fechaDIA': pd.Int32Dtype,
    'fechaMES': pd.Int32Dtype,
    'fechaYEAR': pd.Int32Dtype,
    'horaApert': pd.StringDtype,
    'horaCierre': pd.StringDtype,
    'horaAvance1': pd.StringDtype,
    'horaAvance2': pd.StringDtype,
    'codCand': pd.Int32Dtype,
    'siglaCand': pd.StringDtype,
    'nombreCand': pd.StringDtype,
    'codCandAcumProv': pd.Int32Dtype,
    'codCandAcumAut': pd.Int32Dtype,
    'codCandAcumNac': pd.Int32Dtype,
    'codProv': pd.Int32Dtype,
    'codDistr': pd.Int32Dtype,
    'codMunic': pd.Int32Dtype,
    'numOrdenPersCand': pd.Int32Dtype,
    'tipoPersCand': pd.StringDtype,
    'nomPersCand': pd.StringDtype,
    'ape1PersCand': pd.StringDtype,
    'ape2PersCand': pd.StringDtype,
    'sexPersCand': pd.StringDtype,
    'fecNacDiaPersCand': pd.Int32Dtype,
    'fecNacMesPersCand': pd.Int32Dtype,
    'fecNacYearPersCand': pd.Int32Dtype,
    'dniPersCand': pd.StringDtype,
    'elegidaPersCand': pd.StringDtype,
    'codAut': pd.Int32Dtype,
    'numDistr': pd.Int32Dtype,
    'nomMunic': pd.StringDtype,
    'codPJ': pd.Int32Dtype,
    'codDP': pd.Int32Dtype,
    'codCom': pd.Int32Dtype,
    'pobDerecho': pd.Int32Dtype,
    'numMesas': pd.Int32Dtype,
    'censINE': pd.Int32Dtype,
    'censEscr': pd.Int32Dtype,
    'censCEREescr': pd.Int32Dtype,
    'totVotCERE': pd.Int32Dtype,
    'votAvance1': pd.Int32Dtype,
    'votAvance2': pd.Int32Dtype,
    'votBlanco': pd.Int32Dtype,
    'votNulo': pd.Int32Dtype,
    'votCands': pd.Int32Dtype,
    'numEscs': pd.Int32Dtype,
    'votSI': pd.Int32Dtype,
    'votNO': pd.Int32Dtype,
    'datOfic': pd.StringDtype,
    'votCand': pd.Int32Dtype,
    'numPersElegidas': pd.Int32Dtype,
    'nomAmbito': pd.StringDtype,
    'codSeccion': pd.StringDtype,
    'codMesa': pd.StringDtype,
    'tipoMunic': pd.Int32Dtype,
    'numCandsObten': pd.Int32Dtype,
    'votPersCand': pd.Int32Dtype
}
