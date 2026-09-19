# Run23 Au+Au 200 GeV EPD Calibration — Deployment Summary

## 1. Scope

This document records the final calibration, QA, STAR DB deployment, and validation for the Run23 Au+Au 200 GeV EPD calibration covering Days 162–213.

The calibration workflow is archived in this repository. STAR production DB writes were performed from the RCF environment and independently validated by DB read-back.

## 2. Calibration workflow

The calibration chain is:

1. Fit the ADC spectrum for each physical EPD tile on each usable day.
2. Extract the daily first-MIP MPV and its uncertainty.
3. Group stable days into calibration periods.
4. Derive a period-level constant using the reviewed daily measurements.
5. Apply manual QA exclusions or replacements where justified.
6. Build a reviewed calibration candidate.
7. Export full DB snapshots at calibration change points.
8. Write `epdGain` / `epdStatus` tables to the STAR DB.
9. Validate every deployed change point by DB read-back.

Daily MPVs are intermediate measurements; the DB gain is normally the reviewed period-level calibration constant rather than the MPV from the first day of the period.

For Days 162–182, the reviewed period constants were produced by the Python period-QA workflow using inverse-variance weighted constants after manual QA.

Days 183–186 and 188–189 use the reviewed period-level reference values already available in `data/derived/period_references.csv`.

## 3. Final calibration periods and gain change points

| Calibration interval | DB gain change point | Notes |
|---|---:|---|
| Day162–168 | Day162 | reviewed period constant |
| Day169–175 | Day169 | reviewed period constant |
| Day176–182 | Day176 | reviewed period constant |
| Day183–186 | Day183 | reviewed period reference |
| Day187 | none | no usable calibration input; previous DB state persists |
| Day188–189 | Day188 | reviewed period reference |
| Day190–206 | Day190, with channel-level updates at Day191/192 | reviewed calibration candidate |
| Day207–208 | Day207 | new detector-wide calibration period |
| Day209–210 | none | no usable calibration input; previous DB state persists |
| Day211 | Day211 | day-level calibration |
| Day212 | Day212 | day-level calibration |
| Day213 | Day213 | day-level calibration |

Final `epdGain` DB change points:

`162, 169, 176, 183, 188, 190, 191, 192, 207, 211, 212, 213`

## 4. QA exceptions and manual corrections

### Persistent known-dead tiles

The following two physical tiles are treated as known dead throughout the calibration:

- EW1 PP1 TT6
- EW1 PP2 TT10

For these tiles:

- `epdGain`: MIP = 0, offset = 0
- `epdStatus`: status = 0

All other physical tiles have status = 1 in the final detector mask.

### Daily measurement replacements

Two daily observations were manually replaced before formation of their period constants:

- Day167, EW1 PP7 TT14:
  `132.324295 ± 0.485768`
- Day179, EW0 PP6 TT2:
  `116.307190 ± 1.289736`

These replacements contribute to the corresponding period-level constant and do not create independent DB change points.

### Manual DB offset overrides

Four gain-table entries carry reviewed non-zero offsets:

- Day211, EW1 PP10 TT17:
  MIP = `138.328827`, offset = `-126.5`
- Day211, EW1 PP10 TT18:
  MIP = `140.716248`, offset = `-120.5`
- Day211, EW1 PP11 TT19:
  MIP = `140.804016`, offset = `-118.5`
- Day212, EW1 PP10 TT19:
  MIP = `138.081131`, offset = `-137.5`

## 5. Raw-input-unavailable channels on Days 211–213

A block of 32 EW0 tiles had no usable raw daily calibration input on Days 211–213.

These tiles are **not** classified as bad or dead.

The final policy is state persistence:

> If no new calibration measurement is available for a tile, preserve the previous valid DB gain and status rather than replacing the gain with zero.

The previous valid state comes from the Day207 calibration snapshot.

This behavior is implemented by the stateful DB exporter. The final Day211–213 gain snapshots preserve the Day207 values for these 32 channels.

A precision correction was subsequently made so that the preserved values came from the original full-precision calibration snapshot rather than values truncated by an intermediate DB read-back printout.

Example:

- EW0 PP6 TT12 source value:
  `139.4482464305283`
- ROOT/DB float read-back:
  `139.448242188`

## 6. DB deployment

### Early-period store times

| Day | Store time GMT |
|---:|---|
| 162 | 2023-06-11 06:55:46 |
| 169 | 2023-06-18 04:02:29 |
| 176 | 2023-06-25 05:09:47 |
| 183 | 2023-07-02 04:49:35 |
| 188 | 2023-07-08 00:30:35 |

