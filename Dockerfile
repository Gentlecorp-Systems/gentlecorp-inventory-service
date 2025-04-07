# syntax=docker/dockerfile:1.14.0

# Copyright (C) 2023 - present, Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# Aufruf:   docker build --tag juergenzimmermann/patient:2025.4.1-bookworm .
#           ggf. --no-cache
#           Get-Content Dockerfile | docker run --rm --interactive hadolint/hadolint:2.12.1-beta-debian
#           docker save juergenzimmermann/patient:2025.4.1-bookworm > patient.tar

# https://docs.docker.com/engine/reference/builder/#syntax
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md
# https://hub.docker.com/r/docker/dockerfile
# https://docs.docker.com/build/building/multi-stage
# https://testdriven.io/blog/docker-best-practices
# https://containers.gitbook.io/build-containers-the-hard-way
# https://wiki.debian.org/DebianReleases
# https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# https://www.saaspegasus.com/guides/uv-deep-dive

# ARG: "build-time" Variable
# ENV: "build-time" und "runtime" Variable
ARG PYTHON_MAIN_VERSION=3.13
ARG PYTHON_VERSION=${PYTHON_MAIN_VERSION}.2
ARG UV_VERSION=0.6.9

# ------------------------------------------------------------------------------
# S t a g e   b u i l d e r
# ------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_MAIN_VERSION}-bookworm-slim AS builder

# Install the project into `/opt/app`
WORKDIR /opt/app

# Enable bytecode compilation
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Kein Python-Download, falls eine "managed" Python-Version verwendet wird,
# sondern in beiden Images denselben Python-Interpreter verwenden
ENV UV_PYTHON_DOWNLOADS=0

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml <<EOF \
    uv venv
    uv sync --frozen --no-install-project --no-dev --no-editable
EOF

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /opt/app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable
# ENTRYPOINT ["/bin/bash", "-c", "echo 'Container als bash gestartet.' && sleep infinity"]

# ------------------------------------------------------------------------------
# S t a g e   f i n a l
# ------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS final

# Anzeige bei "docker inspect ..."
# https://specs.opencontainers.org/image-spec/annotations
# https://spdx.org/licenses
# MAINTAINER ist deprecated https://docs.docker.com/engine/reference/builder/#maintainer-deprecated
LABEL org.opencontainers.image.title="patient" \
    org.opencontainers.image.description="Appserver patient mit Basis-Image Bookworm" \
    org.opencontainers.image.version="2025.4.1-bookworm" \
    org.opencontainers.image.licenses="GPL-3.0-or-later" \
    org.opencontainers.image.authors="Juergen.Zimmermann@h-ka.de"

# "working directory" fuer die Docker-Kommandos RUN, ENTRYPOINT, CMD, COPY und ADD
WORKDIR /opt/app

# https://unix.stackexchange.com/questions/217369/clear-apt-get-list
# https://medium.com/vantageai/how-to-make-your-python-docker-images-secure-fast-small-b3a6870373a0
RUN <<EOF
set -eux
# https://manpages.debian.org/bookworm/passwd/groupadd.html
# https://manpages.debian.org/bookworm/adduser/addgroup.html
groupadd --gid 10000 app
# https://manpages.debian.org/bookworm/passwd/useradd.html
# https://manpages.debian.org/bookworm/adduser/adduser.html
useradd --uid 10000 --gid app --shell /bin/bash --no-create-home app
# User "app" als Owner fuer das working directory
chown -R app:app /opt/app
EOF

# User "app" statt User "root"
USER app

COPY --from=builder --chown=app:app /opt/app ./

# Place executables in the environment at the front of the path
ENV PATH="/opt/app/.venv/bin:$PATH"

EXPOSE 8000

STOPSIGNAL SIGINT

# bash, dash (= Debian Almquist Shell), sh -> dash
CMD ["sh", "-c", "python -m patient"]

#CMD ["/bin/bash", "-c", "echo 'Container als bash gestartet.' && sleep infinity"]
#CMD ["sh", "-c", "echo $PATH"]
#CMD ["sh", "-c", "ls -al /opt/app/"]
#CMD ["sh", "-c", "ls -al /opt/app/.venv/bin"]
#CMD ["sh", "-c", "ls -al /usr/bin/*sh"]
#CMD ["sh", "-c", "ls -al /opt/app/src/patient/config/resources/db/postgresql/certificate.crt"]
#CMD ["sh", "-c", "more /opt/app/src/patient/config/resources/patient.toml"]
