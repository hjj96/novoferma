# Package only linked public files into the runtime image.
FROM python:3.12-slim AS packager
WORKDIR /app
COPY scripts/package_site.py ./scripts/package_site.py
COPY output/concept ./output/concept
RUN python scripts/package_site.py

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 NOVOFERMA_DB=/data/private/requests.sqlite3
COPY scripts/serve_site.py ./scripts/serve_site.py
COPY --from=packager /app/output/novoferma-site.zip /tmp/site.zip
RUN python -m zipfile -e /tmp/site.zip /tmp/site \
    && mkdir -p /app/output /data/private \
    && mv /tmp/site/novoferma-site /app/output/concept \
    && rm -rf /tmp/site /tmp/site.zip \
    && useradd --system --uid 10001 --no-create-home novoferma \
    && chown -R 10001:10001 /data/private \
    && chmod 700 /data/private
USER 10001:10001
EXPOSE 8080
VOLUME ["/data"]
CMD ["python", "scripts/serve_site.py", "serve", "--host", "0.0.0.0", "--port", "8080", "--rate-limit", "240"]
