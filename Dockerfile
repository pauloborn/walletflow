FROM apache/airflow:latest

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim libpq-dev python3-dev gcc \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow
COPY walletflow/requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/entrypoint"]
CMD []

RUN pip uninstall -y argparse
