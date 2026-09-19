# Run23 Au+Au 200 GeV EPD Calibration — DB Deployment Complete

The Run23 Au+Au 200 GeV EPD calibration for Days 162–213 has been completed, deployed to the STAR database, and validated by DB read-back.

## Calibration coverage

Final `epdGain` change points:

`162, 169, 176, 183, 188, 190, 191, 192, 207, 211, 212, 213`

The main calibration periods are:

- Days 162–168
- Days 169–175
- Days 176–182
- Days 183–186
- Days 188–189
- Days 190–206, with channel-level updates at Days191 and 192
- Days 207–208
- Day 211
- Day 212
- Day 213

Day187 and Days209–210 had no usable new calibration input, so the previous valid DB state persists through those gaps.

## Method

The calibration workflow is:

daily ADC spectrum fit
→ daily first-MIP MPV and uncertainty
→ reviewed period-level calibration constant
→ QA / manual corrections
→ DB-ready snapshots
→ STAR DB deployment
→ DB read-back validation

For Days162–182, the final period constants were derived from reviewed daily measurements using inverse-variance weighted constants.

## QA / exceptions

Two tiles are treated as persistent known-dead channels:

- EW1 PP1 TT6
- EW1 PP2 TT10

Their final status is `0`, with gain and offset set to `0`.

Two daily measurements were manually replaced before period aggregation:

- Day167, EW1 PP7 TT14
- Day179, EW0 PP6 TT2

Four reviewed non-zero DB offsets were applied on Days211–212.

A block of 32 EW0 channels had no usable raw daily calibration input on Days211–213. These channels were not classified as bad. Their previous valid Day207 gain/status state was preserved.

## DB validation

All deployed gain change points were checked by STAR DB read-back.

The final early-period validity chain is:

```text
Day162: 20230611.65546 -> 20230618.40229
Day169: 20230618.40229 -> 20230625.50947
Day176: 20230625.50947 -> 20230702.44935
Day183: 20230702.44935 -> 20230708.3035
Day188: 20230708.3035  -> 20230709.235431
```

The final Day211–213 precision-corrected gain entries were also read back and verified.

## Archive

The calibration workflow, QA products, final candidate, DB-ready snapshots, and documentation are archived in the calibration repository.

Final deployment documentation:

`projects/2023_AuAu_200GeV/docs/run23_auau200_epd_calibration_deployment_summary.md`

Final calibration commit:

`007f8a6 Finalize Run23 AuAu 200 GeV EPD calibration deployment`

Production-relevant STAR code changes, if needed, will follow the official STAR repository workflow.
