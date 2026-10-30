"""
config.py
---------
Centralized Configuration for P_311 — IoT Fault Diagnosis Assistant.
All MQTT, ML, RAG, LLM, and sensor thresholds are managed in this single file.
"""

import os

# =====================================================================
# 1. MQTT BROKER CONFIGURATION
# =====================================================================
# For local Mosquitto: "127.0.0.1", port 1883
# For HiveMQ Cloud: "your-cluster.s1.eu.hivemq.cloud", port 8883, use_tls=True
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_USE_TLS = False
MQTT_USERNAME = None
MQTT_PASSWORD = None

# Topic patterns
# Wildcard for receiver: "factory/+/sensors"
# Base for publishers: "factory/{machine_id}/sensors"
MQTT_BASE_TOPIC = "factory"
MQTT_SUBSCRIBE_TOPIC = "factory/+/sensors"
DEFAULT_MACHINE_ID = "machine1"

# =====================================================================
# 2. MACHINE LEARNING MODEL CONFIGURATION
# =====================================================================
MODEL_PATH = "models/fault_model.pkl"
DECISION_THRESHOLD = 0.40  # Balanced operating point on AI4I dataset

EXPECTED_FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Type_H",
    "Type_L",
    "Type_M"
]

# =====================================================================
# 3. RAG VECTOR DATABASE CONFIGURATION
# =====================================================================
KNOWLEDGE_FILE = "knowledge_base/maintenance_knowledge.txt"
INDEX_PATH = "rag/maintenance.index"
DOCS_PATH = "rag/documents.pkl"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RAG_TOP_K = 1

# =====================================================================
# 4. LOCAL LLM COPILOT CONFIGURATION
# =====================================================================
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_LLM_MODEL = "llama3.2:1b"
LLM_TIMEOUT = 3.0  # seconds before fallback to grounded synthesizer

# =====================================================================
# 5. STORAGE & DATABASE PATHS
# =====================================================================
DB_PATH = "machine_data.db"
SNAPSHOT_PATH = "latest_telemetry.json"

# =====================================================================
# 6. PHYSICAL SENSOR THRESHOLDS (DIAGNOSIS ENGINE)
# =====================================================================
AIR_TEMP_WARN = 301.0       # K (Elevated ambient temperature)
PROC_TEMP_WARN = 312.0      # K (Elevated cutting process temperature)
RPM_MIN_WARN = 1300         # RPM (Low speed / spindle stall risk)
RPM_MAX_WARN = 1650         # RPM (Over-speeding)
TORQUE_WARN = 55.0          # Nm (High motor mechanical load)
TOOL_WEAR_WARN = 100        # min (Increasing tool degradation)
TOOL_WEAR_CRITICAL = 150    # min (Replacement limit reached)

# Severity threshold boundaries (based on failure probability)
SEVERITY_CRITICAL_THRESHOLD = 0.75
SEVERITY_HIGH_THRESHOLD = 0.40
SEVERITY_MEDIUM_THRESHOLD = 0.20
