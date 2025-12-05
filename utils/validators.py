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
    
    # If name is possibly personal but we have some results, warn user
    if not name_valid and error_type == "possible_personal_name":
        return False, name_msg  # Still block, require user confirmation
    
    return True, ""
