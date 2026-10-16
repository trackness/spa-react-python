import { expect, test } from "@playwright/test";
import { inContainer } from "./docker";
import { checkoutFiles } from "./git";

test("the Image runs the App without Node", () => {
	expect(inContainer("find / -xdev -type f -name node")).toBe("");
});

test("the Image carries the Backend as the checkout has it, with none of the files git ignores", () => {
	const kept = checkoutFiles().filter(
		(file) => file.startsWith("backend/") && !file.startsWith("backend/tests/"),
	);
	// the virtual environment and the bytecode are built in the Image
	const shipped = inContainer(
		"cd /app && find backend -path backend/.venv -prune -o -name __pycache__ -prune -o -type f -print",
	).split("\n");

	expect(shipped.sort()).toEqual(kept.sort());
});

test("the Image carries the App's bytecode, which the App cannot write as it runs", () => {
	expect(inContainer("find /app/backend/src -name '*.pyc'")).not.toBe("");
});

test("the Image carries none of the Backend's development tools", () => {
	expect(
		inContainer(
			"find / -xdev -type f \\( -name ruff -o -name ty -o -name prek -o -name pytest \\)",
		),
	).toBe("");
});
