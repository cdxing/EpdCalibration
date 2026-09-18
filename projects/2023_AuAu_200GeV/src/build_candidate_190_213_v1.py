#!/usr/bin/env python3

import csv
from pathlib import Path

BASE_QA = Path("data/derived/qa")
SEGMENTS = Path("reviews/tile_period_segments.csv")
DB_OVERRIDES = Path("reviews/manual_db_calibration_overrides.csv")

OUTDIR = Path("data/derived/candidate_v1")
OUT = OUTDIR / "candidate_190_213.csv"
GAPS = OUTDIR / "unresolved_gaps.csv"

DEAD = {
    ("1", "1", "6"),
    ("1", "2", "10"),
}

OLD_QA_FILES = {
    (190, 206): BASE_QA / "qa_190_206_review_v6/period_qa.csv",
    (190, 190): BASE_QA / "qa_190_only/period_qa.csv",
    (191, 206): BASE_QA / "qa_191_206/period_qa.csv",
    (190, 191): BASE_QA / "qa_190_191_v2/period_qa.csv",
    (192, 206): BASE_QA / "qa_192_206_v1/period_qa.csv",
    (207, 208): BASE_QA / "qa_207_208_review_v3/period_qa.csv",
}

DAY_QA_FILES = {
    211: Path("data/derived/qa_211_v1/period_qa.csv"),
    212: Path("data/derived/qa_212_v1/period_qa.csv"),
    213: Path("data/derived/qa_213_v1/period_qa.csv"),
}


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def index_qa(path):
    return {
        (r["ew"], r["pp"], r["tt"]): r
        for r in read_csv(path)
    }


def make_row(
    period,
    key,
    calibration_mpv="",
    constant_error="",
    offset="0",
    status="",
    qa_flag="",
    source_qa="",
    segment_reason="",
    calibration_source="period_qa",
    source_artifact="",
    notes="",
):
    return {
        "period_start": period[0],
        "period_end": period[1],
        "ew": key[0],
        "pp": key[1],
        "tt": key[2],
        "calibration_mpv": calibration_mpv,
        "constant_error": constant_error,
        "offset": offset,
        "status": status,
        "qa_flag": qa_flag,
        "source_qa": source_qa,
        "segment_reason": segment_reason,
        "calibration_source": calibration_source,
        "source_artifact": source_artifact,
        "notes": notes,
    }


old_qa = {
    period: index_qa(path)
    for period, path in OLD_QA_FILES.items()
}

day_qa = {
    day: index_qa(path)
    for day, path in DAY_QA_FILES.items()
}

segments = read_csv(SEGMENTS)

segmented_tiles = {
    (r["ew"], r["pp"], r["tt"])
    for r in segments
}

override_rows = read_csv(DB_OVERRIDES)
overrides = {
    (r["day"], r["ew"], r["pp"], r["tt"]): r
    for r in override_rows
}

assert len(overrides) == len(override_rows), "duplicate DB override keys"
assert len(overrides) == 4, f"expected 4 DB overrides, got {len(overrides)}"

out = []

# ----------------------------------------------------------------------
# 190–206 default constants
# ----------------------------------------------------------------------
period = (190, 206)

for key, row in old_qa[period].items():
    if key in segmented_tiles or key in DEAD:
        continue

    assert row["status"] == "provisional", (
        period, key, row["status"], row["qa_flag"]
    )

    out.append(make_row(
        period,
        key,
        calibration_mpv=row["constant"],
        constant_error=row["constant_error"],
        offset="0",
        status="provisional",
        qa_flag=row["qa_flag"],
        source_qa=str(OLD_QA_FILES[period]),
        notes=row["notes"],
    ))

# ----------------------------------------------------------------------
# Tile-specific 190–206 segment overrides
# ----------------------------------------------------------------------
for s in segments:
    key = (s["ew"], s["pp"], s["tt"])
    period = (
        int(s["segment_start"]),
        int(s["segment_end"]),
    )

    row = old_qa[period][key]

    assert row["constant"], (period, key, "missing constant")

    if period == (190, 190):
        status = "accepted_single_day_segment"
    else:
        assert row["status"] == "provisional", (
            period, key, row["status"], row["qa_flag"]
        )
        status = "provisional_segment"

    out.append(make_row(
        period,
        key,
        calibration_mpv=row["constant"],
        constant_error=row["constant_error"],
        offset="0",
        status=status,
        qa_flag=row["qa_flag"],
        source_qa=str(OLD_QA_FILES[period]),
        segment_reason=s["reason"],
        notes=row["notes"],
    ))

# ----------------------------------------------------------------------
# Known-dead rows, 190–206
# ----------------------------------------------------------------------
for key in sorted(DEAD):
    out.append(make_row(
        (190, 206),
        key,
        offset="",
        status="known_dead_tile",
        qa_flag="insufficient_points",
        source_qa=str(OLD_QA_FILES[(190, 206)]),
        calibration_source="none",
        notes="No usable calibration observations; excluded from period fit.",
    ))

# ----------------------------------------------------------------------
# 207–208
# ----------------------------------------------------------------------
period = (207, 208)

