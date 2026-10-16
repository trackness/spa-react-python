import { type ChildProcess, execFileSync, spawn } from "node:child_process";
import { once } from "node:events";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { expect, test } from "@playwright/test";
import { dockerWith } from "./docker";
import { copyCheckout } from "./git";

test("image:run runs the checkout as it is now, not an Image built before a change", async () => {
	test.setTimeout(300_000);
	const checkout = copyCheckout();
	const name = `${process.env.COMPOSE_PROJECT_NAME}-image-run`;
	// a compose project and a build of the Image of its own, so that the other tests' build is left alone
	const compose = join(checkout, "compose.yaml");
	writeFileSync(
		compose,
		readFileSync(compose, "utf8").replace(/image: .*/, `image: ${name}`),
	);
	const env = { ...process.env, COMPOSE_PROJECT_NAME: name, HOST_PORT: "0" };
	const inCheckout = { cwd: checkout, env };
	let run: ChildProcess | undefined;
	try {
		execFileSync("task", ["image:build"], inCheckout);
		mkdirSync(join(checkout, "frontend/public"));
		writeFileSync(join(checkout, "frontend/public/changed.txt"), "changed\n");

		// a process group of its own, so that stopping it stops compose too, as Ctrl+C does
		run = spawn("task", ["image:run"], {
			...inCheckout,
			detached: true,
			stdio: "ignore",
		});
		await expect
			.poll(
				async () => {
					try {
						const address = dockerWith(
							inCheckout,
							"compose",
							"port",
							"app",
							"8000",
						);
						const port = address.split(":").pop();
						return (await fetch(`http://127.0.0.1:${port}/changed.txt`)).status;
					} catch {
						return "not running yet";
					}
				},
				{ timeout: 120_000 },
			)
			.toBe(200);
	} finally {
		// a child a signal killed has no exit code either, and no process group left to stop
		if (run?.pid && run.exitCode === null && run.signalCode === null) {
			process.kill(-run.pid, "SIGINT");
			await once(run, "exit");
		}
		dockerWith(inCheckout, "compose", "down", "--volumes");
		dockerWith(inCheckout, "image", "rm", "--force", name);
		rmSync(checkout, { recursive: true, force: true });
	}
});
