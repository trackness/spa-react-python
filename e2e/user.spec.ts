import { expect, test } from "@playwright/test";
import {
	docker,
	dockerWith,
	expectHealthy,
	image,
	inContainer,
} from "./docker";

test("the App runs as the PUID and PGID its container is given", () => {
	// the App is process 1, since the Image's entrypoint execs it
	expect(inContainer("stat -c %u:%g /proc/1")).toBe(
		`${process.env.PUID}:${process.env.PGID}`,
	);
});

test("the App runs unprivileged when its container is given no PUID or PGID", () => {
	expect(docker("run", "--rm", image(), "id", "-u")).not.toBe("0");
});

test("the App runs as 1000 when its container's PUID and PGID are empty", () => {
	expect(
		docker(
			"run",
			"--rm",
			"--env",
			"PUID=",
			"--env",
			"PGID=",
			image(),
			"stat",
			"-L",
			"-c",
			"%u:%g",
			"/proc/self",
		),
	).toBe("1000:1000");
});

test("the App runs as the user Docker starts the Image as, when that is not root", async () => {
	expect(
		docker("run", "--rm", "--user", "1234:2345", image(), "id", "-u"),
	).toBe("1234");
	await expectHealthy("--user", "1234:2345");
});

test("compose.yaml runs the App unprivileged when no PUID or PGID is set", () => {
	const { PUID, PGID, ...unset } = process.env;
	// a compose project of its own, so that the tests' running App keeps its volume
	const env = {
		...unset,
		COMPOSE_PROJECT_NAME: `${process.env.COMPOSE_PROJECT_NAME}-unset-ids`,
	};
	try {
		expect(
			dockerWith(
				{ env },
				"compose",
				"run",
				"--rm",
				"--no-deps",
				"app",
				"id",
				"-u",
			),
		).not.toBe("0");
	} finally {
		dockerWith({ env }, "compose", "down", "--volumes");
	}
});