The store times were chosen relative to validated RunLog physics-run boundaries. When `run start - 60 s` would overlap the previous valid physics run, the timestamp was placed one second after the previous run stop.

### Later gain store times

The later Run23 deployment contains gain updates at:

- Day190
- Day191
- Day192
- Day207
- Day211
- Day212
- Day213

The final precision-corrected Day211–213 gain entries begin at:

- Day211: `2023-07-30 23:45:13`
- Day212: `2023-07-31 04:05:02`
- Day213: `2023-08-01 05:01:18`

The canonical final gain timestamp manifest is `data/derived/db_ready/gain_store_times_final.csv`.

`data/derived/db_ready/store_times_v2.csv` is retained as provenance for the preceding v2 correction timestamps (`23:45:12`, `04:05:01`, and `05:01:17`). The timestamps above are the final v3 precision-correction entries actually validated in the STAR DB.

## 7. Final DB validation

All deployed change points were validated by STAR DB read-back.

The final early-period `epdGain` validity chain is:

```text
Day162: 20230611.65546 -> 20230618.40229
Day169: 20230618.40229 -> 20230625.50947
Day176: 20230625.50947 -> 20230702.44935
Day183: 20230702.44935 -> 20230708.3035
Day188: 20230708.3035  -> 20230709.235431
```

Representative read-back checks confirmed:

- ordinary physical tiles have finite positive gain;
- EW1 PP1 TT6 and EW1 PP2 TT10 remain gain = 0;
- the same two tiles have status = 0;
- the 32 raw-input-unavailable Day211–213 tiles retain finite Day207 gain values;
- the four reviewed offset overrides are preserved;
- Day211–213 precision-corrected entries contain the expected ROOT float representation of the full-precision source values.

## 8. Calibration sources and contributors

This final calibration and DB deployment builds on and reviews earlier Run23 EPD calibration results produced within the STAR collaboration. Relevant calibration posts and source results include:

- **Yevheniia:** [EPD calibration](https://drupal.star.bnl.gov/STAR/blog/yuno/Epd-calibration) — earlier EPD calibration results used as source/reference input in the reviewed workflow.
- **Cameron:** [Run-23 EPD Calibrations, Days 169–175](https://drupal.star.bnl.gov/STAR/blog/cracz/Run-23-EPD-Calibrations-days-169-175) — source calibration results for the Days 169–175 period.
- **Erik:** [Run23 EPD Live Calibration, Days 183–189](https://drupal.star.bnl.gov/STAR/blog/eloyd/Run23-EPD-Live-Calibration-day-183-189) — period-level reference calibration results for Days 183–186 and 188–189.

The final Days 162–213 candidate documented here combines these source results with the reviewed daily fits, QA decisions, manual corrections, DB-state persistence rules, and final DB read-back validation described above.

The final STAR Drupal summary is available at:

[Run23 Au+Au 200 GeV EPD Calibration — DB Deployment Complete](https://drupal.star.bnl.gov/STAR/blog/dchen/Run23-AuAu-200-GeV-EPD-Calibration-%E2%80%94-DB-Deployment-Complete)

## 9. Deployment history note

The Day211–213 calibration was corrected in stages during deployment:

1. initial deployment;
2. correction of the 32 raw-input-unavailable channels to preserve the previous finite calibration state;
3. final precision correction using the original full-precision Day207 source values.

The final v3 Day211–213 gain entries supersede the earlier correction entries.

This history is retained deliberately for provenance rather than deleting the intermediate deployment evidence.

## 10. Reproducibility and archive

Primary local candidate:

`data/derived/candidate_v2/candidate_162_213.csv`

Stateful DB snapshot exporter:

`src/export_db_ready_v2.py`

This exporter implements state persistence for raw-input-unavailable channels and produced the reviewed v2 snapshots. The final Day211–213 v3 precision correction was performed on RCF using the original full-precision Day207 gain values and is documented in the deployment evidence archive.

Reviewed early-period QA products:

- `data/derived/qa_162_168_review_v3/`
- `data/derived/qa_169_175_v2/`
- `data/derived/qa_176_182_v3/`

Reviewed period references:

`data/derived/period_references.csv`

RCF DB deployment evidence archive:

`run23_epd_db_deployment_evidence_20260918.tar.gz`

SHA256:

`bb09d41f8153cb8ac03fbbea8b1f0f3a8a2263f80562ef0b4f0653ead33a9b73`

The archive contains DB-write logs, read-back evidence, and deployment macros used for the early-period and Day211–213 precision-correction writes.

## 11. Production status

**Run23 Au+Au 200 GeV EPD calibration for Days 162–213 is deployed and DB read-back validated.**

Remaining work is documentation and archival only; no outstanding calibration DB deployment is required for this range.
