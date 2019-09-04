From debian:stretch
LABEL maintainer="ddeconti@hsph.harvard.edu"
#hsphqbrc/singlecell_10_unsupervised_labeling

RUN apt-get update && \
  apt-get install -y build-essential \
    wget \
    zlib1g-dev \
    libcurl4-openssl-dev \
    libncurses-dev \
    libbz2-dev \
    liblzma-dev \
    libxml2-dev \
    zip \
    python3-dev \
    python3-pip \
    python2.7-dev \
    python-pip \
    default-jre \
    r-base \
    pandoc \
    git

# Install all software into /opt/software:
RUN mkdir -p /opt/software 

ADD convert_to_excel.py /opt/software
ADD generate_report.py /opt/software
ADD perform_precheck.py /opt/software
ADD plotting.py /opt/software

# Install libStatGen and fastQValidator:
RUN cd /opt/software && \
  git clone https://github.com/statgen/libStatGen.git && \
  cd libStatGen && \
  make && \
  cd .. && \
  git clone https://github.com/statgen/fastQValidator.git && \
  cd fastQValidator && \
  make && \
  make install

# Install some Python3 libraries:
ADD requirements.txt /opt/software/
ADD requirements27.txt /opt/software/
RUN pip3 install -r /opt/software/requirements.txt
RUN pip install -r /opt/software/requirements27.txt

# Install Jinja2 for templating.  Likely installed with other python packages, but just to be sure:
RUN pip3 install Jinja2

# Install scMatch
RUN git clone https://github.com/asrhou/scMatch.git /opt/software/scMatch
RUN git -C /opt/software/scMatch reset --hard bc116c867ec2d1e635245dbc975078d6b641012a
RUN echo "bc116c867ec2d1e635245dbc975078d6b641012a" > /opt/software/scMatch/git_commit_hash
RUN echo "https://github.com/asrhou/scMatch.git" > /opt/software/scMatch/git_repo_url


# Add the report template and styling to /opt/report
RUN mkdir -p /opt/report
ADD report.md /opt/report/
ADD report.css /opt/report/