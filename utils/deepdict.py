from collections import defaultdict


def deepDictSet(dic, keys, value):
    if isinstance(keys, str):
        dic[keys] = value
    elif isinstance(keys, (tuple, list)):
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys[-1]] = value
    else:
        raise KeyError("deepDictSet: don't know how to handle key '%s'" % keys)


def deepDict(dic, keys, tipoFinal):
    if len(keys) == 0:
        return dic
    if keys[0] not in dic and len(keys) == 1:
        dic[keys[0]] = (tipoFinal)()

    return deepDict(dic.setdefault(keys[0], {}), keys[1:], tipoFinal)


def generaDefaultDict(listaClaves, tipoFinal):
    """
    Genera un diccionario (defauldict) de 4 niveles de profundidad y cuyo tipo final es el que se indica en el parámetro
    :param listaClaves: lista con los niveles de claves (en realidad se usa la longitud)
    :param tipoFinal: tipo que va almacenar el diccionario más profundo
    :return: defaultdict(defaultdict(...(defaultdict(tipoFinal)))
    """

    def actGenera(objLen, tipo):
        if objLen == 1:
            return defaultdict((tipo))
        else:
            return defaultdict(lambda: actGenera(objLen - 1, tipo))

    return actGenera(len(listaClaves), tipoFinal)


def serie2deepdict(ser):
    result = dict()

    for k, v in zip(ser.index.to_list(), ser.values):
        deepDictSet(result, k, v)

    return result


def index2deepdict(myindex):
    result = dict()

    for k in myindex.to_list():
        deepDictSet(result, k, None)

    return result
