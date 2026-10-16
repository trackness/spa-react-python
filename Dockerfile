# syntax=docker/dockerfile:1

# The built Frontend is static files, so it is built once, on the build platform.
FROM --platform=$BUILDPLATFORM ghcr.io/pnpm/pnpm:12.11.2 AS frontend
ARG TASK_VERSION=v3.54.0
RUN sh -c "$(curl --fail --silent --show-error --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin "$TASK_VERSION"
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/
# pnpm installs the Node version the manifest's devEngines names
RUN --mount=type=cache,id=pnpm,target=/var/cache/pnpm \
    pnpm --dir frontend install --frozen-lockfile --store-dir /var/cache/pnpm
COPY Taskfile.yml ./
COPY frontend/ frontend/
RUN task frontend:build

FROM python:3.14.8-slim-trixie AS backend
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0
WORKDIR /app/backend
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    uv sync --locked --no-install-project
COPY version.txt /app/
COPY backend/ ./
# the App is installed in place: it reads pyproject.toml, its migrations and
# version.txt from beside its source
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# No Node and no uv: the App and the built Frontend only.
FROM python:3.14.8-slim-trixie
RUN install --directory --owner=nobody /data
COPY --from=backend /app /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist
WORKDIR /app/backend
ENV PATH=/app/backend/.venv/bin:$PATH \
    APP_LISTEN_ADDRESS__HOST=0.0.0.0 \
    APP_LISTEN_ADDRESS__PORT=8000 \
    APP_DATABASE_FILE=/data/app.db \
    APP_FRONTEND_DIRECTORY=/app/frontend/dist
USER nobody
EXPOSE 8000
VOLUME /data
# readiness fails until migrations have run; the start period gives them time
HEALTHCHECK --start-period=1m --start-interval=1s \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"APP_LISTEN_ADDRESS__PORT\"]}/health/ready')"]
CMD ["sh", "-c", "exec uvicorn app.main:app --log-config logging.json --host \"$APP_LISTEN_ADDRESS__HOST\" --port \"$APP_LISTEN_ADDRESS__PORT\""]
