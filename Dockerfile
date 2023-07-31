FROM python:slim-buster
RUN apt-get update && apt-get install -y \
    git \
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY python-image-organiser/ /home/python-image-organiser/
ENTRYPOINT [ "python", "/home/python-image-organiser/processor.py" ]
