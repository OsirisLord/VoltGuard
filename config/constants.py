"""
Cable sizing constants and data tables.

Contains cable specifications based on IEC 60364-5-52 standards
for XLPE 90°C and PVC 70°C cables.

DISCLAIMER: Values are approximate and based on IEC 60364-5-52.
Always verify with manufacturer data for actual installations.
"""
import sys
from pathlib import Path
from typing import Dict, List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position, import-error
from core.models import (
    Material, InsulationType, InstallationMethod, PhaseSystem, BurialDepth
)


# Standard cable sizes in mm²
CABLE_SIZES: List[int] = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]

# Voltage drop limit (%)
VOLTAGE_DROP_LIMIT: float = 5.0

# Line voltages (V)
LINE_VOLTAGES: Dict[PhaseSystem, int] = {
    PhaseSystem.THREE_PHASE: 400,
    PhaseSystem.SINGLE_PHASE: 230,
}

# IEC Disclaimer
IEC_DISCLAIMER: str = (
    "DISCLAIMER: Calculations based on IEC 60364-5-52 guidelines. "
    "Values are approximate and for preliminary design only. "
    "Verify with manufacturer data and local regulations before installation."
)

# =============================================================================
# AMPACITY TABLES - IEC 60364-5-52
# Format: AMPACITY[insulation][material][method] = [values per size]
# =============================================================================

AMPACITY_TABLES: Dict[InsulationType, Dict[Material, Dict[InstallationMethod, List[int]]]] = {
    # XLPE 90°C Insulation
    InsulationType.XLPE_90C: {
        Material.COPPER: {
            InstallationMethod.METHOD_C: [
                19, 26, 35, 45, 61, 81, 106, 131, 158, 200, 241, 278, 318, 362, 424, 486
            ],
            InstallationMethod.METHOD_D: [
                22, 29, 38, 47, 63, 81, 104, 125, 148, 183, 216, 246, 278, 312, 361, 408
            ],
            InstallationMethod.METHOD_E: [
                22, 30, 40, 51, 70, 94, 119, 148, 180, 232, 282, 328, 379, 434, 514, 593
            ],
            InstallationMethod.METHOD_F: [
                22, 30, 40, 51, 70, 94, 119, 148, 180, 232, 282, 328, 379, 434, 514, 593
            ],
        },
        Material.ALUMINUM: {
            InstallationMethod.METHOD_C: [
                14, 20, 27, 35, 47, 63, 83, 102, 123, 156, 188, 216, 247, 283, 330, 379
            ],
            InstallationMethod.METHOD_D: [
                17, 22, 29, 36, 49, 62, 80, 96, 113, 140, 166, 189, 213, 240, 277, 313
            ],
            InstallationMethod.METHOD_E: [
                17, 23, 31, 40, 53, 73, 93, 116, 140, 181, 220, 255, 294, 339, 400, 464
            ],
            InstallationMethod.METHOD_F: [
                17, 23, 31, 40, 53, 73, 93, 116, 140, 181, 220, 255, 294, 339, 400, 464
            ],
        },
    },
    # PVC 70°C Insulation
    InsulationType.PVC_70C: {
        Material.COPPER: {
            InstallationMethod.METHOD_C: [
                15, 21, 28, 36, 50, 68, 89, 110, 134, 171, 207, 239, 275, 314, 369, 424
            ],
            InstallationMethod.METHOD_D: [
                18, 24, 31, 39, 52, 67, 86, 103, 122, 151, 179, 203, 230, 258, 297, 336
            ],
            InstallationMethod.METHOD_E: [
                17, 24, 32, 41, 57, 76, 96, 119, 144, 184, 223, 259, 299, 341, 403, 464
            ],
            InstallationMethod.METHOD_F: [
                17, 24, 32, 41, 57, 76, 96, 119, 144, 184, 223, 259, 299, 341, 403, 464
            ],
        },
        Material.ALUMINUM: {
            InstallationMethod.METHOD_C: [
                12, 16, 22, 28, 39, 53, 69, 86, 104, 133, 161, 186, 214, 245, 287, 330
            ],
            InstallationMethod.METHOD_D: [
                14, 18, 24, 30, 40, 52, 66, 80, 94, 117, 138, 157, 178, 200, 230, 260
            ],
            InstallationMethod.METHOD_E: [
                13, 18, 25, 32, 44, 59, 75, 92, 112, 143, 174, 201, 232, 265, 314, 361
            ],
            InstallationMethod.METHOD_F: [
                13, 18, 25, 32, 44, 59, 75, 92, 112, 143, 174, 201, 232, 265, 314, 361
            ],
        },
    },
}

