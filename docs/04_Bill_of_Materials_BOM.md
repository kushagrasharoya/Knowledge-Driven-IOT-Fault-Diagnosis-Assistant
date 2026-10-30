# P_311 — Bill of Materials (BOM) & Hardware Specifications
## Knowledge-Driven Industrial IoT Fault Diagnosis Assistant

**Student Name:** KUSHAGRA SHAROYA  
**Roll Number:** 2400320100636  
**Mentor Name:** VIKAS MAURYA  
**Domain:** Embedded Systems & Industrial IoT (IIoT)  
**Standard Compliance:** HCLTech BTech Project Guidelines (Section 5)  
**Document Version:** v1.0 | October 2026  

---

## 1. Executive Hardware Summary

This Bill of Materials (BOM) specifies the industrial edge data acquisition hardware required to deploy the **P_311 Industrial IoT Fault Diagnosis Assistant** onto a 3-machine factory cell (CNC Milling Center, Heavy Duty Lathe, and High Speed Grinder). 

The edge architecture utilizes an **ESP32 DevKit v1 38-Pin Microcontroller** as the central IoT gateway node per machine, coupled with industrial-grade physical transducers for thermal, mechanical, electrical, and rotational measurements.

---

## 2. Complete Bill of Materials (BOM) Table

| S.No | Component Description | Part / Model Number | Qty | Unit Cost (INR) | Total Cost (INR) | Recommended Supplier | Technical Role in System |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **1** | **ESP32 Dual-Core DevKit v1 (38 Pins)** | ESP-WROOM-32 | 3 | ₹450 | ₹1,350 | Robu.in | Core edge gateway; runs telemetry sampling & MQTT publishing. |
| **2** | **K-Type Thermocouple + MAX6675 Module** | MAX6675-K | 3 | ₹280 | ₹840 | Robu.in / Amazon | Measures high-precision tool cutting process temperature ($0 - 600^\circ\text{C}$). |
| **3** | **Digital Ambient Temp & Humidity Sensor** | DHT22 / AM2302 | 3 | ₹180 | ₹540 | Amazon | Measures factory ambient air temperature around the machine. |
| **4** | **Non-Invasive AC Current Sensor (100A/50mA)** | SCT-013-000 | 3 | ₹320 | ₹960 | Robu.in | Clamps on spindle motor phase wire to derive cutting torque from current draw. |
| **5** | **Optical Incremental Rotary Encoder** | E6B2-CWZ6C (1000 P/R) | 3 | ₹650 | ₹1,950 | Robu.in | Measures spindle rotational speed (RPM) via hardware pulse interrupt counters. |
| **6** | **0.96" I2C Monochrome OLED Display** | SSD1306 (128x64) | 3 | ₹180 | ₹540 | Robu.in | Local machine-side dashboard displaying IP, status, and failure probability. |
| **7** | **Industrial Active Alarm Buzzer & Red Strobe LED** | 5V Active Buzzer Module | 3 | ₹45 | ₹135 | Local Electronics | Physical sound & light beacon for `CRITICAL` severity machine shutdown warnings. |
| **8** | **Industrial Buck Converter (24V DC to 5V DC, 3A)** | LM2596 Step-Down Module | 3 | ₹120 | ₹360 | Amazon | Converts factory 24V machine cabinet power to clean 5V DC logic power. |
| **9** | **Signal Conditioning & Burden Resistor PCB** | Custom Proto-PCB + Resistors | 3 | ₹90 | ₹270 | Local / Robu.in | Converts SCT-013 AC current output to 0-3.3V DC centered analog signal for ESP32 ADC. |
| **10** | **IP65 Industrial DIN-Rail Enclosure Box** | ABS Flame-Retardant Box | 3 | ₹250 | ₹750 | Amazon / Local | Protects edge hardware from industrial coolant splash, metal chips, and dust. |
| **11** | **Industrial Shielded Cable & Jumper Harness** | 4-Core Shielded Sensor Cable (5m) | 3 | ₹150 | ₹450 | Local Wire Mart | Connects sensors to control box while shielding against spindle VFD electromagnetic noise. |
| **12** | **Heavy-Duty 5V 2.5A Micro-USB Power Supply** | 5V 2.5A BIS Certified | 3 | ₹220 | ₹660 | Amazon | Backup standalone bench-testing power adapter. |
| **--** | **TOTAL ESTIMATED HARDWARE INVESTMENT** | -- | -- | -- | **₹8,805 INR** | *(Covers full 3-Machine Fleet Cell)* | Average: **₹2,935 INR / Machine** |

---

## 3. Component Selection Rationale & Trade-Off Analysis

### 3.1 ESP32 vs. Arduino Uno vs. Raspberry Pi
* **Selection:** **ESP32 DevKit v1**.
* **Rationale:** An Arduino Uno lacks integrated Wi-Fi/Ethernet and has insufficient memory (2 KB SRAM) to handle modern TLS and JSON serialization. A Raspberry Pi 4 is excessive in cost (~₹6,500/unit) and vulnerable to SD card corruption upon abrupt shop-floor power loss. The ESP32 provides dual 240 MHz Tensilica cores, native Wi-Fi/Bluetooth, hardware timer pulse accumulators for rotary encoders, and instant boot times at a fraction of the cost.

### 3.2 SCT-013 Non-Invasive Current Transformer vs. Inline Shunt
* **Selection:** **SCT-013-000 Current Clamp**.
* **Rationale:** In active factory production, cutting into 415V 3-phase spindle motor wiring to install inline shunts violates safety regulations and halts plant production. The SCT-013 non-invasive split-core clamp clips over the insulated conductor without disrupting machine wiring. Torque is calculated using the standard electromechanical relation:
  $$\tau = \frac{k_t \cdot V \cdot I \cdot \cos(\theta)}{\omega}$$

### 3.3 K-Type Thermocouple with MAX6675 vs. NTC Thermistor
* **Selection:** **MAX6675 Cold-Junction-Compensated SPI Thermocouple**.
* **Rationale:** Metal-cutting zones routinely exceed $200^\circ\text{C}$ where ordinary glass-bead NTC thermistors degrade or melt. K-type thermocouples operate up to $1000^\circ\text{C}$ with stainless steel braiding, providing industrial resilience.

---

## 4. Edge Hardware Assembly & Calibration Notes

1. **ADC Calibration on ESP32:**
   The ESP32 ADC exhibits non-linearity below $0.15\text{V}$ and above $3.15\text{V}$. The analog signal conditioning board offsets the SCT-013 output to $1.65\text{V}$ virtual ground using a precision $10\text{k}\Omega$ voltage divider with a $10\mu\text{F}$ filtering capacitor, ensuring linear sampling.
2. **Electromagnetic Interference (EMI) Mitigation:**
   Variable Frequency Drives (VFDs) driving milling spindles emit significant electromagnetic interference. All sensor leads must use grounded foil-shielded twisted-pair cables, and the ESP32 must reside in a grounded metal or shielded IP65 enclosure.
3. **MQTT Telemetry Failover:**
   If factory Wi-Fi drops, the ESP32 firmware utilizes a circular RAM buffer storing up to 100 historical readings, publishing them in burst mode once connection to the Mosquitto broker is restored.
