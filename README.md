

# Snippets
~~~
. /home/calba/Dropbox/ENVS/ElecSpain/loadEnv 
~~~
## Opciones carga ipython



~~~
%load_ext autoreload
%reload_ext autoreload
%autoreload 2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
~~~

## Para hacer cosas (dentro de iPython)
~~~
from electSpain.MinInt.fileZIP import readFileZIP
from electSpain.MinInt.dfOps import aplanaResultados, recolocaTerrColumns, getExtraInfo
from utils.DHondt import DHondt

res2011 = readFileZIP('/home/Datasets/Elec/Congreso/02201111_MESA.zip')
res2015 = readFileZIP('/home/Datasets/Elec/Congreso/02201512_MESA.zip')
res2016 = readFileZIP('/home/Datasets/Elec/Congreso/02201606_MESA.zip')

extraI2016 = getExtraInfo(res2016)
extraI2015 = getExtraInfo(res2015)
extraI2011 = getExtraInfo(res2011)

planosV2011 = aplanaResultados(res2011,columnaDato='votCand')
planosV2015 = aplanaResultados(res2015,columnaDato='votCand')
planosV2016 = aplanaResultados(res2016,columnaDato='votCand')

planosE2011 = aplanaResultados(res2011,columnaDato='numPersElegidas')
planosE2015 = aplanaResultados(res2015,columnaDato='numPersElegidas')
planosE2016 = aplanaResultados(res2016,columnaDato='numPersElegidas')

supV2011=planosV2011['datosSupMunicResult']
supV2015=planosV2015['datosSupMunicResult']
supV2016=planosV2016['datosSupMunicResult']

munV2011=planosV2011['datosMunicResult']
munV2015=planosV2015['datosMunicResult']
munV2016=planosV2016['datosMunicResult']

mesV2011=planosV2011['datosMesasResult']
mesV2015=planosV2015['datosMesasResult']
mesV2016=planosV2016['datosMesasResult']


supE2011=planosE2011['datosSupMunicResult']
supE2015=planosE2015['datosSupMunicResult']
supE2016=planosE2016['datosSupMunicResult']

munE2011=planosE2011['datosMunicResult']
munE2015=planosE2015['datosMunicResult']
munE2016=planosE2016['datosMunicResult']


madridV2011 = supV2011.loc[(12,28)]
madridV2015 = supV2015.loc[(12,28)]
madridV2016 = supV2016.loc[(12,28)]
~~~

## Regla DHondt
~~~
DHsup2011=supV2011.apply(DHondt,axis=1, umbral=0.03)
DHsup2015=supV2015.apply(DHondt,axis=1, umbral=0.03)
DHsup2016=supV2016.apply(DHondt,axis=1, umbral=0.03)

DHmad2011=DHondt(madridV2011,umbral=0.03)
DHmad2015=DHondt(madridV2015,umbral=0.03)
DHmad2016=DHondt(madridV2016,umbral=0.03)
~~~

