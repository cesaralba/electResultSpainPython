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
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (1, "adjuntaFich01", np.uint32),  # Siempre 1
        (1, "adjuntaFich02", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich03", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich04", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich05", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich06", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich07", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich08", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich09", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich10", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich1104", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich1204", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0510", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0610", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0710", np.uint32),  # 1/0 (se adjunta/no se adjunta el fichero
        (1, "adjuntaFich0810", np.uint32)  # 1/0 (se adjunta/no se adjunta el fichero
    ],
    # 2.- Fichero de IDENTIFICACION del proceso electoral
    '02': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),  # (en procesos a una sola vuelta o Referéndum = 1)
        (1, "ambito", str),  # (N=nacional, A=autonómico)
        (2, "codAmbito", np.uint32),  # del proceso electoral
        (2, "fechaDIA", np.uint32),
        (2, "fechaMES", np.uint32),
        (4, "fechaYEAR", np.uint32),
        (5, "horaApert", str),  # (en formato ‘HH:MM’ de 24 horas)
        (5, "horaCierre", str),  # (en formato ‘HH:MM’ de 24 horas)
        (5, "horaAvance1", str),  # (en formato ‘HH:MM’ de 24 horas)
        (5, "horaAvance2", str)  # (en formato ‘HH:MM’ de 24 horas)
    ],
    # 3.- Fichero de CANDIDATURAS
    '03': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (6, "codCand", np.uint32),
        (50, "siglaCand", str),
        (150, "nombreCand", str),
        (6, "codCandAcumProv", np.uint32),
        (6, "codCandAcumAut", np.uint32),
        (6, "codCandAcumNac", np.uint32)
    ],
    # 4.- Fichero de RELACION DE CANDIDATOS
    '04': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codProv", np.uint32),  # (99 en elecciones al Parlamento Europeo)
        (1, "codDistr", np.uint32),  # Distrito electoral 9 en elecciones que no tienen este tipo de circunscripción
        (3, "codMunic", np.uint32),  # (elecciones municipales) o del Senador (Senado). En el resto de procesos 999
        (6, "codCand", np.uint32),
        (3, "numOrdenPersCand", np.uint32),
        (1, "tipoPersCand", str),  # (T = Titular, " S = Suplente)
        (25, "nomPersCand", str),
        (25, "ape1PersCand", str),
        (25, "ape2PersCand", str),
        (1, "sexPersCand", str),  # (Masculino/Femenino)
        (2, "fecNacDiaPersCand", np.uint32),
        (2, "fecNacMesPersCand", np.uint32),
        (4, "fecNacYearPersCand", np.uint32),
        (10, "dniPersCand", str),
        (1, "elegidaPersCand", str)  # (S/N)
    ],
    # 5.- Fichero de DATOS COMUNES DE MUNICIPIOS
    '05': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codAut", np.uint32),
        (2, "codProv", np.uint32),
        (3, "codMunic", np.uint32),
        (2, "numDistr", np.uint32),  # Distrito municipal 99 si es el total municipal
        (100, "nomMunic", str),  # o del distrito municipal
        (1, "codDistr", np.uint32),  # Distrito electoral 0 en elecciones que no tienen este tipo de circunscripción
        (3, "codPJ", np.uint32),
        (3, "codDP", np.uint32),
        (3, "codCom", np.uint32),  # Comarca
        (8, "pobDerecho", np.uint32),
        (5, "numMesas", np.uint32),
        (8, "censINE", np.uint32),
        (8, "censEscr", np.uint32),
        (8, "censCEREescr", np.uint32),  # (Residentes Extranjeros)
        (8, "totVotCERE", np.uint32),
        (8, "votAvance1", np.uint32),
        (8, "votAvance2", np.uint32),
        (8, "votBlanco", np.uint32),
        (8, "votNulo", np.uint32),
        (8, "votCands", np.uint32),
        (3, "numEscs", np.uint32),  # cuando el municipio es la circunscripción electoral. Ceros en otros casos
        (8, "votSI", np.uint32),  # o ceros en otros procesos electorales
        (8, "votNO", np.uint32),  # o ceros en otros procesos electorales
        (1, "datOfic", str)  # (S/N)
    ],
    # 6.- Fichero de DATOS DE CANDIDATURAS DE MUNICIPIOS
    '06': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codProv", np.uint32),
        (3, "codMunic", np.uint32),
        (2, "numDistr", np.uint32),  # Distrito municipal 99 si es el total municipal
        (6, "codCand", np.uint32),
        (8, "votCand", np.uint32),
        (3, "numPersElegidas", np.uint32)
    ],
    # 7.- Fichero de DATOS COMUNES DE AMBITO SUPERIOR AL MUNICIPIO
    '07': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codAut", np.uint32),  # En el caso de Total Nacional, llevará 99
        (2, "codProv", np.uint32),  # 99 si se trata de datos a nivel Total Comunidad o Total Nacional
        (1, "codDistr", np.uint32),  # Distrito electoral 9 en datos a nivel Total Provincial, Comunidad o Nacional
        (50, "nomAmbito", str),
        (8, "pobDerecho", np.uint32),
        (5, "numMesas", np.uint32),
        (8, "censINE", np.uint32),
        (8, "censEscr", np.uint32),
        (8, "censCEREescr", np.uint32),  # (Residentes Extranjeros)
        (8, "totVotCERE", np.uint32),
        (8, "votAvance1", np.uint32),
        (8, "votAvance2", np.uint32),
        (8, "votBlanco", np.uint32),
        (8, "votNulo", np.uint32),
        (8, "votCands", np.uint32),
        (6, "numEscs", np.uint32),  # cuando el municipio es la circunscripción electoral. Ceros en otros casos
        (8, "votSI", np.uint32),  # o ceros en otros procesos electorales
        (8, "votNO", np.uint32),  # o ceros en otros procesos electorales
        (1, "datOfic", str)  # (S/N)
    ],
    # 8.- Fichero de DATOS DE CANDIDATURAS DE AMBITO SUPERIOR AL MUNICIPIO
    '08': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codAut", np.uint32),  # En el caso de Total Nacional, llevará 99
        (2, "codProv", np.uint32),  # 99 si se trata de datos a nivel Total Comunidad o Total Nacional
        (1, "codDistr", np.uint32),  # Distrito electoral 9 en datos a nivel Total Provincial, Comunidad o Nacional
        (6, "codCand", np.uint32),
        (8, "votCand", np.uint32),
        (5, "numPersElegidas", np.uint32)
    ],
    # 9.- Fichero de DATOS COMUNES DE MESAS y del C.E.R.A
    '09': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codAut", np.uint32),  # 99 si se trata del Total Nacional del C.E.R.A
        (2, "codProv", np.uint32),  # 99 si se trata del Total Nacional o Autonómico del C.E.R.A
        (3, "codMunic", np.uint32),  # (999 = C.E.R.A.)
        (2, "numDistr", np.uint32),  # 01 si distrito único. En C.E.R.A., núm del ‘Distrito Electoral’ o 09 si provincia
        (4, "codSeccion", str),  # (tres dígitos seguidos de un espacio, letra mayúscula u otro dígito)
        (1, "codMesa", str),  # (una letra mayúscula identificando la mesa o una ‘U’ en caso de mesa única)
        (7, "censINE", np.uint32),
        (7, "censEscr", np.uint32),
        (7, "censCEREescr", np.uint32),  # (Residentes Extranjeros)
        (7, "totVotCERE", np.uint32),
        (7, "votAvance1", np.uint32),
        (7, "votAvance2", np.uint32),
        (7, "votBlanco", np.uint32),
        (7, "votNulo", np.uint32),
        (7, "votCands", np.uint32),
        (7, "votSI", np.uint32),  # o ceros en otros procesos electorales
        (7, "votNO", np.uint32),  # o ceros en otros procesos electorales
        (1, "datOfic", str)  # (S/N)
    ],
    # 10.- Fichero de DATOS DE CANDIDATURAS DE MESAS y del C.E.R.A
    '10': [
        (2, "tipoElec", np.uint32),
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codAut", np.uint32),  # 99 si se trata del Total Nacional del C.E.R.A
        (2, "codProv", np.uint32),  # 99 si se trata del Total Nacional o Autonómico del C.E.R.A
        (3, "codMunic", np.uint32),  # (999 = C.E.R.A.)
        (2, "numDistr", np.uint32),  # 01 si distrito único. En C.E.R.A., núm del ‘Distrito Electoral’ o 09 si provincia
        (4, "codSeccion", str),  # (tres dígitos seguidos de un espacio, letra mayúscula u otro dígito)
        (1, "codMesa", str),  # (una letra mayúscula identificando la mesa o una ‘U’ en caso de mesa única)
        (6, "codCand", np.uint32),  # Código de la candidatura o del Senador en elecciones al Senado
        (7, "votCand", np.uint32)
    ],
    # 11.- Fichero de DATOS COMUNES DE MUNICIPIOS menores de 250 habitantes. (Solo en Elecciones Municipales)
    '11': [
        (2, "tipoMunic", np.uint32),  # 08 = entre 100 y 250 habitantes, 09 = menores de 100 habitantes
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codAut", np.uint32),
        (2, "codProv", np.uint32),
        (3, "codMunic", np.uint32),
        (100, "nomMunic", str),  # o del distrito municipal
        (3, "codPJ", np.uint32),
        (3, "codDP", np.uint32),
        (3, "codCom", np.uint32),  # Comarca
        (3, "pobDerecho", np.uint32),
        (2, "numMesas", np.uint32),
        (3, "censINE", np.uint32),
        (3, "censEscr", np.uint32),
        (3, "censCEREescr", np.uint32),  # (Residentes Extranjeros)
        (3, "totVotCERE", np.uint32),
        (3, "votAvance1", np.uint32),
        (3, "votAvance2", np.uint32),
        (3, "votBlanco", np.uint32),
        (3, "votNulo", np.uint32),
        (3, "votCands", np.uint32),
        (2, "numEscs", np.uint32),  # cuando el municipio es la circunscripción electoral. Ceros en otros casos
        (1, "datOfic", str)  # (S/N)
    ],
    # 12.- Fichero de DATOS DE CANDIDATURAS DE MUNICIPIOS menores de 250 hab. (Solo en Elecciones Municipales)
    '12': [
        (2, "tipoMunic", np.uint32),  # 08 = entre 100 y 250 habitantes, 09 = menores de 100 habitantes
        (4, "yearElec", np.uint32),
        (2, "mesElec", np.uint32),
        (1, "numVuelta", np.uint32),
        (2, "codProv", np.uint32),
        (3, "codMunic", np.uint32),
        (6, "codCand", np.uint32),
        (3, "votCand", np.uint32),
        (2, "numCandsObten", np.uint32),
        (25, "nomPersCand", str),
        (25, "ape1PersCand", str),
        (25, "ape2PersCand", str),
        (1, "sexPersCand", str),  # (Masculino/Femenino)
        (2, "fecNacDiaPersCand", np.uint32),
        (2, "fecNacMesPersCand", np.uint32),
        (4, "fecNacYearPersCand", np.uint32),
        (10, "dniPersCand", str),
        (3, "votPersCand", np.uint32),
        (1, "elegidaPersCand", str),  # (S/N)
    ]

}