# =============================================================================
# RESISTANCE AND REACTANCE TABLES (Ω/km at operating temperature)
# =============================================================================

# AC Resistance at operating temperature (90°C for XLPE, 70°C for PVC)
RESISTANCE_AC: Dict[InsulationType, Dict[Material, List[float]]] = {
    InsulationType.XLPE_90C: {
        Material.COPPER: [
            14.8, 8.87, 5.52, 3.69, 2.19, 1.38, 0.868, 0.625, 0.463, 0.321,
            0.232, 0.184, 0.150, 0.121, 0.0958, 0.0780
        ],
        Material.ALUMINUM: [
            24.4, 14.6, 9.09, 6.07, 3.61, 2.27, 1.43, 1.03, 0.762, 0.529,
            0.382, 0.303, 0.247, 0.199, 0.158, 0.128
        ],
    },
    InsulationType.PVC_70C: {
        Material.COPPER: [
            13.7, 8.21, 5.09, 3.39, 2.01, 1.26, 0.795, 0.572, 0.424, 0.294,
            0.213, 0.169, 0.137, 0.111, 0.0876, 0.0712
        ],
        Material.ALUMINUM: [
            22.5, 13.5, 8.36, 5.58, 3.31, 2.08, 1.31, 0.942, 0.699, 0.485,
            0.351, 0.278, 0.226, 0.183, 0.145, 0.118
        ],
    },
}

# Reactance (Ω/km) - varies less with temperature
REACTANCE: Dict[Material, List[float]] = {
    Material.COPPER: [
        0.115, 0.110, 0.107, 0.100, 0.094, 0.090, 0.086, 0.083, 0.080, 0.078,
        0.076, 0.075, 0.074, 0.073, 0.072, 0.071
    ],
    Material.ALUMINUM: [
        0.118, 0.112, 0.110, 0.103, 0.097, 0.093, 0.089, 0.086, 0.083, 0.081,
        0.079, 0.078, 0.076, 0.075, 0.074, 0.073
    ],
}

# =============================================================================
# K-FACTORS FOR SHORT-CIRCUIT CALCULATIONS
# =============================================================================

K_FACTORS: Dict[InsulationType, Dict[Material, int]] = {
    InsulationType.XLPE_90C: {
        Material.COPPER: 143,
        Material.ALUMINUM: 94,
    },
    InsulationType.PVC_70C: {
        Material.COPPER: 115,
        Material.ALUMINUM: 76,
    },
}

# =============================================================================
# DERATING FACTORS
# =============================================================================

# Burial depth correction factors for Method D
BURIAL_DEPTH_FACTORS: Dict[BurialDepth, float] = {
    BurialDepth.DEPTH_0_5M: 1.0,
    BurialDepth.DEPTH_0_7M: 0.97,
    BurialDepth.DEPTH_1_0M: 0.93,
}

# =============================================================================
# PROTECTION DEVICE RATINGS
# =============================================================================

# Standard MCB ratings (Amperes)
MCB_RATINGS: List[int] = [
    6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630
]

# =============================================================================
# CABLE COSTS (Approximate $/m - editable defaults)
# =============================================================================

CABLE_COSTS: Dict[Material, Dict[float, float]] = {
    Material.COPPER: {
        1.5: 0.50, 2.5: 0.75, 4: 1.10, 6: 1.50, 10: 2.50, 16: 4.00,
        25: 6.00, 35: 8.50, 50: 12.00, 70: 17.00, 95: 23.00, 120: 29.00,
        150: 36.00, 185: 45.00, 240: 58.00, 300: 73.00
    },
    Material.ALUMINUM: {
        1.5: 0.30, 2.5: 0.45, 4: 0.65, 6: 0.90, 10: 1.50, 16: 2.40,
        25: 3.60, 35: 5.10, 50: 7.20, 70: 10.20, 95: 13.80, 120: 17.40,
        150: 21.60, 185: 27.00, 240: 34.80, 300: 43.80
    },
}
