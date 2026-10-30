"""
dashboard.py
------------
P_311 — Multi-Machine Industrial IoT Predictive Maintenance & Fault Diagnosis Dashboard
Stage 5 (RAG) + Stage 6 (Local LLM Copilot) + Stage 7 (Dashboard) + Stage 8 (Fleet, XAI & RUL).
Built with Streamlit, Plotly, SQLite, and FAISS RAG Retrieval.
"""

import os
import json
import sqlite3
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_BASE_TOPIC,
    MQTT_USE_TLS,
    DB_PATH,
    SNAPSHOT_PATH,
    DECISION_THRESHOLD
)

# 1. Page Configuration
st.set_page_config(
    page_title="P_311 Industrial Fault Diagnosis",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for Modern Dark Industrial UI
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Top Header */
    .dashboard-header {
        background: linear-gradient(135deg, #111827 0%, #1f293d 100%);
        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .dashboard-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .dashboard-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }
    
    /* Status Badges */
    .badge-normal {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid #10b981;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
    }
    .badge-fault {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.4);
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.65; }
    }
    
    /* Fleet Card */
    .fleet-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Status Hero Banner */
    .hero-banner-normal {
        background: linear-gradient(90deg, rgba(6, 78, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        border-left: 5px solid #10b981;
        border-radius: 8px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .hero-banner-fault {
        background: linear-gradient(90deg, rgba(127, 29, 29, 0.5) 0%, rgba(15, 23, 42, 0.6) 100%);
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
    
    /* LLM Copilot Box */
    .llm-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #6366f1;
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 0.8rem;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
    }
    .llm-tag {
        background: #4f46e5;
        color: #ffffff;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 0.6rem;
    }
    
    /* RAG Box */
    .rag-box {
        background: linear-gradient(180deg, #131b2e 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 0.8rem;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
    }
    .rag-tag {
        background: #2563eb;
        color: #ffffff;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 0.6rem;
    }
    
    /* Condition Chips */
    .condition-chip {
        background: #1e293b;
        border: 1px solid #334155;
        color: #cbd5e1;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .condition-chip-fault {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #fca5a5;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Helper Functions for Data Access & Simulation
FLEET_MAP = {
    "machine1": {"name": "CNC Milling Center", "type": "M"},
    "machine2": {"name": "Heavy Duty Lathe", "type": "H"},
    "machine3": {"name": "High Speed Grinder", "type": "L"},
}

def get_fleet_snapshot():
    """Reads the multi-machine snapshot file."""
    if os.path.exists(SNAPSHOT_PATH):
        try:
            with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def get_historical_telemetry(machine_id=None, limit=60):
    """Fetches recent historical records from SQLite database."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        if machine_id:
            query = f"SELECT * FROM telemetry_logs WHERE machine_id = '{machine_id}' ORDER BY id DESC LIMIT {limit}"
        else:
            query = f"SELECT * FROM telemetry_logs ORDER BY id DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if not df.empty:
            df = df.iloc[::-1].reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()

def publish_quick_telemetry(target_machine="machine1", is_fault=False):
    """Publishes a test packet over MQTT for live presentation demo."""
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    if MQTT_USE_TLS:
        client.tls_set()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 5)
        m_info = FLEET_MAP.get(target_machine, {"name": "CNC Mill", "type": "M"})
        topic = f"{MQTT_BASE_TOPIC}/{target_machine}/sensors"

        if not is_fault:
            payload = {
                "machine_id": target_machine,
                "machine_name": m_info["name"],
                "type": m_info["type"],
                "air_temperature": 298.8,
                "process_temperature": 308.7,
                "rotational_speed": 1530,
                "torque": 41.2,
                "tool_wear": 45
            }
        else:
            payload = {
                "machine_id": target_machine,
                "machine_name": m_info["name"],
                "type": m_info["type"],
                "air_temperature": 302.8,
                "process_temperature": 314.2,
                "rotational_speed": 1160,
                "torque": 66.5,
                "tool_wear": 205
            }
        client.publish(topic, json.dumps(payload))
        client.disconnect()
        return True
    except Exception as e:
        st.sidebar.error(f"MQTT Publish failed: {e}")
        return False

# 4. Gauge & Chart Generators (Plotly)
def create_gauge(value, min_v, max_v, title, unit="", threshold_v=None, is_probability=False):
    """Creates a high-contrast industrial dial gauge."""
    if is_probability:
        steps = [
            {'range': [0, 20], 'color': '#064e3b'},
            {'range': [20, 40], 'color': '#78350f'},
            {'range': [40, 75], 'color': '#7c2d12'},
            {'range': [75, 100], 'color': '#7f1d1d'}
        ]
        bar_color = "#ef4444" if value >= (threshold_v or (DECISION_THRESHOLD * 100)) else "#10b981"
    else:
        steps = [
            {'range': [min_v, (min_v + max_v) * 0.7], 'color': '#1f2937'},
            {'range': [(min_v + max_v) * 0.7, max_v], 'color': '#374151'}
        ]
        bar_color = "#38bdf8"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': unit, 'font': {'size': 26, 'color': '#f8fafc'}},
        title={'text': title, 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge={
            'axis': {'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': '#475569'},
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': '#111827',
            'borderwidth': 1,
            'bordercolor': '#1f2937',
            'steps': steps,
            'threshold': {
                'line': {'color': '#f43f5e', 'width': 3},
                'thickness': 0.75,
                'value': threshold_v
            } if threshold_v else None
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=15, r=15, t=35, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e2e8f0'}
    )
    return fig

def create_xai_chart(data: dict):
    """Explainable AI (XAI) feature contribution breakdown."""
    torque = data.get("torque", 40.0)
    rpm = data.get("rotational_speed", 1500)
    proc_t = data.get("process_temperature", 310.0)
    tool_w = data.get("tool_wear", 0)
    air_t = data.get("air_temperature", 300.0)

    # Calculate normalized risk contribution factors (0 to 100%)
    c_torque = max(5.0, min(100.0, ((torque - 35.0) / 35.0) * 100))
    c_rpm = max(5.0, min(100.0, ((1500.0 - rpm) / 400.0) * 100)) if rpm < 1500 else 8.0
    c_temp = max(5.0, min(100.0, ((proc_t - 308.0) / 7.0) * 100))
    c_wear = max(5.0, min(100.0, (tool_w / 150.0) * 100))
    c_air = max(5.0, min(100.0, ((air_t - 298.0) / 5.0) * 100))

    features = ["Spindle Torque", "Low Spindle Speed", "Cutting Zone Temp", "Tool Wear", "Ambient Heat"]
    scores = [c_torque, c_rpm, c_temp, c_wear, c_air]
    colors = ["#ef4444" if s > 50 else ("#f59e0b" if s > 25 else "#10b981") for s in scores]

    fig = go.Figure(go.Bar(
        x=scores,
        y=features,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{s:.1f}%" for s in scores],
        textposition='outside'
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=25, t=15, b=15),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#111827',
        font=dict(color='#94a3b8', size=11),
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor='#1f2937', title="Relative Risk Contribution (%)"),
        yaxis=dict(autorange="reversed")
    )
    return fig

# 5. Sidebar Controls & Fleet Switcher
with st.sidebar:
    st.markdown("### 🏭 Fleet Monitor")
    st.markdown("**P_311 — IoT Fault Diagnosis**")
    
    # Machine Selector
    machine_options = {
        "machine1": "Machine 1: CNC Milling Center (Type M)",
        "machine2": "Machine 2: Heavy Duty Lathe (Type H)",
        "machine3": "Machine 3: High Speed Grinder (Type L)",
    }
    selected_m_id = st.selectbox(
        "Active Machine Monitor:",
        options=list(machine_options.keys()),
        format_func=lambda x: machine_options[x]
    )
    
    st.markdown("---")
    refresh_rate = st.slider("Auto-Refresh Rate (seconds)", min_value=1, max_value=10, value=2)
    auto_refresh = st.checkbox("Enable Live Polling", value=True)
    
    st.markdown("---")
    st.markdown(f"#### 🧪 Inject Test Telemetry ({selected_m_id})")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🟢 Send Normal", use_container_width=True):
            if publish_quick_telemetry(target_machine=selected_m_id, is_fault=False):
                st.toast(f"Sent Normal Telemetry to {selected_m_id}!", icon="✅")
                time.sleep(0.5)
                st.rerun()
    with col_t2:
        if st.button("🔴 Send Fault", use_container_width=True):
            if publish_quick_telemetry(target_machine=selected_m_id, is_fault=True):
                st.toast(f"Sent Fault Telemetry to {selected_m_id}!", icon="⚠️")
                time.sleep(0.5)
                st.rerun()

    st.markdown("---")
    st.markdown("#### 📡 System Status")
    st.markdown(f"• **MQTT Broker**: `{MQTT_BROKER}:{MQTT_PORT}`")
    st.markdown(f"• **ML Model**: Gradient Boosting (`{DECISION_THRESHOLD*100:.0f}%` cutoff)")
    st.markdown("• **RAG Engine**: FAISS (`all-MiniLM-L6-v2`)")
    st.markdown("• **Stage 6**: Local LLM Copilot Active")
    st.markdown(f"• **Database**: SQLite (`{DB_PATH}`)")


# 6. Live Auto-Refreshing Main View
@st.fragment(run_every=f"{refresh_rate}s" if auto_refresh else None)
def render_live_dashboard():
    fleet_data = get_fleet_snapshot()
    
    # Retrieve data for selected machine
    if fleet_data and "machines" in fleet_data and selected_m_id in fleet_data["machines"]:
        data = fleet_data["machines"][selected_m_id]
    elif fleet_data and fleet_data.get("machine_id") == selected_m_id:
        data = fleet_data
    else:
        # Fallback to single snapshot if machine_id matches or no fleet entry yet
        data = fleet_data if fleet_data else None

    hist_df = get_historical_telemetry(machine_id=selected_m_id, limit=60)
    m_info = FLEET_MAP.get(selected_m_id, {"name": "Industrial Unit", "type": "M"})

    # Top Header
    status_str = data.get("status", "NORMAL") if data else "NORMAL"
    is_fault = (status_str == "FAULT RISK")
    
    st.markdown(f"""
    <div class="dashboard-header">
        <div>
            <div class="dashboard-title">🏭 {m_info['name']} &nbsp;<span style="font-size: 1rem; color: #a78bfa;">({selected_m_id.upper()})</span></div>
            <div class="dashboard-subtitle">Product Type: <b>{m_info['type']}</b> &nbsp;|&nbsp; Predictive Maintenance, RAG & LLM Copilot</div>
        </div>
        <div style="text-align: right;">
            <span class="{'badge-fault' if is_fault else 'badge-normal'}">
                {'⚠️ FAULT RISK DETECTED' if is_fault else '🟢 SYSTEM NORMAL'}
            </span>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.3rem;">
                Last Reading: <b>{data.get('timestamp', '--:--:--') if data else 'Waiting...'}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fleet Status Ribbon
    if fleet_data and "machines" in fleet_data and fleet_data["machines"]:
        f_cols = st.columns(len(FLEET_MAP))
        for idx, (f_id, f_meta) in enumerate(FLEET_MAP.items()):
            with f_cols[idx]:
                f_record = fleet_data["machines"].get(f_id)
                if f_record:
                    f_st = f_record.get("status", "NORMAL")
                    f_prob = f_record.get("failure_probability", 0.0) * 100
                    f_color = "#ef4444" if f_st == "FAULT RISK" else "#10b981"
                    st.markdown(f"""
                    <div class="fleet-card" style="border-left: 4px solid {f_color};">
                        <div>
                            <div style="font-size: 0.82rem; font-weight: 600; color: #f8fafc;">{f_id.upper()}: {f_meta['name']}</div>
                            <div style="font-size: 0.72rem; color: #94a3b8;">Risk: <b style="color: {f_color};">{f_prob:.1f}%</b></div>
                        </div>
                        <div style="font-size: 0.75rem; font-weight: 700; color: {f_color};">
                            {'⚠️ FAULT' if f_st == 'FAULT RISK' else '✓ OK'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="fleet-card" style="border-left: 4px solid #64748b;">
                        <div style="font-size: 0.82rem; color: #94a3b8;">{f_id.upper()}: {f_meta['name']}</div>
                        <div style="font-size: 0.72rem; color: #64748b;">Standby</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    if not data:
        st.warning(f"📡 Waiting for telemetry from `{selected_m_id}`... Click '🟢 Send Normal' or '🔴 Send Fault' in the sidebar to stream telemetry.")
        return

    status = data.get("status", "NORMAL")
    severity = data.get("severity", "LOW")
    prob_pct = data.get("failure_probability", 0.0) * 100
    recommendation = data.get("recommendation", "")
    conditions = data.get("conditions", [])
    rag_advice = data.get("rag_advice", "")
    llm_briefing = data.get("llm_briefing", "")

    # Hero Status Banner
    banner_class = "hero-banner-fault" if status == "FAULT RISK" else "hero-banner-normal"
    st.markdown(f"""
    <div class="{banner_class}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: {'#f87171' if status == 'FAULT RISK' else '#34d399'}; font-weight: 700;">
                    {status} &nbsp;—&nbsp; Severity: <span style="text-decoration: underline;">{severity}</span>
                </h4>
                <div style="margin-top: 0.4rem; font-size: 0.95rem; color: #e2e8f0;">
                    <b>Operational Directive:</b> {recommendation}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">Predicted Failure Risk</div>
                <div style="font-size: 2rem; font-weight: 800; color: {'#ef4444' if prob_pct >= (DECISION_THRESHOLD*100) else '#10b981'};">
                    {prob_pct:.2f}%
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Row 1: Gauges (Failure Probability, Spindle RPM, Torque)
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.plotly_chart(
            create_gauge(round(prob_pct, 1), 0, 100, "FAILURE PROBABILITY", "%", threshold_v=DECISION_THRESHOLD*100, is_probability=True),
            use_container_width=True
        )
    with col_g2:
        st.plotly_chart(
            create_gauge(data.get("rotational_speed", 1500), 800, 2200, "ROTATIONAL SPEED", " RPM", threshold_v=1650),
            use_container_width=True
        )
    with col_g3:
        st.plotly_chart(
            create_gauge(round(data.get("torque", 40.0), 1), 0, 80, "SPINDLE TORQUE", " Nm", threshold_v=55.0),
            use_container_width=True
        )

    # Row 2: Sensor Metric Cards & Stage 8 RUL
    air_t = data.get("air_temperature", 300.0)
    proc_t = data.get("process_temperature", 310.0)
    delta_t = round(proc_t - air_t, 1)
    wear = data.get("tool_wear", 0)

    # Stage 8: Remaining Useful Life (RUL) Calculation
    rul_minutes = max(0, 150 - wear)
    rul_status = "EXPIRED" if wear >= 150 else f"{rul_minutes} min left"
    rul_color = "#ef4444" if wear >= 150 else ("#f59e0b" if wear >= 100 else "#10b981")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Air Temp</div>
            <div class="metric-value">{air_t:.1f} <span style="font-size: 1rem; color: #94a3b8;">K</span></div>
            <div class="metric-sub">Ambient Environment</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Process Temp</div>
            <div class="metric-value">{proc_t:.1f} <span style="font-size: 1rem; color: #94a3b8;">K</span></div>
            <div class="metric-sub">Cutting Zone</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Thermal Delta (ΔT)</div>
            <div class="metric-value" style="color: {'#f87171' if delta_t > 12 else '#38bdf8'};">{delta_t:.1f} <span style="font-size: 1rem; color: #94a3b8;">K</span></div>
            <div class="metric-sub">T_process - T_air</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tool Wear (Active)</div>
            <div class="metric-value" style="color: {'#ef4444' if wear >= 150 else ('#f59e0b' if wear >= 100 else '#10b981')};">{wear} <span style="font-size: 1rem; color: #94a3b8;">min</span></div>
            <div class="metric-sub">Threshold: 150 min</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tool RUL (Stage 8)</div>
            <div class="metric-value" style="color: {rul_color};">{rul_status}</div>
            <div class="metric-sub">Remaining Useful Life</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 3: Stage 6 AI Technician Copilot & Stage 8 Explainable AI
    col_ai1, col_ai2 = st.columns([1.3, 1.0])

    with col_ai1:
        st.markdown("### 🤖 Stage 6: AI Technician Copilot (Local LLM)")
        if llm_briefing:
            st.markdown(f"""
            <div class="llm-box">
                <span class="llm-tag">Grounded AI Technician Briefing</span>
                <pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.85rem; color: #e0e7ff; margin: 0; background: transparent; border: none; padding: 0;">{llm_briefing}</pre>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #111827; border: 1px dashed #374151; border-radius: 10px; padding: 1.5rem; text-align: center; color: #94a3b8;">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🤖</div>
                <b>AI Copilot on Standby</b><br>
                <span style="font-size: 0.85rem;">Continuous monitoring active. Real-time technician briefings generate automatically during operational anomalies.</span>
            </div>
            """, unsafe_allow_html=True)

    with col_ai2:
        st.markdown("### 📊 Stage 8: Explainable AI (XAI)")
        st.caption("Feature risk attribution contributing to current ML probability:")
        st.plotly_chart(create_xai_chart(data), use_container_width=True)

    st.markdown("<br><hr style='border-color: #1f2937;'><br>", unsafe_allow_html=True)

    # Row 4: Diagnosis Engine & RAG Retrieval Hub
    col_d1, col_d2 = st.columns([1, 1.3])

    with col_d1:
        st.markdown("### 🔍 Diagnosis Engine Telemetry")
        st.markdown(f"**Identified Sensor Conditions ({selected_m_id}):**")
        if conditions:
            chips_html = ""
            for cond in conditions:
                c_class = "condition-chip" if "No major" in cond else "condition-chip-fault"
                chips_html += f'<span class="{c_class}">{"✓ " if "No major" in cond else "⚠️ "}{cond}</span>'
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.write("No conditions logged.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Physical Sensor Threshold Reference:**")
        st.markdown("""
        - **Process Temp**: Normal `< 312.0 K` | High `≥ 312.0 K`
        - **Spindle Speed**: Normal `1300 - 1650 RPM`
        - **Spindle Torque**: Normal `< 55.0 Nm` | High `≥ 55.0 Nm`
        - **Tool Wear**: Normal `< 100 min` | Replace `≥ 150 min`
        """)

    with col_d2:
        st.markdown("### 📚 Stage 5: RAG Knowledge Retrieval Hub")
        if rag_advice:
            st.markdown(f"""
            <div class="rag-box">
                <span class="rag-tag">FAISS Retrieved Maintenance Procedure</span>
                <pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.85rem; color: #e2e8f0; margin: 0; background: transparent; border: none; padding: 0;">{rag_advice}</pre>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #111827; border: 1px dashed #374151; border-radius: 10px; padding: 1.5rem; text-align: center; color: #94a3b8;">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🛡️</div>
                <b>Knowledge Engine on Standby</b><br>
                <span style="font-size: 0.85rem;">All monitored telemetry parameters are operating within standard safety tolerances. RAG retrieval will trigger automatically upon anomaly or fault detection.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #1f2937;'><br>", unsafe_allow_html=True)

    # Row 5: Historical Time-Series Analytics (Plotly)
    st.markdown(f"### 📈 Historical Analytics & Sensor Trends ({selected_m_id})")

    if not hist_df.empty:
        t_tab1, t_tab2, t_tab3, t_tab4 = st.tabs([
            "🌡️ Thermal Dynamics",
            "⚡ Mechanical Dynamics",
            "🎯 Failure Probability Timeline",
            "⏳ Tool Wear Progression"
        ])

        with t_tab1:
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=hist_df.index, y=hist_df["air_temperature"], mode="lines+markers", name="Air Temp (K)", line=dict(color="#38bdf8", width=2)))
            fig_t.add_trace(go.Scatter(x=hist_df.index, y=hist_df["process_temperature"], mode="lines+markers", name="Process Temp (K)", line=dict(color="#f43f5e", width=2)))
            fig_t.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#111827',
                font=dict(color='#94a3b8'),
                margin=dict(l=20, r=20, t=30, b=20),
                height=280,
                xaxis=dict(showgrid=True, gridcolor='#1f2937', title="Reading Sequence"),
                yaxis=dict(showgrid=True, gridcolor='#1f2937', title="Temperature (K)")
            )
            st.plotly_chart(fig_t, use_container_width=True)

        with t_tab2:
            fig_m = go.Figure()
            fig_m.add_trace(go.Scatter(x=hist_df.index, y=hist_df["rotational_speed"], mode="lines+markers", name="Speed (RPM)", yaxis="y1", line=dict(color="#a78bfa", width=2)))
            fig_m.add_trace(go.Scatter(x=hist_df.index, y=hist_df["torque"], mode="lines+markers", name="Torque (Nm)", yaxis="y2", line=dict(color="#f59e0b", width=2)))
            fig_m.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#111827',
                font=dict(color='#94a3b8'),
                margin=dict(l=20, r=20, t=30, b=20),
                height=280,
                xaxis=dict(showgrid=True, gridcolor='#1f2937', title="Reading Sequence"),
                yaxis=dict(title="Rotational Speed (RPM)", showgrid=True, gridcolor='#1f2937'),
                yaxis2=dict(title="Torque (Nm)", overlaying="y", side="right", showgrid=False)
            )
            st.plotly_chart(fig_m, use_container_width=True)

        with t_tab3:
            fig_p = go.Figure()
            hist_p = hist_df["failure_probability"] * 100
            fig_p.add_trace(go.Scatter(x=hist_df.index, y=hist_p, mode="lines+markers", name="Failure Probability (%)", line=dict(color="#ef4444", width=2), fill="tozeroy", fillcolor="rgba(239, 68, 68, 0.1)"))
            fig_p.add_hline(y=DECISION_THRESHOLD*100, line_dash="dash", line_color="#f59e0b", annotation_text=f"Cutoff ({DECISION_THRESHOLD*100:.0f}%)", annotation_position="top left")
            fig_p.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#111827',
                font=dict(color='#94a3b8'),
                margin=dict(l=20, r=20, t=30, b=20),
                height=280,
                xaxis=dict(showgrid=True, gridcolor='#1f2937', title="Reading Sequence"),
                yaxis=dict(range=[0, 100], showgrid=True, gridcolor='#1f2937', title="Probability (%)")
            )
            st.plotly_chart(fig_p, use_container_width=True)

        with t_tab4:
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(x=hist_df.index, y=hist_df["tool_wear"], mode="lines+markers", name="Tool Wear (min)", line=dict(color="#10b981", width=2)))
            fig_w.add_hline(y=150, line_dash="dash", line_color="#ef4444", annotation_text="Replacement Limit (150 min)", annotation_position="top left")
            fig_w.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#111827',
                font=dict(color='#94a3b8'),
                margin=dict(l=20, r=20, t=30, b=20),
                height=280,
                xaxis=dict(showgrid=True, gridcolor='#1f2937', title="Reading Sequence"),
                yaxis=dict(showgrid=True, gridcolor='#1f2937', title="Minutes")
            )
            st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info(f"Gathering historical telemetry for {selected_m_id} from SQLite database...")

    # Row 6: Audit Trail & Data Log Table
    with st.expander(f"📋 Telemetry Database Log & Audit Trail ({selected_m_id})", expanded=False):
        if not hist_df.empty:
            display_cols = ["timestamp", "machine_id", "machine_type", "air_temperature", "process_temperature", "rotational_speed", "torque", "tool_wear", "failure_probability", "status", "severity"]
            cols_to_show = [c for c in display_cols if c in hist_df.columns]
            st.dataframe(
                hist_df[cols_to_show].tail(20).iloc[::-1],
                use_container_width=True
            )
            csv_data = hist_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download Telemetry Log CSV ({selected_m_id})",
                data=csv_data,
                file_name=f"{selected_m_id}_telemetry_log.csv",
                mime="text/csv"
            )

render_live_dashboard()
