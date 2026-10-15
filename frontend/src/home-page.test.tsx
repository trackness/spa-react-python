import { QueryClient } from "@tanstack/react-query";
import { createMemoryHistory } from "@tanstack/react-router";
import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { expect, test } from "vitest";
import { App, createAppRouter } from "@/app";
import { server } from "@/test/server";

function renderHomePage() {
	render(
		<App
			queryClient={
				new QueryClient({ defaultOptions: { queries: { retry: false } } })
			}
			router={createAppRouter(createMemoryHistory({ initialEntries: ["/"] }))}
		/>,
	);
}

test("the home page shows the App is ready", async () => {
	server.use(
		http.get("/health/ready", () => HttpResponse.json({ status: "ok" })),
	);

	renderHomePage();

	expect(await screen.findByText("The App is ready.")).toBeInTheDocument();
});

test("the home page shows the status the App is not ready with", async () => {
	server.use(
		http.get("/health/ready", () =>
			HttpResponse.json({ status: "unavailable" }, { status: 503 }),
		),
	);

	renderHomePage();

	expect(
		await screen.findByText("The App is not ready: unavailable."),
	).toBeInTheDocument();
});

test("the home page shows the App did not answer", async () => {
	server.use(http.get("/health/ready", () => HttpResponse.error()));

	renderHomePage();

	expect(
		await screen.findByText("The App did not answer."),
	).toBeInTheDocument();
});
