"""
Chart frame for cable sizing calculator.

Displays interactive matplotlib chart with hover tooltips.
"""
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

import customtkinter as ctk
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position, import-error
from config.constants import VOLTAGE_DROP_LIMIT


class ChartFrame(ctk.CTkFrame):
    """Frame containing interactive matplotlib chart."""

    def __init__(self, master: Any, **kwargs):
        """Initialize chart frame."""
        super().__init__(master, **kwargs)

        self.figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self._cursor = None

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        self.title_label = ctk.CTkLabel(
            self, text="Cable Sizing Chart",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.chart_container = ctk.CTkFrame(self)
        self._create_empty_chart()

    def _layout_widgets(self) -> None:
        """Layout all widgets."""
        self.title_label.pack(pady=(10, 15))
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=10)

    def _get_chart_colors(self) -> Tuple[str, str, str, str]:
        """Get chart colors based on current theme."""
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            return "#1f1f1f", "white", "#4da6ff", "#ff6b6b"
        return "white", "black", "#1a73e8", "#dc3545"

    def _create_empty_chart(self) -> None:
        """Create an empty placeholder chart."""
        bg_color, text_color, _, _ = self._get_chart_colors()

        self.figure = Figure(figsize=(8, 5), dpi=100, facecolor=bg_color)
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(bg_color)
        ax.text(
            0.5, 0.5,
            "Enter parameters and click Calculate\nto view the chart",
            ha='center', va='center', fontsize=12, color=text_color,
            transform=ax.transAxes
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        self._embed_chart()

    def _embed_chart(self) -> None:
        """Embed the matplotlib figure in the tkinter frame."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_chart(
        self,
        sizes: List[float],
        vd_percents: List[float],
        ampacities: List[float],
        design_current: float,
        recommended_index: Optional[int] = None,
        costs: Optional[List[float]] = None
    ) -> None:
        """Update chart with new data and interactive tooltips."""
        bg_color, text_color, vd_color, amp_color = self._get_chart_colors()

        if self.figure:
            self.figure.clear()
        else:
            self.figure = Figure(figsize=(8, 5), dpi=100)

        self.figure.set_facecolor(bg_color)
        ax1 = self.figure.add_subplot(111)
        ax1.set_facecolor(bg_color)

        # Plot voltage drop
        line1, = ax1.plot(
            sizes, vd_percents, 'o-', color=vd_color, linewidth=2,
            markersize=8, label='Voltage Drop (%)'
        )
        ax1.axhline(
            y=VOLTAGE_DROP_LIMIT, color=vd_color, linestyle='--',
            linewidth=1.5, alpha=0.7, label=f'VD Limit ({VOLTAGE_DROP_LIMIT}%)'
        )

        ax1.set_xlabel('Cable Size (mm²)', color=text_color, fontsize=11)
        ax1.set_ylabel('Voltage Drop (%)', color=vd_color, fontsize=11)
        ax1.tick_params(axis='y', labelcolor=vd_color)
        ax1.tick_params(axis='x', colors=text_color)
        ax1.set_xscale('log')
        ax1.set_xticks(sizes)
        ax1.set_xticklabels([str(int(s)) if s >= 1 else str(s) for s in sizes], rotation=45)

        # Secondary axis for ampacity
        ax2 = ax1.twinx()
        line2, = ax2.plot(
            sizes, ampacities, 's-', color=amp_color, linewidth=2,
            markersize=8, label='Effective Ampacity (A)'
        )
        ax2.axhline(
            y=design_current, color=amp_color, linestyle='--',
            linewidth=1.5, alpha=0.7, label=f'Design Current ({design_current:.0f}A)'
        )
        ax2.set_ylabel('Effective Ampacity (A)', color=amp_color, fontsize=11)
        ax2.tick_params(axis='y', labelcolor=amp_color)

        # Highlight recommended
        if recommended_index is not None:
            rec_size = sizes[recommended_index]
            rec_vd = vd_percents[recommended_index]
            rec_amp = ampacities[recommended_index]

            ax1.plot(rec_size, rec_vd, 'o', color=vd_color, markersize=15,
                    markerfacecolor='none', markeredgewidth=3)
            ax2.plot(rec_size, rec_amp, 's', color=amp_color, markersize=15,
                    markerfacecolor='none', markeredgewidth=3)

            ax1.annotate(
                f'Recommended\n{int(rec_size)} mm²',
                xy=(rec_size, rec_vd),
                xytext=(rec_size * 1.5, rec_vd + 0.5),
                fontsize=9, color=text_color,
                arrowprops=dict(arrowstyle='->', color=text_color, lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=bg_color, edgecolor=text_color)
            )

        ax1.grid(True, which='both', linestyle='--', alpha=0.3)

        # Combined legend
        lines = [line1, line2]
        labels: List[str] = [str(l.get_label()) for l in lines]
        ax1.legend(lines, labels, loc='upper right', fontsize=9)

        ax1.set_title('Cable Sizing Analysis', color=text_color, fontsize=14, fontweight='bold')

        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color(text_color)

        self.figure.tight_layout()
        self._embed_chart()

        # Add interactive cursors
        try:
            self._cursor = mplcursors.cursor([line1, line2], hover=True)

            @self._cursor.connect("add")
            def on_add(sel):
                idx = int(sel.index)
                size = sizes[idx]
                vd = vd_percents[idx]
                amp = ampacities[idx]
                cost = costs[idx] if costs else 0

                if sel.artist == line1:
                    sel.annotation.set_text(
                        f"Size: {size} mm²\nVD: {vd:.2f}%"
                    )
                else:
                    sel.annotation.set_text(
                        f"Size: {size} mm²\nAmpacity: {amp:.0f}A\nCost: ${cost:.0f}"
                    )
                sel.annotation.get_bbox_patch().set_facecolor(bg_color)
                sel.annotation.get_bbox_patch().set_edgecolor(text_color)
                sel.annotation.set_color(text_color)
        except Exception:  # pylint: disable=broad-exception-caught
            pass  # Gracefully handle if mplcursors fails
