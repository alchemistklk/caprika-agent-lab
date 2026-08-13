import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const args = process.argv.slice(2);
const sourceFlag = args.indexOf("--source-root");
const outputFlag = args.indexOf("--output-dir");

if (sourceFlag === -1 || !args[sourceFlag + 1]) {
	throw new Error("Usage: render-pi-agent-turn-code.mjs --source-root <pi checkout> [--output-dir <directory>]");
}

const sourceRoot = path.resolve(args[sourceFlag + 1]);
const outputDir = path.resolve(
	outputFlag === -1
		? "assets/agent-implementation-study/pi-agent-turn"
		: args[outputFlag + 1],
);

const captures = [
	{
		name: "01-model-boundary",
		title: "Context becomes a provider-neutral model request",
		file: "packages/agent/src/agent-loop.ts",
		start: 288,
		end: 312,
		highlights: [[294, 312]],
	},
	{
		name: "02-stream-reduction",
		title: "Streaming deltas update one in-progress message",
		file: "packages/agent/src/agent-loop.ts",
		start: 317,
		end: 358,
		highlights: [
			[319, 323],
			[335, 342],
			[346, 358],
		],
	},
	{
		name: "03-loop-decision",
		title: "The loop branches on tool-call content",
		file: "packages/agent/src/agent-loop.ts",
		start: 192,
		end: 224,
		highlights: [
			[192, 203],
			[207, 216],
			[224, 224],
		],
	},
	{
		name: "04-stop-condition",
		title: "No tools and no queued messages means completion",
		file: "packages/agent/src/agent-loop.ts",
		start: 247,
		end: 274,
		highlights: [
			[247, 259],
			[262, 274],
		],
	},
	{
		name: "05-persistence-boundary",
		title: "Final message events cross into durable session state",
		file: "packages/coding-agent/src/core/agent-session.ts",
		start: 633,
		end: 657,
		highlights: [
			[633, 640],
			[650, 657],
		],
	},
];

function escapeHtml(value) {
	return value
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;");
}

function highlightTypeScript(value) {
	let html = escapeHtml(value);
	html = html.replace(/(&quot;|\"|')([^\n]*?)(\1)/g, '<span class="string">$1$2$3</span>');
	html = html.replace(
		/\b(await|async|const|let|if|else|for|while|return|case|switch|break|new|true|false|undefined|function)\b/g,
		'<span class="keyword">$1</span>',
	);
	html = html.replace(/\b([A-Z][A-Za-z0-9_]*)\b/g, '<span class="type">$1</span>');
	html = html.replace(/(\/\/.*)$/g, '<span class="comment">$1</span>');
	return html;
}

function isHighlighted(line, ranges) {
	return ranges.some(([start, end]) => line >= start && line <= end);
}

await fs.mkdir(outputDir, { recursive: true });
const executablePath =
	process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ||
	(process.platform === "darwin" ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : undefined);
const browser = await chromium.launch({ headless: true, executablePath });

try {
	for (const capture of captures) {
		const sourcePath = path.join(sourceRoot, capture.file);
		const source = await fs.readFile(sourcePath, "utf8");
		const selected = source.split("\n").slice(capture.start - 1, capture.end);
		const rows = selected
			.map((line, index) => {
				const lineNumber = capture.start + index;
				const active = isHighlighted(lineNumber, capture.highlights) ? " active" : "";
				return `<div class="code-line${active}"><span class="line-number">${lineNumber}</span><code>${highlightTypeScript(line) || " "}</code></div>`;
			})
			.join("\n");

		const page = await browser.newPage({ viewport: { width: 1440, height: 1200 }, deviceScaleFactor: 1 });
		await page.setContent(`
			<style>
				* { box-sizing: border-box; }
				body { margin: 0; padding: 36px; background: #090d14; color: #d7e0ea; }
				#capture { width: 1368px; overflow: hidden; border: 1px solid #273142; border-radius: 18px; background: #101722; box-shadow: 0 24px 70px rgba(0,0,0,.38); }
				.header { padding: 24px 28px 20px; border-bottom: 1px solid #273142; background: #131c29; }
				.title { font: 650 24px/1.25 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #f1f5f9; }
				.path { margin-top: 8px; font: 14px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace; color: #7dd3fc; }
				.code { padding: 20px 0 24px; }
				.code-line { display: grid; grid-template-columns: 76px 1fr; min-height: 30px; padding: 2px 28px 2px 0; border-left: 4px solid transparent; }
				.code-line.active { background: rgba(56, 189, 248, .075); border-left-color: #38bdf8; }
				.line-number { padding-right: 18px; text-align: right; user-select: none; color: #556579; font: 15px/26px ui-monospace, SFMono-Regular, Menlo, monospace; }
				code { white-space: pre; color: #d7e0ea; font: 16px/26px ui-monospace, SFMono-Regular, Menlo, monospace; tab-size: 2; }
				.keyword { color: #c084fc; font-weight: 650; }
				.type { color: #67e8f9; }
				.string { color: #bef264; }
				.comment { color: #718096; font-style: italic; }
			</style>
			<section id="capture">
				<header class="header">
					<div class="title">${escapeHtml(capture.title)}</div>
					<div class="path">${escapeHtml(capture.file)} · lines ${capture.start}–${capture.end}</div>
				</header>
				<div class="code">${rows}</div>
			</section>
		`);
		const element = page.locator("#capture");
		await element.screenshot({ path: path.join(outputDir, `${capture.name}.png`) });
		await page.close();
	}
} finally {
	await browser.close();
}
