# Version 1.5 regression tests

Run from the Version 1.5 application folder with Node.js 22 or later:

```sh
node --test tests/*.test.cjs
```

The suite uses only Node's standard library. It evaluates the actual JavaScript embedded in `index.html`, with isolated synthetic state and disabled startup/network activity. It does not open browser storage, synchronize GitHub, or load personal finance data.

The tests include ten frozen retirement scenarios captured before Phase 0, mathematical cash-conservation checks, all four conversion-tax funding methods, manual tax funding, withholding refunds, HSA deposits and restrictions, payroll deductions, survivor income, loss-year availability, legacy migration, reports, action-plan labels, Roth Lab, and Risk Lab. The deterministic mixed-scenario test covers 160 four-year projections and reconciles every fully funded year.

Baseline comparisons use a near-exact numerical tolerance except the conversion-withholding fixture, which allows the existing $0.50 solver tolerance. A passing baseline does not certify all tax law; it protects the specified existing behavior while targeted tests verify the corrections.

`fixtures/retired-baseline.json` contains synthetic inputs and selected original projection/report outputs. Its source SHA-256 identifies the original Version 1.5 file. Do not overwrite it with corrected outputs just to make a failing test pass. `capture-baseline.cjs` is an explicit maintenance tool for an original backup, not part of normal test execution.

To check another application file, set `MODEL_FILE` to its absolute path before running the suite. `model-harness.cjs` loads that file's actual main script. No separate copy of the financial engine is maintained in the tests.

## Phase 1: optional family timeline

The additional 36 tests cover opt-in defaults, old saved plans, stable identifiers, JSON round trips, exact birth dates, leap years, December 31 ages, inclusive period boundaries, ongoing periods, gaps, overlaps, partial years, independent residence/tax dependency/support/student periods, validation, future schema retention, HTML escaping, and conditional navigation.

`fixtures/phase1-retired-baseline.json` freezes complete projection rows, report rows, interview steps, and migration behavior for ten synthetic retirement scenarios from the app immediately before Phase 1. All ten must match exactly with the family extension absent, disabled, and enabled. Its source SHA-256 identifies that pre-Phase-1 file. Do not regenerate the fixture to conceal a regression.

Phase 0 and Phase 1 comprise 85 tests. Family planning records do not enter the financial projection engine. Passing these tests protects existing behavior; it does not add tax-credit, ACA, spending, or account-access calculations.

## Phase 2: optional health insurance and ACA

There are now **140 tests** across all three suites. The new 55 tests cover ACA MAGI, prior-year regional poverty guidelines, published 2026/2027 contribution rules, projected later-year assumptions, monthly quotes/credits, tax family versus coverage family, Medicare transition checks, funding feedback, all four conversion-tax methods, manual tax funding, optional navigation, reporting, and Risk Lab health-cost duplication. The 60-case deterministic financial check reconciles 236 funded years. A frozen boundary case protects the conservative full-premium fallback.

`fixtures/phase2-retired-baseline.json` freezes complete synthetic projection/report rows, interview steps and migrations from the Phase 1 app before Phase 2. Its SHA-256 identifies the source. Old results must remain exact with health absent/off. `fixtures/aca-boundary-case.json` is a separate synthetic health-funding stress case. Do not regenerate expected retired outputs to hide a regression.

See `../PHASE2_CHANGES.md` for feature scope, verified rule sources, assumptions, and limits. Financial engine tests use synthetic state only; personal browser storage and network sync remain disabled in the harness.

## Automatic ACA data updates

Run `node --test tests/*.test.cjs` (167 app tests) and `python3 -m unittest discover -s tests -p 'test_aca_update_monitor.py' -v` (21 collector tests). Both suites are offline. `aca-updates.test.cjs` validates every ACA record in `tax-updates.json` as well as synthetic future-year scenarios. `test_aca_update_monitor.py` tests response-year safeguards, supported IRS table parsing, all-region HHS checks, conflict handling and manifest preservation. The existing financial fixtures remain unchanged; migration comparisons separately exclude the new ACA data namespace. See `../ACA_UPDATES.md`.
