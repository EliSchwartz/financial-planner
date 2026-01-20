# Israeli Tax Documentation (2025/2026)

This document provides detailed information about the Israeli income tax and National Insurance calculations implemented in the retirement simulation tool.

## Overview

The tool calculates Israeli taxes using the 2025/2026 tax year brackets and rates. The same tax treatment is applied to both:
- Work income (salary)
- Pension income (withdrawals during retirement)

## Income Tax Brackets

Israeli income tax uses a progressive bracket system where higher income is taxed at higher rates.

### Annual Tax Brackets (2025/2026)

| Annual Income (₪) | Marginal Rate | Cumulative Tax on Bracket Top |
|-------------------|---------------|-------------------------------|
| 0 - 84,120 | 10% | ₪8,412 |
| 84,120 - 120,720 | 14% | ₪13,536 |
| 120,720 - 193,800 | 20% | ₪28,152 |
| 193,800 - 269,280 | 31% | ₪51,551 |
| 269,280 - 560,280 | 35% | ₪153,401 |
| 560,280 - 721,560 | 47% | ₪229,203 |
| Above 721,560 | 50% | - |

### How Progressive Brackets Work

Progressive taxation means you only pay the higher rate on income **above** each threshold. For example:

**Example: ₪240,000 annual income**
- First ₪84,120 taxed at 10% = ₪8,412
- Next ₪36,600 (₪84,120 to ₪120,720) taxed at 14% = ₪5,124
- Next ₪73,080 (₪120,720 to ₪193,800) taxed at 20% = ₪14,616
- Remaining ₪46,200 (₪193,800 to ₪240,000) taxed at 31% = ₪14,322
- **Total income tax: ₪42,474** (17.7% effective rate)

## National Insurance + Health Insurance (Bituach Leumi + Bituach Briut)

National Insurance is Israel's social security system, providing pension, disability, and healthcare coverage. Health Insurance is a separate mandatory contribution for healthcare services.

### Monthly Rates (2025)

The combined rates use a **two-tier** system with a **cap**:

| Monthly Income (₪) | Combined Rate | Breakdown | Example Contribution |
|-------------------|---------------|-----------|----------------------|
| Up to ₪7,522 | 4.27% | NI 1.04% + Health 3.23% | ₪7,522 × 4.27% = ₪321 |
| ₪7,522 - ₪50,695 | 12.17% | NI 7.00% + Health 5.17% | On amount above ₪7,522 |
| Above ₪50,695 | 0% | Cap reached | No additional contributions |

### Calculation Examples

**Example 1: ₪20,000 monthly income**
- First ₪7,522 at 4.27% = ₪321
- Remaining ₪12,478 at 12.17% = ₪1,519
- **Total NI+Health: ₪1,840** (9.2% effective rate)

**Example 2: ₪60,000 monthly income (above cap)**
- First ₪7,522 at 4.27% = ₪321
- Next ₪43,173 (up to cap) at 12.17% = ₪5,254
- **Total NI+Health: ₪5,575** (9.3% effective rate, capped)

## Mandatory Pension Contributions

Israeli law requires **mandatory pension contributions** for all salaried employees. This is separate from income tax and National Insurance.

### Contribution Rates (2025)

| Contributor | Rate | Deducted from Paycheck? | Goes to Pension |
|-------------|------|------------------------|-----------------|
| **Employee** | 6% of gross | ✅ Yes | ✅ Yes |
| **Employer** | 12.5% of gross | ❌ No | ✅ Yes |
| **Total** | **18.5% of gross** | 6% deducted | ✅ Yes |

### Important Notes

1. **Employee pays 6%**: This is deducted from your paycheck (similar to tax)
2. **Employer pays 12.5%**: This is NOT deducted from your paycheck (employer cost)
3. **Pension accumulates 18.5%**: Both contributions go to your pension fund
4. **Mandatory by law**: Cannot opt out (unlike Hishtalmut/Keren Hishtalmut)

