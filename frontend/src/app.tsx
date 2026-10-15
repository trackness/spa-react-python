import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
	createRouter,
	type RouterHistory,
	RouterProvider,
} from "@tanstack/react-router";
import { StrictMode, useState } from "react";
import { ResponseError } from "@/client/.kubb/client";
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
						// an error status is the App's answer; only a request that got none is worth repeating
						retry: (failureCount, error) =>
							!ResponseError.is(error) && failureCount < 3,
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
