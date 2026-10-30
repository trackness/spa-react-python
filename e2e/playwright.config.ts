import { defineConfig } from "@playwright/test";

export default defineConfig({
	// a left-over test.only in CI would skip every other test
	forbidOnly: Boolean(process.env.CI),
	// the e2e:test task runs the Image on a free port and passes its URL in
	use: { baseURL: process.env.APP_URL },
});