### Calculation Examples

**Example 1: ₪20,000 gross salary**
- Employee contribution (6%): ₪1,200 (deducted from paycheck)
- Employer contribution (12.5%): ₪2,500 (not deducted)
- **Total pension accumulation: ₪3,700/month (18.5%)**
- **Employee receives: Gross - Tax - NI - ₪1,200**

**Example 2: ₪30,000 gross salary**
- Employee contribution (6%): ₪1,800 (deducted from paycheck)
- Employer contribution (12.5%): ₪3,750 (not deducted)
- **Total pension accumulation: ₪5,550/month (18.5%)**
- **Employee receives: Gross - Tax - NI - ₪1,800**

## Monthly Tax Calculation Method

The tool uses a **monthly approximation** approach:

### Steps

1. **Annualize monthly income**: `annual_income = monthly_income × 12`
2. **Apply progressive income tax brackets** (using annual thresholds)
3. **Calculate monthly income tax**: `monthly_income_tax = annual_income_tax ÷ 12`
4. **Calculate monthly National Insurance** (using monthly rates and cap)
5. **Sum total monthly tax**: `total_tax = monthly_income_tax + monthly_NI`

### Why Monthly Approximation?

This method assumes consistent monthly income throughout the year. It's accurate for:
- Steady salary workers
- Consistent pension withdrawals

It may be less accurate for:
- Highly variable income
- Bonuses concentrated in specific months
- Part-year employment

For retirement planning with consistent monthly cashflows, this approximation is appropriate.

## Complete Tax Calculation Examples

### Example 1: Average Salary (₪12,000/month)

**Annual Income:** ₪144,000

**Income Tax:**
- ₪0 - ₪84,120 at 10% = ₪8,412
- ₪84,120 - ₪120,720 at 14% = ₪5,124
- ₪120,720 - ₪144,000 at 20% = ₪4,656
- **Annual income tax:** ₪18,192
- **Monthly income tax:** ₪18,192 ÷ 12 = ₪1,516

**National Insurance + Health:**
- ₪7,522 at 4.27% = ₪321
- ₪4,478 at 12.17% = ₪545
- **Monthly NI+Health:** ₪866

**Employee Pension (mandatory):**
- 6% of ₪12,000 = ₪720

**Total Monthly Deductions:** ₪1,516 + ₪866 + ₪720 = ₪3,102
**Net to Hand:** ₪12,000 - ₪3,102 = ₪8,898
**Effective Total Deduction Rate:** 25.9%

**Pension Accumulation:**
- Employee: ₪720 (6%)
- Employer: ₪1,500 (12.5%)
- **Total: ₪2,220/month (18.5%)**

### Example 2: High-Tech Salary (₪30,000/month)

**Annual Income:** ₪360,000

**Income Tax:**
- ₪0 - ₪84,120 at 10% = ₪8,412
- ₪84,120 - ₪120,720 at 14% = ₪5,124
- ₪120,720 - ₪193,800 at 20% = ₪14,616
- ₪193,800 - ₪269,280 at 31% = ₪23,399
- ₪269,280 - ₪360,000 at 35% = ₪31,752
- **Annual income tax:** ₪83,303
- **Monthly income tax:** ₪83,303 ÷ 12 = ₪6,942

**National Insurance + Health:**
- ₪7,522 at 4.27% = ₪321
- ₪22,478 at 12.17% = ₪2,736
- **Monthly NI+Health:** ₪3,057

**Employee Pension (mandatory):**
- 6% of ₪30,000 = ₪1,800

**Total Monthly Deductions:** ₪6,942 + ₪3,057 + ₪1,800 = ₪11,799
**Net to Hand:** ₪30,000 - ₪11,799 = ₪18,201
**Effective Total Deduction Rate:** 39.3%

**Pension Accumulation:**
- Employee: ₪1,800 (6%)
- Employer: ₪3,750 (12.5%)
- **Total: ₪5,550/month (18.5%)**

