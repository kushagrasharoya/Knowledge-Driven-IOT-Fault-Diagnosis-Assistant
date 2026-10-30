"""
ai4i_ml_receiver.py
-------------------
Live IoT ML Receiver integrated with:
1. Multi-Machine Fleet MQTT Support (factory/+/sensors)
2. Gradient Boosting ML Model (AI4I dataset)
3. Rule-based Diagnosis Engine
4. RAG Maintenance Knowledge Retrieval (FAISS)
5. Stage 6: Local LLM Technician Copilot (llm_assistant.py)
6. SQLite Fleet Database Persistence (machine_data.db)
7. Multi-Machine Live Snapshot Broadcasting (latest_telemetry.json)
Configured via config.py.
"""

import sys
import os
import json
import time
import sqlite3
import joblib
import pandas as pd
import paho.mqtt.client as mqtt

# Ensure UTF-8 output encoding where supported
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_SUBSCRIBE_TOPIC,
    MQTT_USE_TLS,
    MODEL_PATH,
    DECISION_THRESHOLD,
    EXPECTED_FEATURES,
    DB_PATH,
    SNAPSHOT_PATH
)
from diagnosis import diagnose_machine
from rag_retriever import get_maintenance_for_conditions, init_rag
from llm_assistant import generate_technician_briefing

print("=" * 70, flush=True)
print("P_311 - Knowledge-Driven IoT Fault Diagnosis Assistant", flush=True)
print("Initializing Multi-Machine ML, Database, RAG & LLM Pipeline...", flush=True)
print("=" * 70, flush=True)

