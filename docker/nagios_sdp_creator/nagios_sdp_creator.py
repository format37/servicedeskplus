#!/usr/bin/env python
import asyncio
from aiohttp import web
import urllib
import urllib.parse
#from urllib.parse import urlparse, parse_qsl
#mport multidict as MultiDict
import requests
from sdp_create import sdp_bid_create
from jira_pause import set_pause as jira_set_pause
import datetime
from time import strftime
from time import gmtime
#from time import sleep
from jira import JIRA
import os
import socket
#import time
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def bid_edit(request):
	try:
		SUBJECT		= request.rel_url.query['SUBJECT']
	except:
		SUBJECT		=''
	try:
		RESOLUTION	= request.rel_url.query['RESOLUTION']
	except:
		RESOLUTION	=''
	try:
		technician	= request.rel_url.query['TECHNICIAN']
	except:
		technician	=''
	try:
		workMinutes = request.rel_url.query['workMinutes']
	except:
		workMinutes =''
	try:
		workHours	= request.rel_url.query['workHours']
	except:
		workHours	=''
	try:
		token	= request.rel_url.query['token']
	except:
		token	=''
	
	content='''<html><body>
		<form method="get" action="http://10.2.4.87:8080/bidclose">
		<table>
		<tr>
			<td>ID Заявки:</td>
			<td><input name="WORKORDERID"> *</td>
		</tr>
		<tr>
			<td>Тема:</td>
			<td><input name="SUBJECT" value="'''+SUBJECT+'''"> *</td>			
		</tr>		  
		<tr>
			<td>Исполнитель:</td>
			<td><input name="TECHNICIAN" value="'''+technician+'''"> *</td>
		</tr>		  
		<tr>
			<td>Заключение:</td>
			<td><input name="RESOLUTION" value="'''+RESOLUTION+'''"> *</td>
		</tr>
		<tr>
			<td>Минут:</td>
			<td><input name="WORKMINUTES" value="'''+workMinutes+'''"></td>
		</tr>
		<tr>
			<td>Часов:</td>
			<td><input name="WORKHOURS" value="'''+workHours+'''"></td>
		</tr>
		<tr>
			<td>Ключ:</td>
			<td><input name="TOKEN" value="'''+token+'''"></td>
		</tr>
		</table>
		<br>		
		<input type="submit" value="Закрыть">
		</form>
		</body></html>'''
	return web.Response(text=content,content_type="text/html")

