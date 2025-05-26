FROM python:3.11-alpine

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src /src

# EXPOSE 5000

CMD ["python", "/src/app.py"]