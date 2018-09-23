import pandas as pd
import numpy as np
from collections import Counter


def DHondt(fila, votos='votCand', numescs=('datosTerr', 'numEscs'), votBlanco=('datosTerr', 'votBlanco'), umbral=0.0):
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
    else:
        raise TypeError("Esperaba una Serie (fila procedente del Dataframe")

    actVotos = Dvotos[~Dvotos.isna()].astype(np.uint64)
    sumVotos = sum(actVotos) + VvotBlanco
    umbVotos = Dvotos[Dvotos > (sumVotos * umbral)]
    noPasaUmbral = Dvotos[~(Dvotos > (sumVotos * umbral))].sum()
    # print("No pasa umbral: %i" % noPasaUmbral)

    cocientes = [(x, y + 1, umbVotos[x] / (y + 1), umbVotos[x]) for x in umbVotos.index for y in range(VnumEscs)]
    cocientes.sort(key=lambda x: x[2], reverse=True)
    elected = cocientes[:VnumEscs]

    ultEleg = cocientes[VnumEscs - 1]
    if len(cocientes) > VnumEscs:
        primNoEleg = cocientes[VnumEscs]
        difUltEsc = ((ultEleg[2] - primNoEleg[2]) * primNoEleg[1])
    else:
        primNoEleg = None
        difUltEsc = None

    dictElegidos = dict(Counter([x[0] for x in elected]))
    costeAsiento = {('costeAsiento', x): umbVotos[x] / dictElegidos[x] for x in dictElegidos}
    sinEsc = {x: np.uint32(0) for x in actVotos.index if x not in dictElegidos}
    votosSinEsc = {('votosSinAsiento', x): actVotos[x] if x not in dictElegidos else 0 for x in actVotos.index}
    dictElegidos.update(sinEsc)

    elegidos = pd.Series(dictElegidos)
    # print(elegidos.sum())
    elegidos.index = pd.MultiIndex.from_tuples([('asignados', x) for x in elegidos.index])
    votosUmbral = pd.Series({('votosUmbral', 'pasa'): umbVotos.sum(), ('votosUmbral', 'noPasa'): noPasaUmbral},
                            dtype=np.uint64)
    ultimoSi = pd.Series({('ultElegido', 'Partido'): ultEleg[0], ('ultElegido', 'Posicion'): ultEleg[1]})

    if primNoEleg is None:
        primeroNo = pd.Series({('primNoElegido', 'Partido'): None, ('primNoElegido', 'Posicion'): None})
        diferUltimo = pd.Series({('difUltEleg', 'votos'): None})
    else:
        primeroNo = pd.Series(
            {('primNoElegido', 'Partido'): primNoEleg[0], ('primNoElegido', 'Posicion'): primNoEleg[1]})
        diferUltimo = np.ceil(pd.Series({('difUltEleg', 'votos'): difUltEsc}))

    costeAsientoS = pd.Series(costeAsiento)
    votosSinEscS = pd.Series(votosSinEsc)

    resultados = pd.concat([elegidos, votosUmbral, ultimoSi, primeroNo, diferUltimo, costeAsientoS, votosSinEscS],
                           sort=False)

    return resultados
