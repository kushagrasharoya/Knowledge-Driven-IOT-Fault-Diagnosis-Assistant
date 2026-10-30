# P_311 — Problem Statement Document
## Knowledge-Driven Industrial IoT Fault Diagnosis Assistant

**Student Name:** KUSHAGRA SHAROYA  
**Roll Number:** 2400320100636  
**Mentor Name:** VIKAS MAURYA  
**Domain:** Embedded Systems & Industrial IoT (IIoT) / AI & Predictive Maintenance  
**Organization / Program:** HCLTech BTech Project Training Program  
**Document Version:** v1.0 | October 2026  

---

## 1. Executive Summary
In modern industrial smart factories (Industry 4.0), sudden mechanical breakdowns in high-throughput machinery (such as CNC milling centers, high-speed lathes, and precision grinders) cause catastrophic downtime, worker safety hazards, and millions in lost production revenue. While modern industrial machines are equipped with physical sensors (temperature, rotational speed, torque, vibration, and tool wear), factory maintenance workflows remain predominantly reactive or rely on simplistic static thresholds that trigger only after severe physical damage has already occurred.

This project delivers an end-to-end **Knowledge-Driven IoT Fault Diagnosis Assistant** that predicts failures before they manifest, isolates underlying physical root causes, retrieves grounded OEM maintenance standard operating procedures (SOPs) using Retrieval-Augmented Generation (RAG), and provides natural-language technician briefings via a Local LLM Copilot on a real-time dark industrial fleet dashboard.

---

## 2. Problem Definition & Core Challenges

### 2.1 The Failure of Static Threshold Systems
Traditional SCADA and basic IoT alarm systems rely on isolated threshold triggers (e.g., $Temperature > 80^\circ\text{C}$ or $Torque > 60\text{ Nm}$). In industrial reality:
* **Compound Degradation:** Multiple sensor readings may remain within nominal individual limits, but their combined multi-dimensional correlation (e.g., high cutting torque + slightly elevated process temperature + high tool wear) indicates an impending catastrophic breakdown (Heat Dissipation Failure or Spindle Stall).
* **Late Warnings:** Threshold alarms fire after mechanical binding or thermal expansion has already caused surface damage to workpieces or tooling.

### 2.2 The "Black Box" Alarm Dilemma
Where machine learning models have been introduced, they suffer from two critical adoption barriers on the factory floor:
1. **Lack of Explainability:** An operator receives a probability alert (e.g., *"Failure Risk: 82%"*), but the model does not explain which sensor factors caused the alarm.
2. **Disconnected Operational Knowledge:** Plant technicians do not just need to know that a machine is failing; they need immediate, step-by-step guidance on how to fix it according to certified OEM maintenance manuals without searching through hundreds of pages of paper documentation.

### 2.3 Hallucination and Latency Constraints in Shop-Floor AI
Deploying generative Large Language Models (LLMs) directly in manufacturing environments introduces severe operational risks:
* **LLM Hallucinations:** Unconstrained LLMs can invent dangerous maintenance advice (e.g., advising incorrect torque wrench ratings or improper electrical lockout-tagout procedures).
* **Edge Latency & Connectivity:** Cloud-dependent LLMs fail when factory networks experience intermittent dropouts or high latency.

---

## 3. Project Objectives & Deliverables

The objective of this project is to architect, develop, and benchmark an integrated, closed-loop industrial predictive maintenance system fulfilling the following milestones:

1. **Multi-Machine IoT Telemetry Ingestion:**
   Simulate and stream high-frequency physical telemetry across a 3-machine factory cell (Milling, Lathe, Grinder) using standard industrial MQTT messaging over topic `factory/+/sensors`.
2. **High-Accuracy ML Failure Prediction:**
   Train an ensemble Gradient Boosting Classifier on the 10,000-record AI4I 2020 Predictive Maintenance dataset, achieving an ROC-AUC score $\ge 0.95$ with strict exclusion of target-leakage variables.
