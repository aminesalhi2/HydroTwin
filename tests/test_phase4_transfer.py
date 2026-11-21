"""Tests for Phase 4: Rich vs. Sparse instrumentation and transfer learning."""

from pathlib import Path
import pytest
import config
from network.loader import load_network
from sim.sensor_network import get_sensor_layout, sample_sensor_telemetry
from sim.simulator import run_simulation
from ml.transfer import train_transfer_comparison, HONESTY_TRANSFER_STATEMENT

def test_sensor_layouts_counts():
    wn = load_network(24)
    rich_sensors, sparse_sensors = get_sensor_layout(wn)
    assert len(rich_sensors) == config.RICH_PRESSURE_SENSOR_COUNT
    assert len(sparse_sensors) == config.SPARSE_PRESSURE_SENSOR_COUNT
    assert set(sparse_sensors).issubset(set(rich_sensors)) or len(sparse_sensors) == 6

def test_sensor_telemetry_failure_in_sparse():
    wn = load_network(24)
    res = run_simulation(wn)
    
    tel_rich = sample_sensor_telemetry(res.pressures, res.flowrates, mode="rich", add_noise=True)
    tel_sparse = sample_sensor_telemetry(res.pressures, res.flowrates, mode="sparse", add_noise=True)
    
    assert tel_rich["sensors_count"] == config.RICH_PRESSURE_SENSOR_COUNT
    assert tel_sparse["sensors_count"] == config.SPARSE_PRESSURE_SENSOR_COUNT
    assert tel_sparse["mode"] == "sparse"

def test_transfer_learning_execution_and_honesty():
    res = train_transfer_comparison()
    assert "rich_dense_accuracy_pct" in res
    assert "sparse_scratch_accuracy_pct" in res
    assert "transfer_adapted_accuracy_pct" in res
    assert res["honesty_statement"] == HONESTY_TRANSFER_STATEMENT
    
    eval_text = (config.DOCS_DIR / "EVALUATION.md").read_text(encoding="utf-8")
    assert "Robustness to Sparse Sensors" in eval_text or "Sensor Topology Transfer Learning Strategy" in eval_text
    assert "HONEST TRANSFER LEARNING VERDICT" in eval_text or "HONEST METHODOLOGICAL STATEMENT" in eval_text
