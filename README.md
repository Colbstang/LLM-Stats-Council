# 📊 Stats Council

**Multi-LLM Statistical Analysis Suite for Medical Research**

Stats Council is an automated statistical analysis pipeline that uses multiple large language models to plan, execute, verify, and write up statistical analyses for medical research. It's specifically optimized for orthopedic and medical informatics research.

## Features

- **Multi-Model Council**: Uses DeepSeek V3.2, DeepSeek R1, Gemini 2.5 Pro, o3, and Claude Opus 4.5 for different stages
- **Human-in-the-Loop**: Pause points at each stage for your review and approval
- **Adversarial Review**: Automated statistical review to catch errors before publication
- **Journal-Specific Formatting**: Pre-configured formats for JBJS, CORR, JAMIA, JOA, and more
- **Publication-Ready Output**: Generates Word documents with Methods and Results sections
- **Full Audit Trail**: Tracks all decisions, costs, and model outputs

## Cost

Typical analysis run: **$10-15**

| Stage | Models Used | Est. Cost |
|-------|-------------|-----------|
| Data Audit | DeepSeek V3.2 | ~$0.05 |
| Planning Council | DeepSeek V3.2 + R1 + Gemini 2.5 + o3 | ~$2.00 |
| Assumption Verification | DeepSeek R1 | ~$0.10 |
| Code Generation + Execution | o3 + OpenAI Sandbox | ~$1.50 |
| Adversarial Review | DeepSeek V3.2 + R1 | ~$0.20 |
| Results Writing | Claude Opus 4.5 | ~$4-6 |

## Prerequisites

1. **OpenRouter API Key** - For multi-model access
   - Sign up at [openrouter.ai](https://openrouter.ai)
   - Add credits to your account
   - Generate an API key

2. **OpenAI API Key** - For code execution sandbox
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Add credits to your account
   - Generate an API key

## Quick Start (Local)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/stats-council.git
cd stats-council

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your API keys

# Run the app
streamlit run app.py
```

## Deployment to Streamlit Cloud (Recommended)

### Step 1: Upload to GitHub

1. Create a new repository on GitHub
2. Upload all files from this folder to the repository
3. Make sure NOT to upload `.streamlit/secrets.toml` (it's in .gitignore)

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set "Main file path" to `app.py`
6. Click "Advanced settings"
7. In the "Secrets" section, add:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-your-actual-key"
   OPENAI_API_KEY = "sk-your-actual-key"
   ```
8. Click "Deploy"

Your app will be live at `https://your-app-name.streamlit.app` in ~2-3 minutes.

## Usage

### 1. Input Tab

- **Upload CSV**: Upload your deidentified dataset
- **Research Question**: Describe what you're investigating
- **Variables**: Specify outcome, exposure, and covariates
- **Study Design**: Select or let the system auto-detect

### 2. Analysis Tab

The pipeline proceeds through 6 stages:

1. **Data Audit**: Reviews your data for quality issues
2. **Planning Council**: Multiple models propose analysis approaches
3. **Assumption Verification**: Checks statistical assumptions
4. **Code Execution**: Generates and runs Python code
5. **Adversarial Review**: Checks for statistical flaws
6. **Results Writing**: Generates publication-ready text

At each stage, you can:
- ✅ Approve and continue
- 🔄 Re-run with different parameters
- ✏️ Add manual modifications

### 3. Results Tab

Preview all outputs:
- Statistical results
- Figures
- Tables

### 4. Downloads Tab

Download your outputs:
- 📄 Methods & Results (Word document)
- 🐍 Analysis script (Python)
- 📊 Tables (CSV)
- 📈 Figures (PNG)
- 📋 Audit trail (JSON)

## Supported Study Designs

- Retrospective Cohort (STROBE)
- Prospective Cohort (STROBE)
- Case-Control (STROBE)
- Cross-sectional (STROBE)
- RCT (CONSORT)
- Case Series (CARE)
- Prediction Model (TRIPOD)

## Supported Journals

- Generic (default)
- JBJS (Journal of Bone and Joint Surgery)
- CORR (Clinical Orthopaedics and Related Research)
- JAMIA (Journal of the American Medical Informatics Association)
- JOA (Journal of Arthroplasty)
- Spine
- AJSM (American Journal of Sports Medicine)

## Project Structure

```
stats_council/
├── app.py                 # Main Streamlit application
├── council.py             # Multi-model orchestration
├── execution.py           # Code execution via OpenAI
├── writing.py             # Results document generation
├── prompts.py             # All LLM prompts
├── journal_formats.py     # Journal-specific formatting
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .streamlit/
    ├── config.toml        # Streamlit configuration
    └── secrets.toml.example  # API key template
```

## Adding New Journals

Edit `journal_formats.py` to add new journal configurations:

```python
'NEW_JOURNAL': {
    'name': 'Full Journal Name',
    'p_value_format': 'exact',  # or 'threshold'
    'ci_format': '(95% CI: {lower} to {upper})',
    # ... other settings
}
```

## Troubleshooting

### "API key invalid"
- Check that your keys are correctly entered in sidebar or secrets
- Ensure you have credits in your OpenRouter/OpenAI accounts

### "Model not found"
- Some models may be temporarily unavailable on OpenRouter
- The app will use fallback models when available

### "Execution failed"
- Check the generated code in the expandable section
- The code may need manual adjustment for unusual data structures

### "Document generation failed"
- Ensure Node.js is installed (for Word document generation)
- Falls back to text file if docx generation fails

## Security Notes

- Never commit `.streamlit/secrets.toml` to git
- API keys entered in the sidebar are stored in session state only
- Uploaded data is not persisted after session ends
- Consider adding password protection for shared deployments

## Contributing

Contributions welcome! Areas for improvement:
- Additional journal formats
- More statistical tests/models
- Better error handling
- UI improvements

## License

MIT License - See LICENSE file

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io)
- [OpenRouter](https://openrouter.ai)
- [OpenAI](https://openai.com)
- DeepSeek, Google Gemini, Anthropic Claude
