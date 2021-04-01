fixesINE = [
    # Sección CUSEC=2006903032
    {"condition": {"CUMUN": "20069", "NPRO": "Gipuzcoa"}, "fix": {"NPRO": "Gipuzkoa"}},
    {
        "condition": {"CUMUN": "20069", "NCA": "Pais Vasco"},
        "fix": {"NCA": "País Vasco"},
    },
    {
        "condition": {"CUMUN": "20069", "NMUN": "Donostia-San Sebastían"},
        "fix": {"NMUN": "Donostia-San Sebastián"},
    },
    # Sección CUSEC=3412101001
    {"condition": {"CPRO": "34", "CNUT3": "2"}, "fix": {"CNUT3": "4"}},
    {"condition": {"CPRO": "34", "NPRO": "Burgos"}, "fix": {"NPRO": "Palencia"}},
    # Sección CUSEC=2809204040,2809204041,2809204042
    {"condition": {"CUMUN": "28092", "NMUN": "Mostoles"}, "fix": {"NMUN": "Móstoles"}},
    # Sección CUSEC=4410901001
    {"condition": {"CCA": "02", "NCA": "Aragon"}, "fix": {"NCA": "Aragón"}},
    # Secciones CUSEC=1190301001,1190301002
    {"condition": {"CUMUN": "11903", "CMUN": "021"}, "fix": {"CMUN": "903"}},
    # {'condition': {}, 'fix': {}},
]
