import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { isUnavailable, theAppAnswered } from "@/answer";
import { readinessQueryOptions } from "@/client/hooks";

export const Route = createFileRoute("/")({ component: HomePage });

function HomePage() {
	const readiness = useQuery(readinessQueryOptions());

	function message(): string {
		if (readiness.isPending) {
			return "Checking whether the App is ready…";
		}
		if (!readiness.isError) {
			return "The App is ready.";
		}
		if (!theAppAnswered(readiness.error)) {
			return "The App did not answer.";
		}
		return isUnavailable(readiness.error.data)
			? `The App is not ready: ${readiness.error.data.status}.`
			: `The App is not ready: it answered with status ${readiness.error.status}.`;
	}

	// one live region whose text changes, so that screen readers announce what the page finds
	return <p role="status">{message()}</p>;
}
