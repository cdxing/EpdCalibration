from pathlib import Path
import pandas as pd


# ================================================================
# Paths
#
# __file__ = .../src/ingest_calibration.py
#
# parents[0] -> src/
# parents[1] -> 2023_AuAu_200GeV/
#
# C++ analogy:
#   const std::string projectRoot = "...";
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
DERIVED_DIR = PROJECT_ROOT / "data" / "derived"

DERIVED_DIR.mkdir(parents=True, exist_ok=True)


# ================================================================
# Generic parser for calibration text files.
#
# Expected first six columns:
#
# day  ew  pp  tt  mpv  mpv_error
#
# Some files have extra text after column 6, for example:
#
#   <----- Fit failed
#   <----- different from nominal
#
# C++ analogy:
#
#   while (input >> day >> ew >> pp >> tt >> mpv >> error) { ... }
#
# Here we read line-by-line because some lines contain extra QA text.
# ================================================================

def read_fit_file(path, source, source_stage):
    rows = []

    with open(path) as f:
        for line in f:

            # line.split() -> list[str]
            parts = line.split()

            if len(parts) < 6:
                continue

            text = line.lower()

            # Preserve existing automatic QA information when present.
            if "fit failed" in text:
                auto_flag = "fit_failed"

            elif "different from nominal" in text:
                auto_flag = "different_from_nominal"

            else:
                # Important:
                # "no flag in the file" does NOT necessarily mean
                # human-verified good calibration.
                auto_flag = "not_flagged"

            rows.append({
                "day": int(parts[0]),
                "ew": int(parts[1]),
                "pp": int(parts[2]),
                "tt": int(parts[3]),
                "mpv": float(parts[4]),
                "mpv_error": float(parts[5]),
                "auto_flag": auto_flag,
                "source": source,
                "source_stage": source_stage,
                "source_file": path.name,
            })

    return pd.DataFrame(rows)


# ================================================================
# 1. DING — individual daily automatic fits
# ================================================================

ding_dir = RAW_DIR / "ding"

ding_frames = []

for path in sorted(
    ding_dir.glob("NmipConstantsDay[0-9][0-9][0-9].txt")
):
    ding_frames.append(
        read_fit_file(
            path,
            source="ding",
            source_stage="automatic_daily_fit",
        )
    )

ding_daily = pd.concat(ding_frames, ignore_index=True)


# ================================================================
# 2. YUNO — Days 162–168
#
# We have:
#
#   original file
#   expert-reviewed / corrected file
#
# We use the corrected file as the daily value, but compare it with
# the original file so that we explicitly preserve manual changes.
# ================================================================

yuno_dir = RAW_DIR / "yuno_162_168"

yuno_original = read_fit_file(
    yuno_dir / "NmipConstantsDay162_168.txt",
    source="yuno",
    source_stage="original_daily_fit",
)

yuno_reviewed = read_fit_file(
    yuno_dir / "NmipConstantsDay162_168_changed.txt",
    source="yuno",
    source_stage="reviewed_daily_fit",
)


# Join the two tables by detector identity.
#
# ROOT analogy:
#   matching two TTrees by (day, ew, pp, tt)
#
# pandas merge is essentially a database-style JOIN.
yuno_compare = yuno_reviewed.merge(
    yuno_original[
        ["day", "ew", "pp", "tt", "mpv", "mpv_error"]
    ],
    on=["day", "ew", "pp", "tt"],
    how="left",
    suffixes=("", "_original"),
)

yuno_compare["manual_correction"] = (
    yuno_compare["mpv"] != yuno_compare["mpv_original"]
)


# ================================================================
# 3. CRACZ / CAMERON — Days 169–175 daily fits
# ================================================================

cracz_dir = RAW_DIR / "cracz_169_175"

cracz_daily = read_fit_file(
    cracz_dir / "NmipConstantsAll169to175.txt",
    source="cracz",
    source_stage="published_daily_fit",
)


# ================================================================
# Combine all currently available daily observations.
# ================================================================

daily_all = pd.concat(
    [
        ding_daily,
        yuno_compare[
            [
                "day",
                "ew",
                "pp",
                "tt",
                "mpv",
                "mpv_error",
                "auto_flag",
                "source",
                "source_stage",
                "source_file",
            ]
        ],
        cracz_daily,
    ],
    ignore_index=True,
)


