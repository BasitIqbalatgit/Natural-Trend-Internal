"""
Input validation and early checks to prevent wasting API tokens
"""
import os
import re
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Common personal name indicators
PERSONAL_NAME_PATTERNS = [
    r'\b(mr|mrs|ms|miss|dr|prof)\b',  # Titles
    r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # FirstName LastName pattern
    r'^[A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+$',  # FirstName M. LastName
]

# Company name indicators
COMPANY_SUFFIXES = [
    'inc', 'incorporated', 'corp', 'corporation', 'llc', 'ltd', 'limited',
    'co', 'company', 'group', 'holdings', 'enterprises', 'industries',
    'solutions', 'systems', 'technologies', 'tech', 'international',
    'global', 'services', 'partners', 'capital', 'ventures'
]

def validate_api_keys() -> Tuple[bool, str]:
    """
    Validate that all required API keys are present
    Returns: (is_valid, error_message)
    """
    required_keys = {
        'OPENAI_API_KEY': 'OpenAI (for GPT-4 analysis)',
        'TAVILY_API_KEY': 'Tavily (for web search)',
    }
    
    missing_keys = []
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"- {key} ({description})")
    
    if missing_keys:
        error_msg = "❌ **Missing Required API Keys:**\n\n" + "\n".join(missing_keys)
        error_msg += "\n\n**Action Required:** Please add these keys to your `.env` file."
        return False, error_msg
    
    return True, ""

def validate_company_name(name: str) -> Tuple[bool, str, str]:
    """
    Validate if input looks like a company name, not a personal name
    Returns: (is_valid, error_type, message)
    """
    # Basic checks
    if not name or len(name.strip()) < 2:
        return False, "empty", "⚠️ Company name cannot be empty."
    
    name_clean = name.strip()
    
    # Check for overly short names (likely typos or invalid)
    if len(name_clean) < 2:
        return False, "too_short", "⚠️ Company name is too short. Please enter a valid company name."
    
    # Check for numbers only
    if name_clean.isdigit():
        return False, "numbers_only", "⚠️ Invalid input. Please enter a company name, not just numbers."
    
    # Check for special characters (except common company name chars)
    if re.search(r'[<>{}|\\\^~\[\]`]', name_clean):
        return False, "invalid_chars", "⚠️ Company name contains invalid characters."
    
    # Check if it looks like a personal name (FirstName LastName)
    words = name_clean.split()
    
    # Check for title indicators (Mr., Mrs., Dr., etc.)
    for pattern in PERSONAL_NAME_PATTERNS:
        if re.search(pattern, name_clean, re.IGNORECASE):
            return False, "personal_name", (
                f"⚠️ **'{name_clean}' appears to be a personal name, not a company.**\n\n"
                "**This tool is designed for vetting companies, not individuals.**\n\n"
                "Please enter:\n"
                "- Full company legal name (e.g., 'Microsoft Corporation')\n"
                "- Brand name (e.g., 'Tesla', 'Google')\n"
                "- Company with suffix (e.g., 'Acme Corp', 'ABC Inc.')"
            )
    
    # If it's exactly two title-case words with no company indicators, likely a person
    if len(words) == 2:
        if all(word[0].isupper() and word[1:].islower() for word in words):
            # Check if it has any company suffix
            last_word_lower = words[-1].lower().rstrip('.')
            has_company_suffix = any(
                suffix in last_word_lower for suffix in COMPANY_SUFFIXES
            )
            
            if not has_company_suffix:
                return False, "possible_personal_name", (
                    f"⚠️ **Warning: '{name_clean}' may be a personal name.**\n\n"
                    "If this is a company, please include:\n"
                    "- Company suffix (Inc., LLC, Corp., Ltd.)\n"
                    "- Additional context (e.g., 'Company', 'Industries')\n\n"
                    "Examples:\n"
                    "✅ 'Johnson & Johnson'\n"
                    "✅ 'Goldman Sachs'\n"
                    "✅ 'Ford Motor Company'\n\n"
                    "Are you sure this is a company name?"
                )
    
    return True, "", ""

