# task tiger worker

# todo fix copypaste with other dockerfiles in this project
FROM python:3

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]
CMD [ "bin/ttworker.py" ]