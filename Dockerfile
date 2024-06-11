FROM python:3.10

RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN mkdir /app/

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app/
WORKDIR /app/

ENV PRJPATH /app/

RUN chmod +x update_cont.sh

# Запуск основного файла
CMD ["python", "-um", "main"]
