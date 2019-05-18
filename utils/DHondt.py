import pandas as pd
import numpy as np
from collections import Counter


def DHondt(fila, votos='votCand', numescs=('datosTerr', 'numEscs'), votBlanco=('datosTerr', 'votBlanco'), umbral=0.0,
           calculaCosteAsiento=False, calculaUltimoElecto=False, calculaVotosSinEsc=False,
           calculaCortadosUmabral=False):
    if isinstance(fila, pd.core.series.Series):
        if votos in fila.index:
            Dvotos = fila[votos]
        else:
            print("DHondt: clave '%s' para votos no está en fila." % votos)
            return None

        if isinstance(numescs, (int, np.uint32, np.uint64)):
            VnumEscs = numescs
        elif numescs in fila.index:
            VnumEscs = fila[numescs]
        else:
            print("DHondt: clave '%s' para numero de escaños no está en fila." % numescs)
            return None


        if isinstance(votBlanco, (int, np.uint32, np.uint64)):
            VvotBlanco = votBlanco
        elif votBlanco in fila.index:
            VvotBlanco = fila[votBlanco]
        else:
            print("DHondt: clave '%s' para numero de votos en blanco no está en fila." % votBlanco)
            return None

        if isinstance(umbral, (float, np.float32, np.float64)):
            Vumbral = umbral
        elif votBlanco in fila.index:
            Vumbral = fila[umbral]
        else:
            print("DHondt: clave '%s' para umbral no está en fila." % umbral)
            return None

    else:
        raise TypeError("Esperaba una Serie (fila procedente del Dataframe")

    actVotos = Dvotos[~Dvotos.isna()].astype(np.uint64)
    sumVotos = sum(actVotos) + VvotBlanco
    umbVotos = Dvotos[Dvotos > (sumVotos * Vumbral)]

    listaSeriesFinal = list()

    # Calcula electos
    if sum(actVotos) > 0:
        cocientes = [(x, y + 1, umbVotos[x] / (y + 1), umbVotos[x]) for x in umbVotos.index for y in range(VnumEscs)]
        cocientes.sort(key=lambda x: x[2], reverse=True)
        elected = cocientes[:VnumEscs]
        ultEleg = cocientes[VnumEscs - 1]
    else:
        cocientes = []
        elected = []
        ultEleg = None

    dictElegidos = dict(Counter([x[0] for x in elected]))
    sinEsc = {x: np.uint32(0) for x in actVotos.index if x not in dictElegidos}
    dictElegidos.update(sinEsc)
    elegidos = pd.Series(dictElegidos)
    elegidos.index = pd.MultiIndex.from_tuples([('asignados', x) for x in elegidos.index])

    listaSeriesFinal.append(elegidos)

    if calculaCosteAsiento:
        costeAsiento = {('costeAsiento', x): umbVotos[x] / dictElegidos[x] for x in dictElegidos}
        costeAsientoS = pd.Series(costeAsiento)
        listaSeriesFinal.append(costeAsientoS)

    if calculaUltimoElecto:
        if len(cocientes) > VnumEscs:
            primNoEleg = cocientes[VnumEscs]
            difUltEsc = ((ultEleg[2] - primNoEleg[2]) * primNoEleg[1])
        else:
            primNoEleg = None
            difUltEsc = None

        if ultEleg is None:
            ultimoSi = pd.Series({('ultElegido', 'Partido'): None, ('ultElegido', 'Posicion'): None})
        else:
            ultimoSi = pd.Series({('ultElegido', 'Partido'): ultEleg[0], ('ultElegido', 'Posicion'): ultEleg[1]})

        if primNoEleg is None:
            primeroNo = pd.Series({('primNoElegido', 'Partido'): None, ('primNoElegido', 'Posicion'): None})
            diferUltimo = pd.Series({('difUltEleg', 'votos'): None})
        else:
            primeroNo = pd.Series(
                {('primNoElegido', 'Partido'): primNoEleg[0], ('primNoElegido', 'Posicion'): primNoEleg[1]})
            diferUltimo = np.ceil(pd.Series({('difUltEleg', 'votos'): difUltEsc}))

        listaSeriesFinal.append(ultimoSi)
        listaSeriesFinal.append(primeroNo)
        listaSeriesFinal.append(diferUltimo)

    if calculaVotosSinEsc:
        votosSinEsc = {('votosSinAsiento', x): actVotos[x] if x not in dictElegidos else 0 for x in actVotos.index}
        votosSinEscS = pd.Series(votosSinEsc)
        listaSeriesFinal.append(votosSinEscS)

    if calculaCortadosUmabral:
        noPasaUmbral = Dvotos[~(Dvotos > (sumVotos * Vumbral))].sum()
        votosUmbral = pd.Series({('votosUmbral', 'pasa'): umbVotos.sum(), ('votosUmbral', 'noPasa'): noPasaUmbral},
                                dtype=np.uint64)
        listaSeriesFinal.append(votosUmbral)

    resultados = pd.concat(objs=listaSeriesFinal, sort=False)

    return resultados
