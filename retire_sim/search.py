"""
Solver for finding earliest feasible retirement age.
"""

from typing import Optional, Tuple
from retire_sim.model import Params, Result, simulate


def find_earliest_retirement(
    params: Params,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None,
    spouse_retire_age: Optional[float] = None,
    step_months: int = 1
) -> Tuple[Optional[float], Optional[Result]]:
    """
    Find the earliest feasible retirement age for Person 1.

    Args:
        params: Simulation parameters
        min_age: Minimum retirement age to consider for Person 1 (defaults to age_now)
        max_age: Maximum retirement age to consider for Person 1 (defaults to pension_start_age)
        spouse_retire_age: Person 2 retirement age (defaults to params.spouse_retire_age)
        step_months: Step size in months for the search (default 1 month)

    Returns:
        Tuple of (earliest_retirement_age, result) or (None, None) if none feasible
    """
    if min_age is None:
        min_age = params.age_now

    if max_age is None:
        max_age = params.pension_start_age

    if spouse_retire_age is None:
        spouse_retire_age = params.spouse_retire_age

    # Validate bounds
    if min_age < params.age_now:
        min_age = params.age_now

    if max_age > params.pension_start_age:
        max_age = params.pension_start_age

    if min_age > max_age:
        return None, None

    # Search in monthly steps
    total_months = round((max_age - min_age) * 12)
    for m in range(0, total_months + 1, step_months):
        retire_age = min_age + m / 12

        # Don't exceed max_age
        if retire_age > max_age:
            retire_age = max_age

        result = simulate(retire_age, params, spouse_retire_age)

        if result.ok:
            return retire_age, result

        # If we've reached max_age, stop
        if retire_age >= max_age:
            break

    # No feasible retirement age found
    return None, None


def find_earliest_joint_retirement(
    params: Params,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None,
    step_months: int = 1
) -> Tuple[Optional[float], Optional[float], Optional[Result]]:
    """
    Find the earliest age at which BOTH people can retire together.

    Args:
        params: Simulation parameters
        min_age: Minimum retirement age to consider (defaults to max of current ages)
        max_age: Maximum retirement age to consider (defaults to min of pension start ages)
        step_months: Step size in months for the search (default 1 month)

    Returns:
        Tuple of (person1_retire_age, person2_retire_age, result) or (None, None, None) if none feasible
    """
    if min_age is None:
        min_age = max(params.age_now, params.spouse_age_now)

    if max_age is None:
        max_age = min(params.pension_start_age, params.spouse_pension_start_age)

    # Validate bounds
    if min_age < max(params.age_now, params.spouse_age_now):
        min_age = max(params.age_now, params.spouse_age_now)

    if max_age > min(params.pension_start_age, params.spouse_pension_start_age):
        max_age = min(params.pension_start_age, params.spouse_pension_start_age)

    if min_age > max_age:
        return None, None, None

    # Calculate the age for each person when they both retire at same time
    age_diff = params.age_now - params.spouse_age_now

    # Search in monthly steps
    total_months = round((max_age - min_age) * 12)
    for m in range(0, total_months + 1, step_months):
        retire_age1 = min_age + m / 12
        retire_age2 = retire_age1 - age_diff

        # Check bounds
        if retire_age1 > params.pension_start_age or retire_age2 > params.spouse_pension_start_age:
            break
        if retire_age1 < params.age_now or retire_age2 < params.spouse_age_now:
            continue

        result = simulate(retire_age1, params, retire_age2)

        if result.ok:
            return retire_age1, retire_age2, result

    # No feasible joint retirement age found
    return None, None, None


def compare_scenarios(
    params: Params,
    retirement_ages: list[float],
    spouse_retire_age: Optional[float] = None
) -> list[dict]:
    """
    Compare multiple retirement age scenarios for Person 1.

    Args:
        params: Simulation parameters
        retirement_ages: List of retirement ages for Person 1 to test
        spouse_retire_age: Person 2 retirement age (defaults to params.spouse_retire_age)

    Returns:
        List of dictionaries with scenario results
    """
    if spouse_retire_age is None:
        spouse_retire_age = params.spouse_retire_age

    scenarios = []

    for retire_age in retirement_ages:
        result = simulate(retire_age, params, spouse_retire_age)

        scenarios.append({
            'retirement_age': retire_age,
            'spouse_retirement_age': spouse_retire_age,
            'feasible': result.ok,
            'reason': result.reason,
            'liquid_at_pension_start': result.liquid_at_pension_start,
            'pension_at_start': result.pension_at_start,
            'pension_income_month': result.pension_income_month,
            'spouse_pension_at_start': result.spouse_pension_at_start,
            'spouse_pension_income_month': result.spouse_pension_income_month,
            'liquid_end': result.liquid_end,
            'working_years': retire_age - params.age_now,
            'spouse_working_years': spouse_retire_age - params.spouse_age_now
        })

    return scenarios


