#!/usr/bin/env python3
"""Audit daily EPD MPVs without changing any calibration inputs.

Python 3 standard library only. This is a review aid, not a calibration release.
Positive, finite daily MPVs with positive, finite errors enter the diagnostic
weighted constant, including flagged fits. Every input and exclusion is audited.
No sigma clipping, error inflation, automatic replacement, or automatic split.
"""

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median


def parse_row(raw, path, line):
    row = dict(raw)
    try:
        for key in ("day", "ew", "pp", "tt"):
            row[key] = int(row[key])
        for key in ("mpv", "mpv_error"):
            row[key] = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("{}:{}: malformed daily row: {}".format(path, line, exc))
    if not (1 <= row["day"] <= 366 and row["ew"] in (0, 1)
            and 1 <= row["pp"] <= 12 and 1 <= row["tt"] <= 31):
        raise ValueError("{}:{}: detector index or day outside range".format(path, line))
    stage = str(row.get("source_stage", "")).lower()
    if "period" in stage or "reference" in stage:
        raise ValueError("{}:{}: period constants are not daily inputs".format(path, line))
    text = str(row.get("auto_flag", "")).lower()
    if "fit_failed" in text or "fit failed" in text:
        flag = "fit_failed"
    elif "different_from_nominal" in text or "different from nominal" in text:
        flag = "different_from_nominal"
    else:
        flag = text.strip() or "unknown"
    row.update(auto_flag=flag, input_file=str(path.resolve()), input_line=line,
               source=row.get("source") or "unspecified",
               source_file=row.get("source_file") or path.name)
    row["numeric_issue"] = (
        "invalid_mpv" if not math.isfinite(row["mpv"]) or row["mpv"] <= 0 else
        "invalid_error" if not math.isfinite(row["mpv_error"]) or row["mpv_error"] <= 0
        else "")
    return row


def read_daily(paths):
    rows, seen = [], {}
    for path in paths:
        # Nmip_Day_<start>.txt has the same six columns but different semantics.
        if path.name.lower().startswith("nmip_day_"):
            raise ValueError("{}: period output cannot be used as daily data".format(path))
        with path.open(encoding="utf-8-sig") as stream:
            if path.suffix.lower() == ".csv":
                reader = csv.DictReader(stream)
                required = {"day", "ew", "pp", "tt", "mpv", "mpv_error"}
                if not required.issubset(reader.fieldnames or []):
                    raise ValueError("{}: CSV needs {}".format(path, sorted(required)))
                source_rows = ((reader.line_num, row) for row in reader)
                for line, raw in source_rows:
                    rows.append(parse_row(raw, path, line))
            else:
                for line, text in enumerate(stream, 1):
                    if not text.strip() or text.lstrip().startswith("#"):
                        continue
                    fields = text.split()
                    if len(fields) < 6:
                        raise ValueError("{}:{}: expected six columns".format(path, line))
                    raw = dict(zip(("day", "ew", "pp", "tt", "mpv", "mpv_error"), fields[:6]))
                    raw["auto_flag"] = " ".join(fields[6:]) or "unknown"
                    rows.append(parse_row(raw, path, line))
    for row in rows:
        key = tuple(row[k] for k in ("day", "ew", "pp", "tt"))
        if key in seen:
            raise ValueError("Duplicate daily key {} in {} and {}; resolve provenance first".format(
                key, seen[key], row["input_file"]))
        seen[key] = row["input_file"]
    if not rows:
        raise ValueError("No daily rows found")
    return rows

def read_reviews(path):
    if path is None:
        return {}

    reviews = {}

    with path.open(encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)

        required = {
            "day", "ew", "pp", "tt",
            "review_status", "action", "reason",
            "replacement_mpv", "replacement_mpv_error",
        }

        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                "{}: review CSV needs {}".format(path, sorted(required))
            )

        for line, raw in enumerate(reader, 2):
            try:
                key = (
                    int(raw["day"]),
                    int(raw["ew"]),
                    int(raw["pp"]),
                    int(raw["tt"]),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "{}:{}: malformed review key: {}".format(path, line, exc)
                )

            if key in reviews:
                raise ValueError(
                    "{}:{}: duplicate review key {}".format(path, line, key)
                )

            row = dict(raw)
            row["action"] = row["action"].strip()
            row["review_status"] = row["review_status"].strip()
            row["reason"] = row["reason"].strip()

            if row["action"] == "replace_daily_observation":
                try:
                    mpv = float(row["replacement_mpv"])
                    err = float(row["replacement_mpv_error"])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        "{}:{}: invalid replacement values: {}".format(
                            path, line, exc
                        )
                    )

                if not (
                    math.isfinite(mpv) and mpv > 0
                    and math.isfinite(err) and err > 0
                ):
                    raise ValueError(
                        "{}:{}: replacement MPV/error must be positive and finite".format(
                            path, line
                        )
                    )

                row["replacement_mpv"] = mpv
                row["replacement_mpv_error"] = err

            reviews[key] = row

    return reviews

