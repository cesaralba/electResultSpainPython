from collections import defaultdict


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
            result += (" inv: " + ", ".join(["  '%s' <- '%s'" % (k, ", ".join(sorted(v))) for k, v in self.inv.items()])
                       )
        else:
            result += " inv: no trads"

        return result

    # __repr__ = __str
    # def __repr__(self):
    #     return self. __str__()
