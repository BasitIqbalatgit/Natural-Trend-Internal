import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

# Initialize Tavily Client for comprehensive web search
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_company_comprehensive(company_name: str) -> Dict[str, Any]:
    """
    Comprehensive search using Tavily API which includes:
    - General web search
    - News articles
    - Social media mentions
    - Regulatory/legal information
    """
    results = {
        "general_search": [],
        "news_search": [],
        "legal_regulatory": [],
        "social_media": [],
        "company_info": {}
    }
    
    try:
        # General web search about the company
        print(f"Searching for: {company_name}")
        general_results = tavily_client.search(
            query=f"{company_name} company overview reputation",
            search_depth="advanced",
            max_results=10
        )
        results["general_search"] = general_results.get("results", [])
        
        # News and scandal search
        news_results = tavily_client.search(
            query=f"{company_name} news scandal controversy lawsuit",
            search_depth="advanced",
            max_results=10,
            topic="news"
        )
        results["news_search"] = news_results.get("results", [])
        
        # Legal and regulatory violations
        legal_results = tavily_client.search(
            query=f"{company_name} legal violations regulatory enforcement SEC violations",
            search_depth="advanced",
            max_results=8
        )
        results["legal_regulatory"] = legal_results.get("results", [])
        
        # Social media presence and reputation
        social_results = tavily_client.search(
            query=f"{company_name} social media Twitter LinkedIn Facebook Instagram reputation",
            search_depth="basic",
            max_results=5
        )
        results["social_media"] = social_results.get("results", [])
        
        return results
        
    except Exception as e:
        print(f"Error in comprehensive search: {str(e)}")
        return results

