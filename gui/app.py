"""
Main application window for cable sizing calculator.

Coordinates all GUI components and handles the main application logic.
"""
import sys
from pathlib import Path
from typing import Optional
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import CableInput
from core.calculator import CableSizingCalculator
from core.export import export_to_csv, export_to_pdf
from gui.input_frame import InputFrame
from gui.results_frame import ResultsFrame
from gui.chart_frame import ChartFrame


class CableSizingApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        self._last_inputs: Optional[CableInput] = None
        self._last_report = None

        self._configure_window()
        self._configure_theme()
        self._create_widgets()
        self._layout_widgets()

    def _configure_window(self) -> None:
        """Configure main window properties."""
        self.title("VoltGuard - IEC 60364-5-52")
        self.geometry("1450x900")
        self.minsize(1200, 750)

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def _configure_theme(self) -> None:
        """Configure application theme."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _create_widgets(self) -> None:
        """Create all main widgets."""
        # Header
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        
        # Load logo
        assets_path = Path(__file__).parent.parent / "assets"
        logo_path = assets_path / "logo_banner.png"
        
        try:
            pil_image = Image.open(logo_path)
            # Maintain aspect ratio, height around 60
            aspect_ratio = pil_image.width / pil_image.height
            logo_height = 60
            logo_width = int(logo_height * aspect_ratio)
            
            self.logo_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(logo_width, logo_height)
            )
            
            self.title_label = ctk.CTkLabel(
                self.header_frame,
                text="",
                image=self.logo_image
            )
        except Exception:
            # Fallback if image fails
            self.title_label = ctk.CTkLabel(
                self.header_frame,
                text="⚡ VoltGuard",
                font=ctk.CTkFont(size=24, weight="bold")
            )

        # Removed text subtitle as it's in the logo

        self.theme_var = ctk.StringVar(value="dark")
        self.theme_switch = ctk.CTkSwitch(
            self.header_frame, text="Dark Mode",
            variable=self.theme_var, onvalue="dark", offvalue="light",
            command=self._toggle_theme
        )

        # Content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.input_frame = InputFrame(
            self.content_frame,
            on_calculate=self._on_calculate,
            width=340,
        )

        self.results_frame = ResultsFrame(
            self.content_frame,
            on_export_csv=self._export_csv,
            on_export_pdf=self._export_pdf,
        )

        self.chart_frame = ChartFrame(self.content_frame)

        # Footer disclaimer
        self.footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.disclaimer_label = ctk.CTkLabel(
            self.footer_frame,
            text="⚠️ Disclaimer: For preliminary design only. Verify with manufacturer data and local regulations.",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )

    def _layout_widgets(self) -> None:
        """Layout all widgets."""
        # Header
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        self.title_label.pack(side="left", padx=20, pady=10)
        self.theme_switch.pack(side="right", padx=20, pady=10)

        # Content
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.input_frame.pack(side="left", fill="y", padx=(0, 5))
        self.results_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.chart_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Footer
        self.footer_frame.pack(fill="x")
        self.footer_frame.pack_propagate(False)
        self.disclaimer_label.pack(pady=5)

    def _toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        mode = self.theme_var.get()
        ctk.set_appearance_mode(mode)
        self.after(100, self._refresh_chart)

    def _refresh_chart(self) -> None:
        """Refresh the chart to apply theme changes."""
        if self._last_inputs:
            self._on_calculate(self._last_inputs)

    def _on_calculate(self, inputs: CableInput) -> None:
        """Handle calculate button click."""
        self._last_inputs = inputs

        calculator = CableSizingCalculator(inputs)
        results = calculator.calculate_all_sizes()
        recommended = calculator.get_recommended_size()

        # Generate and store report for export
        self._last_report = calculator.generate_report()
        self.results_frame.set_report(self._last_report)

        # Update results
        self.results_frame.update_results(results, recommended)

        # Update chart
        sizes, vd_percents, ampacities = calculator.get_chart_data()
        costs = [r.cost_estimate for r in results]
        recommended_index = None
        if recommended:
            for i, r in enumerate(results):
                if r.size == recommended.size:
                    recommended_index = i
                    break

        self.chart_frame.update_chart(
            sizes=sizes,
            vd_percents=vd_percents,
            ampacities=ampacities,
            design_current=inputs.design_current,
            recommended_index=recommended_index,
            costs=costs
        )

    def _export_csv(self, filepath: str) -> None:
        """Export results to CSV."""
        if self._last_report:
            try:
                export_to_csv(self._last_report, filepath)
                messagebox.showinfo("Export Complete", f"CSV saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")

    def _export_pdf(self, filepath: str) -> None:
        """Export results to PDF."""
        if self._last_report:
            try:
                export_to_pdf(self._last_report, filepath)
                messagebox.showinfo("Export Complete", f"PDF saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")

    def run(self) -> None:
        """Run the application main loop."""
        self.mainloop()
