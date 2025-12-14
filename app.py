"""
Stats Council - Multi-LLM Statistical Analysis Suite
A comprehensive statistical analysis tool for orthopedic and medical informatics research.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from council import StatsCouncil
from execution import CodeExecutor
from writing import ResultsWriter
from prompts import PROMPTS
from journal_formats import JOURNAL_FORMATS

# Page configuration
st.set_page_config(
    page_title="Stats Council",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stage-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1E3A5F;
    }
    .stage-complete {
        border-left-color: #28a745;
        background-color: #e8f5e9;
    }
    .stage-active {
        border-left-color: #ffc107;
        background-color: #fff8e1;
    }
    .stage-pending {
        border-left-color: #6c757d;
        background-color: #f8f9fa;
    }
    .model-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .cost-tracker {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .disagreement-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'current_stage': 0,
        'data': None,
        'data_audit': None,
        'council_plans': None,
        'synthesis': None,
        'assumptions': None,
        'code': None,
        'execution_results': None,
        'adversarial_review': None,
        'results_doc': None,
        'figures': [],
        'tables': [],
        'total_cost': 0.0,
        'stage_costs': {},
        'conversation_history': [],
        'analysis_plan_approved': False,
        'assumptions_approved': False,
        'execution_approved': False,
        'review_approved': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Sidebar configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # API Keys section
    with st.expander("🔑 API Keys", expanded=False):
        openrouter_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            value=st.session_state.get('openrouter_key', ''),
            help="Get your key at openrouter.ai"
        )
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_key', ''),
            help="Required for code execution sandbox"
        )
        if openrouter_key:
            st.session_state['openrouter_key'] = openrouter_key
        if openai_key:
            st.session_state['openai_key'] = openai_key
    
    # Analysis mode
    st.markdown("### 📋 Analysis Mode")
    mode = st.selectbox(
        "Select Mode",
        ["Full Pipeline", "Quick Analysis", "Interactive Exploration", "Power Analysis"],
        help="Full Pipeline provides maximum accuracy with multi-model verification"
    )
    st.session_state['mode'] = mode
    
    # Journal format
    st.markdown("### 📰 Journal Format")
    journal = st.selectbox(
        "Target Journal",
        list(JOURNAL_FORMATS.keys()),
        help="Formatting will follow journal-specific conventions"
    )
    st.session_state['journal'] = journal
    
    # Study design (auto-detected but can override)
    st.markdown("### 🔬 Study Design")
    study_design = st.selectbox(
        "Study Design",
        ["Auto-detect", "Retrospective Cohort", "Prospective Cohort", "Case-Control", 
         "Cross-sectional", "RCT", "Case Series", "Prediction Model"],
        help="Used to apply appropriate reporting guidelines (STROBE, CONSORT, TRIPOD)"
    )
    st.session_state['study_design'] = study_design
    
    # Cost tracking
    st.markdown("### 💰 Cost Tracker")
    st.markdown(f"""
    <div class="cost-tracker">
        <strong>Total Cost:</strong> ${st.session_state['total_cost']:.2f}<br>
        <small>Target: $10-15 per run</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Stage progress
    st.markdown("### 📊 Progress")
    stages = ["Data Audit", "Planning Council", "Assumptions", "Execution", "Review", "Writing", "Complete"]
    current = st.session_state['current_stage']
    for i, stage in enumerate(stages):
        if i < current:
            st.markdown(f"✅ {stage}")
        elif i == current:
            st.markdown(f"🔄 **{stage}**")
        else:
            st.markdown(f"⬜ {stage}")
    
    # Reset button
    if st.button("🔄 Reset Analysis", type="secondary"):
        for key in list(st.session_state.keys()):
            if key not in ['openrouter_key', 'openai_key']:
                del st.session_state[key]
        init_session_state()
        st.rerun()

# Main content area
st.markdown('<p class="main-header">📊 Stats Council</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-LLM Statistical Analysis Suite for Medical Research</p>', unsafe_allow_html=True)

# Check for API keys
if not st.session_state.get('openrouter_key') or not st.session_state.get('openai_key'):
    st.warning("⚠️ Please configure your API keys in the sidebar to begin.")
    st.stop()

