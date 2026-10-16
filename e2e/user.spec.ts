import { expect, test } from "@playwright/test";
import {
	docker,
	dockerWith,
	expectHealthy,
	image,
	inContainer,
} from "./docker";

test("the Image runs the App as the PUID and PGID it is given", () => {
	// the App is process 1, since the Image execs it
	expect(inContainer("stat -c %u:%g /proc/1")).toBe(
		`${process.env.PUID}:${process.env.PGID}`,
	);
});

test("the Image runs unprivileged when no PUID or PGID is given", () => {
	expect(docker("run", "--rm", image(), "id", "-u")).not.toBe("0");
});

test("the Image runs as the user Docker starts it as, when that is not root", async () => {
	expect(
		docker("run", "--rm", "--user", "1234:2345", image(), "id", "-u"),
	).toBe("1234");
	await expectHealthy("--user", "1234:2345");
});

test("the compose file runs the App unprivileged when no PUID or PGID is set", () => {
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
