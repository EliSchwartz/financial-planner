"""
Core data model and simulation logic for retirement planning.
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

from retire_sim.israeli_tax import calculate_monthly_tax_from_gross


@dataclass
class Params:
    """Parameters for retirement simulation (all in real terms, after inflation)."""

    # Person 1 ages
    age_now: float = 38.0
    retire_age: float = 65.0
    pension_start_age: float = 67.0

    # Person 1 income schedule (optional list of income changes over time)
    # Each entry is a tuple: (age, gross_income_month)
    # Age is in years (same units as age_now, retire_age, etc.)
    # Income remains at that level until next change or retirement
    income_schedule: Optional[list] = None  # List of (age_in_years, gross_income) tuples

    # Person 2 (spouse) ages
    spouse_age_now: float = 36.0
    spouse_retire_age: float = 65.0
    spouse_pension_start_age: float = 67.0

    # Person 2 income schedule (optional list of income changes over time)
    # Age is in years (same units as spouse_age_now, spouse_retire_age, etc.)
    spouse_income_schedule: Optional[list] = None  # List of (age_in_years, gross_income) tuples

    # One-time events (income or expenses) - age is relative to Person 1
    # Each entry is a tuple: (age, amount, description)
    # Positive amount = income (e.g., inheritance, bonus)
    # Negative amount = expense (e.g., home purchase, car, education)
    one_time_events: Optional[list] = None  # List of (age, amount, description) tuples

    # Expense schedule (optional list of expense changes over time) - age is relative to Person 1
    # Each entry is a tuple: (age, monthly_expense)
    # Age is in years (same units as age_now, retire_age, etc.)
    # Expense remains at that level until next change
    expense_schedule: Optional[list] = None  # List of (age_in_years, monthly_expense) tuples

    # Shared
    end_age: float = 95.0  # Planning horizon (relative to older person)

    # Returns (real, annual)
    r_annual_real: float = 0.03  # 3% real annual return (conservative)

    # Person 1 GROSS income and contribution rates
    gross_income_month: float = 18000.0  # Gross monthly income (before tax) - average middle class
    pension_rate: float = 0.06  # 6% employee pension contribution (deducted from salary)
    pension_rate_employer: float = 0.125  # 12.5% employer pension contribution (not deducted)
    hishtalmut_rate_employee: float = 0.025  # 2.5% employee hishtalmut contribution (deducted from salary)
    hishtalmut_rate_employer: float = 0.075  # 7.5% employer hishtalmut contribution (not deducted)
    hishtalmut_salary_cap: float = 15712.0  # Salary cap for hishtalmut tax benefits (2025)

    # Person 2 (spouse) GROSS income and contribution rates
    spouse_gross_income_month: float = 15000.0  # Average middle class income
    spouse_pension_rate: float = 0.06
    spouse_pension_rate_employer: float = 0.125
    spouse_hishtalmut_rate_employee: float = 0.025  # 2.5% employee hishtalmut contribution
    spouse_hishtalmut_rate_employer: float = 0.075  # 7.5% employer hishtalmut contribution
    spouse_hishtalmut_salary_cap: float = 15712.0  # Salary cap for hishtalmut tax benefits (2025)

    # Shared spending
    spend_month: float = 16000.0  # Monthly spending (combined household) - middle class

    # Current wealth
    liquid_now: float = 300000.0  # Combined liquid assets (savings)
    pension_now: float = 400000.0  # Person 1 pension (10-15 years of accumulation)
    spouse_pension_now: float = 350000.0  # Person 2 pension

    # Minimum assets constraint
    min_assets: float = 150000.0  # Minimum assets to maintain (emergency fund)

    # Pension rule: Mekadem (divisor for monthly income calculation)
    # Monthly income = pension_balance_at_start / mekadem
    mekadem: float = 230.0  # Person 1 mekadem
    spouse_mekadem: float = 230.0  # Person 2 mekadem

    # Old age pension (קצבת זקנה) from National Insurance
    old_age_pension_month: float = 2000.0  # Monthly old age pension per person (typically tax-free)
    old_age_pension_start_age: float = 70.0  # Age at which old age pension starts for both people

    # Pension tax exemption
    pension_tax_free_amount: float = 5000.0  # First ₪5,000 of pension income per person is tax-free

    @property
    def r_month(self) -> float:
        """Monthly return rate derived from annual rate."""
        return (1 + self.r_annual_real) ** (1/12) - 1

    @property
    def contrib_pension_month(self) -> float:
        """Person 1 total pension contribution (employee 6% + employer 12.5% = 18.5%)."""
        employee_contrib = self.gross_income_month * self.pension_rate
        employer_contrib = self.gross_income_month * self.pension_rate_employer
        return employee_contrib + employer_contrib

    @property
    def contrib_pension_employee_month(self) -> float:
        """Person 1 employee pension contribution only (6%, deducted from salary)."""
        return self.gross_income_month * self.pension_rate

    @property
    def contrib_hishtalmut_month(self) -> float:
        """Person 1 total hishtalmut contribution (employee 2.5% + employer 7.5% = 10%)."""
        # Calculate on capped salary (₪15,712/month for tax benefits in 2025)
        capped_salary = min(self.gross_income_month, self.hishtalmut_salary_cap)
        employee_contrib = capped_salary * self.hishtalmut_rate_employee
        employer_contrib = capped_salary * self.hishtalmut_rate_employer
        return employee_contrib + employer_contrib

    @property
    def contrib_hishtalmut_employee_month(self) -> float:
        """Person 1 employee hishtalmut contribution only (2.5%, deducted from salary)."""
        capped_salary = min(self.gross_income_month, self.hishtalmut_salary_cap)
        return capped_salary * self.hishtalmut_rate_employee

    @property
    def spouse_contrib_pension_month(self) -> float:
        """Person 2 total pension contribution (employee 6% + employer 12.5% = 18.5%)."""
        employee_contrib = self.spouse_gross_income_month * self.spouse_pension_rate
        employer_contrib = self.spouse_gross_income_month * self.spouse_pension_rate_employer
        return employee_contrib + employer_contrib

    @property
    def spouse_contrib_pension_employee_month(self) -> float:
        """Person 2 employee pension contribution only (6%, deducted from salary)."""
        return self.spouse_gross_income_month * self.spouse_pension_rate

    @property
    def spouse_contrib_hishtalmut_month(self) -> float:
        """Person 2 total hishtalmut contribution (employee 2.5% + employer 7.5% = 10%)."""
        # Calculate on capped salary (₪15,712/month for tax benefits in 2025)
        capped_salary = min(self.spouse_gross_income_month, self.spouse_hishtalmut_salary_cap)
        employee_contrib = capped_salary * self.spouse_hishtalmut_rate_employee
        employer_contrib = capped_salary * self.spouse_hishtalmut_rate_employer
        return employee_contrib + employer_contrib

    @property
    def spouse_contrib_hishtalmut_employee_month(self) -> float:
        """Person 2 employee hishtalmut contribution only (2.5%, deducted from salary)."""
        capped_salary = min(self.spouse_gross_income_month, self.spouse_hishtalmut_salary_cap)
        return capped_salary * self.spouse_hishtalmut_rate_employee


@dataclass
class Result:
    """Result of a retirement simulation."""

    ok: bool
    reason: str
    df: pd.DataFrame

    # Summary metrics for Person 1
    pension_at_start: float = 0.0
    pension_income_month: float = 0.0

    # Summary metrics for Person 2 (spouse)
    spouse_pension_at_start: float = 0.0
    spouse_pension_income_month: float = 0.0

    # Shared metrics
    liquid_end: float = 0.0
    liquid_at_pension_start: float = 0.0  # When first person's pension starts


def get_income_at_age(age: float, base_income: float, income_schedule: Optional[list]) -> float:
    """Get the gross income at a specific age based on the income schedule.

    Args:
        age: Current age (in years, e.g., 42.5 for 42 years 6 months)
        base_income: Base gross income (used if no schedule or before first change)
        income_schedule: Optional list of (age, gross_income) tuples
            where age is in years (same units as age parameter)

    Returns:
        Gross income at the specified age
    """
    if not income_schedule:
        return base_income

    # Find applicable income changes (at or before current age)
    # Note: Both age and schedule ages must be in the same units (years)
    applicable_changes = [(sch_age, income) for sch_age, income in income_schedule if sch_age <= age]
    # Return most recent change, or base income if no changes yet
    return applicable_changes[-1][1] if applicable_changes else base_income


def get_expense_at_age(age: float, base_expense: float, expense_schedule: Optional[list]) -> float:
    """Get the monthly expense at a specific age based on the expense schedule.

    Args:
        age: Current age (in years, e.g., 42.5 for 42 years 6 months)
        base_expense: Base monthly expense (used if no schedule or before first change)
        expense_schedule: Optional list of (age, monthly_expense) tuples
            where age is in years (same units as age parameter)

    Returns:
        Monthly expense at the specified age
    """
    if not expense_schedule:
        return base_expense

    # Find applicable expense changes (at or before current age)
    applicable_changes = [(sch_age, expense) for sch_age, expense in expense_schedule if sch_age <= age]
    # Return most recent change, or base expense if no changes yet
    return applicable_changes[-1][1] if applicable_changes else base_expense


def simulate(retire_age: float, params: Params, spouse_retire_age: Optional[float] = None) -> Result:
    """
    Simulate retirement scenario for couple with potentially different retirement ages.

    Uses end-of-month convention for all cashflows and balance updates.

    Args:
        retire_age: Age at which person 1 retires
        params: Simulation parameters
        spouse_retire_age: Age at which person 2 retires (defaults to params.spouse_retire_age)

    Returns:
        Result object with feasibility, reason, and detailed DataFrame
    """
    if spouse_retire_age is None:
        spouse_retire_age = params.spouse_retire_age

    # Validate inputs
    if retire_age < params.age_now:
        return Result(
            ok=False,
            reason="Person 1 retirement age cannot be before current age",
            df=pd.DataFrame()
        )

    if spouse_retire_age < params.spouse_age_now:
        return Result(
            ok=False,
            reason="Person 2 retirement age cannot be before current age",
            df=pd.DataFrame()
        )

    if retire_age > params.pension_start_age:
        return Result(
            ok=False,
            reason="Person 1 retirement age cannot be after pension start age",
            df=pd.DataFrame()
        )

    if spouse_retire_age > params.spouse_pension_start_age:
        return Result(
            ok=False,
            reason="Person 2 retirement age cannot be after pension start age",
            df=pd.DataFrame()
        )

    # Validate income schedule for Person 1
    if params.income_schedule:
        for schedule_age, schedule_income in params.income_schedule:
            if schedule_age < params.age_now:
                return Result(
                    ok=False,
                    reason=f"Person 1 income schedule age {schedule_age} cannot be before current age {params.age_now}",
                    df=pd.DataFrame()
                )
            if schedule_age >= retire_age:
                return Result(
                    ok=False,
                    reason=f"Person 1 income schedule age {schedule_age} cannot be at or after retirement age {retire_age}",
                    df=pd.DataFrame()
                )
            if schedule_income < 0:
                return Result(
                    ok=False,
                    reason=f"Person 1 income schedule income {schedule_income} cannot be negative",
                    df=pd.DataFrame()
                )

    # Validate income schedule for Person 2
    if params.spouse_income_schedule:
        for schedule_age, schedule_income in params.spouse_income_schedule:
            if schedule_age < params.spouse_age_now:
                return Result(
                    ok=False,
                    reason=f"Person 2 income schedule age {schedule_age} cannot be before current age {params.spouse_age_now}",
                    df=pd.DataFrame()
                )
            if schedule_age >= spouse_retire_age:
                return Result(
                    ok=False,
                    reason=f"Person 2 income schedule age {schedule_age} cannot be at or after retirement age {spouse_retire_age}",
                    df=pd.DataFrame()
                )
            if schedule_income < 0:
                return Result(
                    ok=False,
                    reason=f"Person 2 income schedule income {schedule_income} cannot be negative",
                    df=pd.DataFrame()
                )

    # Validate one-time events
    if params.one_time_events:
        for event_age, amount, description in params.one_time_events:
            if event_age < params.age_now:
                return Result(
                    ok=False,
                    reason=f"One-time event at age {event_age} cannot be before current age {params.age_now}",
                    df=pd.DataFrame()
                )
            if event_age > params.end_age:
                return Result(
                    ok=False,
                    reason=f"One-time event at age {event_age} cannot be after end age {params.end_age}",
                    df=pd.DataFrame()
                )

    # Validate expense schedule
    if params.expense_schedule:
        for schedule_age, schedule_expense in params.expense_schedule:
            if schedule_age < params.age_now:
                return Result(
                    ok=False,
                    reason=f"Expense schedule age {schedule_age} cannot be before current age {params.age_now}",
                    df=pd.DataFrame()
                )
            if schedule_age > params.end_age:
                return Result(
                    ok=False,
                    reason=f"Expense schedule age {schedule_age} cannot be after end age {params.end_age}",
                    df=pd.DataFrame()
                )
            if schedule_expense < 0:
                return Result(
                    ok=False,
                    reason=f"Expense schedule expense {schedule_expense} cannot be negative",
                    df=pd.DataFrame()
                )

    # Determine simulation duration (until older person reaches end_age)
    older_age_now = max(params.age_now, params.spouse_age_now)
    total_months = round((params.end_age - older_age_now) * 12)

    # Initialize tracking
    liquid = params.liquid_now
    pension1 = params.pension_now
    pension2 = params.spouse_pension_now
    r_month = params.r_month

    # Track pension income (starts when each person reaches their pension start age)
    pension1_income_active = False
    pension1_income_month = 0.0
    pension2_income_active = False
    pension2_income_month = 0.0

    # Track old age pension (קצבת זקנה) from National Insurance
    old_age_pension1_active = False
    old_age_pension2_active = False

    liquid_at_first_pension_start = 0.0
    first_pension_started = False

    # Track minimum assets violation
    min_assets_violated = False
    min_assets_violation_reason = ""

    # Track which one-time events have been applied
    applied_events = set()

    records = []

    # Simulate month by month
    for month in range(total_months):
        age1 = params.age_now + month / 12
        age2 = params.spouse_age_now + month / 12

        # Apply returns to all accounts
        liquid *= (1 + r_month)
        pension1 *= (1 + r_month)
        pension2 *= (1 + r_month)

        # Determine income and contributions for each person
        net_income_this_month = 0.0

        # Initialize salary and hishtalmut tracking variables
        salary1_gross = 0.0
        salary1_net = 0.0
        hishtalmut1 = 0.0
        salary2_gross = 0.0
        salary2_net = 0.0
        hishtalmut2 = 0.0

        # Person 1 working?
        person1_working = age1 < retire_age
        if person1_working:
            # Get current gross income based on income schedule
            gross_p1 = get_income_at_age(age1, params.gross_income_month, params.income_schedule)

            # Calculate contributions based on current gross income
            tax_p1 = calculate_monthly_tax_from_gross(gross_p1)

            # Employee pension: 6% of current gross
            employee_pension_p1 = gross_p1 * params.pension_rate

            # Employee hishtalmut: 2.5% of capped salary
            capped_salary_p1 = min(gross_p1, params.hishtalmut_salary_cap)
            employee_hishtalmut_p1 = capped_salary_p1 * params.hishtalmut_rate_employee

            # Net income after tax, employee pension, and employee hishtalmut deduction
            net_p1 = gross_p1 - tax_p1 - employee_pension_p1 - employee_hishtalmut_p1
            net_income_this_month += net_p1

            # Track salary income
            salary1_gross = gross_p1
            salary1_net = net_p1

            # Total hishtalmut (employee 2.5% + employer 7.5% = 10%) on capped salary
            employer_hishtalmut_p1 = capped_salary_p1 * params.hishtalmut_rate_employer
            hishtalmut1 = employee_hishtalmut_p1 + employer_hishtalmut_p1
            liquid += hishtalmut1

            # Total pension (employee 6% + employer 12.5% = 18.5%)
            employer_pension_p1 = gross_p1 * params.pension_rate_employer
            pension1 += employee_pension_p1 + employer_pension_p1

        # Person 2 working?
        person2_working = age2 < spouse_retire_age
        if person2_working:
            # Get current gross income based on income schedule
            gross_p2 = get_income_at_age(age2, params.spouse_gross_income_month, params.spouse_income_schedule)

            # Calculate contributions based on current gross income
            tax_p2 = calculate_monthly_tax_from_gross(gross_p2)

            # Employee pension: 6% of current gross
            employee_pension_p2 = gross_p2 * params.spouse_pension_rate

            # Employee hishtalmut: 2.5% of capped salary
            capped_salary_p2 = min(gross_p2, params.spouse_hishtalmut_salary_cap)
            employee_hishtalmut_p2 = capped_salary_p2 * params.spouse_hishtalmut_rate_employee

            # Net income after tax, employee pension, and employee hishtalmut deduction
            net_p2 = gross_p2 - tax_p2 - employee_pension_p2 - employee_hishtalmut_p2
            net_income_this_month += net_p2

            # Track salary income
            salary2_gross = gross_p2
            salary2_net = net_p2

            # Total hishtalmut (employee 2.5% + employer 7.5% = 10%) on capped salary
            employer_hishtalmut_p2 = capped_salary_p2 * params.spouse_hishtalmut_rate_employer
            hishtalmut2 = employee_hishtalmut_p2 + employer_hishtalmut_p2
            liquid += hishtalmut2

            # Total pension (employee 6% + employer 12.5% = 18.5%)
            employer_pension_p2 = gross_p2 * params.spouse_pension_rate_employer
            pension2 += employee_pension_p2 + employer_pension_p2

        # Add net income to liquid
        liquid += net_income_this_month

        # Apply one-time events (if any) at the appropriate age
        one_time_event_amount = 0.0
        if params.one_time_events:
            for idx, (event_age, amount, description) in enumerate(params.one_time_events):
                # Apply event once when Person 1 reaches the specified age
                if age1 >= event_age and idx not in applied_events:
                    liquid += amount
                    one_time_event_amount += amount
                    applied_events.add(idx)

        # Activate pension income when each person reaches pension start age
        if not pension1_income_active and age1 >= params.pension_start_age:
            pension1_income_active = True
            pension1_income_month = pension1 / params.mekadem
            if not first_pension_started:
                liquid_at_first_pension_start = liquid
                first_pension_started = True

        if not pension2_income_active and age2 >= params.spouse_pension_start_age:
            pension2_income_active = True
            pension2_income_month = pension2 / params.spouse_mekadem
            if not first_pension_started:
                liquid_at_first_pension_start = liquid
                first_pension_started = True

        # Activate old age pension (קצבת זקנה) when each person reaches 70
        if not old_age_pension1_active and age1 >= params.old_age_pension_start_age:
            old_age_pension1_active = True

        if not old_age_pension2_active and age2 >= params.old_age_pension_start_age:
            old_age_pension2_active = True

        # Calculate old age pension amounts first (needed for tax calculation)
        old_age_pension1_amount = params.old_age_pension_month if old_age_pension1_active else 0.0
        old_age_pension2_amount = params.old_age_pension_month if old_age_pension2_active else 0.0
        total_old_age_pension = old_age_pension1_amount + old_age_pension2_amount

        # Calculate total pension income this month (after tax)
        # Tax is applied to pension income, with first ₪5K per person tax-free
        total_pension_income_net = 0.0
        pension_net_p1 = 0.0
        pension_net_p2 = 0.0
        if pension1_income_active:
            pension_gross_p1 = pension1_income_month
            # First ₪5K per person is tax-free
            taxable_pension_p1 = max(0.0, pension_gross_p1 - params.pension_tax_free_amount)
            pension_tax_p1 = calculate_monthly_tax_from_gross(taxable_pension_p1)
            pension_net_p1 = pension_gross_p1 - pension_tax_p1
            total_pension_income_net += pension_net_p1
            pension1 -= pension_gross_p1
        if pension2_income_active:
            pension_gross_p2 = pension2_income_month
            # First ₪5K per person is tax-free
            taxable_pension_p2 = max(0.0, pension_gross_p2 - params.pension_tax_free_amount)
            pension_tax_p2 = calculate_monthly_tax_from_gross(taxable_pension_p2)
            pension_net_p2 = pension_gross_p2 - pension_tax_p2
            total_pension_income_net += pension_net_p2
            pension2 -= pension_gross_p2

        # Add pension income to liquid (it's net income, after tax)
        liquid += total_pension_income_net

        # Add old age pension to liquid (it's net income, typically tax-free)
        liquid += total_old_age_pension

        # Calculate total income from all sources (salary + pension + old age pension)
        total_income_this_month = net_income_this_month + total_pension_income_net + total_old_age_pension

        # Get monthly spending at current age (may change based on expense schedule)
        current_monthly_expense = get_expense_at_age(age1, params.spend_month, params.expense_schedule)

        # Deduct monthly spending from liquid
        liquid -= current_monthly_expense

        # Track if liquid went below minimum assets threshold (but continue simulation)
        if not min_assets_violated and liquid < params.min_assets:
            min_assets_violated = True
            min_assets_violation_reason = f"Assets fell below minimum (₪{params.min_assets/1000:.0f}K) at person 1 age {age1:.1f}, person 2 age {age2:.1f}"

        # Determine phase for display
        if person1_working and person2_working:
            phase = 'both_working'
        elif person1_working or person2_working:
            phase = 'one_working'
        elif not pension1_income_active and not pension2_income_active:
            phase = 'bridge'
        else:
            phase = 'post_pension'

        # Calculate net change to liquid from cash flows (excluding investment returns)
        # Includes: all income sources + hishtalmut + one-time events - spending
        total_income_to_liquid = (net_income_this_month + total_pension_income_net +
                                  total_old_age_pension + hishtalmut1 + hishtalmut2 +
                                  one_time_event_amount)
        liquid_change = total_income_to_liquid - current_monthly_expense

        records.append({
            'month': month,
            'age1': age1,
            'age2': age2,
            'phase': phase,
            'liquid': liquid,
            'pension1': pension1,
            'pension2': pension2,
            # Salary income (Person 1)
            'salary1_gross': salary1_gross,
            'salary1_net': salary1_net,
            'hishtalmut1': hishtalmut1,
            # Salary income (Person 2)
            'salary2_gross': salary2_gross,
            'salary2_net': salary2_net,
            'hishtalmut2': hishtalmut2,
            # Pension income
            'pension1_income': pension1_income_month if pension1_income_active else 0.0,
            'pension2_income': pension2_income_month if pension2_income_active else 0.0,
            'pension1_income_net': pension_net_p1,
            'pension2_income_net': pension_net_p2,
            # One-time events
            'one_time_event': one_time_event_amount,
            'total_pension_income': total_pension_income_net,
            # Old age pension
            'old_age_pension': total_old_age_pension,
            # Spending and net cash flow
            'monthly_expense': current_monthly_expense,
            'liquid_change': liquid_change,
            # Status flags
            'person1_working': person1_working,
            'person2_working': person2_working
        })

    # Create final DataFrame
    df = pd.DataFrame(records)
    liquid_end = liquid

    # Check if there was any minimum assets violation during simulation
    if min_assets_violated:
        return Result(
            ok=False,
            reason=min_assets_violation_reason,
            df=df,
            pension_at_start=pension1,
            pension_income_month=pension1_income_month,
            spouse_pension_at_start=pension2,
            spouse_pension_income_month=pension2_income_month,
            liquid_end=liquid_end,
            liquid_at_pension_start=liquid_at_first_pension_start
        )

    # Check final liquid balance against minimum assets
    if liquid_end < params.min_assets:
        return Result(
            ok=False,
            reason=f"Assets below minimum (₪{params.min_assets/1000:.0f}K) at end age (₪{liquid_end/1000:.0f}K)",
            df=df,
            pension_at_start=pension1,
            pension_income_month=pension1_income_month,
            spouse_pension_at_start=pension2,
            spouse_pension_income_month=pension2_income_month,
            liquid_end=liquid_end,
            liquid_at_pension_start=liquid_at_first_pension_start
        )

    # Success
    return Result(
        ok=True,
        reason="Feasible retirement scenario for both people",
        df=df,
        pension_at_start=pension1 if pension1_income_active else 0.0,
        pension_income_month=pension1_income_month,
        spouse_pension_at_start=pension2 if pension2_income_active else 0.0,
        spouse_pension_income_month=pension2_income_month,
        liquid_end=liquid_end,
        liquid_at_pension_start=liquid_at_first_pension_start
    )
