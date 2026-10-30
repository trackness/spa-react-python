import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";
import { client } from "@/client/.kubb/client";
import { server } from "@/test/server";

// Node's fetch rejects the relative URLs the Client uses in the browser
client.setConfig({ baseURL: window.location.origin });
// the router scrolls to the top after each render; jsdom lays nothing out, so it has no scrollTo
window.scrollTo = () => {};

beforeAll(() => server.listen({ onUnhandledFrame: "error" }));
afterEach(() => {
	// Testing Library cleans up by itself only when Vitest's globals are on
	cleanup();
	server.resetHandlers();
});
afterAll(() => server.close());
