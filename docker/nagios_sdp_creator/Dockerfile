FROM python:latest
WORKDIR /nagios_sdp_creator
COPY requirements.txt /nagios_sdp_creator
RUN apt-get update
RUN apt-get install nano
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /nagios_sdp_creator 
EXPOSE 8080
ENTRYPOINT ["python3"] 
CMD ["nagios_sdp_creator.py"]
