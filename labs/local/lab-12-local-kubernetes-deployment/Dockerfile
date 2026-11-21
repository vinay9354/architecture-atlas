# Lab 12 tracking stub: multi-stage build.
# Base image: the official Python image, slim variant on Debian trixie. The tag was checked on
# Docker Hub on 2026-11-21. For reproducible builds, also pin the digest
# (python:3.14.10-slim-trixie@sha256:...) after checking it with `docker buildx imagetools inspect`.

# Stage 1: a test gate. The image is only built if the source compiles and the self-test passes.
FROM python:3.14.10-slim-trixie AS build
WORKDIR /src
COPY app/ ./app/
RUN python -m py_compile app/tracking_stub.py app/probe.py \
 && python app/tracking_stub.py --self-test

# Stage 2: the runtime image. Only the two application files are copied from the build stage;
# nothing the build stage created (bytecode caches, test output) reaches the final image.
FROM python:3.14.10-slim-trixie AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=build /src/app/tracking_stub.py /src/app/probe.py /app/
# A numeric, unprivileged user, so Kubernetes can verify runAsNonRoot without a user database.
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "/app/tracking_stub.py"]
CMD ["--host", "0.0.0.0", "--port", "8080"]
