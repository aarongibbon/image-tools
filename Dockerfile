FROM python:slim-buster
ENV REPO https://github.com/aarongibbon/image-tools.git
ENV REPO_TAG latest
RUN apt-get update && apt-get install -y \
    git
RUN git clone -b $REPO_TAG $REPO /home/code
RUN pip install -r /home/code/requirements.txt
ENTRYPOINT [ "python", "/home/code/python-image-organiser/processor.py"]
