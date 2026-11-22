# Version 1.5 — Phase 1: optional family and dependent timeline

Added November 22, 2026.

## Enable the option

Open **Setup Guide → Interview → Household**, expand **Optional family and dependent timeline**, and enable it. A **Family Timeline** tab then appears within Setup Guide. New and existing plans default to off. Turning it off hides the tab and retains all entries for later use. No interview steps were added.

## Included

- Dependent name, relationship, exact birth date, and notes.
- Separate periods for household residence, planned tax dependency, financial support, and student status. Each category supports multiple periods and gaps.
- Dates for residence, support, and student periods; inclusive first/last tax years for planned dependency. Blank ends mean ongoing. A missing period means **Not set**, not an inferred assumption.
- Annual ages at December 31, planned tax-dependent counts, people supported, partial-year markers, and period start/end milestones. Existing wage-ending and survivor milestones appear alongside the family timeline.
- Optional exact adult birth dates used only in this timeline. Without them, adult ages are approximated from the existing birth years and marked ~. A mismatch produces a warning and does not overwrite retirement inputs.
- Validation for invalid/reversed dates, periods before birth, and overlapping periods. Overlapping valid periods count a person only once.
- Entries are included in the app's existing JSON save, backup, import, and synchronization paths. Unsupported future family schema data is retained without interpretation.

## Preserved behavior and scope

The financial projection engine is byte-for-byte unchanged. The family option does not change spending, taxes, benefits, funding order, retirement-account access, existing age conventions, readiness scoring, or printed reports, even when enabled.

This is timeline planning only. Planned tax dependency is a user assumption, not an eligibility determination or ACA household-size calculation. Child tax credits, ACA coverage/subsidies, childcare and education costs, 529 accounts, debt schedules, insurance needs, and the Early Retirement Bridge remain later phases. Financial support periods record timing only; amounts will be added in a later phase.

## Validation

All **85 tests pass**: the existing 49 Phase 0 accounting tests and 36 Phase 1 tests. Ten frozen retirement scenarios match complete projection rows, report rows, interview steps, and applicable migration outputs exactly with family data absent, off, and on. Tests also cover date boundaries, independent periods, validation, legacy imports, and JSON round trips.

A synthetic browser check verified opt-in navigation, dependent editing, saved birth dates and dependency end years after reload, partial-year display, disabling/re-enabling without lost records, and no browser console errors. Existing user plan data was not used or changed during testing.

Run from the Version 1.5 folder with Node.js 22 or later:

```sh
node --test tests/*.test.cjs
```

The GitHub regression workflow now runs both suites.
