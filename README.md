

# Snippets
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

Corregir los ficheros 0710 que fallan por formato random

~~~
cat  07101505.DAT | awk '{ if ($0 !~ /^\s+$/){ if ($0 ~ /\s+$/) { VAL2=$0; gsub(/\s+$/,"",VAL2);  printf("%s%s\n",LINEA,VAL2); LINEA="" } else { LINEA=$0}}}' > 07101505.DATb
~~~

ESCRUTINIO

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

~~~