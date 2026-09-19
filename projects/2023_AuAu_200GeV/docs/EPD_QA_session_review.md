# EPD calibration: evidence review and next executable step

Date: 2026-09-17. Scope: Run23 Au+Au 200 GeV, candidate_v1 preparation.

**A usable candidate_v1 has not yet been produced.** The code and existing QA plots have been reviewed, and a runnable QA script has been prepared. The current environment does not contain the original Day190 ADC spectra or the complete daily/period numerical tables, so it is not yet possible to perform real-data refits, rank the full detector, or accept calibration constants.

## 1. Verified findings

| Finding | Evidence and interpretation |
|---|---|
| Day190 EW0 PP1 TT1 has a very low daily MPV with a small uncertainty | Saved output from the remote notebook shows `30.02668 ± 0.468794`, flagged as `different_from_nominal`. This is consistent with the handoff, but the number alone is not sufficient to conclude that the original spectrum fit failed. |
| The period constant of approximately 87.6 still needs an independent recalculation | The value 87.6 comes from the handoff. Without the complete daily measurements and their uncertainties, the Day190 weight fraction and corrected constant cannot be recomputed here. |
| The 207–208 deviations are not limited to a single tile | All 24 overview pages of `ADCDelta_190_208.pdf` were reviewed. Multiple sectors on both sides show groups of relatively large absolute residuals during the final two days. This is evidence that a common change should be investigated, but it is not yet evidence for a detector-wide split. |
| Day193 contains more extreme numerical anomalies | Saved notebook output records an MPV of approximately `8.588179e21` with an uncertainty of approximately `1.414214` for EW1 PP11 TT26. On page 23 of the PDF, the corresponding color scale reaches the `10^21` level, making changes in other tiles almost invisible. |
| Nominal-value flags depend on the actual code version used | The remote `FindNmip.C` uses nominal=115 for TT1 and flags deviations larger than 15, while the handoff reports values around 103–109 for Days 191–206 that were still flagged. The actual Run23 code version is therefore required; the remote parameters must not be assumed to be the production parameters. |

The PDF plots `abs(daily MPV - period constant)`, so it cannot be used to determine the sign of a change. Each page also uses an automatic color scale; a large blue region must not be interpreted as evidence that a sector is stable. Common changes should be checked with signed daily differences and cross-checked against run/hardware records and the fitted spectra.

## 2. First review targets (not a complete ranking)

These entries come from the handoff, saved notebook output, and the PDF. Values shown in the notebook may be rounded; the original numerical files should be treated as authoritative. All entries below are `manual_review`; none of them is used by itself to classify a tile as bad.

| Priority | Day / tile | Current evidence | Next step |
|---|---|---|---|
| First diagnostic | 190 / EW0 PP1 TT1 | MPV≈30.02668, uncertainty≈0.468794 | Open the ADC spectrum and determine what the automatic fit selected. If refit, record the old value, new value, and fit settings. |
| Extreme-value check | 193 / EW1 PP11 TT26 | MPV≈8.588179e21, uncertainty≈1.414214 | Review the spectrum, fit status, covariance, and input provenance first. |
| Extreme-value check | 193 / EW1 PP11 TT27 | MPV≈−2.752833e11 | This cannot be used as a positive physical calibration MPV. Preserve the record and review the source and fit. |
| Extreme-value check | 193 / EW1 PP7 TT24 | MPV≈1.142534e5, uncertainty≈1.414214 | Corresponds to page 19 of the PDF; review the fit. |
| Extreme-value check | 193 / EW1 PP12 TT1 | MPV≈6.432941e5, uncertainty≈1.414214 | Corresponds to page 24 of the PDF; review the fit. |
| Later period | 211 / EW1 PP11 TT20; 212 / EW1 PP10 TT20 | Notebook records approximately 3.961828e19 and 1.063701e7 | Review these together before the 211–213 constant fit. |
| Period change | 207–208 / multiple sectors on both sides | PDF shows evidence of a common deviation; target-tile values around 134–137 come from the handoff | Compute signed median shifts and the fraction of same-direction tiles per sector, then combine with run logs to decide whether a split is justified. |

## 3. Runnable QA script

File: `epd_period_qa.py`. It requires only the Python 3 standard library and does not depend on ROOT, pandas, or numpy.

From `projects/2023_AuAu_200GeV/`, after placing the script in `src/`, run:

```bash
python3 src/epd_period_qa.py data/derived/daily_observations_primary.csv \
  --start 190 --end 208 --split-day 207 \
  --out data/derived/qa_190_208_v1
```

