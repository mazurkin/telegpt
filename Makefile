# telegpt makefile
#
# https://swcarpentry.github.io/make-novice/reference.html
# https://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/
# https://www.gnu.org/software/make/manual/make.html
# https://www.gnu.org/software/make/manual/html_node/Special-Targets.html
# https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html

SHELL := /bin/bash
ROOT  := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

CONDA_ENV_NAME = telegpt

DOCKER_NAME=telegpt
DOCKER_VERSION=0.1

# -----------------------------------------------------------------------------
# notebook
# -----------------------------------------------------------------------------

.DEFAULT_GOAL = run

.PHONY: run
run:
	$(ROOT)/bin/telegpt.sh

# -----------------------------------------------------------------------------
# conda environment
# -----------------------------------------------------------------------------

.PHONY: env-init
env-init:
	@conda create --yes --name $(CONDA_ENV_NAME) python=3.10.12 conda-forge::poetry=1.8.3

.PHONY: env-create
env-create:
	@conda run --no-capture-output --live-stream --name $(CONDA_ENV_NAME) poetry install --no-root --no-directory

.PHONY: env-update
env-update:
	@conda run --no-capture-output --live-stream --name $(CONDA_ENV_NAME) poetry update

.PHONY: env-list
env-list:
	@conda run --no-capture-output --live-stream --name $(CONDA_ENV_NAME) poetry show

.PHONY: env-remove
env-remove:
	@conda env remove --yes --name $(CONDA_ENV_NAME)

.PHONY: env-shell
env-shell:
	@conda run --no-capture-output --live-stream --name $(CONDA_ENV_NAME) bash

.PHONY: env-info
env-info:
	@conda run --no-capture-output --live-stream --name $(CONDA_ENV_NAME) conda info

# -----------------------------------------------------------------------------
# linters
# -----------------------------------------------------------------------------

.PHONY: shellcheck
shellcheck:
	@shellcheck --norc --shell=bash bin/*

.PHONY: lint-flake8
lint-flake8:
	@conda run --no-capture-output --live-stream --name $(CONDA_ENV_NAME) \
		flake8 src

.PHONY: lint
lint: shellcheck lint-flake8

# -----------------------------------------------------------------------------
# docker image
# -----------------------------------------------------------------------------

.PHONY: docker-prune
docker-prune:
	@docker image prune --force

.PHONY: docker-build
docker-build: lint
	@docker build --progress=plain -t ${DOCKER_NAME}:${DOCKER_VERSION} .

.PHONY: docker-run
docker-run:
	@docker run \
		--name "telegpt" \
		--hostname="telegpt" \
		--rm \
		--read-only \
		--interactive \
		--tty \
		--network host \
		--env TELEGPT_APP_ID \
		--env TELEGPT_APP_HASH \
		--env TELEGPT_PHONE \
		--env TELEGPT_CHAT \
		--env TZ=US/Eastern \
		--volume "$(ROOT)/session:/opt/telegpt/session:rw" \
		${DOCKER_NAME}:${DOCKER_VERSION}

.PHONY: docker-shell
docker-shell:
	@docker run \
		--name "telegpt" \
		--hostname="telegpt" \
		--rm \
		--read-only \
		--interactive \
		--tty \
		--network host \
		--env TELEGPT_APP_ID \
		--env TELEGPT_APP_HASH \
		--env TELEGPT_PHONE \
		--env TELEGPT_CHAT \
		--env TZ=US/Eastern \
		--volume "$(ROOT)/session:/opt/telegpt/session:rw" \
		--entrypoint /bin/bash \
		${DOCKER_NAME}:${DOCKER_VERSION}
