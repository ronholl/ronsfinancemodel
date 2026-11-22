# Version 1.5 — Phase 2: optional pre-Medicare health insurance and ACA

Added November 22, 2026.

## Enable and use

1. Reload the existing Version 1.5 app. Open **Setup Guide → Interview → Household**, expand **Optional pre-Medicare health insurance & ACA**, and enable it.
2. Open the new **Health & ACA** tab. Review tax household size, poverty-guideline region, and any excluded foreign income or required-filer dependent income. Confirm those assumptions before estimating assistance.
3. Add coverage groups with inclusive first/last months, household-paid gross premiums, a quoted eligible benchmark silver-plan premium, an additional medical budget, and the people covered. Confirm Marketplace eligibility for the specific people and months. Other plan types budget costs without Marketplace credits.
4. Review the monthly calculation and year-by-year summary. Year-specific household-size and income entries support changes over time. Split/requote a coverage group when a member changes plans, enters Medicare, or leaves the tax family.

**Enter additional costs only.** Net premiums and the medical budget are added to the existing Annual Spending requirement. Remove the same costs from the ordinary spending inputs first. Do not re-enter premiums already deducted from paychecks. Coverage expenses remain budgeted until the entered end month; they do not automatically disappear at age 65.

The option defaults to **off**, independently of the Family Timeline option. Turning it off preserves all entries and restores existing retirement calculations. Both namespaces are included in the existing JSON backup/import and saved-state paths. The interview still has the same steps.

## Calculation rules