It also supports the original flagged daily TXT files or six-column merged daily TXT files:

```bash
python3 src/epd_period_qa.py NmipConstantsDays190_208.txt \
  --start 190 --end 208 --split-day 207 --out qa_190_208_v1
```

**Prefer a daily CSV that preserves `auto_flag`, or the original daily TXT.** A numerically cleaned file cannot recover flags that were already removed; the script records those cases as `unknown_qa`. Do not use period constants such as `Nmip_Day_190.txt` as input. The output directory must not already exist, to prevent overwriting a previous QA run.

| Output file | Contents |
|---|---|
| `period_qa.csv` | For all 744 tiles: constant, constant_error, chi2, ndf, chi2_ndf, maximum residual, maximum weight, missing/flagged days, status, and related fields. |
| `tile_qa_queue.csv` | Tile review queue sorted by priority, chi2/ndf, and maximum residual, including missing coverage. |
| `manual_qa_queue.csv` | Tile-day review queue sorted by priority and leave-one-out constant shift, preserving input filename and line number. |
| `input_audit.csv` | Every raw input row in the requested period, including the reason for any numerical exclusion. |
| `sector_step_diagnostic.csv` | For each sector, the signed median shift across the requested split-day and the number of tiles changing positively/negatively beyond threshold; it does not perform a split. |
| `qa_run.json` | Input and script SHA-256, thresholds, period, row counts, and status counts for reproducibility. |

### Statistical and status conventions

- The constant is an inverse-variance weighted constant fit under the assumption of independent errors. `constant_error` is only the statistical uncertainty of that model; it does not include systematic uncertainty and is not inflated for high chi2.
- **Positive finite MPVs carrying `fit_failed` / `different_from_nominal` still enter the diagnostic constant** so that the impact of the original result is visible, while the observation is explicitly queued for review. This does not mean the calibration is accepted.
- Non-finite or non-positive MPVs, and non-finite or non-positive uncertainties, are excluded from the weighted fit and the reason is retained in the audit. A large but finite uncertainty does not by itself trigger exclusion.
- There is no sigma clipping, uncertainty floor, automatic replacement, automatic acceptance, or automatic split. Removing a single day is used only for leave-one-out diagnostics.
- If ndf=0, or if there are no usable fit points, chi2/ndf is left blank rather than written as 0. A missing tile receives a blank constant rather than a zero-filled value.
- Status values are limited to `provisional`, `manual_review`, and `missing`. `accepted` and `bad` are reserved for later evidence-based review decisions.
- The default thresholds of 10 ADC, 6σ, chi2/ndf>5, and maximum weight greater than 5 times the uniform weight are configurable **review thresholds**, not validated physics acceptance cuts. The leave-one-out pull is also not a multiple-comparison-corrected significance.
- The split-day diagnostic compares medians from the two subperiods and requires at least two numerically valid points on each side. It can flag a step/drift, but it cannot distinguish a real detector change from a fitting-algorithm change or a change in run conditions.

Validation: cross-checked against an independent numpy weighted least-squares calculation. Tests passed for synthetic outlier influence/ranking, two-period shifts, invalid values/zero uncertainty, single-point ndf handling, 744-tile missing coverage, duplicate-row and malformed-input rejection, period-input rejection, and overwrite protection. **It has not yet been run on the complete real dataset and has not yet been directly compared with a ROOT execution.**

## 4. Improvement points for the existing DayFitsHistos.C

The review used the currently uploaded version of the code and did not overwrite it.

1. It computes `tChi2` and `tAveErr` but does not write them to the output. The sixth column of `Nmip_Day_*` is hard-coded to `0.0`. This zero is an output placeholder, not a measured zero uncertainty.
2. It reads a fixed `744 × days × 6` values without checking file-open/read success, duplicate keys, or index ranges. Missing rows or interrupted formatting could allow zero values to enter later indexing. This is an input-validation issue that should be fixed; it is not evidence that the current complete dataset is already affected.
3. If the period fit fails, it falls back to a simple mean and stores chi2/ndf as 0 in memory without saving the failure state together with the constant. A downstream candidate must not treat such a result as a normal successful fit.
4. The original daily flags should be preserved in a separate table. The new script already provides sidecar QA outputs without requiring modification of the ROOT macro.

## 5. candidate_v1 coverage checklist

The availability shown below comes from the handoff and **is not a validation of the complete constants performed in this review**. The complete numerical tables were not available in the current environment, so no 744-tile constants or accepted states were fabricated.

