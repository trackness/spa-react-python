import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { ResponseError } from "@/client/.kubb/client";
import { readinessQueryOptions } from "@/client/hooks";

export const Route = createFileRoute("/")({ component: HomePage });

function HomePage() {
	const readiness = useQuery(readinessQueryOptions());

	if (readiness.isPending) {
		return <p>Checking whether the App is ready…</p>;
	}
	if (readiness.isError) {
		// a request that never got an answer rejects with something other than a ResponseError
		return ResponseError.is(readiness.error) ? (
			<p>{`The App is not ready: ${readiness.error.data.status}.`}</p>
		) : (
			<p>The App did not answer.</p>
		);
	}
	return <p>The App is ready.</p>;
}
