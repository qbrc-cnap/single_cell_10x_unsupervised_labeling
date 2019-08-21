From debian:stretch
LABEL maintainer="ddeconti@hsph.harvard.edu"
# Please note as of Docker version 2.1.0.0 on Mac OSX (Mojave)
# this docker file will fail to build due to a bug in Docker.

RUN apt-get update && \
  apt-get install -y \
    build-essential \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libxml2-dev

# Install all software into /opt/software:
RUN mkdir -p /opt/software/

# Requires manually downloading and placing the cellranger tar into
# this directory before building the Docker
# md5sum: a362d62530e9d6a653e5bad5b9c19aba
COPY cellranger-3.1.0.tar.gz /opt/software/cellranger-3.1.0.tar.gz
RUN tar xzf /opt/software/cellranger-3.1.0.tar.gz -C /opt/software/
RUN mv /opt/software/cellranger-3.1.0 /opt/software/cellranger
RUN rm /opt/software/cellranger-3.1.0.tar.gz