import { cp, mkdir, writeFile, rm } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceDir = resolve(rootDir, "frontend");
const outputDir = resolve(rootDir, "dist");
const apiBaseUrl = process.env.API_BASE_URL || process.env.VITE_API_BASE_URL || "";

await rm(outputDir, { recursive: true, force: true });
await mkdir(outputDir, { recursive: true });
await cp(sourceDir, outputDir, { recursive: true });
await cp(sourceDir, resolve(outputDir, "static"), { recursive: true });

const configSource = `window.CARDLEARN_API_BASE_URL = ${JSON.stringify(apiBaseUrl)} || "http://127.0.0.1:8000";\n`;
await writeFile(resolve(outputDir, "config.js"), configSource, "utf8");
await writeFile(resolve(outputDir, "static", "config.js"), configSource, "utf8");

console.log(`Built static frontend to ${outputDir}`);
