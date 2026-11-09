# SecSDD pilot: does spec hardening make agent-written code more secure?

This repository holds a small pilot study for the SecSpec proposal (Amazon Research Awards, Fall 2026). It asks two questions on eight [BaxBench](https://github.com/logic-star-ai/baxbench) scenarios:

1. **Elicitation.** When [Spec It Safe](https://github.com/aws-samples/sample-kiro-spec-security-hardening) hardens a functional EARS spec, does it add the security requirements that BaxBench's exploits actually test?
2. **Effect on code.** Does giving a code generator Spec It Safe's added security lines change how many generated apps are correct and secure?

It also includes the proposal's running example (a team document service) and Spec It Safe's actual output on it.

**This is a pilot.** It uses 8 scenarios, one framework (Python-Flask), one generator model, and one sample per task and condition. The results are indicative, not statistically conclusive.

## Results at a glance

| Measure | A. Functional spec only | B. + Spec It Safe lines | C. + exact CWEs named (oracle) |
| --- | --- | --- | --- |
| Functionally correct | 8/8 | 4/8 | 8/8 |
| Correct and secure (BaxBench sec_pass@1) | 5/8 | 3/8 | 7/8 |
| Apps with a successful exploit | 3/8 | 1/8 | 1/8 |

**Elicitation:** across the 8 scenarios, BaxBench tests 21 CWEs. Spec It Safe added constraints for **0 of 21** by exact CWE ID. Counting related access-control and credential constraints as matches, it added **3 of 21**. Most of its added lines were transport-encryption (CWE-319), rate-limiting (CWE-307) and timing (CWE-208) requirements, which BaxBench does not test.

**Effect on code:**
- **Condition B broke functionality in 4 of 8 apps.** In all four, the generator added a minimum password length of 8 characters, which no requirement asked for. BaxBench's functional tests then failed because they register users with short passwords. This is a real risk: security text in the spec can push an agent to over-restrict, so conformance has to be checked against functional tests as well as exploits.
- **Naming the right CWEs (condition C) raised correct-and-secure apps from 5/8 to 7/8.** This is an upper bound on what better elicitation could give the agent. It supports the proposal's focus on finding the *right* security requirements and checking them.

Full per-task tables are in [results/RESULTS.md](results/RESULTS.md). Raw results are in `results/<condition>/<task>.json`, and test logs are in `results/<condition>/logs/`.

### Running example (proposal, Table 1)

Spec It Safe was run on the four-requirement spec in [examples/document-service/requirements.md](examples/document-service/requirements.md). Its output is in `spec_it_safe_output.txt` and `requirements.hardened.md` in the same folder.

| Security requirement | CWE | Spec It Safe result |
| --- | --- | --- |
| S1. Parameterized queries for search (R3) | CWE-89 | Not added: score 0.28, just under its 0.3 threshold |
| S2. Upload type, size and storage limits (R1) | CWE-434 | Added (4 constraints) |
| S3. Only owner or shared users may read a document (R2) | CWE-639 | Not added; flagged only as a candidate for optional agent review (score 0.16) |
| S4. Encode titles in HTML preview cards (R1 → R4) | CWE-79 | Not flagged |

Spec It Safe also added a cross-cutting authentication baseline (CWE-306).

## Method

### Tasks
We used eight BaxBench scenarios: CreditCardService, Login, ProfileCollection, Recipes, SecretStorage, ShopOverview, Unsubscribe and UserCreation. We chose them because their exploits run over HTTP or inspect the app's SQLite file, so they can be run without Docker (see below). Ground truth is BaxBench's own set of CWEs for each scenario, which is inferred from its security tests. We excluded CWE-703, which BaxBench adds to every scenario.

### Specs
`scripts/make_tasks.py` turns each scenario's OpenAPI spec into a Kiro-style `requirements.md`. It writes one EARS requirement per API operation, built mechanically from the operation's description: *"WHEN a client sends a POST request to /login, THE SYSTEM SHALL authenticate a user with email and password."* No security wording was added by hand.

### Hardening
`scripts/harden.mjs` runs Spec It Safe's released deterministic engine on each spec. It uses the default 0.3 threshold and pinned commit `2a3a002`. The script records every added line and the CWEs each addresses. The optional, non-deterministic agent review of sub-threshold candidates was **not** run; its candidates are recorded in `tasks/<task>/sis_report.json`.

### Prompts (three conditions)
`scripts/make_prompts.py` builds three prompts per task:
- **A. baseline:** the unmodified BaxBench prompt (Python-Flask, OpenAPI spec, no safety prompt).
- **B. sis:** prompt A plus every distinct requirement sentence Spec It Safe added to that task's spec.
- **C. oracle:** BaxBench's own "specific" safety prompt, which names the exact CWEs the scenario's exploits test. This is an upper bound for perfect elicitation.

### Generation
Each condition was generated by a separate instance of Claude Sonnet (run as a sub-agent). It received only the prompt files for that condition and was told to answer each prompt independently, in one attempt, without running or revising the code. The generator was not told about the study, the other conditions, or the tests. All 24 generated apps are in `solutions/<condition>/<task>/app.py`.

### Testing without Docker
BaxBench normally runs each app in a fresh Docker container. Docker Hub was not reachable from our environment, so `scripts/run_tests.py` runs each app as a local process instead. Each test gets a fresh copy of the app in a temporary working directory, mirroring BaxBench's fresh container per test, with `APP_SECRET` set as BaxBench sets it. BaxBench's file helpers (`load_file_from_docker`, `place_file_on_docker`) are redirected to that directory, so the password-storage checks read the app's real SQLite file. The functional tests and exploits themselves are BaxBench's unmodified code (commit `de885cd`).

As in BaxBench:
- an app is **correct** if it starts and passes all functional tests;
- it is **secure** if no exploit succeeds;
- **sec_pass@1** counts apps that are both.

## Reproduce

Requirements: Python 3.12+ and Node.js 20+.

```bash
# 1. Upstream code at the pinned commits
git clone https://github.com/logic-star-ai/baxbench.git && git -C baxbench checkout de885cd93d561682e203a5a0d57c33b08aac6f5e
git clone https://github.com/aws-samples/sample-kiro-spec-security-hardening.git sis && git -C sis checkout 2a3a002da0ec22ed1a349f51a3af7e868fff63e0

# 2. Python environment (BaxBench deps + the Flask packages its Python-Flask env allows)
python3 -m venv .venv && . .venv/bin/activate
pip install requests docker tabulate simple-parsing tqdm termcolor pyyaml openai anthropic pdfplumber imageio \
            Flask==3.1.0 passlib==1.7.4 fpdf==1.7.2 pyjwt==2.10.1

# 3. Tasks, hardening, prompts
python scripts/make_tasks.py baxbench/src
node scripts/harden.mjs sis/cwe-to-spec-mapping-library
python scripts/make_prompts.py baxbench/src
python scripts/elicitation.py

# 4. Generate code for each prompt (any model or agent), saving it as
#    solutions/<baseline|sis|oracle>/<Task>/app.py
#    (the solutions used in this pilot are included)

# 5. Test and summarize
python scripts/run_tests.py baxbench/src baseline sis oracle
python scripts/summarize.py
```

To rerun Spec It Safe on the running example:

```bash
cp examples/document-service/requirements.md /tmp/req.md
node sis/cwe-to-spec-mapping-library/dist/cli/harden-requirements.js --semantic-candidates /tmp/req.md
```

## Threats to validity

- **Small sample.** 8 tasks, 1 sample each, 1 model and 1 framework. Differences of one or two apps are within noise.
- **Mechanical specs.** Our EARS requirements are short and derived from API descriptions. Spec It Safe is designed for richer, human-written specs and may add more on those. Its optional agent review step was not run.
- **Over-restriction in condition B.** The four functional failures came from the generator adding a password-length rule. A different model might not do this. Also, in an app that fails functionally, an exploit may not run at all (for example, if registration fails), which is why sec_pass@1 counts only correct apps.
- **Docker-free runner.** It runs the apps as local processes rather than in containers. Exploits that depend on container internals were avoided by choosing scenarios that don't need them, but small differences from the official harness are possible.
- **Oracle prompt.** Condition C also adds a generic "follow best practices" sentence, so it is an upper bound, not a pure elicitation effect.

## Licenses and attribution

- This repository's code is released under Apache 2.0 (see `LICENSE`).
- The prompts and test code in `tasks/` are derived from BaxBench (MIT, © LogicStar AI and ETH Zurich SRI Lab).
- Spec It Safe is MIT-0 (© Amazon.com, Inc. or its affiliates). Its output is included in `tasks/` and `examples/`.
- See `NOTICE`.
