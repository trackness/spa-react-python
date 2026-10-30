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

test("the home page tells screen readers what it finds, in the status it showed while checking", async () => {
	server.use(
		http.get("/health/ready", () => HttpResponse.json({ status: "ok" })),
	);

	render(<App router={await homePageRouter()} />);
	// a live region is announced only if it is there before its text changes
	const status = await screen.findByRole("status");
	expect(status).toHaveTextContent("Checking whether the App is ready…");

	await vi.waitFor(() => {
		expect(status).toHaveTextContent("The App is ready.");
	});
});

// answers every readiness request with `answer`, and counts them
function answerReadiness(answer: () => Response): { requests: number } {
	const counted = { requests: 0 };
	server.use(
		http.get("/health/ready", () => {
			counted.requests++;
			return answer();
		}),
	);
	return counted;
}

test("the home page shows at once the status the App is not ready with", async () => {
	const counted = answerReadiness(() =>
		HttpResponse.json({ status: "unavailable" }, { status: 503 }),
	);

	render(<App router={await homePageRouter()} />);

	expect(
		await screen.findByText("The App is not ready: unavailable."),
	).toBeInTheDocument();
	expect(counted.requests).toBe(1);
});

test("the home page shows at once the error status the App answered with", async () => {
	// what Starlette answers when a handler raises
	const counted = answerReadiness(
		() => new HttpResponse("Internal Server Error", { status: 500 }),
	);

	render(<App router={await homePageRouter()} />);

	expect(
		await screen.findByText(
			"The App is not ready: it answered with status 500.",
		),
	).toBeInTheDocument();
	expect(counted.requests).toBe(1);
});

test.each([
	["no answer", () => HttpResponse.error()],
	// what Vite's proxy answers while the App restarts
	["a gateway's error", () => new HttpResponse(null, { status: 502 })],
	// what a proxy answers with no App behind it
	["a gateway's unavailable", () => new HttpResponse(null, { status: 503 })],
])(
	"the home page asks again after %s, before showing the App did not answer",
	async (_, answer) => {
		const counted = answerReadiness(answer);
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
		expect(counted.requests).toBe(4);
	},
);
