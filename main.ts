// news-image-20261126 — "THE WORLD", morning edition of Thu 26 Nov 2026.
// The front page is rendered at build time by draw.py (Pillow, deterministic)
// into entry.png beside this file; this program's only job is to place that
// exact PNG into the grader's output directory, unchanged.
// 22 stories: 3 heroes, 6 minis, 13 also-on, 12 map pins — every story dated
// Thu 26 Nov 2026 or labelled WED 25 Nov, with a DATE CHECK box saying so.
import { chmodSync, copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(join(here, "entry.png"), target);
chmodSync(target, 0o644);
console.log(`wrote ${target}`);
