"""
Input frame for cable sizing calculator.

Contains all input fields for user parameters with enhanced options.
"""
import sys
from pathlib import Path
from typing import Any, Callable

import customtkinter as ctk

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position, import-error
from core.models import (
    CableInput, Material, InsulationType, InstallationMethod,
    PhaseSystem, BurialDepth
)
from gui.tooltip import Tooltip


class InputFrame(ctk.CTkScrollableFrame):
    """Scrollable frame containing all input fields."""

    def __init__(
        self,
        master: Any,
        on_calculate: Callable[[CableInput], None],
        **kwargs
    ):
        """
        Initialize input frame.

        Args:
            master: Parent widget.
            on_calculate: Callback function when calculate button is pressed.
        """
        super().__init__(master, label_text="Input Parameters", **kwargs)
        self.on_calculate = on_calculate

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self) -> None:
        """Create all input widgets."""
        # === Load Parameters Section ===
        self.load_label = ctk.CTkLabel(
            self, text="Load Parameters",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        self.current_label = ctk.CTkLabel(self, text="Design Current (A):")
        self.current_entry = ctk.CTkEntry(self, placeholder_text="e.g., 100")

        self.length_label = ctk.CTkLabel(self, text="Cable Length (m):")
        self.length_entry = ctk.CTkEntry(self, placeholder_text="e.g., 50")

        self.pf_label = ctk.CTkLabel(self, text="Power Factor:")
        self.pf_entry = ctk.CTkEntry(self, placeholder_text="0.85")
        self.pf_entry.insert(0, "0.85")

        # Tooltips for Load Parameters
        Tooltip(self.current_label, "The full load current of the circuit in Amperes (A).")
        Tooltip(self.length_label, "One-way length of the cable run in meters (m).")
        Tooltip(
            self.pf_label,
            "Power Factor (cos φ) of the load.\n"
            "Typical values: 0.8 to 0.9 for motors, 1.0 for resistive."
        )

        # === System Configuration Section ===
        self.config_label = ctk.CTkLabel(
            self, text="System Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        # Material
        self.material_label = ctk.CTkLabel(self, text="Material:")
        self.material_var = ctk.StringVar(value="Copper")
        self.material_menu = ctk.CTkOptionMenu(
            self, values=["Copper", "Aluminum"],
            variable=self.material_var
        )

        # Insulation
        self.insulation_label = ctk.CTkLabel(self, text="Insulation:")
        self.insulation_var = ctk.StringVar(value="XLPE 90°C")
        self.insulation_menu = ctk.CTkOptionMenu(
            self, values=["XLPE 90°C", "PVC 70°C"],
            variable=self.insulation_var
        )

        # Installation method
        self.install_label = ctk.CTkLabel(self, text="Installation:")
        self.install_var = ctk.StringVar(value="Method C - Wall")
        self.install_menu = ctk.CTkOptionMenu(
            self, values=[
                "Method C - Wall",
                "Method D - Buried",
                "Method E - Tray",
                "Method F - Ladder"
            ],
            variable=self.install_var,
            command=self._on_install_change
        )

        # Burial depth (only for Method D)
        self.depth_label = ctk.CTkLabel(self, text="Burial Depth:")
        self.depth_var = ctk.StringVar(value="0.7m")
        self.depth_menu = ctk.CTkOptionMenu(
            self, values=["0.5m", "0.7m", "1.0m"],
            variable=self.depth_var
        )

        # Phase system
        self.phase_label = ctk.CTkLabel(self, text="Phase System:")
        self.phase_var = ctk.StringVar(value="3-Phase 400V")
        self.phase_menu = ctk.CTkOptionMenu(
            self, values=["3-Phase 400V", "1-Phase 230V"],
            variable=self.phase_var
        )

        # Parallel runs
        self.parallel_label = ctk.CTkLabel(self, text="Parallel Cables:")
        self.parallel_var = ctk.StringVar(value="1")
        self.parallel_menu = ctk.CTkOptionMenu(
            self, values=["1", "2", "3", "4"],
            variable=self.parallel_var
        )

        # Tooltips for System Configuration
        Tooltip(
            self.material_label,
            "Conductor material.\n"
            "Copper: Better conductivity, smaller size.\n"
            "Aluminum: Cheaper, lighter, larger size."
        )
        Tooltip(
            self.insulation_label,
            "Cable insulation type.\n"
            "XLPE: 90°C rating (higher capacity).\n"
            "PVC: 70°C rating (standard)."
        )
        Tooltip(
            self.install_label,
            "Method of installation affects heat dissipation.\n"
            "C: Clipped direct\n"
            "D: Buried in ground\n"
            "E: Perforated tray\n"
            "F: Free air/ladder"
        )
        Tooltip(
            self.depth_label,
            "Depth of burial (only for grounded cables).\n"
            "Deeper cables have lower rating due to soil insulation."
        )
        Tooltip(self.phase_label, "System voltage and phase configuration.")
        Tooltip(self.parallel_label, "Number of cables per phase to increase total capacity.")

        # === Derating Factors Section ===
        self.derating_label = ctk.CTkLabel(
            self, text="Derating Factors",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        self.temp_label = ctk.CTkLabel(self, text="Temperature (Kt):")
        self.temp_entry = ctk.CTkEntry(self, placeholder_text="1.0")
        self.temp_entry.insert(0, "1.0")

        self.group_label = ctk.CTkLabel(self, text="Grouping (Kg):")
        self.group_entry = ctk.CTkEntry(self, placeholder_text="1.0")
        self.group_entry.insert(0, "1.0")

        self.soil_label = ctk.CTkLabel(self, text="Soil (Ks):")
        self.soil_entry = ctk.CTkEntry(self, placeholder_text="1.0")
        self.soil_entry.insert(0, "1.0")

        # Tooltips for Derating Factors
        # Tooltips for Derating Factors
        Tooltip(
            self.temp_label,
            "Ambient Temperature Correction Factor (Kt).\n"
            "< 1.0 if temp > 30°C (Air) or > 20°C (Ground)."
        )
        Tooltip(
            self.group_label,
            "Group Rating Factor (Kg).\n"
            "Reduces capacity when multiple circuits are bundled together."
        )
        Tooltip(
            self.soil_label,
            "Soil Thermal Resistivity Factor (Ks).\n"
            "Adjust for soil conditions different from 2.5 K.m/W."
        )

        # === Short-Circuit Section ===
        self.sc_label = ctk.CTkLabel(
            self, text="Short-Circuit",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        self.isc_label = ctk.CTkLabel(self, text="SC Current (kA):")
        self.isc_entry = ctk.CTkEntry(self, placeholder_text="e.g., 10")

        self.fault_label = ctk.CTkLabel(self, text="Fault Time (s):")
        self.fault_entry = ctk.CTkEntry(self, placeholder_text="1.0")
        self.fault_entry.insert(0, "1.0")
        
        # Tooltips for Short-Circuit
        # Tooltips for Short-Circuit
        Tooltip(
            self.isc_label,
            "Propspective Short-Circuit Current (Isc) in kA.\n"
            "Used to verify cable thermal withstand."
        )
        Tooltip(
            self.fault_label,
            "Duration of the short-circuit fault in seconds.\n"
            "Typically determined by protection device clearing time."
        )

        # === Cost Section ===
        self.cost_label = ctk.CTkLabel(
            self, text="Cost Estimation",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        self.cost_override_label = ctk.CTkLabel(self, text="Custom $/m:")
        self.cost_override_entry = ctk.CTkEntry(self, placeholder_text="(optional)")

        # Calculate button
        self.calculate_btn = ctk.CTkButton(
            self, text="⚡ Calculate",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45, command=self._on_calculate_click
        )

        # Error label
        self.error_label = ctk.CTkLabel(
            self, text="", text_color="red", wraplength=280
        )

    def _layout_widgets(self) -> None:
        """Layout all widgets using grid."""
        row = 0

        # Load parameters
        self.load_label.grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky="w")
        row += 1

        self.current_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.current_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.length_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.length_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.pf_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.pf_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        # System configuration
        self.config_label.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="w")
        row += 1

        self.material_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.material_menu.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.insulation_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.insulation_menu.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.install_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.install_menu.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.depth_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.depth_menu.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        self._depth_row = row
        row += 1

        self.phase_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.phase_menu.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.parallel_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.parallel_menu.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        # Derating factors
        self.derating_label.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="w")
        row += 1

        self.temp_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.temp_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.group_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.group_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.soil_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.soil_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        # Short-circuit
        self.sc_label.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="w")
        row += 1

        self.isc_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.isc_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        self.fault_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.fault_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        # Cost
        self.cost_label.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="w")
        row += 1

        self.cost_override_label.grid(row=row, column=0, padx=5, pady=3, sticky="e")
        self.cost_override_entry.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
        row += 1

        # Error and calculate
        self.error_label.grid(row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        self.calculate_btn.grid(row=row, column=0, columnspan=2, pady=(5, 15), padx=10, sticky="ew")

        self.columnconfigure(1, weight=1)

        # Initially hide burial depth
        self._on_install_change(self.install_var.get())

    def _on_install_change(self, value: str) -> None:
        """Show/hide burial depth based on installation method."""
        if "Buried" in value:
            self.depth_label.grid()
            self.depth_menu.grid()
        else:
            self.depth_label.grid_remove()
            self.depth_menu.grid_remove()

    def _get_float(self, entry: ctk.CTkEntry, default: float = 0.0) -> float:
        """Get float value from entry widget."""
        try:
            value = entry.get().strip()
            return float(value) if value else default
        except ValueError:
            return default

    def _on_calculate_click(self) -> None:
        """Handle calculate button click."""
        self.error_label.configure(text="")

        try:
            # Parse material
            material = (Material.COPPER if self.material_var.get() == "Copper"
                       else Material.ALUMINUM)

            # Parse insulation
            insulation = (InsulationType.XLPE_90C if "XLPE" in self.insulation_var.get()
                         else InsulationType.PVC_70C)

            # Parse installation
            install_val = self.install_var.get()
            if "Method C" in install_val:
                installation = InstallationMethod.METHOD_C
            elif "Method D" in install_val:
                installation = InstallationMethod.METHOD_D
            elif "Method E" in install_val:
                installation = InstallationMethod.METHOD_E
            else:
                installation = InstallationMethod.METHOD_F

            # Parse burial depth
            depth_val = self.depth_var.get()
            if "0.5" in depth_val:
                burial_depth = BurialDepth.DEPTH_0_5M
            elif "1.0" in depth_val:
                burial_depth = BurialDepth.DEPTH_1_0M
            else:
                burial_depth = BurialDepth.DEPTH_0_7M

            # Parse phase
            phase_system = (PhaseSystem.THREE_PHASE if "3-Phase" in self.phase_var.get()
                           else PhaseSystem.SINGLE_PHASE)

            # Parse parallel runs
            parallel_runs = int(self.parallel_var.get())

            # Parse custom cost
            cost_str = self.cost_override_entry.get().strip()
            cost_override = float(cost_str) if cost_str else None

            # Create input
            inputs = CableInput(
                design_current=self._get_float(self.current_entry),
                cable_length=self._get_float(self.length_entry),
                power_factor=self._get_float(self.pf_entry, 0.85),
                temp_factor=self._get_float(self.temp_entry, 1.0),
                group_factor=self._get_float(self.group_entry, 1.0),
                soil_factor=self._get_float(self.soil_entry, 1.0),
                short_circuit_current=self._get_float(self.isc_entry) * 1000,
                fault_time=self._get_float(self.fault_entry, 1.0),
                material=material,
                insulation=insulation,
                installation=installation,
                phase_system=phase_system,
                burial_depth=burial_depth,
                parallel_runs=parallel_runs,
                cost_per_meter=cost_override,
            )

            # Validate
            error = inputs.validate()
            if error:
                self.error_label.configure(text=f"Error: {error}")
                return

            self.on_calculate(inputs)

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.error_label.configure(text=f"Error: {str(e)}")