def find_max_monthly_expense(
    params: Params,
    target_end_assets: float,
    retire_age: Optional[float] = None,
    spouse_retire_age: Optional[float] = None,
    tolerance: float = 1000.0,
    max_iterations: int = 50
) -> Tuple[Optional[float], Optional[Result]]:
    """
    Find the maximum monthly expense that results in target end assets.

    Uses binary search to find the maximum monthly spending that:
    1. Results in end assets >= target_end_assets
    2. Maintains feasibility (doesn't violate min_assets constraint)

    Args:
        params: Simulation parameters (spend_month will be modified during search)
        target_end_assets: Target asset value at end of simulation
        retire_age: Person 1 retirement age (defaults to params.retire_age)
        spouse_retire_age: Person 2 retirement age (defaults to params.spouse_retire_age)
        tolerance: Tolerance for end assets (default 1000 NIS)
        max_iterations: Maximum binary search iterations (default 50)

    Returns:
        Tuple of (max_monthly_expense, result) or (None, None) if no solution found
    """
    if retire_age is None:
        retire_age = params.retire_age
    if spouse_retire_age is None:
        spouse_retire_age = params.spouse_retire_age

    # Binary search bounds
    # Lower bound: 0 (or minimum feasible spending)
    low = 0.0
    
    # Upper bound: estimate based on total income + reasonable buffer
    # Use a high estimate: sum of all potential income sources
    older_age_now = max(params.age_now, params.spouse_age_now)
    total_months = round((params.end_age - older_age_now) * 12)
    
    # Estimate upper bound: current liquid + all future income streams
    # This is a conservative upper bound
    max_estimate = params.liquid_now * 2 + (params.gross_income_month + params.spouse_gross_income_month) * total_months
    high = max_estimate / total_months if total_months > 0 else 1000000.0

    best_spend = None
    best_result = None

    # Binary search
    for iteration in range(max_iterations):
        mid = (low + high) / 2
        
        # Create modified params with this spending level
        test_params = Params(
            age_now=params.age_now,
            retire_age=params.retire_age,
            pension_start_age=params.pension_start_age,
            income_schedule=params.income_schedule,
            spouse_age_now=params.spouse_age_now,
            spouse_retire_age=params.spouse_retire_age,
            spouse_pension_start_age=params.spouse_pension_start_age,
            spouse_income_schedule=params.spouse_income_schedule,
            one_time_events=params.one_time_events,
            expense_schedule=params.expense_schedule,
            end_age=params.end_age,
            r_annual_real=params.r_annual_real,
            gross_income_month=params.gross_income_month,
            pension_rate=params.pension_rate,
            pension_rate_employer=params.pension_rate_employer,
            hishtalmut_rate_employee=params.hishtalmut_rate_employee,
            hishtalmut_rate_employer=params.hishtalmut_rate_employer,
            hishtalmut_salary_cap=params.hishtalmut_salary_cap,
            spouse_gross_income_month=params.spouse_gross_income_month,
            spouse_pension_rate=params.spouse_pension_rate,
            spouse_pension_rate_employer=params.spouse_pension_rate_employer,
            spouse_hishtalmut_rate_employee=params.spouse_hishtalmut_rate_employee,
            spouse_hishtalmut_rate_employer=params.spouse_hishtalmut_rate_employer,
            spouse_hishtalmut_salary_cap=params.spouse_hishtalmut_salary_cap,
            spend_month=mid,
            liquid_now=params.liquid_now,
            min_assets=params.min_assets,
            pension_now=params.pension_now,
            spouse_pension_now=params.spouse_pension_now,
            mekadem=params.mekadem,
            spouse_mekadem=params.spouse_mekadem,
            old_age_pension_month=params.old_age_pension_month,
            old_age_pension_start_age=params.old_age_pension_start_age,
            pension_tax_free_amount=params.pension_tax_free_amount
        )
        
        result = simulate(retire_age, test_params, spouse_retire_age)
        
        if result.ok and result.liquid_end >= target_end_assets - tolerance:
            # This spending level works, try higher
            best_spend = mid
            best_result = result
            low = mid
        else:
            # This spending level doesn't work, try lower
            high = mid
        
        # Check convergence
        if high - low < tolerance / 10:
            break
    
    # Verify the best result actually meets the target
    if best_spend is not None and best_result is not None:
        if best_result.ok and best_result.liquid_end >= target_end_assets - tolerance:
            return best_spend, best_result
    
    return None, None
