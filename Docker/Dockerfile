FROM python:3.9-slim-buster

RUN apt-get update \
 && apt-get install -y \
      python3-tk \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Docker/pipRequirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .
COPY Docker/docker_inspecz.py inspecz.py

CMD [ "python3", "inspecz.py", "/mnt/config.yaml"]
