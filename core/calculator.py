"""
Cable sizing calculator.

Implements the core calculation logic for cable sizing based on
ampacity, voltage drop, and short-circuit requirements per IEC 60364-5-52.
"""
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.constants import (
    CABLE_SIZES,
    VOLTAGE_DROP_LIMIT,
    LINE_VOLTAGES,
    AMPACITY_TABLES,
    RESISTANCE_AC,
    REACTANCE,
    K_FACTORS,
    BURIAL_DEPTH_FACTORS,
    MCB_RATINGS,
    CABLE_COSTS,
)
from core.models import (
    CableInput,
    CableResult,
    CalculationReport,
    PhaseSystem,
    InstallationMethod,
)


class CableSizingCalculator:
    """Calculator for electrical cable sizing per IEC 60364-5-52."""

    def __init__(self, inputs: CableInput):
        """
        Initialize calculator with input parameters.

        Args:
            inputs: CableInput dataclass with all input parameters.
        """
        self.inputs = inputs
        self._results: Optional[List[CableResult]] = None

    @property
    def line_voltage(self) -> int:
        """Get line voltage based on phase system."""
        return LINE_VOLTAGES[self.inputs.phase_system]

    @property
    def k_factor(self) -> int:
        """Get k-factor for short-circuit calculation."""
        return K_FACTORS[self.inputs.insulation][self.inputs.material]

    @property
    def burial_depth_factor(self) -> float:
        """Get burial depth derating factor for Method D."""
        if self.inputs.installation == InstallationMethod.METHOD_D:
            return BURIAL_DEPTH_FACTORS.get(self.inputs.burial_depth, 1.0)
        return 1.0

    @property
    def total_derating(self) -> float:
        """Calculate total derating including burial depth."""
        return self.inputs.derating * self.burial_depth_factor

    def _get_base_ampacity(self) -> List[int]:
        """Get base ampacity table based on insulation, material and installation."""
        return AMPACITY_TABLES[self.inputs.insulation][self.inputs.material][
            self.inputs.installation
        ]

    def _get_resistance(self, index: int) -> float:
        """Get AC resistance for cable size at given index."""
        return RESISTANCE_AC[self.inputs.insulation][self.inputs.material][index]

    def _get_reactance(self, index: int) -> float:
        """Get reactance for cable size at given index."""
        return REACTANCE[self.inputs.material][index]

    def _get_cable_cost(self, size: float) -> float:
        """Get cable cost per meter for given size."""
        if self.inputs.cost_per_meter is not None:
            return self.inputs.cost_per_meter
        return CABLE_COSTS.get(self.inputs.material, {}).get(size, 0.0)

    def _calculate_voltage_drop(self, index: int) -> float:
        """
        Calculate voltage drop for cable size at given index.

        For parallel cables, uses current per cable and effective impedance.

        Args:
            index: Index of cable size in CABLE_SIZES.

        Returns:
            Voltage drop in Volts.
        """
        resistance = self._get_resistance(index) / self.inputs.parallel_runs
        reactance = self._get_reactance(index) / self.inputs.parallel_runs

        impedance_drop = (
            resistance * self.inputs.power_factor +
            reactance * self.inputs.sin_phi
        )

        if self.inputs.phase_system == PhaseSystem.THREE_PHASE:
            delta_v = (
                math.sqrt(3) * self.inputs.design_current *
                impedance_drop * self.inputs.cable_length
            ) / 1000
        else:
            delta_v = (
                2 * self.inputs.design_current *
                impedance_drop * self.inputs.cable_length
            ) / 1000

        return delta_v

    def _calculate_min_sc_area(self) -> float:
        """
        Calculate minimum cable area for short-circuit withstand.

        Returns:
            Minimum cross-sectional area in mm².
        """
        if self.inputs.short_circuit_current <= 0:
            return 0.0
        # For parallel cables, SC current is divided among them
        sc_per_cable = self.inputs.short_circuit_current / self.inputs.parallel_runs
        return (sc_per_cable * math.sqrt(self.inputs.fault_time)) / self.k_factor

    def _calculate_mcb_rating(self, effective_ampacity: float) -> int:
        """
        Suggest appropriate MCB rating based on ampacity.

        Args:
            effective_ampacity: Effective current carrying capacity.

        Returns:
            Suggested MCB rating in Amperes.
        """
        # MCB rating should be >= Ib but <= Iz
        for rating in MCB_RATINGS:
            if rating >= self.inputs.design_current and rating <= effective_ampacity:
                return rating
        # If no suitable rating found, return the next one above Ib
        for rating in MCB_RATINGS:
            if rating >= self.inputs.design_current:
                return rating
        return MCB_RATINGS[-1]

    def _calculate_earth_fault_loop(self, index: int) -> float:
        """
        Calculate earth fault loop impedance (Zs).

        Simplified calculation: Zs = Ze + (R1 + R2)
        Where Ze is external impedance (assumed 0.35Ω typical)
        and R1 + R2 is phase-earth loop for the cable.

        Args:
            index: Index of cable size in CABLE_SIZES.

        Returns:
            Earth fault loop impedance in Ohms.
        """
        ze_typical = 0.35  # Typical external earth fault loop impedance
        resistance = self._get_resistance(index)
        # Assume protective conductor is same size
        r1_r2 = 2 * resistance * (self.inputs.cable_length / 1000)
        return ze_typical + r1_r2 / self.inputs.parallel_runs

    def calculate_for_size(self, index: int) -> CableResult:
        """
        Calculate result for a specific cable size.

        Args:
            index: Index of cable size in CABLE_SIZES.

        Returns:
            CableResult with all calculation results.
        """
        size = CABLE_SIZES[index]
        base_ampacity = self._get_base_ampacity()[index]
        # For parallel cables, total ampacity is multiplied
        effective_ampacity = base_ampacity * self.total_derating * self.inputs.parallel_runs

        # Voltage drop calculation
        delta_v = self._calculate_voltage_drop(index)
        vd_percent = (delta_v / self.line_voltage) * 100

        # Short-circuit calculation
        min_sc_area = self._calculate_min_sc_area()

        # Check criteria
        ampacity_pass = self.inputs.design_current <= effective_ampacity
        vd_pass = vd_percent <= VOLTAGE_DROP_LIMIT
        sc_pass = size >= min_sc_area

        # Cost estimation (total for all parallel runs)
        cost_per_m = self._get_cable_cost(size)
        total_cost = cost_per_m * self.inputs.cable_length * self.inputs.parallel_runs

        # MCB rating suggestion
        mcb_rating = self._calculate_mcb_rating(effective_ampacity)

        # Earth fault loop impedance
        earth_fault_loop = self._calculate_earth_fault_loop(index)

        return CableResult(
            size=size,
            effective_ampacity=effective_ampacity,
            voltage_drop_percent=vd_percent,
            min_sc_area=min_sc_area,
            ampacity_pass=ampacity_pass,
            voltage_drop_pass=vd_pass,
            sc_pass=sc_pass,
            cost_estimate=total_cost,
            mcb_rating=mcb_rating,
            earth_fault_loop=earth_fault_loop,
        )

    def calculate_all_sizes(self) -> List[CableResult]:
        """
        Calculate results for all standard cable sizes.

        Returns:
            List of CableResult for each cable size.
        """
        if self._results is None:
            self._results = [
                self.calculate_for_size(i)
                for i in range(len(CABLE_SIZES))
            ]
        return self._results

    def get_recommended_size(self) -> Optional[CableResult]:
        """
        Get the smallest cable size that passes all criteria.

        Returns:
            CableResult for recommended size, or None if no size passes.
        """
        results = self.calculate_all_sizes()
        for result in results:
            if result.overall_pass:
                return result
        return None

    def get_chart_data(self) -> Tuple[List[float], List[float], List[float]]:
        """
        Get data for plotting charts.

        Returns:
            Tuple of (sizes, voltage_drop_percentages, effective_ampacities).
        """
        results = self.calculate_all_sizes()
        sizes = [r.size for r in results]
        vd_percents = [r.voltage_drop_percent for r in results]
        ampacities = [r.effective_ampacity for r in results]
        return sizes, vd_percents, ampacities

    def generate_report(self) -> CalculationReport:
        """
        Generate a complete calculation report.

        Returns:
            CalculationReport with all data for export.
        """
        results = self.calculate_all_sizes()
        recommended = self.get_recommended_size()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return CalculationReport(
            inputs=self.inputs,
            results=results,
            recommended=recommended,
            timestamp=timestamp,
        )
