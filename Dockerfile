FROM python:3.8

ENV INSTALLDIR /opt/golos-witness-tools

COPY pyproject.toml poetry.lock $INSTALLDIR/

WORKDIR $INSTALLDIR

ENV CONFD_VERSION 0.13.0
ADD https://github.com/kelseyhightower/confd/releases/download/v$CONFD_VERSION/confd-$CONFD_VERSION-linux-amd64 /usr/local/bin/confd
RUN chmod +x /usr/local/bin/confd

RUN set -xe ;\
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python ;\
    . $HOME/.poetry/env ;\
    poetry export -f requirements.txt > requirements.txt ;\
    pip install -r requirements.txt

COPY docker/docker-entrypoint.sh /usr/local/bin
COPY docker/confd/templates/* /etc/confd/templates/
COPY docker/confd/toml/* /etc/confd/conf.d/
COPY *.py $INSTALLDIR/


ENTRYPOINT ["docker-entrypoint.sh"]
