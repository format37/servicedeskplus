import requests
import xml.etree.cElementTree as ET
import urllib.parse
from jira.utils import json_loads
from aiohttp import web
import datetime

async def bid_create(request):
	print('\n======= sdp create by ats:',datetime.datetime.now())
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

	print('created_by:',created_by)
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
		except:
			print('unable to create new order')
	return web.Response(text=response,content_type="text/html")