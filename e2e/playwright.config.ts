import { defineConfig } from "@playwright/test";

export default defineConfig({
	// Biome checks for a left-over test.only only alongside other test runners
	forbidOnly: Boolean(process.env.CI),
	// the e2e:test task runs the Image on a free port and passes its URL in
	use: { baseURL: process.env.APP_URL },
});
