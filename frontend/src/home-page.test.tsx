import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
	createMemoryHistory,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { expect, test } from "vitest";
import { routeTree } from "@/routeTree.gen";
import { server } from "@/test/server";

function renderHomePage() {
	const queryClient = new QueryClient({
		defaultOptions: { queries: { retry: false } },
	});
	const router = createRouter({
		routeTree,
		history: createMemoryHistory({ initialEntries: ["/"] }),
	});
	render(
		<QueryClientProvider client={queryClient}>
			<RouterProvider router={router} />
		</QueryClientProvider>,
	);
}

test("the home page shows the App is ready", async () => {
	server.use(
		http.get("/health/ready", () => HttpResponse.json({ status: "ok" })),
	);

	renderHomePage();

	expect(await screen.findByText("The App is ready.")).toBeInTheDocument();
});

test("the home page shows why the App is not ready", async () => {
	server.use(
		http.get("/health/ready", () =>
			HttpResponse.json({ status: "unavailable" }, { status: 503 }),
		),
	);

	renderHomePage();

	expect(
		await screen.findByText(
			/^The App is not ready: .* 503 Service Unavailable$/,
		),
	).toBeInTheDocument();
});
