"""
ai4i_machine_simulator.py
-------------------------
Simulates a multi-machine industrial cell publishing AI4I-compatible telemetry to MQTT.
Supports a fleet of 3 machines:
- machine1: CNC Milling Center (Type M)
- machine2: Heavy Duty Lathe (Type H)
- machine3: High Speed Grinder (Type L)

Topics: factory/{machine_id}/sensors
Configured via config.py.
"""

import json
import random
import time
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_BASE_TOPIC, MQTT_USE_TLS

FLEET = [
    {"id": "machine1", "name": "CNC Milling Center", "default_type": "M"},
    {"id": "machine2", "name": "Heavy Duty Lathe", "default_type": "H"},
    {"id": "machine3", "name": "High Speed Grinder", "default_type": "L"},
]

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

if MQTT_USE_TLS:
    client.tls_set()

client.connect(MQTT_BROKER, MQTT_PORT)

print("=" * 65)
print("P_311 Multi-Machine Fleet Telemetry Simulator Started")
print(f"MQTT Broker : {MQTT_BROKER}:{MQTT_PORT}")
print(f"Fleet Size  : {len(FLEET)} Industrial Machines")
for m in FLEET:
    print(f"  • {m['id']}: {m['name']} (Type {m['default_type']})")
print("Publishing sensor telemetry every 2 seconds...")
print("=" * 65 + "\n")

cycle_count = 0
try:
    while True:
        cycle_count += 1
        # Cycle through machines in the fleet
        machine = FLEET[(cycle_count - 1) % len(FLEET)]
        m_id = machine["id"]
        topic = f"{MQTT_BASE_TOPIC}/{m_id}/sensors"

        # 80% Normal, 20% Anomalous
        is_fault = (random.random() >= 0.80)

        if not is_fault:
            sensor_data = {
                "machine_id": m_id,
                "machine_name": machine["name"],
                "type": machine["default_type"],
                "air_temperature": round(random.uniform(298.0, 300.0), 1),
                "process_temperature": round(random.uniform(308.0, 310.0), 1),
                "rotational_speed": random.randint(1420, 1580),
                "torque": round(random.uniform(36.0, 48.0), 1),
                "tool_wear": random.randint(10, 85)
            }
        else:
            sensor_data = {
                "machine_id": m_id,
                "machine_name": machine["name"],
                "type": machine["default_type"],
                "air_temperature": round(random.uniform(300.5, 303.5), 1),
                "process_temperature": round(random.uniform(312.0, 315.5), 1),
                "rotational_speed": random.randint(1120, 1340),
                "torque": round(random.uniform(55.0, 72.0), 1),
                "tool_wear": random.randint(120, 220)
            }

        client.publish(topic, json.dumps(sensor_data))
        status_tag = "[FAULT RISK]" if is_fault else "[NORMAL]"
        print(f"[PUBLISH -> {m_id}] {status_tag} Speed: {sensor_data['rotational_speed']} RPM, Torque: {sensor_data['torque']} Nm, Wear: {sensor_data['tool_wear']} min")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nSimulator stopped by user.")
    client.disconnect()
