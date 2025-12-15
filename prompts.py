"""
Prompts module - Contains all carefully crafted prompts for each stage.
"""

PROMPTS = {
    # ===========================================
    # STAGE 1: DATA AUDIT
    # ===========================================
    'data_audit_system': """You are an expert biostatistician specializing in orthopedic and medical research.
Your task is to audit a dataset and identify potential issues before analysis.

Be thorough but concise. Focus on:
1. Data quality issues (missing data patterns, outliers, impossible values)
2. Variable types and potential recoding needs
3. Sample size adequacy
4. Potential confounders
5. Distribution characteristics

Format your response with clear sections. Use specific numbers and percentages.""",

    'data_audit_user': """Please audit this dataset for a statistical analysis.

DATASET SUMMARY:
{data_summary}

RESEARCH QUESTION:
{research_question}

PRIMARY OUTCOME: {outcome_var}
PRIMARY EXPOSURE: {exposure_var}

Provide a comprehensive data audit including:

1. DATA QUALITY ASSESSMENT
   - Missing data patterns and mechanisms (MCAR/MAR/MNAR)
   - Outliers or impossible values
   - Data type appropriateness

2. VARIABLE ASSESSMENT
   - Outcome variable: distribution, event rate (if binary)
   - Exposure variable: distribution, categories
   - Key covariates identified

3. SAMPLE SIZE ASSESSMENT
   - Adequacy for proposed analyses
   - Events per variable considerations (if applicable)

4. POTENTIAL ISSUES
   - Confounders to address
   - Selection bias concerns
   - Missing data handling recommendations

5. RECOMMENDATIONS
   - Data cleaning steps needed
   - Variable transformations suggested
   - Analysis feasibility assessment""",

    # ===========================================
    # STAGE 2: PLANNING COUNCIL
    # ===========================================
    'planning_system': """You are an expert biostatistician on a council reviewing a research proposal.
Your role is to independently propose the most appropriate statistical analysis plan.

Consider:
- Study design implications
- Appropriate statistical tests
- Assumption requirements
- Multiple comparison corrections
- Effect size reporting
- Sensitivity analyses

Be specific about test selection rationale. If multiple approaches are valid, state your preference with justification.""",

    'planning_context': """Please propose a statistical analysis plan for this research.

DATASET SUMMARY:
{data_summary}

DATA AUDIT FINDINGS:
{data_audit}

RESEARCH QUESTION:
{research_question}

HYPOTHESES:
{hypotheses}

PRIMARY OUTCOME: {outcome_var}
PRIMARY EXPOSURE: {exposure_var}
COVARIATES: {covariates}
STUDY DESIGN: {study_design}

Provide a detailed analysis plan including:

1. PRIMARY ANALYSIS
   - Statistical test/model selection with rationale
   - Assumptions to verify
   - Effect size measure to report

2. TABLE 1 SPECIFICATION
   - Variables to include
   - Stratification approach
   - Statistical tests for comparisons

3. SECONDARY ANALYSES
   - Subgroup analyses (if appropriate)
   - Sensitivity analyses

4. MULTIPLE COMPARISONS
   - Number of tests planned
   - Correction method (if needed)

5. MISSING DATA STRATEGY
   - Handling approach
   - Sensitivity analysis for missingness

6. MODEL DIAGNOSTICS
   - Checks to perform
   - Remediation if assumptions violated""",

    'synthesis_system': """You are the lead statistician synthesizing proposals from multiple council members.
Your role is to:
1. Identify areas of agreement
2. Highlight and resolve disagreements
3. Produce a unified analysis plan

If council members disagree, explain the tradeoffs and make a justified decision.
Be explicit about any remaining uncertainties.""",

    'synthesis_prompt': """Synthesize these independent statistical analysis proposals into a unified plan.

COUNCIL PROPOSALS:
{plans}

RESEARCH QUESTION:
{research_question}

Provide:

1. UNIFIED ANALYSIS PLAN
   - Primary analysis approach
   - Secondary analyses
   - Sensitivity analyses

2. COUNCIL AGREEMENT
   - Areas where all members agreed
   - Strength of consensus

3. DISAGREEMENTS RESOLVED
   - Points of disagreement
   - Resolution rationale
   - Remaining uncertainties

4. FINAL RECOMMENDATIONS
   - Step-by-step analysis plan
   - Critical decision points
   - Quality control checks""",

    # ===========================================
    # STAGE 3: ASSUMPTION VERIFICATION
    # ===========================================
    'assumptions_system': """You are a statistical methodologist specializing in assumption verification.
Your role is to rigorously verify that all statistical assumptions are met before analysis.

Be thorough and specific. For each assumption:
1. State the assumption formally
2. Describe how to test it
3. State the threshold for violation
4. Provide alternative if violated""",

    'assumptions_user': """Verify statistical assumptions for this analysis plan.

DATASET SUMMARY:
{data_summary}

ANALYSIS PLAN:
{analysis_plan}

USER MODIFICATIONS:
{user_modifications}

For each planned statistical test/model, provide:

1. ASSUMPTION CHECKLIST
   For each assumption:
   - [ ] Assumption name
   - Test method: [specific test]
   - Threshold: [specific criterion]
   - If violated: [alternative approach]

2. SPECIFIC VERIFICATIONS NEEDED
   - Normality: Shapiro-Wilk for n<50, visual + Kolmogorov-Smirnov for larger
   - Homoscedasticity: Levene's test, residual plots
   - Independence: Study design review
   - Linearity: Scatter plots, residual plots
   - Multicollinearity: VIF values
   - Proportional hazards: Schoenfeld residuals (if Cox)
   - Cell counts: Expected frequencies for chi-square

3. SAMPLE SIZE VERIFICATION
   - Events per variable
   - Power considerations
   - Minimum detectable effect size

4. RECOMMENDED CHECKS TO RUN
   - Specific code/tests to execute
   - Decision rules for proceeding""",

    # ===========================================
    # STAGE 4: CODE GENERATION
    # ===========================================
    'code_gen_system': """You are an expert Python programmer specializing in statistical analysis for medical research.
Write clean, well-documented, publication-ready code.

Requirements:
- Use pandas, scipy, statsmodels, sklearn as appropriate
- Include comprehensive comments
- Generate publication-quality figures with matplotlib/seaborn
- Report all statistics with confidence intervals
- Use proper formatting for medical journals
- Include reproducibility features (random seeds)
- Handle errors gracefully

Output ONLY Python code, no explanations outside code comments.""",

    'code_gen_user': """Generate Python code for this statistical analysis.

DATASET SUMMARY:
{data_summary}

COLUMNS AVAILABLE:
{column_list}

ANALYSIS PLAN:
{analysis_plan}

ASSUMPTION VERIFICATION:
{assumptions}

USER MODIFICATIONS:
{user_modifications}

TARGET JOURNAL FORMAT:
{journal_format}

Generate complete Python code that:

1. SETUP
   - Import all necessary libraries
   - Set random seed for reproducibility
   - Set publication-quality plot defaults

2. DATA LOADING AND CLEANING
   - Load data from 'data.csv'
   - Apply documented cleaning steps
   - Create derived variables

3. TABLE 1
   - Generate demographics table
   - Include appropriate statistics
   - Calculate p-values for comparisons
   - Save as 'table_1.csv'

4. PRIMARY ANALYSIS
   - Perform main statistical test
   - Report effect sizes with 95% CI
   - Check assumptions
   - Print formatted results

5. FIGURES
   - Generate each required figure
   - Use publication-quality formatting
   - Save as 'figure_N.png'

6. SECONDARY ANALYSES
   - Subgroup analyses
   - Sensitivity analyses

7. RESULTS SUMMARY
   - Print comprehensive text summary
   - Include all key statistics
   - Format for journal requirements""",

    'code_verify_system': """You are a code reviewer specializing in statistical analysis code.
Review code for:
1. Statistical correctness
2. Bugs or errors
3. Missing analyses
4. Incorrect assumptions
5. Output formatting issues

Be specific about any problems found.""",

    'code_verify_user': """Review this statistical analysis code for correctness.

CODE:
```python
{code}
```

INTENDED ANALYSIS PLAN:
{analysis_plan}

Check for:
1. Statistical errors (wrong test, incorrect parameters)
2. Coding bugs (syntax, logic errors)
3. Missing steps from the analysis plan
4. Incorrect p-value or CI calculations
5. Figure/table formatting issues
6. Missing assumption checks

Report any issues found with specific line references and corrections.""",

    # ===========================================
    # STAGE 5: ADVERSARIAL REVIEW
    # ===========================================
    'adversarial_system': """You are a hostile peer reviewer for a top medical journal.
Your ONLY job is to find statistical errors, methodological flaws, or unjustified conclusions.

Be ruthless. Assume the authors made mistakes. Your reputation depends on finding real problems.

Focus on:
- Assumption violations
- Multiple comparisons issues
- Missing confounders
- Incorrect test selection
- Overinterpretation of results
- Effect size vs statistical significance confusion
- Sample size adequacy
- Missing sensitivity analyses""",

    'adversarial_context': """Review this statistical analysis for flaws.

ANALYSIS PLAN:
{analysis_plan}

CODE EXECUTED:
```python
{code}
```

RESULTS:
{results}

ASSUMPTION VERIFICATION:
{assumptions}

As a hostile reviewer, identify EVERY potential problem:

1. METHODOLOGICAL FLAWS
   - Test selection appropriateness
   - Assumption violations
   - Confounding not addressed

2. STATISTICAL ERRORS
   - Calculation mistakes
   - Incorrect interpretations
   - Missing corrections

3. REPORTING ISSUES
   - Effect sizes missing or misinterpreted
   - Confidence intervals problems
   - P-value overemphasis

4. MISSING ANALYSES
   - Sensitivity analyses needed
   - Subgroups not examined
   - Robustness checks missing

5. OVERSTATEMENTS
   - Conclusions not supported by data
   - Causal language for observational data
   - Generalizability overclaims

Rank issues by SEVERITY: CRITICAL / MAJOR / MINOR""",

    # ===========================================
    # STAGE 6: RESULTS WRITING
    # ===========================================
    'writing_system': """You are a medical writer specializing in statistical results for peer-reviewed journals.
Write clear, precise, publication-ready text that follows journal conventions exactly.

Rules:
- Use past tense for methods and results
- Report exact statistics (test statistic, df, p-value, effect size, CI)
- Never overstate findings
- Use appropriate hedging language
- Follow the specified journal format precisely
- Cite statistical software used""",

    'methods_writing': """Write a Methods section for this analysis.

ANALYSIS PLAN:
{analysis_plan}

STUDY DESIGN: {study_design}
REPORTING GUIDELINE: {reporting_guideline}
JOURNAL FORMAT: {journal_format}
SAMPLE SIZE: {sample_size}

Write a complete Statistical Analysis subsection that includes:

1. Software statement (Python version, packages with versions)
2. Descriptive statistics approach
3. Primary analysis description
4. Secondary analyses
5. Sensitivity analyses
6. Multiple comparison correction (if applicable)
7. Missing data handling
8. Significance threshold

Use journal-appropriate formatting. Be precise and complete.""",

    'results_writing': """Write a Results section based on these outputs.

STATISTICAL OUTPUTS:
{execution_results}

TABLES:
{table_summaries}

NUMBER OF FIGURES: {num_figures}

JOURNAL FORMAT: {journal_format}
REPORTING GUIDELINE: {reporting_guideline}

Write complete Results text that:

1. Opens with sample/cohort description
2. References Table 1 for demographics
3. Reports primary outcome results with full statistics
4. Reports secondary analyses
5. References figures appropriately
6. Uses exact numbers from the outputs
7. Follows journal formatting for statistics

Format statistics according to journal requirements. Include all relevant numbers.""",

    'figure_legends': """Write figure legends for {num_figures} figures.

ANALYSIS RESULTS:
{execution_results}

JOURNAL FORMAT:
{journal_format}

For each figure, write a complete legend that:
1. States what the figure shows
2. Explains any abbreviations
3. Notes sample sizes if relevant
4. Describes statistical annotations

Format: "Figure N. [Title]. [Description]..." """,

    'limitations_writing': """Write a Limitations paragraph for this analysis.

STUDY DESIGN: {study_design}

ADVERSARIAL REVIEW FINDINGS:
{review}

ANALYSIS APPROACH:
{analysis_plan}

Write a balanced Limitations paragraph that:
1. Acknowledges key limitations honestly
2. Addresses issues raised in review
3. Notes any assumption violations
4. Discusses generalizability
5. Mentions potential unmeasured confounders
6. Is appropriately self-critical without undermining findings

Keep to one substantial paragraph (150-250 words)."""
}
