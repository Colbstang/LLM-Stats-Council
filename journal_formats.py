"""
Journal formats module - Contains formatting specifications for different journals.
"""

JOURNAL_FORMATS = {
    'Generic': {
        'name': 'Generic Medical Journal',
        'p_value_format': 'exact',
        'p_value_threshold': 0.05,
        'ci_format': '95% CI: {lower} to {upper}',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 1,
            'sd': 1,
            'effect_size': 2,
            'ci': 2
        },
        'effect_size_required': True,
        'sample_format': 'n = {n} ({pct}%)',
        'table1_format': {
            'continuous_normal': 'mean ± SD',
            'continuous_skewed': 'median (IQR)',
            'categorical': 'n (%)',
            'test_continuous_normal': 't-test',
            'test_continuous_skewed': 'Mann-Whitney U',
            'test_categorical': 'chi-square or Fisher exact'
        },
        'statistical_software_citation': 'Analyses were performed using Python (version X.X) with pandas, scipy, and statsmodels packages.',
        'significance_statement': 'Statistical significance was set at α = 0.05 (two-tailed).',
        'multiple_comparison_note': 'P-values were adjusted for multiple comparisons using the {method} method.'
    },
    
    'JBJS': {
        'name': 'Journal of Bone and Joint Surgery',
        'p_value_format': 'threshold',
        'p_value_threshold': 0.05,
        'ci_format': '(95% CI, {lower}-{upper})',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 1,
            'sd': 1,
            'effect_size': 2,
            'ci': 1
        },
        'effect_size_required': True,
        'sample_format': '{n} patients ({pct}%)',
        'table1_format': {
            'continuous_normal': 'mean ± SD',
            'continuous_skewed': 'median (range)',
            'categorical': 'n (%)',
            'test_continuous_normal': 't-test',
            'test_continuous_skewed': 'Mann-Whitney U',
            'test_categorical': 'chi-square'
        },
        'statistical_software_citation': 'Statistical analysis was performed using Python statistical packages.',
        'significance_statement': 'Significance was set at p < 0.05.',
        'or_rr_required': True,
        'notes': [
            'JBJS requires effect sizes (OR, RR, HR) with confidence intervals',
            'Table 1 should include demographics stratified by exposure/outcome',
            'Power analysis should be mentioned if sample size is limited'
        ]
    },
    
    'CORR': {
        'name': 'Clinical Orthopaedics and Related Research',
        'p_value_format': 'exact',
        'p_value_threshold': 0.05,
        'ci_format': '(95% CI: {lower} to {upper})',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 1,
            'sd': 1,
            'effect_size': 2,
            'ci': 2
        },
        'effect_size_required': True,
        'sample_format': '{n} ({pct}%)',
        'table1_format': {
            'continuous_normal': 'mean ± SD',
            'continuous_skewed': 'median (IQR)',
            'categorical': 'n (%)',
            'test_continuous_normal': 'Student t-test',
            'test_continuous_skewed': 'Mann-Whitney U test',
            'test_categorical': 'chi-square test or Fisher exact test'
        },
        'statistical_software_citation': 'Statistical analyses were conducted using Python (version X.X).',
        'significance_statement': 'A p-value < 0.05 was considered statistically significant.',
        'or_rr_required': True,
        'notes': [
            'CORR emphasizes clinical significance alongside statistical significance',
            'Minimum clinically important difference should be discussed when relevant',
            'Post-hoc power analysis discouraged - report observed effect sizes instead'
        ]
    },
    
    'JAMIA': {
        'name': 'Journal of the American Medical Informatics Association',
        'p_value_format': 'exact',
        'p_value_threshold': 0.05,
        'ci_format': '(95% CI {lower}–{upper})',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 2,
            'sd': 2,
            'effect_size': 3,
            'ci': 3
        },
        'effect_size_required': True,
        'sample_format': 'n = {n} ({pct}%)',
        'table1_format': {
            'continuous_normal': 'mean (SD)',
            'continuous_skewed': 'median [IQR]',
            'categorical': 'n (%)',
            'test_continuous_normal': 't-test',
            'test_continuous_skewed': 'Wilcoxon rank-sum',
            'test_categorical': 'χ² or Fisher exact'
        },
        'statistical_software_citation': 'Analyses were performed in Python X.X using pandas (X.X), scipy (X.X), and statsmodels (X.X).',
        'significance_statement': 'Statistical significance was defined as P < .05.',
        'ml_metrics': {
            'classification': ['AUROC', 'AUPRC', 'sensitivity', 'specificity', 'PPV', 'NPV', 'F1'],
            'regression': ['RMSE', 'MAE', 'R²'],
            'calibration': ['Brier score', 'calibration plot']
        },
        'notes': [
            'JAMIA expects thorough reporting of ML model performance metrics',
            'Cross-validation strategy should be clearly described',
            'Feature importance or model interpretability encouraged',
            'Code/data availability statement required'
        ]
    },
    
    'JOA': {
        'name': 'Journal of Arthroplasty',
        'p_value_format': 'exact',
        'p_value_threshold': 0.05,
        'ci_format': '(95% CI, {lower}-{upper})',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 1,
            'sd': 1,
            'effect_size': 2,
            'ci': 2
        },
        'effect_size_required': True,
        'sample_format': '{n} ({pct}%)',
        'table1_format': {
            'continuous_normal': 'mean ± SD',
            'continuous_skewed': 'median (range)',
            'categorical': 'n (%)',
            'test_continuous_normal': 't-test',
            'test_continuous_skewed': 'Mann-Whitney U',
            'test_categorical': 'chi-square'
        },
        'statistical_software_citation': 'Statistical analysis was performed using Python.',
        'significance_statement': 'P < .05 was considered significant.',
        'survival_analysis': {
            'required_for': ['revision', 'implant failure', 'reoperation'],
            'methods': ['Kaplan-Meier', 'Cox proportional hazards'],
            'reporting': 'Survival estimates with 95% CI at specified time points'
        },
        'notes': [
            'JOA frequently requires survival analysis for revision outcomes',
            'Competing risks should be addressed when relevant',
            'Minimum follow-up requirements should be stated'
        ]
    },
    
    'Spine': {
        'name': 'Spine',
        'p_value_format': 'exact',
        'p_value_threshold': 0.05,
        'ci_format': '(95% CI: {lower}, {upper})',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 1,
            'sd': 1,
            'effect_size': 2,
            'ci': 2
        },
        'effect_size_required': True,
        'sample_format': 'n = {n} ({pct}%)',
        'table1_format': {
            'continuous_normal': 'Mean ± SD',
            'continuous_skewed': 'Median (IQR)',
            'categorical': 'N (%)',
            'test_continuous_normal': 't test',
            'test_continuous_skewed': 'Mann-Whitney U test',
            'test_categorical': 'Chi-square test'
        },
        'statistical_software_citation': 'Statistical analyses were performed using Python software.',
        'significance_statement': 'Statistical significance was set at P < 0.05.'
    },
    
    'AJSM': {
        'name': 'American Journal of Sports Medicine',
        'p_value_format': 'exact',
        'p_value_threshold': 0.05,
        'ci_format': '(95% CI, {lower}-{upper})',
        'decimal_places': {
            'p_value': 3,
            'percentage': 1,
            'mean': 1,
            'sd': 1,
            'effect_size': 2,
            'ci': 2
        },
        'effect_size_required': True,
        'sample_format': '{n} ({pct}%)',
        'table1_format': {
            'continuous_normal': 'mean ± SD',
            'continuous_skewed': 'median (IQR)',
            'categorical': 'n (%)',
            'test_continuous_normal': 't-test',
            'test_continuous_skewed': 'Mann-Whitney U',
            'test_categorical': 'chi-square or Fisher exact'
        },
        'statistical_software_citation': 'Statistical analysis was performed using Python.',
        'significance_statement': 'Significance was set at P < .05.',
        'notes': [
            'AJSM emphasizes functional outcomes and return-to-sport metrics',
            'MCID values should be referenced when available',
            'Subgroup analyses by sport type often expected'
        ]
    }
}


