FROM ghcr.io/pnpm/pnpm:12.11.2 AS frontend
# Task's latest release, which runs any Taskfile of version: '3'; pipefail, so that a
# failed download stops the build here
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl --fail --silent --show-error --location https://taskfile.dev/install.sh | sh -s -- -d -b /usr/local/bin
WORKDIR /app
# the dependencies first, exactly as locked, so that a change to the Frontend's code reuses them
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/
RUN --mount=type=cache,target=/pnpm/store pnpm --dir frontend install --frozen-lockfile
COPY Taskfile.yml .
COPY frontend frontend
RUN task frontend:build

# a stage of its own, so that Dependabot, which reads only FROM lines, keeps uv updated
FROM ghcr.io/astral-sh/uv:0.13.1 AS uv

FROM python:3.14.8-slim-trixie AS backend
COPY --from=uv /uv /bin/
# the base image's own Python, so the environment still works once copied out of this stage
ENV UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app/backend
# the dependencies first, so that a change to the Backend's code reuses them
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    uv sync --locked --no-install-project
# the Backend's version comes from version.txt beside it
COPY version.txt /app/
COPY backend .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked
# uv compiles the dependencies only, and the App cannot write the bytecode of the Backend or
# its migrations as it runs
RUN python -m compileall -q src migrations

FROM python:3.14.8-slim-trixie
COPY --from=backend /app /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist
WORKDIR /app/backend
ENV APP_LISTEN_ADDRESS__HOST=0.0.0.0 \
    APP_LISTEN_ADDRESS__PORT=8000 \
    APP_DATABASE_FILE=/data/app.db \
    APP_FRONTEND_DIRECTORY=/app/frontend/dist
# writable by whichever user Docker runs the App as, which cannot create it in / itself
RUN mkdir --mode=1777 "$(dirname "$APP_DATABASE_FILE")"
EXPOSE 8000
COPY --chmod=0755 entrypoint.sh /usr/local/bin/entrypoint
ENTRYPOINT ["entrypoint"]
# readiness fails until migrations have run; the start period gives them time
HEALTHCHECK --start-period=1m \
    CMD ["python", "-c", "import http.client, os, sys; app = http.client.HTTPConnection(os.environ['APP_LISTEN_ADDRESS__HOST'], int(os.environ['APP_LISTEN_ADDRESS__PORT'])); app.request('GET', '/health/ready'); sys.exit(app.getresponse().status != 200)"]
CMD ["sh", "-c", "exec .venv/bin/uvicorn app.main:app --log-config logging.json --host \"$APP_LISTEN_ADDRESS__HOST\" --port \"$APP_LISTEN_ADDRESS__PORT\""]
