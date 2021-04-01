manipSecCensales = [
    {
        "2numeric": {
            "prefix": "n",
            "cols": ["CCA", "CPRO", "CMUN", "CDIS", "CSEC", "CUMUN", "CUDIS", "CUSEC"],
        }
    },
    {
        "concat": {
            "NUT1": ["CNUT0", "CNUT1"],
            "NUT2": ["CNUT0", "CNUT1", "CNUT2"],
            "NUT3": ["CNUT0", "CNUT1", "CNUT2", "CNUT3"],
        }
    },
]

validacionesSecCensales = [
    ["CCA", "NCA"],
    ["CCA", "CNUT0"],
    ["CPRO", "NPRO"],
    ["CPRO", "NCA"],
    ["NPRO", "NCA"],
    ["CPRO", "CNUT0"],
    ["CPRO", "CNUT1"],
    ["CPRO", "CNUT2"],
    ["CUMUN", "NMUN"],
    ["CUMUN", "CMUN"],
    ["CUMUN", "NCA"],
    ["CUMUN", "NPRO"],
    ["CUMUN", "NMUN"],
    ["CUDIS", "CDIS"],
    ["CUDIS", "NMUN"],
    ["CUDIS", "CMUN"],
    ["CUDIS", "NCA"],
    ["CUDIS", "NPRO"],
    ["CUDIS", "NMUN"],
    ["CUSEC", "CSEC"],
]
