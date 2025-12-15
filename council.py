"""
Council module - Orchestrates multiple LLMs for statistical planning and verification.
"""

import json
import requests
from typing import Dict, List, Tuple, Optional
import pandas as pd
from prompts import PROMPTS

class StatsCouncil:
    """Multi-LLM council for statistical analysis planning and verification."""
    
    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Model configurations with pricing (per 1M tokens)
        self.models = {
            'deepseek_v3': {
                'id': 'deepseek/deepseek-chat-v3-0324',
                'name': 'DeepSeek V3.2',
                'input_cost': 0.25,
                'output_cost': 0.38
            },
            'deepseek_r1': {
                'id': 'deepseek/deepseek-r1',
                'name': 'DeepSeek R1',
                'input_cost': 0.55,
                'output_cost': 2.19
            },
            'gemini_25': {
                'id': 'google/gemini-2.5-pro-preview',
                'name': 'Gemini 2.5 Pro',
                'input_cost': 2.50,
                'output_cost': 15.00
            },
            'o3': {
                'id': 'openai/o3',
                'name': 'OpenAI o3',
                'input_cost': 2.00,
                'output_cost': 8.00
            },
            'opus': {
                'id': 'anthropic/claude-opus-4-5',
                'name': 'Claude Opus 4.5',
                'input_cost': 5.00,
                'output_cost': 25.00
            }
        }
    
    def _call_model(self, model_key: str, messages: List[Dict], temperature: float = 0.1) -> Tuple[str, float]:
        """Call a model via OpenRouter and return response + cost."""
        model = self.models[model_key]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://stats-council.streamlit.app",
            "X-Title": "Stats Council"
        }
        
        payload = {
            "model": model['id'],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4096
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # Calculate cost
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            cost = (input_tokens * model['input_cost'] / 1_000_000) + (output_tokens * model['output_cost'] / 1_000_000)
            
            return content, cost
        
        except Exception as e:
            return f"Error calling {model['name']}: {str(e)}", 0.0
    
    def _get_data_summary(self, df: pd.DataFrame) -> str:
        """Generate a concise summary of the dataframe for LLM context."""
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Dataset: {len(df)} rows × {len(df.columns)} columns")
        
        # Column info
        summary_parts.append("\nColumns:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_pct = (df[col].isna().sum() / len(df) * 100)
            unique = df[col].nunique()
            
            if dtype in ['int64', 'float64']:
                stats = f"mean={df[col].mean():.2f}, std={df[col].std():.2f}, range=[{df[col].min()}, {df[col].max()}]"
            else:
                top_vals = df[col].value_counts().head(3).to_dict()
                stats = f"top values: {top_vals}"
            
            summary_parts.append(f"  - {col} ({dtype}): {unique} unique, {null_pct:.1f}% null, {stats}")
        
        return "\n".join(summary_parts)
    
    def data_audit(self, df: pd.DataFrame, research_question: str, 
                   outcome_var: str, exposure_var: str) -> Tuple[str, float]:
        """
        Stage 1: Data audit using DeepSeek V3.2
        Returns audit report and cost.
        """
        data_summary = self._get_data_summary(df)
        
        messages = [
            {"role": "system", "content": PROMPTS['data_audit_system']},
            {"role": "user", "content": PROMPTS['data_audit_user'].format(
                data_summary=data_summary,
                research_question=research_question,
                outcome_var=outcome_var,
                exposure_var=exposure_var
            )}
        ]
        
        return self._call_model('deepseek_v3', messages)
    
    def planning_council(self, df: pd.DataFrame, data_audit: str, research_question: str,
                        hypotheses: str, outcome_var: str, exposure_var: str,
                        covariates: str, study_design: str) -> Tuple[Dict, str, str, float]:
        """
        Stage 2: Convene planning council with multiple models.
        Returns individual plans, synthesis, disagreements, and total cost.
        """
        data_summary = self._get_data_summary(df)
        total_cost = 0.0
        plans = {}
        
        # Context for all models
        context = PROMPTS['planning_context'].format(
            data_summary=data_summary,
            data_audit=data_audit,
            research_question=research_question,
            hypotheses=hypotheses,
            outcome_var=outcome_var,
            exposure_var=exposure_var,
            covariates=covariates,
            study_design=study_design
        )
        
        # Get proposals from each council member
        council_models = ['deepseek_v3', 'deepseek_r1', 'gemini_25']
        
        for model_key in council_models:
            messages = [
                {"role": "system", "content": PROMPTS['planning_system']},
                {"role": "user", "content": context}
            ]
            response, cost = self._call_model(model_key, messages)
            plans[self.models[model_key]['name']] = response
            total_cost += cost
        
        # Synthesize with o3
        synthesis_prompt = PROMPTS['synthesis_prompt'].format(
            plans=json.dumps(plans, indent=2),
            research_question=research_question
        )
        
        messages = [
            {"role": "system", "content": PROMPTS['synthesis_system']},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        synthesis_response, synthesis_cost = self._call_model('o3', messages)
        total_cost += synthesis_cost
        
        # Extract disagreements (parse from synthesis response)
        disagreements = self._extract_disagreements(synthesis_response)
        
        return plans, synthesis_response, disagreements, total_cost
    
    def _extract_disagreements(self, synthesis: str) -> Optional[str]:
        """Extract disagreement section from synthesis response."""
        if "DISAGREEMENT" in synthesis.upper() or "CONFLICT" in synthesis.upper():
            # Simple extraction - look for disagreement section
            lines = synthesis.split('\n')
            disagreement_lines = []
            in_disagreement = False
            
            for line in lines:
                if any(word in line.upper() for word in ['DISAGREEMENT', 'CONFLICT', 'DIFFER']):
                    in_disagreement = True
                if in_disagreement:
                    disagreement_lines.append(line)
                    if line.strip() == '' and len(disagreement_lines) > 3:
                        break
            
            if disagreement_lines:
                return '\n'.join(disagreement_lines)
        
        return None
    
    def verify_assumptions(self, df: pd.DataFrame, analysis_plan: str,
                          user_modifications: str) -> Tuple[str, float]:
        """
        Stage 3: Verify statistical assumptions using DeepSeek R1.
        Returns assumption verification report and cost.
        """
        data_summary = self._get_data_summary(df)
        
        messages = [
            {"role": "system", "content": PROMPTS['assumptions_system']},
            {"role": "user", "content": PROMPTS['assumptions_user'].format(
                data_summary=data_summary,
                analysis_plan=analysis_plan,
                user_modifications=user_modifications
            )}
        ]
        
        return self._call_model('deepseek_r1', messages)
    
    def generate_code(self, df: pd.DataFrame, analysis_plan: str, assumptions: str,
                     user_modifications: str, journal_format: str) -> Tuple[str, float]:
        """
        Stage 4a: Generate analysis code using o3.
        Returns Python code and cost.
        """
        data_summary = self._get_data_summary(df)
        column_list = list(df.columns)
        
        messages = [
            {"role": "system", "content": PROMPTS['code_gen_system']},
            {"role": "user", "content": PROMPTS['code_gen_user'].format(
                data_summary=data_summary,
                column_list=column_list,
                analysis_plan=analysis_plan,
                assumptions=assumptions,
                user_modifications=user_modifications,
                journal_format=journal_format
            )}
        ]
        
        response, cost = self._call_model('o3', messages, temperature=0.0)
        
        # Extract code from response
        code = self._extract_code(response)
        
        # Verify code with DeepSeek R1
        verify_messages = [
            {"role": "system", "content": PROMPTS['code_verify_system']},
            {"role": "user", "content": PROMPTS['code_verify_user'].format(
                code=code,
                analysis_plan=analysis_plan
            )}
        ]
        
        verification, verify_cost = self._call_model('deepseek_r1', verify_messages)
        
        # If verification finds issues, note them but proceed
        if "ERROR" in verification.upper() or "BUG" in verification.upper():
            code = f"# VERIFICATION NOTES:\n# {verification[:500]}\n\n{code}"
        
        return code, cost + verify_cost
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from model response."""
        # Look for code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        # If no code blocks, return the whole response
        return response
    
    def adversarial_review(self, analysis_plan: str, code: str, results: str,
                          assumptions: str) -> Tuple[str, Optional[str], str, float]:
        """
        Stage 5: Adversarial review using multiple models.
        Returns review, issues found, confidence level, and cost.
        """
        total_cost = 0.0
        reviews = []
        
        review_context = PROMPTS['adversarial_context'].format(
            analysis_plan=analysis_plan,
            code=code,
            results=results,
            assumptions=assumptions
        )
        
        # Get adversarial reviews from two models
        for model_key in ['deepseek_v3', 'deepseek_r1']:
            messages = [
                {"role": "system", "content": PROMPTS['adversarial_system']},
                {"role": "user", "content": review_context}
            ]
            response, cost = self._call_model(model_key, messages, temperature=0.7)
            reviews.append(response)
            total_cost += cost
        
        # Combine reviews
        combined_review = f"## Review 1 (DeepSeek V3.2)\n{reviews[0]}\n\n## Review 2 (DeepSeek R1)\n{reviews[1]}"
        
        # Determine confidence and extract issues
        issues = self._extract_issues(combined_review)
        confidence = self._determine_confidence(combined_review, issues)
        
        return combined_review, issues, confidence, total_cost
    
    def _extract_issues(self, review: str) -> Optional[str]:
        """Extract issues from adversarial review."""
        issue_keywords = ['ERROR', 'FLAW', 'INCORRECT', 'SHOULD', 'MUST', 'VIOLATION', 'MISSING']
        
        lines = review.split('\n')
        issue_lines = []
        
        for line in lines:
            if any(keyword in line.upper() for keyword in issue_keywords):
                issue_lines.append(line.strip())
        
        if issue_lines:
            return '\n'.join(issue_lines[:10])  # Limit to top 10 issues
        return None
    
    def _determine_confidence(self, review: str, issues: Optional[str]) -> str:
        """Determine confidence level based on review."""
        review_lower = review.lower()
        
        critical_words = ['critical', 'severe', 'major error', 'incorrect', 'invalid']
        warning_words = ['caution', 'consider', 'minor', 'suggest', 'could']
        
        critical_count = sum(1 for word in critical_words if word in review_lower)
        warning_count = sum(1 for word in warning_words if word in review_lower)
        
        if critical_count >= 2 or (issues and len(issues.split('\n')) > 5):
            return 'LOW'
        elif critical_count >= 1 or warning_count >= 3:
            return 'MEDIUM'
        else:
            return 'HIGH'
