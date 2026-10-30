# P_311 — Software Requirements Specification (SRS)
## Knowledge-Driven Industrial IoT Fault Diagnosis Assistant

**Student Name:** KUSHAGRA SHAROYA  
**Roll Number:** 2400320100636  
**Mentor Name:** VIKAS MAURYA  
**Standard Compliance:** IEEE Std 830-1998 Format  
**Version:** v1.0 | October 2026  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document defines the complete functional and non-functional requirements for the **P_311 Knowledge-Driven Industrial IoT Fault Diagnosis Assistant**. It serves as the baseline contract for developers, quality assurance engineers, system architects, and university/corporate evaluators.

### 1.2 Document Conventions
* **FR:** Functional Requirement
* **NFR:** Non-Functional Requirement
* **IR:** Interface Requirement
* **Priority Levels:** High (Mandatory for core operation), Medium (Important operational value), Low (Enhancement)

### 1.3 Intended Audience
* Academic Evaluators & Mentors (HCLTech & University Examination Panels)
* IoT Systems Engineers & Shop-Floor Maintenance Specialists
* Machine Learning & Software Developers

### 1.4 Project Scope
The system ingests real-time sensor streams from a 3-machine industrial cell via MQTT, performs binary failure risk classification using a trained Gradient Boosting Classifier, isolates physical root anomalies via an expert rule engine, executes semantic vector search (RAG) over OEM manuals via FAISS, and synthesizes grounded natural-language briefings via a Local LLM Copilot on a Streamlit dashboard.

---

## 2. Overall Description

### 2.1 Product Perspective
The system operates as an Edge-to-Gateway Industrial Predictive Maintenance solution:
```
[Physical Sensors / Fleet Simulator] 
           │ (MQTT: factory/+/sensors)
           ▼
[Mosquitto Message Broker :1883]
           │
           ▼
[ML Ingestion & Analytics Engine] ───► [SQLite: machine_data.db]
           │                              │
           ▼                              ▼
[FAISS RAG & Local LLM Copilot] ───► [JSON State Buffer]
                                          │
                                          ▼
                         [Streamlit Industrial Dashboard :8501]
```

### 2.2 User Classes and Characteristics
1. **Operator:** Views live machine health, visual gauges, status badges, and tool remaining useful life. Requires zero technical ML knowledge.
2. **Technician:** Reads the root-cause sensor breakdowns, XAI attribution charts, and step-by-step OEM maintenance action checklists.
3. **Supervisor / Auditor:** Filters historical logs by machine ID, inspects audit trails, and exports time-stamped CSV telemetry reports.

### 2.3 Operating Environment
* **Operating System:** Windows 10/11, Ubuntu 22.04 LTS, or Debian Linux.
* **Runtime:** Python 3.10+ (Tested on Python 3.14.x 64-bit).
* **Communication:** TCP/IP Local Network, Port 1883 (MQTT), Port 8501 (HTTP Streamlit).
* **Hardware Requirements:** Minimum Dual-core x86/ARM64 CPU, 4 GB RAM, 2 GB free disk space.

---

## 3. Specific Functional Requirements (FR)

### 3.1 Module 1: Multi-Machine Fleet Telemetry (Simulator & Ingestion)
* **FR-1.1 [High]:** The system shall simulate a fleet of 3 industrial machines: `machine1` (CNC Milling Center, Type M), `machine2` (Heavy Duty Lathe, Type H), and `machine3` (High Speed Grinder, Type L).
* **FR-1.2 [High]:** Telemetry shall publish JSON payloads every 2.0 seconds to topic pattern `factory/{machine_id}/sensors`.
* **FR-1.3 [High]:** Each payload shall contain: `machine_id`, `machine_name`, `type`, `air_temperature` (K), `process_temperature` (K), `rotational_speed` (RPM), `torque` (Nm), `tool_wear` (min), and `timestamp`.
* **FR-1.4 [Medium]:** The simulator shall generate realistic physical correlations (e.g., higher torque correlating with increased tool wear and reduced rotational speed).

### 3.2 Module 2: Machine Learning Failure Prediction
* **FR-2.1 [High]:** The ML engine shall load the pre-trained Gradient Boosting model package from `models/fault_model.pkl`.
* **FR-2.2 [High]:** The model shall accept 8 strictly leak-free input features: Air temperature, Process temperature, Rotational speed, Torque, Tool wear, and one-hot encoded Type flags (`Type_H`, `Type_L`, `Type_M`).
* **FR-2.3 [High]:** The engine shall output a continuous failure probability between $0.0$ and $1.0$.
* **FR-2.4 [High]:** The operating threshold shall be fixed at $0.40$ (calibrated for high recall of minority failures). Probabilities $\ge 0.40$ shall flag machine status as `FAULT RISK`; values $< 0.40$ shall flag status as `NORMAL`.

