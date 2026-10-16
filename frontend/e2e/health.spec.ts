import { execFileSync } from "node:child_process";
import { expect, test } from "@playwright/test";

function docker(...args: string[]): string {
	return execFileSync("docker", args, { encoding: "utf8" }).trim();
}

test("the image reports itself healthy once the App is ready", () => {
	const container = docker("compose", "ps", "--quiet", "app");

	expect(
		docker("inspect", "--format", "{{json .State.Health.Status}}", container),
	).toBe('"healthy"');
});
