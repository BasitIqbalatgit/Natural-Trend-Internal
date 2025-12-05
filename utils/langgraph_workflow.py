import os
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client directly
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_gpt4(system_message: str, user_message: str) -> str:
    """Helper function to call GPT-4"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling GPT-4: {str(e)}")
        return f"Error: {str(e)}"

class VettingState(TypedDict):
    """State for the vetting workflow"""
    company_name: str
    raw_data: Dict[str, Any]
    extracted_entities: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    pg_questions_answered: Dict[str, str]
    final_report: Dict[str, Any]
    current_step: str

# P&G Vetting Questions
PG_VETTING_QUESTIONS = {
    "q1": "Does the company have a positive corporate reputation?",
    "q2": "Is the company free from current and serious public scandals?",
    "q3": "Is the company free from current and serious regulatory violations?",
    "q4": "Is the company free from current and serious legal violations?",
    "q5": "Are the company's principals/executives free from serious misconduct?",
    "q6": "Is there no negative media event likely to cause a PR 'black eye'?",
    "q7": "Does the company comply with brand safety standards?"
}

def extract_entities_node(state: VettingState) -> VettingState:
    """
    Extract key entities (executives, incidents, dates) from raw data
    """
    print("🔍 Extracting entities from raw data...")
    
    raw_data = state["raw_data"]
    
    # Prepare data for LLM analysis
    data_summary = f"""
    Company: {state['company_name']}
    
    General Search Results: {len(raw_data.get('comprehensive_search', {}).get('general_search', []))} results
    News Articles: {len(raw_data.get('comprehensive_search', {}).get('news_search', []))} articles
    Legal/Regulatory Info: {len(raw_data.get('comprehensive_search', {}).get('legal_regulatory', []))} items
    Recent News: {len(raw_data.get('recent_news', []))} recent articles
    Social Media: {sum(len(v) for v in raw_data.get('social_media', {}).values())} mentions
    """
    
    # Extract sample content for analysis
    all_content = []
    for result in raw_data.get('comprehensive_search', {}).get('general_search', [])[:5]:
        all_content.append(f"Title: {result.get('title', '')}\nContent: {result.get('content', '')}")
    
    for result in raw_data.get('comprehensive_search', {}).get('news_search', [])[:5]:
        all_content.append(f"News: {result.get('title', '')}\nContent: {result.get('content', '')}")
    
    content_text = "\n\n---\n\n".join(all_content[:10])  # Limit to prevent token overflow
    
    extraction_prompt = f"""
    Analyze the following information about {state['company_name']} and extract:
    
    1. Key executives and their roles
    2. Any incidents, scandals, or controversies mentioned
    3. Legal or regulatory issues
    4. Timeframes for any negative events
    5. Overall reputation indicators
    
    Data Summary:
    {data_summary}
    
    Sample Content:
    {content_text}
    
    Provide a structured JSON response with these categories.
    """
    
    try:
        response = call_gpt4(
            "You are an expert at entity extraction and corporate intelligence analysis.",
            extraction_prompt
        )
        
        state["extracted_entities"] = {
            "raw_analysis": response,
            "data_points": len(all_content),
            "processed": True
        }
    except Exception as e:
        print(f"Error in entity extraction: {str(e)}")
        state["extracted_entities"] = {"error": str(e), "processed": False}
    
    state["current_step"] = "entities_extracted"
    return state

def analyze_risks_node(state: VettingState) -> VettingState:
    """
    Analyze risks using GPT-4 with sophisticated prompting
    """
    print("⚠️  Analyzing risks with GPT-4...")
    
    raw_data = state["raw_data"]
    
    # Compile all negative indicators
    negative_content = []
    
    # News scandals
    for item in raw_data.get('comprehensive_search', {}).get('news_search', []):
        if any(keyword in item.get('content', '').lower() for keyword in 
               ['scandal', 'lawsuit', 'fraud', 'violation', 'controversy', 'investigation']):
            negative_content.append(f"NEWS: {item.get('title', '')} - {item.get('content', '')[:200]}")
    
    # Legal/regulatory
    for item in raw_data.get('comprehensive_search', {}).get('legal_regulatory', []):
        negative_content.append(f"LEGAL: {item.get('title', '')} - {item.get('content', '')[:200]}")
    
    negative_text = "\n\n".join(negative_content[:15])
    
    risk_analysis_prompt = f"""
    You are a corporate risk assessment expert for P&G brand safety compliance.
    
    Analyze the following information about {state['company_name']} and assess:
    
    1. SEVERITY: How serious are any negative findings? (Critical/High/Medium/Low/None)
    2. RECENCY: Are issues current (last 12 months) or historical?
    3. CREDIBILITY: Are sources credible and verified?
    4. PATTERN: Is there a pattern of misconduct or isolated incidents?
    5. IMPACT: Could this cause a PR "black eye" for P&G?
    
    Negative Indicators Found:
    {negative_text if negative_text else "No significant negative indicators found"}
    
    Provide a detailed risk assessment with specific evidence and reasoning.
    """
    
    try:
        response = call_gpt4(
            "You are an expert corporate risk analyst specializing in brand safety and reputation management.",
            risk_analysis_prompt
        )
        
        state["risk_analysis"] = {
            "analysis": response,
            "negative_items_found": len(negative_content),
            "processed": True
        }
    except Exception as e:
        print(f"Error in risk analysis: {str(e)}")
        state["risk_analysis"] = {"error": str(e), "processed": False}
    
    state["current_step"] = "risks_analyzed"
    return state

def answer_pg_questions_node(state: VettingState) -> VettingState:
    """
    Answer P&G's specific vetting questions using AI reasoning
    """
    print("📋 Answering P&G vetting questions...")
    
    risk_analysis = state["risk_analysis"].get("analysis", "No analysis available")
    
    questions_prompt = f"""
    Based on your risk analysis of {state['company_name']}, answer these P&G brand safety questions.
    
    For EACH question, provide:
    - Answer: YES / NO / MAYBE
    - Confidence: High / Medium / Low
    - Reasoning: 2-3 sentence explanation with specific evidence
    
    Risk Analysis Summary:
    {risk_analysis}
    
    Questions:
    1. Does the company have a positive corporate reputation?
    2. Is the company free from current and serious public scandals?
    3. Is the company free from current and serious regulatory violations?
    4. Is the company free from current and serious legal violations?
    5. Are the company's principals/executives free from serious misconduct?
    6. Is there no negative media event likely to cause a PR 'black eye'?
    7. Does the company comply with brand safety standards?
    
    Provide structured answers in JSON format.
    """
    
    try:
        response = call_gpt4(
            "You are a P&G brand safety compliance officer making critical vetting decisions.",
            questions_prompt
        )
        
        state["pg_questions_answered"] = {
            "answers": response,
            "processed": True
        }
    except Exception as e:
        print(f"Error answering P&G questions: {str(e)}")
        state["pg_questions_answered"] = {"error": str(e), "processed": False}
    
    state["current_step"] = "questions_answered"
    return state

def generate_report_node(state: VettingState) -> VettingState:
    """
    Generate final comprehensive report
    """
    print("📄 Generating final report...")
    
    report_prompt = f"""
    Create a comprehensive executive summary for {state['company_name']} vetting report.
    
    Include:
    1. Overall Recommendation (APPROVED / REJECTED / REQUIRES REVIEW)
    2. Key Findings (3-5 bullet points)
    3. Risk Level (Low / Medium / High / Critical)
    4. Action Items (if any)
    
    Based on:
    - Risk Analysis: {state['risk_analysis'].get('analysis', 'N/A')[:500]}
    - P&G Questions: {state['pg_questions_answered'].get('answers', 'N/A')[:500]}
    
    Be concise, professional, and actionable.
    """
    
    try:
        response = call_gpt4(
            "You are a senior compliance officer creating executive-level reports.",
            report_prompt
        )
        
        state["final_report"] = {
            "executive_summary": response,
            "company_name": state["company_name"],
            "data_sources_checked": sum([
                len(state["raw_data"].get('comprehensive_search', {}).get('general_search', [])),
                len(state["raw_data"].get('comprehensive_search', {}).get('news_search', [])),
                len(state["raw_data"].get('recent_news', [])),
            ]),
            "processed": True
        }
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        state["final_report"] = {"error": str(e), "processed": False}
    
    state["current_step"] = "report_generated"
    return state

def create_vetting_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for company vetting
    """
    workflow = StateGraph(VettingState)
    
    # Add nodes
    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("analyze_risks", analyze_risks_node)
    workflow.add_node("answer_questions", answer_pg_questions_node)
    workflow.add_node("generate_report", generate_report_node)
    
    # Define edges (workflow flow)
    workflow.set_entry_point("extract_entities")
    workflow.add_edge("extract_entities", "analyze_risks")
    workflow.add_edge("analyze_risks", "answer_questions")
    workflow.add_edge("answer_questions", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()

def run_vetting_analysis(company_name: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the complete vetting workflow
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting AI-Powered Vetting for: {company_name}")
    print(f"{'='*60}\n")
    
    # Initialize state
    initial_state = VettingState(
        company_name=company_name,
        raw_data=raw_data,
        extracted_entities={},
        risk_analysis={},
        pg_questions_answered={},
        final_report={},
        current_step="initialized"
    )
    
    # Create and run workflow
    workflow = create_vetting_workflow()
    
    try:
        final_state = workflow.invoke(initial_state)
        print(f"\n{'='*60}")
        print("✅ Vetting Analysis Complete!")
        print(f"{'='*60}\n")
        return final_state
    except Exception as e:
        print(f"❌ Error in workflow execution: {str(e)}")
        return initial_state
