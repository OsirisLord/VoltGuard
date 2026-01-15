"""
Tests for data models and validation logic.
"""

import pytest
from core.models import CableInput, Material, InsulationType, InstallationMethod


def test_cable_input_validation_valid():
    """Test that valid input returns None."""
    inputs = CableInput(
        design_current=100.0,
        cable_length=50.0,
        power_factor=0.9,
        material=Material.COPPER,
        insulation=InsulationType.XLPE_90C,
        installation=InstallationMethod.METHOD_E,
    )
    assert inputs.validate() is None


def test_cable_input_validation_invalid_current():
    """Test validation for invalid design current."""
    inputs = CableInput(
        design_current=-10.0,
        cable_length=50.0,
        power_factor=0.9,
    )
    assert inputs.validate() == "Design current must be positive"


def test_cable_input_validation_invalid_length():
    """Test validation for invalid cable length."""
    inputs = CableInput(
        design_current=100.0,
        cable_length=0.0,
        power_factor=0.9,
    )
    assert inputs.validate() == "Cable length must be positive"


def test_cable_input_validation_invalid_power_factor():
    """Test validation for invalid power factor."""
    inputs = CableInput(
        design_current=100.0,
        cable_length=50.0,
        power_factor=1.5,
    )
    assert inputs.validate() == "Power factor must be between 0 and 1"


def test_cable_input_validation_invalid_parallel_runs():
    """Test validation for invalid parallel runs."""
    inputs = CableInput(
        design_current=100.0, cable_length=50.0, power_factor=0.9, parallel_runs=5
    )
    assert inputs.validate() == "Parallel runs must be between 1 and 4"


def test_cable_input_derating_calculation():
    """Test total derating factor calculation."""
    inputs = CableInput(
        design_current=100.0,
        cable_length=50.0,
        temp_factor=0.9,
        group_factor=0.8,
        soil_factor=1.0,
    )
    # 0.9 * 0.8 * 1.0 = 0.72
    assert inputs.derating == pytest.approx(0.72)


def test_cable_input_current_per_cable():
    """Test current per cable calculation with parallel runs."""
    inputs = CableInput(design_current=100.0, cable_length=50.0, parallel_runs=2)
    assert inputs.current_per_cable == 50.0