# Initialize council and executor
council = StatsCouncil(st.session_state['openrouter_key'])
executor = CodeExecutor(st.session_state['openai_key'])
writer = ResultsWriter(st.session_state['openrouter_key'])

# Tab navigation
tab1, tab2, tab3, tab4 = st.tabs(["📤 Input", "🔬 Analysis", "📄 Results", "📁 Downloads"])

with tab1:
    st.markdown("## Data Input")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload Your Data")
        uploaded_file = st.file_uploader(
            "Upload CSV file (deidentified)",
            type=['csv'],
            help="Ensure all PHI has been removed"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state['data'] = df
                st.success(f"✅ Loaded {len(df)} rows × {len(df.columns)} columns")
                
                with st.expander("Preview Data", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                
                with st.expander("Column Summary"):
                    col_info = pd.DataFrame({
                        'Type': df.dtypes.astype(str),
                        'Non-Null': df.notna().sum(),
                        'Null %': (df.isna().sum() / len(df) * 100).round(1)
                    })
                    st.dataframe(col_info, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with col2:
        st.markdown("### Research Context")
        
        research_question = st.text_area(
            "Research Question",
            placeholder="e.g., Does patient BMI affect 30-day complication rates after primary TKA?",
            height=100
        )
        st.session_state['research_question'] = research_question
        
        hypotheses = st.text_area(
            "Hypotheses (optional)",
            placeholder="e.g., H1: Higher BMI is associated with increased complication rates\nH0: No association between BMI and complications",
            height=100
        )
        st.session_state['hypotheses'] = hypotheses
        
        outcome_var = st.text_input(
            "Primary Outcome Variable",
            placeholder="e.g., any_complication, revision, mortality"
        )
        st.session_state['outcome_var'] = outcome_var
        
        exposure_var = st.text_input(
            "Primary Exposure/Predictor Variable",
            placeholder="e.g., bmi, surgical_approach, implant_type"
        )
        st.session_state['exposure_var'] = exposure_var
        
        covariates = st.text_input(
            "Key Covariates (comma-separated)",
            placeholder="e.g., age, sex, asa_class, diabetes"
        )
        st.session_state['covariates'] = covariates
        
        additional_context = st.text_area(
            "Additional Context",
            placeholder="Any other relevant information about the study, data source, exclusion criteria, etc.",
            height=100
        )
        st.session_state['additional_context'] = additional_context

with tab2:
    st.markdown("## Analysis Pipeline")
    
    if st.session_state['data'] is None:
        st.info("📤 Please upload your data in the Input tab to begin.")
        st.stop()
    
    # Stage 1: Data Audit
    st.markdown("---")
    stage1_status = "complete" if st.session_state['data_audit'] else ("active" if st.session_state['current_stage'] == 0 else "pending")
    st.markdown(f"""
    <div class="stage-box stage-{stage1_status}">
        <h3>Stage 1: Data Audit</h3>
        <p>Model: DeepSeek V3.2 | Est. Cost: ~$0.05</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['current_stage'] == 0:
        if st.button("🚀 Run Data Audit", type="primary"):
            with st.spinner("Analyzing your data..."):
                audit_result, cost = council.data_audit(
                    st.session_state['data'],
                    st.session_state['research_question'],
                    st.session_state.get('outcome_var', ''),
                    st.session_state.get('exposure_var', '')
                )
                st.session_state['data_audit'] = audit_result
                st.session_state['total_cost'] += cost
                st.session_state['stage_costs']['data_audit'] = cost
                st.rerun()
    
    if st.session_state['data_audit']:
        with st.expander("📋 Data Audit Results", expanded=True):
            st.markdown(st.session_state['data_audit'])
        
        if st.session_state['current_stage'] == 0:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm & Continue", type="primary"):
                    st.session_state['current_stage'] = 1
                    st.rerun()
            with col2:
                if st.button("🔄 Re-run Audit"):
                    st.session_state['data_audit'] = None
                    st.rerun()
    
    # Stage 2: Statistical Planning Council
    st.markdown("---")
    stage2_status = "complete" if st.session_state['synthesis'] else ("active" if st.session_state['current_stage'] == 1 else "pending")
    st.markdown(f"""
    <div class="stage-box stage-{stage2_status}">
        <h3>Stage 2: Statistical Planning Council</h3>
        <p>Models: DeepSeek V3.2 + DeepSeek R1 + Gemini 2.5 Pro → o3 synthesis | Est. Cost: ~$2.00</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['current_stage'] >= 1 and not st.session_state['synthesis']:
        if st.button("🧠 Convene Council", type="primary"):
            with st.spinner("Council deliberating on analysis approach..."):
                plans, synthesis, disagreements, cost = council.planning_council(
                    st.session_state['data'],
                    st.session_state['data_audit'],
                    st.session_state['research_question'],
                    st.session_state.get('hypotheses', ''),
                    st.session_state.get('outcome_var', ''),
                    st.session_state.get('exposure_var', ''),
                    st.session_state.get('covariates', ''),
                    st.session_state.get('study_design', 'Auto-detect')
                )
                st.session_state['council_plans'] = plans
                st.session_state['synthesis'] = synthesis
                st.session_state['disagreements'] = disagreements
                st.session_state['total_cost'] += cost
                st.session_state['stage_costs']['planning'] = cost
                st.rerun()
    
    if st.session_state['synthesis']:
        # Show individual council member proposals
        with st.expander("👥 Individual Council Proposals"):
            if st.session_state['council_plans']:
                for model, plan in st.session_state['council_plans'].items():
                    st.markdown(f"**{model}:**")
                    st.markdown(plan)
                    st.markdown("---")
        
        # Show disagreements if any
        if st.session_state.get('disagreements'):
            st.markdown("""
            <div class="disagreement-box">
                <h4>⚠️ Council Disagreements Detected</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state['disagreements'])
        
        # Show synthesis
        with st.expander("📋 Synthesized Analysis Plan", expanded=True):
            st.markdown(st.session_state['synthesis'])
        
        if st.session_state['current_stage'] == 1:
            st.markdown("### Approve Analysis Plan")
            user_modifications = st.text_area(
                "Add modifications or instructions (optional)",
                placeholder="e.g., Also run subgroup analysis by sex, use propensity matching instead of regression"
            )
            st.session_state['user_modifications'] = user_modifications
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Approve Plan", type="primary"):
                    st.session_state['analysis_plan_approved'] = True
                    st.session_state['current_stage'] = 2
                    st.rerun()
            with col2:
                if st.button("🔄 Re-convene Council"):
                    st.session_state['council_plans'] = None
                    st.session_state['synthesis'] = None
                    st.rerun()
            with col3:
                if st.button("✏️ Edit Plan Manually"):
                    st.session_state['manual_edit_mode'] = True
    
    # Stage 3: Assumption Verification
    st.markdown("---")
    stage3_status = "complete" if st.session_state['assumptions'] else ("active" if st.session_state['current_stage'] == 2 else "pending")
    st.markdown(f"""
    <div class="stage-box stage-{stage3_status}">
        <h3>Stage 3: Assumption Verification</h3>
        <p>Model: DeepSeek R1 | Est. Cost: ~$0.10</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['current_stage'] >= 2 and not st.session_state['assumptions']:
        if st.button("🔍 Verify Assumptions", type="primary"):
            with st.spinner("Checking statistical assumptions..."):
                assumptions, cost = council.verify_assumptions(
                    st.session_state['data'],
                    st.session_state['synthesis'],
                    st.session_state.get('user_modifications', '')
                )
                st.session_state['assumptions'] = assumptions
                st.session_state['total_cost'] += cost
                st.session_state['stage_costs']['assumptions'] = cost
                st.rerun()
    
    if st.session_state['assumptions']:
        with st.expander("📋 Assumption Verification Results", expanded=True):
            st.markdown(st.session_state['assumptions'])
        
        if st.session_state['current_stage'] == 2:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Proceed with Analysis", type="primary"):
                    st.session_state['assumptions_approved'] = True
                    st.session_state['current_stage'] = 3
                    st.rerun()
            with col2:
                if st.button("🔄 Revise Plan"):
                    st.session_state['current_stage'] = 1
                    st.session_state['synthesis'] = None
                    st.rerun()
    
    # Stage 4: Code Generation & Execution
    st.markdown("---")
    stage4_status = "complete" if st.session_state['execution_results'] else ("active" if st.session_state['current_stage'] == 3 else "pending")
    st.markdown(f"""
    <div class="stage-box stage-{stage4_status}">
        <h3>Stage 4: Code Generation & Execution</h3>
        <p>Code: o3 | Verification: DeepSeek R1 | Execution: OpenAI Sandbox | Est. Cost: ~$1.50</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['current_stage'] >= 3 and not st.session_state['execution_results']:
        if st.button("⚡ Generate & Execute Analysis", type="primary"):
            with st.spinner("Generating analysis code..."):
                # Generate code
                code, code_cost = council.generate_code(
                    st.session_state['data'],
                    st.session_state['synthesis'],
                    st.session_state['assumptions'],
                    st.session_state.get('user_modifications', ''),
                    st.session_state.get('journal', 'Generic')
                )
                st.session_state['code'] = code
                st.session_state['total_cost'] += code_cost
            
            with st.spinner("Executing analysis in sandbox..."):
                # Execute code
                results, figures, tables, exec_cost = executor.execute(
                    code,
                    st.session_state['data']
                )
                st.session_state['execution_results'] = results
                st.session_state['figures'] = figures
                st.session_state['tables'] = tables
                st.session_state['total_cost'] += exec_cost
                st.session_state['stage_costs']['execution'] = code_cost + exec_cost
                st.rerun()
    
    if st.session_state['execution_results']:
        with st.expander("💻 Generated Code", expanded=False):
            st.code(st.session_state['code'], language='python')
        
        with st.expander("📊 Execution Results", expanded=True):
            st.markdown(st.session_state['execution_results'])
        
        if st.session_state['figures']:
            with st.expander("📈 Figures", expanded=True):
                for i, fig in enumerate(st.session_state['figures']):
                    st.image(fig, caption=f"Figure {i+1}")
        
        if st.session_state['tables']:
            with st.expander("📋 Tables", expanded=True):
                for name, table in st.session_state['tables'].items():
                    st.markdown(f"**{name}**")
                    st.dataframe(table, use_container_width=True)
        
        if st.session_state['current_stage'] == 3:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Proceed to Review", type="primary"):
                    st.session_state['execution_approved'] = True
                    st.session_state['current_stage'] = 4
                    st.rerun()
            with col2:
                if st.button("🔄 Re-run Analysis"):
                    st.session_state['execution_results'] = None
                    st.session_state['code'] = None
                    st.rerun()
    
    # Stage 5: Adversarial Review
    st.markdown("---")
    stage5_status = "complete" if st.session_state['adversarial_review'] else ("active" if st.session_state['current_stage'] == 4 else "pending")
    st.markdown(f"""
    <div class="stage-box stage-{stage5_status}">
        <h3>Stage 5: Adversarial Review</h3>
        <p>Models: DeepSeek V3.2 + DeepSeek R1 | Est. Cost: ~$0.20</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['current_stage'] >= 4 and not st.session_state['adversarial_review']:
        if st.button("🔎 Run Adversarial Review", type="primary"):
            with st.spinner("Reviewing for statistical flaws..."):
                review, issues, confidence, cost = council.adversarial_review(
                    st.session_state['synthesis'],
                    st.session_state['code'],
                    st.session_state['execution_results'],
                    st.session_state['assumptions']
                )
                st.session_state['adversarial_review'] = review
                st.session_state['review_issues'] = issues
                st.session_state['confidence_score'] = confidence
                st.session_state['total_cost'] += cost
                st.session_state['stage_costs']['review'] = cost
                st.rerun()
    
    if st.session_state['adversarial_review']:
        # Confidence indicator
        conf = st.session_state.get('confidence_score', 'MEDIUM')
        conf_class = f"confidence-{conf.lower()}"
        st.markdown(f'<p class="{conf_class}">Overall Confidence: {conf}</p>', unsafe_allow_html=True)
        
        with st.expander("📋 Adversarial Review", expanded=True):
            st.markdown(st.session_state['adversarial_review'])
        
        if st.session_state.get('review_issues'):
            st.warning("⚠️ Issues identified - review carefully before proceeding")
        
        if st.session_state['current_stage'] == 4:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Accept & Generate Report", type="primary"):
                    st.session_state['review_approved'] = True
                    st.session_state['current_stage'] = 5
                    st.rerun()
            with col2:
                if st.button("🔄 Revise Analysis"):
                    st.session_state['current_stage'] = 3
                    st.session_state['execution_results'] = None
                    st.rerun()
            with col3:
                if st.button("📝 Add Notes"):
                    st.session_state['adding_notes'] = True
    
    # Stage 6: Results Writing
    st.markdown("---")
    stage6_status = "complete" if st.session_state['results_doc'] else ("active" if st.session_state['current_stage'] == 5 else "pending")
    st.markdown(f"""
    <div class="stage-box stage-{stage6_status}">
        <h3>Stage 6: Results Writing</h3>
        <p>Model: Claude Opus 4.5 | Est. Cost: ~$4-6</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['current_stage'] >= 5 and not st.session_state['results_doc']:
        if st.button("✍️ Generate Results Document", type="primary"):
            with st.spinner("Writing methods and results sections..."):
                doc_path, cost = writer.generate_results_document(
                    st.session_state['data'],
                    st.session_state['synthesis'],
                    st.session_state['execution_results'],
                    st.session_state['figures'],
                    st.session_state['tables'],
                    st.session_state['adversarial_review'],
                    st.session_state.get('journal', 'Generic'),
                    st.session_state.get('study_design', 'Auto-detect')
                )
                st.session_state['results_doc'] = doc_path
                st.session_state['total_cost'] += cost
                st.session_state['stage_costs']['writing'] = cost
                st.session_state['current_stage'] = 6
                st.rerun()
    
    if st.session_state['results_doc']:
        st.success("✅ Analysis Complete!")
        st.balloons()

with tab3:
    st.markdown("## Results Preview")
    
    if st.session_state['current_stage'] < 5:
        st.info("Complete the analysis pipeline to view results.")
    else:
        if st.session_state['execution_results']:
            st.markdown("### Statistical Results")
            st.markdown(st.session_state['execution_results'])
        
        if st.session_state['figures']:
            st.markdown("### Figures")
            cols = st.columns(min(len(st.session_state['figures']), 2))
            for i, fig in enumerate(st.session_state['figures']):
                with cols[i % 2]:
                    st.image(fig, caption=f"Figure {i+1}")
        
        if st.session_state['tables']:
            st.markdown("### Tables")
            for name, table in st.session_state['tables'].items():
                st.markdown(f"**{name}**")
                st.dataframe(table, use_container_width=True)

with tab4:
    st.markdown("## Downloads")
    
    if st.session_state['current_stage'] < 6:
        st.info("Complete the analysis to access downloads.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Documents")
            if st.session_state.get('results_doc'):
                with open(st.session_state['results_doc'], 'rb') as f:
                    st.download_button(
                        "📥 Methods & Results (Word)",
                        f,
                        file_name="methods_results.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            
            if st.session_state.get('code'):
                st.download_button(
                    "📥 Analysis Script (Python)",
                    st.session_state['code'],
                    file_name="analysis.py",
                    mime="text/plain"
                )
        
        with col2:
            st.markdown("### 📊 Data & Figures")
            if st.session_state.get('tables'):
                for name, table in st.session_state['tables'].items():
                    csv = table.to_csv(index=False)
                    st.download_button(
                        f"📥 {name} (CSV)",
                        csv,
                        file_name=f"{name.lower().replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
            
            if st.session_state.get('figures'):
                for i, fig in enumerate(st.session_state['figures']):
                    st.download_button(
                        f"📥 Figure {i+1} (PNG)",
                        fig,
                        file_name=f"figure_{i+1}.png",
                        mime="image/png"
                    )
        
        # Analysis audit trail
        st.markdown("### 📋 Audit Trail")
        audit_data = {
            'timestamp': datetime.now().isoformat(),
            'total_cost': st.session_state['total_cost'],
            'stage_costs': st.session_state['stage_costs'],
            'journal_format': st.session_state.get('journal'),
            'study_design': st.session_state.get('study_design'),
            'research_question': st.session_state.get('research_question'),
            'confidence_score': st.session_state.get('confidence_score'),
            'council_disagreements': st.session_state.get('disagreements'),
            'review_issues': st.session_state.get('review_issues')
        }
        st.download_button(
            "📥 Audit Trail (JSON)",
            json.dumps(audit_data, indent=2),
            file_name="analysis_audit.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Stats Council v1.0 | Multi-LLM Statistical Analysis Suite<br>
    Built for orthopedic and medical informatics research
</div>
""", unsafe_allow_html=True)
