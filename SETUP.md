# Stats Council - Setup Guide

A comprehensive statistical analysis tool using multiple LLMs for medical research.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Quick Start

### 1. Clone or Download the Repository

```bash
cd /path/to/LLM-Stats-Council
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

**Option A: Using Streamlit Secrets (Recommended for deployment)**

1. Copy the template file:
   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your API keys:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-YOUR-KEY-HERE"
   OPENAI_API_KEY = "sk-YOUR-KEY-HERE"
   ```

**Option B: Using Environment Variables (Recommended for local development)**

```bash
# On macOS/Linux:
export OPENROUTER_API_KEY="sk-or-v1-YOUR-KEY-HERE"
export OPENAI_API_KEY="sk-YOUR-KEY-HERE"

# On Windows (Command Prompt):
set OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
set OPENAI_API_KEY=sk-YOUR-KEY-HERE

# On Windows (PowerShell):
$env:OPENROUTER_API_KEY="sk-or-v1-YOUR-KEY-HERE"
$env:OPENAI_API_KEY="sk-YOUR-KEY-HERE"
```

**Option C: Enter in the App**

You can also enter API keys directly in the sidebar when the app starts.

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
LLM-Stats-Council/
├── app.py                    # Main Streamlit application
├── council.py                # Multi-model orchestration via OpenRouter
├── execution.py              # Code execution via OpenAI Assistants API
├── writing.py                # Results document generation using Claude Opus
├── prompts.py                # All LLM prompts for each stage
├── journal_formats.py        # Journal-specific formatting configs
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit theme configuration
│   └── secrets.toml         # API keys (create from template)
├── SETUP.md                 # This file
└── README.md                # Project overview
```

## How It Works

The app follows a 6-stage pipeline:

1. **Stage 1: Data Audit** (DeepSeek V3)
   - Identifies data quality issues
   - Assesses variable distributions
   - Checks sample size adequacy

2. **Stage 2: Planning Council** (DeepSeek V3 + R1 + Gemini 2.5 Pro → o3 synthesis)
   - Multiple models independently propose analysis plans
   - o3 synthesizes and resolves disagreements
   - User approval required before proceeding

3. **Stage 3: Assumption Verification** (DeepSeek R1)
   - Rigorously checks all statistical assumptions
   - Provides alternative approaches if assumptions violated

4. **Stage 4: Code Generation & Execution** (o3 → OpenAI Sandbox)
   - o3 generates Python analysis code
   - Code is executed in OpenAI's sandboxed environment
   - Figures and tables are generated

5. **Stage 5: Adversarial Review** (DeepSeek V3 + R1)
   - Hostile peer review to find flaws
   - Confidence scoring
   - Issues flagged for user review

6. **Stage 6: Results Writing** (Claude Opus 4.5)
   - Generates publication-ready Methods section
   - Writes Results section
   - Creates figure legends
   - Writes Limitations paragraph
   - Outputs Word document (.docx)

## Model IDs Used

The app uses the following models via OpenRouter:

- **DeepSeek V3**: `deepseek/deepseek-chat-v3-0324`
- **DeepSeek R1**: `deepseek/deepseek-r1`
- **Gemini 2.5 Pro**: `google/gemini-2.5-pro-preview`
- **OpenAI o3**: `openai/o3`
- **Claude Opus 4.5**: `anthropic/claude-opus-4-5`

Code execution uses OpenAI's Assistants API with `gpt-4o` model.

## Cost Estimates

Typical costs per full analysis run:

- Stage 1 (Data Audit): ~$0.05
- Stage 2 (Planning Council): ~$2.00
- Stage 3 (Assumptions): ~$0.10
- Stage 4 (Execution): ~$1.50
- Stage 5 (Review): ~$0.20
- Stage 6 (Writing): ~$4-6

**Total: $8-10 per complete analysis**

## Troubleshooting

### Import Errors

If you get import errors, make sure you've activated your virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### API Key Errors

- Verify your API keys are correctly formatted
- Check that you have credits available on both OpenRouter and OpenAI
- For OpenRouter, ensure you have access to the models you're trying to use

### Model Not Found Errors

If you get "model not found" errors:
1. Check [OpenRouter Models](https://openrouter.ai/models) for current model IDs
2. Update the model IDs in [council.py](council.py#L21-L49)
3. Some models may require special access or credits

### Code Execution Failures

The app uses OpenAI's Assistants API with Code Interpreter. If execution fails:
- Check your OpenAI API key has access to the Assistants API
- Ensure you have sufficient credits
- Review error messages in the execution results

### Word Document Generation Issues

The app uses `python-docx` to create Word documents. If this fails:
- The app will fallback to creating a `.txt` file
- Check that `python-docx` is installed: `pip install python-docx`

## Development

### Running in Development Mode

```bash
# Watch for file changes (auto-reload)
streamlit run app.py --server.runOnSave true
```

### Testing Individual Modules

```python
# Test council module
from council import StatsCouncil
import pandas as pd

council = StatsCouncil("your-openrouter-key")
df = pd.read_csv("test_data.csv")
audit, cost = council.data_audit(df, "Research question", "outcome", "exposure")
print(audit)
```

## Deploying to Streamlit Cloud

1. Push your code to GitHub (without API keys!)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set secrets in the Streamlit Cloud dashboard:
   - `OPENROUTER_API_KEY`
   - `OPENAI_API_KEY`
5. Deploy!

## Support

For issues or questions:
- Check the [README.md](README.md) for project overview
- Review error messages carefully
- Verify API keys and credits
- Check model availability on OpenRouter

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all code follows the existing style and includes appropriate error handling.
