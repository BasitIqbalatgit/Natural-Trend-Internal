# 🔍 Complete Validation Flow - Technical Documentation

## System Architecture Overview

This document explains the **5-Layer Validation System** that prevents token waste and ensures data quality.

---

## 📊 Complete Data Flow (Step-by-Step)

### **User Journey:**
```
User Input → Validation Layers → Data Collection → Filtering → Analysis → Report
     ↓              ↓                   ↓              ↓           ↓         ↓
  "Tesla"      5 Checks         Tavily API      Relevance    GPT-4 AI    PDF
```

---

## 🛡️ Layer 1: Pre-Search Input Validation

**Location:** `app.py` (Lines 165-181) + `utils/validators.py` (Lines 55-114)

### **What Happens:**
User clicks "Run Vetting Analysis" button → System validates input BEFORE making any API calls

### **Source Code Flow:**

**File:** `app.py`
```python
# Line 165: User clicks button
if vet_button:
    if not company_name:
        st.error("⚠️ Please enter a company name to proceed.")
    else:
        # Line 169: STEP 0 - Validate BEFORE any API calls
        name_valid, error_type, validation_msg = validate_company_name(company_name)
```

**File:** `utils/validators.py` - `validate_company_name()`
```python
def validate_company_name(name: str) -> Tuple[bool, str, str]:
    """
    Validates input format
    Returns: (is_valid, error_type, message)
    """
    # Check 1: Empty input
    if not name or len(name.strip()) < 2:
        return False, "empty", "⚠️ Company name cannot be empty."
    
    # Check 2: Numbers only
    if name_clean.isdigit():
        return False, "numbers_only", "⚠️ Invalid input."
    
    # Check 3: Special characters
    if re.search(r'[<>{}|\\\^~\[\]`]', name_clean):
        return False, "invalid_chars", "⚠️ Invalid characters."
    
    # Check 4: Personal name patterns (Mr., Mrs., Dr.)
    for pattern in PERSONAL_NAME_PATTERNS:
        if re.search(pattern, name_clean, re.IGNORECASE):
            return False, "personal_name", "This appears to be a person..."
    
    # Check 5: Two words without company suffix = probably person
    if len(words) == 2:
        # "John Smith" vs "Goldman Sachs"
        has_company_suffix = any(suffix in last_word for suffix in COMPANY_SUFFIXES)
        if not has_company_suffix:
            return False, "possible_personal_name", "May be a personal name..."
```

### **Examples:**
- ✅ Input: `"Tesla"` → **PASS** → Continue
- ❌ Input: `"123"` → **BLOCKED** → Error shown
- ❌ Input: `"John Smith"` → **BLOCKED** → Error shown
- ⚠️ Input: `"Basit Iqbal"` → **WARNING** → User must confirm

**Cost:** $0.00 (No API calls made)

---

## 🌐 Layer 2: Data Collection (Tavily API)

**Location:** `utils/api_calls.py` (Lines 14-72)

### **What Happens:**
If Layer 1 passes → System calls Tavily Search API to gather web data

### **Source Code Flow:**

**File:** `app.py`
```python
# Line 197: Start data collection
status_text.text("📡 Step 1/4: Collecting data from multiple sources...")
raw_data = aggregate_all_data(company_name)
```

**File:** `utils/api_calls.py` - `aggregate_all_data()`
```python
def aggregate_all_data(company_name: str) -> Dict[str, Any]:
    # Step 1: Get raw data from Tavily API
    comprehensive = search_company_comprehensive(company_name)
    recent = get_recent_news(company_name)
    social = search_social_media_specific(company_name)
    execs = search_executives(company_name)
