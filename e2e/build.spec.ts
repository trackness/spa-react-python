import {
	cpSync,
	mkdirSync,
	mkdtempSync,
	readFileSync,
	rmSync,
	writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { expect, test } from "@playwright/test";
import { docker } from "./docker";
import { checkoutFiles } from "./git";

const TAG = `${process.env.COMPOSE_PROJECT_NAME}-frontend-stage`;

// builds the Frontend's image stage from a copy of the checkout, changed first by `change`
function buildFrontendStage(change: (checkout: string) => void): void {
	const checkout = mkdtempSync(join(tmpdir(), "checkout-"));
	try {
		for (const file of checkoutFiles()) {
			cpSync(join("..", file), join(checkout, file), { recursive: true });
		}
		change(checkout);
		docker("build", "--target", "frontend", "--tag", TAG, checkout);
	} finally {
		rmSync(checkout, { recursive: true, force: true });
	}
}

// each test builds the Frontend's image stage
test.describe.configure({ timeout: 300_000 });

test.afterEach(() => {
	docker("image", "rm", "--force", TAG);
});

test("the image is built from a checkout's files, never the ones git ignores", () => {
	// files git ignores: Vite reads a local env file, and copies its public directory whole
	const ignored = [
		".DS_Store",
		"Icon\r",
		".apdisk",
		"Temporary Items",
		"notes~",
		"debug.log",
		"local.db",
	];
	buildFrontendStage((checkout) => {
		writeFileSync(join(checkout, "frontend/.env.local"), "VITE_LOCAL=1\n");
		mkdirSync(join(checkout, "frontend/public"));
		for (const file of ignored) {
			writeFileSync(join(checkout, "frontend/public", file), "");
		}
	});

	expect(
		docker(
			"run",
			"--rm",
			TAG,
			"find",
			"/app",
			...[".env.local", ...ignored].flatMap((name, index) =>
				index ? ["-o", "-name", name] : ["-name", name],
			),
		),
	).toBe("");
});

test("the image builds the Frontend from every file the checkout keeps", () => {
	buildFrontendStage((checkout) => {
		// Vite copies its public directory into the build as it is
		mkdirSync(join(checkout, "frontend/public"));
		writeFileSync(join(checkout, "frontend/public/kept.txt"), "kept\n");
		// named like Finder's Icon\r, which git ignores, yet a file of its own
		writeFileSync(join(checkout, "frontend/public/Icons"), "kept\n");
	});

	expect(docker("run", "--rm", TAG, "cat", "/app/frontend/dist/kept.txt")).toBe(
		"kept",
	);
	expect(docker("run", "--rm", TAG, "cat", "/app/frontend/dist/Icons")).toBe(
		"kept",
	);
});

test("the image is not built from a Frontend whose lockfile its manifest has outgrown", () => {
	expect(() =>
		buildFrontendStage((checkout) => {
			const manifest = join(checkout, "frontend/package.json");
			const parsed = JSON.parse(readFileSync(manifest, "utf8"));
			parsed.dependencies["left-pad"] = "1.3.0";
			writeFileSync(manifest, JSON.stringify(parsed));
		}),
	).toThrow(/ERR_PNPM_OUTDATED_LOCKFILE/);
});