## Control de calidad de datos Min Int
~~~
FILELIST=['/home/Datasets/Elec/CAbildos/06197904_TOTA.zip', '/home/Datasets/Elec/CAbildos/06198706_MESA.zip', '/home/Datasets/Elec/CAbildos/06199105_MESA.zip', '/home/Datasets/Elec/CAbildos/06199505_MESA.zip', '/home/Datasets/Elec/CAbildos/06199906_MESA.zip', '/home/Datasets/Elec/CAbildos/06200305_MESA.zip', '/home/Datasets/Elec/CAbildos/06200705_MESA.zip', '/home/Datasets/Elec/CAbildos/06201105_MESA.zip', '/home/Datasets/Elec/Congreso/02197706_MUNI.zip', '/home/Datasets/Elec/Congreso/02197903_MUNI.zip', '/home/Datasets/Elec/Congreso/02198210_MESA.zip', '/home/Datasets/Elec/Congreso/02198606_MESA.zip', '/home/Datasets/Elec/Congreso/02198910_MESA.zip', '/home/Datasets/Elec/Congreso/02199306_MESA.zip', '/home/Datasets/Elec/Congreso/02199603_MESA.zip', '/home/Datasets/Elec/Congreso/02200003_MESA.zip', '/home/Datasets/Elec/Congreso/02200403_MESA.zip', '/home/Datasets/Elec/Congreso/02200803_MESA.zip', '/home/Datasets/Elec/Congreso/02201111_MESA.zip', '/home/Datasets/Elec/Congreso/02201606_MESA.zip', '/home/Datasets/Elec/Congreso/02201512_MESA.zip', '/home/Datasets/Elec/Congreso/03201512_MESA.zip', '/home/Datasets/Elec/Europeas/07198706_MESA.zip', '/home/Datasets/Elec/Europeas/07198906_MESA.zip', '/home/Datasets/Elec/Europeas/07199406_MESA.zip', '/home/Datasets/Elec/Europeas/07199906_MESA.zip', '/home/Datasets/Elec/Europeas/07200406_MESA.zip', '/home/Datasets/Elec/Europeas/07200906_MESA.zip', '/home/Datasets/Elec/Europeas/07201405_MESA.zip', '/home/Datasets/Elec/Municipales/04197904_MUNI.zip', '/home/Datasets/Elec/Municipales/04198305_MUNI.zip', '/home/Datasets/Elec/Municipales/04198706_MESA.zip', '/home/Datasets/Elec/Municipales/04199105_MESA.zip', '/home/Datasets/Elec/Municipales/04199505_MESA.zip', '/home/Datasets/Elec/Municipales/04199906_MESA.zip', '/home/Datasets/Elec/Municipales/04200305_MESA.zip', '/home/Datasets/Elec/Municipales/04200705_MESA.zip', '/home/Datasets/Elec/Municipales/04201105_MESA.zip', '/home/Datasets/Elec/Municipales/04201505_MESA.zip', '/home/Datasets/Elec/Senado/03198606_MESA.zip', '/home/Datasets/Elec/Senado/03198910_MESA.zip', '/home/Datasets/Elec/Senado/03199306_MESA.zip', '/home/Datasets/Elec/Senado/03199603_MESA.zip', '/home/Datasets/Elec/Senado/03200003_MESA.zip', '/home/Datasets/Elec/Senado/03200403_MESA.zip', '/home/Datasets/Elec/Senado/03200803_MESA.zip', '/home/Datasets/Elec/Senado/03201111_MESA.zip', '/home/Datasets/Elec/Senado/03201606_MESA.zip']

for i in FILELIST:
    print(i)
    res=readFileZIP(i)

~~~

# Corregir los ficheros 0710 que fallan por formato random

~~~
cat  07101505.DAT | awk '{ if ($0 !~ /^\s+$/){ if ($0 ~ /\s+$/) { VAL2=$0; gsub(/\s+$/,"",VAL2);  printf("%s%s\n",LINEA,VAL2); LINEA="" } else { LINEA=$0}}}' > 07101505.DATb
~~~

# Secciones censales

~~~
In [26]: gdf.columns
Out[26]:
Index(['OBJECTID', 'CUSEC', 'CUMUN', 'CSEC', 'CDIS', 'CMUN', 'CPRO', 'CCA',
       'CUDIS', 'OBS', 'CNUT0', 'CNUT1', 'CNUT2', 'CNUT3', 'CLAU2', 'NPRO',
       'NCA', 'NMUN', 'Shape_Leng', 'Shape_area', 'Shape_len', 'geometry',
       'count'],
      dtype='object')

~~~

~~~
import geopandas as gpd
from seccCensales.matrAdyacencia import leeContornoSeccionesCensales, agrupaContornos, creaNumCols, creaMatrizRec, preparaAgrupacionConts, secNIV, vecinos2DF, setDFLabels
from itertools import product
import numpy as np
import pandas as pd

#Carga los contornos de 2011
gdf = leeContornoSeccionesCensales("/home/Datasets/Elec/SeccionesCensales/years/2019/SECC_CE_20190101.dbf")




gdf['count']=1 # Para contar secciones en el territorio

