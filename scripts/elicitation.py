"""Compare the CWEs Spec It Safe added (deterministic engine, default threshold)
with the CWEs BaxBench's exploits test for each scenario.
'exact' = same CWE ID. 'related' additionally credits an access-control constraint
(CWE-306/639/862/863/284) for an access-control CWE (CWE-284/863), and a password
constraint (CWE-256/916/522) for CWE-522."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
ACCESS = {"CWE-284", "CWE-306", "CWE-639", "CWE-862", "CWE-863"}
CRED = {"CWE-256", "CWE-916", "CWE-522", "CWE-257"}
def related(target, added):
    if target in added: return True
    if target in {"CWE-284", "CWE-863"} and added & ACCESS: return True
    if target == "CWE-522" and added & CRED: return True
    return False
rows, tot, ex, rel = [], 0, 0, 0
for d in sorted((ROOT / "tasks").iterdir()):
    meta = json.loads((d / "meta.json").read_text()); rep = json.loads((d / "sis_report.json").read_text())
    tgt = meta["baxbench_cwes"]; added = set(rep["cwes_addressed"])
    e = [c for c in tgt if c in added]; r = [c for c in tgt if related(c, added)]
    tot += len(tgt); ex += len(e); rel += len(r)
    rows.append({"task": d.name, "baxbench_cwes": tgt, "sis_added_cwes": sorted(added),
                 "sis_semantic_candidates": sorted({c["cwe"] for c in rep["semantic_candidates"]}),
                 "found_exact": e, "found_related": r})
out = {"per_task": rows, "total_target_cwes": tot, "found_exact": ex, "found_related": rel}
(ROOT / "results" / "elicitation.json").write_text(json.dumps(out, indent=2))
for x in rows: print(f"{x['task']:18} target={x['baxbench_cwes']} added={x['sis_added_cwes']} related={x['found_related']}")
print(f"exact {ex}/{tot}, related {rel}/{tot}")
