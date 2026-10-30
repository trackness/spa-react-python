import { ResponseError } from "@/client/.kubb/client";
import type { Unavailable } from "@/client/types";

// what a gateway, such as Vite's proxy, answers when the App behind it did not
const GATEWAY_ERRORS = new Set([502, 503, 504]);

// whether a body is the App's own answer that it is not ready
export function isUnavailable(data: unknown): data is Unavailable {
	return (
		typeof data === "object" &&
		data !== null &&
		"status" in data &&
		data.status === "unavailable"
	);
}

// whether a failed request was answered by the App itself, not left unanswered or answered by a gateway
export function theAppAnswered(
	error: unknown,
): error is ResponseError<unknown, unknown, unknown> {
	return (
		ResponseError.is(error) &&
		(!GATEWAY_ERRORS.has(error.status) || isUnavailable(error.data))
	);
}
