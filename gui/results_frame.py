"""
Results frame for cable sizing calculator.

Displays calculation results with export functionality.
"""

import sys
from pathlib import Path
from tkinter import filedialog
from typing import Any, List, Optional, Callable

import customtkinter as ctk

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import CableResult, CalculationReport
from gui.tooltip import Tooltip


class ResultsFrame(ctk.CTkFrame):
    """Frame displaying calculation results with export buttons."""

    def __init__(
        self,
        master: Any,
        on_export_csv: Optional[Callable[[str], None]] = None,
        on_export_pdf: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        """Initialize results frame."""
        super().__init__(master, **kwargs)
        self.on_export_csv = on_export_csv
        self.on_export_pdf = on_export_pdf
        self._report: Optional[CalculationReport] = None

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Title and export buttons
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Calculation Results",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.export_csv_btn = ctk.CTkButton(
            self.header_frame, text="📊 CSV", width=70, command=self._on_export_csv
        )
        self.export_pdf_btn = ctk.CTkButton(
            self.header_frame, text="📄 PDF", width=70, command=self._on_export_pdf
        )

        # Recommendation panel
        self.rec_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"))
        self.rec_title = ctk.CTkLabel(
            self.rec_frame,
            text="Recommended Cable Size",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.rec_size_label = ctk.CTkLabel(
            self.rec_frame,
            text="--",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#1a73e8", "#4da6ff"),
        )
        self.rec_details_label = ctk.CTkLabel(
            self.rec_frame, text="Enter parameters and click Calculate", wraplength=350
        )

        # Results table
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="All Cable Sizes")

        # Table headers
        self.headers = [
            "Size",
            "Ampacity",
            "VD%",
            "MCB",
            "Zs",
            "Cost",
            "Amp",
            "VD",
            "SC",
            "Status",
        ]
        self.header_labels: List[ctk.CTkLabel] = []
        for header in self.headers:
            width = 85 if header == "Cost" else 55
            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=width,
            )
            self.header_labels.append(label)

            # Tooltips for headers
            if header == "Amp":
                Tooltip(label, "Effective Ampacity (A) after derating.")
            elif header == "VD":
                Tooltip(
                    label, "Voltage Drop (%).\nLimit: 3% for lighting, 5% for other."
                )
            elif header == "MCB":
                Tooltip(label, "Resulting MCB/Breaker rating (A).")
            elif header == "Zs":
                Tooltip(label, "Earth Fault Loop Impedance (Ohms).")
            elif header == "SC":
                Tooltip(label, "Short-Circuit thermal withstand status.")

        self.result_rows: List[List[ctk.CTkLabel]] = []

    def _layout_widgets(self) -> None:
        """Layout all widgets."""
        # Header with export buttons
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.title_label.pack(side="left")
        self.export_pdf_btn.pack(side="right", padx=2)
        self.export_csv_btn.pack(side="right", padx=2)

        # Recommendation panel
        self.rec_frame.pack(fill="x", padx=10, pady=5)
        self.rec_title.pack(pady=(10, 5))
        self.rec_size_label.pack(pady=5)
        self.rec_details_label.pack(pady=(5, 10))

        # Table
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Layout headers
        for col, label in enumerate(self.header_labels):
            label.grid(row=0, column=col, padx=1, pady=5, sticky="ew")

    def _clear_results(self) -> None:
        """Clear existing result rows."""
        for row_labels in self.result_rows:
            for label in row_labels:
                label.destroy()
        self.result_rows.clear()

    def _on_export_csv(self) -> None:
        """Handle CSV export button click."""
        if self._report and self.on_export_csv:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Export to CSV",
            )
            if filepath:
                self.on_export_csv(filepath)

    def _on_export_pdf(self) -> None:
        """Handle PDF export button click."""
        if self._report and self.on_export_pdf:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Export to PDF",
            )
            if filepath:
                self.on_export_pdf(filepath)

    def set_report(self, report: CalculationReport) -> None:
        """Store the report for export."""
        self._report = report

    def update_results(
        self, results: List[CableResult], recommended: Optional[CableResult]
    ) -> None:
        """Update the results display."""
        self._clear_results()

        # Update recommendation panel
        if recommended:
            self.rec_size_label.configure(text=f"{recommended.size} mm²")
            details = (
                f"Ampacity: {recommended.effective_ampacity:.1f} A  |  "
                f"VD: {recommended.voltage_drop_percent:.2f}%\n"
                f"MCB: {recommended.mcb_rating}A  |  "
                f"Zs: {recommended.earth_fault_loop:.3f}Ω  |  "
                f"Cost: ${recommended.cost_estimate:.0f}"
            )
            self.rec_details_label.configure(text=details)
        else:
            self.rec_size_label.configure(text="None")
            self.rec_details_label.configure(
                text="No suitable size found. Try larger cables or parallel runs."
            )

        # Populate table
        for row_idx, result in enumerate(results, start=1):
            is_recommended = recommended and result.size == recommended.size

            if is_recommended:
                text_color = ("#155724", "#98d4a0")
            elif result.overall_pass:
                text_color = ("#28a745", "#5cb85c")
            else:
                text_color = ("#dc3545", "#e74c3c")

            row_data = [
                f"{result.size}",
                f"{result.effective_ampacity:.0f}",
                f"{result.voltage_drop_percent:.1f}",
                f"{result.mcb_rating}",
                f"{result.earth_fault_loop:.2f}",
                f"${result.cost_estimate:.0f}",
                "✓" if result.ampacity_pass else "✗",
                "✓" if result.voltage_drop_pass else "✗",
                "✓" if result.sc_pass else "✗",
                result.status,
            ]

            row_labels: List[ctk.CTkLabel] = []
            for col, value in enumerate(row_data):
                # Increase width for Cost column (index 5)
                width = 85 if col == 5 else 55
                label = ctk.CTkLabel(
                    self.table_frame,
                    text=value,
                    width=width,
                    text_color=text_color if col >= 6 else None,
                    font=ctk.CTkFont(weight="bold") if is_recommended else None,
                )
                label.grid(row=row_idx, column=col, padx=1, pady=1, sticky="ew")
                row_labels.append(label)

            self.result_rows.append(row_labels)

        for col in range(len(self.headers)):
            self.table_frame.columnconfigure(col, weight=1)
