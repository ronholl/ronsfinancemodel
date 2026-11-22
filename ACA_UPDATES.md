# Automatic annual ACA data updates

Added November 22, 2026. The optional family and pre-Medicare features remain off by default. Medicare, IRMAA and ordinary income-tax calculations keep their existing rules.

## How this works for users

Tax Tables now includes an **ACA contribution percentages & poverty guidelines** panel with a separate coverage-year selector, source links, and independent Official/Entered/Projected status for each ACA section. It does not create an income-tax or Medicare table when an ACA year is added.

**Automatically apply validated official ACA figures** defaults to on. The app checks the public update manifest at most daily and accepts valid ACA-only updates. Other tax and Medicare sections still require the existing Review & Apply action. Turning automatic ACA updates off allows manual review/apply through the existing update picker. Saved entered/pinned ACA sections are protected from automatic replacement.

The app checks GitHub before its bundled fallback file, so an older local copy can still receive new public figures. Network failures retain cached/applied/built-in data. Routine source-check metadata does not mark an unchanged plan dirty or upload it to private plan storage. Parameter updates wait for the initial private-plan load, preserving the loaded plan's update preference.

Health & ACA and Tax Tables show the monitor's last official-source check. A check older than 35 days or a source/validation error produces a notice. Future sections remain Projected until the applicable published data is available. Premium and benchmark quotes remain household-specific inputs.

## Official sources and validation

The collector uses the [HHS poverty-guidelines API](https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines/poverty-guidelines-api) and [IRS Internal Revenue Bulletins](https://www.irs.gov/internal-revenue-bulletins). It sends no household or financial inputs.

For HHS, every response must match the requested guideline year, region and household size. The collector checks sizes 1–8 for all three regions and verifies the supported per-person arithmetic. The API can return the current year's data for an unpublished future year; that response is treated as **not yet published**, never as new-year data. The published guideline year is kept separate from its following ACA coverage year.

For IRS contribution percentages, the collector follows bulletin identifiers listed by the official index, reads the corresponding HTML editions, and extracts only the specifically titled coverage-year table. The six supported poverty-percentage bands and literal percentage cells must match the app's supported structure. A changed band structure, eligibility bound, conflicting table, or unexpected format requires review. The current parser does not implement new legislation or infer changed income/eligibility rules.

The manifest contains independent `acaContribution` and `acaPoverty` records, with coverage year, guideline year where applicable, official source URL, publication date when provided, deterministic record id, and source evidence hash. Existing federal, California, Medicare and IRMAA records are preserved. Independent sections can arrive at different times: a new poverty table does not make the contribution schedule Official for the same coverage year.

The app validates the records again before applying them. It requires approved official HTTPS sources, supported coverage years and fields, finite values, the supported six-band schedule, all three poverty regions, and the correct guideline-to-coverage-year relationship. Conflicting records for the same year/section are rejected.

## Projection rules

An exact published section is used for its coverage year. For an unpublished year, contribution percentages use the latest earlier available schedule, and poverty guidelines grow from the latest earlier coverage-year table at the plan's chosen rate. The app never applies a future table backwards. Each section's source year and projection status remain visible. A routine annual update changes data only; a change to ACA eligibility or the MAGI formula needs a reviewed app change.

## Scheduled maintenance

`.github/workflows/aca-data-updates.yml` checks sources weekly on Mondays at 15:23 UTC. It also runs on the initial deployment/relevant code changes and supports **Run workflow** in GitHub Actions. It:

1. Runs the collector's offline unit tests.
2. Fetches official HHS and IRS publications.
3. Updates only supported ACA records and the source-check status in `tax-updates.json`.
4. Runs the app regression suites against the resulting manifest.
5. Commits/pushes that one data file on `main` when checks pass.
6. Reports a failed workflow if sources need attention, after retaining prior figures and publishing the source-check warning.

Each weekly source check records a timestamp, providing ongoing repository activity even when figures do not change. GitHub can delay scheduled jobs and disables schedules after extended repository inactivity; the client freshness warning remains the fallback if the service stops running. [GitHub schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

The workflow needs the repository's normal Actions token with `contents: write` for this data-file commit. It uses no personal access token or paid AI/API service. It does not modify the app, workflows, or household plan files during scheduled runs. Branch protection or repository settings that prohibit bot pushes can prevent publication; the app then displays the overdue check instead of treating guessed figures as Official.

## Maintenance commands

```sh
node --test tests/*.test.cjs
python3 -m unittest discover -s tests -p 'test_aca_update_monitor.py' -v
python3 scripts/aca_update_monitor.py --manifest tax-updates.json --strict
```

The first two commands are offline. The third contacts official public sources and replaces the manifest atomically. An IRS rule/schema change requires reviewing the app and collector rather than loosening validation to accept an unknown table.

## Verification

The existing 140 tests pass. Twenty-seven new application tests cover validation, automatic/manual modes, protected data, partial publication, source years, later-year projection, old-year preservation, actual subsidy recalculation, import/export, stale monitor status, and unchanged retired-user outputs. Twenty-one collector tests cover real response formats, unpublished-year defaults, all-region/size checks, source restrictions, IRS parsing, schema changes, conflicts and manifest preservation.

A live source run verified the 2025/2026 HHS tables for 2026/2027 coverage and the published 2026/2027 IRS contribution schedules. HHS 2027 guidelines are currently pending publication; no 2028 figures have been invented or marked Official.

Browser verification confirmed the live-source manifest, independent Official/Projected year status, automatic/manual toggle persistence after reload, and no console errors, using a synthetic household on localhost.