### Example 3: Pension Income (₪15,000/month)

**Annual Income:** ₪180,000

**Income Tax:**
- ₪0 - ₪84,120 at 10% = ₪8,412
- ₪84,120 - ₪120,720 at 14% = ₪5,124
- ₪120,720 - ₪180,000 at 20% = ₪11,856
- **Annual income tax:** ₪25,392
- **Monthly income tax:** ₪25,392 ÷ 12 = ₪2,116

**National Insurance + Health:**
- ₪7,522 at 4.27% = ₪321
- ₪7,478 at 12.17% = ₪910
- **Monthly NI+Health:** ₪1,231

**Employee Pension:**
- **₪0** (No pension contributions during retirement)

**Total Monthly Deductions:** ₪2,116 + ₪1,231 = ₪3,347
**Net Pension to Hand:** ₪15,000 - ₪3,347 = ₪11,653
**Effective Tax Rate:** 22.3%

**Note:** Pension income is taxed the same as work income (income tax + NI), but no 6% pension contribution is deducted since you're retired.

## Implementation Details

### Code Location

All tax calculations are in `retire_sim/israeli_tax.py`:

- `calculate_income_tax(annual_income)` - Progressive income tax
- `calculate_national_insurance(monthly_income)` - NI with two tiers and cap
- `calculate_monthly_tax_from_gross(gross_monthly)` - Combined calculation
- `calculate_net_from_gross(gross_monthly)` - Returns net income
- `get_effective_tax_rate(gross_monthly)` - Returns percentage
- `tax_summary(gross_monthly)` - Detailed breakdown

### Test Coverage

Comprehensive unit tests in `tests/test_israeli_tax.py` cover:
- Zero income edge case
- Each tax bracket boundary
- National Insurance cap
- Realistic salary scenarios (₪10K, ₪20K, ₪35K)
- Consistency of calculations

Run tests with:
```bash
PYTHONPATH=. pytest tests/test_israeli_tax.py -v
```

## Updating for Future Years

To update tax brackets for a new tax year:

### 1. Find Official Rates

