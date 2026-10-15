import { QueryClient } from "@tanstack/react-query";
import { createRoot } from "react-dom/client";
import { App, createAppRouter } from "@/app";

// biome-ignore lint/style/noNonNullAssertion: index.html always holds the root element
createRoot(document.getElementById("root")!).render(
	<App queryClient={new QueryClient()} router={createAppRouter()} />,
);
