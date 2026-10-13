# Jason Stys: dependency-free probe image; no credentials or development tools.
# Python 3.14.6-alpine OCI index digest reviewed 2026-10-13; fixed non-root UID.
FROM python:3.14.6-alpine@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92
WORKDIR /app
COPY delivery/__init__.py delivery/io.py delivery/probe.py /app/delivery/
COPY delivery/probe.py /app/__main__.py
COPY LICENSE /app/LICENSE
RUN apk upgrade --no-cache \
    && python -m pip uninstall --yes pip \
    && python -m zipapp /app --output /opt/release-probe.pyz
COPY --chown=10001:10001 examples/inventory.json /app/inventory.json
USER 10001:10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
HEALTHCHECK NONE
ENTRYPOINT ["python", "-I", "/opt/release-probe.pyz"]
CMD ["--input", "/app/inventory.json"]
