FROM python:latest
WORKDIR /jira_issue_creator
COPY requirements.txt /jira_issue_creator
RUN apt-get update
RUN apt-get install nano
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /jira_issue_creator 
ENTRYPOINT ["python3","-W", "ignore"] 
CMD ["order_creator_daemon.py"]