```

### **What `search_company_comprehensive()` Does:**

```python
def search_company_comprehensive(company_name: str) -> Dict[str, Any]:
    # 4 separate Tavily API calls:
    
    # 1. General company information
    general_results = tavily_client.search(
        query=f"{company_name} company overview reputation",
        search_depth="advanced",
        max_results=10
    )
    # Returns: [{title: "...", url: "...", content: "..."}, ...]
    
    # 2. News and scandals
    news_results = tavily_client.search(
        query=f"{company_name} news scandal controversy lawsuit",
        search_depth="advanced",
        max_results=10,
        topic="news"
    )
    
    # 3. Legal/regulatory violations
    legal_results = tavily_client.search(
        query=f"{company_name} legal violations regulatory enforcement",
        search_depth="advanced",
        max_results=8
    )
    
    # 4. Social media
    social_results = tavily_client.search(
        query=f"{company_name} social media Twitter LinkedIn",
        search_depth="basic",
        max_results=5
    )
```

### **Tavily API Response Example:**
```json
{
  "results": [
    {
      "title": "Tesla - Official Website",
      "url": "https://www.tesla.com",
      "content": "Tesla designs and manufactures electric vehicles...",
      "score": 0.95
    },
    {
      "title": "Tesla News on Bloomberg",
      "url": "https://bloomberg.com/tesla",
      "content": "Latest Tesla news and stock information...",
      "score": 0.87
    }
  ]
}
```

**Cost:** ~$0.02 (4 Tavily API calls)

---

## 🔍 Layer 3: Content Relevance Filtering (NEW)

**Location:** `utils/api_calls.py` (Lines 180-243)

### **What Happens:**
After getting raw results → System filters out irrelevant results that don't mention the company

### **Source Code Flow:**

**File:** `utils/api_calls.py` - Inside `aggregate_all_data()`
```python
# Line 232: Filter for relevance
print("🔍 Validating result relevance...")
comprehensive["general_search"] = filter_irrelevant_results(
    comprehensive.get("general_search", []), 
    company_name
)
comprehensive["news_search"] = filter_irrelevant_results(
    comprehensive.get("news_search", []), 
    company_name
)
```

### **How `filter_irrelevant_results()` Works:**

```python
def filter_irrelevant_results(results: List[Dict], company_name: str) -> List[Dict]:
    """
    Filters out results that don't mention the company
    """
    relevant_results = []
    for result in results:
        if validate_result_relevance(result, company_name):
            relevant_results.append(result)  # Keep it
        # else: discard it
    
    print(f"🔍 Filtered out {filtered_count} irrelevant results")
    return relevant_results
```

### **How `validate_result_relevance()` Works:**

```python
def validate_result_relevance(result: Dict[str, Any], company_name: str) -> bool:
    """
    Checks if result actually mentions the company
    """
    # Extract all text from result
    title = result.get('title', '').lower()
    content = result.get('content', '').lower()
    url = result.get('url', '').lower()
    full_text = f"{title} {content} {url}"
    
    # Get company name words
    company_lower = company_name.lower()
    company_words = company_lower.split()
    
    if len(company_words) == 1:
        # Single word: must appear in result
        # "Tesla" must be in title/content/url
        return company_lower in full_text
    else:
        # Multi-word: at least 50% of words must appear
        # "Goldman Sachs" → need "goldman" OR "sachs"
        matches = sum(1 for word in company_words if len(word) > 2 and word in full_text)
        return matches >= len(company_words) * 0.5
```

### **Real Example:**

**Input:** "Microsoft"

**Raw Results from Tavily:**
1. Title: "Microsoft Corporation - Official Site" → Contains "microsoft" ✅ **KEEP**
2. Title: "Apple releases new MacBook" → No "microsoft" ❌ **FILTER OUT**
3. Title: "Tech industry news" → No "microsoft" ❌ **FILTER OUT**
4. Title: "Microsoft Azure cloud services" → Contains "microsoft" ✅ **KEEP**

**Result:** 50 raw results → 35 relevant results (15 filtered out)

**Cost:** $0.00 (Pure text matching, no API calls)

---

## 🤖 Layer 4: LLM Company Match Verification

**Location:** `utils/validators.py` (Lines 152-245)

### **What Happens:**
After filtering → GPT-4 verifies that results are actually about the company we searched for

### **Source Code Flow:**

**File:** `app.py`
```python
# Line 202: LLM Verification
status_text.text(f"🔍 Verifying search results match '{company_name}'...")
should_proceed, validation_msg = validate_before_analysis(company_name, raw_data)
```

**File:** `utils/validators.py` - `validate_before_analysis()`
```python
def validate_before_analysis(company_name: str, search_results: Dict[str, Any]):
    # Multiple checks...
    
    # CRITICAL: LLM verification
    llm_valid, detected_name, llm_msg = llm_verify_company_match(company_name, search_results)
    if not llm_valid:
        return False, llm_msg  # Block analysis
