"""
Israeli tax calculation module for retirement simulation.

This module implements Israeli income tax and National Insurance calculations
based on 2025/2026 tax brackets and rates.

Sources:
- PWC Israel Tax Summaries: https://taxsummaries.pwc.com/israel/individual/taxes-on-personal-income
- CWS Israel National Insurance 2025: https://www.cwsisrael.com/national-insurance-bituach-leumi-and-health-tax-in-2025/
- Bituach Leumi Official: https://www.btl.gov.il/English%20Homepage/Insurance/Ratesandamount/Pages/forSalaried.aspx
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TaxBracket:
    """Single tax bracket with threshold and rate."""
    threshold: float  # Annual income threshold in ILS
    rate: float       # Tax rate as decimal (e.g., 0.10 for 10%)
    base_tax: float   # Accumulated tax from lower brackets


# 2025/2026 Israeli Income Tax Brackets (annual amounts in ILS)
ISRAELI_TAX_BRACKETS: List[TaxBracket] = [
    TaxBracket(threshold=0, rate=0.10, base_tax=0),
    TaxBracket(threshold=84_120, rate=0.14, base_tax=8_412),
    TaxBracket(threshold=120_720, rate=0.20, base_tax=13_536),
    TaxBracket(threshold=193_800, rate=0.31, base_tax=28_152),
    TaxBracket(threshold=269_280, rate=0.35, base_tax=51_551),
    TaxBracket(threshold=560_280, rate=0.47, base_tax=153_401),
    TaxBracket(threshold=721_560, rate=0.50, base_tax=229_203),  # 47% + 3% surtax
]


@dataclass
class NationalInsuranceConfig:
    """National Insurance (Bituach Leumi) and Health Insurance (Bituach Briut) configuration.

    Combined rates as of 2025:
    - Low rate (4.27%) = National Insurance (1.04%) + Health Insurance (3.23%)
    - High rate (12.17%) = National Insurance (7.00%) + Health Insurance (5.17%)
    """
    rate_low: float = 0.0427   # Up to 60% of avg wage (₪7,522/month)
    rate_high: float = 0.1217  # Between 60% avg wage and cap
    threshold_low_monthly: float = 7_522  # 60% of avg wage (2025)
    cap_monthly: float = 50_695           # Maximum salary for contributions


NATIONAL_INSURANCE = NationalInsuranceConfig()


def calculate_income_tax(annual_income: float) -> float:
    """
    Calculate Israeli income tax from annual gross income.

    Uses progressive brackets defined in ISRAELI_TAX_BRACKETS.

    Args:
        annual_income: Annual gross income in ILS

    Returns:
        Annual income tax amount in ILS
    """
    if annual_income <= 0:
        return 0.0

    # Find the applicable bracket
    tax = 0.0
    for i, bracket in enumerate(ISRAELI_TAX_BRACKETS):
        if i == len(ISRAELI_TAX_BRACKETS) - 1:
            # Highest bracket
            if annual_income > bracket.threshold:
                tax = bracket.base_tax + (annual_income - bracket.threshold) * bracket.rate
        else:
            next_bracket = ISRAELI_TAX_BRACKETS[i + 1]
            if annual_income <= next_bracket.threshold:
                tax = bracket.base_tax + (annual_income - bracket.threshold) * bracket.rate
                break

    return tax


def calculate_national_insurance(monthly_income: float) -> float:
    """
    Calculate monthly National Insurance (Bituach Leumi + Health Tax).

    Uses simplified two-tier rate system with cap.

    Args:
        monthly_income: Monthly gross income in ILS

    Returns:
        Monthly National Insurance contribution in ILS
    """
    if monthly_income <= 0:
        return 0.0

    # Cap the income at maximum
    capped_income = min(monthly_income, NATIONAL_INSURANCE.cap_monthly)

    # Calculate contribution based on income level
    if capped_income <= NATIONAL_INSURANCE.threshold_low_monthly:
        # Low income rate
        contribution = capped_income * NATIONAL_INSURANCE.rate_low
    else:
        # Low bracket + high bracket
        low_part = NATIONAL_INSURANCE.threshold_low_monthly * NATIONAL_INSURANCE.rate_low
        high_part = (capped_income - NATIONAL_INSURANCE.threshold_low_monthly) * NATIONAL_INSURANCE.rate_high
        contribution = low_part + high_part

    return contribution


def calculate_monthly_tax_from_gross(gross_monthly_income: float) -> float:
    """
    Calculate total monthly tax from gross monthly income.

    Uses monthly approximation:
    1. Annualize the monthly income (× 12)
    2. Apply annual income tax brackets
    3. Add National Insurance (calculated monthly)
    4. Return monthly total (income tax ÷ 12 + NI)

    Args:
        gross_monthly_income: Monthly gross income in ILS

    Returns:
        Total monthly tax (income tax + National Insurance) in ILS
    """
    if gross_monthly_income <= 0:
        return 0.0

    # Annual income for income tax calculation
    annual_income = gross_monthly_income * 12

    # Calculate annual income tax, then convert to monthly
    annual_income_tax = calculate_income_tax(annual_income)
    monthly_income_tax = annual_income_tax / 12

    # Calculate monthly National Insurance
    monthly_ni = calculate_national_insurance(gross_monthly_income)

    # Total monthly tax
    total_monthly_tax = monthly_income_tax + monthly_ni

    return total_monthly_tax


def calculate_net_from_gross(gross_monthly_income: float) -> float:
    """
    Calculate net monthly income from gross monthly income.

    Args:
        gross_monthly_income: Monthly gross income in ILS

    Returns:
        Net monthly income after all taxes in ILS
    """
    total_tax = calculate_monthly_tax_from_gross(gross_monthly_income)
    net_income = gross_monthly_income - total_tax
    return net_income


def get_effective_tax_rate(gross_monthly_income: float) -> float:
    """
    Calculate effective tax rate as percentage.

    Args:
        gross_monthly_income: Monthly gross income in ILS

    Returns:
        Effective tax rate as percentage (0-100)
    """
    if gross_monthly_income <= 0:
        return 0.0

    total_tax = calculate_monthly_tax_from_gross(gross_monthly_income)
    effective_rate = (total_tax / gross_monthly_income) * 100
    return effective_rate


def tax_summary(gross_monthly_income: float) -> dict:
    """
    Get detailed tax breakdown for display/debugging.

    Args:
        gross_monthly_income: Monthly gross income in ILS

    Returns:
        Dictionary with tax breakdown
    """
    annual_income = gross_monthly_income * 12
    annual_income_tax = calculate_income_tax(annual_income)
    monthly_income_tax = annual_income_tax / 12
    monthly_ni = calculate_national_insurance(gross_monthly_income)
    total_tax = monthly_income_tax + monthly_ni
    net_income = gross_monthly_income - total_tax

    return {
        'gross_monthly': gross_monthly_income,
        'gross_annual': annual_income,
        'income_tax_annual': annual_income_tax,
        'income_tax_monthly': monthly_income_tax,
        'national_insurance_monthly': monthly_ni,
        'total_tax_monthly': total_tax,
        'net_monthly': net_income,
        'effective_rate_pct': (total_tax / gross_monthly_income * 100) if gross_monthly_income > 0 else 0
    }
