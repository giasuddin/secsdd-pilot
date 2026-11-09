// Run Spec It Safe (deterministic engine, default threshold 0.3) on each task's
// requirements.md copy and record the added lines and the CWEs they address.
// Usage: node scripts/harden.mjs <path-to-spec-it-safe>/cwe-to-spec-mapping-library
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
const lib = await import(pathToFileURL(path.join(process.argv[2], "dist/index.js")).href);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const tasks = fs.readdirSync(path.join(root, "tasks"));
for (const t of tasks) {
  const dir = path.join(root, "tasks", t);
  const hardened = path.join(dir, "requirements.hardened.md");
  fs.copyFileSync(path.join(dir, "requirements.md"), hardened);
  const res = await lib.hardenMarkdownFile(hardened, { semanticCandidates: true });
  const cwes = new Set();
  for (const r of res.report.results) for (const p of r.proposedRequirements) for (const c of p.addressesCWEs) cwes.add(c);
  const triggered = res.report.results.flatMap(r => r.triggeredCWEs.map(c => ({ cwe: c.cweId, conf: +c.confidence.toFixed(2) })));
  const semantic = (res.semanticCandidates || []).map(c => ({ cwe: c.cweId, conf: c.confidence }));
  const out = { task: t, added_lines: res.addedLines.map(l => l.text), cwes_addressed: [...cwes].sort(), triggered, semantic_candidates: semantic };
  fs.writeFileSync(path.join(dir, "sis_report.json"), JSON.stringify(out, null, 2));
  console.log(t, out.cwes_addressed.join(" "), "| semantic:", semantic.map(s => s.cwe).join(" "));
}
