"""
Streamlit UI for Financial Life Planner (couple version).

Run with: streamlit run retire_sim/app.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

from retire_sim.model import Params, simulate
from retire_sim.search import find_earliest_retirement, find_earliest_joint_retirement, compare_scenarios, find_max_monthly_expense
from retire_sim.plots import plot_combined
from retire_sim.israeli_tax import calculate_monthly_tax_from_gross, get_effective_tax_rate

# File to persist session across refreshes
PERSIST_FILE = Path.home() / '.financial_life_planner_session.json'


def load_persisted_session():
    """Load persisted session state from file."""
    if PERSIST_FILE.exists():
        try:
            with open(PERSIST_FILE, 'r') as f:
                data = json.load(f)
                # Only load if not already in session state (to avoid overwriting current session)
                for key, value in data.items():
                    if key not in st.session_state:
                        st.session_state[key] = value
        except Exception as e:
            # If loading fails, just continue with defaults
            pass


def save_persisted_session():
    """Save current session state to file."""
    try:
        # Only save the keys we care about
        keys_to_save = [
            'end_age', 'returns', 'spend', 'liquid', 'min_assets',
            'p1_age_now', 'p1_income', 'p1_retire', 'p1_pension', 'p1_pension_now', 'p1_mekadem',
            'p2_age_now', 'p2_income', 'p2_retire', 'p2_pension', 'p2_pension_now', 'p2_mekadem',
            'p1_income_schedule', 'p2_income_schedule', 'one_time_events', 'expense_schedule'
        ]
        data = {key: st.session_state.get(key) for key in keys_to_save if key in st.session_state}
        with open(PERSIST_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        # If saving fails, just continue
        pass


def render_income_schedule_ui(person_id: str, current_age: float, gross_income: float) -> list:
    """Render income schedule UI for a person and return the schedule list.

    Args:
        person_id: 'p1' or 'p2' to distinguish between Person 1 and 2
        current_age: Current age of the person
        gross_income: Base gross income

    Returns:
        List of (age, income) tuples or None if no schedule
    """
    session_key = f'{person_id}_income_schedule'

    # Initialize session state
    if session_key not in st.session_state:
        st.session_state[session_key] = []

    # Auto-check checkbox if schedule has entries
    has_entries = len(st.session_state[session_key]) > 0
    enable_schedule = st.checkbox("Income Changes", value=has_entries,
                                   key=f'{person_id}_enable_schedule',
                                   help="Specify income changes over time (e.g., part-time transitions)")

    # Return schedule regardless of checkbox (if it has entries)
    schedule = st.session_state[session_key] if st.session_state[session_key] else None

    if enable_schedule:
        st.markdown("**Income Schedule**")

        # Show existing entries
        for idx, (age, income) in enumerate(st.session_state[session_key]):
            col_age, col_income, col_del = st.columns([2, 2, 1])
            col_age.text(f"Age {age}")
            col_income.text(f"₪{income/1000:.1f}K")
            if col_del.button("🗑️", key=f'{person_id}_del_{idx}'):
                st.session_state[session_key].pop(idx)
                st.rerun()

        # Add new entry
        col_add_age, col_add_income = st.columns(2)
        new_age = col_add_age.number_input("Add at Age", min_value=current_age, max_value=100.0,
                                           value=current_age + 5, step=1.0, key=f'{person_id}_new_age',
                                           help="Age at which income changes")
        new_income = col_add_income.number_input("Income (₪K)", min_value=0.0,
                                                 value=gross_income / 2000, step=1.0,
                                                 format="%.1f", key=f'{person_id}_new_income',
                                                 help="New gross monthly income from this age") * 1000

        if st.button("➕ Add Income Change", key=f'{person_id}_add_schedule'):
            st.session_state[session_key].append((new_age, new_income))
            st.session_state[session_key].sort(key=lambda x: x[0])
            st.rerun()

    return schedule


def render_expense_schedule_ui(current_age: float, end_age: float, base_expense: float) -> list:
    """Render expense schedule UI and return the schedule list.

    Args:
        current_age: Current age of Person 1 (expenses are relative to Person 1)
        end_age: End age of simulation
        base_expense: Base monthly expense

    Returns:
        List of (age, monthly_expense) tuples or None if no schedule
    """
    session_key = 'expense_schedule'

    # Initialize session state
    if session_key not in st.session_state:
        st.session_state[session_key] = []

    # Auto-check checkbox if schedule has entries
    has_entries = len(st.session_state[session_key]) > 0
    enable_schedule = st.checkbox("Expense Changes", value=has_entries,
                                   key='enable_expense_schedule',
                                   help="Specify expense changes over time (e.g., reducing expenses in retirement)")

    # Return schedule regardless of checkbox (if it has entries)
    schedule = st.session_state[session_key] if st.session_state[session_key] else None

    if enable_schedule:
        st.markdown("**Expense Schedule**")

        # Show existing entries
        for idx, (age, expense) in enumerate(st.session_state[session_key]):
            col_age, col_expense, col_del = st.columns([2, 2, 1])
            col_age.text(f"Age {age}")
            col_expense.text(f"₪{expense/1000:.1f}K")
            if col_del.button("🗑️", key=f'expense_del_{idx}'):
                st.session_state[session_key].pop(idx)
                st.rerun()

        # Add new entry
        col_add_age, col_add_expense = st.columns(2)
        new_age = col_add_age.number_input("Add at Age", min_value=current_age, max_value=end_age,
                                           value=current_age + 5, step=1.0, key='new_expense_age',
                                           help="Age at which monthly expense changes")
        new_expense = col_add_expense.number_input("Expense (₪K)", min_value=0.0,
                                                   value=base_expense / 1000 * 0.8, step=1.0,
                                                   format="%.1f", key='new_expense_amount',
                                                   help="New monthly expense from this age") * 1000

        if st.button("➕ Add Expense Change", key='add_expense_schedule'):
            st.session_state[session_key].append((new_age, new_expense))
            st.session_state[session_key].sort(key=lambda x: x[0])
            st.rerun()

    return schedule


def render_one_time_events_ui(current_age: float, end_age: float) -> list:
    """Render one-time events UI and return the events list.

    Args:
        current_age: Current age of Person 1 (events are relative to Person 1)
        end_age: End age of simulation

    Returns:
        List of (age, amount, description) tuples or None if no events
    """
    session_key = 'one_time_events'

    # Initialize session state
    if session_key not in st.session_state:
        st.session_state[session_key] = []

    # Auto-check checkbox if events exist
    has_events = len(st.session_state[session_key]) > 0
    enable_events = st.checkbox("One-Time Events", value=has_events, key='enable_one_time_events',
                                help="Add one-time income (inheritance, bonus) or expenses (home purchase, car)")

    # Always return events if they exist, regardless of checkbox
    events = st.session_state[session_key] if st.session_state[session_key] else None

    if enable_events:
        st.markdown("_Events are applied at Person 1's age_")

        # Show existing events
        if st.session_state[session_key]:
            st.markdown("**Existing Events:**")
            for idx, (age, amount, desc) in enumerate(st.session_state[session_key]):
                col_age, col_amount, col_desc, col_del = st.columns([1, 2, 3, 1])
                col_age.text(f"Age {age:.0f}")
                event_type = "Income" if amount > 0 else "Expense"
                col_amount.text(f"₪{abs(amount)/1000:.0f}K ({event_type})")
                col_desc.text(desc)
                if col_del.button("🗑️", key=f'event_del_{idx}'):
                    st.session_state[session_key].pop(idx)
                    st.rerun()

        # Add new event
        st.markdown("**Add New Event:**")
        col_age, col_amount, col_type = st.columns(3)

        new_event_age = col_age.number_input("At Age", min_value=current_age, max_value=end_age,
                                             value=current_age + 10, step=1.0, key='new_event_age',
                                             help="Person 1's age when event occurs")
        new_event_amount_abs = col_amount.number_input("Amount (₪K)", min_value=0.0,
                                                       value=100.0, step=10.0,
                                                       format="%.0f", key='new_event_amount',
                                                       help="Amount of one-time income or expense") * 1000
        event_type = col_type.selectbox("Type", ["Income", "Expense"], key='new_event_type',
                                        help="Income adds to assets, expense reduces assets")

        new_event_desc = st.text_input("Description", value="", placeholder="e.g., Home purchase, Inheritance, etc.",
                                       key='new_event_desc',
                                       help="Brief description of the event")

        if st.button("➕ Add Event", key='add_event'):
            if new_event_desc.strip():
                # Make amount negative for expenses
                amount = new_event_amount_abs if event_type == "Income" else -new_event_amount_abs
                st.session_state[session_key].append((new_event_age, amount, new_event_desc))
                st.session_state[session_key].sort(key=lambda x: x[0])
                st.rerun()
            else:
                st.warning("Please enter a description for the event")

    return events


def main():
    st.set_page_config(
        page_title="Financial Life Planner",
        page_icon="💰",
        layout="wide"
    )

    # Load persisted session on startup
    load_persisted_session()

    st.title("💰 Financial Life Planner")
    st.markdown("Plan your financial future for you and your spouse with different scenarios and life events.")

    # Sidebar for parameters
    with st.sidebar:
        st.header("Parameters")

        # Use hardcoded defaults from Params dataclass
        defaults = Params()

        # Shared parameters at the top
        st.subheader("Shared Parameters")

        # Add reset button
        if st.button("🔄 Reset to Defaults", help="Clear saved values and reset to default parameters"):
            # Delete persisted file
            if PERSIST_FILE.exists():
                PERSIST_FILE.unlink()
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()

        end_age = st.number_input("End Age (Planning Horizon)", min_value=50.0, max_value=120.0, value=st.session_state.get('end_age', defaults.end_age), step=1.0, key='end_age', help="Age to plan until (simulation stops here)")
        r_annual_real = st.slider("Real Annual Return (%)", min_value=0.0, max_value=15.0, value=st.session_state.get('returns', defaults.r_annual_real * 100), step=0.5, key='returns', help="Expected annual investment return after inflation (real return)") / 100
        liquid_now = st.number_input("Assets (exc. pension) (₪K)", min_value=0.0, value=st.session_state.get('liquid', defaults.liquid_now / 1000), step=10.0, format="%.1f", key='liquid', help="Current liquid assets (savings, stocks, bonds) excluding pension accounts") * 1000
        min_assets = st.number_input("Minimum Assets (₪K)", min_value=0.0, value=st.session_state.get('min_assets', defaults.min_assets / 1000), step=100.0, format="%.0f", key='min_assets', help="Assets cannot fall below this level") * 1000

        st.divider()

        # Get age_now to pass to the functions (need to read it early for this)
        age_now_for_schedules = st.session_state.get('p1_age_now', defaults.age_now)

        # Monthly expenses and expense schedule grouped together
        spend_month = st.number_input("Monthly Expense (₪K)", min_value=0.0, value=st.session_state.get('spend', defaults.spend_month / 1000), step=1.0, format="%.1f", key='spend', help="Combined household monthly expense (in real terms, constant throughout simulation unless modified by expense schedule)") * 1000

        # Expense schedule
        expense_schedule = render_expense_schedule_ui(age_now_for_schedules, end_age, spend_month)

        # One-time events (income or expenses)
        one_time_events = render_one_time_events_ui(age_now_for_schedules, end_age)

        st.divider()

        # Person-specific parameters side by side
        st.subheader("Person-Specific Parameters")

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown("**Person 1**")
            age_now = st.number_input("Current Age", min_value=18.0, max_value=100.0, value=st.session_state.get('p1_age_now', defaults.age_now), step=1.0, key='p1_age_now', help="Current age (starting point of simulation)")
            gross_income_month = st.number_input("Gross Income (₪K)", min_value=0.0, value=st.session_state.get('p1_income', defaults.gross_income_month / 1000), step=1.0, format="%.1f", key='p1_income', help="Monthly gross income before tax (Israeli tax calculated automatically)") * 1000

            # Income schedule UI
            income_schedule = render_income_schedule_ui('p1', age_now, gross_income_month)

            retire_age = st.number_input("Retirement Age",
                                        min_value=age_now,
                                        max_value=100.0,
                                        value=st.session_state.get('p1_retire', defaults.retire_age),
                                        step=1.0,
                                        key='p1_retire',
                                        help="Age to stop working and start drawing from assets")

            pension_start_age = st.number_input("Pension Start Age", min_value=retire_age, max_value=100.0, value=st.session_state.get('p1_pension', defaults.pension_start_age), step=1.0, key='p1_pension', help="Age to start receiving pension income (usually 67 in Israel)")

            pension_rate = 0.06  # Fixed rate (6% employee contribution)
            pension_rate_employer = 0.125  # Fixed rate (12.5% employer contribution)
            hishtalmut_rate_employee = 0.025  # Fixed rate (2.5% employee contribution)
            hishtalmut_rate_employer = 0.075  # Fixed rate (7.5% employer contribution)
            hishtalmut_salary_cap = defaults.hishtalmut_salary_cap

            st.markdown("**Pension**")
            pension_now = st.number_input("Pension Now (₪K)", min_value=0.0, value=st.session_state.get('p1_pension_now', defaults.pension_now / 1000), step=10.0, format="%.1f", key='p1_pension_now', help="Current balance in pension account (Keren Pensia)") * 1000
            mekadem = st.number_input(
                "Mekadem",
                min_value=1.0,
                value=st.session_state.get('p1_mekadem', defaults.mekadem),
                step=1.0,
                format="%.0f",
                key='p1_mekadem',
                help="Divisor for pension income (Monthly pension = Balance / Mekadem)"
            )

        with col_p2:
            st.markdown("**Person 2**")
            spouse_age_now = st.number_input("Current Age", min_value=18.0, max_value=100.0, value=st.session_state.get('p2_age_now', defaults.spouse_age_now), step=1.0, key='p2_age_now', help="Current age (starting point of simulation)")
            spouse_gross_income_month = st.number_input("Gross Income (₪K)", min_value=0.0, value=st.session_state.get('p2_income', defaults.spouse_gross_income_month / 1000), step=1.0, format="%.1f", key='p2_income', help="Monthly gross income before tax (Israeli tax calculated automatically)") * 1000

            # Income schedule UI
            spouse_income_schedule = render_income_schedule_ui('p2', spouse_age_now, spouse_gross_income_month)

            spouse_retire_age = st.number_input("Retirement Age",
                                               min_value=spouse_age_now,
                                               max_value=100.0,
                                               value=st.session_state.get('p2_retire', defaults.spouse_retire_age),
                                               step=1.0,
                                               key='p2_retire',
                                               help="Age to stop working and start drawing from assets")

            spouse_pension_start_age = st.number_input("Pension Start Age", min_value=spouse_retire_age, max_value=100.0, value=st.session_state.get('p2_pension', defaults.spouse_pension_start_age), step=1.0, key='p2_pension', help="Age to start receiving pension income (usually 67 in Israel)")

            spouse_pension_rate = 0.06  # Fixed rate (6% employee contribution)
            spouse_pension_rate_employer = 0.125  # Fixed rate (12.5% employer contribution)
            spouse_hishtalmut_rate_employee = 0.025  # Fixed rate (2.5% employee contribution)
            spouse_hishtalmut_rate_employer = 0.075  # Fixed rate (7.5% employer contribution)
            spouse_hishtalmut_salary_cap = defaults.spouse_hishtalmut_salary_cap

            st.markdown("**Pension**")
            spouse_pension_now = st.number_input("Pension Now (₪K)", min_value=0.0, value=st.session_state.get('p2_pension_now', defaults.spouse_pension_now / 1000), step=10.0, format="%.1f", key='p2_pension_now', help="Current balance in pension account (Keren Pensia)") * 1000
            spouse_mekadem = st.number_input(
                "Mekadem",
                min_value=1.0,
                value=st.session_state.get('p2_mekadem', defaults.spouse_mekadem),
                step=1.0,
                format="%.0f",
                key='p2_mekadem',
                help="Divisor for pension income (Monthly pension = Balance / Mekadem)"
            )

        # Create params from user inputs (old age pension values use defaults)
        params = Params(
            age_now=age_now,
            retire_age=retire_age,
            pension_start_age=pension_start_age,
            income_schedule=income_schedule,
            spouse_age_now=spouse_age_now,
            spouse_retire_age=spouse_retire_age,
            spouse_pension_start_age=spouse_pension_start_age,
            spouse_income_schedule=spouse_income_schedule,
            one_time_events=one_time_events,
            expense_schedule=expense_schedule,
            end_age=end_age,
            r_annual_real=r_annual_real,
            gross_income_month=gross_income_month,
            pension_rate=pension_rate,
            pension_rate_employer=pension_rate_employer,
            hishtalmut_rate_employee=hishtalmut_rate_employee,
            hishtalmut_rate_employer=hishtalmut_rate_employer,
            hishtalmut_salary_cap=hishtalmut_salary_cap,
            spouse_gross_income_month=spouse_gross_income_month,
            spouse_pension_rate=spouse_pension_rate,
            spouse_pension_rate_employer=spouse_pension_rate_employer,
            spouse_hishtalmut_rate_employee=spouse_hishtalmut_rate_employee,
            spouse_hishtalmut_rate_employer=spouse_hishtalmut_rate_employer,
            spouse_hishtalmut_salary_cap=spouse_hishtalmut_salary_cap,
            spend_month=spend_month,
            liquid_now=liquid_now,
            min_assets=min_assets,
            pension_now=pension_now,
            spouse_pension_now=spouse_pension_now,
            mekadem=mekadem,
            spouse_mekadem=spouse_mekadem,
            old_age_pension_month=defaults.old_age_pension_month,
            old_age_pension_start_age=defaults.old_age_pension_start_age
        )

        # Save session state to persist across refreshes
        save_persisted_session()

        # Display derived values
        st.divider()
        st.subheader("Derived Values")
        st.metric("Monthly Return Rate", f"{params.r_month * 100:.3f}%")

        # Calculate tax and net income for display
        tax_p1 = calculate_monthly_tax_from_gross(params.gross_income_month)
        net_p1 = params.gross_income_month - tax_p1
        eff_rate_p1 = get_effective_tax_rate(params.gross_income_month)

        tax_p2 = calculate_monthly_tax_from_gross(params.spouse_gross_income_month)
        net_p2 = params.spouse_gross_income_month - tax_p2
        eff_rate_p2 = get_effective_tax_rate(params.spouse_gross_income_month)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("**Person 1**")
            # Net income after tax, employee pension, and employee hishtalmut deductions
            net_after_all_p1 = params.gross_income_month - tax_p1 - params.contrib_pension_employee_month - params.contrib_hishtalmut_employee_month
            st.metric("Net to Hand", f"₪{net_after_all_p1/1000:.1f}K",
                     help=f"Gross: ₪{params.gross_income_month/1000:.1f}K - Tax: ₪{tax_p1/1000:.1f}K - Employee Pension: ₪{params.contrib_pension_employee_month/1000:.1f}K - Employee Hishtalmut: ₪{params.contrib_hishtalmut_employee_month/1000:.1f}K")
            st.metric("Effective Tax Rate", f"{eff_rate_p1:.1f}%")
            st.metric("Pension Accumulation", f"₪{params.contrib_pension_month/1000:.1f}K",
                     help=f"Employee: ₪{params.contrib_pension_employee_month/1000:.1f}K (6%) + Employer: ₪{(params.contrib_pension_month - params.contrib_pension_employee_month)/1000:.1f}K (12.5%) = 18.5% total")
            st.metric("Hishtalmut to Assets", f"₪{params.contrib_hishtalmut_month/1000:.1f}K",
                     help=f"Employee: ₪{params.contrib_hishtalmut_employee_month/1000:.1f}K (2.5%) + Employer: ₪{(params.contrib_hishtalmut_month - params.contrib_hishtalmut_employee_month)/1000:.1f}K (7.5%) = 10% total, capped at salary of ₪{params.hishtalmut_salary_cap/1000:.1f}K")

        with col_d2:
            st.markdown("**Person 2**")
            # Net income after tax, employee pension, and employee hishtalmut deductions
            net_after_all_p2 = params.spouse_gross_income_month - tax_p2 - params.spouse_contrib_pension_employee_month - params.spouse_contrib_hishtalmut_employee_month
            st.metric("Net to Hand", f"₪{net_after_all_p2/1000:.1f}K",
                     help=f"Gross: ₪{params.spouse_gross_income_month/1000:.1f}K - Tax: ₪{tax_p2/1000:.1f}K - Employee Pension: ₪{params.spouse_contrib_pension_employee_month/1000:.1f}K - Employee Hishtalmut: ₪{params.spouse_contrib_hishtalmut_employee_month/1000:.1f}K")
            st.metric("Effective Tax Rate", f"{eff_rate_p2:.1f}%")
            st.metric("Pension Accumulation", f"₪{params.spouse_contrib_pension_month/1000:.1f}K",
                     help=f"Employee: ₪{params.spouse_contrib_pension_employee_month/1000:.1f}K (6%) + Employer: ₪{(params.spouse_contrib_pension_month - params.spouse_contrib_pension_employee_month)/1000:.1f}K (12.5%) = 18.5% total")
            st.metric("Hishtalmut to Assets", f"₪{params.spouse_contrib_hishtalmut_month/1000:.1f}K",
                     help=f"Employee: ₪{params.spouse_contrib_hishtalmut_employee_month/1000:.1f}K (2.5%) + Employer: ₪{(params.spouse_contrib_hishtalmut_month - params.spouse_contrib_hishtalmut_employee_month)/1000:.1f}K (7.5%) = 10% total, capped at salary of ₪{params.spouse_hishtalmut_salary_cap/1000:.1f}K")

        combined_net_to_hand = net_after_all_p1 + net_after_all_p2
        st.metric("Combined Net to Hand (Both Working)", f"₪{combined_net_to_hand / 1000:.1f}K",
                 help="After tax, employee pension, and employee hishtalmut deductions.")

        # Tax information expander
        with st.expander("ℹ️ Israeli Tax & Pension Information (2025)"):
            st.markdown("**Income Tax Brackets (Annual)**")
            st.markdown("""
            - ₪0 - ₪84,120: **10%**
            - ₪84,120 - ₪120,720: **14%**
            - ₪120,720 - ₪193,800: **20%**
            - ₪193,800 - ₪269,280: **31%**
            - ₪269,280 - ₪560,280: **35%**
            - ₪560,280 - ₪721,560: **47%**
            - Above ₪721,560: **50%**
            """)

            st.markdown("**National Insurance + Health (Bituach Leumi + Briut) - Monthly**")
            st.markdown("""
            - Up to ₪7,522/month: **4.27%** (NI 1.04% + Health 3.23%)
            - ₪7,522 - ₪50,695/month: **12.17%** (NI 7.00% + Health 5.17%)
            - Cap at ₪50,695/month
            """)

            st.markdown("**Mandatory Pension Contributions**")
            st.markdown("""
            - **Employee contribution:** 6% of gross salary (deducted from paycheck)
            - **Employer contribution:** 12.5% of gross salary (not deducted from paycheck)
            - **Total pension accumulation:** 18.5% of gross salary

            Note: This is mandatory by Israeli law. The simulation uses these rates by default.
            """)

            st.markdown("**Net Income Calculation**")
            st.markdown("""
            Net to Hand = Gross - Income Tax - National Insurance - Employee Pension (6%)

            Example for ₪30,000 gross:
            - Income Tax: ~₪6,942/month
            - National Insurance: ~₪3,020/month
            - Employee Pension (6%): ₪1,800/month
            - **Net to Hand: ~₪18,238/month**
            - Employer adds ₪3,750/month to pension (12.5%)
            - **Total Pension: ₪5,550/month (18.5%)**
            """)

    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Run Simulation", "Find Earliest Retirement", "Find Joint Retirement", "Compare Scenarios", "Max Monthly Expense"])

    with tab1:
        st.header("Run Simulation")
        st.markdown("Simulate your financial plan with the parameters specified in the sidebar.")

        if st.button("Run Simulation", type="primary"):
            result = simulate(params.retire_age, params, params.spouse_retire_age)

            # Display summary
            if result.ok:
                st.success(f"✅ {result.reason}")
            else:
                st.error(f"❌ {result.reason}")

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Assets at First Pension", f"₪{result.liquid_at_pension_start / 1000:.1f}K")
            with col2:
                st.metric("P1 Pension Income/Mo", f"₪{result.pension_income_month / 1000:.1f}K")
            with col3:
                st.metric("P2 Pension Income/Mo", f"₪{result.spouse_pension_income_month / 1000:.1f}K")
            with col4:
                st.metric("Assets at End", f"₪{result.liquid_end / 1000:.1f}K")

            # Plots
            if not result.df.empty:
                st.plotly_chart(
                    plot_combined(result.df, params.retire_age, params.spouse_retire_age,
                                params.pension_start_age, params.spouse_pension_start_age,
                                params.income_schedule, params.spouse_income_schedule,
                                params.one_time_events, params.expense_schedule),
                    width='stretch'
                )

                # Data table
                with st.expander("View Detailed Data"):
                    # Convert dataframe to CSV for download
                    csv = result.df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"financial_plan_{params.retire_age:.0f}_{params.spouse_retire_age:.0f}.csv",
                        mime="text/csv",
                        key="download_csv_tab1"
                    )
                    st.dataframe(result.df, width='stretch')

    with tab2:
        st.header("Find Earliest Retirement Age (Person 1)")
        st.markdown("Find the earliest age at which Person 1 can retire, assuming Person 2 retires at their specified age.")

        search_spouse_retire = st.number_input(
            "Person 2 Retirement Age (for search)",
            min_value=params.spouse_age_now,
            max_value=params.spouse_pension_start_age,
            value=params.spouse_retire_age,
            step=1.0,
            key='search_spouse_retire'
        )

        if st.button("Find Earliest Retirement", type="primary"):
            with st.spinner("Searching for earliest feasible retirement age for Person 1..."):
                earliest_age, result = find_earliest_retirement(params, spouse_retire_age=search_spouse_retire)

            if earliest_age is not None:
                st.success(f"✅ Earliest feasible retirement age for Person 1: **{earliest_age:.1f}** years")

                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Working Years (P1)", f"{earliest_age - params.age_now:.1f}")
                with col2:
                    st.metric("Working Years (P2)", f"{search_spouse_retire - params.spouse_age_now:.1f}")
                with col3:
                    st.metric("Assets at First Pension", f"₪{result.liquid_at_pension_start / 1000:.1f}K")
                with col4:
                    st.metric("Assets at End", f"₪{result.liquid_end / 1000:.1f}K")

                # Plots
                if not result.df.empty:
                    st.plotly_chart(
                        plot_combined(result.df, earliest_age, search_spouse_retire,
                                    params.pension_start_age, params.spouse_pension_start_age,
                                    params.income_schedule, params.spouse_income_schedule,
                                    params.one_time_events, params.expense_schedule),
                        width='stretch'
                    )
            else:
                st.error("❌ No feasible retirement age found for Person 1 between current age and pension start age.")

    with tab3:
        st.header("Find Joint Retirement Age")
        st.markdown("Find the earliest age at which BOTH people can retire at the same time.")

        if st.button("Find Joint Retirement", type="primary"):
            with st.spinner("Searching for earliest joint retirement..."):
                retire1, retire2, result = find_earliest_joint_retirement(params)

            if retire1 is not None and retire2 is not None:
                st.success(f"✅ Earliest joint retirement: Person 1 at **{retire1:.1f}**, Person 2 at **{retire2:.1f}** years")

                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Person 1 Retirement Age", f"{retire1:.1f}")
                with col2:
                    st.metric("Person 2 Retirement Age", f"{retire2:.1f}")
                with col3:
                    st.metric("Assets at First Pension", f"₪{result.liquid_at_pension_start / 1000:.1f}K")
                with col4:
                    st.metric("Assets at End", f"₪{result.liquid_end / 1000:.1f}K")

                # Plots
                if not result.df.empty:
                    st.plotly_chart(
                        plot_combined(result.df, retire1, retire2,
                                    params.pension_start_age, params.spouse_pension_start_age,
                                    params.income_schedule, params.spouse_income_schedule,
                                    params.one_time_events, params.expense_schedule),
                        width='stretch'
                    )
            else:
                st.error("❌ No feasible joint retirement age found.")

    with tab4:
        st.header("Compare Multiple Scenarios")

        st.markdown("Compare different retirement ages for Person 1.")

        # Generate scenario ages for Person 1
        num_scenarios = st.slider("Number of Scenarios", min_value=3, max_value=10, value=5, key='num_scenarios')
        compare_spouse_retire = st.number_input(
            "Person 2 Retirement Age (for comparison)",
            min_value=params.spouse_age_now,
            max_value=params.spouse_pension_start_age,
            value=params.spouse_retire_age,
            step=1.0,
            key='compare_spouse_retire'
        )

        age_range = params.pension_start_age - params.age_now
        retirement_ages = [params.age_now + (age_range * i / (num_scenarios - 1)) for i in range(num_scenarios)]

        if st.button("Compare Scenarios", type="primary"):
            with st.spinner("Running scenarios..."):
                scenarios = compare_scenarios(params, retirement_ages, compare_spouse_retire)

            # Convert to DataFrame
            df_scenarios = pd.DataFrame(scenarios)

            # Format for display
            df_display = df_scenarios.copy()
            df_display['retirement_age'] = df_display['retirement_age'].apply(lambda x: f"{x:.1f}")
            df_display['spouse_retirement_age'] = df_display['spouse_retirement_age'].apply(lambda x: f"{x:.1f}")
            df_display['feasible'] = df_display['feasible'].apply(lambda x: "✅" if x else "❌")
            df_display['liquid_at_pension_start'] = df_display['liquid_at_pension_start'].apply(lambda x: f"₪{x / 1000:.1f}K")
            df_display['pension_income_month'] = df_display['pension_income_month'].apply(lambda x: f"₪{x / 1000:.1f}K")
            df_display['spouse_pension_income_month'] = df_display['spouse_pension_income_month'].apply(lambda x: f"₪{x / 1000:.1f}K")
            df_display['liquid_end'] = df_display['liquid_end'].apply(lambda x: f"₪{x / 1000:.1f}K")
            df_display['working_years'] = df_display['working_years'].apply(lambda x: f"{x:.1f}")
            df_display['spouse_working_years'] = df_display['spouse_working_years'].apply(lambda x: f"{x:.1f}")

            # Rename columns for display
            df_display = df_display[[
                'retirement_age',
                'spouse_retirement_age',
                'feasible',
                'working_years',
                'spouse_working_years',
                'liquid_at_pension_start',
                'pension_income_month',
                'spouse_pension_income_month',
                'liquid_end'
            ]]

            df_display.columns = [
                'P1 Retire Age',
                'P2 Retire Age',
                'Feasible',
                'P1 Working Yrs',
                'P2 Working Yrs',
                'Assets at Pension',
                'P1 Pension/Mo',
                'P2 Pension/Mo',
                'Assets at End'
            ]

            st.dataframe(df_display, width='stretch')

            # Show earliest feasible
            feasible_scenarios = [s for s in scenarios if s['feasible']]
            if feasible_scenarios:
                earliest = min(feasible_scenarios, key=lambda x: x['retirement_age'])
                st.info(f"ℹ️ Earliest feasible: Person 1 at **{earliest['retirement_age']:.1f}** years, Person 2 at **{earliest['spouse_retirement_age']:.1f}** years")

    with tab5:
        st.header("Maximum Monthly Expense Calculator")
        st.markdown("Find the maximum monthly expense you can afford while maintaining a target asset level at the end of the simulation.")
        st.info(f"ℹ️ Using retirement ages from sidebar: Person 1 at **{params.retire_age:.1f}**, Person 2 at **{params.spouse_retire_age:.1f}**. Target assets: **₪{params.min_assets/1000:.0f}K** (from Minimum Assets setting).")

        if st.button("Calculate Max Monthly Expense", type="primary"):
            with st.spinner("Calculating maximum monthly expense..."):
                max_expense, result = find_max_monthly_expense(
                    params,
                    params.min_assets,
                    retire_age=params.retire_age,
                    spouse_retire_age=params.spouse_retire_age
                )

            if max_expense is not None and result is not None:
                st.success(f"✅ Maximum monthly expense: **₪{max_expense/1000:.1f}K**")

                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Max Monthly Expense", f"₪{max_expense/1000:.1f}K")
                with col2:
                    st.metric("Assets at First Pension", f"₪{result.liquid_at_pension_start / 1000:.1f}K")
                with col3:
                    st.metric("P1 Pension Income/Mo", f"₪{result.pension_income_month / 1000:.1f}K")
                with col4:
                    st.metric("P2 Pension Income/Mo", f"₪{result.spouse_pension_income_month / 1000:.1f}K")

                # Additional metrics
                col5, col6 = st.columns(2)
                with col5:
                    st.metric("Assets at End", f"₪{result.liquid_end / 1000:.1f}K")
                with col6:
                    difference = max_expense - params.spend_month
                    st.metric(
                        "Difference from Current Expense",
                        f"₪{difference/1000:+.1f}K",
                        help=f"Current expense: ₪{params.spend_month/1000:.1f}K"
                    )

                # Plots
                if not result.df.empty:
                    st.plotly_chart(
                        plot_combined(result.df, params.retire_age, params.spouse_retire_age,
                                    params.pension_start_age, params.spouse_pension_start_age,
                                    params.income_schedule, params.spouse_income_schedule,
                                    params.one_time_events, params.expense_schedule),
                        width='stretch'
                    )

                    # Data table
                    with st.expander("View Detailed Data"):
                        # Convert dataframe to CSV for download
                        csv = result.df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"financial_plan_max_expense_{params.retire_age:.0f}_{params.spouse_retire_age:.0f}.csv",
                            mime="text/csv",
                            key="download_csv_tab5"
                        )
                        st.dataframe(result.df, width='stretch')
            else:
                st.error("❌ Could not find a feasible solution. Try adjusting the Minimum Assets or retirement ages in the sidebar.")


if __name__ == "__main__":
    main()
