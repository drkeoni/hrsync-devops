#
# Makefile to simplify common tasks
#
SHELL:=/bin/bash -o pipefail
VE_DIR:=ve

PKG_NAME:=hrsync-mgmt

NOSE_OPTS:=--with-xunit --with-doctest --detailed-errors --xunit-file=tests/nosetests.xml

ACTIVATE:=${VE_DIR}/bin/activate

_:=$(shell mkdir -p logs)

help:
	@echo "  Type make setup to install ${PKG_NAME} into the virtualenv"

create-ve: FORCE
	[[ -d ${VE_DIR} ]] || ( \
	  echo "[INFO] Bootstrap installing virtualenv"	&& \
          python3 -m venv ${VE_DIR} && \
          . ${ACTIVATE} && \
	  pip install --upgrade pip && \
	  pip install wheel )

setup: logs/setup.log

logs/setup.log: etc/requirements.txt
	. ${ACTIVATE} && pip3 ${PIP_OPTS} install -r $(word 1,$^) 2>&1 | tee "$@.err"
	/bin/mv "$@.err" "$@"

test: FORCE
	( [[ -z "${DEPLOY_MODE}" ]] && echo "[ERROR] Missing DEPLOY_MODE, need to source environment first" ) || \
	  nosetests ${NOSE_OPTS}

cleanest: FORCE
	rm -rf ${VE_DIR}
	rm -f logs/*

rebuild-ve: cleanest create-ve logs/setup.log

.PHONY: FORCE help create-ve setup test cleanest rebuild-ve
