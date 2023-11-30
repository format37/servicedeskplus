# -*- coding: utf-8 -*-
import sys
import json
import os
from jira import JIRA
import time
import html2text
import requests

def get_api_key():
    with open('api.key', 'r') as key_file:
        return key_file.read()

def get_jira_accounts_from_file(file_path='jira_members.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_jira_accounts_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return {}

def issue_assignee(jira, issue, accountId):
    url = jira._options['server'] + '/rest/api/latest/issue/' + issue + '/assignee'
    payload = {'accountId': accountId}
    return jira._session.put(url, data=json.dumps(payload))

def create_issue(project, summary, description, accountId, issuetype, item):
    if '-Сервис' in item:
        item = '1С-Сервис'
    issue_dict = {
        'project': project,
        'issuetype': issuetype,
        'components': [{'name': item}],
        'summary': summary,
        'description': html2text.html2text(description),
        'assignee': {
            'accountId': accountId,
            'name': accountId
        },
    }
    return jira.create_issue(fields=issue_dict)

def save_log(message):
    with open('log.txt', 'a') as log_file:
        log_file.write(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} {message}")

sdp_jira_issue_types = {
    'Изменение': 'Задача',
    'Информация': 'Консультация',
    'Инцидент': 'Баг',
    'Обслуживание': 'Обслуживание',
}

jira_options = {'server': 'http://jira.icecorp.ru'}
os.environ['no_proxy'] = '*'
jira = JIRA(options=jira_options, basic_auth=('ServiceDesk', get_api_key()))

try:
	sdp_jira_accounts = get_jira_accounts_from_url("https://gitlab.icecorp.ru/service/servicedeskplus/-/raw/master/settings/jira_members.json")
except Exception as e:
	print(e);
	sdp_jira_accounts = get_jira_accounts_from_file()

param = sys.argv[1]
file_name = param[param.rfind('/') + 1:]
json_path = 'request\\' + file_name

with open(json_path, encoding='utf-8') as json_file:
    json_data = json.load(json_file)
    request = json_data['request']

with open('log.json', 'w') as json_log:
    json.dump(json_data, json_log)

if request['TECHNICIAN'] in sdp_jira_accounts.keys():
    current_issue_type = sdp_jira_issue_types[request['REQUESTTYPE']]
    save_log(f"{request['WORKORDERID']} with {current_issue_type} for {request['TECHNICIAN']} send to jira")
    issue = create_issue(
        'HELP1C',
        f"{request['WORKORDERID']} {request['SUBJECT']}",
        request['DESCRIPTION'],
        sdp_jira_accounts[request['TECHNICIAN']],
        current_issue_type,
        request['ITEM']
    )
    issue.update({'customfield_10043': request['WORKORDERID']})
else:
    save_log(f"{request['TECHNICIAN']} is not in white list. {request['WORKORDERID']} stay only in sdp")