| Period | Source | Handoff status | Work required before candidate |
|---|---|---|---|
| 162–168 | Yevheniia | reviewed daily | Obtain the complete data and perform the period fit; clarify whether the primary analysis range begins only at Day167. |
| 169–175 | Cameron | period result + badTiles | Read the period table and badTiles while preserving per-tile QA; an existing collaborator result does not imply that every tile is accepted. |
| 176–182 | Ding | 744 constants + PDF | Obtain the numerical table, compute QA from the daily data, and confirm manual revisions. |
| 183–186 | Erik | period result | Read `Nmip_Day_183.txt` together with the related refits and QA. |
| 187 | — | no data | Record a no-data gap; do not fabricate a calibration or automatically extend validity across the gap. |
| 188–189 | Erik | period result | Interpret `Nmip_Day_189.txt` as the 188–189 period and read the associated QA. |
| 190–208 | Ding | 744 constants + PDF, with clear anomalies | Complete the Day190 and Day193 reviews and the 207–208 range diagnostic; keep the split decision pending until supported. |
| 209–210 | — | locally unavailable | Record the missing interval; recover the data or obtain an evidence-based validity decision. |
| 211–213 | Ding | daily available | Perform extreme-fit QA, period fitting, and documented manual review. |

The final fields should retain the handoff schema `period_start, period_end, ew, pp, tt, calibration_mpv, source, status, qa_flag, notes`, with recommended additions `constant_error, source_file, input_sha256, review_record`. All manual fixes should be explicit replacements keyed by `(day, ew, pp, tt)` with the previous value retained; raw and revised data must not simply be concatenated into duplicate rows.

## 6. Files required to unlock the next step

Provide these first:

1. **Day190.root** (or a ROOT file containing `AdcEW0PP1TT1`). For spectrum inspection only, page 1 of `ADCspectraDay190.pdf` is sufficient; in the remote macro layout the target tile is in pad 2. An actual refit requires the histogram data.
2. **The actual Run23 FindNmip.C / refit macro**, to verify the fitting model, range, initialization, and constraints that were really used.
3. **daily_observations_primary.csv**, for complete 190–208 and 211–213 QA and for sector-level range diagnostics.

Candidate merging will additionally require `period_references.csv`, `manual_refits.csv`, `badTiles.txt`, Yevheniia's reviewed daily data, and the latest Ding period files. If convenient, package the text tables under `projects/2023_AuAu_200GeV/data/` together with the relevant ROOT spectra.

## Sources

