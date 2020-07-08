#!/usr/bin/env python
import asyncio
from aiohttp import web
import urllib
import urllib.parse
from urllib.parse import urlparse, parse_qsl
import multidict as MultiDict
import requests
import datetime
from time import strftime
from time import gmtime
from time import sleep
from jira import JIRA

import time

async def sdp_bid_close(request):
	try:
		WORKORDERID = request.rel_url.query['sdp_id']
		jira_type		= request.rel_url.query['jira_type']
		SUBJECT		= request.rel_url.query['subject']
		description	= request.rel_url.query['description']
		RESOLUTION	= "Закрыто\n"+request.rel_url.query['resolution']
		ITEM	= request.rel_url.query['component']
		user = request.rel_url.query['user']
		jira_issue = request.rel_url.query['issue_key']
		token	= '76ED27EB-D26D-412A-8151-5A65A16198E7'
		workHours	= '0'
		workMinutes = '1'	
		add_worklog_file='/home/alex/projects/servicedeskplus/sdp_close/ADD_WORKLOG.xml'
		edit_request_file='/home/alex/projects/servicedeskplus/sdp_close/EDIT_REQUEST.xml'

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

		if ITEM in sub_cats.keys():
			SUBCAT	= sub_cats[ITEM]
		else:
			SUBCAT = '1С Cистемы'

		print('jira_type',jira_type)

		jira_sdp_types = {
			'Task':'Изменение',
			'Consultation':'Информация',
			'Bug':'Инцидент',
			'Service':'Обслуживание',
			}

		if jira_type in jira_sdp_types.keys():
			rtype = jira_sdp_types[jira_type]
		else:
			rtype = jira_sdp_types['Consultation']

		print('Subcategory',SUBCAT)
		print('sdp_id',WORKORDERID)
		print('jira issue',jira_issue)
		print('subject',SUBJECT)
		print('description',description)

		users={
			'557058:fa79f484-a387-495b-9862-1af505d8d70a'	: 'Фролов Максим Евгеньевич',
			'5de505aa22389c0d118c3eaf'						: 'Сотников Артём Игоревич',
			'5dfb26b2588f6e0cb033698e'						: 'Семенов Олег Владимирович',
			'557058:f0548e8f-6a09-44bd-bfb5-43a0a40531bb'	: 'Юрасов Алексей Александрович',
			'5dfb273f9422830cacaa5c02'						: 'Полухин Владимир Геннадьевич',
			'5dfb26b35697460cb3d98780'						: 'Бывальцев Виктор Валентинович',
			'5dfb2741eaf5880cad03b10f'						: 'Васильченко Евгения Алексеевна'
		}
		technician = 'Юрасов Алексей Александрович'		


		if user in users.keys():
			technician = users[user]
			print('technician',technician)
		else:
			print('technician not found:',user)
			send_to_telegram('-7022979',str(datetime.datetime.now())+' technician not found:'+str(user) )


		sdp_tokens={
			'Фролов Максим Евгеньевич'		: '210ECA4F-859F-45DE-9DDB-5AB19B9617A5',
			'Сотников Артём Игоревич'		: '4CD78BFF-BFBA-4A00-A91C-2DF01EA12CAA',
			'Семенов Олег Владимирович'		: 'CEB75C6A-1D07-411E-B34C-ECC6902AA1A0',
			'Юрасов Алексей Александрович'	: '76ED27EB-D26D-412A-8151-5A65A16198E7',
			'Полухин Владимир Геннадьевич'	: '5801D334-C5C3-4BEC-9209-309AFCA27DAE',
			'Бывальцев Виктор Валентинович'	: '157D4CAC-6947-4F44-BCE7-BAF2E3ABF672',
		}
		token = sdp_tokens['Юрасов Алексей Александрович']
		if technician in sdp_tokens.keys():
			token = sdp_tokens[technician]
			print('sdp token',token)
		else:
			print('sdp token for',technician,'not found. using default')
			send_to_telegram('-7022979',str(datetime.datetime.now())+' sdp token for '+str(technician)+' not found. using default' )

		response = ''
		worklog_comments = ''

		with open(add_worklog_file,'rb') as fh:
			INPUT_DATA_ORIGINAL	= fh.read().decode("utf-8")

		jira_options = {'server': 'https://icebergproject.atlassian.net'}
		with open('/home/alex/projects/servicedeskplus/sdp_close/jira.key','r') as key_file:
			jira_key = key_file.read()

		jira = JIRA(options=jira_options, basic_auth=('yurasov@iceberg.ru', jira_key))

		worklogs = jira.worklogs(jira_issue)
		for wl in worklogs:
			spent_hours = int(strftime("%H", gmtime(wl.timeSpentSeconds)))
			spent_minutes = int(strftime("%M", gmtime(wl.timeSpentSeconds)))

			try:
				worklog_comments+=('' if worklog_comments=='' else '\n')+wl.comment
			except:
				print('no comments')

			INPUT_DATA = INPUT_DATA_ORIGINAL
			INPUT_DATA = INPUT_DATA.replace("%technician%", technician)
			INPUT_DATA = INPUT_DATA.replace("%workMinutes%", str(spent_minutes))
			INPUT_DATA = INPUT_DATA.replace("%workHours%", str(spent_hours))
			url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'/worklogs?OPERATION_NAME=ADD_WORKLOG&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
			headers = {'Content-Type': 'application/xml'}	
			response += requests.post(url, headers=headers).text

		with open(edit_request_file,'rb') as fh:
			INPUT_DATA	= fh.read().decode("utf-8")
			INPUT_DATA = INPUT_DATA.replace("%rtype%", rtype)
			INPUT_DATA = INPUT_DATA.replace("%Description%", description)
			INPUT_DATA = INPUT_DATA.replace("%Subject%", SUBJECT)
			INPUT_DATA = INPUT_DATA.replace("%Resolution%", 'Закрыто' if worklog_comments=='' else worklog_comments)
			INPUT_DATA = INPUT_DATA.replace("%Technician%", technician)
			INPUT_DATA = INPUT_DATA.replace("%Item%", ITEM)
			INPUT_DATA = INPUT_DATA.replace("%Subcategory%", SUBCAT)
			url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'?OPERATION_NAME=EDIT_REQUEST&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
			headers = {'Content-Type': 'application/xml'}	
			response += requests.post(url, headers=headers).text
		
	except Exception as e:
		response	= 'error'
		send_to_telegram('-7022979',str(datetime.datetime.now())+' sdp close by jira error: '+str(e))

	return web.Response(text=response,content_type="text/html")

