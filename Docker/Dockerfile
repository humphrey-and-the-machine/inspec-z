FROM python:3.9-buster

WORKDIR /app

COPY Docker/pipRequirements.txt requirements.txt
COPY Docker/dockerInspecz.py inspecz.py

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "inspecz.py", "/mnt/config.yaml"]