```

### **How `llm_verify_company_match()` Works:**

```python
def llm_verify_company_match(company_name: str, search_results: Dict[str, Any]):
    """
    Uses GPT-4 to verify search results match input
    """
    # Step 1: Extract titles from search results
    titles = []
    for result in search_results.get('comprehensive_search', {}).get('general_search', [])[:5]:
        titles.append(result.get('title', ''))
    
    # Step 2: Create verification prompt
    verification_prompt = f"""
    You are a data verification expert.
    
    INPUT QUERY: "{company_name}"
    
    SEARCH RESULT TITLES:
    - {titles[0]}
    - {titles[1]}
    - {titles[2]}
    ...
    
    Answer:
    1. Are these about a COMPANY or PERSON?
    2. What is the EXACT company name?
    3. Does it MATCH the input "{company_name}"?
    
    FORMAT:
    TYPE: [COMPANY or PERSON]
    EXACT_NAME: [company name]
    MATCH: [YES or NO]
    """
    
    # Step 3: Call GPT-4
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You prevent false matches."},
            {"role": "user", "content": verification_prompt}
        ],
        temperature=0.1  # Low temperature = more factual
    )
    
    # Step 4: Parse response
    verification = response.choices[0].message.content
    
    is_company = "TYPE: COMPANY" in verification
    is_match = "MATCH: YES" in verification
    
    # Step 5: Make decision
    if not is_company:
        return False, "", "This appears to be a PERSON, not a company"
    
    if not is_match:
        return False, detected_name, "Search results are about a DIFFERENT company"
    
    return True, company_name, ""  # All good!
```

### **Real Example:**

**Input:** "Basit"

**Search Result Titles:**
- "Basit Ambulette Services"
- "Basit Transport Company"
- "Muhammad Basit Profile"

**GPT-4 Analysis:**
```
TYPE: COMPANY
EXACT_NAME: Basit Ambulette
MATCH: NO
ACTUAL_SUBJECT: Basit Ambulette (different from input 'Basit')
```

**System Action:** ❌ **BLOCKED** → "Results are about 'Basit Ambulette', not 'Basit'"

**Cost:** ~$0.01 (1 GPT-4 API call, ~500 tokens)

---

## 🎯 Layer 5: Pre-Analysis Final Check

**Location:** `utils/langgraph_workflow.py` (Lines 293-350)

### **What Happens:**
Before spending tokens on full analysis → Verify we have enough relevant data

### **Source Code Flow:**

**File:** `utils/langgraph_workflow.py` - `run_vetting_analysis()`
```python
def run_vetting_analysis(company_name: str, raw_data: Dict[str, Any]):
    # Check if sufficient data exists
    total_results = raw_data.get('total_results', 0)
    data_found = raw_data.get('data_found', False)
    
    if not data_found or total_results < 3:
        # Return limited report without expensive AI analysis
        return VettingState(
            company_name=company_name,
            final_report={
                "executive_summary": f"## ⚠️ INSUFFICIENT DATA FOR: {company_name}...",
                "data_sources_checked": total_results,
            },
            current_step="insufficient_data"
        )
    
    # Enough data → Proceed with full AI analysis
    workflow = create_vetting_workflow()
    final_state = workflow.invoke(initial_state)
```

### **Decision Logic:**
```
IF total_results == 0:
    → "No company found"
ELSE IF total_results < 3:
    → "Insufficient data for analysis"
ELSE:
    → Proceed with AI analysis (costs $0.05-0.10)
