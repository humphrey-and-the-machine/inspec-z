FROM python:3.9-buster

WORKDIR /app

COPY pipRequirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "inspecz.py", "/mnt/config.yaml"]
