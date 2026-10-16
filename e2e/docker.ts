import { execFileSync } from "node:child_process";
import { expect } from "@playwright/test";

// docker in another `cwd` or with another `env` than the e2e:test task's
export function dockerWith(
	options: { cwd?: string; env?: NodeJS.ProcessEnv },
	...args: string[]
): string {
	return execFileSync("docker", args, { ...options, encoding: "utf8" }).trim();
}

// the e2e:test task names the compose project the App runs in
export function docker(...args: string[]): string {
	return dockerWith({}, ...args);
}

// runs the Image with `runArgs`, such as --env options, and expects it to report itself healthy
export async function expectHealthy(...runArgs: string[]): Promise<void> {
	const container = docker("run", "--detach", ...runArgs, image());
	try {
		await expect
			.poll(
				() =>
					docker("inspect", "--format", "{{.State.Health.Status}}", container),
				// from Docker Engine 25, the start period checks every 5 seconds
				{ timeout: 20_000 },
			)
			.toBe("healthy");
	} finally {
		docker("rm", "--force", container);
	}
}

export function image(): string {
	return docker("compose", "config", "--images");
}

export function inContainer(command: string): string {
	return docker("compose", "exec", "app", "sh", "-c", command);
}
