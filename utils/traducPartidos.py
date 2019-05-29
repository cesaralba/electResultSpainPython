from collections import defaultdict
from copy import deepcopy

from .deepdict import serie2deepdict


class traducPartidos(object):

    def __init__(self):
        self.dir = dict()
        self.inv = defaultdict(list)

    def nuevaTrad(self, plocal, pagg):

        origList = plocal if isinstance(plocal, (tuple, list)) else [plocal]

        for orig in origList:
            self.dir[orig] = pagg
            self.inv[pagg].append(orig)

    def traduce(self, sigla):
        return self.dir.get(sigla, None)

    def quitaTrad(self, plocal):
        if plocal in self.dir:
            tradExist = self.dir[plocal]
            self.dir.pop(plocal)
            self.inv[tradExist].pop(plocal)
            if len(self.inv[tradExist]) == 0:
                self.inv.pop(tradExist)

    def listaPartidos(self):
        return self.dir.keys()

    def listaAgregados(self):
        return self.inv.keys()

    def __repr__(self):
        result = ""
        if self.dir:
            result += (" dir: " + ", ".join(["  '%s' -> '%s'" % (k, v) for k, v in self.dir.items()]))
        else:
            result += " dir: no trads"

        if self.inv:
            result += (" inv: " + ", ".join(["  '%s' <- [%s]" % (k, ", ".join(sorted(v))) for k, v in self.inv.items()])
                       )
        else:
            result += " inv: no trads"

        return result

    def eliminaTraduccionesIntermedias(self):
        keysTo = set(self.inv.keys())
        keysFrom = set(self.dir.keys())

        for k in keysTo.intersection(keysFrom):
            self.nuevaTrad(self.inv[k], self.dir[k])
            self.inv.pop(k)


class agrupaTraduccionesFB(object):
    """
    Asigna las equivalencias de partidos por fuerza bruta. Problema habitual con este enfoque: escala mal.
    Pero me ha servido para hacer un generador de iterador.

    """

    def __init__(self, agrupadores, aagrupar, tradConoc=None):
        """
        Inicializa el objeto para buscar combinaciones válidas

        :param agrupadores:  nombres de los partidos en los que se van a asignar
        :param aagrupar: nombres de los partidos que se van a asignar
        :param tradConoc: traducciones ya conocidas para añadir el resultado
        """
        if len(agrupadores) == 0:
            raise ValueError("AgrupaTraducciones: no se han indicado agrupadores")
        if len(agrupadores) > len(aagrupar):
            raise ValueError("AgrupaTraducciones: se han indicado mas agrupadores (%i) que clases a agrupar(%i)" % (
                len(agrupadores), len(aagrupar)))

        self.contenedores = agrupadores
        self.clases = aagrupar

        self.trads = tradConoc if tradConoc else traducPartidos()

        self.numcont = len(self.contenedores)
        self.lenClases = len(self.clases)

        self.i2cont = dict(zip(range(self.numcont), self.contenedores))
        self.i2class = dict(zip(range(self.lenClases), self.clases))

        self.estado = 0

    def combinador(self):
        """
        Devuelve una traducción valida (todos los partidos asignados y ni un agregador sin partido).
        OJO: es una traducción válida que luego hay que ver si las sumas dan.

        Iterador
        :return:
        """

        while self.estado < (self.numcont) ** (self.lenClases + 1):
            flag = True
            while flag:
                if self.estado >= (self.numcont) ** (self.lenClases + 1):
                    raise StopIteration()

                nBase = self.estado

                dests = {x: [] for x in self.i2cont}

                for i in range(self.lenClases):
                    dest = nBase % self.numcont
                    dests[dest].append(i)
                    nBase = nBase // self.numcont

                # print("-------------------> comb", nBase, dests)
                self.estado += 1
                control = [(len(dests[d]) == 0) for d in dests]
                if sum(control) == 0:
                    flag = False

            result = deepcopy(self.trads)

            for d in dests:
                origTrad = [self.i2class[x] for x in dests[d]]
                result.nuevaTrad(origTrad, self.i2cont[d])

            # print("combinador", vars(result))

            yield result


def asignaTradsKS(contenedores, clases, knownTrad=None):
    """
    Asigna traducciones analizando el problema como sucesivos Knapsacks (uno por cada traducción destino)

    OJO: Asume que todos los partidos asignables van a ir a un contenedor, que todos los contenedores van a tener al
    menos un partido y que las sumas son exactas: votos de contenedor = suma(votos partidos asignables)

    OJO2: Aunque se pueda hacer con "carg" (escaños) no tiene demasiado sentido ya que puede haber más de un asignable
    con los mismos escaños (1 ó 2, p.ej.). Lo razonable es usar "vot" que es menos probable que las sumas den

    :param contenedores: serie con los partidos en los que se van a asignar con numero de "cosas" (votos)
    :param clases: serie con los partidos que se tienen que distribuir en los contenedores. Los valores deben ser
                   POSITIVOS
    :param knownTrad: traducciones conocidas. Las descubiertas se añadirán. OJO: debe ser un objeto traducPartidos.

    :return: traducciones nuevas.
    """

    def findPosItems(cap, itemlist):
        return sorted([(k, v) for k, v in itemlist if v <= cap], key=lambda kv: kv[1], reverse=True)

    def ks(capacidad, carga, elementos):
        if capacidad == 0:
            return carga
        if len(elementos) == 0 and capacidad > 0:
            return None
        for e, v in elementos:
            nuevaCarga = carga.copy()
            nuevaCarga.append((e, v))
            nuevaCapacidad = capacidad - v

            nuevosElementos = findPosItems(nuevaCapacidad, [(k, v) for k, v in elementos if k != e])

            resKS = ks(nuevaCapacidad, nuevaCarga, nuevosElementos)
            if resKS is not None:
                return resKS

        return None

    if knownTrad:
        result = deepcopy(knownTrad)
    else:
        result = traducPartidos()

    dicCont = sorted(serie2deepdict(contenedores).items(), key=lambda kv: kv[1])
    dicClass = sorted(serie2deepdict(clases).items(), key=lambda kv: kv[1], reverse=True)

    for kagg, v in dicCont:
        elemList = [(k, v) for k, v in dicClass if k not in list(result.listaPartidos())]

        resKS = ks(v, [], elemList)
        result.nuevaTrad([k for k, v in resKS], kagg)

    return result
