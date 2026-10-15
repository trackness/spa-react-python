import tomllib

from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from prometheus_client import CollectorRegistry
from pythonjsonlogger.core import RESERVED_ATTRS
from pythonjsonlogger.json import JsonFormatter

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
# adding a reader at runtime resets its totals, so the reader is fixed here
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
