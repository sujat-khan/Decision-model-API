"""Streamlit UI Playground for OpenRouter System One Decision Models."""
import json
import streamlit as st
from typing import Dict, Any, Union

from src.config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL_ID,
    OPENROUTER_SYSTEMONE_URL,
    get_api_key,
)
from src.schemas import SystemOneRequest
from src.client import DecisionClient, DecisionAPIError, AuthenticationError
from src.presets import PRESETS
from src.visualizer import (
    create_noul_gauge,
    create_choice_barchart,
    create_score_distribution_chart,
)

# Page configuration
st.set_page_config(
    page_title="Decision Models Playground | OpenRouter System One",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .model-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .card-metric {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for scenario
if "current_preset_key" not in st.session_state:
    st.session_state.current_preset_key = "agent_guardrail"
if "state_input" not in st.session_state:
    preset = PRESETS["agent_guardrail"]
    st.session_state.state_input = (
        preset["state"]
        if isinstance(preset["state"], str)
        else json.dumps(preset["state"], indent=2)
    )
if "questions_input" not in st.session_state:
    st.session_state.questions_input = PRESETS["agent_guardrail"]["questions"]
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# Sanitize session questions to remove any invalid null criteria
if isinstance(st.session_state.get("questions_input"), dict):
    for q in st.session_state.questions_input.values():
        if isinstance(q, dict) and q.get("criteria") is None:
            q.pop("criteria", None)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚡ System One Engine")
    st.caption("Structured Decision Models via OpenRouter")

    # API Key Handling
    env_key = get_api_key()
    api_key_input = st.text_input(
        "OpenRouter API Key",
        value=env_key,
        type="password",
        help="Reads from OPENROUTER_API_KEY in .env by default.",
    )
    if not api_key_input:
        st.warning("⚠️ Enter OpenRouter API Key to execute requests.")
    else:
        st.success("API Key detected")

    st.markdown("---")

    # Model Selection
    model_ids = [m["id"] for m in AVAILABLE_MODELS] + ["Custom Model ID"]
    selected_model_idx = 0
    if DEFAULT_MODEL_ID in model_ids:
        selected_model_idx = model_ids.index(DEFAULT_MODEL_ID)

    selected_model_choice = st.selectbox(
        "Decision Model",
        options=model_ids,
        index=selected_model_idx,
        help="Select standard System One decision model or provide custom slug.",
    )

    if selected_model_choice == "Custom Model ID":
        active_model_id = st.text_input(
            "Custom Model Slug",
            value="inception/mercury-decide:free",
            help="e.g. inception/mercury-decide:free",
        )
        active_model_meta = {
            "name": "Custom Model",
            "provider": "Custom",
            "badge": "Custom",
            "speed": "N/A",
            "context": "N/A",
            "description": "User-specified OpenRouter System One model.",
        }
    else:
        active_model_id = selected_model_choice
        active_model_meta = next(
            m for m in AVAILABLE_MODELS if m["id"] == selected_model_choice
        )

    # Model Info Card
    with st.expander("ℹ️ Model Specs", expanded=False):
        st.markdown(f"**Name:** {active_model_meta['name']}")
        st.markdown(f"**Provider:** {active_model_meta['provider']}")
        st.markdown(f"**Tier:** `{active_model_meta['badge']}`")
        st.markdown(f"**Context:** {active_model_meta.get('context', 'N/A')}")
        st.markdown(f"**Speed:** {active_model_meta.get('speed', 'N/A')}")
        st.caption(active_model_meta.get("description", ""))

    st.markdown("---")

    # Preset Loader
    st.markdown("### 📋 Test Scenarios")
    preset_keys = list(PRESETS.keys())
    preset_labels = [PRESETS[k]["title"] for k in preset_keys]
    selected_preset_label = st.selectbox(
        "Load Preset Scenario",
        options=preset_labels,
        index=0,
    )
    selected_preset_key = preset_keys[preset_labels.index(selected_preset_label)]

    if st.button("📥 Apply Preset", use_container_width=True):
        preset_data = PRESETS[selected_preset_key]
        st.session_state.current_preset_key = selected_preset_key
        st.session_state.state_input = (
            preset_data["state"]
            if isinstance(preset_data["state"], str)
            else json.dumps(preset_data["state"], indent=2)
        )
        st.session_state.questions_input = preset_data["questions"]
        st.session_state.last_response = None
        st.rerun()

    st.markdown("---")

    # Confidence Threshold & Escalation Simulator Settings
    st.markdown("### 🎯 Decision Policy Gate")
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.50,
        max_value=0.99,
        value=0.70,
        step=0.05,
        help="Decisions with confidence below this threshold will be flagged for human escalation.",
    )
    st.caption("Decisions below threshold trigger human oversight.")


# ================= MAIN AREA =================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-title">Decision Models Playground</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-title">Evaluating state and calibrated probabilities with <span class="model-badge">{active_model_id}</span></div>',
        unsafe_allow_html=True,
    )