- The currently uploaded `DayFitsHistos.C` (read-only during this review).
- The currently uploaded `ADCDelta_190_208.pdf` (all 24 overview pages and key pages were reviewed); `ADCDelta_176_182.pdf` was also obtained, but this review did not use it to declare the full period QA-complete.
- [Remote notebook](https://github.com/cdxing/EpdCalibration/blob/apple-epd-ml/projects/2023_AuAu_200GeV/notebooks/01_problem_data_baseline.ipynb), blob SHA read during this review: `9decd08554ed8c686db5bce8ddce89cfafd8c8c6`. Saved notebook output is a historical execution record and does not imply that it was rerun in this review.
- [Remote FindNmip.C](https://github.com/cdxing/EpdCalibration/blob/apple-epd-ml/FindNmip.C), blob SHA `510dd1cec6b3c3088ad29399b42de75dc551cce7`.
- [Remote ingest_calibration.py](https://github.com/cdxing/EpdCalibration/blob/apple-epd-ml/projects/2023_AuAu_200GeV/src/ingest_calibration.py), blob SHA `2d4b2028192961558ea79b60c741d109697ba97d`.
- Work Session Handoff provided for this review. Period values and statuses from the handoff are treated in this document at their original evidence level.

### 169–175 QA: EW0 PP1 TT7 Day169 reviewed and retained
- Trigger: large_leave_one_out_pull = 6.09 for Day169.
- Day169 MPV: 127.793991 ± 0.988674.
- Neighbor tiles TT6/TT8 also shift upward on Day169, so this is not an isolated TT7 fit anomaly.
- Detector-wide median shift: 168→169 = +2.008%; 169→170 = -0.150%.
- Modern 169–175 weighted constant = 122.101379 ± 0.323078.
- cracz period reference = 122.101379, exactly matching the modern weighted constant to 6 decimals.
- Decision: retain Day169 observation; no refit, no exclusion, no segment split. Treat large leave-one-out pull as reviewed diagnostic only.

### 176–182 QA closed

- Final QA output: `data/derived/qa_176_182_v3`
- 742 tiles provisional.
- EW1 PP1 TT6 and EW1 PP2 TT10 are known dead tiles; all 176–182 observations excluded from the period fit with no carry-forward. Their `manual_review / insufficient_points` status is expected because `n_used=0`.
- Day179 EW0 PP6 TT2 automatic MPV `105.997108` was not supported by manual refit.
- Accepted replacement: `116.307190 +/- 1.289736`, fit start 60, FitStatus 0, chi2/ndf ~1.07.
- Fit-start checks at 50, 60, and 70 were stable; start 80 was unstable/degraded.
- Conclusion: 176–182 is scientifically closed; no unresolved blocking QA items remain.

### 183–189 QA closed

- Erik period references are complete: 183–186 has 744 tiles and 188–189 has 744 tiles.
- Day187 is an intentional no-data gap; `timestampAndNotes.txt` explicitly states "No data for Day 187." No calibration is fabricated or carried across the gap.
- Day188 was merged with Day189 because of low statistics.
- EW1 PP1 TT6 and EW1 PP2 TT10 are known dead tiles and have final reference MPV 0.0 in both periods.
- Day184 EW1 PP3 TT6–9 strange-shape tiles are documented in the historical notes and appear in `RefitWork.txt`.
- Run 24186010 on Day186 contained single-value spikes in 34 documented tiles. These tiles are not listed in `RefitWork.txt`.
- Period-level cross-check against 188–189 gives median absolute change 0.457% for the 34 affected tiles, with 0/34 changing by more than 5%; no group-level evidence of contamination of the final 183–186 period constants was found.
- Conclusion: accept Erik's 183–186 and 188–189 period references for candidate v1, retaining the documented Day187 gap and known-dead-tile semantics.

### Day211 pedestal-shift calibration semantics

For EPD reconstruction, `StEpdHitMaker` uses

    nMIP = (ADC + offset) / mip

where `ADC` is the raw value returned by `trg->epdADC(...)`.

Therefore, for a channel with a shifted pedestal:

- raw pedestal position ≈ +P
- DB `offset` ≈ -P
- DB `mip` is the pedestal-subtracted 1-MIP spacing, not the absolute raw-ADC position of the 1-MIP peak.

Example: Day211 EW1 PP11 TT19
- low-ADC peak ≈ 118.5
- next MIP-like peak ≈ 254.5
- peak separation ≈ 136 ADC
- candidate interpretation: `offset ≈ -118.5`, `mip ≈ 136`
- then `(254.5 - 118.5) / 136 ≈ 1 MIP`

The existing `FindNmipFix.C` fit assumes zero offset and models peaks approximately at
`mip, 2*mip, 3*mip, ...`. It therefore cannot correctly fit a spectrum with a large additive
pedestal shift. The manual raw-ADC fit result near 273 must NOT be accepted as the MIP constant.

Next action: validate this interpretation with an offset-aware fit / pedestal-subtracted spectrum
before assigning the final Day211 calibration constants.

#### Day211 EW1 PP11 TT19 pedestal-aware validation

The raw-ADC spectrum shows a shifted low-ADC structure near 118.5 ADC and the next MIP-like peak near 254.5 ADC.

STAR reconstruction uses:

    nMIP = (ADC + offset) / mip

with raw `ADC = trg->epdADC(...)`.

A validation histogram was constructed with the x axis shifted by 118.5 ADC while preserving all bin contents. The existing multi-MIP fitting model was then applied unchanged.

Fit-start stability:
- start 60: MPV = 141.375 +/- 0.686, chi2/NDF = 1332.25/616 = 2.16
- start 70: MPV = 140.679 +/- 0.591, chi2/NDF = 1083.42/606 = 1.79
- start 80: MPV = 140.804 +/- 0.535, chi2/NDF = 940.29/596 = 1.58, FitStatus = 0

Accepted validation result:
- candidate DB offset = -118.5 ADC
- candidate mip = 140.804016 +/- 0.534756 ADC

Artifacts:
- ADCspectraFix_Day211_EW1_PP11_TT19_PedSub_20260917.pdf
- NmipConstantsFix_Day211_EW1_PP11_TT19_PedSub_20260917.txt

This result must NOT yet be entered as a normal `replace_daily_observation` review because the current review schema carries only MIP and not DB offset. Using mip=140.804 with offset=0 would be incorrect.
