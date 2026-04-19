FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "agent_connect_kit.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
