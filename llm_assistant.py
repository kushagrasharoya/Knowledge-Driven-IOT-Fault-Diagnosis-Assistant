"""
llm_assistant.py
----------------
Stage 6: Local LLM Integration for P_311.
Synthesizes live telemetry, ML failure probability, diagnosed conditions,
and FAISS-retrieved maintenance knowledge into a technician-friendly explanation.

Supports:
1. Local Ollama API (e.g., llama3.2, phi3, mistral) if running on http://localhost:11434
2. Zero-latency Grounded Synthesizer as an automatic reliable fallback.
Configured via config.py.
"""

import json
import requests
from config import OLLAMA_URL, DEFAULT_LLM_MODEL, LLM_TIMEOUT

def generate_technician_briefing(
    sensor_data: dict,
    failure_probability: float,
    status: str,
    severity: str,
    conditions: list[str],
    rag_knowledge: str,
    model_name: str = DEFAULT_LLM_MODEL
) -> str:
    """
    Generates a natural-language technician explanation.
    Tries local Ollama LLM first; if unavailable, uses grounded fallback synthesizer.
    """
    prob_pct = failure_probability * 100
    air_t = sensor_data.get("air_temperature", 300.0)
    proc_t = sensor_data.get("process_temperature", 310.0)
    rpm = sensor_data.get("rotational_speed", 1500)
    torque = sensor_data.get("torque", 40.0)
    wear = sensor_data.get("tool_wear", 0)
    m_type = sensor_data.get("type", "M")

    # If normal with no anomalies, return reassuring operational summary
    is_normal = (status == "NORMAL" and conditions == ["No major abnormal sensor condition detected"])
    if is_normal and prob_pct < 20.0:
        return (
            f"[OK] [NOMINAL OPERATION] Machine {m_type} is running within healthy operating parameters. "
            f"Failure risk is negligible ({prob_pct:.2f}%). Rotational speed ({rpm} RPM) and spindle torque ({torque:.1f} Nm) "
            f"are balanced. Tool wear is currently at {wear} min (well below the 150 min threshold). "
            f"Directive: Continue scheduled cycle without intervention."
        )

    # 1. Attempt generation via Local Ollama if available
    prompt = f"""You are the P_311 Industrial AI Technician Assistant for CNC Machine Type {m_type}.
Synthesize the machine telemetry and RAG maintenance knowledge into a concise, professional briefing for a shop-floor technician.
Strict Rule: Rely ONLY on the provided maintenance procedure. Do NOT invent steps.

[LIVE TELEMETRY]
- Failure Probability: {prob_pct:.2f}% (Severity: {severity})
- Air Temp: {air_t:.1f} K | Process Temp: {proc_t:.1f} K (Heat Differential DT: {proc_t - air_t:.1f} K)
- Rotational Speed: {rpm} RPM
- Spindle Torque: {torque:.1f} Nm
- Tool Wear: {wear} min

[DETECTED CONDITIONS]
{", ".join(conditions)}

[RETRIEVED MAINTENANCE KNOWLEDGE (GROUND TRUTH)]
{rag_knowledge}

Structure your response into:
1. SITUATION SUMMARY (What is happening)
2. ROOT CAUSE ASSESSMENT (Why it is happening based on telemetry)
3. TECHNICIAN ACTION PLAN (Numbered immediate steps)
"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 300}
            },
            timeout=LLM_TIMEOUT
        )
        if response.status_code == 200:
            res_json = response.json()
            briefing = res_json.get("response", "").strip()
            if briefing:
                return f"[Ollama LLM - {model_name}]\n{briefing}"
    except Exception:
        # Fall back to grounded synthesizer if Ollama is offline or timed out
        pass

    # 2. Grounded Generative Synthesizer (Zero-latency fallback)
    alert_tag = "[CRITICAL ALERT]" if severity in ["CRITICAL", "HIGH"] else "[WARNING]"
    
    # Extract causes and steps from RAG text
    causes_text = ""
    inspection_text = ""
    actions_text = ""
    
    if rag_knowledge:
        lines = rag_knowledge.split("\n")
        section = None
        causes = []
        inspections = []
        actions = []
        for line in lines:
            line_str = line.strip()
            if "Possible Causes:" in line_str:
                section = "causes"
                continue
            elif "Inspection Steps:" in line_str:
                section = "inspections"
                continue
            elif "Recommended Actions:" in line_str:
                section = "actions"
                continue
            elif line_str.startswith("TOPIC:") or line_str.startswith("Condition:"):
                continue

            if section == "causes" and line_str.startswith("-"):
                causes.append(line_str.lstrip("- "))
            elif section == "inspections" and any(line_str.startswith(f"{i}.") for i in range(1, 10)):
                inspections.append(line_str)
            elif section == "actions" and line_str.startswith("-"):
                actions.append(line_str.lstrip("- "))

        if causes:
            causes_text = " - " + "\n - ".join(causes[:3])
        if inspections:
            inspection_text = "\n".join(f"  {step}" for step in inspections[:3])
        if actions:
            actions_text = " - " + "\n - ".join(actions[:3])

    briefing = f"""{alert_tag} [SITUATION SUMMARY - {severity} RISK ({prob_pct:.1f}%)]
Machine Type {m_type} has triggered active maintenance warnings: {', '.join(conditions)}.
Live Telemetry highlights:
  - Spindle Torque: {torque:.1f} Nm {'(EXCEEDS 55 Nm LIMIT)' if torque >= 55 else ''}
  - Rotational Speed: {rpm} RPM {'(BELOW 1300 RPM CRITICAL STALL)' if rpm < 1300 else ''}
  - Tool Wear: {wear} min {'(EXCEEDS 150 min CRITICAL WEAR)' if wear >= 150 else ''}
  - Process Temp: {proc_t:.1f} K (Heat Differential DT: {proc_t - air_t:.1f} K)

[ROOT CAUSE ASSESSMENT]
Telemetry deviations indicate mechanical strain and wear progression:
{causes_text if causes_text else ' - Compound thermal and mechanical stress on active cutting tooling.'}

[TECHNICIAN ACTION PLAN]
Immediate Inspection Checklist:
{inspection_text if inspection_text else '  1. Halt spindle and verify workpiece clearance.\n  2. Inspect cutting tool edge for wear or chipping.\n  3. Verify coolant flow rate.'}

Prescribed Corrective Actions:
{actions_text if actions_text else ' - Replace worn tool inserts.\n - Reduce feed rate.\n - Clear mechanical binding.'}"""

    return briefing

if __name__ == "__main__":
    print("--- Testing LLM Assistant Module ---")
    sample_sensor = {
        "type": "H",
        "air_temperature": 303.0,
        "process_temperature": 314.5,
        "rotational_speed": 1150,
        "torque": 66.0,
        "tool_wear": 195
    }
    sample_conditions = ["Elevated air temperature", "High process temperature", "Low rotational speed", "High torque", "High tool wear"]
    from rag_retriever import get_maintenance_for_conditions
    rag_doc = get_maintenance_for_conditions(sample_conditions, top_k=1)
    
    output = generate_technician_briefing(
        sample_sensor,
        0.825,
        "FAULT RISK",
        "CRITICAL",
        sample_conditions,
        rag_doc
    )
    print("\n" + output)
