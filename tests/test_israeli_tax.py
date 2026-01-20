"""
Tests for Israeli tax calculations.
"""

import pytest
from retire_sim.israeli_tax import (
    calculate_income_tax,
    calculate_national_insurance,
    calculate_monthly_tax_from_gross,
    calculate_net_from_gross,
    get_effective_tax_rate,
    tax_summary
)


class TestIncomeTax:
    """Test income tax calculations."""

    def test_zero_income(self):
        """Zero income should have zero tax."""
        assert calculate_income_tax(0) == 0.0

    def test_lowest_bracket(self):
        """Test income in lowest bracket (10%)."""
        annual_income = 50000  # Below 84,120
        expected_tax = 50000 * 0.10
        assert calculate_income_tax(annual_income) == pytest.approx(expected_tax)

    def test_second_bracket(self):
        """Test income in second bracket (14%)."""
        annual_income = 100000  # Between 84,120 and 120,720
        expected_tax = 8412 + (100000 - 84120) * 0.14
        assert calculate_income_tax(annual_income) == pytest.approx(expected_tax)

    def test_third_bracket(self):
        """Test income in third bracket (20%)."""
        annual_income = 150000  # Between 120,720 and 193,800
        expected_tax = 13536 + (150000 - 120720) * 0.20
        assert calculate_income_tax(annual_income) == pytest.approx(expected_tax)

    def test_high_income(self):
        """Test income in highest bracket."""
        annual_income = 1000000
        # Should use 50% bracket
        expected_tax = 229203 + (1000000 - 721560) * 0.50
        assert calculate_income_tax(annual_income) == pytest.approx(expected_tax)


class TestNationalInsurance:
    """Test National Insurance calculations."""

    def test_zero_income(self):
        """Zero income should have zero NI."""
        assert calculate_national_insurance(0) == 0.0

    def test_low_income(self):
        """Test income below threshold."""
        monthly_income = 5000
        expected_ni = 5000 * 0.0427
        assert calculate_national_insurance(monthly_income) == pytest.approx(expected_ni)

    def test_mid_income(self):
        """Test income above threshold but below cap."""
        monthly_income = 20000
        low_part = 7522 * 0.0427
        high_part = (20000 - 7522) * 0.1217
        expected_ni = low_part + high_part
        assert calculate_national_insurance(monthly_income) == pytest.approx(expected_ni)

    def test_above_cap(self):
        """Test income above cap."""
        monthly_income = 60000  # Above cap of 50,695
        # Should calculate on capped amount
        capped = 50695
        low_part = 7522 * 0.0427
        high_part = (capped - 7522) * 0.1217
        expected_ni = low_part + high_part
        assert calculate_national_insurance(monthly_income) == pytest.approx(expected_ni)


class TestMonthlyTax:
    """Test combined monthly tax calculations."""

    def test_typical_income_20k(self):
        """Test typical monthly income of 20K."""
        gross_monthly = 20000

        # Annual income: 240,000
        # In bracket: 193,800 - 269,280 (31% on excess)
        annual_income_tax = 28152 + (240000 - 193800) * 0.31
        monthly_income_tax = annual_income_tax / 12

        # NI on 20K monthly
        ni = 7522 * 0.0427 + (20000 - 7522) * 0.1217

        expected_total = monthly_income_tax + ni

        result = calculate_monthly_tax_from_gross(gross_monthly)
        assert result == pytest.approx(expected_total, rel=0.01)

    def test_net_from_gross(self):
        """Test net income calculation."""
        gross = 30000
        tax = calculate_monthly_tax_from_gross(gross)
        net = calculate_net_from_gross(gross)
        assert net == pytest.approx(gross - tax)

    def test_effective_rate(self):
        """Test effective tax rate calculation."""
        gross = 20000
        tax = calculate_monthly_tax_from_gross(gross)
        expected_rate = (tax / gross) * 100

        result = get_effective_tax_rate(gross)
        assert result == pytest.approx(expected_rate, rel=0.01)


class TestTaxSummary:
    """Test tax summary function."""

    def test_summary_structure(self):
        """Test that summary returns all expected fields."""
        summary = tax_summary(25000)

        required_keys = [
            'gross_monthly',
            'gross_annual',
            'income_tax_annual',
            'income_tax_monthly',
            'national_insurance_monthly',
            'total_tax_monthly',
            'net_monthly',
            'effective_rate_pct'
        ]

        for key in required_keys:
            assert key in summary

    def test_summary_values_consistent(self):
        """Test that summary values are mathematically consistent."""
        gross = 30000
        summary = tax_summary(gross)

        assert summary['gross_monthly'] == gross
        assert summary['gross_annual'] == gross * 12
        assert summary['income_tax_monthly'] == pytest.approx(summary['income_tax_annual'] / 12)
        assert summary['total_tax_monthly'] == pytest.approx(
            summary['income_tax_monthly'] + summary['national_insurance_monthly']
        )
        assert summary['net_monthly'] == pytest.approx(gross - summary['total_tax_monthly'])


class TestRealisticScenarios:
    """Test with realistic Israeli salary scenarios."""

    def test_average_salary(self):
        """Test with average Israeli salary (~12-13K/month)."""
        gross_monthly = 12500
        net = calculate_net_from_gross(gross_monthly)

        # Net should be roughly 80-85% of gross for this income level
        ratio = net / gross_monthly
        assert 0.78 < ratio < 0.87

    def test_high_tech_salary(self):
        """Test with high-tech salary (~30-40K/month)."""
        gross_monthly = 35000
        net = calculate_net_from_gross(gross_monthly)

        # Net should be roughly 60-70% of gross for this income level
        ratio = net / gross_monthly
        assert 0.58 < ratio < 0.72

    def test_pension_income(self):
        """Test pension income taxation."""
        # Pension income should be taxed same as work income
        pension_monthly = 15000

        pension_net = calculate_net_from_gross(pension_monthly)
        work_net = calculate_net_from_gross(pension_monthly)

        assert pension_net == pytest.approx(work_net)

    def test_low_income(self):
        """Test low income scenario."""
        gross_monthly = 6000
        net = calculate_net_from_gross(gross_monthly)

        # Low income should have lower effective tax rate
        ratio = net / gross_monthly
        assert 0.85 < ratio < 0.95  # 85-95% take-home
