import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
	createRouter,
	type RouterHistory,
	RouterProvider,
} from "@tanstack/react-router";
import { StrictMode, useState } from "react";
import { theAppAnswered } from "@/answer";
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

export function App({ router }: { router: AppRouter }) {
	const [queryClient] = useState(
		() =>
			new QueryClient({
				defaultOptions: {
					queries: {
						// an error status from the App is its answer; only a request it did not answer is worth repeating
						retry: (failureCount, error) =>
							!theAppAnswered(error) && failureCount < 3,
					},
				},
			}),
	);
	return (
		<StrictMode>
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router} />
			</QueryClientProvider>
		</StrictMode>
	);
}
