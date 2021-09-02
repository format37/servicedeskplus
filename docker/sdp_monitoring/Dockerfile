FROM python:latest
WORKDIR /sdp_monitoring
#COPY requirements.txt /jira_issue_creator
#COPY users.txt /jira_issue_creator
#COPY monitoring.py /jira_issue_creator
#COPY GET_REQUESTS.xml /jira_issue_creator
COPY . /sdp_monitoring
RUN pip3 install -r requirements.txt --no-cache-dir
#COPY . /jira_issue_creator 
ENTRYPOINT ["python3"] 
CMD ["sdp_monitoring.py"]
