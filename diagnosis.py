"""
diagnosis.py
------------
Rule-based diagnosis engine that analyzes sensor readings and ML failure probability.
Identifies abnormal sensor conditions, assigns severity, and generates recommendations.
Thresholds are dynamically loaded from config.py.
"""

from config import (
    AIR_TEMP_WARN,
    PROC_TEMP_WARN,
    RPM_MIN_WARN,
    RPM_MAX_WARN,
    TORQUE_WARN,
    TOOL_WEAR_WARN,
    TOOL_WEAR_CRITICAL,
    SEVERITY_CRITICAL_THRESHOLD,
    SEVERITY_HIGH_THRESHOLD,
    SEVERITY_MEDIUM_THRESHOLD,
    DECISION_THRESHOLD
)

def diagnose_machine(sensor_data: dict, failure_probability: float):
    """
    Evaluates sensor values and failure probability to return:
    - status: "FAULT RISK" or "NORMAL"
    - severity: "CRITICAL", "HIGH", "MEDIUM", or "LOW"
    - conditions: list of identified abnormal sensor conditions
    - recommendation: operational maintenance guidance
    """
    conditions = []

    air_temp = sensor_data.get("air_temperature", 300.0)
    proc_temp = sensor_data.get("process_temperature", 310.0)
    rpm = sensor_data.get("rotational_speed", 1500)
    torque = sensor_data.get("torque", 40.0)
    tool_wear = sensor_data.get("tool_wear", 0)

    # 1. Evaluate sensor conditions against calibrated thresholds
    if air_temp >= AIR_TEMP_WARN:
        conditions.append("Elevated air temperature")

    if proc_temp >= PROC_TEMP_WARN:
        conditions.append("High process temperature")

    if rpm < RPM_MIN_WARN:
        conditions.append("Low rotational speed")
    elif rpm > RPM_MAX_WARN:
        conditions.append("High rotational speed")

    if torque >= TORQUE_WARN:
        conditions.append("High torque")

    if tool_wear >= TOOL_WEAR_CRITICAL:
        conditions.append("High tool wear")
    elif tool_wear >= TOOL_WEAR_WARN:
        conditions.append("Increasing tool wear")

    if not conditions:
        conditions.append("No major abnormal sensor condition detected")

    # 2. Determine severity based on ML failure probability
    if failure_probability >= SEVERITY_CRITICAL_THRESHOLD:
        severity = "CRITICAL"
        recommendation = "Stop or isolate the machine and perform immediate inspection."
    elif failure_probability >= SEVERITY_HIGH_THRESHOLD:
        severity = "HIGH"
        recommendation = "Schedule immediate maintenance inspection and check the identified sensor conditions."
    elif failure_probability >= SEVERITY_MEDIUM_THRESHOLD:
        severity = "MEDIUM"
        recommendation = "Continue monitoring the machine and schedule preventive maintenance."
    else:
        severity = "LOW"
        recommendation = "Machine appears stable. Continue normal monitoring."

    # 3. Overall machine status based on operating threshold
    status = "FAULT RISK" if failure_probability >= DECISION_THRESHOLD else "NORMAL"

    return {
        "status": status,
        "severity": severity,
        "conditions": conditions,
        "recommendation": recommendation
    }
