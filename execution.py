"""
Execution module - Handles code execution via OpenAI Responses API.
"""

import os
import json
import base64
import tempfile
from typing import Dict, List, Tuple, Optional
import pandas as pd
from openai import OpenAI

class CodeExecutor:
    """Executes Python code using OpenAI's code interpreter."""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
    
    def execute(self, code: str, df: pd.DataFrame) -> Tuple[str, List[bytes], Dict[str, pd.DataFrame], float]:
        """
        Execute analysis code in OpenAI sandbox.
        
        Args:
            code: Python code to execute
            df: DataFrame to analyze
            
        Returns:
            Tuple of (results_text, figures_list, tables_dict, cost)
        """
        figures = []
        tables = {}
        
        # Save dataframe to temp file for upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f, index=False)
            temp_csv_path = f.name
        
        try:
            # Upload the data file
            with open(temp_csv_path, 'rb') as f:
                file = self.client.files.create(file=f, purpose='assistants')
            
            # Create the analysis prompt
            analysis_prompt = f"""
You are a statistical analyst. Execute the following Python code to analyze the uploaded CSV data.

IMPORTANT INSTRUCTIONS:
1. Load the data from the uploaded CSV file
2. Execute the analysis code provided below
3. Generate all figures as PNG files
4. Generate all tables as CSV files
5. Provide a comprehensive text summary of results

ANALYSIS CODE:
```python
{code}
```

After running the analysis:
1. Save each figure as 'figure_1.png', 'figure_2.png', etc.
2. Save Table 1 as 'table_1.csv'
3. Save any results tables as 'results_table.csv'
4. Print a complete summary of statistical results including:
   - Sample sizes
   - Descriptive statistics
   - Test statistics, p-values, and confidence intervals
   - Effect sizes with interpretation
   - Model diagnostics if applicable

Execute the code now and provide results.
"""
            
            # Call the Responses API with code interpreter
            response = self.client.responses.create(
                model="gpt-4o",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": file.id
                            },
                            {
                                "type": "input_text",
                                "text": analysis_prompt
                            }
                        ]
                    }
                ],
                tools=[{"type": "code_interpreter"}],
                temperature=0.0
            )
            
            # Extract results
            results_text = ""
            
            for item in response.output:
                if item.type == "message":
                    for content in item.content:
                        if hasattr(content, 'text'):
                            results_text += content.text + "\n"
                        elif hasattr(content, 'file'):
                            # Download generated files
                            file_content = self.client.files.content(content.file.file_id)
                            file_bytes = file_content.read()
                            
                            if content.file.filename.endswith('.png'):
                                figures.append(file_bytes)
                            elif content.file.filename.endswith('.csv'):
                                # Parse CSV into DataFrame
                                import io
                                table_df = pd.read_csv(io.BytesIO(file_bytes))
                                table_name = content.file.filename.replace('.csv', '').replace('_', ' ').title()
                                tables[table_name] = table_df
            
            # Calculate cost (approximate)
            # GPT-4o with code interpreter: ~$0.01-0.05 per execution typically
            cost = 0.03  # Rough estimate
            
            # Clean up uploaded file
            self.client.files.delete(file.id)
            
            return results_text, figures, tables, cost
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            return error_msg, [], {}, 0.0
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
    
    def execute_simple(self, code: str, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Simple execution for quick analysis mode - just returns text results.
        """
        # Save dataframe to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f, index=False)
            temp_csv_path = f.name
        
        try:
            with open(temp_csv_path, 'rb') as f:
                file = self.client.files.create(file=f, purpose='assistants')
            
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_file", "file_id": file.id},
                            {"type": "input_text", "text": f"Execute this code and return results:\n```python\n{code}\n```"}
                        ]
                    }
                ],
                tools=[{"type": "code_interpreter"}],
                temperature=0.0
            )
            
            results_text = ""
            for item in response.output:
                if item.type == "message":
                    for content in item.content:
                        if hasattr(content, 'text'):
                            results_text += content.text + "\n"
            
            self.client.files.delete(file.id)
            
            return results_text, 0.01
            
        except Exception as e:
            return f"Error: {str(e)}", 0.0
        finally:
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)


class LocalExecutor:
    """
    Fallback executor that runs code locally.
    Used when OpenAI API is unavailable or for testing.
    """
    
    def __init__(self):
        pass
    
    def execute(self, code: str, df: pd.DataFrame) -> Tuple[str, List[bytes], Dict[str, pd.DataFrame], float]:
        """Execute code locally using exec()."""
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        figures = []
        tables = {}
        
        # Capture stdout
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create execution namespace
        namespace = {
            'pd': pd,
            'df': df.copy(),
            'plt': plt,
            '__builtins__': __builtins__
        }
        
        try:
            # Add common imports to namespace
            exec("""
import numpy as np
import scipy.stats as stats
from scipy import stats as scipy_stats
import warnings
warnings.filterwarnings('ignore')
""", namespace)
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)
            
            results_text = stdout_capture.getvalue()
            
            # Capture any matplotlib figures
            fig_nums = plt.get_fignums()
            for fig_num in fig_nums:
                fig = plt.figure(fig_num)
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                figures.append(buf.read())
                plt.close(fig)
            
            # Check for saved tables in namespace
            for key, value in namespace.items():
                if isinstance(value, pd.DataFrame) and key.startswith('table'):
                    tables[key.replace('_', ' ').title()] = value
            
            return results_text, figures, tables, 0.0
            
        except Exception as e:
            import traceback
            error_msg = f"Execution error:\n{traceback.format_exc()}"
            return error_msg, [], {}, 0.0
