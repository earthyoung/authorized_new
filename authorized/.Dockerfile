FROM python:3.11

ENV PYTHONBUFFERED 1

RUN apt-get -y update && apt-get -y install vim && apt-get clean
RUN mkdir /project
ADD . /project

WORKDIR /project
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ['python', 'manage.py', 'runserver', '0.0.0.0:8000']

