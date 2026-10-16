import { expect, test } from "@playwright/test";
import { docker, image } from "./docker";

function healthcheck(): { Test: string[]; StartPeriod?: number } {
	const container = docker("compose", "ps", "--quiet", "app");
	return JSON.parse(
		docker("inspect", "--format", "{{json .Config.Healthcheck}}", container),
	);
}

test("the image reports itself healthy only once the App is ready", () => {
	expect(healthcheck().Test.join(" ")).toContain("/health/ready");
});

test("the image reports itself healthy on the listen address it is given", async () => {
	const container = docker(
		"run",
		"--detach",
		"--env",
		"APP_LISTEN_ADDRESS__HOST=127.0.0.2",
		"--env",
		"APP_LISTEN_ADDRESS__PORT=9000",
		image(),
	);
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
});

test("the image gives the App a start period to migrate in before a failed check counts", () => {
	expect(healthcheck().StartPeriod).toBeGreaterThan(0);
});
