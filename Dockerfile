FROM ubuntu:18.04
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv gcc python3-dev \
  && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/usr/local/dawa-updater/
ENV DEBIAN_FRONTEND=noninteractive
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR "/usr/local/dawa-updater"
ENV PYTHONPATH=".:$PYTHONPATH"

ENV DATABASE_HOST 'localhost'
ENV DATABASE_NAME 'sammy'
ENV DATABASE_USER 'sammy'
ENV DATABASE_PASSWORD 'sammy'

ENV LANG en_US.UTF-8

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /usr/local/dawa-updater/
RUN . /usr/local/dawa-updater/bin/activate
ENTRYPOINT ["python3", "dawaupdater.py"]
