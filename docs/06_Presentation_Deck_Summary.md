# P_311 — Presentation Deck Summary
## Knowledge-Driven Industrial IoT Fault Diagnosis Assistant

**Student Name:** KUSHAGRA SHAROYA  
**Roll Number:** 2400320100636  
**Mentor Name:** VIKAS MAURYA  
**Native Presentation File:** [docs/P_311_Final_Presentation_Deck.pptx](P_311_Final_Presentation_Deck.pptx)  
**Version:** v1.0 | October 2026  

---

### Slide 1: Title Slide & Credentials
* **Project Title:** P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant
* **Subtitle:** An End-to-End Industrial Predictive Maintenance System with Gradient Boosting ML, FAISS RAG, and a Local LLM Shop-Floor Copilot
* **Learner:** KUSHAGRA SHAROYA (Roll No. 2400320100636)
* **Mentor:** VIKAS MAURYA
* **Organization:** HCLTech BTech Project Training Program
* **GitHub Repository:** [github.com/kushagrasharoya/Knowledge-Driven-IOT-Fault-Diagnosis-Assistant](https://github.com/kushagrasharoya/Knowledge-Driven-IOT-Fault-Diagnosis-Assistant)
* **Live YouTube Video Walkthrough:** [youtu.be/co-VyIK7CFI](https://youtu.be/co-VyIK7CFI)

---

### Slide 2: Problem Statement & Industrial Context
* **Static Threshold Limitations:** Compound degradation escapes naive limit alarms; multiple sensors remain seemingly nominal while their joint interaction signals an impending breakdown.
* **The Black-Box Alarm Dilemma:** Conventional ML emits ungrounded probability figures with no explanation of root causes.
* **Shop-Floor AI Challenge:** Cloud-dependent LLMs hallucinate critical maintenance parameters and fail during factory network dropouts.

---

### Slide 3: End-to-End System Architecture
* **Perception Layer:** 3-machine fleet simulation / physical sensors (Speed, Torque, Temperature, Tool Wear).
* **Transport Layer:** Mosquitto MQTT broker on port `1883` (`factory/+/sensors`).
* **Analytics Layer:** Preprocessing $\rightarrow$ Gradient Boosting Inference $\rightarrow$ Physical Rule Engine $\rightarrow$ FAISS Dense Vector RAG $\rightarrow$ Stage 6 Local LLM Copilot.
* **Persistence & Cache:** SQLite `machine_data.db` + atomic multi-machine `latest_telemetry.json`.
* **Presentation Layer:** Streamlit dark industrial dashboard on port `8501`.

---

### Slide 4: Multi-Machine IoT Fleet Simulation
* **`machine1`:** CNC Milling Center (Type M) — High precision under medium mechanical load.
* **`machine2`:** Heavy Duty Lathe (Type H) — High-torque turning operations.
* **`machine3`:** High Speed Grinder (Type L) — Ultra-high RPM, low torque, thermal dissipation sensitivity.
* **Telemetry Cadence:** Streamed asynchronously every 2.0 seconds.

---

### Slide 5: Machine Learning Failure Prediction (Stage 4)
* **Dataset:** 10,000-record AI4I 2020 Predictive Maintenance Dataset.
* **Algorithm:** Gradient Boosting Classifier (**ROC-AUC: 0.9696**).
* **Target Leakage Exclusion:** Specific failure labels (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) strictly omitted from input features.
* **Calibrated Decision Boundary:** Threshold tuned to **0.40**, boosting minority failure recall from $58.8\%$ to **$72.1\%$** ($84.5\%$ precision).

---

### Slide 6: Physical Sensor Rule Engine & Severity Grading
* **Physical Limits:** Evaluates Torque ($\ge 55\text{ Nm}$), Speed ($< 1300\text{ RPM}$ or $> 1650\text{ RPM}$), Temps, and Tool Wear ($\ge 150\text{ min}$).
* **Severity Tiers:**
  * `CRITICAL` ($p \ge 0.75$): Immediate E-STOP or machine isolation.
  * `HIGH` ($p \ge 0.40$): Urgent maintenance inspection scheduled within shift.
  * `MEDIUM` ($p \ge 0.20$): Heightened monitoring.
  * `LOW` ($p < 0.20$): Nominal operation.

---

### Slide 7: Stage 5 Semantic Vector RAG (FAISS)
* **Limitation of Keyword Search:** Overcomes terminology mismatch between technician queries and technical manual headers.
* **Vector Embeddings:** 384-dimensional dense semantic vectors using `sentence-transformers/all-MiniLM-L6-v2`.
* **Vector Index:** FAISS `IndexFlatIP` returning certified OEM procedures in $< 5\text{ ms}$.

---

### Slide 8: Stage 6 Local LLM Shop-Floor Copilot
* **Dual-Backend:** Local Ollama (`llama3.2:1b`) with a 3.0-second timeout and an instant deterministic grounded fallback synthesizer.
* **Zero Hallucination:** Instructions strictly anchored in retrieved OEM documentation.
* **Structured Briefing:** Situation Summary, Root-Cause Assessment, and Immediate Action Checklists.

---

### Slide 9: Explainable AI (XAI) & Remaining Useful Life (RUL)
* **XAI Feature Attribution:** Real-time normalized bar chart displaying relative sensor risk contributions.
* **Tool RUL Degradation:** Real-time countdown towards the 150-minute tool limit ($\text{RUL} = \max(0, 150 - \text{Tool\_Wear})$).

---

### Slide 10: Bill of Materials (BOM) & Edge Hardware Architecture
* **Edge Gateway:** ESP32 DevKit v1 micro-controller.
* **Sensors:** MAX6675 K-Type thermocouple, SCT-013 non-invasive current clamp, optical rotary encoder, SSD1306 OLED display.
* **Economics:** Total hardware retrofit cost under **₹3,000 INR per machine cell**.

---

### Slide 11: Verification, Benchmarks & Test Matrix
* **Test Suite:** 10 / 10 Test Cases Passed (100% Pass Rate).
* **Confusion Matrix:** 1923 True Negatives, 49 True Positives, 19 False Negatives, 9 False Positives.
* **Engineering Hardening:** Windows console UTF-8 encoding fix and unread pipe buffer deadlock prevention.

---

### Slide 12: Viva Defense & Conclusion
* **Key Viva Defense:** Demonstrates why tree-based models beat deep learning on tabular telemetry, how precision-recall trade-offs dictate threshold calibration, and why RAG eliminates LLM hallucinations.
* **Public GitHub Repository:** [https://github.com/kushagrasharoya/Knowledge-Driven-IOT-Fault-Diagnosis-Assistant](https://github.com/kushagrasharoya/Knowledge-Driven-IOT-Fault-Diagnosis-Assistant)
* **Live YouTube Video Walkthrough:** [https://youtu.be/co-VyIK7CFI](https://youtu.be/co-VyIK7CFI)
* **Future Scope:** Hardware-in-the-loop edge microcontroller deployment, acoustic vibration FFT, and automated ERP spare-parts replenishment.
