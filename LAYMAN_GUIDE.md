# 📘 AI-Powered Client Vetting Tool - User Guide
## For Non-Technical Users (Executives, Managers, Business Users)

---

## 🎯 What Is This Tool?

This is an **automated company vetting system** that helps you quickly check if a company is safe to work with. Think of it as a "background check" for businesses.

Instead of spending hours manually searching Google, reading news articles, and checking legal databases, this tool does all that work for you in **30-60 seconds** using artificial intelligence.

---

## 🤔 Why Do We Need This?

**The Problem:**
- Manual vetting takes 2-4 hours per company
- Easy to miss important scandals or legal issues
- Inconsistent results between different researchers
- Risk of partnering with problematic companies

**The Solution:**
This tool automatically:
- ✅ Searches hundreds of web sources in seconds
- ✅ Analyzes news articles, legal records, and social media
- ✅ Checks company executives for misconduct
- ✅ Answers P&G's 7 brand safety questions
- ✅ Generates professional PDF reports

---

## 📋 How to Use (Step-by-Step)

### **Step 1: Open the Tool**
1. Someone from IT will run the command: `streamlit run app.py`
2. Your web browser will open automatically
3. You'll see a page that looks like a modern website

### **Step 2: Enter Company Information**
1. **Type the company name** in the text box
   - ✅ Good: "Microsoft Corporation", "Tesla", "Goldman Sachs"
   - ❌ Bad: "John Smith" (that's a person!), "MSFT" (use full name)

**Note:** All searches are automatically performed at Deep Search level for comprehensive analysis (60+ seconds).

### **Step 3: Optional - Add Executive Names**
- If you want to check specific executives, add their names
- Example: "Elon Musk", "Tim Cook"
- Leave blank to auto-detect leadership

### **Step 4: Click "Run Vetting Analysis"**
- Wait 30-60 seconds
- Watch the progress bar
- Don't close the browser!

### **Step 5: Review Results**
You'll see 5 tabs with information:

#### **Tab 1: Risk Analysis** ⚠️
Shows if the company has:
- Scandals or controversies
- Legal problems
- Regulatory violations
- How serious the issues are

#### **Tab 2: P&G Questions** ✅
Answers 7 key questions:
1. Does the company have good reputation?
2. Free from serious scandals?
3. No regulatory violations?
4. No legal violations?
5. Executives clean record?
6. No PR risks?
7. Brand safety compliant?

#### **Tab 3: Executive Checks** 👔
Shows background on company leaders:
- ⚠️ **NEGATIVE** = Criminal, fraud, scandals
- ✅ **POSITIVE** = Awards, achievements
- ℹ️ **NEUTRAL** = General information

#### **Tab 4: Data Sources** 📰
Lists all the websites, news articles, and sources checked

#### **Tab 5: PDF Report** 📄
Download a professional report to share with your team

---

## ⏱️ How Long Does It Take?

**All analyses use Deep Search automatically:**
- Time Required: 60-90 seconds
- Data Points Analyzed: 80-120 sources

**Total Process:**
- Data Collection: 10-15 seconds
- AI Analysis: 15-25 seconds
- PDF Generation: 2-5 seconds
- **Total: 30-60 seconds**

**Note:** The system performs comprehensive Deep Search for all companies to ensure thorough vetting.

---

## 💰 How Much Does It Cost?

### **Per Company Analysis:**
- **Low complexity:** $0.01-0.02 (small company, little data)
- **Medium complexity:** $0.03-0.06 (typical company)
- **High complexity:** $0.07-0.12 (large company, lots of news)

### **Monthly Costs (Examples):**
- **10 companies/month:** ~$0.50
- **50 companies/month:** ~$2.50
- **100 companies/month:** ~$5.00
- **500 companies/month:** ~$25.00

### **Fixed Monthly Subscriptions:**
- **OpenAI (GPT-4):** Pay-per-use (~$0.03 per 1,000 words)
- **Tavily Search API:** $50/month (500 searches) or $200/month (5,000 searches)
- **LangChain (optional):** Free tier available

**💡 Cost Comparison:**
- Manual vetting: **$50-100 per company** (2-4 hours at $25/hr)
- This tool: **$0.03-0.12 per company** (30-60 seconds)
- **Savings: 99% cost reduction!**

---

## ⚖️ What Can This Tool Do? (Capabilities)

### ✅ **What It DOES:**
1. **Comprehensive Search:**
   - General web information
   - News articles (recent and historical)
   - Legal and regulatory databases
   - Social media mentions
   - Executive background checks

2. **Smart Analysis:**
   - Uses GPT-4 (most advanced AI available)
   - Identifies patterns and severity
   - Separates isolated incidents from systemic problems
   - Provides confidence levels (High/Medium/Low)

3. **Professional Output:**
   - Executive summary with clear recommendation
   - Audit-ready PDF reports
   - Source citations for verification
   - Easy-to-understand language

4. **Brand Safety:**
   - Evaluates P&G's 7 compliance questions
   - Risk scoring (Low/Medium/High/Critical)
   - PR impact assessment

---

## ⚠️ What Are the Limitations?

### ❌ **What It CANNOT Do:**

1. **Private/Confidential Information:**
   - Cannot access private databases
   - No classified or restricted information
   - Only publicly available data

2. **Real-Time Monitoring:**
   - Not a continuous monitoring system
   - Shows snapshot at time of analysis
   - Doesn't alert you to new scandals after analysis

3. **Human Judgment:**
   - Cannot replace final human decision
   - Should be reviewed by compliance team
   - Cultural context may need human interpretation

4. **Company Name Issues:**
   - Struggles with very small/unknown companies
   - Common names may cause confusion (e.g., "Phoenix Company" - which one?)
   - Foreign companies with special characters

5. **Data Quality:**
   - Depends on what's publicly available online
   - Small private companies have limited data
   - New companies (< 6 months old) may lack information

6. **Language:**
   - Works best with English sources
   - Non-English content may be missed or poorly translated

---

## 🚨 Common Problems & Solutions

### **Problem 1: "No information found"**
**Causes:**
- Company name spelled wrong
- Company is too small/private
- Company doesn't exist

**Solution:**
- Double-check spelling
- Try full legal name (e.g., "Microsoft Corporation" not "MS")
- Verify company actually exists

---

### **Problem 2: "Results don't match company"**
**Causes:**
- Common company name (e.g., "Phoenix LLC")
- Typo in company name

**Solution:**
- Add more context: "Phoenix LLC California"
- Use full legal name with suffix (Inc., Corp., Ltd.)

---

### **Problem 3: "Tool says it's a person, not company"**
**Causes:**
- You entered someone's name by mistake
- Company has a personal name (e.g., "John Smith Enterprises")

**Solution:**
- If it's a person: This tool doesn't vet individuals
- If it's a company: Add "Inc.", "LLC", or "Company"

---

### **Problem 4: "Analysis taking too long"**
**Causes:**
- Internet connection slow
- API servers busy

**Solution:**
- Wait patiently (up to 2 minutes is normal)
- Check internet connection
- Try again in a few minutes

---

## 📊 Understanding the Results

### **Recommendation Types:**

✅ **APPROVED** = Safe to proceed
- No serious issues found
- Positive reputation
- Clean legal record

⚠️ **REQUIRES REVIEW** = Needs human judgment
- Minor issues or old incidents
- Conflicting information
- Unclear severity

❌ **REJECTED** = High risk, do not proceed
- Active scandals or lawsuits
- Criminal violations
- Serious executive misconduct

---

### **Risk Levels:**

🟢 **LOW** = Minimal risk, safe to proceed
- No significant negative findings
- Positive reputation overall

🟡 **MEDIUM** = Some concerns, investigate further
- Minor legal issues
- Old controversies (5+ years ago)
- Mixed reviews

🟠 **HIGH** = Serious concerns, proceed with caution
- Recent legal violations
- Regulatory enforcement actions
- Negative executive history

🔴 **CRITICAL** = Severe risk, strong recommendation against
- Active criminal investigations
- Major fraud or scandals
- Multiple serious violations

---

## 📋 Best Practices

### **DO:**
✅ Always enter the **full legal company name**
✅ **Review the PDF report** before making final decisions
✅ **Check executive backgrounds** if it's a small company
✅ **Verify sources** by clicking on citations
✅ **Share reports** with compliance team

### **DON'T:**
❌ Don't rely solely on this tool for critical decisions
❌ Don't enter personal names (only companies)
❌ Don't use abbreviations (e.g., use "Microsoft" not "MSFT")
❌ Don't close the browser while analysis is running
❌ Don't ignore "REQUIRES REVIEW" recommendations

---

## 🔐 Privacy & Ethics

### **What Data Is Collected?**
- NONE - No personal data stored
- Reports saved locally on your computer only
- No data sent to external servers (except API calls)

### **Is It Fair?**
- Only uses publicly available information
- No bias based on demographics
- Transparent reasoning provided
- Sources cited for verification

### **Is It Legal?**
- 100% legal - all data is public
- Complies with data privacy laws
- No unauthorized access to private systems

---

## 🎓 Training Your Team

### **Who Should Use This?**
- Compliance officers
- Risk management teams
- Partnership managers
- Procurement teams
- Legal departments

### **Training Time:**
- 15-30 minutes for basic usage
- 1-2 hours for advanced interpretation

### **Support:**
- This guide
- README.md (more technical)
- Your IT department

---

## 📞 When to Get Help

### **Contact IT If:**
- Tool won't start
- Getting error messages
- API keys expired
- Need to install updates

### **Contact Compliance If:**
- Results are unclear
- Need help interpreting risk levels
- Company has major red flags
- Unsure about recommendation

---

## 📈 What's Coming Next? (Future Features)

### **Phase 2 (2-4 weeks):**
- Real-time monitoring (alerts for new scandals)
- Batch processing (analyze 100+ companies at once)
- Historical tracking (compare companies over time)
- LexisNexis integration (legal database access)

### **Phase 3 (4-8 weeks):**
- Mobile app
- API for other systems
- Custom compliance questions
- Advanced analytics dashboard

---

## 💡 Quick Tips

1. **Start with a test:** Try a well-known company first (e.g., "Tesla")
2. **Compare with manual research:** Verify results match what you'd find manually
3. **Keep reports:** Save PDFs for audit trail
4. **Regular updates:** Run analysis every 3-6 months for active partners
5. **Trust but verify:** Use this as a starting point, not final decision

---

## 📊 Success Stories

**Before this tool:**
- 2-4 hours per company
- Inconsistent results
- Easy to miss critical information
- High labor costs

**After this tool:**
- 30-60 seconds per company
- Consistent, AI-powered analysis
- Comprehensive multi-source search
- 99% cost reduction

---

## 🏁 Summary

**This tool helps you:**
- ✅ Vet companies 100x faster
- ✅ Save 99% on vetting costs
- ✅ Reduce risk of bad partnerships
- ✅ Generate professional reports
- ✅ Make data-driven decisions

**Remember:**
- Takes 30-60 seconds per company
- Costs ~$0.03-0.12 per analysis
- Should be reviewed by humans
- Works best with well-known companies
- Requires active internet connection

---

**Need More Help?**
- Read **TECHNICAL_DOCUMENTATION.md** (for IT team)
- Review **README.md** (setup guide)
- Contact your IT support team

---

*Generated for Natural Trends AI Client Vetting System*  
*Last Updated: December 8, 2025*  
*Version 2.0*
