# OpenCog Devcontainer Dockerfile
# Provides a development environment where all OpenCog packages can be
# pre-built from the workspace sources via the build-opencog.sh script.
# Based on unified-build.yml: 44 packages across 6 dependency tiers.
# Critical path: cogutil -> atomspace -> unify -> ure -> pln -> python-attic

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install all system dependencies required by the 44 OpenCog packages.
# Sourced from the system_setup and per-package dep lists in unified-build.yml
# and single-job-build.yml.  Packages that may not exist in the Ubuntu 24.04
# archive are installed with `|| true` so the image build never fails.
RUN apt-get update && apt-get install -y \
    autoconf \
    autoconf-archive \
    automake \
    binutils-dev \
    cmake \
    cxxtest \
    cython3 \
    flex \
    guile-3.0-dev \
    libboost-all-dev \
    libiberty-dev \
    libgtk-3-dev \
    liboctomap-dev \
    libopencv-dev \
    libopenmpi-dev \
    libpqxx-dev \
    libprotobuf-dev \
    librocksdb-dev \
    libssl-dev \
    libtool \
    nlohmann-json3-dev \
    pkg-config \
    protobuf-compiler \
    python3-dev \
    python3-pip \
    python3-numpy \
    python3-scipy \
    swig \
    unixodbc-dev \
    uuid-dev \
    && apt-get install -y libgrpc++-dev protobuf-compiler-grpc || true \
    && apt-get install -y libopendht-dev || true \
    && apt-get install -y libipfs-http-client-dev || true \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Pre-configure the dynamic linker so OpenCog shared libraries installed
# under /usr/local/lib/opencog are found automatically.
RUN echo "/usr/local/lib/opencog" > /etc/ld.so.conf.d/opencog.conf \
    && ldconfig
