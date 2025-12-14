"""
Writing module - Generates methods and results sections using Claude Opus.
"""

import os
import json
import tempfile
from typing import Dict, List, Tuple, Optional
import pandas as pd
import requests
from prompts import PROMPTS
from journal_formats import JOURNAL_FORMATS

class ResultsWriter:
    """Generates publication-ready methods and results sections."""
    
    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model_id = "anthropic/claude-opus-4"
        self.input_cost = 5.00  # per 1M tokens
        self.output_cost = 25.00  # per 1M tokens
    
    def _call_opus(self, messages: List[Dict], temperature: float = 0.3) -> Tuple[str, float]:
        """Call Claude Opus via OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://stats-council.streamlit.app",
            "X-Title": "Stats Council"
        }
        
        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 8192
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # Calculate cost
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            cost = (input_tokens * self.input_cost / 1_000_000) + (output_tokens * self.output_cost / 1_000_000)
            
            return content, cost
            
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    def generate_results_document(self, df: pd.DataFrame, analysis_plan: str,
                                  execution_results: str, figures: List[bytes],
                                  tables: Dict[str, pd.DataFrame], review: str,
                                  journal: str, study_design: str) -> Tuple[str, float]:
        """
        Generate complete methods and results sections.
        
        Returns:
            Tuple of (document_path, cost)
        """
        # Get journal-specific formatting
        journal_format = JOURNAL_FORMATS.get(journal, JOURNAL_FORMATS['Generic'])
        
        # Determine reporting guideline
        reporting_guideline = self._get_reporting_guideline(study_design)
        
        # Prepare table summaries for context
        table_summaries = {}
        for name, table in tables.items():
            table_summaries[name] = table.to_string()[:2000]  # Limit for context
        
        # Generate methods section
        methods_prompt = PROMPTS['methods_writing'].format(
            analysis_plan=analysis_plan,
            study_design=study_design,
            reporting_guideline=reporting_guideline,
            journal_format=json.dumps(journal_format, indent=2),
            sample_size=len(df)
        )
        
        messages = [
            {"role": "system", "content": PROMPTS['writing_system']},
            {"role": "user", "content": methods_prompt}
        ]
        
        methods_text, methods_cost = self._call_opus(messages)
        
        # Generate results section
        results_prompt = PROMPTS['results_writing'].format(
            execution_results=execution_results,
            table_summaries=json.dumps(table_summaries, indent=2),
            num_figures=len(figures),
            journal_format=json.dumps(journal_format, indent=2),
            reporting_guideline=reporting_guideline
        )
        
        messages = [
            {"role": "system", "content": PROMPTS['writing_system']},
            {"role": "user", "content": results_prompt}
        ]
        
        results_text, results_cost = self._call_opus(messages)
        
        # Generate figure legends
        legends_prompt = PROMPTS['figure_legends'].format(
            num_figures=len(figures),
            execution_results=execution_results[:3000],
            journal_format=json.dumps(journal_format, indent=2)
        )
        
        messages = [
            {"role": "system", "content": PROMPTS['writing_system']},
            {"role": "user", "content": legends_prompt}
        ]
        
        legends_text, legends_cost = self._call_opus(messages)
        
        # Generate limitations paragraph
        limitations_prompt = PROMPTS['limitations_writing'].format(
            study_design=study_design,
            review=review,
            analysis_plan=analysis_plan
        )
        
        messages = [
            {"role": "system", "content": PROMPTS['writing_system']},
            {"role": "user", "content": limitations_prompt}
        ]
        
        limitations_text, limitations_cost = self._call_opus(messages)
        
        total_cost = methods_cost + results_cost + legends_cost + limitations_cost
        
        # Create Word document
        doc_path = self._create_word_document(
            methods_text, results_text, legends_text, limitations_text,
            tables, journal_format
        )
        
        return doc_path, total_cost
    
    def _get_reporting_guideline(self, study_design: str) -> str:
        """Get appropriate reporting guideline for study design."""
        guidelines = {
            'Retrospective Cohort': 'STROBE (Strengthening the Reporting of Observational Studies in Epidemiology)',
            'Prospective Cohort': 'STROBE',
            'Case-Control': 'STROBE',
            'Cross-sectional': 'STROBE',
            'RCT': 'CONSORT (Consolidated Standards of Reporting Trials)',
            'Case Series': 'CARE (Case Report Guidelines)',
            'Prediction Model': 'TRIPOD (Transparent Reporting of a Multivariable Prediction Model)',
            'Auto-detect': 'STROBE'
        }
        return guidelines.get(study_design, 'STROBE')
    
    def _create_word_document(self, methods: str, results: str, legends: str,
                             limitations: str, tables: Dict[str, pd.DataFrame],
                             journal_format: dict) -> str:
        """Create Word document using docx library via Node.js."""
        import subprocess
        import json
        
        # Prepare content for the document
        doc_content = {
            'methods': methods,
            'results': results,
            'legends': legends,
            'limitations': limitations,
            'tables': {name: table.to_dict('records') for name, table in tables.items()},
            'journal_format': journal_format
        }
        
        # Save content to temp JSON
        content_path = tempfile.mktemp(suffix='.json')
        with open(content_path, 'w') as f:
            json.dump(doc_content, f)
        
        # Output path
        output_path = tempfile.mktemp(suffix='.docx')
        
        # Create the document using Node.js script
        js_script = self._generate_docx_script(content_path, output_path)
        
        script_path = tempfile.mktemp(suffix='.js')
        with open(script_path, 'w') as f:
            f.write(js_script)
        
        try:
            result = subprocess.run(['node', script_path], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise Exception(f"Document generation failed: {result.stderr}")
            
            return output_path
            
        except Exception as e:
            # Fallback: create simple text file
            fallback_path = tempfile.mktemp(suffix='.txt')
            with open(fallback_path, 'w') as f:
                f.write("METHODS\n\n")
                f.write(methods)
                f.write("\n\nRESULTS\n\n")
                f.write(results)
                f.write("\n\nFIGURE LEGENDS\n\n")
                f.write(legends)
                f.write("\n\nLIMITATIONS\n\n")
                f.write(limitations)
            
            return fallback_path
        
        finally:
            # Cleanup temp files
            for path in [content_path, script_path]:
                if os.path.exists(path):
                    os.remove(path)
    
    def _generate_docx_script(self, content_path: str, output_path: str) -> str:
        """Generate Node.js script for creating Word document."""
        return f'''
const {{ Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, 
         Table, TableRow, TableCell, BorderStyle, WidthType }} = require('docx');
const fs = require('fs');

const content = JSON.parse(fs.readFileSync('{content_path}', 'utf8'));

// Helper to convert markdown-like text to paragraphs
function textToParagraphs(text) {{
    const paragraphs = [];
    const lines = text.split('\\n');
    
    for (const line of lines) {{
        if (line.trim() === '') {{
            continue;
        }}
        
        // Check for headers
        if (line.startsWith('### ')) {{
            paragraphs.push(new Paragraph({{
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({{ text: line.substring(4), bold: true }})]
            }}));
        }} else if (line.startsWith('## ')) {{
            paragraphs.push(new Paragraph({{
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({{ text: line.substring(3), bold: true }})]
            }}));
        }} else if (line.startsWith('# ')) {{
            paragraphs.push(new Paragraph({{
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({{ text: line.substring(2), bold: true }})]
            }}));
        }} else {{
            // Regular paragraph - handle bold text marked with **
            const runs = [];
            const parts = line.split(/\\*\\*([^*]+)\\*\\*/g);
            for (let i = 0; i < parts.length; i++) {{
                if (parts[i]) {{
                    runs.push(new TextRun({{
                        text: parts[i],
                        bold: i % 2 === 1
                    }}));
                }}
            }}
            paragraphs.push(new Paragraph({{ children: runs }}));
        }}
    }}
    
    return paragraphs;
}}

// Create document
const doc = new Document({{
    styles: {{
        default: {{
            document: {{
                run: {{
                    font: "Arial",
                    size: 24  // 12pt
                }}
            }}
        }},
        paragraphStyles: [
            {{
                id: "Heading1",
                name: "Heading 1",
                basedOn: "Normal",
                run: {{ size: 32, bold: true, font: "Arial" }},
                paragraph: {{ spacing: {{ before: 240, after: 120 }} }}
            }},
            {{
                id: "Heading2",
                name: "Heading 2", 
                basedOn: "Normal",
                run: {{ size: 28, bold: true, font: "Arial" }},
                paragraph: {{ spacing: {{ before: 200, after: 100 }} }}
            }}
        ]
    }},
    sections: [{{
        properties: {{
            page: {{
                margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }}
            }}
        }},
        children: [
            // Title
            new Paragraph({{
                alignment: AlignmentType.CENTER,
                children: [new TextRun({{ text: "Statistical Analysis Results", bold: true, size: 36 }})]
            }}),
            new Paragraph({{ children: [] }}),
            
            // Methods section
            new Paragraph({{
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({{ text: "Methods", bold: true }})]
            }}),
            ...textToParagraphs(content.methods),
            
            new Paragraph({{ children: [] }}),
            
            // Results section
            new Paragraph({{
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({{ text: "Results", bold: true }})]
            }}),
            ...textToParagraphs(content.results),
            
            new Paragraph({{ children: [] }}),
            
            // Figure legends
            new Paragraph({{
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({{ text: "Figure Legends", bold: true }})]
            }}),
            ...textToParagraphs(content.legends),
            
            new Paragraph({{ children: [] }}),
            
            // Limitations
            new Paragraph({{
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({{ text: "Limitations", bold: true }})]
            }}),
            ...textToParagraphs(content.limitations)
        ]
    }}]
}});

// Save document
Packer.toBuffer(doc).then(buffer => {{
    fs.writeFileSync('{output_path}', buffer);
    console.log('Document created successfully');
}}).catch(err => {{
    console.error('Error creating document:', err);
    process.exit(1);
}});
'''
