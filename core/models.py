"""
Data models for cable sizing calculations.

Contains dataclasses for input parameters and calculation results.
"""
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class Material(Enum):
    """Conductor material type."""
    COPPER = "copper"
    ALUMINUM = "aluminum"


class InsulationType(Enum):
    """Cable insulation type."""
    XLPE_90C = "XLPE 90°C"
    PVC_70C = "PVC 70°C"


class InstallationMethod(Enum):
    """Cable installation method per IEC 60364-5-52."""
    METHOD_C = "Method C - Clipped direct to wall"
    METHOD_D = "Method D - Direct buried"
    METHOD_E = "Method E - Perforated cable tray"
    METHOD_F = "Method F - Cable ladder"


class PhaseSystem(Enum):
    """Electrical phase system."""
    THREE_PHASE = "3-phase"
    SINGLE_PHASE = "single-phase"


class BurialDepth(Enum):
    """Burial depth for Method D installation."""
    DEPTH_0_5M = "0.5m"
    DEPTH_0_7M = "0.7m"
    DEPTH_1_0M = "1.0m"


@dataclass
class CableInput:
    """Input parameters for cable sizing calculation."""

    design_current: float  # Ib in Amperes
    cable_length: float  # L in meters
    power_factor: float = 0.85  # cos φ (0-1)

    # Derating factors
    temp_factor: float = 1.0  # Kt - Temperature factor
    group_factor: float = 1.0  # Kg - Grouping factor
    soil_factor: float = 1.0  # Ks - Soil thermal resistivity factor

    # Short-circuit parameters
    short_circuit_current: float = 0.0  # Isc in Amperes
    fault_time: float = 1.0  # t in seconds

    # System configuration
    material: Material = Material.COPPER
    insulation: InsulationType = InsulationType.XLPE_90C
    installation: InstallationMethod = InstallationMethod.METHOD_C
    phase_system: PhaseSystem = PhaseSystem.THREE_PHASE

    # Enhanced options
    burial_depth: BurialDepth = BurialDepth.DEPTH_0_7M
    parallel_runs: int = 1  # Number of parallel cables (1-4)
    cost_per_meter: Optional[float] = None  # Custom cost override $/m

    @property
    def derating(self) -> float:
        """Calculate total derating factor."""
        return self.temp_factor * self.group_factor * self.soil_factor

    @property
    def sin_phi(self) -> float:
        """Calculate sin of power factor angle."""
        return math.sqrt(1 - self.power_factor ** 2)

    @property
    def current_per_cable(self) -> float:
        """Calculate current per cable when using parallel runs."""
        return self.design_current / max(1, self.parallel_runs)

    def validate(self) -> Optional[str]:
        """
        Validate input parameters.

        Returns:
            Error message if validation fails, None otherwise.
        """
        if self.design_current <= 0:
            return "Design current must be positive"
        if self.cable_length <= 0:
            return "Cable length must be positive"
        if not 0 < self.power_factor <= 1:
            return "Power factor must be between 0 and 1"
        if self.temp_factor <= 0 or self.group_factor <= 0 or self.soil_factor <= 0:
            return "Derating factors must be positive"
        if self.short_circuit_current < 0:
            return "Short-circuit current cannot be negative"
        if self.fault_time <= 0:
            return "Fault time must be positive"
        if not 1 <= self.parallel_runs <= 4:
            return "Parallel runs must be between 1 and 4"
        return None


@dataclass
class CableResult:
    """Result of cable sizing calculation for a specific size."""

    size: int  # Cable cross-section in mm²
    effective_ampacity: float  # Iz_eff in Amperes (after derating)
    voltage_drop_percent: float  # ΔV as percentage
    min_sc_area: float  # Minimum area for short-circuit withstand in mm²

    ampacity_pass: bool  # True if Ib <= Iz_eff
    voltage_drop_pass: bool  # True if VD <= limit
    sc_pass: bool  # True if size >= min_sc_area

    # Enhanced fields
    cost_estimate: float = 0.0  # Estimated cost for this size
    mcb_rating: int = 0  # Suggested MCB rating in Amperes
    earth_fault_loop: float = 0.0  # Earth fault loop impedance

    @property
    def overall_pass(self) -> bool:
        """Check if cable passes all criteria."""
        return self.ampacity_pass and self.voltage_drop_pass and self.sc_pass

    @property
    def status(self) -> str:
        """Get pass/fail status string."""
        return "PASS" if self.overall_pass else "FAIL"


@dataclass
class CalculationReport:
    """Complete calculation report for export."""

    inputs: CableInput
    results: List[CableResult]
    recommended: Optional[CableResult]
    timestamp: str = ""
    disclaimer: str = field(default_factory=lambda: (
        "DISCLAIMER: This calculation is based on IEC 60364-5-52 guidelines. "
        "Always verify cable specifications with manufacturer data and local "
        "regulations. This tool is for preliminary design purposes only."
    ))