def apply_reviews(rows, reviews):
    out = []
    seen = set()

    for original in rows:
        row = dict(original)

        key = (row["day"], row["ew"], row["pp"], row["tt"])

        row["original_mpv"] = row["mpv"]
        row["original_mpv_error"] = row["mpv_error"]
        row["review_status"] = ""
        row["review_action"] = ""
        row["review_reason"] = ""
        row["review_excluded"] = False

        review = reviews.get(key)

        if review:
            seen.add(key)

            row["review_status"] = review["review_status"]
            row["review_action"] = review["action"]
            row["review_reason"] = review["reason"]

            if review["action"] == "exclude_from_period_fit":
                row["review_excluded"] = True

            elif review["action"] == "replace_daily_observation":
                row["mpv"] = review["replacement_mpv"]
                row["mpv_error"] = review["replacement_mpv_error"]
                row["numeric_issue"] = ""

            else:
                raise ValueError(
                    "Unknown review action {!r} for {}".format(
                        review["action"], key
                    )
                )

        out.append(row)

    unused = set(reviews) - seen

    if unused:
        raise ValueError(
            "Review keys not found in daily observations: {}".format(
                sorted(unused)
            )
        )

    return out

def constant_fit(rows):
    """Analytic pol0 solution for independent positive-error daily measurements."""
    if not rows:
        return None
    smallest = min(r["mpv_error"] for r in rows)
    scaled = [(smallest / r["mpv_error"]) ** 2 for r in rows]
    total = math.fsum(scaled)
    weights = [w / total for w in scaled]
    value = math.fsum(r["mpv"] * w for r, w in zip(rows, weights))
    error = smallest / math.sqrt(total)
    pulls = [(r["mpv"] - value) / r["mpv_error"] for r in rows]
    chi2 = math.fsum(p * p for p in pulls)
    ndf = len(rows) - 1
    return {"constant": value, "constant_error": error, "chi2": chi2,
            "ndf": ndf, "chi2_ndf": chi2 / ndf if ndf else None,
            "weights": weights}


def day_list(days):
    return ";".join(str(d) for d in sorted(set(days)))


