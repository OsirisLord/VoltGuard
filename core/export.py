"""
Export functionality for cable sizing calculator.

Supports exporting results to CSV and PDF formats.
"""

import sys
from pathlib import Path
from typing import Optional

import csv
from fpdf import FPDF

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.constants import VOLTAGE_DROP_LIMIT
from core.models import CalculationReport


def export_to_csv(report: CalculationReport, filepath: str) -> None:
    """
    Export calculation results to CSV file.

    Args:
        report: CalculationReport with all data.
        filepath: Path to save CSV file.
    """
    data = []
    for result in report.results:
        data.append(
            {
                "Size (mm²)": result.size,
                "Ampacity (A)": round(result.effective_ampacity, 1),
                "Voltage Drop (%)": round(result.voltage_drop_percent, 2),
                "SC Min Area (mm²)": round(result.min_sc_area, 2),
                "MCB Rating (A)": result.mcb_rating,
                "Zs (Ω)": round(result.earth_fault_loop, 3),
                "Cost ($)": round(result.cost_estimate, 2),
                "Ampacity OK": "Yes" if result.ampacity_pass else "No",
                "VD OK": "Yes" if result.voltage_drop_pass else "No",
                "SC OK": "Yes" if result.sc_pass else "No",
                "Status": result.status,
            }
        )

    if not data:
        return

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    except IOError as e:
        raise Exception(f"File IO Error: {e}")


