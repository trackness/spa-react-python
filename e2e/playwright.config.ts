import { defineConfig } from "@playwright/test";

export default defineConfig({
	// the e2e:test task runs the image on a free port and passes its URL in
	use: { baseURL: process.env.APP_URL },
});
