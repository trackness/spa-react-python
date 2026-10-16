import { execFileSync } from "node:child_process";

// the e2e:test task names the compose project the image runs in
export function docker(...args: string[]): string {
	return execFileSync("docker", args, { encoding: "utf8" }).trim();
}

export function image(): string {
	return docker("compose", "config", "--images");
}

export function inContainer(command: string): string {
	return docker("compose", "exec", "app", "sh", "-c", command);
}