for key, row in old_qa[period].items():
    if key in DEAD:
        continue

    assert row["status"] == "provisional", (
        period, key, row["status"], row["qa_flag"]
    )

    out.append(make_row(
        period,
        key,
        calibration_mpv=row["constant"],
        constant_error=row["constant_error"],
        offset="0",
        status="provisional",
        qa_flag=row["qa_flag"],
        source_qa=str(OLD_QA_FILES[period]),
        notes=row["notes"],
    ))

for key in sorted(DEAD):
    out.append(make_row(
        period,
        key,
        offset="",
        status="known_dead_tile",
        qa_flag="insufficient_points",
        source_qa=str(OLD_QA_FILES[period]),
        calibration_source="none",
        notes="No usable calibration observations; excluded from period fit.",
    ))

# ----------------------------------------------------------------------
# 211–213: detector-wide drift => day-level calibration
# ----------------------------------------------------------------------
for day in (211, 212, 213):
    period = (day, day)
    qa_path = DAY_QA_FILES[day]

    for key, row in day_qa[day].items():
        full_key = (str(day), key[0], key[1], key[2])

        # Known dead remains explicitly unavailable.
        if key in DEAD:
            assert row["n_used"] == "0", (day, key, row["n_used"])

            out.append(make_row(
                period,
                key,
                offset="",
                status="known_dead_tile",
                qa_flag=row["qa_flag"],
                source_qa=str(qa_path),
                calibration_source="none",
                notes="Known dead tile; no carry-forward.",
            ))
            continue

        # Pedestal-shift channels: QA observation is intentionally excluded.
        # Use manually validated MIP + nonzero offset.
        if full_key in overrides:
            ov = overrides[full_key]

            assert row["n_used"] == "0", (
                day, key, "DB override observation should be excluded",
                row["n_used"],
            )

            out.append(make_row(
                period,
                key,
                calibration_mpv=ov["mip"],
                constant_error=ov["mip_error"],
                offset=ov["offset"],
                status="manual_db_override",
                qa_flag=row["qa_flag"],
                source_qa=str(qa_path),
                segment_reason="pedestal_shift_requires_nonzero_offset",
                calibration_source="manual_db_override",
                source_artifact=ov["source_artifact"],
                notes=ov["notes"],
            ))
            continue

        # Other n_used=0 rows are raw-input unavailable for that day.
        # Never carry forward another day's calibration.
        if row["n_used"] == "0":
            assert not row["constant"], (day, key, row["constant"])

            out.append(make_row(
                period,
                key,
                offset="",
                status="raw_input_unavailable",
                qa_flag=row["qa_flag"],
                source_qa=str(qa_path),
                calibration_source="none",
                notes="No usable raw daily observation; no carry-forward.",
            ))
            continue

        # Every other usable single-day value is deliberately accepted.
        assert row["n_used"] == "1", (day, key, row["n_used"])
        assert row["constant"], (day, key, "missing single-day constant")

        out.append(make_row(
            period,
            key,
            calibration_mpv=row["constant"],
            constant_error=row["constant_error"],
            offset="0",
            status="accepted_single_day_segment",
            qa_flag=row["qa_flag"],
            source_qa=str(qa_path),
            segment_reason="detector_wide_day_to_day_drift",
            calibration_source="period_qa",
            notes=(
                row["notes"]
                + ";single_day_segment_intentionally_accepted"
            ),
        ))

# ----------------------------------------------------------------------
# Sanity checks
# ----------------------------------------------------------------------

# Existing 190–208 candidate contributed 1500 rows.
# 211, 212, 213 contribute exactly 744 rows each.
assert len(out) == 1500 + 3 * 744, (
    f"expected 3732 candidate rows, got {len(out)}"
)

for day in (211, 212, 213):
    rows = [
        r for r in out
        if r["period_start"] == day and r["period_end"] == day
    ]
    assert len(rows) == 744, (day, len(rows))

# Verify DB override count in output.
db_rows = [
    r for r in out
    if r["status"] == "manual_db_override"
]
assert len(db_rows) == 4, len(db_rows)

# Explicit unresolved acquisition/input gap.
gap_rows = [
    {
        "start_day": "209",
        "end_day": "210",
        "status": "unresolved_input_gap",
        "reason": "Day209.root and Day210.root are empty/unusable artifacts",
        "action": "no_calibration_fabricated",
    }
]

OUTDIR.mkdir(parents=True, exist_ok=True)

fields = [
    "period_start", "period_end",
    "ew", "pp", "tt",
    "calibration_mpv", "constant_error", "offset",
    "status", "qa_flag",
    "source_qa", "segment_reason",
    "calibration_source", "source_artifact",
    "notes",
]

with OUT.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(sorted(
        out,
        key=lambda r: (
            int(r["period_start"]),
            int(r["period_end"]),
            int(r["ew"]),
            int(r["pp"]),
            int(r["tt"]),
        ),
    ))

with GAPS.open("w", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "start_day", "end_day", "status", "reason", "action"
        ],
        lineterminator="\n",
    )
    w.writeheader()
    w.writerows(gap_rows)

print("candidate:", OUT)
print("rows:", len(out))
print("DB overrides:", len(db_rows))
print("unresolved gap manifest:", GAPS)
