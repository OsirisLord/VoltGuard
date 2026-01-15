"""
VoltGuard - Main Entry Point.

VoltGuard is a professional cable sizing tool with modern GUI for electrical engineers.
Calculates cable size based on ampacity, voltage drop, and short-circuit
requirements according to IEC 60364-5-52 standards.
"""
from gui import CableSizingApp


def main() -> None:
    """Run the cable sizing calculator application."""
    app = CableSizingApp()
    app.run()


if __name__ == "__main__":
    main()
