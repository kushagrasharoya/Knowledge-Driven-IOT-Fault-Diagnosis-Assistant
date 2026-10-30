# 🎓 P_311 — Complete Viva & Hackathon Defense Guide
**Project Title:** P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant  
**Domain:** Industrial IoT (IIoT), Predictive Maintenance, Machine Learning, Retrieval-Augmented Generation (RAG), Edge AI

---

## 1. High-Level Elevator Pitch (30-Second Summary)

> *"Our project is an end-to-end industrial predictive maintenance and intelligent fault diagnosis system. A multi-machine IoT fleet streams sensor telemetry over MQTT. A Gradient Boosting machine learning model predicts machine failure probability in real time. When anomalies arise, a physical diagnosis engine detects root sensor conditions, which dynamically queries a FAISS vector database to retrieve grounded maintenance procedures (RAG). Finally, a Local LLM synthesizes this into an actionable technician briefing displayed on a real-time Streamlit dashboard alongside Explainable AI (XAI) feature attributions and Remaining Useful Life (RUL) estimates."*

---

## 2. Top 10 Technical Questions & Winning Answers

### Q1: Why use Machine Learning for fault detection instead of simple rule-based thresholds?
* **Answer:**  
  *"Simple thresholds (e.g. Temperature > 80°C) fail when compound degradation occurs. A machine might fail even when individual sensor readings appear within nominal bounds if elevated torque coincides with high tool wear and subtle thermal changes. Our Gradient Boosting model captures non-linear interactions across multidimensional sensor variables simultaneously, enabling predictive warnings before catastrophic thresholds are breached."*

---

### Q2: Why Gradient Boosting over Deep Learning (LSTM / CNN)?
* **Answer:**  
  *"For tabular sensor telemetry, ensemble tree-based models like Gradient Boosting consistently outperform deep neural networks in sample efficiency, interpretability, and inference speed. On the AI4I 2020 dataset, our Gradient Boosting model achieved a 0.9696 ROC-AUC with sub-millisecond inference latency on standard edge CPU hardware, without requiring power-hungry GPUs."*

---

### Q3: Why is the classification threshold set to 0.40 instead of the standard 0.50?
* **Answer:**  
  *"In predictive maintenance, the business cost of a False Negative (a missed breakdown causing factory stoppage or equipment destruction) is vastly higher than a False Positive (an early preventive inspection). By tuning the decision threshold from 0.50 down to 0.40, we increased failure recall from 58.8% to over 72% while maintaining strong precision (84.5%), optimizing the operational trade-off."*

---

### Q4: Why did you exclude TWF, HDF, PWF, OSF, and RNF from the training features?
* **Answer:**  
  *"Because of **Target Leakage**. In the AI4I dataset, columns like Tool Wear Failure (TWF) and Heat Dissipation Failure (HDF) directly encode specific failure modes. Including them as inputs would artificially inflate test accuracy to 100% because the model would simply check if any failure mode column was 1. In real-world factory operations, those labels do not exist until after failure occurs. We strictly trained on raw operational telemetry: Air Temperature, Process Temperature, Rotational Speed, Torque, Tool Wear, and Machine Type."*

---

### Q5: How did you address the 3.39% class imbalance in the AI4I dataset?
* **Answer:**  
  *"1. We did not rely on standard accuracy (which is deceptively 96.6% even for a dummy model predicting zero failures).  
   2. We evaluated Balanced Accuracy, Precision, Recall, F1-Score, and ROC-AUC (0.9696).  
   3. We used stratified train/test splitting to preserve minority class ratios.  
   4. We tuned the decision probability threshold (0.40) to boost recall on minority failure events."*

---

### Q6: Why use RAG (Retrieval-Augmented Generation) instead of fine-tuning an LLM?
* **Answer:**  
  *"1. **Zero Hallucination:** Fine-tuned LLMs can still hallucinate technical parameters (e.g. wrong torque limits or incorrect coolant ratios). RAG forces the assistant to base its recommendations strictly on retrieved OEM maintenance documents.  
   2. **Dynamic Knowledge Updates:** When factory SOPs or tool replacement guides update, we simply re-index the text file into the FAISS vector database without expensive LLM retraining.  
   3. **Resource Efficiency:** RAG runs on lightweight CPU embeddings (`all-MiniLM-L6-v2`) with sub-5ms vector similarity lookups."*

---

### Q7: Why use FAISS and Sentence Transformers instead of keyword search?
* **Answer:**  
  *"Keyword search fails when terminology varies (e.g. searching 'spindle overload' would miss documents titled 'high mechanical resistance'). Sentence Transformers (`all-MiniLM-L6-v2`) map text into a 384-dimensional dense semantic vector space. FAISS calculates cosine similarity across these vectors, enabling semantic conceptual matching regardless of exact wording."*

---

### Q8: What is the role of the Local LLM (Stage 6)?
* **Answer:**  
  *"RAG retrieves raw manual excerpts, which are dense and technical. The Local LLM acts as an intelligent shop-floor copilot. It takes:  
   1. Live telemetry values,  
   2. Failure probability and severity,  
   3. Diagnosed conditions, and  
   4. Retrieved maintenance context,  
   and generates a concise, personalized briefing: Situation Summary, Root-Cause Assessment, and a Step-by-Step Action Plan."*

---

### Q9: Why MQTT instead of HTTP REST APIs?
* **Answer:**  
  *"MQTT is a lightweight publish/subscribe protocol designed specifically for industrial telemetry. Unlike HTTP (which requires heavy headers and request-response handshakes), MQTT uses minimal binary headers, supports asynchronous decoupling, enables wildcard topic subscriptions (e.g., `factory/+/sensors` for multi-machine fleets), and operates reliably over low-bandwidth shop-floor networks."*

---

### Q10: What are your Explainable AI (XAI) and Remaining Useful Life (RUL) features?
* **Answer:**  
  *"1. **Explainable AI (XAI):** A live feature-attribution chart breaks down which sensor inputs (Torque, Tool Wear, Speed, or Thermal Delta) contributed most to the current failure probability, removing the 'black box' stigma.  
   2. **Remaining Useful Life (RUL):** Rather than a binary fault alarm, we calculate the estimated remaining operating minutes on the active cutting tool before reaching the 150-minute replacement limit, enabling proactive shift planning."*

---

## 3. Technology Stack Reference

| Layer | Technologies Used |
|---|---|
| **IoT Transport** | MQTT (Eclipse Mosquitto broker, `paho-mqtt` client) |
| **Data Persistence** | SQLite (`machine_data.db`), JSON live snapshot cache |
| **Machine Learning** | Scikit-Learn (Gradient Boosting Classifier, Joblib) |
| **Dataset** | AI4I 2020 Predictive Maintenance Dataset (UCI Machine Learning Repository) |
| **Vector DB & RAG** | FAISS (`faiss-cpu`), Hugging Face `sentence-transformers` (`all-MiniLM-L6-v2`) |
| **Local LLM** | Multi-backend: Local Ollama API / Zero-latency Grounded Synthesizer |
| **Frontend Dashboard** | Streamlit, Plotly interactive charts, custom CSS dark industrial theme |
