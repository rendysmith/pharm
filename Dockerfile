FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir --upgrade numpy pandas

COPY . .

CMD ["python", "main.py"]

