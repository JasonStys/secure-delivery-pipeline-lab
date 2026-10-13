# Jason Stys: dependency-free probe image; no credentials or development tools.
# Python 3.14.6-slim OCI index digest reviewed 2026-10-13; fixed non-root UID.
FROM python:3.14.6-slim@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144
WORKDIR /app
COPY delivery/__init__.py delivery/io.py delivery/probe.py /app/delivery/
COPY delivery/probe.py /app/__main__.py
COPY LICENSE /app/LICENSE
RUN python -m zipapp /app --output /opt/release-probe.pyz
COPY --chown=10001:10001 examples/inventory.json /app/inventory.json
USER 10001:10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
HEALTHCHECK NONE
ENTRYPOINT ["python", "-I", "/opt/release-probe.pyz"]
CMD ["--input", "/app/inventory.json"]
