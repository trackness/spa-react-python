import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { readinessHealthReadyGetQueryOptions } from "@/client/hooks";

export const Route = createFileRoute("/")({ component: HomePage });

function HomePage() {
	const readiness = useQuery(readinessHealthReadyGetQueryOptions());

	if (readiness.isPending) {
		return <p>Checking whether the App is ready…</p>;
	}
	if (readiness.isError) {
		return <p>{`The App is not ready: ${readiness.error.message}`}</p>;
	}
	return <p>The App is ready.</p>;
}