```

**Cost:** $0.00 (Simple counting, no API calls)

---

## 💰 Complete Cost Analysis

### **Failed Request (Blocked Early):**
```
Input: "John Smith"
├─ Layer 1: Input Validation ❌ BLOCKED
└─ Total Cost: $0.00
```

### **Invalid Company (Blocked Mid-Way):**
```
Input: "XYZ Fake Corp"
├─ Layer 1: Input Validation ✅ ($0.00)
├─ Layer 2: Tavily Search ✅ ($0.02)
├─ Layer 3: Content Filtering → 0 relevant ✅ ($0.00)
├─ Layer 4: LLM Verification ❌ BLOCKED ($0.01)
└─ Total Cost: $0.03 (saved $0.07)
```

### **Valid Company (Full Analysis):**
```
Input: "Tesla"
├─ Layer 1: Input Validation ✅ ($0.00)
├─ Layer 2: Tavily Search ✅ ($0.02)
├─ Layer 3: Content Filtering → 45 relevant ✅ ($0.00)
├─ Layer 4: LLM Verification ✅ ($0.01)
├─ Layer 5: Sufficient Data Check ✅ ($0.00)
└─ AI Analysis ✅ ($0.07)
└─ Total Cost: $0.10
```

---

## 📁 File Structure & Responsibilities

```
app.py
├─ User Interface (Streamlit)
├─ Button click handling
└─ Calls: validate_company_name()

utils/validators.py
├─ validate_api_keys() → Startup check
├─ validate_company_name() → Layer 1
├─ llm_verify_company_match() → Layer 4
└─ validate_before_analysis() → Orchestrator

utils/api_calls.py
├─ search_company_comprehensive() → Tavily API calls
├─ validate_result_relevance() → Layer 3
├─ filter_irrelevant_results() → Layer 3
└─ aggregate_all_data() → Data collection

utils/langgraph_workflow.py
├─ run_vetting_analysis() → Layer 5
├─ extract_entities_node() → AI analysis
├─ analyze_risks_node() → AI analysis
└─ generate_report_node() → Final report
```

---

## 🔄 Complete Flow Diagram

```
┌──────────────┐
│  User Input  │
│   "Tesla"    │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────┐
│  LAYER 1: Input Validation      │
│  File: validators.py            │
│  - Check empty/invalid          │
│  - Detect personal names        │
│  Cost: $0.00                    │
└──────┬──────────────────────────┘
       │ ✅ PASS
       ▼
┌─────────────────────────────────┐
│  LAYER 2: Data Collection       │
│  File: api_calls.py             │
│  - 4x Tavily API calls          │
│  - General, news, legal, social │
│  Cost: ~$0.02                   │
│  Returns: 50 raw results        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  LAYER 3: Content Filtering     │
│  File: api_calls.py             │
│  - Check title/content/url      │
│  - Must mention company name    │
│  Cost: $0.00                    │
│  Returns: 35 relevant results   │
└──────┬──────────────────────────┘
       │ ✅ Has relevant data
       ▼
┌─────────────────────────────────┐
│  LAYER 4: LLM Verification      │
│  File: validators.py            │
│  - GPT-4 verifies exact match   │
│  - Person vs company check      │
│  Cost: ~$0.01                   │
└──────┬──────────────────────────┘
       │ ✅ MATCH confirmed
       ▼
┌─────────────────────────────────┐
│  LAYER 5: Pre-Analysis Check    │
│  File: langgraph_workflow.py   │
│  - Verify sufficient data       │
│  Cost: $0.00                    │
└──────┬──────────────────────────┘
       │ ✅ Enough data (35 > 3)
       ▼
┌─────────────────────────────────┐
│  AI ANALYSIS                     │
│  - Entity extraction             │
│  - Risk analysis                 │
│  - P&G questions                 │
│  - Report generation             │
│  Cost: ~$0.07                    │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  PDF REPORT                      │
│  "Tesla_vetting_report.pdf"     │
└─────────────────────────────────┘
```

---

## 🎓 Key Takeaways

1. **5 Validation Layers** protect against invalid inputs
2. **Early Blocking** saves 70% of costs on invalid requests
3. **Content Filtering** ensures data quality
4. **LLM Verification** prevents hallucination
5. **Graceful Degradation** provides useful feedback even on failure

This system is **production-ready** and follows **enterprise software engineering** best practices! 🚀
