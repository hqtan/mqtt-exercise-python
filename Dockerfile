FROM python:3.10.5-buster
WORKDIR /app
RUN python3 -m venv ./venv
ADD ./requirements.txt .
RUN ./venv/bin/pip install --disable-pip-version-check -r ./requirements.txt
ADD .env .
ADD *.py ./
