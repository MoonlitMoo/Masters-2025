# Data Processing

[https://data.nrao.edu/portal/#/](https://data.nrao.edu/portal/#/)

# General notes

[Flagging notes](Data%20Processing/Flagging%20notes%201d01feeec5b78031a513c7232b96be9c.md)

[Calibration Parts](Data%20Processing/Calibration%20Parts%201ed1feeec5b780d3a311ee88a6a2a841.md)

[Pipeline Calibration Steps](Data%20Processing/Pipeline%20Calibration%20Steps%201ef1feeec5b780fdbfcfd7596dbbe1f9.md)

Related repositories

- https://github.com/MoonlitMoo/casa-pipeline
- https://github.com/MoonlitMoo/Masters-2025 (Private)

# Overview

- Project names are **24A-411** (C-config) ****and **25A-157** (D-config)
- Taken in C and D configuration in the X-band (8-12 GHz). Some C-band scans are taken for X-band setup, but can be ignored.
- Polarisation should be minimal and we won’t be using it.

## Emojis

- ✅ Means the data is calibrated and ready to be archived
- ▶️ Means that data is in process of being calibrated
- ❓ Means that there is a problem needing to be solved
- 👀 Need to show Yvette
- 🍪 Means that it was a special cookie that was processed entirely by the pipeline.
- 🖼️ Need to check image for artefacts or more required cleaning.
- 📁 Means that the data is backed up to SOLAR

# 24A-411.sb45152540.eb45209965.60336.070794328705 ✅📁

- Calibrator is **3C48**
- Secondary calibrator **J0321+1221, J0424+0204**
- Science targets: **2A0335+096**, **A478** (single scan, not main target)
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas is 27

[24A-411.sb45152540.eb45209965.60336.070794328705](Data%20Processing/24A-411%20sb45152540%20eb45209965%2060336%20070794328705%201ba1feeec5b780349b9dcf33a649233f.md)

# **25A-157.sb47896990.eb48078690.60734.01560996528** ✅📁

- Calibrator is **3C48 (2)**
- Secondary calibrator is **J0321+1221 (0)**
- Science targets: **2A0335+096 (1)**
- Spectral windows 48, first 16 are C-band, last are X-band [8-12] GHz.
- Number of antennas is 26

[**25A-157.sb47896990.eb48078690.60734.01560996528**](Data%20Processing/25A-157%20sb47896990%20eb48078690%2060734%2001560996528%201d01feeec5b780298a02f70a3811412d.md)

# 25A-157.sb47896587.eb48188930.60749.83678572917 ✅📁

- Calibrator is **3C48 (0)**
- Secondary calibrator is **J0321+1221 (1)**
- Science targets: **2A0335+096 (2)**
- Spectral windows 48, first 16 are C-band, last are X-band [8-12] GHz.
- Number of antennas is 27

[25A-157.sb47896587.eb48188930.60749.83678572917](Data%20Processing/25A-157%20sb47896587%20eb48188930%2060749%2083678572917%201d01feeec5b7800a9db2cf88f986f4a8.md)

# 25A-157.sb47896788.eb48078564.60733.06076180555 ✅📁🍪

- Calibrator is **3C48 (0)**
- Secondary calibrator is **J0424+0204 (1)**
- Science targets: **A478 (2)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas is 26

[25A-157.sb47896788.eb48078564.60733.06076180555 ](Data%20Processing/25A-157%20sb47896788%20eb48078564%2060733%2006076180555%201f41feeec5b780f6a278e16dab64995d.md)

# **25A-157.sb47897178.eb48143348.60745.94845704861** ✅📁

- Calibrator is **3C48 (2)**
- Secondary calibrator is **J0424+0204 (0)**
- Science targets: **A478 (1)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas is 27

[25A-157.sb47897178.eb48143348.60745.94845704861](Data%20Processing/25A-157%20sb47897178%20eb48143348%2060745%2094845704861%201f41feeec5b780458b18ee312b8be945.md)

# 24A-411.sb45153015.eb45227399.60343.435757858795 ✅📁

- Primary calibrator: **3C286 (0)**
- Secondary calibrators: **J1436+2321 (1), J1616+459(3), J1719+1745 (5)**
- Science targets: **MS1455+2232 (2, 7x9=63m), A2204 (4, 7x9=63m), RXJ1720+2638 (6, 5x9=45m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 27.

[24A-411.sb45153015.eb45227399.60343.435757858795](Data%20Processing/24A-411%20sb45153015%20eb45227399%2060343%20435757858795%2020e1feeec5b780ccb385dfec6b9f93eb.md)

# **25A-157.sb47896383.eb48084831.60734.58634814815** ✅📁

- Primary calibrator: **1331+305=3C286 (0)**
- Secondary calibrators: **J1616+0459 (1), J1719+1745 (3)**
- Science targets: **A2204 (2, 36m), RXJ1720.1+2638 (4, 36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47896383.eb48084831.60734.58634814815**](Data%20Processing/25A-157%20sb47896383%20eb48084831%2060734%2058634814815%2020f1feeec5b7809f8318c01d7acbe228.md)

# 25A-157.sb47895952.eb48256632.60761.33700966435 ✅📁

- Primary calibrator: **1331+305=3C286 (4)**
- Secondary calibrators: **J1616+0459 (0), J1719+1745 (2)**
- Science targets: **A2204 (1, 36m), RXJ1720.1+2638 (3, 36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[25A-157.sb47895952.eb48256632.60761.33700966435](Data%20Processing/25A-157%20sb47895952%20eb48256632%2060761%2033700966435%202141feeec5b7802a99b1f7fc60716984.md)

# 24A-411.sb45152792.eb45228190.60344.213862488425 ✅📁

- Primary calibrator: **1331+305=3C286 (6)**
- Secondary calibrators: **J1031+0610 (0), J1058+0133 (2), J1150+2417 (4), 1331+305=3C286 (6 for A1795?)**
- Science targets: **Z3146 (1, 72m), RXCJ1115+0129 (3, 72m), A1413 (5, 36m), A1795 (7, 72m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 27.

[24A-411.sb45152792.eb45228190.60344.213862488425](Data%20Processing/24A-411%20sb45152792%20eb45228190%2060344%20213862488425%202161feeec5b780faadbedeb125a25b17.md)

# **25A-157.sb47894733.eb48078570.60733.28727417824** ✅📁

- Primary calibrator: **1331+305=3C286 (0)**
- Secondary calibrators: **J1041+0610 (1), J1058+0133 (3)**
- Science targets: **Z3146 (2, 36m), RXCJ1115+0129 (4, 36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47894733.eb48078570.60733.28727417824**](Data%20Processing/25A-157%20sb47894733%20eb48078570%2060733%2028727417824%202251feeec5b780d8b374e1d5fe512d5c.md)

# 25A-157.sb47894310.eb48188934.60750.12720050926 ✅📁

- Primary calibrator: **1331+305=3C286 (4)**
- Secondary calibrators: **J1041+0610 (0), J1058+0133 (2)**
- Science targets: **Z3146 (1, 36m), RXCJ1115+0129 (3, 36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 27.

[25A-157.sb47894310.eb48188934.60750.12720050926](Data%20Processing/25A-157%20sb47894310%20eb48188934%2060750%2012720050926%202281feeec5b780b3acb3e6be55d79baa.md)

# 25A-157.sb47894310.eb48187719.60748.13153532408 ❌📁🍪

- Primary calibrator: *None as observation died, using calibrator from 25A-157.sb47894310.eb48188934.60750.12720050926 above.* **1331+305=3C286 (4)**
- Secondary calibrators: **J1041+0610 (0), J1058+0133 (2)**
- Science targets: **Z3146 (1, 36m), RXCJ1115+0129 (3, 9m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.
- Number of antennas 26.

[25A-157.sb47894310.eb48187719.60748.13153532408](Data%20Processing/25A-157%20sb47894310%20eb48187719%2060748%2013153532408%2022b1feeec5b78019a87dcdeeef6cd9ce.md)

# **25A-157.sb47895724.eb48209198.60753.20907715277** ✅📁

- Primary calibrator: **1331+305=3C286 (0)**
- Secondary calibrators: **J1330+2509 (1), J1436+2321 (3)**
- Science targets: **A1795** **(2, 36m), MS1455+2232 (3, 36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47895724.eb48209198.60753.20907715277**](Data%20Processing/25A-157%20sb47895724%20eb48209198%2060753%2020907715277%2023e1feeec5b78088bcfcd4f452bea008.md)

# **25A-157.sb47896182.eb48256644.60761.48394760417** ✅📁

- Primary calibrator: **1331+305=3C286 (0)**
- Secondary calibrators: **J1330+2509 (1), J1436+2321 (3)**
- Science targets: **A1795** **(2, 36m), MS1455+2232 (3, 36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47896182.eb48256644.60761.48394760417**](Data%20Processing/25A-157%20sb47896182%20eb48256644%2060761%2048394760417%2023e1feeec5b780c098fedbcbebc9b7f3.md)

# **25A-157.sb47894939.eb48078696.60734.16955045139** ✅📁

- Primary calibrator: **1331+305=3C286 (2)**
- Secondary calibrators: **J1150+2417 (0)**
- Science targets: **A1413 (1, ~2hrs)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47894939.eb48078696.60734.16955045139**](Data%20Processing/25A-157%20sb47894939%20eb48078696%2060734%2016955045139%202421feeec5b780f9b005f8fc905c4d27.md)

# **25A-157.sb47895290.eb48084827.60734.36249717593** ✅📁

- Primary calibrator: **1331+305=3C286 (2)**
- Secondary calibrators: **J1150+2417 (0)**
- Science targets: **A1413 (1, ~2hrs)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47895290.eb48084827.60734.36249717593**](Data%20Processing/25A-157%20sb47895290%20eb48084827%2060734%2036249717593%2024a1feeec5b7806bad62c33396dfb839.md)

# **24A-411.sb45228321.eb45252099.60350.80962270833** ✅📁

- Primary calibrator: **0137+331=3C48 (7), J2130+0502 (0)**
- Secondary calibrators: **J2136+0041 (1), J2253+1608 (3), J0022+0014 (5)**
- Science targets: **RXJ2129+0005 (2, ~135m), A2626 (4, ~45m), ACTJ0022-0036 (6, ~81m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**24A-411.sb45228321.eb45252099.60350.80962270833**](Data%20Processing/24A-411%20sb45228321%20eb45252099%2060350%2080962270833%2024b1feeec5b7802bbea0d1ed9f18ad90.md)

# **25A-157.sb47856643.eb48084985.60734.6548690162** ✅📁🍪

- Primary calibrator: **0137+331=3C48 (7), J2130+0502 (0)**
- Secondary calibrators: **J2136+0041 (1), J2253+1608 (3), J0022+0014 (5)**
- Science targets: **RXJ2129+0005 (2, ~63m), A2626 (4, ~36m), ACTJ0022-0036 (6, ~36m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47856643.eb48084985.60734.6548690162**](Data%20Processing/25A-157%20sb47856643%20eb48084985%2060734%206548690162%202561feeec5b78092802bca9ae4c8389f.md)

# **25A-157.sb47856867.eb48085842.60734.77350795139** ✅📁

- Primary calibrator: **0137+331=3C48 (0)**
- Secondary calibrators: **J2136+0041 (1), J2253+1608 (3), J0022+0014 (5)**
- Science targets: **RXJ2129+0005 (2, ~63m), A2626 (4, ~45m), ACTJ0022-0036 (6, ~27m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**25A-157.sb47856867.eb48085842.60734.77350795139**](Data%20Processing/25A-157%20sb47856867%20eb48085842%2060734%2077350795139%202561feeec5b780c491c9c85c5232899f.md)

# **24A-411.sb44878514.eb45254944.60351.68494363426** ✅📁

- Primary calibrator: **0137+331=3C48 (7), J2130+0502 (0)**
- Secondary calibrators: **J2136+0041 (1), J2253+1608 (3), J0022+0014 (5)**
- Science targets: **RXJ2129+0005 (2, ~135m), A2626 (4, ~45m), ACTJ0022-0036 (6, ~81m)**
- Spectral windows 48, with 64 channels, First 16 are C-band and can be ignored. Remaining X-band [8, 12] GHz.
- Number of antennas 26.

[**24A-411.sb44878514.eb45254944.60351.68494363426**](Data%20Processing/24A-411%20sb44878514%20eb45254944%2060351%2068494363426%202571feeec5b780d99edef201a5c0ea5b.md)