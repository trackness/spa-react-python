import { expect, test } from "@playwright/test";
import { inContainer } from "./docker";
import { checkoutFiles } from "./git";

// the Backend's files that find's `expression` selects, leaving out its virtual
// environment, which is built in the Image
function backendFiles(expression: string): string[] {
	return inContainer(
		`cd /app && find backend -path backend/.venv -prune -o ${expression} -print`,
	).split("\n");
}

test("the Image carries no Node", () => {
	expect(inContainer("find / -xdev -type f -name node")).toBe("");
});

test("the Image carries the Backend, but for its tests, as the checkout has it, with none of the files git ignores", () => {
	const kept = checkoutFiles().filter(
		(file) => file.startsWith("backend/") && !file.startsWith("backend/tests/"),
	);
	// the bytecode is built in the Image
	const shipped = backendFiles("-name __pycache__ -prune -o -type f");

	expect(shipped.sort()).toEqual(kept.sort());
});

test("the Image carries the Backend's bytecode, which the App cannot write as it runs", () => {
	const tag = inContainer(
		"python -c 'import sys; print(sys.implementation.cache_tag)'",
	);
	const sources = backendFiles("-name '*.py'");
	const bytecode = new Set(backendFiles(`-name '*.${tag}.pyc'`));

	expect(sources).toContain("backend/src/app/main.py");
	expect(
		sources.filter((source) => {
			const [, directory, module] = source.match(/^(.*)\/([^/]*)\.py$/) ?? [];
			return !bytecode.has(`${directory}/__pycache__/${module}.${tag}.pyc`);
		}),
	).toEqual([]);
});

test("the Image carries none of the Backend's development tools", () => {
	expect(
		inContainer(
			"find / -xdev -type f \\( -name ruff -o -name ty -o -name prek -o -name pytest \\)",
		),
	).toBe("");
});