async def bid_close(request):
	
	back_link='<br><input type="submit" value="Продолжить"><br><br>'
	
	try:
		WORKORDERID = request.rel_url.query['WORKORDERID']
	except:
		print('Не заполнено поле ID Заявки'+back_link)
		return
		
	try:
		SUBJECT		= request.rel_url.query['SUBJECT']
	except:
		print('Не заполнено поле Тема'+back_link)
		return
	
	try:
		RESOLUTION	= request.rel_url.query['RESOLUTION']
	except:
		print('Не заполнено поле Заключение'+back_link)
		return
	
	try:
		technician	= request.rel_url.query['TECHNICIAN']
	except:
		print('Не заполнено поле Исполнитель'+back_link)
		return
		
	try:
		token	= request.rel_url.query['TOKEN']
	except:
		print('Не заполнено поле Ключ'+back_link)
		return
	
	try:
		workMinutes = request.rel_url.query['WORKMINUTES']	
	except:
		workMinutes = ''
		
	try:
		workHours	= request.rel_url.query['WORKHOURS']
	except:
		workHours	=''
	
	if workMinutes=='':
		workMinutes='0'
	if workHours=='':
		workHours='0'
	
	edit_request_file='/home/alex/projects/servicedeskplus/sdp_close/EDIT_REQUEST.xml'
	add_worklog_file='/home/alex/projects/servicedeskplus/sdp_close/ADD_WORKLOG.xml'
	
	#responce = 'WORKORDERID'+'<br>'+SUBJECT+'<br>'+RESOLUTION+'<br>'+technician+'<br>'+workMinutes+'<br>'+workHours+'<br>'+requester'
	content='''<html><body>
	<form method="get" action="http://10.2.4.87:8080/bidedit">
	<input type="hidden" id="TECHNICIAN" name="TECHNICIAN" value="'''+technician+'''">
	<input type="hidden" id="SUBJECT" name="SUBJECT" value="'''+SUBJECT+'''">
	<input type="hidden" id="RESOLUTION" name="RESOLUTION" value="'''+RESOLUTION+'''">
	<input type="hidden" id="workMinutes" name="workMinutes" value="'''+workMinutes+'''">
	<input type="hidden" id="workHours" name="workHours" value="'''+workHours+'''">
	<input type="hidden" id="token" name="token" value="'''+token+'''">
		<table>
		<tr>
			<td>ID Заявки:</td>
			<td>'''+WORKORDERID+'''</td>			
		</tr>
		<tr>
			<td>Тема:</td>
			<td>'''+SUBJECT+'''</td>			
		</tr>
		<tr>
			<td>Исполнитель:</td>
			<td>'''+technician+'''</td>
		</tr>		  
		<tr>
			<td>Заключение:</td>
			<td>'''+RESOLUTION+'''</td>
		</tr>
		<tr>
			<td>Минут:</td>
			<td>'''+workMinutes+'''</td>
		</tr>
		<tr>
			<td>Часов:</td>
			<td>'''+workHours+'''</td>
		</tr>
		</table>
		<br>'''	
	
	with open(add_worklog_file,'rb') as fh:
		INPUT_DATA	= fh.read().decode("utf-8")
		INPUT_DATA = INPUT_DATA.replace("%technician%", technician)
		INPUT_DATA = INPUT_DATA.replace("%workMinutes%", workMinutes)
		INPUT_DATA = INPUT_DATA.replace("%workHours%", workHours)
		url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'/worklogs?OPERATION_NAME=ADD_WORKLOG&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
		headers = {'Content-Type': 'application/xml'}	
		response = requests.post(url, headers=headers).text
		content	+='<br>'+response.replace('\n','<br>')+'<br>'

	with open(edit_request_file,'rb') as fh:
		INPUT_DATA	= fh.read().decode("utf-8")
		INPUT_DATA = INPUT_DATA.replace("%Subject%", SUBJECT)
		INPUT_DATA = INPUT_DATA.replace("%Resolution%", RESOLUTION)
		#INPUT_DATA = INPUT_DATA.replace("%requester%", '' if requester=='' else '<parameter><name>requester</name><value>'+requester+'</value></parameter>')
		url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'?OPERATION_NAME=EDIT_REQUEST&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
		headers = {'Content-Type': 'application/xml'}	
		response = requests.post(url, headers=headers).text
		content	+='<br>'+response.replace('\n','<br>')+'<br>'

	content+=back_link
	content+='<p><tt>'
	content+='''
	<br>-------------------YAao,---------------------------
	<br>--------------------Y8888b,------------------------
	<br>------------------,oA8888888b,---------------------
	<br>------------,aaad8888888888888888bo,---------------
	<br>---------,d888888888888888888888888888b,-----------
	<br>-------,888888888888888888888888888888888b,--------
	<br>------d8888888888888888888888888888888888888,------
	<br>-----d888888888888888888888888888888888888888b-----
	<br>----d888888P'--------------------`Y888888888888,---
	<br>----88888P'--------------------Ybaaaa8888888888l---
	<br>---a8888'----------------------`Y8888P'-`V888888---
	<br>-d8888888a--------------------------------`Y8888---
	<br>AY/''-`\Y8b---------------------------------``Y8b--
	<br>Y'------`YP------------------------------------~~--'''
	content+='</tt></p>'
	content+='</form></body></html>'
	return web.Response(text=content,content_type="text/html")


# def get_jira_accounts_from_file(file_path='jira_members.json'):
def get_json_from_file(file_path):
	with open(file_path, 'r') as f:
		return json.load(f)

# def get_jira_accounts_from_url(url):
def get_json_from_url(url):
	try:
		response = requests.get(url)
		response.raise_for_status()  # Raise an exception for HTTP errors
		return response.json()
	except requests.RequestException as e:
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
	
	# print('technician not found 1:',user)
	# send_to_telegram(str(datetime.datetime.now())+' technician not found 1:'+str(user) )
	logger.error('technician not found 1: %s', value_to_find)

	return default

