#!/usr/bin/env python3
import requests
import xml.etree.cElementTree as ET
import urllib.parse
from aiohttp import web
import datetime
import sys
from jira import JIRA
import json
from jira.utils import json_loads
import urllib
import pymssql
import time
import asyncio
import os
import urllib3


def send_to_telegram(message):
	token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
	chat_id = os.environ.get('TELEGRAM_CHAT', '')
	session = requests.Session()
	get_request = 'https://api.telegram.org/bot' + token	
	get_request += '/sendMessage?chat_id=' + chat_id
	get_request += '&text=' + urllib.parse.quote_plus(message)
	session.get(get_request)

def jira_datetime_format(dt):
    return str(dt.year)+'-'+str(dt.month).zfill(2)+'-'+str(dt.day).zfill(2)+'T'+str(dt.hour).zfill(2)+':'+str(dt.minute).zfill(2)+':'+str(dt.second).zfill(2)+'.'+str(int(dt.microsecond/1000)).zfill(3)+'+0300'

def issue_assignee(jira,issue,accountId):
	url = jira._options['server'] + '/rest/api/latest/issue/' + issue + '/assignee'
	payload = {'accountId': accountId}
	return jira._session.put(url, data=json.dumps(payload))

def create_issue(jira, project,summary,description,accountId,issuetype,item):
	if '-Сервис' in item:
		item='1С-Сервис'
	#b = datetime.datetime.now()
	#print(ex)
	#print(jira_datetime_format(b))
	issue_dict={
		'project': project,
		'issuetype': issuetype,
		'components': [{'name': item}],
		'summary': summary,
		'description': description,
		'assignee': {'accountId': accountId},
		'duedate': jira_datetime_format(datetime.datetime.now()),
	}
	return jira.create_issue(fields=issue_dict)

