"""Test Phase 0 setup and configuration integrity."""

from pathlib import Path
import config

def test_config_assumptions():
    assert config.RANDOM_SEED == 42
    assert config.SIMULATION_DURATION_HOURS == 24
    assert config.MIN_SERVICE_PRESSURE_M == 15.0
    assert config.REQUIRED_PRESSURE_PDD_M == 20.0
    assert len(config.DISTRICT_NAMES) == 5
    assert config.TUNISIA_LOSS_RANGE_PCT == (25.0, 50.0)
    assert "SIMULATED DATA" in config.DISCLAIMER_BANNER
    assert "ADVISES" in config.DECISION_RULE_TEXT

def test_assumptions_doc_exists():
    assumptions_path = Path(config.DOCS_DIR) / "ASSUMPTIONS.md"
    assert assumptions_path.exists()
    content = assumptions_path.read_text(encoding="utf-8")
    assert "HydroTwin" in content
    assert "0.210" in content
    assert "25.0%" in content
    assert "50.0%" in content

def test_cursor_rules_exist():
    cursor_rules_path = Path(__file__).resolve().parent.parent / ".cursor" / "rules" / "hydrotwin.mdc"
    assert cursor_rules_path.exists()
    content = cursor_rules_path.read_text(encoding="utf-8")
    assert "Simulated data" in content
    assert "The system ADVISES, humans DECIDE" in content