async def call_check(request):
	return web.Response(text='ok',content_type="text/html")
	
async def call_jira_pause(request):
	assignee	= request.rel_url.query['assignee']
	issuekey	= request.rel_url.query['issuekey']
	jira_set_pause(assignee,issuekey)
	
def send_to_telegram(chat,message):
	headers = {
		"Origin": "http://scriptlab.net",
		"Referer": "http://scriptlab.net/telegram/bots/relaybot/",
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
		}
	url     = "http://scriptlab.net/telegram/bots/relaybot/relaylocked.php?chat="+chat+"&text="+urllib.parse.quote_plus(message)
	return requests.get(url,headers = headers)

app = web.Application()
app.router.add_route('GET', '/check', call_check)
app.router.add_route('GET', '/bidclosebyjira', sdp_bid_close)

with open('/home/alex/projects/servicedeskplus/sdp_close/telegram.chat','r') as fh:
	telegram_group=fh.read()
	fh.close()
send_to_telegram(telegram_group,str(datetime.datetime.now())+' server started')

loop = asyncio.get_event_loop()
handler = app.make_handler()
f = loop.create_server(handler, port='80')
srv = loop.run_until_complete(f)

print('serving on', srv.sockets[0].getsockname())
try:
	loop.run_forever()
except KeyboardInterrupt:
	print("serving off...")
finally:
	loop.run_until_complete(handler.finish_connections(1.0))
	srv.close()