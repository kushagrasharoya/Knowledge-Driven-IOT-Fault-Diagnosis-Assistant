# P_311 — Live Demonstration & Viva Defense Presentation Script
## Knowledge-Driven Industrial IoT Fault Diagnosis Assistant

**Student Name:** KUSHAGRA SHAROYA  
**Roll Number:** 2400320100636  
**Mentor Name:** VIKAS MAURYA  
**Presentation Duration:** ~3 Minutes (Standard Hackathon / Viva Format)  
**Version:** v1.0 | October 2026  

---

## 🎬 3-Minute Live Demo Walkthrough Script

| Timestamp | Screen Action / Mouse Interaction | Spoken Presentation Dialogue (What to Say) | Key Technical Concepts to Highlight |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:25** | Open **`http://localhost:8501`** (or double-click [DEMO_INTERACTIVE_SHOWCASE.html](DEMO_INTERACTIVE_SHOWCASE.html)). Point mouse to the top header banner and the 3-Machine Fleet Ribbon. | *"Respected mentors and evaluators, I am Kushagra Sharoya. Today I am presenting project P_311: our Knowledge-Driven Industrial IoT Fault Diagnosis Assistant. Across modern CNC machining lines, sudden spindle breakdowns cost thousands of dollars per hour. Here on screen, you see our 3-machine production cell streaming real-time physical telemetry over MQTT to our Mosquitto broker."* | Multi-machine IoT fleet architecture, MQTT asynchronous protocol, 3 industrial machine quality grades (M, H, L). |
| **0:25 - 0:50** | Hover over the 4 Plotly speedometer gauges (Speed, Torque, Process Temp, Tool Wear) and the baseline 0.27% failure risk. | *"Currently, Machine 1 (CNC Milling Center) is running in its nominal envelope. Notice our Plotly speedometer dials: Spindle Speed is at 1,526 RPM, Torque is nominal at 41 Nm, cutting temperature is 308 Kelvin, and Tool Wear is at 45 minutes. Our Gradient Boosting classifier continuously evaluates risk at a negligible 0.27%, well below our 40% operating threshold."* | Non-linear sensor correlations, gradient boosting inference latency (<2ms), baseline operating thresholds. |
| **0:50 - 1:20** | In the sidebar or toolbar, click the **"🔴 Send Fault"** button (or **"⚠️ Spindle Stall"**). | *"Now, let us simulate a severe industrial fault: an acute cutting load spike and spindle stall. As I trigger the fault injection, observe the immediate transition! The top status badge pulses crimson: 'FAULT RISK DETECTED'. Spindle rotational speed drops to 1,120 RPM while motor torque spikes past 72 Nm. Our Gradient Boosting classifier immediately calculates an 89.1% failure probability, crossing our calibrated 40% decision threshold."* | Asymmetrical business cost of false negatives vs false positives; why the threshold is calibrated to 0.40 (72.1% recall). |
| **1:20 - 1:50** | Smoothly scroll down to the **Explainable AI (XAI)** Feature Attribution bar chart and the **Tool RUL** card. | *"Standard AI in industry fails because it acts as an ungrounded black box. To solve this, our system introduces Explainable AI (XAI). Looking at our real-time attribution bar chart, the operator sees immediately that Spindle Torque (82%) and Rotational Stall (65%) are the primary drivers of this failure probability. Meanwhile, our Remaining Useful Life card tracks degradation towards the 150-minute tool replacement limit."* | Explainable AI (XAI) feature attribution, removing black-box stigma, RUL degradation countdown. |
| **1:50 - 2:25** | Point to the **Stage 5 FAISS Semantic RAG Box** and the **Stage 6 Local LLM Copilot Briefing Box**. | *"Next, the maintenance technician needs to know how to fix it. Our physical rule engine isolates the compound condition and queries our FAISS vector database. Using 384-dimensional dense semantic embeddings, FAISS retrieves the certified OEM maintenance standard operating procedure in under 5 milliseconds. Our Stage 6 Local LLM Copilot then synthesizes this into an actionable briefing: Situation Summary, Root-Cause Assessment, and an Immediate Step-by-Step Action Plan with a 100% zero-hallucination guarantee."* | FAISS dense vector search (`IndexFlatIP`), Sentence Transformers (`all-MiniLM-L6-v2`), zero-hallucination grounded LLM synthesis. |
| **2:25 - 2:50** | Click **"🟢 Send Normal"** (or Nominal Cycle), switch dropdown to `machine2` and `machine3`, then expand the **Audit Trail**. | *"With one click, we restore nominal parameters. Plant supervisors can switch between the Lathe and High Speed Grinder seamlessly. Finally, every single reading, prediction, and technician directive is recorded to our embedded SQLite database. Technicians can inspect the full historical audit log and export it to CSV with one click."* | SQLite persistence, atomic multi-machine state caching, regulatory traceability, CSV data portability. |
| **2:50 - 3:00** | Return to the top overview card and conclude. | *"To conclude, project P_311 delivers an end-to-end, explainable, and cost-effective predictive maintenance solution at under ₹3,000 INR per machine cell, bridging the gap between advanced machine learning and real factory maintenance. Thank you, and I look forward to your questions."* | Total BOM cost (₹2,935/machine), commercial brownfield feasibility, Industry 4.0 modernization. |

