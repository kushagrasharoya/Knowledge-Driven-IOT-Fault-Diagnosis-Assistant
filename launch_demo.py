"""
launch_demo.py
--------------
One-Click Master Launcher for P_311 Industrial IoT Fault Diagnosis Assistant.
Automatically starts:
1. ML Receiver & RAG + LLM Pipeline (ai4i_ml_receiver.py)
2. Interactive Real-Time Dashboard (dashboard.py)
3. Multi-Machine Fleet Simulator (ai4i_machine_simulator.py)
4. Opens browser to http://localhost:8501
Cleanly stops all processes on Ctrl+C.
"""

import os
import sys
import time
import socket
import subprocess
import webbrowser

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

VENV_PYTHON = os.path.join(".venv", "Scripts", "python.exe")
PYTHON_EXE = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

def is_port_open(host: str, port: int) -> bool:
    """Checks if a network port is reachable."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.5)
        return s.connect_ex((host, port)) == 0

def main():
    print("=" * 70)
    print(">> P_311 - IoT Fault Diagnosis Assistant (Master Launcher)")
    print("=" * 70)
    print(f"Using Python: {PYTHON_EXE}\n")

    # 1. Check MQTT Broker
    print("1. Checking Mosquitto MQTT Broker (127.0.0.1:1883)...")
    if is_port_open("127.0.0.1", 1883):
        print("   [OK] Mosquitto MQTT Broker is active.\n")
    else:
        print("   [WARNING] Mosquitto broker is not reachable on port 1883.")
        print("   Please start Mosquitto broker or check service status.\n")

    processes = []
    log_files = []
    os.makedirs("logs", exist_ok=True)

    try:
        # 2. Start ML Receiver + RAG + LLM Pipeline
        print("2. Starting Live ML Receiver & RAG/LLM Pipeline...")
        receiver_log = open(os.path.join("logs", "ml_receiver.log"), "a", encoding="utf-8")
        log_files.append(receiver_log)
        receiver_proc = subprocess.Popen(
            [PYTHON_EXE, "-u", "ai4i_ml_receiver.py"],
            stdout=receiver_log,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append(("ML Receiver", receiver_proc))
        time.sleep(2)
        print("   [OK] ML Receiver running (logging to logs/ml_receiver.log).\n")

        # 3. Start Streamlit Dashboard
        print("3. Starting Streamlit Dashboard Server on port 8501...")
        dash_log = open(os.path.join("logs", "dashboard.log"), "a", encoding="utf-8")
        log_files.append(dash_log)
        dash_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.headless", "true"],
            stdout=dash_log,
            stderr=subprocess.STDOUT
        )
        processes.append(("Dashboard", dash_proc))
        time.sleep(3)
        print("   [OK] Dashboard Server running on http://localhost:8501 (logging to logs/dashboard.log).\n")

        # 4. Start Fleet Simulator
        print("4. Starting Multi-Machine Fleet Simulator...")
        sim_log = open(os.path.join("logs", "simulator.log"), "a", encoding="utf-8")
        log_files.append(sim_log)
        sim_proc = subprocess.Popen(
            [PYTHON_EXE, "-u", "ai4i_machine_simulator.py"],
            stdout=sim_log,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append(("Simulator", sim_proc))
        print("   [OK] Fleet Simulator actively streaming telemetry (logging to logs/simulator.log).\n")

        # 5. Open Browser
        print("=" * 70)
        print(">> ALL SYSTEMS ONLINE & SYNCHRONIZED!")
        print("   • Live Dashboard : http://localhost:8501")
        print("   • MQTT Stream    : factory/+/sensors (3-Machine Fleet)")
        print("   • ML + RAG + LLM : Active and logging to machine_data.db")
        print("   • System Logs    : logs/ directory")
        print("=" * 70)
        print("Press Ctrl+C at any time to cleanly stop all processes.\n")

        webbrowser.open("http://localhost:8501")

        # Keep master process alive and monitor health
        reported_exits = set()
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None and name not in reported_exits:
                    reported_exits.add(name)
                    print(f"[ALERT] {name} exited with return code {proc.returncode}")

    except KeyboardInterrupt:
        print("\nStopping all system processes...")
        for name, proc in processes:
            print(f"Shutting down {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        for f in log_files:
            try:
                f.close()
            except Exception:
                pass
        print("All processes stopped cleanly. Goodbye!")

if __name__ == "__main__":
    main()
