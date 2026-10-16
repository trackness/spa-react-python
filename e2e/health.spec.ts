import { expect, test } from "@playwright/test";
import { docker, expectHealthy, image } from "./docker";

function healthcheck(): { Test: string[]; StartPeriod?: number } {
	const container = docker("compose", "ps", "--quiet", "app");
	return JSON.parse(
		docker("inspect", "--format", "{{json .Config.Healthcheck}}", container),
	);
}

test("the Image's healthcheck passes only once the App is ready", () => {
	expect(healthcheck().Test.join(" ")).toContain("/health/ready");
});

test("the Image's healthcheck passes on the listen address the App is given", async () => {
	await expectHealthy(
		"--env",
		"APP_LISTEN_ADDRESS__HOST=127.0.0.2",
		"--env",
		"APP_LISTEN_ADDRESS__PORT=9000",
	);
});

test("the Image declares the port the App listens on", () => {
	expect(
		JSON.parse(
			docker(
				"image",
				"inspect",
				"--format",
				"{{json .Config.ExposedPorts}}",
				image(),
			),
		),
	).toHaveProperty(["8000/tcp"]);
});

test("the Image's healthcheck gives the App a start period to migrate in before a failed check counts", () => {
	expect(healthcheck().StartPeriod).toBeGreaterThan(0);
});