---

## 🎯 Top 5 Viva Questions & Winning Defense Answers

### 1. "Why did you use Gradient Boosting instead of an LSTM or Deep Learning?"
* **Winning Answer:** *"For tabular industrial sensor data, tree-based ensemble models like Gradient Boosting consistently outperform deep neural networks in sample efficiency, interpretability, and noise resistance. On the AI4I dataset, our Gradient Boosting model achieved a 0.9696 ROC-AUC score with sub-2 millisecond CPU inference latency, eliminating the need for expensive, high-power GPUs on the factory floor."*

### 2. "Why is your operating threshold 0.40 instead of the standard 0.50?"
* **Winning Answer:** *"In predictive maintenance, the business cost of a False Negative (a missed breakdown causing tool breakage or factory stoppage) is vastly higher than a False Positive (an early technician inspection). By tuning the decision threshold from 0.50 down to 0.40, we increased minority failure recall from 58.8% to 72.1% while maintaining an 84.5% precision rate, optimizing the operational cost trade-off."*

### 3. "How did you avoid Target Leakage?"
* **Winning Answer:** *"In the AI4I 2020 dataset, columns like Tool Wear Failure (TWF), Heat Dissipation Failure (HDF), and Power Failure (PWF) directly identify the failure modes. Including them as inputs artificially inflates test accuracy to 100% because the model simply checks if any failure column is 1. In real-world factory operations, those labels do not exist until after failure occurs. We strictly excluded them and trained solely on raw physical telemetry: Air Temp, Process Temp, Speed, Torque, Tool Wear, and Machine Type."*

### 4. "Why use RAG instead of fine-tuning an LLM?"
* **Winning Answer:** *"First, Zero Hallucination: fine-tuned LLMs can still hallucinate technical parameters. RAG anchors recommendations strictly in verified OEM text. Second, Dynamic Updates: when factory maintenance SOPs change, the text file is re-indexed in FAISS in seconds without expensive model retraining. Third, Edge Efficiency: FAISS runs locally on edge CPU hardware in under 5 milliseconds."*

### 5. "What is the hardware deployment cost?"
* **Winning Answer:** *"Our complete Bill of Materials (BOM) utilizes an ESP32 DevKit v1 edge gateway with non-invasive SCT-013 current clamps, K-Type thermocouples, and optical encoders. The total hardware investment averages just ₹2,935 INR per machine cell, making large-scale retrofitting of legacy factory machines economically feasible."*
