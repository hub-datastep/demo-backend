FROM ubuntu:latest
LABEL authors="bleschunov"
WORKDIR app

RUN apt-get update && apt-get install -y python3 pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements. txt

COPY . .

RUN cd src
CMD ["python3", "src/app. py"]