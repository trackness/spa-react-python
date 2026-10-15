import { createMemoryHistory } from "@tanstack/react-router";
import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { expect, onTestFinished, test, vi } from "vitest";
import { App, createAppRouter } from "@/app";
import { server } from "@/test/server";

// the home page's code is split into its own chunk, which the router loads asynchronously
async function homePageRouter() {
	const router = createAppRouter(
		createMemoryHistory({ initialEntries: ["/"] }),
	);
	await router.load();
	return router;
}

test("the home page shows the App is ready", async () => {
	server.use(
		http.get("/health/ready", () => HttpResponse.json({ status: "ok" })),
	);

	render(<App router={await homePageRouter()} />);

	expect(await screen.findByText("The App is ready.")).toBeInTheDocument();
});

test("the home page shows at once the status the App is not ready with", async () => {
	let requests = 0;
	server.use(
		http.get("/health/ready", () => {
			requests++;
			return HttpResponse.json({ status: "unavailable" }, { status: 503 });
		}),
	);

	render(<App router={await homePageRouter()} />);

	expect(
		await screen.findByText("The App is not ready: unavailable."),
	).toBeInTheDocument();
	expect(requests).toBe(1);
});

test("the home page asks again before showing the App did not answer", async () => {
	let requests = 0;
	server.use(
		http.get("/health/ready", () => {
			requests++;
			return HttpResponse.error();
		}),
	);
	const router = await homePageRouter();
	vi.useFakeTimers();
	onTestFinished(() => {
		vi.useRealTimers();
	});

	render(<App router={router} />);
	// past TanStack Query's three retries, 1, 2 and 4 seconds apart
	await vi.advanceTimersByTimeAsync(7000);

	await vi.waitFor(() => {
		expect(screen.getByText("The App did not answer.")).toBeInTheDocument();
	});
	expect(requests).toBe(4);
});
