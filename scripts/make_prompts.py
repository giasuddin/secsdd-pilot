"""Build the three prompt conditions for each task.
  A  baseline : BaxBench prompt, safety prompt "none"
  B  sis      : A + the [SECURITY] lines Spec It Safe added to the task's requirements.md
  C  oracle   : BaxBench prompt with its "specific" safety prompt, which names the exact
                CWEs the scenario's exploits test (an upper bound on what perfect
                elicitation could tell the agent)
Usage: python scripts/make_prompts.py <path-to-baxbench/src>
"""
import json, sys, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import _bax  # noqa: E402,F401
BAX = pathlib.Path(sys.argv[1]).resolve(); sys.path.insert(0, str(BAX))
import scenarios
from env.python import FlaskEnv
ROOT = pathlib.Path(__file__).resolve().parents[1]
by_id = {s.id: s for s in scenarios.all_scenarios}
MARK = "Make sure that the code is runnable"
for d in sorted((ROOT / "tasks").iterdir()):
    sc = by_id[d.name]
    a = (d / "prompt_baseline.txt").read_text()
    rep = json.loads((d / "sis_report.json").read_text())
    sec = []
    for l in rep["added_lines"]:
        m = re.search(r"\[SECURITY: [^\]]+\]\s*(.*)", l)
        if m and m.group(1) not in sec:
            sec.append(m.group(1))
    block = "The specification also contains the following security requirements, which the code must satisfy:\n" + "\n".join(f"- {s}" for s in sec) + "\n\n"
    b = a.replace(MARK, block + MARK, 1) if sec else a
    c = sc.build_prompt(FlaskEnv, "openapi", "specific", agent=False)
    (d / "prompt_sis.txt").write_text(b)
    (d / "prompt_oracle.txt").write_text(c)
    print(d.name, len(sec), "security lines")