%time ccas = creaNumCols(agrupaContornos(gdf, claveAgr=['CCA'],extraCols=['NCA']), cols=['CCA'])  # ~ 60s  
%time provs = creaNumCols(agrupaContornos(gdf, claveAgr=['CPRO'],extraCols=['CCA', 'NCA', 'NPRO']), cols=['CCA','CPRO'])  # ~ 50s
%time muns = creaNumCols(agrupaContornos(gdf, claveAgr=['CUMUN'],extraCols=['CCA', 'CPRO', 'CMUN','NCA', 'NPRO', 'NMUN']), cols=['CCA','CPRO', 'CMUN','CUMUN']) # ~ 22s   
%time dis = creaNumCols(agrupaContornos(gdf, claveAgr=['CUDIS'],extraCols=['CCA', 'CPRO', 'CMUN','CDIS','CUMUN', 'NCA', 'NPRO', 'NMUN']), cols=['CCA','CPRO', 'CMUN','CDIS','CUMUN','CUDIS']) # ~15s
%time secs = creaNumCols(gdf,cols=[ 'CCA', 'CPRO', 'CMUN','CDIS','CSEC', 'CUMUN','CUDIS', 'CUSEC'])  # < 1s

%time mcca = creaMatriz(ccas,clave='nCCA')
matricesAdj = { 'nCCA': mcca }
%time mprovs = creaMatriz(provs,clave='nCPRO',matricesMR=matricesAdj)
matricesAdj = { 'nCPRO': mprovs }

for p in product(cca2.index, cca2.index):
    d0 = cca2.loc[p[0]]
    d1 = cca2.loc[p[1]]
    g0 = d0.geometry
    g1 = d1.geometry
    print(p[0],p[1],d0['NCA'],d1['NCA'],g0.intersects(g1))

%time g1 = preparaAgrupacionConts(gdf) ~ 3 min
%time g2 = creaMatrizRec(g1,['CCAA', 'PRO', 'MUN', 'DIS', 'SEC']) ~ 1h
  
for k in g1:
    print(k,g1[k].keys())

for k in g2:
    print(k,len(g2[k]))


for k in g1:
    print(k,g1[k].keys())
    if 'sup2k' in g1[k]:
        print(k,'sup2k\n', g1[k]['sup2k'].apply(len).value_counts().sort_index())

for k in g2:
    print(k)
        print(k, g2[k].apply(sum).value_counts().sort_index())

matAUT = setDFLabels(g2['CCAA'], g1, 'CCAA', 'NCA'):
matPRO = setDFLabels(g2['PRO'], g1, 'PRO', 'NPRO'):

~~~

# ESCRUTINIO
=======
# Procesado ESCRUTINIO


~~~
from utils.openJSONescr import *
from collections import Counter, defaultdict
from itertools import chain

DIRBASE='/home/calba/devel/Elec2018/out'
FILEALL='/home/calba/devel/Elec2018/out/201904282110/CO99999999999.json'
FILEAUT='/home/calba/devel/Elec2018/out/201904282110/CO04999999999.json'
FILEPROV='/home/calba/devel/Elec2018/out/201904282110/CO04079999999.json'
FILENOMENC='/home/calba/devel/Elec2018/out/nomenclator.json'
OUTFILE='/tmp/escGen201904.parquet'

resAll = readJSONfile(FILEALL)  
resAut = readJSONfile(FILEAUT)  
resProv = readJSONfile(FILEPROV)  

nomenc=processNomenclator(FILENOMENC) 
allMerged=processResultsDir(DIRBASE, nomenclator=nomenc, year=2019)

allDF = createDataframe(allMerged)

ultEscr= allDF.groupby('amb').tail(n=1) 

~~~


~~~
from seccCensales.matrAdyacencia import leeContornoSeccionesCensales, agrupaContornos, creaNumCols, creaMatrizRec, preparaAgrupacionConts, secNIV, vecinos2DF, setDFLabels
from itertools import product
import numpy as np
import pandas as pd


g2011 = leeContornoSeccionesCensales("/home/Datasets/Elec/SeccionesCensales/years/2011/SECC_CE_20110101_03_R_INE.dbf")
g2019 = leeContornoSeccionesCensales("/home/Datasets/Elec/SeccionesCensales/years/2019/SECC_CE_20190101.dbf")

~~~

# Analisis ESCRUTINIO 2019

~~~
import pandas as pd
import numpy as np
from utils.consEntidades import consolidaPartidosIntraperiodo, aplicaTraducciones, consolidaDFesp, extraeNivel, preparaDatos
   
FILEESCR='/home/calba/Dropbox/SuperManager/escrutiniogen201904.parquet'      
from utils.openJSONescr import ultEntrada, parquet2DF
from utils.DHondt import DHondt