def quick_company_validation(search_results: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Quick validation based on initial search results
    Returns: (appears_valid, message)
    """
    total_results = search_results.get('total_results', 0)
    
    # If we got zero results, likely not a real company
    if total_results == 0:
        return False, (
            "❌ **No Information Found**\n\n"
            "**This suggests the company does not exist or the name is incorrect.**\n\n"
            "**Recommendations:**\n"
            "- Verify the exact legal company name\n"
            "- Check for common spelling variations\n"
            "- Ensure the company is publicly known\n"
            "- Try including location (e.g., 'Acme Corp California')"
        )
    
    # If very few results (1-2), might be invalid
    if total_results < 3:
        return False, (
            f"⚠️ **Very Limited Data Found** ({total_results} results)\n\n"
            "**This may indicate:**\n"
            "- Company name is misspelled\n"
            "- Company is very small or private\n"
            "- Company has minimal online presence\n\n"
            "**Proceeding with analysis will consume API tokens but may not provide meaningful results.**"
        )
    
    return True, ""

def estimate_token_cost(total_results: int) -> str:
    """
    Estimate approximate token cost for analysis
    """
    if total_results < 10:
        return "Low (~$0.01-0.02)"
    elif total_results < 30:
        return "Medium (~$0.03-0.06)"
    else:
        return "High (~$0.07-0.12)"

def llm_verify_company_match(company_name: str, search_results: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Use LLM to verify that:
    1. Search results are actually about the input company name
    2. The input is indeed a company, not a person
    Returns: (is_valid, detected_company_name, message)
    """
    from openai import OpenAI
    
    if not os.getenv("OPENAI_API_KEY"):
        return True, company_name, ""  # Skip if no API key
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Gather sample titles from search results
        titles = []
        for result in search_results.get('comprehensive_search', {}).get('general_search', [])[:5]:
            titles.append(result.get('title', ''))
        for result in search_results.get('comprehensive_search', {}).get('news_search', [])[:3]:
            titles.append(result.get('title', ''))
        
        if not titles:
            return False, "", "No search results to verify"
        
        titles_text = "\n".join([f"- {t}" for t in titles if t])
        
        verification_prompt = f"""You are a data verification expert. Analyze if the search results match the input query.

INPUT QUERY: "{company_name}"

SEARCH RESULT TITLES:
{titles_text}

Answer these questions:
1. Are these search results about a COMPANY or about a PERSON?
2. If it's a company, what is the EXACT company name from the results?
3. Does the company name in results MATCH the input query "{company_name}"?
4. If it's different, what company are the results actually about?

Respond in this exact format:
TYPE: [COMPANY or PERSON]
EXACT_NAME: [exact company name from results or "N/A"]
MATCH: [YES or NO]
ACTUAL_SUBJECT: [what the results are actually about]
CONFIDENCE: [HIGH, MEDIUM, or LOW]

Be very strict. If the results are about a different company or person, say NO for MATCH."""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a strict data verification assistant. Your job is to prevent false matches and hallucinations."},
                {"role": "user", "content": verification_prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        verification = response.choices[0].message.content
        
        # Parse the response
        is_company = "TYPE: COMPANY" in verification
        is_match = "MATCH: YES" in verification
        
        # Extract actual company name if different
        detected_name = company_name
        for line in verification.split('\n'):
            if line.startswith('EXACT_NAME:'):
                name = line.replace('EXACT_NAME:', '').strip()
                if name and name != "N/A":
                    detected_name = name
            if line.startswith('ACTUAL_SUBJECT:'):
                actual = line.replace('ACTUAL_SUBJECT:', '').strip()
        
        # Determine validity
        if not is_company:
            return False, "", (
                f"❌ **'{company_name}' appears to be a PERSON, not a company.**\n\n"
                f"**Search results are about an individual, not a business entity.**\n\n"
                f"This tool is designed for vetting companies only. Please enter a company name."
            )
        
        if not is_match:
            return False, detected_name, (
                f"⚠️ **Search Results Mismatch Detected!**\n\n"
                f"**You searched for:** '{company_name}'\n"
                f"**Results are about:** '{detected_name}'\n\n"
                f"**This suggests:**\n"
                f"- The company name you entered may not exist\n"
                f"- The search engine found a similar but different company\n"
                f"- You need to enter the EXACT legal company name\n\n"
                f"**Action Required:** Enter the exact company name or verify spelling."
            )
        
        return True, detected_name, ""
        
    except Exception as e:
        print(f"LLM verification error: {str(e)}")
        # On error, allow to proceed but log it
        return True, company_name, ""

def validate_before_analysis(company_name: str, search_results: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Comprehensive validation before proceeding with expensive AI analysis
    Returns: (should_proceed, message)
    """
    # Check API keys first
    keys_valid, keys_msg = validate_api_keys()
    if not keys_valid:
        return False, keys_msg
    
    # Validate company name format
    name_valid, error_type, name_msg = validate_company_name(company_name)
    if not name_valid and error_type in ["empty", "too_short", "invalid_chars", "numbers_only", "personal_name"]:
        return False, name_msg
    
    # Quick validation based on search results
    results_valid, results_msg = quick_company_validation(search_results)
    if not results_valid:
        return False, results_msg
    
    # LLM-based verification to prevent hallucination and name mismatch
    llm_valid, detected_name, llm_msg = llm_verify_company_match(company_name, search_results)
    if not llm_valid:
        return False, llm_msg
    
    # If name is possibly personal but we have some results, warn user
    if not name_valid and error_type == "possible_personal_name":
        return False, name_msg  # Still block, require user confirmation
    
    return True, ""
