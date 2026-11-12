# syntax=docker/dockerfile:1
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS builder
WORKDIR /build
COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))" > requirements.txt \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY app/ ./app/
RUN pip install --no-cache-dir --prefix=/install --no-deps .

FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser \
 && mkdir /app && chown appuser:appuser /app
WORKDIR /app
COPY --from=builder /install /usr/local
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
