FROM python:3.12.2

WORKDIR /app

COPY requirements.txt requirements.txt
COPY ventas.csv ventas.csv
COPY main.py main.py

RUN apt-get update && apt-get install -y \
    && pip install -r requirements.txt

RUN useradd -m app && echo "app ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER app

ENTRYPOINT ["python", "main.py"]
# 