### 3.3 Module 3: Physical Rule Diagnosis & Severity Grading
* **FR-3.1 [High]:** The diagnosis engine shall independently evaluate physical boundary conditions:
  - Air temperature $\ge 301.0\text{ K}$ (`Elevated air temperature`)
  - Process temperature $\ge 312.0\text{ K}$ (`High process temperature`)
  - Rotational speed $< 1300\text{ RPM}$ (`Low rotational speed / stall risk`)
  - Rotational speed $> 1650\text{ RPM}$ (`High rotational speed`)
  - Torque $\ge 55.0\text{ Nm}$ (`High torque load`)
  - Tool wear $\ge 150\text{ min}$ (`Critical tool wear limit`)
* **FR-3.2 [High]:** The engine shall assign a 4-tier severity rating:
  - `CRITICAL`: Failure probability $\ge 0.75$
  - `HIGH`: Failure probability $\ge 0.40$
  - `MEDIUM`: Failure probability $\ge 0.20$
  - `LOW`: Failure probability $< 0.20$

### 3.4 Module 4: Retrieval-Augmented Generation (RAG)
* **FR-4.1 [High]:** The system shall index certified OEM maintenance knowledge from `knowledge_base/maintenance_knowledge.txt`.
* **FR-4.2 [High]:** Text chunks shall be encoded into 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2`.
* **FR-4.3 [High]:** Semantic similarity search shall be performed using FAISS (`IndexFlatIP`) with inner-product cosine similarity.
* **FR-4.4 [High]:** When an abnormal sensor condition is flagged, the top matching SOP document shall be retrieved in $< 10\text{ ms}$.

### 3.5 Module 5: Stage 6 Local LLM Technician Copilot
* **FR-5.1 [High]:** The system shall attempt to contact a local Ollama API (`http://localhost:11434/api/generate`) with model `llama3.2:1b`.
* **FR-5.2 [High]:** If Ollama is unavailable or exceeds a 3.0-second timeout, the system shall seamlessly fall back to the built-in deterministic grounded synthesizer without throwing an error.
* **FR-5.3 [High]:** All generated briefings shall adhere strictly to a 3-part structure:
  1. *Situation Summary* (Live sensor numbers and risk)
  2. *Root-Cause Assessment* (Pinpointed physical anomaly)
  3. *Immediate Action Directive* (Step-by-step actions derived from retrieved OEM manual)

### 3.6 Module 6: Persistence & Atomic State Sync
* **FR-6.1 [High]:** Every incoming message, prediction, diagnosis, and briefing shall be persisted to SQLite table `telemetry_logs` in `machine_data.db`.
* **FR-6.2 [High]:** An atomic multi-machine JSON cache (`latest_telemetry.json`) shall be updated on every message to ensure zero lag across fleet switching in the dashboard.

### 3.7 Module 7: Streamlit Real-Time Dashboard
* **FR-7.1 [High]:** The dashboard shall render on port `8501` featuring a custom dark industrial theme (`#0b0f19` background).
* **FR-7.2 [High]:** A fleet selector dropdown shall allow instantaneous switching between `machine1`, `machine2`, and `machine3`.
* **FR-7.3 [High]:** 4 real-time Plotly speedometer gauges shall display Rotational Speed, Torque, Process Temperature, and Tool Wear with color-coded safety zones.
* **FR-7.4 [High]:** An Explainable AI (XAI) bar chart shall quantify relative feature contributions to the current failure probability.
* **FR-7.5 [High]:** A Remaining Useful Life (RUL) card shall display remaining operating minutes before tool replacement.
* **FR-7.6 [Medium]:** An audit log table shall support one-click CSV download of filtered historical machine records.

---

## 4. Non-Functional Requirements (NFR)

* **NFR-1: Performance & Latency:** The end-to-end processing latency (MQTT receive $\rightarrow$ ML inference $\rightarrow$ Rule check $\rightarrow$ FAISS RAG $\rightarrow$ DB write) shall not exceed $150\text{ ms}$ on standard edge hardware.
* **NFR-2: Reliability & Fault Tolerance:** If an individual machine stops transmitting, the system shall continue logging and displaying all other active fleet units without crashing.
* **NFR-3: Zero Hallucination Guarantee:** The RAG and Copilot pipeline shall never fabricate maintenance instructions; all directives must be anchored in OEM documentation.
* **NFR-4: Portability:** The software stack must execute on standard CPU hardware without mandatory external internet or GPU dependencies.
* **NFR-5: Modularity & Maintainability:** All configuration parameters (MQTT broker, topic names, ML thresholds, sensor boundaries, file paths) shall reside in a single centralized configuration file ([config.py](file:///e:/HCL%20TRAINING/Knowledge%20Driven%20IOT%20Fault%20Diagnosis%20Assistant/config.py)).
* **NFR-6: Usability & Ergonomics:** Visual indicators must use standardized industrial color psychology: Green for Nominal, Amber for Elevated Warning, and Crimson Red for Critical Danger.

---

## 5. External Interface Requirements

### 5.1 Communication Interfaces
* **Protocol:** MQTT v3.1.1 / v5.0 via TCP socket connection.
* **Network Port:** 1883 (Unencrypted local) / 8883 (TLS secure cloud broker).

### 5.2 Software Interfaces
* **Database:** SQLite 3 Embedded Engine (`machine_data.db`).
* **Vector Store:** FAISS binary index format (`rag/maintenance.index`).
* **Web UI Server:** Streamlit HTTP Application Server (`localhost:8501`).