class PDFReport(FPDF):
    """Custom PDF class for cable sizing reports."""

    def header(self):
        """Add header to each page."""
        self.set_font("Helvetica", "B", 16)
        self.cell(
            0,
            10,
            "VoltGuard Calculation Report",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_font("Helvetica", "I", 10)
        self.cell(
            0, 6, "IEC 60364-5-52 Compliant", align="C", new_x="LMARGIN", new_y="NEXT"
        )
        self.ln(5)

    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def export_to_pdf(
    report: CalculationReport,
    filepath: str,
    engineer_name: Optional[str] = None,
    approver_name: Optional[str] = None,
) -> None:
    """
    Export calculation results to PDF file.

    Args:
        report: CalculationReport with all data.
        filepath: Path to save PDF file.
        engineer_name: Optional name of the design engineer.
        approver_name: Optional name of the approver.
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Timestamp
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {report.timestamp}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Input Summary Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Input Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    inputs = report.inputs
    input_data = [
        ("Design Current", f"{inputs.design_current:.1f} A"),
        ("Cable Length", f"{inputs.cable_length:.1f} m"),
        ("Power Factor", f"{inputs.power_factor:.2f}"),
        ("Material", inputs.material.value.title()),
        ("Insulation", inputs.insulation.value),
        ("Installation", inputs.installation.value),
        ("Phase System", inputs.phase_system.value),
        ("Parallel Runs", str(inputs.parallel_runs)),
        ("Temperature Factor (Kt)", f"{inputs.temp_factor:.2f}"),
        ("Grouping Factor (Kg)", f"{inputs.group_factor:.2f}"),
        ("Soil Factor (Ks)", f"{inputs.soil_factor:.2f}"),
        ("Short-Circuit Current", f"{inputs.short_circuit_current / 1000:.2f} kA"),
        ("Fault Time", f"{inputs.fault_time:.2f} s"),
    ]

    for label, value in input_data:
        pdf.cell(70, 6, label + ":", new_x="RIGHT")
        pdf.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Recommendation Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Recommendation", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    if report.recommended:
        rec = report.recommended
        pdf.set_fill_color(200, 255, 200)
        pdf.cell(
            0,
            8,
            f"Recommended Cable Size: {rec.size} mm2",
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.cell(
            0,
            6,
            f"Effective Ampacity: {rec.effective_ampacity:.1f} A",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.cell(
            0,
            6,
            f"Voltage Drop: {rec.voltage_drop_percent:.2f}% (Limit: {VOLTAGE_DROP_LIMIT}%)",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.cell(
            0,
            6,
            f"Suggested MCB Rating: {rec.mcb_rating} A",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.cell(
            0,
            6,
            f"Earth Fault Loop Impedance (Zs): {rec.earth_fault_loop:.3f} Ohms",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.cell(
            0,
            6,
            f"Estimated Cost: ${rec.cost_estimate:.2f}",
            new_x="LMARGIN",
            new_y="NEXT",
        )
    else:
        pdf.set_fill_color(255, 200, 200)
        pdf.cell(
            0,
            8,
            "No suitable cable size found. Consider larger cables or parallel runs.",
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(5)

    # Results Table Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "All Cable Sizes", new_x="LMARGIN", new_y="NEXT")

    # Table header
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(220, 220, 220)
    col_widths = [18, 22, 18, 22, 18, 18, 22, 16, 14, 14, 16]
    headers = [
        "Size",
        "Ampacity",
        "VD %",
        "SC Min",
        "MCB",
        "Zs",
        "Cost",
        "Amp",
        "VD",
        "SC",
        "Status",
    ]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 6, header, border=1, fill=True, align="C")
    pdf.ln()

    # Table data
    pdf.set_font("Helvetica", "", 7)
    for result in report.results:
        is_recommended = report.recommended and result.size == report.recommended.size

        if is_recommended:
            pdf.set_fill_color(200, 255, 200)
        elif result.overall_pass:
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_fill_color(255, 230, 230)

        row_data = [
            f"{result.size}",
            f"{result.effective_ampacity:.1f}",
            f"{result.voltage_drop_percent:.2f}",
            f"{result.min_sc_area:.2f}",
            f"{result.mcb_rating}",
            f"{result.earth_fault_loop:.3f}",
            f"${result.cost_estimate:.0f}",
            "Y" if result.ampacity_pass else "N",
            "Y" if result.voltage_drop_pass else "N",
            "Y" if result.sc_pass else "N",
            result.status,
        ]

        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 5, data, border=1, fill=True, align="C")
        pdf.ln()

    pdf.ln(5)

    # Equations Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Calculation Equations", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)

    equations = [
        "3-Phase Voltage Drop: dV = sqrt(3) * Ib * (R*cos(phi) + X*sin(phi)) * L / 1000",
        "1-Phase Voltage Drop: dV = 2 * Ib * (R*cos(phi) + X*sin(phi)) * L / 1000",
        "Short-Circuit Min Area: S = Isc * sqrt(t) / k",
        "Earth Fault Loop: Zs = Ze + (R1 + R2)",
    ]

    for eq in equations:
        pdf.cell(0, 5, f"- {eq}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Disclaimer Section
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "Disclaimer", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, report.disclaimer)

    pdf.ln(10)

    # Formal Sign-off Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Project Approval", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Save current Y position
    start_y = pdf.get_y()

    # Check if page break is needed for the signature block (approx 40mm height)
    if pdf.h - start_y < 50:
        pdf.add_page()
        start_y = pdf.get_y()

    # Left block: Designed By
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 6, "Designed By:", new_x="RIGHT")
    # Right block: Approved By
    pdf.cell(0, 6, "Approved By:", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)

    # Names
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        90,
        6,
        f"Name: {engineer_name if engineer_name else '____________________'}",
        new_x="RIGHT",
    )
    pdf.cell(
        0,
        6,
        f"Name: {approver_name if approver_name else '____________________'}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(2)

    # Dates
    pdf.cell(90, 6, "Date:   ____________________", new_x="RIGHT")
    pdf.cell(0, 6, "Date:   ____________________", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # Signatures
    pdf.cell(90, 6, "Signature: ____________________", new_x="RIGHT")
    pdf.cell(0, 6, "Signature: ____________________", new_x="LMARGIN", new_y="NEXT")

    # Save PDF
    pdf.output(filepath)
