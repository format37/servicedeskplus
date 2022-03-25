## -*- coding: utf-8 -*-

#import pip
#pip.main(['install', '--proxy=user:password@proxy:port', 'packagename'])
#pip.main(['install', '--proxy=http://10.0.4.222:3128', 'html2text'])

import sys
from jira import JIRA
import json
from jira.utils import json_loads
import urllib
import requests
import time
import html2text

def get_api_key():
	with open('api.key','r') as key_file:
		return key_file.read()
		
def issue_assignee(jira,issue,accountId):
	url = jira._options['server'] + '/rest/api/latest/issue/' + issue + '/assignee'
	payload = {'accountId': accountId}
	return jira._session.put(url, data=json.dumps(payload))
	
def create_issue(project,summary,description,accountId,issuetype,item):
	if '-Сервис' in item:
		item='1С-Сервис'
	
	issue_dict={
		'project': project,
		'issuetype': issuetype,
		#'components': [{'name': urllib.parse.quote_plus(item)}],
		#'components': [{'name': item.encode("cp1251")}],
		'components': [{'name': item}],
		'summary': summary,
		'description': html2text.html2text(description),
		#'assignee': {'accountId': accountId} # v3
		'assignee': { # v2
            'accountId': accountId,
            'name': accountId
        },
	}
	return jira.create_issue(fields=issue_dict)

def save_log(message):
	with open('log.txt','a') as log_file:
		log_file.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S')+' '+message)
		log_file.close()
	
#icebergproject.atlassian.net/jira/people/search
#select an account and copypaste id from adress after people/
sdp_jira_accounts={	
	'Сотников Артём Игоревич':'a.sotnikov@iceberg.ru',
	'Бывальцев Виктор Валентинович':'v.byvaltsev@iceberg.ru',
	'Титов Иван Сергеевич':'i.titov@iceberg.ru',
	'Юрасов Алексей Александрович':'yurasov@iceberg.ru',
	'Севрюкова Анна Юрьевна':'a.sevrjukova@iceberg.ru',
	'Песоцкий Константин Вячеславович':'k.pesotskii@iceberg.ru',
	}
	
sdp_jira_issue_types={
    'Изменение':'Задача',
    'Информация':'Консультация',
    'Инцидент':'Баг',
    'Обслуживание':'Обслуживание',
}
	
#jira_options = {'server': 'https://icebergproject.atlassian.net'}
jira_options = {'server': 'http://10.2.4.14'}
jira = JIRA(options=jira_options, basic_auth=('ServiceDesk', get_api_key()))

param=sys.argv[1]
file_name=param[param.rfind('/')+1:]
json_path='request\\'+file_name
with open(json_path, encoding='utf-8') as json_file:
#with open(json_path, encoding='cp1251') as json_file:
	json_text	= json_file.read()
	json_data=json.loads(json_text)
	request=json_data['request']
	
with open('log.json','w') as json_log:
	json_log.write(json_text)

#issue=jira.issue('PRJ1C-324')
#issue.update({'Epic_link':'PRJ1C-5'})

if request['TECHNICIAN'] in sdp_jira_accounts.keys():
	current_issue_type = sdp_jira_issue_types[request['REQUESTTYPE']]
	save_log(request['WORKORDERID']+' with '+current_issue_type+' for '+request['TECHNICIAN']+' send to jira')
	issue=create_issue(
		'HELP1C',
		request['WORKORDERID']+' '+request['SUBJECT'],
		request['DESCRIPTION'],
		sdp_jira_accounts[request['TECHNICIAN']],
		current_issue_type,
		request['ITEM']
		)
	issue.update({'customfield_10043':request['WORKORDERID']})
	#comment = jira.add_comment(str(issue), 'Created automatically from Service Desk Plus')
else:
	save_log(request['TECHNICIAN']+' is not in white list. '+request['WORKORDERID']+' stay only in sdp')