"""
Tooltip component for CustomTkinter widgets.

Provides a floating window with explanatory text when hovering over a widget.
"""
import customtkinter as ctk
import tkinter as tk


class Tooltip:
    """
    A tooltip that appears when hovering over a widget.
    
    Displays text in a small floating window near the mouse pointer.
    """

    def __init__(self, widget, text: str, delay: int = 500):
        """
        Initialize the tooltip.

        Args:
            widget: The widget to attach the tooltip to.
            text: The text to display in the tooltip.
            delay: Delay in milliseconds before showing the tooltip.
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        """Schedule the tooltip to appear after the delay."""
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        """Cancel the scheduled appearance."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        """Display the tooltip window."""
        if self.tooltip_window:
            return

        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            corner_radius=6,
            fg_color="#333333",
            text_color="white",
            padx=10,
            pady=5,
            font=ctk.CTkFont(size=12)
        )
        label.pack()

    def hide(self, event=None):
        """Hide the tooltip window."""
        self.unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
