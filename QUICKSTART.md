# Stats Council - Quick Start

## 🚀 Get Started in 5 Minutes

### 1. Setup Virtual Environment

```bash
# Navigate to project directory
cd /Users/colbygrames/LLM-Stats-Council

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

**Option A: Using secrets file (Recommended)**
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your keys
```

**Option B: Environment variables**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENAI_API_KEY="sk-..."
```

**Option C: Enter in app**
Just run the app and enter keys in the sidebar.

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📊 Using the App

### Upload Your Data (Tab 1: Input)
1. Upload CSV file (deidentified medical research data)
2. Enter research question
3. Specify outcome variable
4. Specify exposure/predictor variable
5. List covariates

### Run the Analysis (Tab 2: Analysis)

**Stage 1: Data Audit** (~$0.05)
- Automatic data quality assessment
- Missing data analysis
- Sample size check

**Stage 2: Planning Council** (~$2.00)
- Multi-model deliberation
- Statistical plan synthesis
- User approval required

**Stage 3: Assumption Verification** (~$0.10)
- Check all statistical assumptions
- Alternative approaches if violated

**Stage 4: Code Generation & Execution** (~$1.50)
- AI generates Python code
- Executes in OpenAI sandbox
- Generates figures and tables

**Stage 5: Adversarial Review** (~$0.20)
- Hostile peer review
- Identifies flaws
- Confidence scoring

**Stage 6: Results Writing** (~$4-6)
- Generates Methods section
- Writes Results section
- Creates Word document (.docx)

### Download Results (Tab 4: Downloads)
- Methods & Results (Word document)
- Analysis Script (Python)
- Tables (CSV)
- Figures (PNG)
- Audit Trail (JSON)

---

## 💰 Cost Estimate

**Total per analysis: $8-10**

Monitor costs in the sidebar under "Cost Tracker"

---

## 🔧 Troubleshooting

### Can't activate virtual environment?
```bash
# Make sure you're in the project directory
pwd
# Should show: /Users/colbygrames/LLM-Stats-Council
```

### Import errors?
```bash
# Ensure virtual environment is activated
which python
# Should show: .../venv/bin/python
```

### API key errors?
- Verify keys are correct (no extra spaces)
- Check you have credits on OpenRouter and OpenAI
- Try entering keys directly in the app sidebar

### Model not found?
- Check [OpenRouter Models](https://openrouter.ai/models) for availability
- Some models (like o3) may have limited access
- Verify your OpenRouter account has access

---

## 📚 Need More Help?

- Full setup guide: [SETUP.md](SETUP.md)
- Complete changelog: [CHANGES.md](CHANGES.md)
- Project overview: [README.md](README.md)

---

## ✅ Ready to Go!

You're all set! Upload your data and let the AI council analyze it.

**Key Features:**
- Multi-LLM verification for maximum accuracy
- Adversarial review catches errors
- Publication-ready output
- Complete audit trail
- Journal-specific formatting

Good luck with your research! 🎓
