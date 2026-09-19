#!/usr/bin/env python3

import csv
from pathlib import Path

CANDIDATE = Path("data/derived/candidate_v2/candidate_162_213.csv")
STORE_TIMES = Path("data/derived/db_ready/store_times_v2.csv")
OUTDIR = Path("data/derived/db_ready")

GAIN_DAYS = [162, 169, 176, 183, 188, 190, 191, 192, 207, 211, 212, 213]
STATUS_DAYS = [162]

KNOWN_DEAD = "known_dead_tile"
RAW_UNAVAILABLE = "raw_input_unavailable"


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


rows = read_csv(CANDIDATE)
times = {int(r["day"]): r for r in read_csv(STORE_TIMES)}

assert all(times[d]["status"] == "confirmed" for d in GAIN_DAYS)


def active(day):
    rr = [
        r for r in rows
        if int(r["period_start"]) <= day <= int(r["period_end"])
    ]
    rr.sort(key=lambda r: (int(r["ew"]), int(r["pp"]), int(r["tt"])))

    assert len(rr) == 744, (day, len(rr))
    assert len({(r["ew"], r["pp"], r["tt"]) for r in rr}) == 744
    return rr


OUTDIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# epdGain full snapshots.
#
# Stateful rule:
# - normal/current calibration updates DB state
# - known dead explicitly becomes 0/0
# - raw_input_unavailable does NOT create a new calibration;
#   the previous valid DB state is preserved in the full-table snapshot
# ------------------------------------------------------------

gain_state = {}

for day in GAIN_DAYS:
    rr = active(day)

    for r in rr:
        key = (r["ew"], r["pp"], r["tt"])

        if r["status"] == RAW_UNAVAILABLE:
            assert key in gain_state, (
                day, key, "raw unavailable but no previous DB state"
            )
            continue

        if r["status"] == KNOWN_DEAD:
            gain_state[key] = ("0", "0")
            continue

        assert r["calibration_mpv"], (day, key, r["status"])
        gain_state[key] = (
            r["calibration_mpv"],
            r["offset"] or "0",
        )

    assert len(gain_state) == 744, (day, len(gain_state))

    path = OUTDIR / f"epdGain_Day{day}_v2.txt"

    with path.open("w", newline="") as f:
        f.write(
            f"# storeTime GMT: {times[day]['store_time_gmt']}\n"
            "# day ew pp tile mip offset\n"
        )

        for ew in ("0", "1"):
            for pp in map(str, range(1, 13)):
                for tt in map(str, range(1, 32)):
                    key = (ew, pp, tt)
                    mip, offset = gain_state[key]
                    f.write(
                        f"{day} {ew} {pp} {tt} {mip} {offset}\n"
                    )

# ------------------------------------------------------------
# epdStatus.
#
# For the reviewed 162–213 range the stable physical mask is:
# - two known-dead tiles -> 0
# - all other physical tiles -> 1
#
# Write the initial Day162 full snapshot only.
# Existing later DB entries may repeat the same effective mask.
# ------------------------------------------------------------

for day in STATUS_DAYS:
    rr = active(day)

    path = OUTDIR / f"epdStatus_Day{day}_v2.txt"

    with path.open("w", newline="") as f:
        f.write(
            f"# storeTime GMT: {times[day]['store_time_gmt']}\n"
            "# ew pp tile status\n"
        )

        for r in rr:
            if int(r["tt"]) == 1:
                f.write(f"{r['ew']} {r['pp']} 0 1\n")

            status = 0 if r["status"] == KNOWN_DEAD else 1
            f.write(
                f"{r['ew']} {r['pp']} {r['tt']} {status}\n"
            )

print("gain files:", len(GAIN_DAYS))
print("status files:", len(STATUS_DAYS))
print("output:", OUTDIR)