async def sdp_bid_close(request):
	try:
		# print('\n======= sdp close by jira:',datetime.datetime.now())
		logger.info('>> sdp close by jira: %s', datetime.datetime.now())
		#print(request.rel_url.query)
		WORKORDERID = request.rel_url.query['sdp_id']
		jira_type		= request.rel_url.query['jira_type']
		SUBJECT		= request.rel_url.query['subject']
		#description	= 'test'
		description	= request.rel_url.query['description']
		#RESOLUTION	= "Закрыто\n"+request.rel_url.query['resolution']
		RESOLUTION	= "Закрыто\n"
		ITEM	= request.rel_url.query['component']
		user = request.rel_url.query['user']
		jira_issue = request.rel_url.query['issue_key']	

		token	= os.environ.get('SDP_USER_TOKEN', '')
		workHours	= '0'
		workMinutes = '1'	
		add_worklog_file='ADD_WORKLOG.xml'
		edit_request_file='EDIT_REQUEST.xml'

		# print('item received:',ITEM)
		logger.info('item received: %s', ITEM)

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
			# print('item changed')
			logger.info(f'item changed')

		# print('item set:',ITEM)
		logger.info('item set: %s', ITEM)

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

		# print('jira_type',jira_type)
		logger.info('jira_type: %s', jira_type)

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

		print('Subcategory',SUBCAT)
		print('sdp_id',WORKORDERID)
		print('jira issue',jira_issue)
		print('subject',SUBJECT)
		print('description',description)
		#print('resolution',RESOLUTION)

		try:
			config = get_json_from_url("https://gitlab.icecorp.ru/service/servicedeskplus/-/raw/master/settings/config.json")
		except Exception as e:
			# send_to_telegram(str(datetime.datetime.now())+' Unable to read config from config.json. Using default. Error: '+str(e))
			logger.error('Unable to read config from config.json. Using default. Error: %s', e)
			config = get_json_from_file('config.json')

		# try:
		# 	sdp_jira_accounts = get_json_from_url("https://gitlab.icecorp.ru/service/servicedeskplus/-/raw/master/settings/jira_members.json")
		# except Exception as e:
		# 	print(e);
		# 	sdp_jira_accounts = get_json_from_file('jira_members.json')
		sdp_jira_accounts = config['jira_members']

		"""users={
			'a.yurasov@iceberg.ru' : 'Юрасов Алексей Александрович',
			'v.byvaltsev@iceberg.ru' : 'Бывальцев Виктор Валентинович',
			'i.titov@iceberg.ru' : 'Титов Иван Сергеевич',
			'a.sevrjukova@iceberg.ru' : 'Севрюкова Анна Юрьевна',
			'a.sevrjukova@iceberg.ru' : 'Севрюкова Анна Юрьевна',
		}
		"""
		
		# technician = 'Юрасов Алексей Александрович'
		technician = 'Титов Иван Сергеевич'
		# if user in users.keys():
			# technician = users[user]
		if user in sdp_jira_accounts.values():
			technician = find_key_by_value(
				sdp_jira_accounts, 
				user,
				'Титов Иван Сергеевич'
				)
			# print('technician',technician)
			logger.info('technician: %s', technician)
		else:
			# print('technician not found 1:',user)
			logger.error('technician not found 1: %s', user)
			# send_to_telegram(str(datetime.datetime.now())+' technician not found 1:'+str(user) )

		# sdp_tokens={
		# 	'Юрасов Алексей Александрович' : '76ED27EB-D26D-412A-8151-5A65A16198E7',
		# 	'Бывальцев Виктор Валентинович' : '157D4CAC-6947-4F44-BCE7-BAF2E3ABF672',
		# 	'Титов Иван Сергеевич' : '53A9ED31-00AB-4FCB-8E97-FF523E781281',
		# 	'Севрюкова Анна Юрьевна' : 'A58A60DB-6F90-415E-8620-CD2674918B22',
		# 	'Гречкин Алексей Васильевич' : 'AAAC9CA6-C8D5-425C-96AA-578AF0518BF0',
		# }
		# try:
		# 	sdp_tokens = get_json_from_url("https://gitlab.icecorp.ru/service/servicedeskplus/-/raw/master/settings/sdp_tokens.json")
		# except Exception as e:
		# 	print(e)
		# 	sdp_tokens = get_json_from_file('sdp_tokens.json')
		sdp_tokens = config['sdp_tokens']

		# token = sdp_tokens['Юрасов Алексей Александрович']
		token = sdp_tokens['Титов Иван Сергеевич']
		if technician in sdp_tokens.keys():
			token = sdp_tokens[technician]
			# print('sdp token',token)
			logger.info('sdp token: %s', token)
		else:
			# print('sdp token for',technician,'not found. using default')
			logger.error('sdp token for %s not found. using default', technician)
			# send_to_telegram(str(datetime.datetime.now())+' sdp token for '+str(technician)+' not found. using default' )

		response = ''
		worklog_comments = '.'

		with open(add_worklog_file,'rb') as fh:
			INPUT_DATA_ORIGINAL	= fh.read().decode("utf-8")

		#jira_options = {'server': 'https://icebergproject.atlassian.net'}
		jira_options = {'server': 'http://jira.iceberg.ru'}
		jira_key = os.environ.get('JIRA_KEY', '')	

		#with open('/home/alex/projects/servicedeskplus/sdp_close/jira.key','r') as key_file:
		#	jira_key = key_file.read()
		jira = JIRA(options=jira_options, basic_auth=('ServiceDesk', jira_key))

		worklogs = jira.worklogs(jira_issue)
		spent_hours = 0
		spent_minutes = 1
		for wl in worklogs:
			spent_hours = int(strftime("%H", gmtime(wl.timeSpentSeconds)))
			spent_minutes = int(strftime("%M", gmtime(wl.timeSpentSeconds)))
			#print(wl.timeSpent, wl.timeSpentSeconds, wl.comment)

			try:
				worklog_comments+=('' if worklog_comments=='' else '\n')+wl.comment
			except:
				print('no comments')
			worklog_comments = 'Закрыто' if worklog_comments.replace('_n','')=='' else worklog_comments
			
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
			INPUT_DATA = INPUT_DATA.replace("%Description%", description) #
			INPUT_DATA = INPUT_DATA.replace("%Subject%", SUBJECT)
			INPUT_DATA = INPUT_DATA.replace("%Resolution%", worklog_comments)
			INPUT_DATA = INPUT_DATA.replace("%Technician%", technician)
			INPUT_DATA = INPUT_DATA.replace("%Item%", ITEM)
			INPUT_DATA = INPUT_DATA.replace("%Subcategory%", SUBCAT)
			url='http://10.2.4.46/sdpapi/request/'+WORKORDERID+'?OPERATION_NAME=EDIT_REQUEST&TECHNICIAN_KEY='+token+'&INPUT_DATA='+INPUT_DATA
			headers = {'Content-Type': 'application/xml'}	
			response += requests.post(url, headers=headers).text

	except Exception as e:
		response	= 'error'
		# send_to_telegram(str(datetime.datetime.now())+' sdp close by jira error: '+str(e))
		logger.error('sdp close by jira error: %s', e)

	return web.Response(text=response,content_type="text/html")


