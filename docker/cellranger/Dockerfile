From debian:stretch
LABEL maintainer="ddeconti@hsph.harvard.edu"

RUN apt-get update && \
  apt-get install -y build-essential \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libxml2-dev

# Install all software into /opt/software:
RUN mkdir -p /opt/software/cellranger

COPY cellranger-3.1.0.tar.gz /opt/software/cellranger-3.1.0.tar.gz
#RUN tar xzf /opt/software/cellranger-3.1.0.tar.gz -C /opt/software/cellranger