df2019 = parquet2DF(FILEESCR)
df2019final = ultEntrada(df2019)

df2019aux = pd.concat([df2019final.idTerr.droplevel(2,axis=1).droplevel(1,axis=1),
                       df2019final.totales.act[['carg','votbla']].droplevel(1,axis=1),
                       df2019final.escrutinio[['pexclus']].droplevel(2,axis=1).droplevel(1,axis=1)/100,   
                      ],axis=1)

df2019terr = pd.concat([df2019aux],axis=1,keys=['datosTerr'])
df2019vots = pd.concat([df2019final.partidos.act.vot],axis=1,keys=['votCand'])
df2019escs = pd.concat([df2019final.partidos.act.carg],axis=1,keys=['escsCand'])


df2019votsC=df2019terr.join(df2019vots).loc[df2019final.idTerr.tipo.iloc[:,0]== 'CIRCUNSCRIPCIÓN ELECTORAL']
df2019escsC=df2019terr.join(df2019escs).loc[df2019final.idTerr.tipo.iloc[:,0]== 'CIRCUNSCRIPCIÓN ELECTORAL']
df2019votsA=df2019terr.join(df2019vots).loc[df2019final.idTerr.tipo.iloc[:,0]== 'COMUNIDAD']
df2019escsA=df2019terr.join(df2019escs).loc[df2019final.idTerr.tipo.iloc[:,0]== 'COMUNIDAD']
df2019votsE=df2019terr.join(df2019vots).loc[df2019final.idTerr.tipo.iloc[:,0]== 'ESPAÑA']
df2019escsE=df2019terr.join(df2019escs).loc[df2019final.idTerr.tipo.iloc[:,0]== 'ESPAÑA']



#pAct = df2019circs.partidos.act

#df2019terr = pd.concat([df2019circs.idTerr.copy().droplevel(2,axis=1).droplevel(1,axis=1)],keys=['idTerr'])
#df2019Info=df2019circs[[('totales', 'act', 'carg', np.nan),('totales', 'act', 'votbla', np.nan),('escrutinio', 'pexclus', np.nan, np.nan)]].copy()
#df2019Info.columns=pd.Index(['numEscs','votbla','pexclus'])

#df2019vot =  df2019circs.partidos.act.vot.copy()
#df2019carg =  df2019circs.partidos.act.carg.copy()

#subCol=[x for x in df2019.columns.to_list() if (x[0] == 'idTerr' or (x[0] == 'partidos' and x[1] == 'act'))]
#dfAct = df2019final[subCol]

#trad=None
#for g in df2019final.groupby(df2019final.idTerr.codAut.iloc[:,0]):
#    df=g[1]
#    print(df)
#    print(df[df[('idTerr','codProv',np.nan,np.nan)] == 99][[('idTerr', 'tipo', np.nan, np.nan),('idTerr', 'nombre', np.nan, np.nan)]])

#    trad=consolidaPartidosIntraperiodo(g[1],claveDisc=('idTerr','codProv',np.nan,np.nan),trads=trad)
#trad=consolidaPartidosIntraperiodo(df2019final[df2019final.idTerr.codProv.iloc[:,0]==99], claveDisc=('idTerr','codAut',np.nan,np.nan),trads=trad)

#df2019final.groupby(df2019final.idTerr.codAut.iloc[:,0]).apply(procesaGrCircs,claveDisc=('idTerr','codProv',np.nan,np.nan))

dfTraducido=consolidaDFesp(df2019final)

dfTV,dfTC=preparaDatos(dfTraducido)

dfTVnac=extraeNivel(dfTV,"ESPAÑA")
dfTCnac=extraeNivel(dfTC,"ESPAÑA")

dfTVprov=extraeNivel(dfTV,"CIRCUNSCRIPCIÓN ELECTORAL")
dfTCprov=extraeNivel(dfTC,"CIRCUNSCRIPCIÓN ELECTORAL")

aux=dfTVprov.apply(DHondt,axis=1,votos='partidos',numescs=('totales', 'carg'),votBlanco=('totales', 'votbla'),umbral=0.03,calculaCosteAsiento=True, calculaUltimoElecto=True,calculaVotosSinEsc=True,calculaCortadosUmbral=True) 


~~~
