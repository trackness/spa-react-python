import { type QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
	createRouter,
	type RouterHistory,
	RouterProvider,
} from "@tanstack/react-router";
import { StrictMode } from "react";
import { routeTree } from "@/routeTree.gen";

// without a history the router follows the browser's address bar
export function createAppRouter(history?: RouterHistory) {
	return createRouter({ routeTree, history });
}

type AppRouter = ReturnType<typeof createAppRouter>;

declare module "@tanstack/react-router" {
	interface Register {
		router: AppRouter;
	}
}

export function App({
	queryClient,
	router,
}: {
	queryClient: QueryClient;
	router: AppRouter;
}) {
	return (
		<StrictMode>
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router} />
			</QueryClientProvider>
		</StrictMode>
	);
}
