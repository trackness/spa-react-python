/// <reference types="vitest/config" />
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
	// the router plugin must come before the React plugin
	plugins: [
		tanstackRouter({ target: "react", autoCodeSplitting: true }),
		react(),
	],
	resolve: { tsconfigPaths: true },
	server: {
		// lists every top-level path the Frontend calls on the App; a new API path is added here
		proxy: {
			// the dev task loads the Backend's listen address from the environment files
			"/health": `http://${process.env.APP_LISTEN_ADDRESS__HOST}:${process.env.APP_LISTEN_ADDRESS__PORT}`,
		},
	},
	test: {
		environment: "jsdom",
		setupFiles: ["./src/test/setup.ts"],
	},
});
