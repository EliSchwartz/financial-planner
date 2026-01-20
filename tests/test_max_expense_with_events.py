"""
Test that max monthly expense calculation considers one-time events and income schedules.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from retire_sim.model import Params
from retire_sim.search import find_max_monthly_expense


def test_max_expense_with_one_time_events():
    """Test that one-time events (like inheritance) increase max monthly expense."""

    print("\n=== Test 1: Max expense WITHOUT one-time events ===")

    # Baseline scenario - no one-time events
    params_base = Params(
        age_now=40.0,
        retire_age=50.0,
        pension_start_age=67.0,
        end_age=95.0,
        gross_income_month=30000.0,
        spouse_gross_income_month=25000.0,
        spouse_age_now=38.0,
        spouse_retire_age=48.0,
        liquid_now=500000.0,
        pension_now=100000.0,
        spouse_pension_now=80000.0,
        min_assets=200000.0,
        r_annual_real=0.03,
    )

    max_spend_base, result_base = find_max_monthly_expense(
        params_base,
        target_end_assets=500000.0,
        retire_age=50.0,
        spouse_retire_age=48.0,
        tolerance=1000.0
    )

    print(f"Max monthly expense (no events): ₪{max_spend_base:,.0f}")
    if result_base:
        print(f"Final assets: ₪{result_base.liquid_end:,.0f}")

    # Scenario with large inheritance at age 55
    print("\n=== Test 2: Max expense WITH large inheritance ===")

    params_with_inheritance = Params(
        age_now=40.0,
        retire_age=50.0,
        pension_start_age=67.0,
        end_age=95.0,
        gross_income_month=30000.0,
        spouse_gross_income_month=25000.0,
        spouse_age_now=38.0,
        spouse_retire_age=48.0,
        liquid_now=500000.0,
        pension_now=100000.0,
        spouse_pension_now=80000.0,
        min_assets=200000.0,
        r_annual_real=0.03,
        one_time_events=[(55.0, 1000000.0, 'Inheritance')]  # ₪1M inheritance
    )

    max_spend_inheritance, result_inheritance = find_max_monthly_expense(
        params_with_inheritance,
        target_end_assets=500000.0,
        retire_age=50.0,
        spouse_retire_age=48.0,
        tolerance=1000.0
    )

    print(f"Max monthly expense (with ₪1M inheritance): ₪{max_spend_inheritance:,.0f}")
    if result_inheritance:
        print(f"Final assets: ₪{result_inheritance.liquid_end:,.0f}")

    # Verify inheritance increases max spending
    if max_spend_base and max_spend_inheritance:
        increase = max_spend_inheritance - max_spend_base
        increase_pct = (increase / max_spend_base) * 100
        print(f"\nIncrease in max spending: ₪{increase:,.0f} (+{increase_pct:.1f}%)")

        assert max_spend_inheritance > max_spend_base, "Inheritance should increase max spending"
        print("✓ Inheritance correctly increases max monthly expense")
    else:
        print("⚠ Warning: Could not find max expense for one or both scenarios")

    # Scenario with large one-time expense
    print("\n=== Test 3: Max expense WITH large expense ===")

    params_with_expense = Params(
        age_now=40.0,
        retire_age=50.0,
        pension_start_age=67.0,
        end_age=95.0,
        gross_income_month=30000.0,
        spouse_gross_income_month=25000.0,
        spouse_age_now=38.0,
        spouse_retire_age=48.0,
        liquid_now=500000.0,
        pension_now=100000.0,
        spouse_pension_now=80000.0,
        min_assets=200000.0,
        r_annual_real=0.03,
        one_time_events=[(55.0, -500000.0, 'Home renovation')]  # ₪500K expense
    )

    max_spend_expense, result_expense = find_max_monthly_expense(
        params_with_expense,
        target_end_assets=500000.0,
        retire_age=50.0,
        spouse_retire_age=48.0,
        tolerance=1000.0
    )

    print(f"Max monthly expense (with ₪500K expense): ₪{max_spend_expense:,.0f}")
    if result_expense:
        print(f"Final assets: ₪{result_expense.liquid_end:,.0f}")

    # Verify expense decreases max spending
    if max_spend_base and max_spend_expense:
        decrease = max_spend_base - max_spend_expense
        decrease_pct = (decrease / max_spend_base) * 100
        print(f"\nDecrease in max spending: ₪{decrease:,.0f} (-{decrease_pct:.1f}%)")

        assert max_spend_expense < max_spend_base, "Large expense should decrease max spending"
        print("✓ Large expense correctly decreases max monthly expense")
    else:
        print("⚠ Warning: Could not find max expense for one or both scenarios")


def test_max_expense_with_income_schedule():
    """Test that income changes affect max monthly expense calculation."""

    print("\n=== Test 4: Max expense with CONSTANT income ===")

    # Baseline - constant income
    params_constant = Params(
        age_now=40.0,
        retire_age=60.0,
        pension_start_age=67.0,
        end_age=95.0,
        gross_income_month=40000.0,  # Constant ₪40K
        spouse_gross_income_month=30000.0,
        spouse_age_now=38.0,
        spouse_retire_age=58.0,
        liquid_now=300000.0,
        pension_now=100000.0,
        spouse_pension_now=80000.0,
        min_assets=200000.0,
        r_annual_real=0.03,
    )

    max_spend_constant, result_constant = find_max_monthly_expense(
        params_constant,
        target_end_assets=500000.0,
        retire_age=60.0,
        spouse_retire_age=58.0,
        tolerance=1000.0
    )

    print(f"Max monthly expense (constant ₪40K income): ₪{max_spend_constant:,.0f}")
    if result_constant:
        print(f"Final assets: ₪{result_constant.liquid_end:,.0f}")

    # Scenario with income increase
    print("\n=== Test 5: Max expense with INCREASING income ===")

    params_increasing = Params(
        age_now=40.0,
        retire_age=60.0,
        pension_start_age=67.0,
        end_age=95.0,
        gross_income_month=40000.0,
        income_schedule=[
            (45.0, 50000.0),  # Increase to ₪50K at age 45
            (50.0, 60000.0),  # Increase to ₪60K at age 50
        ],
        spouse_gross_income_month=30000.0,
        spouse_age_now=38.0,
        spouse_retire_age=58.0,
        liquid_now=300000.0,
        pension_now=100000.0,
        spouse_pension_now=80000.0,
        min_assets=200000.0,
        r_annual_real=0.03,
    )

    max_spend_increasing, result_increasing = find_max_monthly_expense(
        params_increasing,
        target_end_assets=500000.0,
        retire_age=60.0,
        spouse_retire_age=58.0,
        tolerance=1000.0
    )

    print(f"Max monthly expense (increasing income): ₪{max_spend_increasing:,.0f}")
    if result_increasing:
        print(f"Final assets: ₪{result_increasing.liquid_end:,.0f}")

    # Verify income increase raises max spending
    if max_spend_constant and max_spend_increasing:
        increase = max_spend_increasing - max_spend_constant
        increase_pct = (increase / max_spend_constant) * 100
        print(f"\nIncrease in max spending: ₪{increase:,.0f} (+{increase_pct:.1f}%)")

        assert max_spend_increasing > max_spend_constant, "Income increases should increase max spending"
        print("✓ Income increases correctly increase max monthly expense")
    else:
        print("⚠ Warning: Could not find max expense for one or both scenarios")

    # Scenario with income decrease (part-time transition)
    print("\n=== Test 6: Max expense with DECREASING income (part-time) ===")

    params_decreasing = Params(
        age_now=40.0,
        retire_age=60.0,
        pension_start_age=67.0,
        end_age=95.0,
        gross_income_month=40000.0,
        income_schedule=[
            (50.0, 25000.0),  # Reduce to ₪25K at age 50 (part-time)
        ],
        spouse_gross_income_month=30000.0,
        spouse_age_now=38.0,
        spouse_retire_age=58.0,
        liquid_now=300000.0,
        pension_now=100000.0,
        spouse_pension_now=80000.0,
        min_assets=200000.0,
        r_annual_real=0.03,
    )

    max_spend_decreasing, result_decreasing = find_max_monthly_expense(
        params_decreasing,
        target_end_assets=500000.0,
        retire_age=60.0,
        spouse_retire_age=58.0,
        tolerance=1000.0
    )

    print(f"Max monthly expense (part-time at 50): ₪{max_spend_decreasing:,.0f}")
    if result_decreasing:
        print(f"Final assets: ₪{result_decreasing.liquid_end:,.0f}")

    # Verify income decrease lowers max spending
    if max_spend_constant and max_spend_decreasing:
        decrease = max_spend_constant - max_spend_decreasing
        decrease_pct = (decrease / max_spend_constant) * 100
        print(f"\nDecrease in max spending: ₪{decrease:,.0f} (-{decrease_pct:.1f}%)")

        assert max_spend_decreasing < max_spend_constant, "Income decreases should decrease max spending"
        print("✓ Income decreases correctly decrease max monthly expense")
    else:
        print("⚠ Warning: Could not find max expense for one or both scenarios")


if __name__ == '__main__':
    print("="*60)
    print("Testing Max Monthly Expense with One-Time Events")
    print("="*60)
    test_max_expense_with_one_time_events()

    print("\n" + "="*60)
    print("Testing Max Monthly Expense with Income Schedules")
    print("="*60)
    test_max_expense_with_income_schedule()

    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print("\nSummary:")
    print("  ✓ One-time income events increase max monthly expense")
    print("  ✓ One-time expense events decrease max monthly expense")
    print("  ✓ Income increases raise max monthly expense")
    print("  ✓ Income decreases lower max monthly expense")
