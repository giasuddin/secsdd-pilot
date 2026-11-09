"""Build pilot tasks from BaxBench scenarios.

For each scenario this writes:
  tasks/<id>/requirements.md   functional EARS spec, generated mechanically from the
                               scenario's OpenAPI paths (one requirement per operation)
  tasks/<id>/prompt_baseline.txt  the unmodified BaxBench prompt (Python-Flask, OpenAPI
                               spec, safety prompt = "none")
  tasks/<id>/meta.json         scenario CWEs (BaxBench ground truth, from its security tests)
Usage: python scripts/make_tasks.py <path-to-baxbench/src>
"""
import json, sys, pathlib, yaml
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import _bax  # noqa: E402,F401
BAX = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(BAX))
import scenarios  # noqa: E402
from env.python import FlaskEnv  # noqa: E402

PILOT = None  # None = all BaxBench scenarios
ROOT = pathlib.Path(__file__).resolve().parents[1]

def ears_from_openapi(sc):
    spec = yaml.safe_load(sc.api_spec)
    title = spec.get("info", {}).get("title", sc.id)
    lines = ["# Requirements Document", "", "## Introduction", "",
             f"{sc.short_app_description[0].upper() + sc.short_app_description[1:]} ({title})."
             + (" Data is stored in an SQLite database." if sc.needs_db else ""), "",
             "## Requirements", ""]
    n = 0
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            if method.lower() not in {"get", "post", "put", "delete", "patch"}:
                continue
            n += 1
            summary = (op.get("summary") or "Operation").strip().rstrip(".")
            desc = (op.get("description") or summary).strip().split("\n")[0].split(". ")[0].rstrip(".")
            if "(" in desc and ")" not in desc:
                desc = desc.split("(")[0].strip().rstrip(",")
            words = desc.split(" ")
            if words[0].lower() in {"adds", "retrieves", "allows", "lets", "expects", "prepares", "returns", "creates", "gets"}:
                words[0] = words[0][:-1]
            desc = " ".join(words)
            action = desc[0].lower() + desc[1:]
            lines += [f"### Requirement {n}: {summary}", "",
                      f"**User Story:** As a client, I want to {action}.", "",
                      "#### Acceptance Criteria", "",
                      f"1. WHEN a client sends a {method.upper()} request to {path}, THE SYSTEM SHALL {action}.", ""]
    return "\n".join(lines)

by_id = {s.id: s for s in scenarios.all_scenarios}
for sid in (PILOT or sorted(by_id)):
    sc = by_id[sid]
    d = ROOT / "tasks" / sid
    d.mkdir(parents=True, exist_ok=True)
    (d / "requirements.md").write_text(ears_from_openapi(sc))
    (d / "prompt_baseline.txt").write_text(sc.build_prompt(FlaskEnv, "openapi", "none", agent=False))
    cwes = sorted({f"CWE-{c.value['num']}" for c in sc.potential_cwes} - {"CWE-703"})
    (d / "meta.json").write_text(json.dumps({"scenario": sid, "baxbench_cwes": cwes,
                                             "n_functional_tests": len(sc.functional_tests),
                                             "n_security_tests": len(sc.security_tests)}, indent=2))
    print(sid, cwes)
