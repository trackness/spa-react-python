import { expect, test } from "@playwright/test";
import { docker, expectHealthy, image } from "./docker";

// Python run in a container, with the App's database open as `database`
function onDatabase(python: string): string {
	return `import os, sqlite3; database = sqlite3.connect(os.environ['APP_DATABASE_FILE']); ${python}`;
}

test("the database outlives the container, on compose.yaml's volume", () => {
	docker(
		"compose",
		"exec",
		"app",
		"python",
		"-c",
		onDatabase("database.execute('CREATE TABLE outlives (id INTEGER)')"),
	);

	// a new container of the same service, which shares only the volume
	const tables = docker(
		"compose",
		"run",
		"--rm",
		"--no-deps",
		"app",
		"python",
		"-c",
		onDatabase(
			"print([name for (name,) in database.execute('SELECT name FROM sqlite_master')])",
		),
	);

	expect(tables).toContain("outlives");
});

test("the App keeps its database wherever APP_DATABASE_FILE puts it", async () => {
	await expectHealthy(
		"--env",
		"APP_DATABASE_FILE=/var/lib/app/database/app.db",
	);
});

test("the Image gives the App its database's files and nothing else in their directory", () => {
	expect(
		docker(
			"run",
			"--rm",
			"--env",
			"APP_DATABASE_FILE=/app.db",
			image(),
			"stat",
			"-c",
			"%u",
			"/usr",
		),
	).toBe("0");
});

// the Image's own database, and one whose name holds a pattern's wildcards
for (const database of ["/data/app.db", "/data/app[1].db"]) {
	test(`the App keeps writing ${database} after PUID and PGID change`, () => {
		// a volume of its own, so that the running App's database is left alone
		const volume = docker("volume", "create");
		const writeAs = (id: string) =>
			docker(
				"run",
				"--rm",
				"--env",
				`PUID=${id}`,
				"--env",
				`PGID=${id}`,
				"--env",
				`APP_DATABASE_FILE=${database}`,
				"--volume",
				`${volume}:/data`,
				image(),
				"python",
				"-c",
				onDatabase(
					`database.execute('CREATE TABLE written_by_${id} (id INTEGER)')`,
				),
			);
		try {
			writeAs("1111");

			expect(() => writeAs("2222")).not.toThrow();
		} finally {
			docker("volume", "rm", volume);
		}
	});
}