Reliable sources:
- **Israel Tax Authority** (רשות המיסים): Official government source
- **PWC Israel**: [Tax Summaries](https://taxsummaries.pwc.com/israel/individual/taxes-on-personal-income)
- **CWS Israel**: [National Insurance Rates](https://www.cwsisrael.com/national-insurance-bituach-leumi-and-health-tax-in-2025/)
- **Bituach Leumi**: [Official NI Rates](https://www.btl.gov.il/English%20Homepage/Insurance/Ratesandamount/Pages/forSalaried.aspx)

### 2. Update Code

Edit `retire_sim/israeli_tax.py`:

**Update income tax brackets:**
```python
ISRAELI_TAX_BRACKETS: List[TaxBracket] = [
    TaxBracket(threshold=0, rate=0.10, base_tax=0),
    TaxBracket(threshold=NEW_THRESHOLD, rate=NEW_RATE, base_tax=NEW_BASE),
    # ... update all brackets
]
```

**Update National Insurance:**
```python
NATIONAL_INSURANCE = NationalInsuranceConfig(
    rate_low=NEW_LOW_RATE,           # e.g., 0.0427
    rate_high=NEW_HIGH_RATE,         # e.g., 0.12
    threshold_low_monthly=NEW_THRESHOLD,  # e.g., 7500
    cap_monthly=NEW_CAP              # e.g., 50695
)
```

### 3. Update Documentation

- Update this file (`docs/tax_documentation.md`)
- Update main `README.md` tax bracket table
- Update year references in docstrings
- Update tax information expander in `app.py`

### 4. Update Tests

Review and update test expectations in `tests/test_israeli_tax.py` if rates changed significantly.

### 5. Run Tests

```bash
PYTHONPATH=. pytest tests/test_israeli_tax.py -v
```

All 18 tests should pass.

## Limitations and Assumptions

### What's Included

✅ Progressive income tax brackets (2025/2026)
✅ National Insurance (Bituach Leumi) - Combined with Health Insurance
✅ Two-tier NI+Health rates with cap
✅ Mandatory pension contributions (18.5% total: 6% employee + 12.5% employer)
✅ Employee pension deduction (6%) from net income
✅ Employer pension contribution (12.5%) added to pension without deduction
✅ Same tax treatment for work income and pension income
✅ No pension contributions during retirement (only taxes)

### What's Not Included

❌ **Tax credits** (נקודות זיכוי) - Would reduce effective tax rate
❌ **Tax exemptions** for certain pension withdrawals
❌ **Health tax** (separate from NI) - Some sources combine these
❌ **Local property tax** (ארנונה)
❌ **Capital gains tax** on investment returns
❌ **Employer contributions** (not part of employee's gross)
❌ **Tax deductions** for donations, mortgage interest, etc.
❌ **Different rates** for self-employed vs salaried

### Impact on Results

The tool may **overestimate** taxes because it doesn't include:
- Tax credits (would reduce tax by ~₪500-1,500/month for typical cases)
- Potential pension withdrawal exemptions

The tool may **underestimate** taxes because it doesn't include:
- Health tax (if not included in NI rates)
- Capital gains on investment growth

For retirement planning, these approximations are reasonable. The tool provides conservative estimates.

## FAQ

### Why use gross income instead of net?

Gross income is the standard way to discuss salary in Israel. It's also more accurate because:
- Tax rates change over time
- Pension/Hishtalmut contributions are based on gross
- Easier to compare scenarios

### Do I need to adjust for bonuses?

The monthly approximation assumes consistent income. If you receive annual bonuses:
- Calculate your total annual gross (salary + bonus)
- Divide by 12 for average monthly gross
- Use this as your `gross_income_month` parameter

### What if my employer pays more to pension?

Israeli law requires **minimum** 12.5% employer contribution. Some employers pay more (e.g., 13.3% or 15%). The tool uses the legal minimum by default:
- **Employee portion**: 6% (mandatory, deducted from paycheck)
- **Employer portion**: 12.5% (mandatory minimum, not deducted)
- **Total**: 18.5%

If your employer contributes more, you can adjust the `pension_rate_employer` parameter in the code or accept that the simulation is slightly conservative (underestimates pension growth).

### Are pension withdrawals really taxed the same?

In Israel, pension income is generally taxed as regular income (income tax + National Insurance). The tool applies the same tax rates with one key difference:

**During work:**
- Pay income tax + NI + **6% employee pension** (deducted)
- Pension accumulates 18.5% (6% employee + 12.5% employer)

**During retirement:**
- Pay income tax + NI + **0% pension** (no pension contributions)
- Pension is drawn down (no accumulation)

**Note:** There may be tax exemptions for certain pension withdrawal amounts in Israel. Consult a tax advisor for your specific situation. The tool uses conservative assumptions (no exemptions).

### How accurate is the monthly approximation?

Very accurate for consistent monthly income (standard salaries, steady pension withdrawals). Less accurate for:
- Highly variable income month-to-month
- Single large withdrawals
- Part-year employment

For long-term retirement planning, the monthly approximation is appropriate.

## Contact and Updates

This tax documentation is current as of **January 2025** for the **2025/2026 tax year**.

Israeli tax rates typically change annually. Check official sources each year and update the code accordingly.

For questions about the implementation:
- Review the source code: `retire_sim/israeli_tax.py`
- Review the tests: `tests/test_israeli_tax.py`
- Consult official Israeli tax resources for legal/tax advice

---

**Disclaimer:** This tool provides estimates for retirement planning purposes. It is not professional tax advice. Consult with a qualified Israeli tax advisor (רואה חשבון) for accurate tax calculations and planning.