# 1. Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            machine_id TEXT,
            machine_type TEXT,
            air_temperature REAL,
            process_temperature REAL,
            rotational_speed INTEGER,
            torque REAL,
            tool_wear INTEGER,
            failure_probability REAL,
            status TEXT,
            severity TEXT,
            conditions TEXT,
            recommendation TEXT,
            rag_advice TEXT,
            llm_briefing TEXT
        )
    """)
    # Add machine_id column if migrating existing table
    try:
        cursor.execute("ALTER TABLE telemetry_logs ADD COLUMN machine_id TEXT")
    except sqlite3.OperationalError:
        pass
    # Add llm_briefing column if migrating
    try:
        cursor.execute("ALTER TABLE telemetry_logs ADD COLUMN llm_briefing TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
    print(f"[OK] Database initialized: {DB_PATH}", flush=True)

init_db()

# 2. Load trained ML model package
print(f"Loading ML model from: {MODEL_PATH}", flush=True)
model_pkg = joblib.load(MODEL_PATH)
model = model_pkg["model"]
features = model_pkg["features"]
threshold = model_pkg.get("threshold", DECISION_THRESHOLD)
print(f"[OK] Model Loaded: Gradient Boosting (Threshold: {threshold})", flush=True)
print(f"[OK] Expected Features: {features}\n", flush=True)

# 3. Warm up RAG Vector Database & Embedding Model
print("Initializing RAG Vector Engine...", flush=True)
init_rag()

# Memory store for fleet snapshot
fleet_state = {
    "active_machine": "machine1",
    "machines": {}
}

def save_record(record: dict):
    """Saves telemetry to SQLite and updates multi-machine snapshot JSON."""
    m_id = record.get("machine_id", "machine1")

    # 1. Write to SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry_logs (
                timestamp, machine_id, machine_type, air_temperature, process_temperature,
                rotational_speed, torque, tool_wear, failure_probability,
                status, severity, conditions, recommendation, rag_advice, llm_briefing
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["timestamp"],
            m_id,
            record["machine_type"],
            record["air_temperature"],
            record["process_temperature"],
            record["rotational_speed"],
            record["torque"],
            record["tool_wear"],
            record["failure_probability"],
            record["status"],
            record["severity"],
            json.dumps(record["conditions"]),
            record["recommendation"],
            record["rag_advice"],
            record.get("llm_briefing", "")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] DB write failed: {e}", flush=True)

    # 2. Update multi-machine snapshot buffer
    try:
        fleet_state["active_machine"] = m_id
        fleet_state["machines"][m_id] = record
        # Include top-level keys for backward compatibility
        full_snapshot = {**record, **fleet_state}
        with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
            json.dump(full_snapshot, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Snapshot write failed: {e}", flush=True)

def on_connect(client, userdata, flags, rc, properties=None):
    failed = rc.is_failure if hasattr(rc, "is_failure") else (rc != 0)
    if not failed:
        print(f"[OK] Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}", flush=True)
        client.subscribe(MQTT_SUBSCRIBE_TOPIC)
        print(f"[OK] Subscribed to fleet topic: {MQTT_SUBSCRIBE_TOPIC}", flush=True)
        print("Waiting for incoming machine sensor telemetry...\n", flush=True)
    else:
        print(f"[ERROR] Failed to connect to MQTT broker: {rc}", flush=True)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Invalid JSON payload: {e}", flush=True)
        return

    # Extract machine_id from topic (factory/{machine_id}/sensors) or payload
    topic_parts = msg.topic.split("/")
    if len(topic_parts) >= 3 and topic_parts[1]:
        m_id = topic_parts[1]
    else:
        m_id = payload.get("machine_id", "machine1")

    # Extract raw sensor fields
    m_type = payload.get("type", "M")
    m_name = payload.get("machine_name", f"Machine {m_id}")
    air_temp = float(payload.get("air_temperature", 300.0))
    proc_temp = float(payload.get("process_temperature", 310.0))
    rpm = int(payload.get("rotational_speed", 1500))
    torque = float(payload.get("torque", 40.0))
    tool_wear = int(payload.get("tool_wear", 0))

    # Preprocess into feature format expected by the model
    feature_dict = {
        "Air temperature [K]": air_temp,
        "Process temperature [K]": proc_temp,
        "Rotational speed [rpm]": rpm,
        "Torque [Nm]": torque,
        "Tool wear [min]": tool_wear,
        "Type_H": 1.0 if m_type == "H" else 0.0,
        "Type_L": 1.0 if m_type == "L" else 0.0,
        "Type_M": 1.0 if m_type == "M" else 0.0,
    }

    input_df = pd.DataFrame([feature_dict])[features]

    # Predict failure probability with ML model
    proba = float(model.predict_proba(input_df)[0][1])

    # Run Diagnosis Engine
    diagnosis = diagnose_machine(payload, proba)
    status = diagnosis["status"]
    severity = diagnosis["severity"]
    conditions = diagnosis["conditions"]
    recommendation = diagnosis["recommendation"]

    # RAG KNOWLEDGE RETRIEVAL (Triggered if anomalies or fault risks are detected)
    has_anomalies = (conditions != ["No major abnormal sensor condition detected"])
    rag_advice = ""
    if status == "FAULT RISK" or has_anomalies or severity in ["HIGH", "CRITICAL"]:
        rag_advice = get_maintenance_for_conditions(conditions, top_k=1)

    # STAGE 6: LOCAL LLM COPILOT BRIEFING
    llm_briefing = generate_technician_briefing(
        payload,
        proba,
        status,
        severity,
        conditions,
        rag_advice
    )

    current_time = time.strftime("%H:%M:%S")

    # Record payload for DB and Dashboard
    record = {
        "timestamp": current_time,
        "machine_id": m_id,
        "machine_name": m_name,
        "machine_type": m_type,
        "air_temperature": air_temp,
        "process_temperature": proc_temp,
        "rotational_speed": rpm,
        "torque": torque,
        "tool_wear": tool_wear,
        "failure_probability": proba,
        "status": status,
        "severity": severity,
        "conditions": conditions,
        "recommendation": recommendation,
        "rag_advice": rag_advice,
        "llm_briefing": llm_briefing
    }

    # Save to SQLite and JSON snapshot
    save_record(record)

    # Print Telemetry & Diagnosis Header
    print("-" * 70, flush=True)
    print(f"Time                : {current_time} | Machine: {m_id.upper()} ({m_name})", flush=True)
    print(f"Machine Type        : {m_type}", flush=True)
    print(f"Air Temperature     : {air_temp:.1f} K", flush=True)
    print(f"Process Temperature : {proc_temp:.1f} K", flush=True)
    print(f"Rotational Speed    : {rpm} RPM", flush=True)
    print(f"Torque              : {torque:.1f} Nm", flush=True)
    print(f"Tool Wear           : {tool_wear} min", flush=True)
    print(flush=True)
    print(f"Failure Probability : {proba * 100:.2f}% (Threshold: {threshold * 100:.0f}%)", flush=True)
    print(f"Machine Status      : {status}", flush=True)
    print(f"Severity            : {severity}", flush=True)
    print(flush=True)
    print("Possible contributing conditions:", flush=True)
    for cond in conditions:
        print(f"  -> {cond}", flush=True)
    print(flush=True)
    print(f"Recommended Action:\n  -> {recommendation}", flush=True)

    if rag_advice:
        print("\n" + "=" * 70, flush=True)
        print("[RAG KNOWLEDGE RETRIEVAL - RETRIEVED MAINTENANCE PROCEDURE]", flush=True)
        print("=" * 70, flush=True)
        print(rag_advice, flush=True)
        print("=" * 70, flush=True)

    if llm_briefing:
        print("\n" + "-" * 70, flush=True)
        print("[STAGE 6: LOCAL LLM TECHNICIAN COPILOT BRIEFING]", flush=True)
        print("-" * 70, flush=True)
        print(llm_briefing, flush=True)
        print("-" * 70, flush=True)

    print("-" * 70 + "\n", flush=True)

# Connect and run MQTT loop
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

if MQTT_USE_TLS:
    client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
