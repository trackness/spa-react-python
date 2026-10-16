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

// runs `use` with a volume of its own, so that the running App's database is left alone
function withVolume(use: (volume: string) => void): void {
	const volume = docker("volume", "create");
	try {
		use(volume);
	} finally {
		docker("volume", "rm", volume);
	}
}

// as the Image's own APP_DATABASE_FILE, /data/app.db, names them
const SQLITE_FILES = ["app.db", "app.db-wal", "app.db-shm", "app.db-journal"];

function runOnVolume(volume: string, ...args: string[]): string {
	return docker("run", "--rm", "--volume", `${volume}:/data`, ...args);
}

// the owners `paths` on `volume` have, once the Image's entrypoint has run
function ownersOf(volume: string, ...paths: string[]): string[] {
	return runOnVolume(volume, image(), "stat", "-c", "%u", ...paths).split("\n");
}

// a link on the volume, as the App could leave one in its database's directory
function linkOnVolume(volume: string, target: string, link: string): void {
	runOnVolume(volume, "--entrypoint", "ln", image(), "-s", target, link);
}

// the entrypoint's own refusal, not any failure to run
function expectRefused(databaseFile: string, volume?: string): void {
	const mount = volume ? ["--volume", `${volume}:/data`] : [];
	expect(() =>
		docker(
			"run",
			"--rm",
			"--env",
			`APP_DATABASE_FILE=${databaseFile}`,
			...mount,
			image(),
			"true",
		),
	).toThrow(
		"APP_DATABASE_FILE must name a file in an absolute directory other than /, with no link, ., .. or repeated / on the way",
	);
}

test("the Image's entrypoint gives the App its database's directory and files, and nothing else in it", () => {
	withVolume((volume) => {
		// SQLite's files and a file of someone else's, all as root left them
		const sqliteFiles = SQLITE_FILES.map((file) => `/data/${file}`);
		runOnVolume(
			volume,
			"--entrypoint",
			"touch",
			image(),
			...sqliteFiles,
			"/data/app.db.bak",
		);

		expect(
			ownersOf(volume, "/data", ...sqliteFiles, "/data/app.db.bak"),
		).toEqual(["1000", ...sqliteFiles.map(() => "1000"), "0"]);
	});
});

for (const file of SQLITE_FILES) {
	test(`the Image's entrypoint gives the App no file the link ${file} points to`, () => {
		withVolume((volume) => {
			linkOnVolume(volume, "/etc/passwd", `/data/${file}`);

			expect(ownersOf(volume, "/etc/passwd")).toEqual(["0"]);
		});
	});
}

test("the Image's entrypoint refuses a database whose directory a link leads to", () => {
	withVolume((volume) => {
		linkOnVolume(volume, "/etc", "/data/database");

		expectRefused("/data/database/app.db", volume);
	});
});

test("the Image's entrypoint refuses a database path that names a directory", () => {
	withVolume((volume) => {
		runOnVolume(volume, "--entrypoint", "mkdir", image(), "/data/directory");

		expectRefused("/data/directory", volume);
	});
});

// paths that would steer root's chown elsewhere than the database's own directory and files
for (const [databaseFile, why] of [
	["", "no value"],
	["/app.db", "a directory of /"],
	["//app.db", "a directory of / written as //"],
	["app.db", "a directory relative to the Backend's working directory"],
	["/data/x\n/app.db", "a newline a shell's command substitution would drop"],
	["/data/./app.db", "a . step"],
	["/data/../data/app.db", "a .. step"],
	["/data//app.db", "a repeated /"],
	["/data/..", "a file name of .."],
	["/data/.", "a file name of ."],
	["/data/", "no file name"],
]) {
	test(`the Image's entrypoint refuses a database path with ${why}`, () => {
		expectRefused(databaseFile);
	});
}

// the Image's own database, and one whose name holds a pattern's wildcards
for (const databaseFile of ["/data/app.db", "/data/app[1].db"]) {
	test(`the App keeps writing ${databaseFile} after PUID and PGID change`, () => {
		withVolume((volume) => {
			const writeAs = (id: string) =>
				runOnVolume(
					volume,
					"--env",
					`PUID=${id}`,
					"--env",
					`PGID=${id}`,
					"--env",
					`APP_DATABASE_FILE=${databaseFile}`,
					image(),
					"python",
					"-c",
					onDatabase(
						`database.execute('CREATE TABLE written_by_${id} (id INTEGER)')`,
					),
				);
			writeAs("1111");

			expect(() => writeAs("2222")).not.toThrow();
		});
	});
}
