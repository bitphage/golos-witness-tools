FROM python:3

ENV INSTALLDIR /opt/golos-witness-tools

COPY requirements.txt *.py $INSTALLDIR/
COPY docker/docker-entrypoint.sh /usr/local/bin

COPY docker/confd/templates/* /etc/confd/templates/
COPY docker/confd/toml/* /etc/confd/conf.d/

RUN set -xe ;\
    pip install --no-cache-dir -r $INSTALLDIR/requirements.txt ;\
    # FIXME: temp hack around pycrypto
    pip uninstall -y pycrypto pycryptodome ;\
    pip install pycryptodome

ENV CONFD_VERSION 0.13.0
ADD https://github.com/kelseyhightower/confd/releases/download/v$CONFD_VERSION/confd-$CONFD_VERSION-linux-amd64 /usr/local/bin/confd
RUN chmod +x /usr/local/bin/confd

WORKDIR $INSTALLDIR
ENTRYPOINT ["docker-entrypoint.sh"]
