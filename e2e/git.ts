import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

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