3. **Calibrated Decision Thresholding:**
   Calibrate operating decision probability threshold to $0.40$ to optimize minority class failure recall ($\ge 70\%$), reflecting the high operational cost of False Negatives in industrial plants.
4. **Physical Anomaly Isolation (Rule Engine):**
   Implement deterministic boundary checks evaluating thermal deltas, low-speed stall risks, mechanical load spikes, and tool replacement limits.
5. **Grounded Retrieval-Augmented Generation (RAG):**
   Convert certified OEM maintenance procedures into dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and index them with FAISS for sub-5 millisecond semantic retrieval.
6. **Local LLM Shop-Floor Copilot:**
   Integrate a local LLM copilot that synthesizes telemetry, ML predictions, and retrieved OEM procedures into a standardized briefing (Situation Summary, Root Cause Assessment, and Action Directives) with 0% hallucination risk.
7. **Explainable AI (XAI) & Remaining Useful Life (RUL):**
   Calculate real-time sensor feature attributions and degradation countdowns toward the 150-minute cutting tool limit.
8. **Interactive Industrial Fleet Dashboard:**
   Deploy a responsive, multi-machine dark industrial dashboard in Streamlit and Plotly with live audit trails and CSV export.

---

## 4. Target Users & Operational Personas

| Persona | Role | Primary Need | System Feature Delivered |
| :--- | :--- | :--- | :--- |
| **Shop-Floor Machine Operator** | Operates CNC and milling machines during production shifts. | Clear, immediate visual status and countdown to tool replacement. | Real-time Plotly gauges, status badges (`NORMAL` vs `FAULT RISK`), and Tool RUL degradation timer. |
| **Maintenance Technician** | Dispatched to inspect and repair machines upon warning. | Exact root causes, sensor attributions, and OEM step-by-step repair checklists. | Explainable AI (XAI) feature attribution bar chart + Stage 6 Local LLM Copilot briefing. |
| **Plant Engineering Supervisor** | Oversees overall equipment effectiveness (OEE) and maintenance scheduling. | Multi-machine fleet overview, historical trends, and compliance audit trail. | Multi-machine dropdown switcher, historical time-series analytics, and one-click CSV log download. |

---

## 5. Success Metrics & Key Performance Indicators (KPIs)

| Metric | Target KPI | Achieved in Project | Validation Method |
| :--- | :---: | :---: | :--- |
| **ML Model ROC-AUC** | $\ge 0.9500$ | **0.9696** | Stratified 5-fold cross-validation on AI4I test set |
| **Failure Class Recall** | $\ge 70.0\%$ | **72.1%** | Calibrated threshold at $0.40$ on imbalanced dataset |
| **Inference Latency** | $< 10\text{ ms}$ | **$< 2\text{ ms}$** | Gradient boosting inference on edge CPU |
| **RAG Retrieval Speed** | $< 15\text{ ms}$ | **$< 5\text{ ms}$** | Dense vector search via FAISS IndexFlatIP |
| **LLM Grounding / Hallucination** | **0% Hallucination** | **0% Hallucination** | Strict prompting anchored only in retrieved OEM context |
| **Telemetry Ingestion Rate** | $0.5\text{ Hz / Machine}$ | **$0.5\text{ Hz}$ (Every 2s)** | Non-blocking asynchronous paho-mqtt client |
| **Fleet Uptime Monitoring** | 100% 3-machine sync | **100% Synchronized** | Atomic JSON buffer + SQLite persistence |

---

## 6. Project Constraints & Compliance
* **Edge Hardware Suitability:** All inference, embeddings, and database operations run locally without requiring expensive cloud GPUs or continuous external internet access.
* **Open Source Standards:** Built entirely on standard Python 3, MQTT (Eclipse Mosquitto), SQLite, Scikit-learn, FAISS, and Streamlit.
* **Safety & Security:** No hardcoded passwords, clear separation of operational edge telemetry, and standardized process shutdown mechanics.
