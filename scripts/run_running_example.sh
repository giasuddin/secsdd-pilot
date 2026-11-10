#!/usr/bin/env bash
# Reproduce the Spec It Safe runs for the proposal's running example
# (Table 1 and Appendix B). Requires Node.js and a checkout of Spec It Safe
# at commit 2a3a002 in ./sis (see README, "Reproduce").
#
# Usage: bash scripts/run_running_example.sh [path-to-sis-checkout]
set -euo pipefail

SIS="${1:-sis}"
CLI="$SIS/cwe-to-spec-mapping-library/dist/cli/harden-requirements.js"
EX="examples/document-service"
OUT="$(mktemp -d)"

want="2a3a002da0ec22ed1a349f51a3af7e868fff63e0"
have="$(git -C "$SIS" rev-parse HEAD)"
if [ "$have" != "$want" ]; then
  echo "Warning: Spec It Safe is at $have, not $want. Output may differ." >&2
fi

# The tool edits the file in place, so run each mode on its own copy.
cp "$EX/requirements.md" "$OUT/run1.md"
cp "$EX/requirements.md" "$OUT/run2.md"

# Run 1: default review mode (Table 1, "Spec It Safe (actual run)").
node "$CLI" --semantic-candidates "$OUT/run1.md" > "$OUT/run1_output.txt"

# Run 2: also list every sub-threshold candidate (Appendix B, "run 2 only").
node "$CLI" --semantic-candidates --semantic-all "$OUT/run2.md" > "$OUT/run2_output.txt"

echo "Hardened spec:        $OUT/run1.md   (compare with $EX/requirements.hardened.md)"
echo "Run 1 output:         $OUT/run1_output.txt   (compare with $EX/spec_it_safe_output.txt)"
echo "Run 2 output:         $OUT/run2_output.txt   (compare with $EX/spec_it_safe_output_semantic_all.txt)"
echo "File names inside the outputs differ; everything else should match."