def classify_executive_information(executive_name: str, findings: List[Dict]) -> Dict[str, List]:
    """
    Use LLM to classify executive information as positive, neutral, or negative
    Returns: {"positive": [...], "neutral": [...], "negative": [...]}
    """
    from openai import OpenAI
    
    if not os.getenv("OPENAI_API_KEY") or not findings:
        return {"positive": [], "neutral": [], "negative": []}
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        classified = {"positive": [], "neutral": [], "negative": []}
        
        # Classify each finding
        for finding in findings[:10]:  # Limit to prevent token overflow
            title = finding.get('title', '')
            content = finding.get('content', '')[:300]
            
            if not title and not content:
                continue
            
            classification_prompt = f"""Analyze this information about {executive_name}:

Title: {title}
Content: {content}

Classify as:
- POSITIVE: Awards, achievements, positive leadership, good reviews, charity work
- NEGATIVE: Scandals, crimes, lawsuits, misconduct, fraud, violations, controversies
- NEUTRAL: General information, job announcements, neutral facts

Also verify: Is this actually about {executive_name} (the person)?

Respond ONLY with:
CLASSIFICATION: [POSITIVE/NEGATIVE/NEUTRAL]
ABOUT_PERSON: [YES/NO]
REASON: [one sentence why]"""

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You classify executive information accurately."},
                    {"role": "user", "content": classification_prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content
            
            # Parse response
            is_about_person = "ABOUT_PERSON: YES" in result
            
            if not is_about_person:
                continue  # Skip if not about the person
            
            # Add to appropriate category
            if "CLASSIFICATION: POSITIVE" in result:
                classified["positive"].append(finding)
            elif "CLASSIFICATION: NEGATIVE" in result:
                classified["negative"].append(finding)
            else:
                classified["neutral"].append(finding)
        
        return classified
        
    except Exception as e:
        print(f"   ⚠️ Classification error: {str(e)}")
        # On error, put everything in neutral
        return {"positive": [], "neutral": findings, "negative": []}

def search_executive_background(executive_name: str, company_name: str) -> Dict[str, Any]:
    """
    Comprehensive background check on a specific executive
    Searches for: legal issues, scandals, controversies, social media
    Returns classified information (positive/negative/neutral)
    """
    exec_data = {
        "name": executive_name,
        "all_findings": [],
        "positive": [],
        "negative": [],
        "neutral": [],
        "summary": {
            "total_findings": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0
        }
    }
    
    try:
        print(f"   🔍 Investigating: {executive_name}")
        
        # 1. General information
        general_results = tavily_client.search(
            query=f'"{executive_name}" {company_name} CEO executive biography achievements',
            search_depth="basic",
            max_results=5
        )
        
        # 2. Scandals and controversies
        scandal_results = tavily_client.search(
            query=f'"{executive_name}" {company_name} scandal controversy misconduct allegations',
            search_depth="advanced",
            max_results=8
        )
        
        # 3. Legal issues (criminal, civil, regulatory)
        legal_results = tavily_client.search(
            query=f'"{executive_name}" lawsuit arrest charges indictment fraud criminal investigation SEC',
            search_depth="advanced",
            max_results=8
        )
        
        # Combine all findings
        all_findings = (
            general_results.get("results", []) +
            scandal_results.get("results", []) +
            legal_results.get("results", [])
        )
        
        # Filter for relevance to the person
        relevant_findings = filter_irrelevant_results(all_findings, executive_name)
        
        print(f"   📊 Found {len(relevant_findings)} relevant items, classifying...")
        
        # Classify findings as positive/negative/neutral
        classified = classify_executive_information(executive_name, relevant_findings)
        
        exec_data["positive"] = classified["positive"]
        exec_data["negative"] = classified["negative"]
        exec_data["neutral"] = classified["neutral"]
        exec_data["all_findings"] = relevant_findings
        
        exec_data["summary"] = {
            "total_findings": len(relevant_findings),
            "positive_count": len(classified["positive"]),
            "negative_count": len(classified["negative"]),
            "neutral_count": len(classified["neutral"])
        }
        
        if exec_data["summary"]["negative_count"] > 0:
            print(f"   ⚠️  Found {exec_data['summary']['negative_count']} NEGATIVE items about {executive_name}")
        elif exec_data["summary"]["positive_count"] > 0:
            print(f"   ✅ Found {exec_data['summary']['positive_count']} POSITIVE items about {executive_name}")
        else:
            print(f"   ℹ️  Found {exec_data['summary']['neutral_count']} NEUTRAL items about {executive_name}")
        
        return exec_data
        
    except Exception as e:
        print(f"   ❌ Error investigating {executive_name}: {str(e)}")
        return exec_data

def search_executives(company_name: str, executive_names: List[str] = None) -> Dict[str, Any]:
    """
    Comprehensive executive background checks
    If no names provided, searches for CEO and C-suite
    """
    executives_data = {
        "leadership_overview": [],
        "executives_investigated": {},
        "total_executives": 0,
        "negative_findings_count": 0
    }
    
    try:
        print("👔 Starting executive background checks...")
        
        # Step 1: Find company leadership if not provided
        if not executive_names:
            print("   🔍 Identifying company executives...")
            leadership_search = tavily_client.search(
                query=f"{company_name} CEO CFO COO executives leadership management team board",
                search_depth="advanced",
                max_results=10
            )
            executives_data["leadership_overview"] = filter_irrelevant_results(
                leadership_search.get("results", []),
                company_name
            )
            
            # Use LLM to extract executive names from results
            executive_names = extract_executive_names_from_results(
                company_name,
                executives_data["leadership_overview"]
            )
        
        # Step 2: Deep dive on each executive
        if executive_names:
            print(f"   📋 Investigating {len(executive_names)} executives...")
            for exec_name in executive_names[:5]:  # Limit to top 5
                exec_data = search_executive_background(exec_name, company_name)
                executives_data["executives_investigated"][exec_name] = exec_data
                
                # Count negative findings from summary
                negative_count = exec_data.get("summary", {}).get("negative_count", 0)
                executives_data["negative_findings_count"] += negative_count
            
            executives_data["total_executives"] = len(executive_names)
        
        print(f"   ✅ Executive checks complete: {executives_data['total_executives']} executives, {executives_data['negative_findings_count']} negative findings")
        return executives_data
        
    except Exception as e:
        print(f"   ❌ Error in executive search: {str(e)}")
        return executives_data

def extract_executive_names_from_results(company_name: str, search_results: List[Dict]) -> List[str]:
    """
    Use LLM to extract executive names from search results
    Returns list of executive names
    """
    from openai import OpenAI
    
    if not os.getenv("OPENAI_API_KEY") or not search_results:
        return []
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Compile text from search results
        text_content = ""
        for result in search_results[:5]:
            text_content += f"Title: {result.get('title', '')}\n"
            text_content += f"Content: {result.get('content', '')[:300]}\n\n"
        
        extraction_prompt = f"""Extract the names of executives (CEO, CFO, COO, President, etc.) from this text about {company_name}.

Text:
{text_content}

Return ONLY a JSON array of executive names with their titles, like this:
["John Doe (CEO)", "Jane Smith (CFO)", "Bob Johnson (COO)"]

If no executives found, return: []
Be strict: only return names that are clearly identified as executives of {company_name}."""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You extract executive names from text. Return only valid JSON array."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        import json
        names_json = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if "```" in names_json:
            names_json = names_json.split("```")[1].replace("json", "").strip()
        
        executive_names = json.loads(names_json)
        
        if executive_names:
            print(f"   ✅ Identified executives: {', '.join(executive_names)}")
        
        return executive_names
        
    except Exception as e:
        print(f"   ⚠️  Could not extract executive names: {str(e)}")
        return []

def get_recent_news(company_name: str, days: int = 90) -> List[Dict]:
    """
    Get recent news articles about the company (last X days)
    """
    try:
        results = tavily_client.search(
            query=f"{company_name} latest news updates",
            search_depth="advanced",
            max_results=15,
            topic="news",
            days=days
        )
        return results.get("results", [])
    except Exception as e:
        print(f"Error fetching recent news: {str(e)}")
        return []

def search_social_media_specific(company_name: str) -> Dict[str, Any]:
    """
    Targeted social media search across platforms
    """
    social_data = {
        "twitter": [],
        "linkedin": [],
        "facebook": [],
        "reddit": [],
        "general": []
    }
    
    try:
        # Twitter/X mentions
        twitter_results = tavily_client.search(
            query=f"{company_name} site:twitter.com OR site:x.com",
            max_results=5
        )
        social_data["twitter"] = twitter_results.get("results", [])
        
        # LinkedIn company page
        linkedin_results = tavily_client.search(
            query=f"{company_name} site:linkedin.com company",
            max_results=3
        )
        social_data["linkedin"] = linkedin_results.get("results", [])
        
        # Reddit discussions
        reddit_results = tavily_client.search(
            query=f"{company_name} site:reddit.com controversy opinion",
            max_results=5
        )
        social_data["reddit"] = reddit_results.get("results", [])
        
        return social_data
        
    except Exception as e:
        print(f"Error in social media search: {str(e)}")
        return social_data

def validate_result_relevance(result: Dict[str, Any], company_name: str) -> bool:
    """
    Validate that a search result actually mentions the company
    Returns True if relevant, False otherwise
    """
    if not result:
        return False
    
    # Get title and content
    title = result.get('title', '').lower()
    content = result.get('content', '').lower()
    url = result.get('url', '').lower()
    
    # Combine all text
    full_text = f"{title} {content} {url}"
    
    # Check if company name appears in the result
    company_lower = company_name.lower()
    company_words = company_lower.split()
    
    # Must contain at least the main company words
    # For "Microsoft Corporation", check if "microsoft" appears
    # For "Goldman Sachs", check if both "goldman" and "sachs" appear
    
    if len(company_words) == 1:
        # Single word company name must appear
        return company_lower in full_text
    else:
        # Multi-word: at least 50% of words must appear
        matches = sum(1 for word in company_words if len(word) > 2 and word in full_text)
        return matches >= len(company_words) * 0.5

def filter_irrelevant_results(results: List[Dict], company_name: str) -> List[Dict]:
    """
    Filter out results that don't actually mention the company
    """
    relevant_results = []
    for result in results:
        if validate_result_relevance(result, company_name):
            relevant_results.append(result)
    
    if len(results) > 0:
        filtered_count = len(results) - len(relevant_results)
        if filtered_count > 0:
            print(f"🔍 Filtered out {filtered_count} irrelevant results")
    
    return relevant_results

def aggregate_all_data(company_name: str) -> Dict[str, Any]:
    """
    Aggregate all available data for comprehensive vetting
    """
    print(f"Starting comprehensive data collection for: {company_name}")
    
    # Validate API key exists
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    
    # Get raw data
    comprehensive = search_company_comprehensive(company_name)
    recent = get_recent_news(company_name)
    social = search_social_media_specific(company_name)
    execs = search_executives(company_name)
    
    # Filter for relevance
    print("🔍 Validating result relevance...")
    comprehensive["general_search"] = filter_irrelevant_results(
        comprehensive.get("general_search", []), 
        company_name
    )
    comprehensive["news_search"] = filter_irrelevant_results(
        comprehensive.get("news_search", []), 
        company_name
    )
    comprehensive["legal_regulatory"] = filter_irrelevant_results(
        comprehensive.get("legal_regulatory", []), 
        company_name
    )
    recent = filter_irrelevant_results(recent, company_name)
    
    # Filter social media
    for platform in social:
        social[platform] = filter_irrelevant_results(
            social.get(platform, []), 
            company_name
        )
    
    all_data = {
        "company_name": company_name,
        "comprehensive_search": comprehensive,
        "recent_news": recent,
        "social_media": social,
        "executives": execs,
        "data_found": False,
        "total_results": 0,
        "relevant_results": 0
    }
    
    # Calculate total results found
    total_results = (
        len(all_data["comprehensive_search"].get("general_search", [])) +
        len(all_data["comprehensive_search"].get("news_search", [])) +
        len(all_data["comprehensive_search"].get("legal_regulatory", [])) +
        len(all_data["recent_news"]) +
        sum(len(v) for v in all_data["social_media"].values())
    )
    
    all_data["total_results"] = total_results
    all_data["relevant_results"] = total_results
    all_data["data_found"] = total_results > 0
    
    # Warn if no data found
    if total_results == 0:
        print(f"⚠️ WARNING: No relevant data found for company '{company_name}'. Company may not exist or name may be incorrect.")
    else:
        print(f"✅ Found {total_results} relevant data points for {company_name}")
    
    return all_data
