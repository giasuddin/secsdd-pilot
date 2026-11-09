"""Aggregate results/<condition>/<task>.json into results/summary.json and results/RESULTS.md."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
CONDS = [("baseline", "A. Functional spec only"), ("sis", "B. + Spec It Safe security lines"), ("oracle", "C. + exact CWEs named (oracle)")]
tasks = sorted(p.name for p in (ROOT / "tasks").iterdir())
summary, md = {}, ["# Pilot results", "", "One sample per task and condition; generator model: Claude Sonnet (via subagent), Python-Flask, BaxBench OpenAPI prompts.", "",
                   "| Task | " + " | ".join(c[1] for c in CONDS) + " |", "| --- | " + " | ".join("---" for _ in CONDS) + " |"]
cells = {t: [] for t in tasks}
for c, _ in CONDS:
    s = {"functionally_correct": 0, "correct_and_secure": 0, "any_exploit": 0, "per_task": {}}
    for t in tasks:
        r = json.loads((ROOT / "results" / c / f"{t}.json").read_text())
        s["functionally_correct"] += r["functionally_correct"]; s["correct_and_secure"] += r["correct_and_secure"]
        s["any_exploit"] += bool(r["cwes_exploited"])
        s["per_task"][t] = {k: r[k] for k in ("functionally_correct", "cwes_exploited", "correct_and_secure")}
        txt = ("correct" if r["functionally_correct"] else "**incorrect**") + (", exploited: " + ", ".join(r["cwes_exploited"]) if r["cwes_exploited"] else ", no exploit")
        cells[t].append(txt)
    summary[c] = s
for t in tasks:
    md.append(f"| {t} | " + " | ".join(cells[t]) + " |")
n = len(tasks)
md.append("| **Functionally correct** | " + " | ".join(f"{summary[c]['functionally_correct']}/{n}" for c, _ in CONDS) + " |")
md.append("| **Correct and secure (sec_pass@1)** | " + " | ".join(f"{summary[c]['correct_and_secure']}/{n}" for c, _ in CONDS) + " |")
md.append("| **Apps with a successful exploit** | " + " | ".join(f"{summary[c]['any_exploit']}/{n}" for c, _ in CONDS) + " |")
el = json.loads((ROOT / "results" / "elicitation.json").read_text())
md += ["", "## Elicitation: did Spec It Safe add the CWEs BaxBench tests?", "",
       "| Task | CWEs tested by BaxBench | CWEs Spec It Safe added | Matched (exact / related) |", "| --- | --- | --- | --- |"]
for x in el["per_task"]:
    md.append(f"| {x['task']} | {', '.join(x['baxbench_cwes'])} | {', '.join(x['sis_added_cwes'])} | {len(x['found_exact'])} / {len(x['found_related'])} |")
md.append(f"| **Total** | {el['total_target_cwes']} | | **{el['found_exact']} / {el['found_related']}** |")
(ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=2))
(ROOT / "results" / "RESULTS.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