# Gene's current Run23 analysis range.
daily_all["in_primary_range"] = daily_all["day"].between(162, 213)

daily_primary = daily_all[
    daily_all["in_primary_range"]
].copy()


# ================================================================
# 4. Period-level reference calibration
#
# These are NOT daily measurements.
#
# They are recommended tile calibration values obtained from
# cross-day constant fits.
# ================================================================

reference_frames = []


# ---- Cameron: Days 169–175
ref_169 = read_fit_file(
    cracz_dir / "Nmip_Day_169.txt",
    source="cracz",
    source_stage="period_reference",
)

ref_169["period_start"] = 169
ref_169["period_end"] = 175

reference_frames.append(ref_169)


# ---- Eloy: Days 183–186
eloy_dir = (
    RAW_DIR
    / "eloyd_183_189"
    / "AuAu2023_183-189"
)

ref_183 = read_fit_file(
    eloy_dir / "Nmip_Day_183.txt",
    source="eloyd",
    source_stage="period_reference",
)

ref_183["period_start"] = 183
ref_183["period_end"] = 186

reference_frames.append(ref_183)


# ---- Eloy: Day 188 merged into Day 189
ref_189 = read_fit_file(
    eloy_dir / "Nmip_Day_189.txt",
    source="eloyd",
    source_stage="period_reference",
)

ref_189["period_start"] = 188
ref_189["period_end"] = 189

reference_frames.append(ref_189)


period_references = pd.concat(
    reference_frames,
    ignore_index=True,
)

period_references = period_references.rename(
    columns={
        "mpv": "reference_mpv",
        "mpv_error": "reference_mpv_error",
    }
)


# ================================================================
# 5. Manual refits
#
# These are fits where a human adjusted the fitting setup and
# accepted the resulting calibration.
# ================================================================

manual_frames = []


# ---- Eloy manual refits: 104 accepted fits
eloy_refit = read_fit_file(
    eloy_dir / "RefitWork.txt",
    source="eloyd",
    source_stage="manual_refit",
)

manual_frames.append(eloy_refit)


# ---- Ding manual refit, if available
ding_fix_path = ding_dir / "NmipConstantsFix.txt"

if ding_fix_path.exists():
    ding_refit = read_fit_file(
        ding_fix_path,
        source="ding",
        source_stage="manual_refit",
    )

    manual_frames.append(ding_refit)


# ---- Yuno: detect the one original -> corrected value
yuno_manual = yuno_compare[
    yuno_compare["manual_correction"]
].copy()

yuno_manual["source_stage"] = "manual_correction"

manual_frames.append(
    yuno_manual[
        [
            "day",
            "ew",
            "pp",
            "tt",
            "mpv",
            "mpv_error",
            "auto_flag",
            "source",
            "source_stage",
            "source_file",
        ]
    ]
)


manual_refits = pd.concat(
    manual_frames,
    ignore_index=True,
)

manual_refits = manual_refits.rename(
    columns={
        "mpv": "manual_mpv",
        "mpv_error": "manual_mpv_error",
    }
)


# ================================================================
# 6. Save ML-ready derived tables
# ================================================================

daily_all.to_csv(
    DERIVED_DIR / "daily_observations_all.csv",
    index=False,
)

daily_primary.to_csv(
    DERIVED_DIR / "daily_observations_primary.csv",
    index=False,
)

period_references.to_csv(
    DERIVED_DIR / "period_references.csv",
    index=False,
)

manual_refits.to_csv(
    DERIVED_DIR / "manual_refits.csv",
    index=False,
)


# ================================================================
# 7. Sanity checks
# ================================================================

print("\n=== DAILY OBSERVATIONS ===")
print("All rows:", len(daily_all))
print("Primary 162-213 rows:", len(daily_primary))
print("Primary days:", daily_primary["day"].nunique())

print("\nRows by source:")
print(daily_primary.groupby("source").size())

print("\n=== PERIOD REFERENCES ===")
print("Rows:", len(period_references))
print(
    period_references[
        ["source", "period_start", "period_end"]
    ]
    .drop_duplicates()
    .sort_values(["period_start"])
)

print("\n=== MANUAL REFITS ===")
print("Rows:", len(manual_refits))

print("\nManual refits by source:")
print(manual_refits.groupby("source").size())