def dump_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize_tile(key, group, args):
    ew, pp, tt = key
    used = [
        r for r in group
        if not r["numeric_issue"]
        and not r["review_excluded"]
    ]
    active = [
        r for r in group
        if not r["review_excluded"]
    ]
    missing = sorted(set(range(args.start, args.end + 1)) - {r["day"] for r in group})
    fit = constant_fit(used)
    flags = set()
    if missing:
        flags.add("missing_days")
    if any(r["numeric_issue"] for r in active):
        flags.add("invalid_numeric")
    if any(
        r["auto_flag"] == "fit_failed"
        and r["review_action"] != "replace_daily_observation"
        for r in active
    ):
        flags.add("fit_failed")
    if any(
        r["auto_flag"] == "different_from_nominal"
        and r["review_action"] != "replace_daily_observation"
        for r in active
    ):
        flags.add("different_from_nominal")
    if any(r["auto_flag"] not in ("fit_failed", "different_from_nominal", "not_flagged")
           for r in group):
        flags.add("unknown_qa")
    if len(used) < 2:
        flags.add("insufficient_points")
    if fit and fit["chi2_ndf"] is not None and fit["chi2_ndf"] > args.chi2_threshold:
        flags.add("large_chi2_ndf")
    center = median([r["mpv"] for r in used]) if used else None
    max_residual = max((abs(r["mpv"] - fit["constant"]) for r in used), default=None)
    if max_residual is not None and max_residual > args.adc_threshold:
        flags.add("large_residual")
    if used and len(used) * max(fit["weights"]) > args.weight_factor:
        flags.add("weight_dominance")

    queue = []
    #for r in group:
    for r in active:
        reasons = []
        tier = 3
        loo_shift = loo_pull = None
        if r["numeric_issue"]:
            tier, reasons = 0, [r["numeric_issue"]]
        else:
            others = [q for q in used if q["day"] != r["day"]]
            if others:
                loo = constant_fit(others)
                loo_shift = abs(fit["constant"] - loo["constant"])
                loo_pull = abs(r["mpv"] - loo["constant"]) / math.hypot(
                    r["mpv_error"], loo["constant_error"])
                if loo_shift > args.adc_threshold:
                    reasons.append("large_leave_one_out_shift")
                    tier = min(tier, 1)
                if loo_pull > args.pull_threshold:
                    reasons.append("large_leave_one_out_pull")
                    tier = min(tier, 1)
                # Robust neighbor comparison keeps one extreme fit from making
                # every ordinary day the only apparent outlier.
                if len(others) >= 2:
                    med = median(q["mpv"] for q in others)
                    mad = median(abs(q["mpv"] - med) for q in others)
                    scale = max(1.4826 * mad, args.adc_threshold / args.pull_threshold)
                    if abs(r["mpv"] - med) > args.pull_threshold * scale:
                        reasons.append("robust_neighbor_outlier")
                        tier = min(tier, 1)
            if (
                r["auto_flag"] == "fit_failed"
                and r["review_action"] != "replace_daily_observation"
            ):
                reasons.append("fit_failed")
                tier = min(tier, 1)

            elif (
                r["auto_flag"] == "different_from_nominal"
                and r["review_action"] != "replace_daily_observation"
            ):
                reasons.append("different_from_nominal")
                tier = min(tier, 2)

            elif (
                r["auto_flag"] != "not_flagged"
                and r["review_action"] != "replace_daily_observation"
            ):
                reasons.append("unknown_qa")
            if len(used) < 2:
                reasons.append("insufficient_points")
                tier = min(tier, 2)
        if reasons:
            queue.append(dict(r, priority_tier=tier, reasons=";".join(reasons),
                              leave_one_out_constant_shift=loo_shift,
                              leave_one_out_pull=loo_pull,
                              action="inspect_spectrum_or_provenance; do_not_auto_reject"))
    if any("robust_neighbor_outlier" in r["reasons"] for r in queue):
        flags.add("robust_neighbor_outlier")

    before = [r["mpv"] for r in used if args.split_day and r["day"] < args.split_day]
    after = [r["mpv"] for r in used if args.split_day and r["day"] >= args.split_day]
    shift = median(after) - median(before) if min(len(before), len(after)) >= 2 else None
    if shift is not None and abs(shift) > args.adc_threshold:
        flags.add("step_or_drift_candidate")
    # Distinguish data coverage from a claimed validated constant.
    if not group:
        status = "missing"
    elif flags - {"unknown_qa", "large_chi2_ndf", "different_from_nominal"}:
        status = "manual_review"
    else:
        status = "provisional"
    summary = dict(ew=ew, pp=pp, tt=tt, period_start=args.start, period_end=args.end,
                   n_found=len(group), n_used=len(used), status=status,
                   median_mpv=center, max_abs_residual=max_residual,
                   missing_days=day_list(missing),
                   flagged_days=day_list(r["day"] for r in group
                                          if r["auto_flag"] in ("fit_failed", "different_from_nominal")),
                   numeric_excluded_days=day_list(r["day"] for r in group if r["numeric_issue"]),
                   qa_flag=";".join(sorted(flags)),
                   source=";".join(sorted({r["source"] for r in group})),
                   split_day=args.split_day, n_before=len(before), n_after=len(after),
                   signed_median_shift=shift,
                   notes="diagnostic_only; no_auto_accept; no_auto_split")
    for name in ("constant", "constant_error", "chi2", "ndf", "chi2_ndf"):
        summary[name] = fit[name] if fit else None
    summary["max_weight_fraction"] = max(fit["weights"]) if fit else None
    summary["dominant_day"] = used[fit["weights"].index(max(fit["weights"]))]["day"] if fit else None
    return summary, queue


