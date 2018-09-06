
import zipfile as zf


def unzipfile(filename):
    try:
        zhandle = zf.ZipFile(filename)
    except BaseException as exc:
        print("Algo malo ha pasado. ")
        exit(1)

    infoList = [ x.filename for x in zhandle.infolist()]
    return zhandle, infoList

