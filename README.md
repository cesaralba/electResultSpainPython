

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
from electSpain.MinInt.dfOps import aplanaResultados
from utils.DHondt import DHondt

res2011 = readFileZIP('/home/Datasets/Elec/Congreso/02201111_MESA.zip')
res2015 = readFileZIP('/home/Datasets/Elec/Congreso/02201512_MESA.zip')
res2016 = readFileZIP('/home/Datasets/Elec/Congreso/02201606_MESA.zip')

planosV2011 = aplanaResultados(res2011,columnaDato='votCand')
planosV2015 = aplanaResultados(res2015,columnaDato='votCand')
planosV2016 = aplanaResultados(res2016,columnaDato='votCand')

planosE2011 = aplanaResultados(res2011,columnaDato='numPersElegidas')
planosE2015 = aplanaResultados(res2015,columnaDato='numPersElegidas')
planosE2016 = aplanaResultados(res2016,columnaDato='numPersElegidas')

supV2011=planosV2011['datosSupMunicResult']
supV2015=planosV2015['datosSupMunicResult']
supV2016=planosV2016['datosSupMunicResult']

supE2011=planosE2011['datosSupMunicResult']
supE2015=planosE2015['datosSupMunicResult']
supE2016=planosE2016['datosSupMunicResult']

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
DHmad2011=DHondt(madridV2015,umbral=0.03)
DHmad2011=DHondt(madridV2016,umbral=0.03)
~~~

