# VoltGuard

VoltGuard is a professional cable sizing tool for electrical engineers with a modern Windows 11-style GUI, fully compliant with IEC 60364-5-52.

> ⚠️ **DISCLAIMER**: This tool is for preliminary design only. Always verify cable specifications with manufacturer data and comply with local regulations before installation.

## Features

### Standards Compliance

- **IEC 60364-5-52** compliant ampacity tables
- **XLPE 90°C** and **PVC 70°C** insulation support
- **Copper** and **Aluminum** conductors
- **Installation Methods**: C (wall), D (buried), E (tray), F (ladder)

### Enhanced Calculations

- **Parallel cable runs** (1-4 cables)
- **Burial depth derating** for Method D (0.5m, 0.7m, 1.0m)
- **Voltage drop** calculation (3-phase and single-phase)
- **Short-circuit** withstand verification
- **Protection device** (MCB) rating suggestions
- **Earth fault loop impedance** (Zs) calculation
- **Cost estimation** with customizable $/m

### Modern GUI

- Dark/light theme support
- Scrollable input panel
- Results table with pass/fail indicators
- Interactive charts with hover tooltips

### Export Options

- **CSV export** for spreadsheet analysis
- **PDF report** with inputs, equations, and full results

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI Application

```bash
python main.py
```

### Python API

```python
from core.models import CableInput, Material, InsulationType, InstallationMethod
from core.calculator import CableSizingCalculator

# Configure calculation parameters
# Note: Internal calculation constraints are encapsulated within the core module
inputs = CableInput(
    design_current=150.0,    # Amperes
    cable_length=75.0,       # Meters
    material=Material.COPPER,
    insulation=InsulationType.XLPE_90C,
    installation=InstallationMethod.METHOD_E,
    power_factor=0.9
)

# Initialize calculator with validated inputs
calculator = CableSizingCalculator(inputs)

# Execute sizing calculation (IEC 60364-5-52 logic)
result = calculator.get_recommended_size()

if result:
    print(f"Recommended Cable Size: {result.size} mm²")
    print(f"Effective Ampacity: {result.effective_ampacity:.1f} A")
    print(f"Voltage Drop: {result.voltage_drop_percent:.2f}%")
```

### Input Parameters

| Parameter | Description |
| --------- | ----------- |
| Design Current | Load current in Amperes |
| Cable Length | Route length in meters |
| Power Factor | cos φ (0-1) |
| Material | Copper or Aluminum |
| Insulation | XLPE 90°C or PVC 70°C |
| Installation | Method C, D, E, or F |
| Burial Depth | For Method D only |
| Parallel Cables | 1-4 cables in parallel |
| Derating Factors | Kt, Kg, Ks |
| SC Current | Short-circuit current in kA |
| Fault Time | Protection clearing time in seconds |

## Project Structure

```text
VoltGuard/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── config/
│   └── constants.py     # IEC ampacity tables
├── core/
│   ├── models.py        # Data classes
│   ├── calculator.py    # Calculation logic
│   └── export.py        # CSV/PDF export
└── gui/
    ├── app.py           # Main window
    ├── input_frame.py   # Input fields
    ├── results_frame.py # Results table
    └── chart_frame.py   # Interactive chart
```

## Calculation Equations

- **3-Phase Voltage Drop**: `ΔV = √3 × Ib × (R×cosφ + X×sinφ) × L / 1000`
- **1-Phase Voltage Drop**: `ΔV = 2 × Ib × (R×cosφ + X×sinφ) × L / 1000`
- **Short-Circuit Min Area**: `S = Isc × √t / k`
- **Earth Fault Loop**: `Zs = Ze + (R1 + R2)`

## License

MIT License
