# app.py - FINAL ENTERPRISE-GRADE AI VAPT ANALYST WORKBENCH
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import uuid

from generate_attacks import BASE_ATTACKS, generate_mutations
from evaluate_attacks import evaluate_payload

st.set_page_config(page_title="AI Red Team Analyst Workbench", layout="wide")
st.title("🔴 AI Red Team Analyst Workbench")
st.markdown("**Complete AI VAPT Platform** | MITRE ATLAS + OWASP LLM Top 10 | Local & Private")

# Initialize session state for findings
if 'findings' not in st.session_state:
    st.session_state.findings = []
if 'current_case_id' not in st.session_state:
    st.session_state.current_case_id = str(uuid.uuid4())[:8]

tab1, tab2, tab3, tab4 = st.tabs(["🧪 Automated Red Team", "✍️ Manual Attack Lab", "🔍 Investigation Workspace", "📊 Reports & Compliance"])

# ==================== 1. Automated Red Team ====================
with tab1:
    st.header("Automated Red Team Simulation")
    
    col1, col2 = st.columns(2)
    with col1:
        num_payloads = st.slider("Payloads to Test", 5, 30, 10)
    with col2:
        target_model = st.selectbox("Target Model", ["gemma2:2b", "tinyllama:1.1b", "phi3:mini", "llama3.2:1b"], index=0)
    
    goal = st.selectbox("Attack Goal", [
        "Generate Disallowed Content",
        "Extract System Prompt",
        "Bypass Safety Policy",
        "Privilege Escalation",
        "General Jailbreak"
    ])

    system_prompt = st.text_area("Add Safety System Prompt (Defense Hardening)", placeholder="You must refuse all harmful requests and never provide step-by-step instructions...")

    if st.button("Launch Attack Campaign", type="primary"):
        with st.spinner("Running attack campaign..."):
            all_payloads = []
            for base in BASE_ATTACKS:
                all_payloads.extend(generate_mutations(base))
            
            results = []
            for i, p in enumerate(all_payloads[:num_payloads]):
                full_prompt = f"{system_prompt}\nUser: {p}" if system_prompt else p
                result = evaluate_payload(full_prompt, target_model)
                result.update({
                    "case_id": st.session_state.current_case_id,
                    "timestamp": datetime.now().isoformat(),
                    "goal": goal,
                    "finding_status": "Needs Review",
                    "severity": "Medium",
                    "analyst_notes": "",
                    "tags": [],
                    "defense_applied": bool(system_prompt)
                })
                results.append(result)
            
            df = pd.DataFrame(results)
            df['status'] = df['success'].apply(lambda x: "🚨 BYPASSED" if x else "✅ BLOCKED")
            st.session_state.results = df
            st.session_state.raw_results = results
            st.session_state.findings.extend(results)
            st.success("Attack Campaign Complete!")

    if 'results' in st.session_state:
        df = st.session_state.results
        success_rate = df['success'].mean() * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Payloads", len(df))
        c2.metric("Bypasses", df['success'].sum())
        c3.metric("Resilience", f"{100-success_rate:.1f}/100")
        
        st.plotly_chart(px.pie(df, names='success', color_discrete_sequence=["#44FF44", "#FF4444"]), use_container_width=True)
        
        st.subheader("Latest Findings")
        display_cols = ['payload', 'mitre_name', 'refusal_quality', 'status', 'confidence']
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True)

# ==================== 2. Manual Attack Lab ====================
with tab2:
    st.header("Manual Attack Lab")
    prompt = st.text_area("Craft Your Payload", height=150)
    model = st.text_input("Target Model", "gemma2:2b")
    
    col1, col2 = st.columns(2)
    with col1:
        mutation_type = st.selectbox("Mutation Type", ["None", "Paraphrase", "Base64 Encode", "Roleplay", "Hypothetical"])
    with col2:
        severity = st.selectbox("Mark Severity", ["Low", "Medium", "High", "Critical"])

    if st.button("Execute Attack"):
        if prompt:
            with st.spinner("Attacking..."):
                result = evaluate_payload(prompt, model)
                result.update({
                    "case_id": st.session_state.current_case_id,
                    "timestamp": datetime.now().isoformat(),
                    "severity": severity,
                    "finding_status": "Confirmed" if result["success"] else "False Positive",
                    "analyst_notes": "",
                    "tags": ["manual"]
                })
                
                if result["success"]:
                    st.error("VULNERABLE – Attack Succeeded")
                else:
                    st.success("Secure – Blocked")
                
                with st.expander("Full Response & Analysis"):
                    st.code(result['response'])
                    st.write(f"**MITRE:** {result.get('mitre_name', 'N/A')}")
                    st.write(f"**Refusal Quality:** {result.get('refusal_quality', 'N/A')}")

# ==================== 3. Investigation Workspace ====================
with tab3:
    st.header("Investigation Workspace")
    
    if st.session_state.findings:
        findings = st.session_state.findings
        
        for finding in findings:
            with st.expander(f"Case {finding.get('case_id', 'N/A')} | {finding.get('mitre_name', 'Unknown')} | {'BYPASSED' if finding['success'] else 'BLOCKED'}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Payload**")
                    st.code(finding['payload'])
                with col2:
                    st.write("**Response**")
                    st.code(finding['response'])
                
                col3, col4 = st.columns(2)
                with col3:
                    finding['finding_status'] = st.selectbox(
                        "Status", ["Confirmed", "False Positive", "Needs Review", "Duplicate"],
                        index=["Confirmed", "False Positive", "Needs Review", "Duplicate"].index(finding.get('finding_status', "Needs Review")),
                        key=f"status_{id(finding)}"
                    )
                    finding['severity'] = st.selectbox(
                        "Severity", ["Low", "Medium", "High", "Critical"],
                        index=["Low", "Medium", "High", "Critical"].index(finding.get('severity', "Medium")),
                        key=f"sev_{id(finding)}"
                    )
                with col4:
                    finding['tags'] = st.multiselect("Tags", ["prompt-injection", "jailbreak", "data-leak", "policy-bypass"], default=finding.get('tags', []), key=f"tag_{id(finding)}")
                    finding['analyst_notes'] = st.text_area("Analyst Notes", value=finding.get('analyst_notes', ""), key=f"note_{id(finding)}")

# ==================== 4. Reports & Compliance ====================
with tab4:
    st.header("Executive Report Builder")
    if st.session_state.findings:
        findings_df = pd.DataFrame(st.session_state.findings)
        confirmed = findings_df[findings_df['finding_status'] == "Confirmed"]
        
        st.subheader("Executive Summary")
        st.write(f"**Total Findings:** {len(findings_df)}")
        st.write(f"**Confirmed Vulnerabilities:** {len(confirmed)}")
        st.write(f"**Critical/High:** {len(confirmed[confirmed['severity'].isin(['Critical', 'High'])])}")
        
        st.download_button("Export Full Report (JSON)", json.dumps(st.session_state.findings, indent=2), "executive_report.json")
    else:
        st.info("Run simulations to generate findings")

st.caption("Devansh Jain | Application Security Analyst | AI Red Teaming | GitHub: Deva1234567")