async def sdp_bid_create(created_by,caller_phone_number,department,receiver_phone_number):
	
	try:
		print('\n======= sdp create by ats:',datetime.datetime.now())
		sdp_order=''
		technican=''
		category=''
		#created_by 				= request.rel_url.query['created_by']				# Петров М.В.
		#caller_phone_number		= request.rel_url.query['caller_phone_number']		# 2001 - имя хоста от Nagios	
		#department				= request.rel_url.query['department']				# MRM
		#receiver_phone_number	= request.rel_url.query['receiver_phone_number']	# SIP/1611 - звонок принят
		#api_key					= request.rel_url.query['api_key']					# API Key sdp
		#api_key = os.environ.get('API_KEY', '')
		sdp_key = os.environ.get('SDP_KEY', '')
		
		try:
			http = urllib3.PoolManager()
			url = 'http://10.2.4.52/service/servicedeskplus/-/raw/master/settings/technicans.txt'
			response = http.request('GET', url)
			technicans = eval(response.data.decode('utf-8'))
		except Exception as e:
			print('technicans.txt request error: '+str(e))
			technicans={
				'1611':'Сотников Артём Игоревич',
				'1613':'Юрасов Алексей Александрович',
				'1606':'Бывальцев Виктор Валентинович',
				'1615':'Семенов Олег Владимирович',
				'1601':'Кузьмин Евгений Андреевич',
				'1602':'Дрожжин Николай Сергеевич',
				'1501':'Васильев Дмитрий Александрович',
				'1608':'Головин Олег Дмитриевич',
				'1519':'Бойко Илья Вадимович',
				'1607':'Титов Иван Сергеевич',
				'2202':'Севрюкова Анна Юрьевна',
				'1621':'Песоцкий Константин Вячеславович',
			}
		receiver_four_digit_phone=receiver_phone_number[-4:]
		if receiver_four_digit_phone in technicans.keys():
			technican = technicans[receiver_four_digit_phone]

		subject		= created_by+' '+caller_phone_number+' '+department
		description = subject+' Звонок принят '+receiver_phone_number+' '+technican
		# create_request_file='/home/alex/projects/servicedeskplus/sdp_close/CREATE_REQUEST.xml'
		create_request_file='CREATE_REQUEST.xml'

		response = '0'
		requester	= 'RoboTechnician'

		try:
			http = urllib3.PoolManager()
			url = 'http://10.2.4.52/service/servicedeskplus/-/raw/master/settings/requesters.txt'
			response = http.request('GET', url)
			requesters = eval(response.data.decode('utf-8'))
		except Exception as e:
			print('requesters.txt request error: '+str(e))

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
				'2003':'Петровский Виталий Игоревич',
				'1536':'Смирнов Геннадий Валерьевич',
				'1532':'Пономарев Павел Петрович',
				'1557':'Глазкова Ольга Ивановна',
				'1409':'Шабанова Ирина Викторовна',
				'1569':'Голосина Мария Игоревна',
				'1568':'Глушков Дмитрий Александрович',
				'1534':'Лагутин Юрий Семенович',
				'1579':'Тихонов Антон Витальевич',
				'1520':'Палагин Андрей Юрьевич',
				'1571':'Дворова Ольга Викторовна',
				'1528':'Захаров Василий Павлович',
				'1612':'Сычева Ольга Ивановна',
				'1572':'Леонова Марина Анатольевна',
				'1548':'Симанова Екатерина Юрьевна',
				'1523':'Апряткин Александр Васильевич',
				'1676':'Сионская Галина Андреевна',
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
		print('sdp_key:',sdp_key)
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
			url='http://10.2.4.46/sdpapi/request/?OPERATION_NAME=ADD_REQUEST&TECHNICIAN_KEY='+sdp_key+'&INPUT_DATA='+urllib.parse.quote_plus(INPUT_DATA)
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

			details		= operation[1]
			response = details[0].text;
			print('sdp new order',details[0].text)
			sdp_order=details[0].text
			
	except Exception as e:
		message = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))+\
		'\njira order_creator_daemon error: '+str(e)
		send_to_telegram(message)
	
	try:
	
		response =''
		#print('\nreturn',datetime.datetime.now())
		#return web.Response(text=response,content_type="text/html")
		
		jira_issue=''
		if sdp_order!='':
			print('\n======= jira create by ats:',datetime.datetime.now())
			#icebergproject.atlassian.net/jira/people/search
			#select an account and copypaste id from adress after people/
			sdp_jira_accounts={	
				'Сотников Артём Игоревич':'5de505aa22389c0d118c3eaf',
				'Семенов Олег Владимирович':'5dfb26b2588f6e0cb033698e',				
				'Бывальцев Виктор Валентинович':'5dfb26b35697460cb3d98780',
				'Юрасов Алексей Александрович':'557058:f0548e8f-6a09-44bd-bfb5-43a0a40531bb',
				'Титов Иван Сергеевич':'5f3a2c5d3e9e2e004dd3bf1c',
				'Севрюкова Анна Юрьевна':'5f6c3d20f0d40100704c2a57',
				'Песоцкий Константин Вячеславович':'603652b125b84e00694657ab',
				}
				
			sdp_jira_issue_types={
				'Изменение':'Task',
				'Информация':'Consultation',
				'Инцидент':'Bug',
				'Обслуживание':'Service',
			}

			jira_options = {'server': 'https://icebergproject.atlassian.net'}
			#with open('/home/alex/projects/servicedeskplus/sdp_close/jira.key','r') as key_file:
			#	jira_key = key_file.read().replace('\n', '')
			jira_key = os.environ.get('JIRA_KEY', '')
			jira_user = 'yurasov@iceberg.ru'
			#jira_user = 'frolov@iceberg.ru'

			jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_key))

			#issue=jira.issue('PRJ1C-324')
			#issue.update({'Epic_link':'PRJ1C-5'})

			if technican in sdp_jira_accounts.keys():
				issue=create_issue(
					jira,					
					'DEV1CHELP', #'HELP1C',
					sdp_order+' '+subject,
					description,
					sdp_jira_accounts[technican],
					sdp_jira_issue_types['Информация'],
					'1С-Сервис'
					)
				# custom felds list:
				# https://icebergproject.atlassian.net/rest/api/3/issue/HELP1C-424
				jira_issue='\nJira: https://icebergproject.atlassian.net/browse/'+str(issue)
				issue.update({'customfield_10043':sdp_order}) # sdp_id
				issue.update({'customfield_10044':requester}) # requester_name
				issue.update({'customfield_10045':caller_phone_number}) # requester_phone
				#comment = jira.add_comment(str(issue), 'Created automatically from Service Desk Plus')
				print('jira issue create succesfull')
			else:
				print(technican,'is not in sdp_jira_accounts')
				message = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))+\
					'\n'+str(technican)+' is not in sdp_jira_accounts'
				send_to_telegram(message)
		
		# send to telegram
		message = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))+\
			'\nЗвонок от '+caller_phone_number+' '+requester+' 74957770320,'+caller_phone_number+\
			'\nПринял '+receiver_phone_number+' '+technican+\
			'\nSdp: http://help.icecorp.ru/WorkOrder.do?woMode=viewWO&woID='+sdp_order+jira_issue
		send_to_telegram(message)
		
		#return web.Response(text=response,content_type="text/html")
	
	except Exception as e:
		message = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))+\
			'\njira order_creator_daemon error: '+str(e)
		send_to_telegram(message)

def connect_sql():
	sql_login='ICECORP\\1c_sql'
	sql_pass='dpCEoF1e4A6XPOL'
	#return pymssql.connect(server='10.2.4.124', user=sql_login, password=sql_pass, database='sdp', autocommit=True)
	return pymssql.connect(server='10.2.4.124', user=sql_login, password=sql_pass, database='sdp')

async def main():
	send_to_telegram(str(datetime.datetime.now())+' jira issue creator daemon started')
	print(time.strftime('%Y-%m-%d %H:%M:%S'),'alive')
	conn = connect_sql()
	cursor = conn.cursor()

	while True:

		query ="select ID_column, created_by,caller_phone_number,department,receiver_phone_number from ats_requests order by event_date"
		cursor.execute(query)
		to_clean = []
		tasks = []
		for row in cursor.fetchall():
			id						= row[0]
			created_by				= row[1]
			caller_phone_number		= row[2]
			department				= row[3]
			receiver_phone_number	= row[4]
			print(time.strftime('%Y-%m-%d %H:%M:%S'),'received',id, created_by,caller_phone_number,department,receiver_phone_number)
			to_clean.append(id)
			tasks.append( asyncio.create_task(sdp_bid_create(created_by,caller_phone_number,department,receiver_phone_number)) )
		
		for task in tasks:
			await task
						
		for id in to_clean:
			query ="delete from ats_requests where ID_column="+str(id)+";"
			cursor.execute(query)
			conn.commit()
		
		if len(tasks)>0:	
			time.sleep(1)
	
asyncio.run(main())
