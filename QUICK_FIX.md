# 🔧 Quick Fix - Installation Issues

## Problem
Some packages are showing permission errors because Streamlit is running and holding files.

## Solution

### Step 1: Stop Streamlit
In the terminal running Streamlit, press `Ctrl + C` to stop it.

### Step 2: Install Missing Packages
Run these commands one by one:

```bash
pip install --upgrade --force-reinstall numpy==1.26.4
pip install --upgrade pydantic==2.12.5
pip install --upgrade langchain==0.1.0 langchain-core==0.1.23
pip install --upgrade openai==1.6.1
```

### Step 3: Verify Installation
```bash
pip list | findstr "tavily langchain openai numpy"
```

You should see:
- tavily-python
- langchain
- langchain-core  
- langchain-openai
- langgraph
- openai
- numpy

### Step 4: Run the App
```bash
streamlit run app.py
```

## Alternative: Restart Fresh

If above doesn't work:

```bash
# 1. Close ALL VS Code terminals
# 2. Close VS Code completely
# 3. Reopen VS Code
# 4. Open new terminal
# 5. Run:

cd "d:\Test natural tread proj"
pip install tavily-python==0.5.0
pip install openai==1.6.1
pip install langchain==0.1.0
pip install langgraph==0.0.20
pip install reportlab==4.0.7
streamlit run app.py
```

## Verification

The app should start at `http://localhost:8502` and you should see the interface without errors.

Test with a company name like "Microsoft" or "Tesla" to verify it's working.
