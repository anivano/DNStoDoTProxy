FROM python:2.7
RUN apt-get update -y
RUN apt-get install dnsutils vim -y
RUN apt-get install openssl
WORKDIR /usr/local/bin
COPY proxy.py .
CMD ["python","proxy.py"]
