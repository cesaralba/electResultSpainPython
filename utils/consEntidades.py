from collections import defaultdict

import numpy as np

dirTrans = {'ant': dict(), 'act': dict()}
dirInv = {'ant': defaultdict(list), 'act': defaultdict(list)}


def procesaGrCircs(df, claveDisc=None):
    if len(df) <= 2:
        return None

    targKeys = [x for x in df.partidos.columns.to_list() if not x[1].startswith('p')]
    dfAux = df.partidos[targKeys]

    # print(dfAux)
    # print(dfAux[df[claveDisc] != 99])

    filAgr = dfAux[df[claveDisc] == 99].sum(axis=0)
    filInd = dfAux[df[claveDisc] != 99].sum(axis=0)
    difFil = filAgr - filInd

    actDifs = difFil[difFil != 0]

    if (len(actDifs) == 0):
        return
    # print("A",filAgr)
    # print("I",filInd)
    # print("D",difFil)
    print(df[df[claveDisc] == 99][('idTerr', 'nombre', np.nan, np.nan)])
    # print("D+",actDifs)
    difPos = difFil[difFil > 0]
    difNeg = difFil[difFil < 0]
    print(len(difPos), len(difNeg))
    print(difPos)
    print(difNeg)

# procesaGrCircs(df2019final[df2019final.idTerr.codProv.iloc[:,0]==99], claveDisc=('idTerr','codAut',np.nan,np.nan))

# df2019final.groupby(df2019final.idTerr.codAut.iloc[:,0]).apply(procesaGrCircs,claveDisc=('idTerr','codProv',np.nan,np.nan))
