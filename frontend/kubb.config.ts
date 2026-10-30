import { pluginFetch } from "@kubb/plugin-fetch";
import { pluginReactQuery } from "@kubb/plugin-react-query";
import { pluginTs } from "@kubb/plugin-ts";
import { defineConfig } from "kubb/config";

export default defineConfig({
	input: "../backend/openapi.json",
	output: { path: "./src/client", clean: true },
	plugins: [pluginTs(), pluginFetch(), pluginReactQuery()],
});
