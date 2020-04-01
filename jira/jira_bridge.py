import sys
from jira import JIRA
import json
from jira.utils import json_loads


def get_api_key():
	with open('api.key','r') as key_file:
		return key_file.read()

		
def issue_assignee(jira,issue,accountId):
	url = jira._options['server'] + '/rest/api/latest/issue/' + issue + '/assignee'
	payload = {'accountId': accountId}
	return jira._session.put(url, data=json.dumps(payload))

	
def create_issue(project,summary,description,accountId,issuetype):
	issue_dict={
		'project': project,
		'issuetype': issuetype,
		'components': [{'name': 'Jira'}],
		'summary': summary,
		'description': description,
		'assignee': {'accountId': accountId}
	}
	return jira.create_issue(fields=issue_dict)

#icebergproject.atlassian.net/jira/people/search
#select an account and copypaste id from adress after people/
sdp_jira_accounts={	
	'Сотников Артём Игоревич':'5de505aa22389c0d118c3eaf',
	'Семенов Олег Владимирович':'5dfb26b2588f6e0cb033698e',
	'Полухин Владимир Геннадьевич':'5dfb273f9422830cacaa5c02',
	'Бывальцев Виктор Валентинович':'5dfb26b35697460cb3d98780',
	'Васильченко Евгения Алексеевна':'5dfb2741eaf5880cad03b10f',
	'Фролов Максим Евгеньевич':'557058:fa79f484-a387-495b-9862-1af505d8d70a',
	'Юрасов Алексей Александрович':'557058:f0548e8f-6a09-44bd-bfb5-43a0a40531bb',
	}
	
sdp_jira_issue_types={
	'Изменение':'Task',
	'Информация':'Consultation',
	'Инцидент':'Bug',
	'Обслуживание':'Service',
}
	
jira_options = {'server': 'https://icebergproject.atlassian.net'}
jira = JIRA(options=jira_options, basic_auth=('yurasov@iceberg.ru', get_api_key()))

param=sys.argv[1]
file_name=param[param.rfind('/')+1:]
json_path='request\\'+file_name
with open(json_path, encoding='utf-8') as json_file:
	json_data=json.loads(json_file.read())
	request=json_data['request']

#issue=jira.issue('PRJ1C-324')
#issue.update({'Epic_link':'PRJ1C-5'})

if request['TECHNICIAN'] in sdp_jira_accounts.keys():	
	issue=create_issue(
		'HELP1C',
		request['WORKORDERID']+' '+request['SUBJECT'],
		request['DESCRIPTION'],
		sdp_jira_accounts[request['TECHNICIAN']],
		sdp_jira_issue_types[request['REQUESTTYPE']],
		)
	issue.update({'customfield_10043':request['WORKORDERID']})
	#comment = jira.add_comment(str(issue), 'Created automatically from Service Desk Plus')