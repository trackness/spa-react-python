import tomllib

from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from prometheus_client import CollectorRegistry, make_asgi_app
from pythonjsonlogger.core import RESERVED_ATTRS
from pythonjsonlogger.json import JsonFormatter
from starlette.types import Receive, Scope, Send

from app import BACKEND

resource = Resource.create(
    {
        SERVICE_NAME: tomllib.loads((BACKEND / "pyproject.toml").read_text())[
            "project"
        ]["name"],
        SERVICE_VERSION: (BACKEND.parent / "version.txt").read_text().strip(),
    }
)
tracer_provider = TracerProvider(sampler=ALWAYS_ON, resource=resource)
# its own registry leaves out prometheus_client's default collectors; the reader
# cannot name its metrics in advance, so a scrape narrowed by name still asks it
metrics_registry = CollectorRegistry(support_collectors_without_names=True)
# a reader added later starts empty and misses everything measured before it
meter_provider = MeterProvider(
    metric_readers=[
        PrometheusMetricReader(
            resource_attribute_filter=lambda key: (
                key in {SERVICE_NAME, SERVICE_VERSION}
            ),
            registry=metrics_registry,
        )
    ],
    resource=resource,
)


class PrometheusEndpoint:
    """prometheus_client's own endpoint, routed at exactly /metrics.

    A mount would redirect /metrics with a 307, and a route treats a function as a
    request handler, so the library's ASGI app is routed through this callable object.
    """

    def __init__(self, registry: CollectorRegistry) -> None:
        self.app = make_asgi_app(registry)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)


metrics_endpoint = PrometheusEndpoint(metrics_registry)
LoggingInstrumentor().instrument(
    tracer_provider=tracer_provider,
    inject_trace_context=True,
    enable_log_auto_instrumentation=False,
)


def json_formatter() -> JsonFormatter:
    return JsonFormatter(
        ["levelname", "name", "message"],
        timestamp=True,
        rename_fields={
            "otelTraceID": "trace_id",
            "otelSpanID": "span_id",
            "otelTraceSampled": "trace_sampled",
            "otelServiceName": SERVICE_NAME,
        },
        static_fields={SERVICE_VERSION: resource.attributes[SERVICE_VERSION]},
        # uvicorn repeats each message with terminal colour codes
        reserved_attrs=[*RESERVED_ATTRS, "color_message"],
    )
