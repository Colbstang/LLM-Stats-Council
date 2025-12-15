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
        Execute analysis code in OpenAI sandbox using Assistants API.

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

            # Create assistant with code interpreter
            assistant = self.client.beta.assistants.create(
                name="Statistical Analyst",
                instructions="You are a statistical analyst. Execute Python code to analyze data and generate results.",
                model="gpt-4o",
                tools=[{"type": "code_interpreter"}]
            )

            # Create the analysis prompt
            analysis_prompt = f"""
Execute the following Python code to analyze the uploaded CSV data.

IMPORTANT INSTRUCTIONS:
1. Load the data from the uploaded file using pandas
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

            # Create thread
            thread = self.client.beta.threads.create()

            # Add message with file attachment
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=analysis_prompt,
                attachments=[
                    {
                        "file_id": file.id,
                        "tools": [{"type": "code_interpreter"}]
                    }
                ]
            )

            # Run the assistant
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
                timeout=300  # 5 minutes timeout
            )

            # Extract results
            results_text = ""

            if run.status == 'completed':
                # Get messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id,
                    order="asc"
                )

                for msg in messages:
                    if msg.role == "assistant":
                        for content in msg.content:
                            if content.type == "text":
                                results_text += content.text.value + "\n"
                            elif content.type == "image_file":
                                # Download image file
                                file_content = self.client.files.content(content.image_file.file_id)
                                figures.append(file_content.read())

                # Check for generated files in run steps
                run_steps = self.client.beta.threads.runs.steps.list(
                    thread_id=thread.id,
                    run_id=run.id
                )

                for step in run_steps:
                    if step.type == "tool_calls":
                        for tool_call in step.step_details.tool_calls:
                            if tool_call.type == "code_interpreter":
                                # Get output files from code interpreter
                                for output in tool_call.code_interpreter.outputs:
                                    if output.type == "image":
                                        file_content = self.client.files.content(output.image.file_id)
                                        figures.append(file_content.read())
                                    # Note: CSV files need to be explicitly saved and referenced
            else:
                results_text = f"Run failed with status: {run.status}"

            # Calculate cost (approximate)
            # GPT-4o with code interpreter: ~$0.01-0.05 per execution typically
            cost = 0.03  # Rough estimate

            # Clean up
            self.client.files.delete(file.id)
            self.client.beta.assistants.delete(assistant.id)

            return results_text, figures, tables, cost

        except Exception as e:
            error_msg = f"Execution error: {str(e)}\n{type(e).__name__}"
            import traceback
            error_msg += f"\n{traceback.format_exc()}"
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

            # Create assistant
            assistant = self.client.beta.assistants.create(
                name="Quick Analyst",
                instructions="Execute Python code and return results.",
                model="gpt-4o-mini",
                tools=[{"type": "code_interpreter"}]
            )

            # Create thread and run
            thread = self.client.beta.threads.create()
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Execute this code and return results:\n```python\n{code}\n```",
                attachments=[{"file_id": file.id, "tools": [{"type": "code_interpreter"}]}]
            )

            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
                timeout=120
            )

            results_text = ""
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id,
                    order="asc"
                )
                for msg in messages:
                    if msg.role == "assistant":
                        for content in msg.content:
                            if content.type == "text":
                                results_text += content.text.value + "\n"

            self.client.files.delete(file.id)
            self.client.beta.assistants.delete(assistant.id)

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
