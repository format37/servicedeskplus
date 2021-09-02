#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import xml.etree.cElementTree as ET
import datetime
import time
import urllib
import urllib.parse
import urllib3
import os

#with open('/home/alex/projects/servicedeskplus/sdp_monitoring/token.key','r') as fh:
#	token=fh.read().replace('\n', '')
#	fh.close()

#with open('/home/alex/projects/servicedeskplus/sdp_monitoring/telegram.group','r') as fh:
#	telegram_group=fh.read().replace('\n', '')
#	fh.close()

get_requests_file='GET_REQUESTS.xml'
alert_minutes_limit	= 30
check_minutes_interval = 10
check_hour_start	= 7
check_hour_end		= 19

def send_to_telegram(message):
	token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
	chat_id = os.environ.get('TELEGRAM_CHAT', '')
	session = requests.Session()
	get_request = 'https://api.telegram.org/bot' + token	
	get_request += '/sendMessage?chat_id=' + chat_id
	get_request += '&text=' + urllib.parse.quote_plus(message)
	session.get(get_request)

def today_is_holiday():
	week_day	= datetime.datetime.today().weekday()
	now = datetime.datetime.now()
	
	workdays	= {
		2018:{
			4:[28],
			}
		}

	if week_day==5 or week_day==6:
		if	now.year in workdays.keys() and now.month in workdays[now.year].keys() and now.day in workdays[now.year][now.month]:
			return False
		else:
			return True
		
	holydays	= {
		2020:{
			5:[1,4,5,11],
			6:[12],
			11:[4],
		}
	}

	if	now.year in holydays.keys() and now.month in holydays[now.year].keys() and now.day in holydays[now.year][now.month]:
		return True
	
	return False	

def dt(u):
	return datetime.datetime.utcfromtimestamp(int(u)+60*60*3)

def check():
	with open(get_requests_file,'rb') as fh:
		token = os.environ.get('SDP_KEY', '')
		url='http://10.2.4.46/sdpapi/request/?OPERATION_NAME=GET_REQUESTS&TECHNICIAN_KEY='+token+'&INPUT_DATA='+fh.read().decode("utf-8")
		headers = {'Content-Type': 'application/xml'}	
		xmlData = requests.post(url, headers=headers).text
		API = ET.fromstring(xmlData)
		
		responce	= API[0]
		operation	= responce[0]
		details		= operation[1]
		
		current_time	= time.time()
		
		try:
			http = urllib3.PoolManager()
			url = 'https://raw.githubusercontent.com/format37/servicedeskplus/master/sdp_monitoring/users.txt'
			response = http.request('GET', url)
			telegram_users = eval(response.data.decode('utf-8'))
		except Exception as e:
			print('Telegram users request error: '+str(e))
			telegram_users = {
				'Песоцкий Константин Вячеславович': '@Komandorr', 
				'Сотников Артём Игоревич': '@vindento', 
				'Севрюкова Анна Юрьевна': '@AnnaSY64', 
				'Юрасов Алексей Александрович': '@format37', 
				'Титов Иван Сергеевич': '@ibrogim66', 
				'Бывальцев Виктор Валентинович': '@I23vitiaz321', 
				'Кузьмин Евгений Андреевич': '@SummerDevil', 
				'Дрожжин Николай Сергеевич': '@nikolay3697', 
				'Васильев Дмитрий Александрович': '@DVasilev', 
				'Головин Олег Дмитриевич': '@Enaleven', 
				'Бойко Илья Вадимович': '@IlyaBoiko'
			}
		
		message = ''
		event_count=0
		
		for record in details:
		
			workorder={}
		
			for parameter in record:
			
				name=parameter[0].text
				value=parameter[1].text
				workorder[name]=value
				
			duebytime	= int(workorder['duebytime'][:10])
			createdtime	= int(workorder['createdtime'][:10])
			duebytime_difference_m		= (duebytime-current_time)/60
			createdtime_difference_m	= (current_time-createdtime)/60
			
			if duebytime_difference_m<alert_minutes_limit and duebytime_difference_m>-31 and 'technician' in workorder.keys() and workorder['technician'] in telegram_users.keys():
				message='Заявка: '+workorder['workorderid']+ \
					'\n'+workorder['subject']+ \
					'\n'+'http://help.icecorp.ru/WorkOrder.do?woMode=viewWO&woID='+workorder['workorderid'] +\
					'\nОт: '+workorder['requester']+ \
					'\nНа: '+workorder['technician']+' '+telegram_users[workorder['technician']]+ \
					'\n'+( 'Истекает через '+str(int(duebytime_difference_m))+' мин.' if int(duebytime_difference_m)>0 else 'Просрочена '+str(int(-duebytime_difference_m))+' мин. назад.' )
				event_count+=1
				send_to_telegram(message)
			
			if createdtime_difference_m>=5 and 'technician' not in workorder.keys():
				message='Заявка: '+workorder['workorderid']+ \
					'\n'+workorder['subject']+ \
					'\n'+'http://help.icecorp.ru/WorkOrder.do?woMode=viewWO&woID='+workorder['workorderid'] +\
					'\nОт: '+workorder['requester']+ \
					'\n'+( 'Создана '+str(int(createdtime_difference_m))+' мин. назад и не имеет исполнителя.' )
				event_count+=1
				send_to_telegram(message)
				
		if event_count==0:
			return('ok')
		else:
			return('sent '+str(event_count)+' events')

send_to_telegram(str(datetime.datetime.now())+' sdp monitoring started')

while True:
	
	now = datetime.datetime.now()
	if now.hour>=check_hour_start and now.hour<check_hour_end and today_is_holiday()==False:
		print(str(now.year)+'.'+str(now.month)+'.'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second)+' '+str(check()))
	time.sleep(check_minutes_interval*60)
	
