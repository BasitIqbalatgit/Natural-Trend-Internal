import streamlit as st
import time
from datetime import datetime
from utils.api_calls import aggregate_all_data
from utils.langgraph_workflow import run_vetting_analysis
from utils.pdf_generator import create_pdf_report
import os

# Page Configuration
st.set_page_config(
    page_title="AI-Powered Client Vetting Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🔍 AI-Powered Client Vetting & Brand-Safety Tool</h1>', unsafe_allow_html=True)

# Sidebar Information
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Natural+Trends", use_container_width=True)
    st.markdown("### 🚀 Features")
    st.markdown("""
    - ✅ Comprehensive Web Search
    - ✅ Social Media Analysis
    - ✅ AI-Powered Risk Assessment
    - ✅ LangGraph NLP Orchestration
    - ✅ GPT-4 Turbo Integration
    - ✅ P&G Compliance Checking
    - ✅ Professional PDF Reports
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This tool automates client vetting by:
    - Searching multiple data sources
    - Analyzing company reputation
    - Detecting scandals & violations
    - Checking P&G brand safety criteria
    - Generating audit-ready reports
    """)
    
    st.markdown("---")
    st.markdown("### 📊 P&G Questions Covered")
    st.markdown("""
    1. Positive corporate reputation?
    2. Free from serious scandals?
    3. No regulatory violations?
    4. No legal violations?
    5. Executives free from misconduct?
    6. No PR risk events?
    7. Brand safety compliant?
    """)

# Main Content Area
st.markdown("### 📝 Enter Company Information")

col1, col2 = st.columns([3, 1])

with col1:
    company_name = st.text_input(
        "Company Name *",
        placeholder="e.g., Microsoft, Tesla, etc.",
        help="Enter the full legal name of the company to vet"
    )

with col2:
    st.markdown("###")
    search_depth = st.selectbox(
        "Search Depth",
        ["Standard", "Advanced", "Deep"],
        index=1
    )

# Optional Executive Names
with st.expander("🔍 Add Specific Executives to Investigate (Optional)"):
    exec_names = st.text_area(
        "Executive Names (one per line)",
        placeholder="John Doe\nJane Smith\nRobert Johnson",
        help="Add specific executive names to investigate. Leave empty to auto-detect from company data."
    )

# Action Buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    vet_button = st.button("🚀 Run Vetting Analysis", type="primary", use_container_width=True)

# Session state initialization
if 'vetting_complete' not in st.session_state:
    st.session_state.vetting_complete = False
    st.session_state.vetting_results = None
    st.session_state.company_name = None
    st.session_state.pdf_path = None

# Main Vetting Process
if vet_button:
    if not company_name:
        st.error("⚠️ Please enter a company name to proceed.")
    else:
        st.session_state.vetting_complete = False
        st.session_state.company_name = company_name
        
        # Progress Container
        progress_container = st.container()
        
        with progress_container:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"### 🔄 Vetting Analysis in Progress for: **{company_name}**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Data Collection
                status_text.text("📡 Step 1/4: Collecting data from multiple sources...")
                progress_bar.progress(10)
                time.sleep(0.5)
                
                # Collect all data
                raw_data = aggregate_all_data(company_name)
                progress_bar.progress(30)
                status_text.text("✅ Step 1/4: Data collection complete!")
                time.sleep(0.5)
                
                # Step 2: AI Analysis with LangGraph
                status_text.text("🤖 Step 2/4: Running AI-powered analysis with GPT-4...")
                progress_bar.progress(40)
                time.sleep(0.5)
                
                # Run LangGraph workflow
                vetting_results = run_vetting_analysis(company_name, raw_data)
                progress_bar.progress(70)
                status_text.text("✅ Step 2/4: AI analysis complete!")
                time.sleep(0.5)
                
                # Step 3: Generate PDF Report
                status_text.text("📄 Step 3/4: Generating professional PDF report...")
                progress_bar.progress(80)
                time.sleep(0.5)
                
                pdf_path = create_pdf_report(company_name, vetting_results)
                progress_bar.progress(90)
                status_text.text("✅ Step 3/4: PDF report generated!")
                time.sleep(0.5)
                
                # Step 4: Complete
                status_text.text("🎉 Step 4/4: Vetting analysis complete!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Store results in session state
                st.session_state.vetting_complete = True
                st.session_state.vetting_results = vetting_results
                st.session_state.pdf_path = pdf_path
                
                st.success("✅ Vetting analysis completed successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ An error occurred during vetting: {str(e)}")
                st.exception(e)

# Display Results if Available
if st.session_state.vetting_complete and st.session_state.vetting_results:
    st.markdown("---")
    st.markdown("## 📊 Vetting Results")
    
    results = st.session_state.vetting_results
    
    # Executive Summary
    st.markdown("### 📋 Executive Summary")
    final_report = results.get('final_report', {})
    
    if final_report.get('executive_summary'):
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(final_report['executive_summary'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Data Sources Analyzed", final_report.get('data_sources_checked', 0))
    with col2:
        risk_items = results.get('risk_analysis', {}).get('negative_items_found', 0)
        st.metric("Risk Items Found", risk_items)
    with col3:
        st.metric("Current Step", results.get('current_step', 'N/A'))
    
    # Detailed Sections
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Risk Analysis", "✅ P&G Questions", "📰 Data Sources", "📄 PDF Report"])
    
    with tab1:
        st.markdown("### ⚠️ Detailed Risk Analysis")
        risk_analysis = results.get('risk_analysis', {})
        if risk_analysis.get('analysis'):
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(risk_analysis['analysis'])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No detailed risk analysis available.")
    
    with tab2:
        st.markdown("### ✅ P&G Brand Safety Questions")
        pg_answers = results.get('pg_questions_answered', {})
        if pg_answers.get('answers'):
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(pg_answers['answers'])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("P&G questions not yet answered.")
    
    with tab3:
        st.markdown("### 📰 Data Sources Summary")
        raw_data = results.get('raw_data', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### General Search Results")
            general_results = raw_data.get('comprehensive_search', {}).get('general_search', [])
            st.write(f"Total: {len(general_results)} results")
            
            if general_results:
                for idx, result in enumerate(general_results[:5], 1):
                    with st.expander(f"{idx}. {result.get('title', 'N/A')[:80]}..."):
                        st.write(f"**URL:** {result.get('url', 'N/A')}")
                        st.write(f"**Content:** {result.get('content', 'N/A')[:300]}...")
        
        with col2:
            st.markdown("#### News & Media")
            news_results = raw_data.get('comprehensive_search', {}).get('news_search', [])
            st.write(f"Total: {len(news_results)} articles")
            
            if news_results:
                for idx, result in enumerate(news_results[:5], 1):
                    with st.expander(f"{idx}. {result.get('title', 'N/A')[:80]}..."):
                        st.write(f"**URL:** {result.get('url', 'N/A')}")
                        st.write(f"**Content:** {result.get('content', 'N/A')[:300]}...")
        
        st.markdown("#### Social Media Analysis")
        social_media = raw_data.get('social_media', {})
        total_social = sum(len(v) for v in social_media.values())
        st.write(f"Total social media mentions: {total_social}")
        
        if total_social > 0:
            for platform, results in social_media.items():
                if results:
                    st.write(f"**{platform.capitalize()}:** {len(results)} mentions")
    
    with tab4:
        st.markdown("### 📄 Download PDF Report")
        
        if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name=f"{st.session_state.company_name.replace(' ', '_')}_vetting_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.success(f"✅ PDF report saved to: `{st.session_state.pdf_path}`")
        else:
            st.warning("PDF report not available.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Natural Trends AI Client Vetting System</strong></p>
    <p>Powered by GPT-4 Turbo, LangGraph, and Tavily Search</p>
    <p><em>Version 2.0 - Enhanced with Advanced AI & Multi-Source Intelligence</em></p>
</div>
""", unsafe_allow_html=True)