def run(args):
    if not (1 <= args.start <= args.end <= 366):
        raise ValueError("Require 1 <= start <= end <= 366")
    if args.split_day and not (args.start + 2 <= args.split_day <= args.end - 1):
        raise ValueError("Split comparison needs at least two calendar days on each side")
    for k in ("adc_threshold", "pull_threshold", "chi2_threshold", "weight_factor"):
        if not math.isfinite(getattr(args, k)) or getattr(args, k) <= 0:
            raise ValueError("{} must be positive and finite".format(k))
    all_rows = read_daily(args.inputs)
    reviews = read_reviews(args.reviews)

    period_reviews = {
        key: review
        for key, review in reviews.items()
        if args.start <= key[0] <= args.end
    }
    selected = [
        r for r in all_rows
        if args.start <= r["day"] <= args.end
    ]

    selected = apply_reviews(selected, period_reviews)

    print("manual reviews loaded:", len(reviews))
    print("manual reviews in period:", len(period_reviews))

    print(
        "review exclusions:",
        sum(r["review_excluded"] for r in selected)
    )
    print(
        "review replacements:",
        sum(r["review_action"] == "replace_daily_observation"
            for r in selected)
    )
    if not selected:
        raise ValueError("No daily observations in the requested period")
    groups = defaultdict(list)
    for r in selected:
        groups[(r["ew"], r["pp"], r["tt"])].append(r)
    summaries, queue = [], []
    for ew in range(2):
        for pp in range(1, 13):
            for tt in range(1, 32):
                key = (ew, pp, tt)
                summary, issues = summarize_tile(key, sorted(groups[key], key=lambda r:r["day"]), args)
                summaries.append(summary)
                queue.extend(issues)
    queue.sort(key=lambda r:(r["priority_tier"],
                             -(r["leave_one_out_constant_shift"] or 0),
                             -(r["leave_one_out_pull"] or 0),
                             r["day"], r["ew"], r["pp"], r["tt"]))
    for rank, r in enumerate(queue, 1):
        r["rank"] = rank
    # New output directory prevents accidental overwrites of earlier QA runs.
    args.out.mkdir(parents=True, exist_ok=False)
    dump_csv(args.out / "period_qa.csv", summaries, list(summaries[0]))
    tile_queue = []
    for s in summaries:
        if s["qa_flag"]:
            flags = set(s["qa_flag"].split(";"))
            tier = (0 if "invalid_numeric" in flags else
                    1 if flags & {"fit_failed", "large_residual",
                                  "robust_neighbor_outlier", "step_or_drift_candidate",
                                  "weight_dominance"} else
                    2 if flags - {"unknown_qa"} else 3)
            tile_queue.append(dict(s, priority_tier=tier))
    tile_queue.sort(key=lambda s:(s["priority_tier"], -(s["chi2_ndf"] or 0),
                                  -(s["max_abs_residual"] or 0), s["ew"], s["pp"], s["tt"]))
    for rank, s in enumerate(tile_queue, 1):
        s["rank"] = rank
    dump_csv(args.out / "tile_qa_queue.csv", tile_queue,
             ["rank", "priority_tier"] + list(summaries[0]))
    dump_csv(args.out / "manual_qa_queue.csv", queue,
             ["rank", "priority_tier", "day", "ew", "pp", "tt", "mpv", "mpv_error",
              "auto_flag", "reasons", "leave_one_out_constant_shift", "leave_one_out_pull",
              "source", "source_file", "input_file", "input_line", "action"])
    dump_csv(args.out / "input_audit.csv", selected,
             ["day", "ew", "pp", "tt", "mpv", "mpv_error", "auto_flag", "numeric_issue",
              "source", "source_stage", "source_file", "input_file", "input_line"])
    sector = []
    if args.split_day:
        for ew in range(2):
            for pp in range(1, 13):
                candidates = [r["signed_median_shift"] for r in summaries
                              if r["ew"] == ew and r["pp"] == pp and r["signed_median_shift"] is not None]
                sector.append(dict(ew=ew, pp=pp, n_compared=len(candidates),
                                   median_signed_shift=median(candidates) if candidates else None,
                                   n_positive_over_threshold=sum(v > args.adc_threshold for v in candidates),
                                   n_negative_over_threshold=sum(v < -args.adc_threshold for v in candidates),
                                   note="descriptive_only; check_spectra_and_run_logs"))
        dump_csv(args.out / "sector_step_diagnostic.csv", sector, list(sector[0]))
    metadata = {"tool_version":"0.1.0", "period":[args.start,args.end],
                "split_day":args.split_day, "daily_rows_in_period":len(selected),
                "daily_rows_outside_period":len(all_rows)-len(selected),
                "queue_rows":len(queue), "status_counts":{},
                "thresholds":{k:getattr(args,k) for k in ("adc_threshold","pull_threshold","chi2_threshold","weight_factor")},
                "policy":"QA only. Thresholds are triage heuristics, not calibrated significance or acceptance cuts. No calibration release written.",
                "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "inputs":[{"path":str(p.resolve()),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in args.inputs]}
    for s in summaries:
        metadata["status_counts"][s["status"]] = metadata["status_counts"].get(s["status"],0)+1
    (args.out / "qa_run.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"output":str(args.out.resolve()),"tiles":len(summaries),
                      "queue_rows":len(queue),"status_counts":metadata["status_counts"]}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("inputs", nargs="+", type=Path, help="daily CSVs or six-column daily TXT files; never period constants")
    p.add_argument("--start", required=True, type=int)
    p.add_argument("--end", required=True, type=int)
    p.add_argument("--out", required=True, type=Path, help="new output directory")
    p.add_argument(
    "--reviews",
    type=Path,
    help="manual observation review CSV; overlays exclusions/replacements without modifying source data",
    )
    p.add_argument("--split-day", type=int, help="diagnostic before/after comparison only")
    p.add_argument("--adc-threshold", type=float, default=10.0)
    p.add_argument("--pull-threshold", type=float, default=6.0)
    p.add_argument("--chi2-threshold", type=float, default=5.0)
    p.add_argument("--weight-factor", type=float, default=5.0)
    args = p.parse_args()
    try:
        run(args)
    except (ValueError, OSError, OverflowError) as exc:
        p.exit(2, "ERROR: {}\n".format(exc))


if __name__ == "__main__":
    main()
