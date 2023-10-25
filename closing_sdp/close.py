#!/usr/bin/env python
from jira import JIRA
import urllib
import urllib.parse
import requests
import datetime
from time import strftime
from time import gmtime
import os
import socket

def get_jira_accounts_from_file(file_path='jira_members.json'):
	with open(file_path, 'r') as f:
		return json.load(f)

def get_jira_accounts_from_url(url):
	# try:
	response = requests.get(url)
	response.raise_for_status()  # Raise an exception for HTTP errors
	return response.json()
	# except requests.RequestException as e:
	print(f"An error occurred while fetching data: {e}")
	return {}

def find_key_by_value(dictionary, value_to_find, default = None):
	"""
	Find the key corresponding to a given value in a dictionary.

	Parameters:
		dictionary (dict): The dictionary to search in.
		value_to_find: The value for which to find the corresponding key.

	Returns:
		The key corresponding to the value if found, otherwise None.
	"""
	for key, value in dictionary.items():
		if value == value_to_find:
			return key
	
	print('technician not found 1:', value_to_find)
	# send_to_telegram(str(datetime.datetime.now())+' technician not found 1:'+str(user) )

	return default

def sdp_bid_close(request):
	response = ''
	add_worklog_file='ADD_WORKLOG.xml'
	edit_request_file='EDIT_REQUEST.xml'

	# try:
	print('\n======= sdp close by jira:',datetime.datetime.now())
	#print(request.rel_url.query)
	WORKORDERID = request['sdp_id']
	jira_type		= request['jira_type']
	SUBJECT		= request['subject']
	#description	= 'test'
	description	= request['description']
	#RESOLUTION	= "Закрыто\n"+request.rel_url.query['resolution']
	RESOLUTION	= "Закрыто\n"
	ITEM	= request['component']
	user = request['user']
	jira_issue = request['issue_key']	

	token	= os.environ.get('SDP_USER_TOKEN', '')
	workHours	= '0'
	workMinutes = '1'	
	

	print('item received:',ITEM)

	items =[
		'1C-Сервис',
		'МРМ',
		'Бухгалтерия',
		'МПК',
		'Склады',
		'Реклама',
	]
	if (ITEM in items)==False:
		ITEM = '1C-Сервис'
		print('item changed')

	print('item set:',ITEM)

	sub_cats = {
		'1C-Сервис':'1С Cистемы',
		'МРМ':'Мобильные приложения',
		'МПК':'Мобильные приложения',
		'Бухгалтерия':'1С Cистемы',
		'Склады':'1С Cистемы',
		'Реклама':'1С Cистемы',
	}

	"""if ITEM in sub_cats.keys():
		SUBCAT	= sub_cats[ITEM]		"""

	print('jira_type',jira_type)

	"""jira_sdp_types = {
		'Task':'Изменение',
		'Consultation':'Информация',
		'Bug':'Инцидент',
		'Service':'Обслуживание',
		}"""

	jira_sdp_types={
		'Task':'Задача',
		'Consultation':'Консультация',
		'Bug':'Баг',
		'Service':'Обслуживание',
	}

	if jira_type in jira_sdp_types.keys():
		rtype = jira_sdp_types[jira_type]
	else:
		rtype = jira_sdp_types['Consultation']

	# print('Subcategory',SUBCAT)
	print('sdp_id',WORKORDERID)
	print('jira issue',jira_issue)
	print('subject',SUBJECT)
	print('description',description)

	# try:
	sdp_jira_accounts = get_jira_accounts_from_url("https://gitlab.icecorp.ru/service/servicedeskplus/-/raw/master/settings/jira_members.json")
	token = '76ED27EB-D26D-412A-8151-5A65A16198E7'
	# Adding worklog
	spent_hours = 0
	spent_minutes = 5

	worklog_comments = 'Консультация'
	technician = 'Юрасов Алексей Александрович'
	SUBCAT = '1С Cистемы'
	
	with open(add_worklog_file,'rb') as fh:
		INPUT_DATA_ORIGINAL	= fh.read().decode("utf-8")

	INPUT_DATA = INPUT_DATA_ORIGINAL
	INPUT_DATA = INPUT_DATA.replace("%technician%", technician)
	INPUT_DATA = INPUT_DATA.replace("%workMinutes%", str(spent_minutes))
	INPUT_DATA = INPUT_DATA.replace("%workHours%", str(spent_hours))
	url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'/worklogs?OPERATION_NAME=ADD_WORKLOG&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
	print('worklog url',url)
	headers = {'Content-Type': 'application/xml'}
	response += requests.post(url, headers=headers).text		

	with open(edit_request_file,'rb') as fh:
		INPUT_DATA	= fh.read().decode("utf-8")
		INPUT_DATA = INPUT_DATA.replace("%rtype%", rtype)
		INPUT_DATA = INPUT_DATA.replace("%Description%", description) #
		INPUT_DATA = INPUT_DATA.replace("%Subject%", SUBJECT)
		INPUT_DATA = INPUT_DATA.replace("%Resolution%", worklog_comments)
		INPUT_DATA = INPUT_DATA.replace("%Technician%", technician)
		INPUT_DATA = INPUT_DATA.replace("%Item%", ITEM)
		INPUT_DATA = INPUT_DATA.replace("%Subcategory%", SUBCAT)
		url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'?OPERATION_NAME=EDIT_REQUEST&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
		headers = {'Content-Type': 'application/xml'}	
		response += requests.post(url, headers=headers).text

	return response

if __name__ == '__main__':

	bids = ['76311','76308','76306','76302','76300','76296','76291','76289','76287','76282','76280','76279','76269','76263','76262','76261','76260','76255','76254','76252','76251','76244','76242','76241','76208','76205','76200','76199','76194','76185','76146','76135','76131','76130','76124','76064','76037']

	for bid in bids:
		# http://10.2.4.87:8080/bidclosebyjira?
		# resolution=.
		# &issue_key={{issue.key}}
		# &component={{issue.components.name.urlEncode}}
		# &jira_type={{issue.issuetype.name}}
		# &user={{issue.fields.Assignee}}
		# &sdp_id={{issue.fields.sdp_id}}
		# &subject={{issue.summary.urlEncode}}
		# &description={{issue.fields.description.urlEncode}}
		query = {'sdp_id': bid, 
				'workMinutes': '5',
				'description': 'consultation',
				'jira_type': 'Consultation',
				'subject': 'test',
				'issue_key': 'test',
				'component': '1C-Сервис',
				'user': 'Юрасов Алексей Александрович',
				}

		response = sdp_bid_close(query)
		print(response)
		break

	print('done')
