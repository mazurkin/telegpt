FROM rockylinux:8.9
USER root

# linux packages, folders and the user
RUN yum install -y wget logrotate time bind-utils make nano \
 && yum clean all \
 && rm -rf /var/cache/yum \
 && groupadd --gid 1000 conda \
 && useradd --uid 1000 --gid 1000 conda

# conda
ARG CONDA_VERSION=py310_24.11.1-0
RUN mkdir -p '/opt/miniconda' \
 && wget -qc -O '/tmp/miniconda.sh' "https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh" \
 && bash "/tmp/miniconda.sh" -b -f -p /opt/miniconda \
 && rm "/tmp/miniconda.sh"
ENV PATH="/opt/miniconda/bin:${PATH}"

# conda environment
RUN conda create --yes --name telegpt python=3.10.12 conda-forge::poetry=1.8.3

# copy poetry environment
COPY poetry.lock poetry.toml pyproject.toml /tmp/environment/poetry/

# install poetry environment
RUN cd /tmp/environment/poetry/ \
 && conda run --no-capture-output --live-stream --name telegpt poetry install --no-root

# mutable volumes (the rest of the filesystem is considered as immutable)
VOLUME ["/home/conda"]
VOLUME ["/tmp"]

# python environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# files
COPY bin    /opt/telegpt/bin
COPY src    /opt/telegpt/src
COPY prompt /opt/telegpt/prompt

# for some reason the base container doesn't set `${USER}` variable, and `source ...` fails in BASH
ENV USER="conda"

# run the application
USER conda
WORKDIR /home/conda
ENTRYPOINT ["/opt/telegpt/bin/telegpt.sh"]
CMD []
