#!/usr/bin/env python
"""Cross-platform command runner for HydroTwin.

Supports commands:
  python run.py setup
  python run.py data
  python run.py train
  python run.py eval
  python run.py test
  python run.py demo
  python run.py app
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable

def cmd_setup():
    print("[HydroTwin] Running setup...")
    subprocess.check_call([PYTHON, "generate_assumptions.py"])
    print("[HydroTwin] Setup complete. Assumptions generated.")

def cmd_data():
    print("[HydroTwin] Generating synthetic datasets (demands & leak scenarios)...")
    from sim.scenario_generator import generate_all_scenarios
    from ml.demand_forecasting import generate_synthetic_demand_dataset
    generate_synthetic_demand_dataset()
    generate_all_scenarios()
    print("[HydroTwin] Datasets generated in data/")

def cmd_train():
    print("[HydroTwin] Training ML models (forecasting, leak localization, transfer)...")
    from ml.demand_forecasting import train_demand_forecast_model
    from ml.leak_localizer import train_leak_localization_models
    from ml.transfer import train_transfer_comparison
    train_demand_forecast_model()
    train_leak_localization_models()
    train_transfer_comparison()
    print("[HydroTwin] Models trained and saved in models/")

def cmd_eval():
    print("[HydroTwin] Running evaluation on unseen scenarios...")
    from ml.leak_localizer import evaluate_unseen_scenarios
    evaluate_unseen_scenarios()
    print("[HydroTwin] Evaluation complete. Results saved in docs/EVALUATION.md")

def cmd_demo():
    print("[HydroTwin] Precomputing demo scenarios cache for instant offline playback...")
    from app.demo_steps import precompute_demo_cache
    precompute_demo_cache()
    print("[HydroTwin] Demo cache successfully generated.")

def cmd_test():
    print("[HydroTwin] Running pytest suite...")
    subprocess.check_call([PYTHON, "-m", "pytest", "tests/", "-v"])

def cmd_app():
    print("[HydroTwin] Starting Streamlit application...")
    streamlit_path = Path(sys.prefix) / "Scripts" / "streamlit.exe"
    if not streamlit_path.exists():
        streamlit_path = "streamlit"
    subprocess.run([str(streamlit_path), "run", "app/main.py"])

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [setup|data|train|eval|demo|test|app]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    commands = {
        "setup": cmd_setup,
        "data": cmd_data,
        "train": cmd_train,
        "eval": cmd_eval,
        "demo": cmd_demo,
        "test": cmd_test,
        "app": cmd_app,
    }
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available commands: {list(commands.keys())}")
        sys.exit(1)

if __name__ == "__main__":
    main()