async def call_check(request):
	return web.Response(text='ok',content_type="text/html")
	

async def call_jira_pause(request):
	assignee	= request.rel_url.query['assignee']
	issuekey	= request.rel_url.query['issuekey']
	jira_set_pause(assignee,issuekey)
	

def send_to_telegram(message):
	token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
	chat_id = os.environ.get('TELEGRAM_CHAT', '')
	session = requests.Session()
	get_request = 'https://api.telegram.org/bot' + token	
	get_request += '/sendMessage?chat_id=' + chat_id
	get_request += '&text=' + urllib.parse.quote_plus(message)
	session.get(get_request)


def main():

	#while(1):
	#	pass

	app = web.Application()
	app.router.add_route('GET', '/bidedit', bid_edit)
	app.router.add_route('GET', '/', call_check)
	app.router.add_route('GET', '/bidclose', bid_close)
	app.router.add_route('GET', '/bidcreate', sdp_bid_create)
	app.router.add_route('GET', '/bidclosebyjira', sdp_bid_close)
	#app.router.add_route('GET', '/telegram', telegram)
	app.router.add_route('GET', '/jirapause', call_jira_pause)

	send_to_telegram(str(datetime.datetime.now())+' sdp order creator server started on ' + str(socket.gethostname()))

	loop = asyncio.get_event_loop()
	handler = app.make_handler()
	f = loop.create_server(handler, port='8080')
	srv = loop.run_until_complete(f)

	print('serving on', srv.sockets[0].getsockname())
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		print("serving off...")
	finally:
		loop.run_until_complete(handler.finish_connections(1.0))
		srv.close()


if __name__ == '__main__':
	main()
