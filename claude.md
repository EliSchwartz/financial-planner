
## Goal

Build a maintainable simulation tool to explore early-retirement scenarios by changing assumptions (income, spending, returns, pension rule, contributions, start ages). The tool must be in Python and easy to extend. Provide an interactive UI. Prefer a lightweight local web UI (HTML) powered by Python, or a notebook UI if that’s simpler. Avoid heavy frameworks unless clearly beneficial.

## Core requirements

1. **Python-first**:

   * Core logic in a plain Python module (no notebook-only code).
   * Clear data model for assumptions.
   * Deterministic simulation that can be unit tested.
2. **Interactive front-end** (pick one):

   * Option A: **Streamlit** app (recommended for simplicity).
   * Option B: **Gradio** app (also fine).
   * Option C: Flask/FastAPI + simple HTML form (only if you want full control).
3. **User can edit assumptions** via UI:

   * Ages: current age, retirement age, pension start age, end age.
   * Wealth now: liquid_now, pension_now, optional other buckets.
   * Cashflows while working: net income, spend, liquid savings, pension contributions, hishtalmut contributions.
   * Returns: real annual return (convert to monthly).
   * Pension rule: monthly income per 1M at pension-start; optionally allow it to be a function of age.
4. **Outputs**:

   * Earliest feasible retirement age (search in monthly steps).
   * Time series of liquid and pension balances by age.
   * Time series of pension income and liquid draw after pension start.
   * Key summary numbers: liquid at pension start, pension balance at pension start, pension monthly income, liquid at end age, failure reason if infeasible.
5. **Charts**:

   * Plot balances over time (liquid, pension).
   * Plot cashflows over time (liquid draw, pension income).
6. **Scenario comparison**:

   * Allow running multiple retirement ages and show a table of feasibility and key outputs.

## Model assumptions (baseline)

* Everything is in **real terms** (after inflation). One real annual return parameter.
* Monthly compounding:

  * `r_month = (1+r_annual)^(1/12) - 1`
* Phases:

  1. Work: liquid grows + contributions; pension grows + contributions.
  2. Bridge: after retirement until pension start, liquid pays full spending; pension just grows.
  3. Post pension start: pension income reduces required draw from liquid:

     * `pension_income_month = pension_income_per_million_month * (pension_balance_at_start / 1e6)`
     * `draw_after = max(spend_month - pension_income_month, 0)`
* Feasibility:

  * Liquid must never go below 0.
  * Liquid at end age must be >= 0.
* The model does not need taxes/fees initially, but design it so you can add them later (eg reduce return or add explicit deductions).

## Implementation details

### 1) Project structure

Create:

* `retire_sim/`

  * `__init__.py`
  * `model.py` (dataclasses and simulation)
  * `search.py` (earliest retirement solver)
  * `plots.py` (chart helpers)
  * `app.py` (UI entrypoint)
* Optional:

  * `tests/` with a few unit tests
  * `requirements.txt`

### 2) Data model

Use `@dataclass` for parameters, with types and defaults:

* Ages: `age_now`, `retire_age`, `pension_start_age`, `end_age`
* Returns: `r_annual_real`
* Monthly cashflows: `net_income_month`, `spend_month`, `contrib_pension_month`, `contrib_hishtalmut_month`
* Wealth now: `liquid_now`, `pension_now`
* Pension rule: `pension_income_per_million_month`

Include derived:

* `save_to_liquid_month = (net_income_month - spend_month) + contrib_hishtalmut_month`

### 3) Simulation function

Implement:

`simulate(retire_age: float, params: Params) -> Result`

Where `Result` contains:

* `ok: bool`
* `reason: str` (human readable)
* `df: pandas.DataFrame` with monthly rows:

  * columns: `month`, `age`, `phase`, `liquid`, `pension`, `pension_income`, `liquid_draw`
* `pension_at_start`, `pension_income_month`, `liquid_end`

Be explicit about timing convention:

* Use end-of-month contributions and withdrawals (document it).
* Use monthly loop with integer months:

  * `m_work = round((retire_age - age_now)*12)`
  * `m_bridge = round((pension_start_age - retire_age)*12)`
  * `m_post = round((end_age - pension_start_age)*12)`

Stop and return failure if liquid < 0.

### 4) Solver for earliest retirement age

Implement:

`find_earliest_retirement(params, min_age=None, max_age=None)`

* Search in monthly steps from `age_now` to `pension_start_age`.
* Return first feasible `retire_age`.
* Include edge case handling if none feasible.

### 5) UI requirements

In the UI:

* Input widgets for every parameter (numbers and sliders).
* Button: “Run simulation” for a chosen retirement age.
* Button: “Find earliest retirement age”.
* Show:

  * Summary metrics as cards/metrics.
  * Table of scenario comparisons.
  * Charts.

Include a “load defaults” and “export config”:

* Export assumptions to JSON.
* Import assumptions from JSON.

### 6) Maintainability

* Keep business logic separate from UI.
* Add docstrings, type hints, and simple tests.
* Avoid global state.
* Make it easy to plug additional income streams later:

  * Optional list of income events: `(start_age, end_age, amount_month)`
  * Optional one-time expenses at a given age.

## Acceptance criteria

* Running `python -m retire_sim.app` starts the UI.
* User can change numbers and instantly rerun.
* Earliest retirement age computation works and matches manual checks.
* Charts render correctly.
* Config export/import works.
* Code is readable and modular.

## Recommended tech choice

Prefer **Streamlit**:

* Minimal code, good widgets, fast iteration.
* If Streamlit isn’t allowed, use **Gradio**.
* Only use Flask/FastAPI if required.

## Deliverables

1. Full code for the tool (all files).
2. `requirements.txt`
3. Short README:

   * how to install
   * how to run
   * what each parameter means
   * example configuration

---

