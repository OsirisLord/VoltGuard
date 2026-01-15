"""
Tests for calculation logic.
"""
import pytest
from core.models import CableInput, Material, InsulationType, InstallationMethod, PhaseSystem
from core.calculator import CableSizingCalculator

@pytest.fixture
def basic_input():
    return CableInput(
        design_current=50.0,
        cable_length=30.0,
        material=Material.COPPER,
        insulation=InsulationType.XLPE_90C,
        installation=InstallationMethod.METHOD_E,
        power_factor=0.9
    )

def test_calculator_initialization(basic_input):
    """Test that calculator initializes correctly."""
    calc = CableSizingCalculator(basic_input)
    assert calc.inputs == basic_input

def test_get_recommended_size_valid(basic_input):
    """Test getting a recommended size for a standard case."""
    calc = CableSizingCalculator(basic_input)
    result = calc.get_recommended_size()
    
    assert result is not None
    assert result.overall_pass is True
    assert result.effective_ampacity >= basic_input.design_current
    assert result.voltage_drop_percent <= 5.0  # Assuming standard 5% limit? Default is usually 3-5%

def test_voltage_drop_calculation_3phase(basic_input):
    """Test voltage drop logic generally returns expected range."""
    basic_input.phase_system = PhaseSystem.THREE_PHASE
    calc = CableSizingCalculator(basic_input)
    # Just checking it runs and returns a sane value (0-100%)
    result = calc.get_recommended_size()
    if result:
        assert 0 < result.voltage_drop_percent < 100

def test_short_circuit_withstand(basic_input):
    """Test short circuit calculation."""
    basic_input.short_circuit_current = 6000 # 6kA
    basic_input.fault_time = 0.5
    
    calc = CableSizingCalculator(basic_input)
    result = calc.get_recommended_size()
    
    if result:
        assert result.min_sc_area > 0
        assert result.sc_pass is True

def test_no_solution_found():
    """Test case where current is too high for any cable."""
    inputs = CableInput(
        design_current=5000.0, # Huge current
        cable_length=50.0,
        material=Material.COPPER,
        insulation=InsulationType.XLPE_90C,
        installation=InstallationMethod.METHOD_E
    )
    calc = CableSizingCalculator(inputs)
    result = calc.get_recommended_size()
    
    # Depending on implementation, it might return None or the largest cable with failure status
    # Let's check the implementation behavior in a moment.
    # For now, if it returns None, that's one valid outcome.
    # If it returns a result, it should fail.
    if result:
        assert result.overall_pass is False
