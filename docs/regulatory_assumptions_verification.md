# Regulatory Assumptions Verification Report

**Date:** January 14, 2026
**Purpose:** Verify all Israeli tax and pension regulatory assumptions in the retirement simulation code against current regulations

---

## Summary

All major regulatory assumptions in the code are **verified as accurate** for 2025. Minor discrepancies noted below with recommendations for 2026 updates.

---

## 1. Income Tax Brackets

### Code Assumption (2025/2026)
```python
# Annual thresholds in ILS
₪0 - ₪84,120: 10%
₪84,120 - ₪120,720: 14%
₪120,720 - ₪193,800: 20%
₪193,800 - ₪269,280: 31%
₪269,280 - ₪560,280: 35%
₪560,280 - ₪721,560: 47%
Above ₪721,560: 50%
```

### Verification Status: ✅ **VERIFIED for 2025**

**Sources:**
- [PWC Israel Tax Summaries](https://taxsummaries.pwc.com/israel/individual/taxes-on-personal-income)
- [CWS Israel Tax Changes 2026](https://www.cwsisrael.com/israeli-tax-changes-2026-complete-guide/)

**Notes:**
- 2025 brackets are correct as coded
- **⚠️ 2026 UPDATE NEEDED:** The Israeli government approved widening tax brackets for 2026:
  - 20% bracket expanded to cover income up to ₪228,000/year (₪19,000/month)
  - 31% bracket now starts at ₪228,000 instead of ₪193,800
  - 35% bracket raised to ₪301,200/year (₪25,100/month) from ₪269,280
  - Workers earning ₪19,000/month will save ₪400-800/month in tax
- Tax brackets frozen (not adjusted for inflation) through 2027

---

## 2. National Insurance (Bituach Leumi + Health Insurance)

### Code Assumption
```python
# Employee contributions (combined NI + Health)
Up to ₪7,522/month: 4.27% (1.04% NI + 3.23% Health)
Above ₪7,522/month: 12.17% (7.00% NI + 5.17% Health)
Cap at ₪50,695/month
```

### Verification Status: ✅ **VERIFIED for 2025**

**Sources:**
- [CWS Israel National Insurance 2025](https://www.cwsisrael.com/national-insurance-bituach-leumi-and-health-tax-in-2025/)
- [Bituach Leumi Official Rates](https://www.btl.gov.il/English%20Homepage/Insurance/Ratesandamount/Pages/forSalaried.aspx)

**Breakdown Confirmed:**
- **Low rate (4.27%):** NI 1.04% + Health 3.23% = 4.27% ✓
- **High rate (12.17%):** NI 7.00% + Health 5.17% = 12.17% ✓
- **Threshold:** ₪7,522/month (60% of average wage) ✓
- **Cap:** ₪50,695/month ✓

**Notes:**
- Rates effective as of February 1, 2025
- Threshold of ₪7,522 represents 60% of the average wage in Israel
- No contributions on income above cap

---

## 3. Mandatory Pension Contributions

### Code Assumption
```python
Employee contribution: 6% of gross (deducted from salary)
Employer contribution: 12.5% of gross (not deducted)
Total pension accumulation: 18.5% of gross
```

### Verification Status: ✅ **VERIFIED**

**Sources:**
- [CWS Israel Payroll Updates 2025](https://www.cwsisrael.com/2025-israeli-payroll-updates/)
- [Playroll Israel Payroll Guide](https://www.playroll.com/payroll/israel)

**Breakdown Confirmed:**
- **Employee:** 6% towards pension (deducted from paycheck) ✓
- **Employer:** 12.5% total
  - 6.5% towards pension funding
  - 6.0% towards severance (pitzuim) funding
- **Total accumulation:** 18.5% ✓

**Notes:**
- This 18.5% rate has been in effect since January 2018
- Contributions calculated on salary up to ₪50,695/month cap
- Employees become eligible after 6 months of employment (or immediately if they already hold a pension fund)
- Mandatory by Israeli law for all salaried employees

---

## 4. Hishtalmut (Keren Hishtalmut / Study Fund)

### Code Assumption
```python
Contribution rate: 6% of gross income
Monthly cap: ₪1,600
```

### Verification Status: ⚠️ **PARTIALLY VERIFIED - SIMPLIFIED**

**Sources:**
- [Blue & White Finance Keren Hishtalmut Guide](https://bluewhitefinance.com/the-ultimate-guide-to-keren-hishtalmut/)
- [CWS Israel Payroll Updates 2025](https://www.cwsisrael.com/2025-israeli-payroll-updates/)

**Actual Structure:**
- **Common split:** 2.5% employee + 7.5% employer = 10% total
- **Tax benefit salary cap:** ₪15,712/month in 2025
- **Maximum monthly deposit:** ₪1,571 (≈₪1,600 in code)

**Discrepancy:**
- Code uses simplified 6% rate (not 10% split)
- Code cap of ₪1,600 is close to actual max of ₪1,571

**Assessment:**
- The ₪1,600 cap is accurate as an approximation
- The 6% rate appears to be a simplification (actual is typically 10% combined)
- **Recommendation:** Code comment should clarify this is a simplified assumption
- For conservative estimation, using lower contribution rate is acceptable

---

## 5. Old Age Pension (Bitachon Zikna - קצבת זקנה)

### Code Assumption
```python
Monthly amount: ₪2,000 per person
Start age: 70 (no income test)
Tax treatment: Tax-free
```

### Verification Status: ✅ **REASONABLE APPROXIMATION**

**Sources:**
- [Bituach Leumi Old Age Pension Rates](http://www.btl.gov.il/English%20Homepage/Benefits/Old%20Age%20Insurance/Pages/Pensionrates.aspx)
- [Shivat Zion Old Age Pension Guide](https://shivat-zion.com/information-portal/finances/old-age-pension/)

**Actual Amounts (2025):**
- **Basic pension (under 80):** ₪1,896/month
- **Seniority increment:** +2% per year of contributions (max 50%)
- **With full seniority:** ₪1,896 × 1.5 = ₪2,844/month
- **Health insurance deduction:** -₪231/month per person

**Age Eligibility:**
- Men: Age 67
- Women: Age 62-65 (gradually increasing to 65 by 2032)
- **At age 70:** Pension granted without income test ✓

**Assessment:**
- Code assumption of ₪2,000 at age 70 is reasonable
- Actual amount varies based on work history (₪1,665 to ₪2,844 after health deduction)
- Using age 70 (no income test) is conservative and correct
- Old age pension is generally not subject to income tax ✓

---

## 6. Pension Income Tax Exemption

### Code Assumption
```python
Pension tax-free amount: ₪5,000 per person per month
```

### Verification Status: ⚠️ **APPROXIMATE - NEEDS 2025 CLARIFICATION**

**Sources:**
- [Israel Tax Agency Pension Guidelines 2025](https://news.bloombergtax.com/daily-tax-report-international/israel-tax-agency-issues-guidelines-regarding-tax-exemption-for-qualifying-pensions)
- [JPost Tax Guide](https://www.jpost.com/business-and-innovation/banking-and-finance/article-880103)

**Actual Exemption (Gradual Phase-In):**
- **2023:** ~₪4,399/month
- **2025:** Between ₪4,399 and ₪5,422 (exact amount unclear)
- **2026:** ₪5,422/month
- **2027:** ₪5,893/month
- **2028+:** ₪6,318/month (67% of ₪9,340)

**Assessment:**
- Code assumption of ₪5,000 is reasonable for 2025
- Likely slightly higher than actual 2025 amount but within range
- **Recommendation:** Update to ₪5,422 for 2026
- Exemption applies to qualifying pension income (not all pension types)

---

## 7. Pension Start Ages (Default Values)

### Code Assumption
```python
Person 1 (Male): 67
Person 2 (Female): 65
```

### Verification Status: ✅ **CORRECT for 2025**

**Sources:**
- [WIS Israel Retirement Age Guide](https://wis.it.com/what-is-the-average-retirement-age-in-israel)
- [Bituach Leumi Retirement Age](https://www.btl.gov.il/English%20Homepage/Benefits/Old%20Age%20Insurance/Conditions/ageofentitlement/Pages/ARetirementage.aspx)

**Official Retirement Ages (2025):**
- **Men:** 67 ✓
- **Women:** Progressive increase from 62 to 65 (2022-2032)
  - Born 1960-1964: 62-64 (gradual)
  - Born 1965-1969: 63.75-64.75
  - Born 1970+: 65 ✓
- Default of 65 for women is correct for current planning

---

## 8. Other Model Assumptions (Non-Regulatory)

### Investment Returns
```python
Real annual return: 4% (default)
```
**Status:** User-configurable parameter, not a regulation

### Mekadem (Pension Withdrawal Divisor)
```python
Default: 230
```
**Status:** This is a pension fund parameter, varies by fund and age
- Typical range: 180-240
- Code default of 230 is reasonable and conservative
- Higher mekadem = lower monthly income

### Minimum Assets Constraint
```python
Default: ₪1,000,000
```
**Status:** User preference, not a regulation

---

## Recommendations for Code Updates

### Immediate (Critical)
None - all core assumptions are accurate for 2025

### For 2026 Release
1. **Update income tax brackets** (approved changes for 2026):
   - 20% bracket: up to ₪228,000 annual (₪19,000/month)
   - 31% bracket: starts at ₪228,000
   - 35% bracket: starts at ₪301,200 (₪25,100/month)

2. **Update pension tax exemption:**
   - Change from ₪5,000 to ₪5,422/month

### Documentation Improvements
1. **Hishtalmut assumption:** Add comment explaining 6% is simplified (actual often 10%)
2. **Pension exemption:** Add note about gradual phase-in schedule
3. **Old age pension:** Add note explaining ₪2,000 represents average with seniority

---

## Compliance Summary

| Assumption | 2025 Status | 2026 Action Needed |
|-----------|-------------|-------------------|
| Income tax brackets | ✅ Accurate | ⚠️ Update brackets |
| National Insurance rates | ✅ Accurate | Monitor for changes |
| Pension contributions (18.5%) | ✅ Accurate | No change expected |
| Hishtalmut cap (₪1,600) | ✅ Reasonable | Monitor salary cap |
| Old age pension (₪2,000) | ✅ Reasonable | Monitor annual adjustment |
| Pension tax exemption (₪5,000) | ⚠️ Approximate | Update to ₪5,422 |
| Pension start ages (67/65) | ✅ Correct | No change expected |

---

## Data Sources

### Official Government Sources
- [Bituach Leumi (National Insurance Institute)](https://www.btl.gov.il/English%20Homepage/Pages/default.aspx)
- [Israeli Government Tax Information](https://www.gov.il/en/pages/income-tax-monthly-deductions-booklet)

### Professional Tax Services
- [PWC Israel Tax Summaries](https://taxsummaries.pwc.com/israel)
- [CWS Israel Tax & Payroll Updates](https://www.cwsisrael.com)

### Financial Planning Resources
- [Blue & White Finance](https://bluewhitefinance.com)
- [Nefesh B'Nefesh Tax Information](https://www.nbn.org.il/life-in-israel/finances/taxes/)

---

## Annual Update Checklist

Use this checklist when updating tax assumptions for a new year:

- [ ] Verify income tax brackets (usually announced Q4 previous year)
- [ ] Check National Insurance rates and thresholds (updated annually in January/February)
- [ ] Confirm pension contribution rates (rarely change, but verify)
- [ ] Update old age pension amounts (adjusted annually)
- [ ] Check pension tax exemption phase-in schedule
- [ ] Verify retirement age changes for women (gradual until 2032)
- [ ] Review Hishtalmut salary cap for tax benefits
- [ ] Run test suite to verify calculations
- [ ] Update documentation (README.md, tax_documentation.md)

**Last Verified:** January 14, 2026
**Next Review Due:** January 2027 (for 2027 tax year)
