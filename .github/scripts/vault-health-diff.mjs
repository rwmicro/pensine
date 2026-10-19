// Compares two vault-health reports (learn-nebula's scripts/vault-health.ts,
// run on the PR's base and on its head) and fails only on what the PR adds:
// a new broken link, a newly missing frontmatter field, a new broken clip.
// Near-empty and mostly-English notes are listed as warnings, never failures.
//
//   node vault-health-diff.mjs base.json head.json
import fs from "node:fs";

const [base, head] = process.argv.slice(2).map((f) => JSON.parse(fs.readFileSync(f, "utf8")));

const keys = (report) => {
  const out = new Map();
  const add = (key, msg) => out.set(key, msg);
  for (const n of report.brokenLinks ?? [])
    for (const l of n.links) add(`link|${n.slug}|${l.target}`, `${n.path ?? n.slug}: lien cassé « ${l.target} » (${l.reason})`);
  for (const n of report.frontmatter ?? [])
    for (const f of n.missing) add(`fm|${n.slug}|${f}`, `${n.path ?? n.slug}: frontmatter sans « ${f} »`);
  for (const n of report.audio ?? [])
    for (const c of n.clips) add(`audio|${n.slug}|${c.src}`, `${n.path ?? n.slug}: clip ${c.problem} « ${c.src} »`);
  for (const c of report.prereqCycles ?? [])
    add(`cycle|${JSON.stringify(c)}`, `cycle de prérequis : ${JSON.stringify(c)}`);
  return out;
};
const warnings = (report) => {
  const out = new Map();
  for (const n of report.nearEmpty ?? []) out.set(`empty|${n.slug}`, `${n.path ?? n.slug}: presque vide (${n.chars} caractères)`);
  for (const n of report.english ?? []) out.set(`en|${n.slug}`, `${n.path ?? n.slug}: surtout en anglais`);
  return out;
};

const added = (a, b) => [...b].filter(([k]) => !a.has(k)).map(([, m]) => m);
const errors = added(keys(base), keys(head));
const warns = added(warnings(base), warnings(head));

const lines = [`Notes : ${base.notes} → ${head.notes}`];
for (const m of errors) {
  console.log(`::error::${m}`);
  lines.push(`- ❌ ${m}`);
}
for (const m of warns) {
  console.log(`::warning::${m}`);
  lines.push(`- ⚠️ ${m}`);
}
if (!errors.length && !warns.length) lines.push("Rien de nouveau à signaler.");
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `## Santé du vault\n\n${lines.join("\n")}\n`);
console.log(lines.join("\n"));
process.exit(errors.length ? 1 : 0);