def get_format_string(journal: str, stat_type: str, **kwargs) -> str:
    """
    Get a formatted string for a statistic according to journal conventions.
    
    Args:
        journal: Journal name key
        stat_type: Type of statistic ('p_value', 'ci', 'sample', 'mean_sd', etc.)
        **kwargs: Values to format
        
    Returns:
        Formatted string
    """
    fmt = JOURNAL_FORMATS.get(journal, JOURNAL_FORMATS['Generic'])
    
    if stat_type == 'p_value':
        p = kwargs.get('p', 0)
        decimals = fmt['decimal_places']['p_value']
        if fmt['p_value_format'] == 'threshold':
            if p < 0.001:
                return 'P < .001'
            elif p < fmt['p_value_threshold']:
                return f'P = {p:.{decimals}f}'
            else:
                return f'P = {p:.{decimals}f}'
        else:
            if p < 0.001:
                return 'P < .001'
            return f'P = {p:.{decimals}f}'
    
    elif stat_type == 'ci':
        lower = kwargs.get('lower', 0)
        upper = kwargs.get('upper', 0)
        decimals = fmt['decimal_places']['ci']
        template = fmt['ci_format']
        return template.format(lower=f'{lower:.{decimals}f}', upper=f'{upper:.{decimals}f}')
    
    elif stat_type == 'sample':
        n = kwargs.get('n', 0)
        pct = kwargs.get('pct', 0)
        decimals = fmt['decimal_places']['percentage']
        template = fmt['sample_format']
        return template.format(n=n, pct=f'{pct:.{decimals}f}')
    
    elif stat_type == 'mean_sd':
        mean = kwargs.get('mean', 0)
        sd = kwargs.get('sd', 0)
        decimals = fmt['decimal_places']['mean']
        return f'{mean:.{decimals}f} ± {sd:.{decimals}f}'
    
    elif stat_type == 'effect_size':
        effect = kwargs.get('effect', 0)
        decimals = fmt['decimal_places']['effect_size']
        return f'{effect:.{decimals}f}'
    
    return str(kwargs)


def get_table1_format(journal: str) -> dict:
    """Get Table 1 formatting specifications for a journal."""
    fmt = JOURNAL_FORMATS.get(journal, JOURNAL_FORMATS['Generic'])
    return fmt.get('table1_format', JOURNAL_FORMATS['Generic']['table1_format'])


def get_software_citation(journal: str, packages: dict = None) -> str:
    """
    Get statistical software citation formatted for journal.
    
    Args:
        journal: Journal name key
        packages: Dict of package names to versions
        
    Returns:
        Formatted citation string
    """
    fmt = JOURNAL_FORMATS.get(journal, JOURNAL_FORMATS['Generic'])
    base = fmt.get('statistical_software_citation', '')
    
    if packages:
        import sys
        python_version = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        
        pkg_strings = []
        for name, version in packages.items():
            pkg_strings.append(f'{name} ({version})')
        
        base = base.replace('X.X', python_version)
        if pkg_strings:
            base = base.rstrip('.') + f' with {", ".join(pkg_strings)}.'
    
    return base
