import { execFileSync } from "node:child_process";
import { expect, test } from "@playwright/test";
import { docker, image, inContainer } from "./docker";

test("the image runs the App as the PUID and PGID it is given", () => {
	// the App is process 1, since the image execs it
	expect(inContainer("stat -c %u:%g /proc/1")).toBe(
		`${process.env.PUID}:${process.env.PGID}`,
	);
});

test("the image runs unprivileged when no PUID or PGID is given", () => {
	expect(docker("run", "--rm", image(), "id", "-u")).not.toBe("0");
});

test("the compose file runs the App unprivileged when no PUID or PGID is set", () => {
	const { PUID, PGID, ...unset } = process.env;
	// a compose project of its own, so that the tests' running App keeps its volume
	const env = {
		...unset,
		COMPOSE_PROJECT_NAME: `${process.env.COMPOSE_PROJECT_NAME}-unset-ids`,
	};
	const compose = (...args: string[]) =>
		execFileSync("docker", ["compose", ...args], { encoding: "utf8", env });
	try {
		expect(
			compose("run", "--rm", "--no-deps", "app", "id", "-u").trim(),
		).not.toBe("0");
	} finally {
		compose("down", "--volumes");
	}
});
