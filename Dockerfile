FROM python:3

ENV INSTALLDIR /opt/golos-witness-tools

COPY Pipfile* *.py $INSTALLDIR/
COPY docker/docker-entrypoint.sh /usr/local/bin

COPY docker/confd/templates/* /etc/confd/templates/
COPY docker/confd/toml/* /etc/confd/conf.d/

WORKDIR $INSTALLDIR

RUN set -xe ;\
    pip install pipenv ;\
    pipenv install --system --deploy

ENV CONFD_VERSION 0.13.0
ADD https://github.com/kelseyhightower/confd/releases/download/v$CONFD_VERSION/confd-$CONFD_VERSION-linux-amd64 /usr/local/bin/confd
RUN chmod +x /usr/local/bin/confd

ENTRYPOINT ["docker-entrypoint.sh"]
