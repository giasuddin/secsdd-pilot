# Running example: document service

This is the running example in the SecSpec proposal (Section 3, Table 1, and Appendix B).

We wrote this example to show four common weaknesses in one small spec. It is **not** a BaxBench or CWEval task, and no application code was generated for it. The only experiment on it is running Spec It Safe, which is what Table 1's "Spec It Safe (actual run)" column and Appendix B report. The "SecSpec O1 (planned)" column in Table 1 describes the proposed method; it is not a result.

| File | What it is |
| --- | --- |
| `requirements.md` | Kiro-style requirements with four EARS requirements (R1–R4). This is the input to Spec It Safe. |
| `design.md` | The design: data model (owner, share list), endpoints, and data flows. Spec It Safe does not read it. It is the input SecSpec O1 would use. |
| `requirements.hardened.md` | `requirements.md` after Spec It Safe added its security lines (run 1). |
| `spec_it_safe_output.txt` | Console output of run 1: `--semantic-candidates` (default review mode). |
| `spec_it_safe_output_semantic_all.txt` | Console output of run 2: `--semantic-candidates --semantic-all`, which also lists every candidate below the 0.3 threshold. |

## Security requirements the example needs

| SR | Requirement | CWE | Spec It Safe result |
| --- | --- | --- | --- |
| S1 | Search uses parameterized queries (R3) | CWE-89 | Not added. Scored 0.28, under the 0.3 threshold. Listed only in run 2. |
| S2 | Upload type, size, and storage limits (R1) | CWE-434 | Added: four constraints. |
| S3 | Only the owner or shared users may read a document (R2) | CWE-639 | Not added. Sent to optional agent review (score 0.16). |
| S4 | Encode titles before rendering preview cards (R1 → R4) | CWE-79 | Not added. Listed only in run 2 (score 0.16). |

Spec It Safe also added three cross-cutting lines requiring authentication on every request (CWE-306).

## Reproduce

Spec It Safe version: [aws-samples/sample-kiro-spec-security-hardening](https://github.com/aws-samples/sample-kiro-spec-security-hardening), Git commit `2a3a002da0ec22ed1a349f51a3af7e868fff63e0`. Set it up as described in the top-level README, then run from the repository root:

```bash
bash scripts/run_running_example.sh sis
```

We reran both runs on 2026-11-10 at this commit. The hardened file and both console outputs matched the stored files exactly, apart from the temporary file names printed in the output.
