"""
Plotting utilities for financial simulation results.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_combined(
    df: pd.DataFrame,
    retire_age1: float,
    retire_age2: float,
    pension_start_age1: float,
    pension_start_age2: float,
    income_schedule1: list = None,
    income_schedule2: list = None,
    one_time_events: list = None,
    expense_schedule: list = None
) -> go.Figure:
    """
    Create a combined plot showing balances and cashflows for couple.

    Args:
        df: DataFrame with simulation results
        retire_age1: Person 1 retirement age
        retire_age2: Person 2 retirement age
        pension_start_age1: Person 1 pension start age
        pension_start_age2: Person 2 pension start age
        income_schedule1: Person 1 income schedule
        income_schedule2: Person 2 income schedule
        one_time_events: List of one-time events
        expense_schedule: Monthly expense schedule

    Returns:
        Plotly figure with subplots
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Account Balances Over Time (by Person 1 Age)', 'Monthly Cashflows Over Time'),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )

    # Balances
    fig.add_trace(
        go.Scatter(
            x=df['age1'], y=df['liquid'],
            name='Liquid (Combined)',
            line=dict(color='blue', width=2),
            legendgroup='balances'
        ),
        row=1, col=1
    )

    # Filter pension1 data to only show until pension start age
    df_pension1 = df[df['age1'] <= pension_start_age1]
    fig.add_trace(
        go.Scatter(
            x=df_pension1['age1'], y=df_pension1['pension1'],
            name='Pension 1',
            line=dict(color='green', width=2),
            legendgroup='balances'
        ),
        row=1, col=1
    )

    # Filter pension2 data to only show until pension start age
    df_pension2 = df[df['age1'] <= pension_start_age2]
    fig.add_trace(
        go.Scatter(
            x=df_pension2['age1'], y=df_pension2['pension2'],
            name='Pension 2',
            line=dict(color='lightgreen', width=2, dash='dash'),
            legendgroup='balances'
        ),
        row=1, col=1
    )

    # Cashflows - Stacked area chart showing all income sources
    # Order from bottom to top: Salary 2, Salary 1, Old Age Pension, Pension 2, Pension 1, Asset Withdrawal

    # Net Salary Person 2 (bottom layer)
    fig.add_trace(
        go.Scatter(
            x=df['age1'], y=df['salary2_net'],
            name='Net Salary Person 2',
            line=dict(color='lightblue', width=2),
            legendgroup='cashflows',
            stackgroup='income',
            fillcolor='lightblue'
        ),
        row=2, col=1
    )

    # Net Salary Person 1
    fig.add_trace(
        go.Scatter(
            x=df['age1'], y=df['salary1_net'],
            name='Net Salary Person 1',
            line=dict(color='cornflowerblue', width=2),
            legendgroup='cashflows',
            stackgroup='income',
            fillcolor='cornflowerblue'
        ),
        row=2, col=1
    )

    # Old Age Pension (קצבת זקנה)
    if 'old_age_pension' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['age1'], y=df['old_age_pension'],
                name='Old Age Pension (קצבת זקנה)',
                line=dict(color='purple', width=2),
                legendgroup='cashflows',
                stackgroup='income',
                fillcolor='purple'
            ),
            row=2, col=1
        )

    # Pension 2 Income (Net)
    fig.add_trace(
        go.Scatter(
            x=df['age1'], y=df['pension2_income_net'],
            name='Pension 2 Income (Net)',
            line=dict(color='lightgreen', width=2),
            legendgroup='cashflows',
            stackgroup='income',
            fillcolor='lightgreen'
        ),
        row=2, col=1
    )
    
    # Pension 1 Income (Net)
    fig.add_trace(
        go.Scatter(
            x=df['age1'], y=df['pension1_income_net'],
            name='Pension 1 Income (Net)',
            line=dict(color='green', width=2),
            legendgroup='cashflows',
            stackgroup='income',
            fillcolor='green'
        ),
        row=2, col=1
    )

    # Add line for monthly expenses (on top of stacked cashflows)
    # This line will change over time if there's an expense schedule
    fig.add_trace(
        go.Scatter(
            x=df['age1'],
            y=df['monthly_expense'],
            name='Monthly Expenses',
            line=dict(color='red', width=3, dash='solid'),
            legendgroup='cashflows',
            mode='lines',
            showlegend=True
        ),
        row=2, col=1
    )

    # Add vertical lines for Person 1
    for row in [1, 2]:
        fig.add_vline(
            x=retire_age1,
            line_dash="dash",
            line_color="red",
            row=row, col=1,
            annotation_text=f"P1 Retire ({retire_age1:.0f})" if row == 1 else "",
            annotation_position="top"
        )
        fig.add_vline(
            x=pension_start_age1,
            line_dash="dash",
            line_color="orange",
            row=row, col=1,
            annotation_text=f"P1 Pension ({pension_start_age1:.0f})" if row == 1 else "",
            annotation_position="top"
        )

    # Add vertical lines for Person 2 (if different ages)
    if abs(retire_age2 - retire_age1) > 0.5:
        for row in [1, 2]:
            fig.add_vline(
                x=retire_age2,
                line_dash="dot",
                line_color="darkred",
                row=row, col=1,
                annotation_text=f"P2 Retire ({retire_age2:.0f})" if row == 1 else "",
                annotation_position="bottom"
            )

    if abs(pension_start_age2 - pension_start_age1) > 0.5:
        for row in [1, 2]:
            fig.add_vline(
                x=pension_start_age2,
                line_dash="dot",
                line_color="darkorange",
                row=row, col=1,
                annotation_text=f"P2 Pension ({pension_start_age2:.0f})" if row == 1 else "",
                annotation_position="bottom"
            )

    # Add vertical lines for income schedule changes
    if income_schedule1:
        for idx, (age, income) in enumerate(income_schedule1):
            for row in [1, 2]:
                fig.add_vline(
                    x=age,
                    line_dash="dashdot",
                    line_color="blue",
                    opacity=0.5,
                    row=row, col=1,
                    annotation_text=f"P1 Income: ₪{income/1000:.0f}K" if row == 2 else "",
                    annotation_position="top right",
                    annotation_font_size=10
                )

    if income_schedule2:
        for idx, (age, income) in enumerate(income_schedule2):
            for row in [1, 2]:
                fig.add_vline(
                    x=age,
                    line_dash="dashdot",
                    line_color="lightblue",
                    opacity=0.5,
                    row=row, col=1,
                    annotation_text=f"P2 Income: ₪{income/1000:.0f}K" if row == 2 else "",
                    annotation_position="bottom right",
                    annotation_font_size=10
                )

    # Add markers for one-time events
    if one_time_events:
        for idx, (age, amount, description) in enumerate(one_time_events):
            event_type = "Income" if amount > 0 else "Expense"
            color = "green" if amount > 0 else "red"
            for row in [1, 2]:
                fig.add_vline(
                    x=age,
                    line_dash="dot",
                    line_color=color,
                    opacity=0.6,
                    row=row, col=1,
                    annotation_text=f"{description}: ₪{abs(amount)/1000:.0f}K" if row == 1 else "",
                    annotation_position="top left",
                    annotation_font_size=9
                )

    # Add vertical lines for expense schedule changes
    if expense_schedule:
        for idx, (age, expense) in enumerate(expense_schedule):
            for row in [1, 2]:
                fig.add_vline(
                    x=age,
                    line_dash="dashdot",
                    line_color="darkred",
                    opacity=0.5,
                    row=row, col=1,
                    annotation_text=f"Expense: ₪{expense/1000:.0f}K" if row == 2 else "",
                    annotation_position="bottom left",
                    annotation_font_size=10
                )

    fig.update_xaxes(title_text="Person 1 Age", row=2, col=1)
    fig.update_yaxes(title_text="Balance (NIS)", row=1, col=1)
    fig.update_yaxes(title_text="Monthly Amount (NIS)", row=2, col=1)

    fig.update_layout(
        height=800,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            x=1,
            y=0.5,
            xanchor='left',
            yanchor='middle'
        )
    )

    return fig
