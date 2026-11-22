# Version 1.5 Phase 0 accounting corrections

Phase 0 corrects the current retirement calculation path. Early Retirement and Family features are not included. Existing saved plan inputs, tax tables, account settings, and backup files are retained.

## Corrections

- Surplus income is saved once. Amounts already sent to securities are removed from cash with either a zero or positive reserve target.
- HSA deposits are household-funded transfers. They increase funding required, reduce cash, and add only the amount that can be funded to the HSA. A deposit shortfall remains visible. Existing maturity restrictions are respected on HSA withdrawals.
- Pre-tax Section 125 payroll deductions reduce taxable wages and take-home pay once. Annual dollar deductions carry forward until changed; an entered zero stops them. Automatic withholding also accounts for Traditional 401(k) contributions.
- Excess withholding returns as a modeled tax-year refund, shown as negative Funded Tax. This is an annual cash-flow convention, not a prediction of a refund payment date.
- Outside-asset and separate-IRA conversion-tax payments remain cash outflows when ordinary tax funding is overridden. Tax withheld from a conversion reduces Net to Roth and is not charged against cash a second time.
- Account draws and conversions use balances after modeled annual growth, matching the existing end-of-year balance convention. Losses can no longer support withdrawals from assets that have already been lost. A calculated RMD exceeding available assets receives a separate warning.
- Wages, person-specific non-wage income, and employer contributions stop after the modeled death year. Any continuing survivor pension or other taxable income should be entered under the surviving person.
- Cash draws, HSA funding, and shortfalls appear in the dashboard action plan. A shortfall year no longer displays “Step 1 Funded.” A printable report no longer counts a conversion alone as spending funding.
- The calculation records solver convergence and warns when tax/funding estimates do not settle. Solver working variables are local to each projection.

## What existing users should expect

Corrected projected balances may be lower where the previous model duplicated surplus income, credited an unfunded HSA deposit, omitted payroll expenses, or overdrawn assets after losses. Refund recognition can increase balances in overwithheld wage years. These changes apply to current retired users as well as working households.

Keep HSA deposit amounts separate from household spending and payroll deductions. Costs entered as pre-tax payroll deductions should also be excluded from household spending. Otherwise the same payment would be entered twice.

The existing HSA field remains a cash-funded deposit. HSA contribution eligibility, contribution tax deductions, qualified-expense verification, and employer/payroll contribution classification are not added in Phase 0. Medicare premiums remain part of the household spending input when applicable; Phase 0 does not change the existing Medicare budget convention.

Annual payroll limits/rate updates, account-access law, ACA insurance, dependent credits, and detailed family accounts remain later work. The regression fixtures protect the covered calculations; they are not a complete certification of every tax assumption or every saved plan.

## Validation

49 automated tests pass, including ten original retirement fixtures and 160 deterministic four-year mixed retirement scenarios. Tests reconcile all 622 fully funded years in those mixed scenarios, verify all conversion tax-funding methods and manual overrides, and exercise report generation and legacy JSON migration. Browser checks with an isolated synthetic retiree verified the dashboard, cash-flow table, and year details, with no console errors.

Run `node --test tests/phase0.test.cjs` from this application folder. See `tests/README.md` for the test harness and baseline policy.
