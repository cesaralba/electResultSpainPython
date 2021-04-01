import bz2
import gzip
import zipfile as zf


def fileOpener(filename, mode="r"):
    """
    Devuelve un handler de fichero abierto en función de la extensión del fichero
    :param filename: Nombre del fichero de entrada / salida. Extensiones soportadas: bz2 (bzip 2) y gz (gzip)
    :param mode: r para lectura (defecto) o w para escritura (le añade el 't' si el fichero lo precisa)
    :return: un file handler donde se puede leer / escribir.
    """

    extraMode = "t" if "b" not in mode else ""
    if filename.endswith(".gz"):
        f = gzip.open(filename, mode + extraMode)
    elif filename.endswith(".bz2"):
        f = bz2.open(filename, mode + extraMode)
    else:
        f = open(filename, mode)

    return f


def unzipfile(filename):
    try:
        zhandle = zf.ZipFile(filename)
    except BaseException as exc:
        print("Algo malo ha pasado. %s: %s " % (type(exc), exc))
        exit(1)

    infoList = [x.filename for x in zhandle.infolist()]
    return zhandle, infoList
