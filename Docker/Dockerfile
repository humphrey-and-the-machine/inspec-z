FROM python:3.9-buster

WORKDIR /app

COPY Docker/pipRequirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .
COPY Docker/docker_inspecz.py inspecz.py

CMD [ "python3", "inspecz.py", "/mnt/config.yaml"]
