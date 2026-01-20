# Financial Life Planner (Couple Edition)

A maintainable Python-based simulation tool to plan your financial future as a couple. Model different life scenarios including retirement planning, career changes, income variations, and major life events. Includes Israeli income tax and National Insurance calculations.

## Features

- **Interactive Streamlit UI** for easy parameter adjustment
- **Couple support** with separate ages, retirement dates, and pension accounts
- **Israeli tax integration** with 2025/2026 tax brackets and National Insurance
- **Income schedules** to model salary changes over time (raises, part-time transitions)
- **One-time events** for major life events (inheritance, home purchase, education expenses)
- **Feasibility checking** to ensure financial plans are viable
- **Scenario comparison** to evaluate different retirement ages
- **Automatic search** for earliest feasible retirement age
- **Visual charts** showing account balances and cashflows over time

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit app with:

```bash
streamlit run retire_sim/app.py
```

Or use the Python module syntax:

```bash
python -m streamlit run retire_sim/app.py
```

The app will open in your default web browser (typically at http://localhost:8501).

## How to Use

### 1. Single Scenario Simulation

- Adjust parameters in the sidebar (ages, wealth, cashflows, etc.)
- Click "Run Simulation" to see if the retirement age is feasible
- View summary metrics and interactive charts
- Expand "View Detailed Data" to see month-by-month balances

### 2. Find Earliest Retirement

- Set your current situation and constraints
- Click "Find Earliest Retirement" to automatically search for the youngest age at which retirement is feasible
- The tool searches in monthly increments from your current age to pension start age

### 3. Compare Scenarios

- Select number of scenarios to compare (3-10)
- Click "Compare Scenarios" to run simulations at evenly-spaced retirement ages
- View a table showing feasibility and key metrics for each scenario

### 4. Configuration Management

- **Load Defaults**: Reset all parameters to default values
- **Export Config**: Save current parameters to a JSON file
- **Import Config**: Load parameters from a previously saved JSON file

## Parameters Explained

### Shared Parameters

- **End Age**: Planning horizon (e.g., age 95, relative to older person)
- **Real Annual Return (%)**: Expected investment return after inflation (e.g., 5% real means 5% above inflation)
- **Monthly Spending (₪K)**: Combined household monthly spending needs (assumed constant in real terms)
- **Liquid Now (₪K)**: Combined current balance in liquid accounts (stocks, bonds, savings)

### Person-Specific Parameters

Each person has their own set of parameters:

#### Ages
- **Current Age**: Age now (starting point of simulation)
- **Retirement Age**: Age at which to stop working
- **Pension Start Age**: Age at which pension income begins

#### Income & Contributions
- **Gross Income (₪K)**: Monthly gross (pre-tax) income
- **Pension Rate (%)**: Employee pension contribution (mandatory 6% by Israeli law, deducted from paycheck)
- **Hishtalmut**: Fixed at 6% of gross income, capped at ₪1,600/month (goes to liquid savings)

Note: The app automatically calculates:
- Income tax using Israeli progressive tax brackets (2025/2026)
- National Insurance (Bituach Leumi + Bituach Briut) contributions
- **Employer pension contribution** (mandatory 12.5% by Israeli law, NOT deducted from paycheck)
- **Total pension accumulation**: 18.5% (6% employee + 12.5% employer)
- Net income to hand: Gross - Tax - National Insurance - Employee Pension (6%)

#### Pension
- **Pension Now (₪K)**: Current pension account balance
- **Mekadem**: Divisor used to calculate monthly pension income
  - Monthly income = Pension Balance / Mekadem
  - Example: Mekadem of 210 means a ₪1,000,000 pension generates ₪4,762/month
  - Default is 210 (conservative estimate)

## Model Details

### Phases

The simulation runs in three phases for each person:

1. **Work Phase** (current age → retirement age)
   - Earn gross income
   - Pay Israeli income tax and National Insurance
   - Net income (after tax) goes to liquid account
   - Contributions (as % of gross) go to pension and Hishtalmut
   - Both liquid and pension grow with returns
   - Household spending comes from combined liquid assets

2. **Bridge Phase** (retirement age → pension start age)
   - No more income or contributions for that person
   - Spending comes entirely from liquid account
   - Pension continues to grow but cannot be accessed

3. **Post-Pension Phase** (pension start age → end age)
   - Pension generates monthly income (balance / Mekadem)
   - Pension income is taxed just like work income
   - Net pension income helps offset household spending
   - Any remaining spending needs are drawn from liquid
   - Both accounts continue to earn returns

### Tax Treatment

The tool implements Israeli tax and National Insurance calculations:

**Income Tax (Progressive Brackets - Annual):**
- ₪0 - ₪84,120: 10%
- ₪84,120 - ₪120,720: 14%
- ₪120,720 - ₪193,800: 20%
- ₪193,800 - ₪269,280: 31%
- ₪269,280 - ₪560,280: 35%
- ₪560,280 - ₪721,560: 47%
- Above ₪721,560: 50%

**National Insurance (Monthly):**
- Up to ₪7,500/month: 4.27%
- Above ₪7,500/month: 12%
- Cap at ₪50,695/month

**Calculation Method:**
1. Annualize monthly income (× 12)
2. Apply progressive income tax brackets
3. Calculate monthly income tax (÷ 12)
4. Add monthly National Insurance
5. Same tax treatment for work income and pension income

### Feasibility Rules

A scenario is feasible if:
- Liquid account never goes negative during any phase
- Liquid account is non-negative at end age

### Assumptions

- All values are in **real terms** (after inflation)
- Monthly compounding: `r_month = (1 + r_annual)^(1/12) - 1`
- End-of-month timing convention for all cashflows
- Spending is constant in real terms (adjusts with inflation)
- Israeli tax brackets are based on 2025/2026 rates (update annually)

## Example Configuration

Default parameters represent a typical couple scenario:

```json
{
  "age_now": 35.0,
  "retire_age": 50.0,
  "pension_start_age": 60.0,
  "spouse_age_now": 33.0,
  "spouse_retire_age": 50.0,
  "spouse_pension_start_age": 60.0,
  "end_age": 95.0,
  "r_annual_real": 0.05,
  "gross_income_month": 30000.0,
  "pension_rate": 0.06,
  "hishtalmut_rate": 0.025,
  "spouse_gross_income_month": 20000.0,
  "spouse_pension_rate": 0.06,
  "spouse_hishtalmut_rate": 0.025,
  "spend_month": 12000.0,
  "liquid_now": 500000.0,
  "pension_now": 300000.0,
  "spouse_pension_now": 200000.0,
  "mekadem": 210.0,
  "spouse_mekadem": 210.0
}
```

This represents:
- **Person 1**: Age 35, planning to retire at 50
  - Gross income: ₪30K/month
  - Net to hand: ~₪18.2K/month (after tax ₪10K + employee pension ₪1.8K)
  - Pension accumulation: ₪5,550/month (employee ₪1,800 + employer ₪3,750 = 18.5%)
  - Hishtalmut: ₪1,800/month (6% of ₪30K, capped at ₪1,600/month = ₪1,600/month)
  - Current pension: ₪300K
- **Person 2**: Age 33, planning to retire at 50
  - Gross income: ₪20K/month
  - Net to hand: ~₪13.1K/month (after tax ₪5.7K + employee pension ₪1.2K)
  - Pension accumulation: ₪3,700/month (employee ₪1,200 + employer ₪2,500 = 18.5%)
  - Hishtalmut: ₪1,200/month (6% of ₪20K)
  - Current pension: ₪200K
- **Shared**: Combined liquid ₪500K, household spending ₪12K/month
- **Returns**: 5% real annual return
- **Pension rule**: Mekadem 210 (balance / 210 = monthly income)

## Migration Guide

If you have old configuration files from before the tax integration update, they will need to be converted:

### What Changed

**Old Model (Net Income):**
- `net_income_month`: After-tax income
- `contrib_pension_month`: Fixed monthly pension contribution
- `contrib_hishtalmut_month`: Fixed monthly Hishtalmut contribution

**New Model (Gross Income with Tax):**
- `gross_income_month`: Before-tax income
- `pension_rate`: Percentage of gross (e.g., 0.06 for 6%)
- `hishtalmut_rate`: Fixed at 6% of gross, capped at ₪1,600/month (field exists for backward compatibility but calculation uses fixed 6% with cap)

### Conversion Formula

To convert old configs to new format:

1. **Estimate Gross from Net:**
   - If you know your actual gross income, use that
   - Otherwise, estimate: `gross = net / 0.70` (assumes ~30% effective tax rate)
   - More accurate: Use online Israeli tax calculator to find gross that yields your net

2. **Calculate Contribution Rates:**
   - `pension_rate = old_pension_contribution / estimated_gross`
   - `hishtalmut_rate`: Fixed at 6% with ₪1,600/month cap (no need to calculate from old config)

3. **Example:**
   - Old: net = ₪20,000, pension = ₪2,000, hishtalmut = ₪1,000
   - Estimated gross = ₪20,000 / 0.70 = ₪28,571
   - Pension rate = ₪2,000 / ₪28,571 = 7%
   - Hishtalmut: Fixed at 6% (₪1,714) but capped at ₪1,600/month

### Automatic Migration

The app includes automatic migration for old session states. When you load the app with an old configuration, it will automatically convert using the formula above. However, you should verify and adjust the gross income and rates to match your actual situation.

## Extending the Tool

The codebase is structured for easy extension:

- **retire_sim/model.py**: Add new parameters or modify simulation logic
- **retire_sim/search.py**: Add new optimization algorithms
- **retire_sim/plots.py**: Add new visualization types
- **retire_sim/app.py**: Add new UI tabs or features
- **retire_sim/israeli_tax.py**: Update tax brackets annually or add other tax systems

Potential enhancements:
- Additional income streams (rental, side business)
- Social security or other government benefits beyond קצבת זקנה
- Monte Carlo simulation for uncertain returns
- Variable spending in retirement phases
- Inflation-adjusted spending profiles
- Healthcare cost modeling
- Multiple currency support

### Updating Tax Brackets

To update Israeli tax brackets for a new year:

1. Edit `retire_sim/israeli_tax.py`
2. Update `ISRAELI_TAX_BRACKETS` with new thresholds and rates
3. Update `NationalInsuranceConfig` with new NI rates and caps
4. Update the year reference in docstrings and comments
5. Run tests: `pytest tests/test_israeli_tax.py`
6. Update README.md with new brackets

Sources for current rates:
- [PWC Israel Tax Summaries](https://taxsummaries.pwc.com/israel/individual/taxes-on-personal-income)
- [CWS Israel National Insurance](https://www.cwsisrael.com/national-insurance-bituach-leumi-and-health-tax-in-2025/)
- [Bituach Leumi Official](https://www.btl.gov.il/English%20Homepage/Insurance/Ratesandamount/Pages/forSalaried.aspx)

## Project Structure

```
retire_sim/
├── __init__.py          # Package initialization
├── model.py             # Core data model and simulation logic
├── search.py            # Optimization for finding earliest retirement
├── plots.py             # Plotting utilities with Plotly
├── israeli_tax.py       # Israeli tax calculations (2025/2026)
└── app.py               # Streamlit UI application

tests/
└── test_israeli_tax.py  # Unit tests for tax calculations

requirements.txt         # Python dependencies
README.md               # This file
CLAUDE.md              # Original specification
```

## Testing

Run the comprehensive test suite:

```bash
PYTHONPATH=. pytest tests/test_israeli_tax.py -v
```

Or test the core simulation logic programmatically:

```python
from retire_sim.model import Params, simulate
from retire_sim.israeli_tax import calculate_net_from_gross

params = Params()
result = simulate(retire_age=50, params=params)

assert result.ok
assert result.liquid_end >= 0

# Test tax calculations
gross = 30000
net = calculate_net_from_gross(gross)
print(f"Gross: ₪{gross:,}, Net: ₪{net:,.0f}")
```

The test suite includes:
- Income tax bracket calculations
- National Insurance calculations
- Combined tax calculations
- Realistic Israeli salary scenarios

## License

This tool is provided as-is for personal financial planning and educational purposes.

## Disclaimer

This tool provides estimates based on simplified assumptions. It should not be considered professional financial advice. Consult with a qualified financial advisor before making retirement decisions.
