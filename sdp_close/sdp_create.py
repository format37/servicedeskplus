import requests
import xml.etree.cElementTree as ET
import urllib.parse
from jira.utils import json_loads
from aiohttp import web
import datetime
import sys
from jira import JIRA
import json
from jira.utils import json_loads
import urllib

def issue_assignee(jira,issue,accountId):
	url = jira._options['server'] + '/rest/api/latest/issue/' + issue + '/assignee'
	payload = {'accountId': accountId}
	return jira._session.put(url, data=json.dumps(payload))

def create_issue(jira, project,summary,description,accountId,issuetype,item):
	if '-Сервис' in item:
		item='1С-Сервис'
	
	issue_dict={
		'project': project,
		'issuetype': issuetype,
		'components': [{'name': item}],
		'summary': summary,
		'description': description,
		'assignee': {'accountId': accountId}
	}
	return jira.create_issue(fields=issue_dict)

async def sdp_bid_create(request):
	
	print('\n======= sdp create by ats:',datetime.datetime.now())
	sdp_order=''
	technican=''
	category=''
	created_by 				= request.rel_url.query['created_by']				# Петров М.В.
	caller_phone_number		= request.rel_url.query['caller_phone_number']		# 2001 - имя хоста от Nagios	
	department				= request.rel_url.query['department']				# MRM
	receiver_phone_number	= request.rel_url.query['receiver_phone_number']	# SIP/1611 - звонок принят
	#api_key					= request.rel_url.query['api_key']					# API Key sdp	
	with open('token.key','r') as fh:
		api_key=fh.read()
		fh.close()
	technicans={
		'1611':'Сотников Артём Игоревич',
		'1613':'Юрасов Алексей Александрович',
		'1606':'Бывальцев Виктор Валентинович',
		'1621':'Полухин Владимир Геннадьевич',
		'1910':'Васильченко Евгения Алексеевна',
		'1604':'Фролов Максим Евгеньевич',
		'1615':'Семенов Олег Владимирович',
		'1601':'Кузьмин Евгений Андреевич',
		'1602':'Дрожжин Николай Сергеевич',
		'1504':'Мизякин Антон Сергеевич',
		'1501':'Васильев Дмитрий Александрович',
		'1608':'Головин Олег Дмитриевич',
		'1519':'Бойко Илья Вадимович',
	}
	receiver_four_digit_phone=receiver_phone_number[4:]
	if receiver_four_digit_phone in technicans.keys():
		technican = technicans[receiver_four_digit_phone]
	
	subject		= created_by+' '+caller_phone_number+' Оставил Заявку '+department
	description = subject+' Звонок принят '+receiver_phone_number+' '+technican
	create_request_file='CREATE_REQUEST.xml'
	
	response = '0'
	requester	= 'RoboTechnician'
	
	requesters={
		'1539':'Смолина Наталья Викторовна',
		'1639':'Судакова Елена Викторовна',
		'2001':'Муненко Максим Владимирович',
		'1531':'Бухтин Андрей Борисович',
		'1550':'Кузьмин Олег Юрьевич',
		'1516':'Лапшина Инесса Николаевна',
		'1610':'Хайтович Светлана Федоровна',
		'1542':'Руссман Татьяна Викторовна',
		'1509':'Кондратьев Сергей Александрович',
		'1645':'Дробышева Анна Сергеевна',
		'1802':'Буренкова Вера Леонидовна',
		'1545':'Гундоров Илья Александрович',
		'2003':'Мирошник Максим Геннадьевич',
		'1536':'Смирнов Геннадий Валерьевич',
		'1532':'Пономарев Павел Петрович',
		'1557':'Глазкова Ольга Ивановна',
		'1409':'Шабанова Ирина Викторовна',
		'1569':'Голосина Мария Игоревна',
		'1568':'Глушков Дмитрий Александрович',
		'1534':'Лагутин Юрий Семенович',
		'1579':'Боголюбов Дмитрий Александрович',
		'1520':'Авечкин Александр Дмитреевич',
		'1571':'Дворова Ольга Викторовна',
		'1528':'Захаров Василий Павлович',
		'1612':'Сычева Ольга Ивановна',
		'1572':'Леонова Марина Анатольевна',
		'1548':'Симанова Екатерина Юрьевна',
		'1523':'Апряткин Александр Васильевич',
		'1676':'Слободенюк Оксана Юрьевна',
		'2004':'Самохин Олег Игоревич',
		'1584':'Авдеева Валентина Валерьевна',
		'1617':'Акинфиева Евгения Валерьевна',
		'1527':'Кудинов Дмитрий Александрович',
		'1545':'Гундоров Илья Александрович',
		'2101':'Темгаев Павел Борисович',
		'1618':'Захарова Наталья Юрьевна',
	}
	
	requesters.update(technicans)
	
	if caller_phone_number in requesters.keys():
		requester	= requesters[caller_phone_number]

	print('created_by:',created_by)
	print('requester',requester)
	print('technican:',technican)
	print('caller_phone_number:',caller_phone_number)
	print('api_key:',api_key)
	print('department:',department)
	print('receiver_phone_number:',receiver_phone_number)
	print('subject:',subject)
	
	with open(create_request_file,'rb') as fh:		
		INPUT_DATA	= fh.read().decode("utf-8")
		INPUT_DATA = INPUT_DATA.replace("%Subject%",	subject)
		INPUT_DATA = INPUT_DATA.replace("%Technician%",	technican)
		INPUT_DATA = INPUT_DATA.replace("%Category%",	category)
		INPUT_DATA = INPUT_DATA.replace("%Description%",description)
		INPUT_DATA = INPUT_DATA.replace("%Requester%",requester)
		url='http://10.2.4.46/sdpapi/request/?OPERATION_NAME=ADD_REQUEST&TECHNICIAN_KEY='+api_key+'&INPUT_DATA='+urllib.parse.quote_plus(INPUT_DATA)
		#print(INPUT_DATA)
		headers = {'Content-Type': 'application/xml'}		
		xmlData = requests.post(url, headers=headers).text
		API = ET.fromstring(xmlData)
		#print('xmlData',xmlData)
		responce	= API[0]		
		operation	= responce[0]
		result		= operation[0]
		status		= result[0]
		print('status',status.text)
		message		= result[1]
		print('message',message.text)
		try:
			details		= operation[1]
			response = details[0].text;
			print('sdp new order',details[0].text)
			sdp_order=details[0].text
		except:
			print('unable to create new order')
	
	if sdp_order!='':
		print('\n======= jira create by ats:',datetime.datetime.now())
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
		with open('jira.key','r') as key_file:
			jira_key = key_file.read()

		jira = JIRA(options=jira_options, basic_auth=('yurasov@iceberg.ru', jira_key))

		# param=sys.argv[1]
		# file_name=param[param.rfind('/')+1:]
		# json_path='request\\'+file_name
		# with open(json_path, encoding='utf-8') as json_file:
		# #with open(json_path, encoding='cp1251') as json_file:
			# json_data=json.loads(json_file.read())
			# request=json_data['request']

		#issue=jira.issue('PRJ1C-324')
		#issue.update({'Epic_link':'PRJ1C-5'})

		if technican in sdp_jira_accounts.keys():
			issue=create_issue(
				jira,
				'HELP1C',
				sdp_order+' '+subject,
				description,
				sdp_jira_accounts[technican],
				sdp_jira_issue_types['Информация'],
				'1С-Сервис'
				)
			issue.update({'customfield_10043':sdp_order})
			#comment = jira.add_comment(str(issue), 'Created automatically from Service Desk Plus')
			print('jira issue create succesfull')
		else:
			print(technican,'is not in sdp_jira_accounts')
	
	return web.Response(text=response,content_type="text/html")