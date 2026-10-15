#!/usr/bin/env python3
"""Aggregate repeated k6 runs into a stable requests-per-second comparison."""

import csv
import json
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ERROR_RATE_MAX = float(os.environ.get("ERROR_RATE_MAX", "0.01"))
P95_MAX_MS = float(os.environ.get("P95_MAX_MS", "500"))
CHECK_RATE_MIN = float(os.environ.get("CHECK_RATE_MIN", "0.99"))
PLATEAU_GAIN = float(os.environ.get("PLATEAU_GAIN", "0.10"))

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def mean(values):
    return statistics.fmean(values)


def load_rows():
    rows = []
    for path in sorted(RESULTS.glob("*.json")):
        data = json.loads(path.read_text())
        if "rps" not in data or "app" not in data:
            continue
        rows.append(data)
    return rows


def aggregate(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["app"], int(row["vus"]))].append(row)

    levels = []
    for (app, vus), samples in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        failed = [sample["failed_rate"] for sample in samples]
        checks = [sample["checks_rate"] for sample in samples]
        p95 = [sample["p95_ms"] for sample in samples]
        stable = (
            max(failed) < ERROR_RATE_MAX
            and max(p95) < P95_MAX_MS
            and min(checks) >= CHECK_RATE_MIN
        )
        levels.append(
            {
                "app": app,
                "vus": vus,
                "repeats": len(samples),
                "rps": mean(sample["rps"] for sample in samples),
                "requests": mean(sample["requests"] for sample in samples),
                "failed_rate": mean(failed),
                "worst_failed_rate": max(failed),
                "checks_rate": mean(checks),
                "worst_checks_rate": min(checks),
                "avg_ms": mean(sample["avg_ms"] for sample in samples),
                "p50_ms": mean(sample["p50_ms"] for sample in samples),
                "p95_ms": mean(p95),
                "worst_p95_ms": max(p95),
                "p99_ms": mean(sample["p99_ms"] for sample in samples),
                "stable": stable,
            }
        )
    return levels


def plateau_vus(levels):
    stable = [level for level in levels if level["stable"]]
    if len(stable) < 2:
        return None
    knee = stable[0]["vus"]
    previous = stable[0]["rps"]
    for level in stable[1:]:
        if previous <= 0 or (level["rps"] - previous) / previous < PLATEAU_GAIN:
            return knee
        knee = level["vus"]
        previous = level["rps"]
    return None


def best_stable(levels):
    stable = [level for level in levels if level["stable"]]
    if not stable:
        return None
    return max(stable, key=lambda level: level["rps"])


def fmt(value, digits=1):
    return f"{value:.{digits}f}"


def render(levels):
    apps = []
    for level in levels:
        if level["app"] not in apps:
            apps.append(level["app"])

    lines = [
        "# Request per second summary",
        "",
        "A concurrency level is stable when every repeat meets all three gates:",
        "",
        f"- error rate under {ERROR_RATE_MAX:.0%}",
        f"- response checks passing at least {CHECK_RATE_MIN:.0%}",
        f"- p95 latency under {P95_MAX_MS:.0f} ms",
        "",
        "The reported rate is the mean of the repeats. Stability uses the worst repeat.",
        "",
        "| App | VUs | Mean RPS | p50 ms | p95 ms | p99 ms | Error rate | Stable |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for level in levels:
        lines.append(
            "| {app} | {vus} | {rps} | {p50} | {p95} | {p99} | {errors} | {stable} |".format(
                app=level["app"],
                vus=level["vus"],
                rps=fmt(level["rps"]),
                p50=fmt(level["p50_ms"]),
                p95=fmt(level["p95_ms"]),
                p99=fmt(level["p99_ms"]),
                errors=f"{level['worst_failed_rate']:.2%}",
                stable="yes" if level["stable"] else "no",
            )
        )

    lines.extend(["", "## Highest stable rate", ""])
    for app in apps:
        app_levels = [level for level in levels if level["app"] == app]
        best = best_stable(app_levels)
        if best is None:
            lines.append(f"- **{app}** did not meet the stability gates at any tested concurrency.")
            continue
        lines.append(
            f"- **{app}** reached **{best['rps']:.1f} RPS** at {best['vus']} virtual users "
            f"(p95 {best['p95_ms']:.1f} ms, worst error rate {best['worst_failed_rate']:.2%})."
        )
        knee = plateau_vus(app_levels)
        if knee is not None:
            lines.append(
                f"  Throughput stopped increasing by {PLATEAU_GAIN:.0%} or more after {knee} virtual users."
            )

    lines.append("")
    return "\n".join(lines)


def write_csv(rows, levels):
    raw_path = RESULTS / "raw.csv"
    with raw_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "app",
                "vus",
                "repeat",
                "duration",
                "rps",
                "requests",
                "failed_rate",
                "checks_rate",
                "avg_ms",
                "p50_ms",
                "p95_ms",
                "p99_ms",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in writer.fieldnames})

    summary_path = RESULTS / "summary.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "app",
                "vus",
                "repeats",
                "rps",
                "p50_ms",
                "p95_ms",
                "p99_ms",
                "worst_failed_rate",
                "worst_checks_rate",
                "stable",
            ],
        )
        writer.writeheader()
        for level in levels:
            writer.writerow({key: level[key] for key in writer.fieldnames})


def main():
    rows = load_rows()
    if not rows:
        print("No k6 result files were found in results/.", file=sys.stderr)
        return 1

    levels = aggregate(rows)
    report = render(levels)
    (RESULTS / "summary.md").write_text(report)
    write_csv(rows, levels)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
