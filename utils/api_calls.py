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

def search_executives(company_name: str, executive_names: List[str] = None) -> Dict[str, List]:
    """
    Search for information about company executives
    """
    executives_info = {}
    
    try:
        # If no specific executives provided, search for company leadership
        if not executive_names:
            exec_search = tavily_client.search(
                query=f"{company_name} CEO executives leadership team",
                search_depth="basic",
                max_results=5
            )
            executives_info["leadership_overview"] = exec_search.get("results", [])
        else:
            # Search for specific executives
            for exec_name in executive_names:
                exec_results = tavily_client.search(
                    query=f"{exec_name} {company_name} scandal controversy misconduct",
                    search_depth="advanced",
                    max_results=5
                )
                executives_info[exec_name] = exec_results.get("results", [])
        
        return executives_info
        
    except Exception as e:
        print(f"Error searching executives: {str(e)}")
        return executives_info

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

def aggregate_all_data(company_name: str) -> Dict[str, Any]:
    """
    Aggregate all available data for comprehensive vetting
    """
    print(f"Starting comprehensive data collection for: {company_name}")
    
    # Validate API key exists
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    
    all_data = {
        "company_name": company_name,
        "comprehensive_search": search_company_comprehensive(company_name),
        "recent_news": get_recent_news(company_name),
        "social_media": search_social_media_specific(company_name),
        "executives": search_executives(company_name),
        "data_found": False,
        "total_results": 0
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
    all_data["data_found"] = total_results > 0
    
    # Warn if no data found
    if total_results == 0:
        print(f"⚠️ WARNING: No data found for company '{company_name}'. Company may not exist or name may be incorrect.")
    else:
        print(f"✅ Found {total_results} data points for {company_name}")
    
    return all_data