- **ACA household MAGI** uses projected current-year AGI plus tax-exempt interest, nontaxable Social Security, excluded foreign income, and entered MAGI of tax dependents required to file. Taxable dividends, interest, realized gains, traditional retirement-account distributions, and Roth conversions enter through AGI. Returned brokerage basis and distributions the existing model treats as qualified Roth or HSA withdrawals do not add income by themselves. [HealthCare.gov income guidance](https://www.healthcare.gov/income-and-household-information/income/)
- Tax family size differs from the number insured: a Medicare-covered spouse and tax dependents can still count. Household size can derive from annual filing status plus the Phase 1 planned tax-dependent periods, or be entered explicitly. Missing/invalid dependency assumptions suppress assistance until corrected or overridden. An unmarried partner is not automatically added to the tax family. [IRS tax-family and household-income definitions](https://www.irs.gov/instructions/i8962)
- Assistance is estimated **month by month**, using the lesser of eligible premiums or the positive difference between the eligible quoted benchmark and one household monthly contribution. Multiple policies share that contribution once. Assistance offsets premium spending in the coverage year; it is not deducted again from modeled income tax. The result assumes assistance is received during the coverage year. [IRS monthly-credit formula](https://www.irs.gov/instructions/i8962)
- The separate 2026 and 2027 contribution schedules come from [IRS Revenue Procedure 2025-25](https://www.irs.gov/irb/2025-32_IRB) and [IRS Revenue Procedure 2026-26](https://www.irs.gov/irb/2026-31_irb). Coverage-year poverty guidelines use the prior calendar year's figures, with separate 48-state/DC, Alaska, and Hawaii tables. [HHS guidelines](https://aspe.hhs.gov/poverty-guidelines/), [2025 official tables](https://public-inspection.federalregister.gov/2025-01377.pdf), [2026 official tables](https://public-inspection.federalregister.gov/2026-00755.pdf)
- Coverage after 2027 is explicitly a **projection assumption**: 2027 contribution percentages continue, while poverty guidelines grow at the entered annual rate (default 2.5%). Quotes and medical budgets use their own entered growth rate. Coverage before 2026 receives no calculated federal assistance.
- Ordinary estimates assume no credit below 100% or above 400% of the guideline. Below-threshold special cases, Medicaid/CHIP, employer affordability, and other eligibility must be reviewed separately. Estimates interpolate contribution rates continuously; they do not reproduce Form 8962 tax-form rounding.
- Health costs, funding withdrawals, income taxes, and assistance are solved together. Funding uses normal account order and existing Roth conversion tax rules. Manual Funded Tax overrides still allow health-cost feedback to settle. The existing Income Level conversion target uses calculated ACA MAGI when this option is on; Medicare/IRMAA targeting retains its existing basis.
- A yearly ACA MAGI override fixes the assistance income input; it does not change taxes, Medicare MAGI, cash receipts, or the calculated income used to size conversions. Finalized Year-End Closeout Medicare MAGI remains a lookback input. Enter an explicit ACA override when an actual ACA household-income figure should replace the projection.
- Cycles near a subsidy/funding boundary fall back to budgeting full premiums with **zero assistance used**, with a clear review warning. An unresolved tax/funding solve remains flagged. Invalid quoted costs are marked incomplete instead of being presented as a complete funded plan; Risk Lab refuses incomplete or unsettled health calculations.

## Medicare/IRMAA preservation

The Medicare/IRMAA helper and the existing two-year lookback, survivor-relief, surcharge, and Part B calculation blocks are unchanged. `magi`, historical MAGI inputs, and Year-End Closeout Medicare MAGI retain their existing meanings. New `acaMagi` and health details live separately.

Exact Family Timeline birth dates can identify Medicare eligibility months for the new assistance checks, including first-of-month birthdays. Without exact birth dates, checks use the existing annual age convention. They do not alter existing Medicare timing, premiums, or IRMAA. If a quoted group still includes a person at Medicare timing, assistance is withheld for the affected group/month and a split/requote warning appears; gross premiums remain budgeted. Continue entering Medicare premiums in the ordinary budget as before. [Medicare coverage timing](https://www.medicare.gov/basics/get-started-with-medicare/sign-up/when-does-medicare-coverage-start)

When enabled, new health costs can legitimately change withdrawals and future MAGI, and therefore later IRMAA **amounts** through the existing rules. With the option off, existing outputs match exactly.

## Reporting and related workflows

- Health & ACA shows monthly coverage, ACA MAGI components, family size, FPL percentage, contribution rate, and assumption warnings.
- Dashboard action-plan cards and Year Detail explain health costs already included in Spending.
- Cash Flow and the printed report include a health/ACA summary only when enabled.
- Family Timeline edits recompute ACA household assumptions when health modeling is enabled.
- SOY spending defaults and Risk Lab use ordinary household spending before the health addition, preventing duplicate premiums. Risk Lab recomputes assistance for each simulated path while coverage quotes retain their entered growth assumptions.

## Limits of this phase

This is a planning estimate, not a Marketplace eligibility determination or tax-return/APTC reconciliation. It does not model actual advance-credit payments and repayments, state assistance, cost-sharing reductions, Medicaid/CHIP benefit amounts, HRA offsets, shared-policy tax allocations, special below-poverty eligibility, or the self-employed health-insurance deduction/PTC interaction. Confirm those situations outside this estimate; do not mark a coverage group eligible when a disqualifying condition applies.

This phase preserves existing retirement-account accessibility, Roth distribution, and HSA qualification assumptions. It does not yet validate pre-59½ account access, Roth basis/conversion histories, SEPP, or qualified HSA reimbursements. Ordinary Marketplace premiums generally are not eligible tax-free HSA expenses. Those account-access improvements remain Phase 3. [IRS HSA guidance](https://www.irs.gov/publications/p969)

## Verification

All **140 tests pass**: the existing 85 tests plus 55 Phase 2 tests. Ten frozen retirement scenarios compare complete projection rows, report rows, interview steps, and financial migration behavior exactly with health data absent or disabled. Original fixtures were not regenerated. The Phase 1 migration assertion now separately checks the new disabled health namespace while retaining its exact financial-state comparison.

New tests cover MAGI addbacks and exclusions, 2026/2027 rates, regional/prior-year FPL, subsidy boundaries, partial-year coverage, multiple policies, dependent/partner treatment, mixed Medicare/Marketplace couples, birthday timing, confirmations, invalid inputs, quote growth, annual overrides, conversions and all four conversion-tax funding methods, manual tax funding, cash conservation, Risk Lab duplication, reports, and import escaping. A deterministic set of 60 four-year scenarios reconciled all 236 fully funded health-insurance years. A frozen cutoff-cycle case verifies the conservative fallback and review status.

Synthetic browser checks verified opt-in/off navigation, eligibility confirmations, premium edits, adding/removing a coverage period, incomplete-input warnings, saved entries after reload, family-dependency edits flowing into ACA family size/assistance, exact restoration of ordinary Spending after disabling, re-enabling retained entries, and Cash Flow summary values. No browser console errors were observed. Existing user plan storage was not used or changed.

Run from the Version 1.5 application folder using Node.js 22 or later:

```sh
node --test tests/*.test.cjs
```

The existing GitHub regression workflow already runs all test suites.
