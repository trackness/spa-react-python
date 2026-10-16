import { execFileSync } from "node:child_process";
import { cpSync, existsSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// a copy of the checkout in a new directory, for a test to change; the test removes it
export function copyCheckout(): string {
	const checkout = mkdtempSync(join(tmpdir(), "checkout-"));
	for (const file of checkoutFiles()) {
		cpSync(join("..", file), join(checkout, file), { recursive: true });
	}
	return checkout;
}

// every file git keeps, as the checkout has it now, as paths from the repository's root
export function checkoutFiles(): string[] {
	return (
		execFileSync(
			"git",
			["-C", "..", "ls-files", "--cached", "--others", "--exclude-standard"],
			{ encoding: "utf8" },
		)
			.split("\n")
			// git still lists a committed file the checkout has deleted
			.filter((file) => file && existsSync(join("..", file)))
	);
}