with col_status:
    st.markdown(
        f"""
        <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; font-size: 0.85rem;">
            <div><b>Endpoint:</b> <code>/v1/systemone</code></div>
            <div><b>Output Tokens:</b> <span style="color:#10b981">Free (Logits)</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Input Tabs: Form Builder vs Raw JSON
tab_form, tab_json = st.tabs(["📝 Form Builder Mode", "🔧 Raw JSON Schema Mode"])

with tab_form:
    st.markdown("#### 1. Input State")
    state_input_area = st.text_area(
        "State (Context, Ticket, Agent Tool Call, or JSON Object)",
        value=st.session_state.state_input,
        height=140,
        help="The state to be evaluated by the model. Can be plain text or JSON string.",
        key="form_state_area",
    )

    st.markdown("#### 2. Typed Questions")
    st.caption("Questions to evaluate against the state. Supported types: `noul` (Boolean), `choice` (Multi-class), `score` (Ordinal scale).")

    # Render questions in editable view or summary
    questions_dict = st.session_state.questions_input
    for q_id, q_cfg in list(questions_dict.items()):
        q_type = q_cfg.get("type", "noul")
        with st.container():
            col_qhead, col_qdel = st.columns([5, 1])
            with col_qhead:
                st.markdown(f"**Question ID:** `{q_id}` &nbsp; | &nbsp; Type: `{q_type.upper()}`")
            with col_qdel:
                if st.button("🗑️ Remove", key=f"del_{q_id}"):
                    del questions_dict[q_id]
                    st.session_state.questions_input = questions_dict
                    st.rerun()

            st.text_input(
                "Instructions / Prompt",
                value=q_cfg.get("instructions", ""),
                key=f"inst_{q_id}",
                disabled=True,
            )

            # Display criteria breakdown
            if q_type == "noul":
                crit = q_cfg.get("criteria", {})
                if crit:
                    st.caption(f"**True:** {crit.get('true', 'N/A')} | **False:** {crit.get('false', 'N/A')}")
            elif q_type == "choice":
                crit = q_cfg.get("criteria", {})
                st.caption(f"**Options:** {', '.join([f'`{k}`: {v}' for k, v in crit.items()])}")
            elif q_type == "score":
                crit_list = q_cfg.get("criteria", [])
                st.caption(f"**Scale (0-{len(crit_list)-1}):** {' → '.join(crit_list)}")

            st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'/>", unsafe_allow_html=True)

    # Add New Question expander
    with st.expander("➕ Add Another Question", expanded=False):
        new_col1, new_col2 = st.columns([2, 1])
        with new_col1:
            new_qid = st.text_input("New Question ID (e.g. is_safe)", key="new_qid")
        with new_col2:
            new_qtype = st.selectbox("Type", ["noul", "choice", "score"], key="new_qtype")

        new_qinst = st.text_input("Instructions / Question Prompt", key="new_qinst")

        if new_qtype == "noul":
            col_t, col_f = st.columns(2)
            with col_t:
                crit_t = st.text_input("Condition for True", key="crit_t")
            with col_f:
                crit_f = st.text_input("Condition for False", key="crit_f")
            if st.button("Add Noul Question"):
                if new_qid and new_qinst:
                    new_q = {
                        "type": "noul",
                        "instructions": new_qinst,
                    }
                    if crit_t or crit_f:
                        new_q["criteria"] = {
                            "true": crit_t or "Yes / Condition holds",
                            "false": crit_f or "No / Condition does not hold",
                        }
                    questions_dict[new_qid] = new_q
                    st.session_state.questions_input = questions_dict
                    st.rerun()

        elif new_qtype == "choice":
            st.caption("Provide options as comma-separated keys (e.g. `opt_a, opt_b`)")
            raw_keys = st.text_input("Choice Keys", "billing, technical, sales", key="new_choice_keys")
            if st.button("Add Choice Question"):
                if new_qid and new_qinst:
                    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
                    questions_dict[new_qid] = {
                        "type": "choice",
                        "instructions": new_qinst,
                        "criteria": {k: f"Category {k}" for k in keys},
                    }
                    st.session_state.questions_input = questions_dict
                    st.rerun()

        elif new_qtype == "score":
            st.caption("Provide comma-separated scale criteria from 0 to N (e.g. `Low, Medium, High`)")
            raw_scale = st.text_input("Scale Buckets", "Low priority, Medium priority, High priority", key="new_scale")
            if st.button("Add Score Question"):
                if new_qid and new_qinst:
                    buckets = [b.strip() for b in raw_scale.split(",") if b.strip()]
                    questions_dict[new_qid] = {
                        "type": "score",
                        "instructions": new_qinst,
                        "criteria": buckets,
                    }
                    st.session_state.questions_input = questions_dict
                    st.rerun()

with tab_json:
    st.markdown("#### Complete JSON Payload Inspector / Editor")
    # Try parsing state if it is JSON
    state_parsed: Union[str, Dict[str, Any]] = state_input_area
    try:
        if state_input_area.strip().startswith("{") and state_input_area.strip().endswith("}"):
            state_parsed = json.loads(state_input_area)
    except Exception:
        state_parsed = state_input_area

    full_payload = {
        "model": active_model_id,
        "state": state_parsed,
        "questions": st.session_state.questions_input,
    }

    json_text = st.text_area(
        "Edit Raw JSON Request",
        value=json.dumps(full_payload, indent=2),
        height=320,
        key="raw_json_editor",
    )
    if st.button("Sync from Raw JSON to Form"):
        try:
            parsed = json.loads(json_text)
            st.session_state.state_input = (
                parsed["state"]
                if isinstance(parsed["state"], str)
                else json.dumps(parsed["state"], indent=2)
            )
            st.session_state.questions_input = parsed.get("questions", {})
            st.success("Synchronized JSON into Form Builder successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

# ================= EXECUTION =================
st.markdown("---")
btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    execute_button = st.button("⚡ Evaluate Decision Model", type="primary", use_container_width=True)
with btn_col2:
    if st.button("🔄 Reset / Clear Output", use_container_width=True):
        st.session_state.last_response = None
        st.rerun()

if execute_button:
    if not api_key_input:
        st.error("Please enter your OpenRouter API Key in the sidebar.")
    else:
        # Prepare state
        st.session_state.state_input = state_input_area
        final_state: Union[str, Dict[str, Any]] = state_input_area
        try:
            if state_input_area.strip().startswith("{") and state_input_area.strip().endswith("}"):
                final_state = json.loads(state_input_area)
        except Exception:
            final_state = state_input_area

        client = DecisionClient(api_key=api_key_input)
        with st.spinner(f"Evaluating {len(st.session_state.questions_input)} decision questions with {active_model_id}..."):
            try:
                response = client.evaluate(
                    model=active_model_id,
                    state=final_state,
                    questions=st.session_state.questions_input,
                )
                st.session_state.last_response = response
                st.success("Decision evaluated successfully!")
            except AuthenticationError as e:
                st.error(f"Authentication Error: {e}")
            except DecisionAPIError as e:
                st.error(f"Decision API Error: {e}")
            except Exception as e:
                st.error(f"Unexpected Error: {e}")

# ================= RESULTS & VISUALIZATIONS =================
if st.session_state.last_response:
    resp = st.session_state.last_response
    answers = resp.answers

    st.markdown("### 📊 Decision Intelligence Results")

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Questions", len(answers))
    with m2:
        st.metric("Latency", f"{resp.latency_ms} ms")
    with m3:
        st.metric("Input Tokens", resp.usage.input_tokens if resp.usage else "N/A")
    with m4:
        st.metric("Output Tokens", resp.usage.output_tokens if resp.usage else "0 (Free)")
    with m5:
        st.metric("Model Used", resp.model.split("/")[-1] if resp.model else active_model_id)

    # Decision Policy / Escalation Banner
    escalation_needed = False
    escalation_reasons = []

    for q_id, ans in answers.items():
        ans_type = ans.get("type", "")
        conf = ans.get("confidence")
        if conf is not None and conf < confidence_threshold:
            escalation_needed = True
            escalation_reasons.append(f"Question `{q_id}` confidence ({conf:.2%}) is below threshold ({confidence_threshold:.0%})")
        elif ans_type == "noul":
            prob = ans.get("noul", 0.5)
            # If near uncertain (40% to 60%)
            if 0.40 <= prob <= 0.60:
                escalation_reasons.append(f"Question `{q_id}` probability ({prob:.2%}) is in the uncertain range (40%-60%)")

    if escalation_needed:
        st.warning(
            f"⚠️ **Escalation Policy Triggered:** Human verification or fallback model recommended.\n\n"
            + "\n".join([f"- {r}" for r in escalation_reasons])
        )
    else:
        st.success(
            f"✅ **Automated Policy Clear:** All evaluated decisions meet or exceed confidence threshold ({confidence_threshold:.0%}). Autonomous agent action approved."
        )

    # Detailed Question Results
    st.markdown("#### Detailed Question Breakdown")
    for q_id, ans in answers.items():
        q_cfg = st.session_state.questions_input.get(q_id, {})
        ans_type = ans.get("type", "")

        with st.expander(f"Question: **{q_id}** ({ans_type.upper()})", expanded=True):
            col_info, col_viz = st.columns([1, 1])

            with col_info:
                st.markdown(f"**Instructions:** {q_cfg.get('instructions', 'N/A')}")
                if ans_type == "noul":
                    prob = ans.get("noul", 0.0)
                    prob_pct = round(prob * 100, 1)
                    verdict = "TRUE (YES)" if prob >= 0.5 else "FALSE (NO)"
                    badge_color = "#10b981" if prob >= 0.7 else ("#ef4444" if prob <= 0.3 else "#f59e0b")

                    st.markdown(
                        f"""
                        <div style="margin-top: 15px; padding: 15px; border-radius: 8px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155;">
                            <div style="font-size: 0.9rem; color: #94a3b8;">Binary Decision Verdict</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: {badge_color};">{verdict}</div>
                            <div style="font-size: 1.1rem; color: #f8fafc; margin-top: 5px;">Calibrated Probability: <b>{prob_pct}%</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                elif ans_type == "choice":
                    choice = ans.get("choice", "N/A")
                    conf = ans.get("confidence", 0.0)
                    st.markdown(
                        f"""
                        <div style="margin-top: 15px; padding: 15px; border-radius: 8px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155;">
                            <div style="font-size: 0.9rem; color: #94a3b8;">Selected Choice</div>
                            <div style="font-size: 1.6rem; font-weight: 700; color: #38bdf8;"><code>{choice}</code></div>
                            <div style="font-size: 1.0rem; color: #cbd5e1; margin-top: 5px;">Model Confidence: <b>{conf:.1%}</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                elif ans_type == "score":
                    score = ans.get("score", 0.0)
                    conf = ans.get("confidence", 0.0)
                    st.markdown(
                        f"""
                        <div style="margin-top: 15px; padding: 15px; border-radius: 8px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155;">
                            <div style="font-size: 0.9rem; color: #94a3b8;">Weighted Rubric Score</div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: #c084fc;">{score:.2f}</div>
                            <div style="font-size: 1.0rem; color: #cbd5e1; margin-top: 5px;">Certainty / Confidence: <b>{conf:.1%}</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with col_viz:
                if ans_type == "noul":
                    prob = ans.get("noul", 0.0)
                    fig = create_noul_gauge(prob, title=f"{q_id} (Yes/True Probability)")
                    st.plotly_chart(fig, use_container_width=True)

                elif ans_type == "choice":
                    probs = ans.get("probabilities", {})
                    choice = ans.get("choice", "")
                    if probs:
                        fig = create_choice_barchart(probs, choice, title=f"Distribution for {q_id}")
                        st.plotly_chart(fig, use_container_width=True)

                elif ans_type == "score":
                    score = ans.get("score", 0.0)
                    probs = ans.get("probabilities")
                    legend = ans.get("legend") or {
                        str(i): c for i, c in enumerate(q_cfg.get("criteria", []))
                    }
                    fig = create_score_distribution_chart(
                        score, probs, legend, title=f"Rubric Breakdown for {q_id}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # Raw API JSON collapsible inspector
    with st.expander("🔍 Raw OpenRouter API Response Inspector", expanded=False):
        st.json(resp.raw or {})
