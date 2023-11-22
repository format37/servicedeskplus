from aiohttp import web
import datetime
import pymssql
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_sql():
	sql_login='ICECORP\\1c_sql'
	sql_pass='dpCEoF1e4A6XPOL'
	return pymssql.connect(server='10.2.4.124', user=sql_login, password=sql_pass, database='sdp')
	
# create table ats_requests( ID_column INT NOT NULL IDENTITY(1,1) PRIMARY KEY, created_by varchar(64), caller_phone_number varchar(16), department varchar(64), receiver_phone_number varchar(16), event_date DATETIME );

def queue_create(created_by, caller_phone_number, department, receiver_phone_number):
	event_date = time.strftime('%Y-%m-%d %H:%M:%S')
	conn = connect_sql()
	cursor = conn.cursor()
	query	= "insert into ats_requests(created_by,caller_phone_number,department,receiver_phone_number,event_date) values ('"+created_by+"','"+caller_phone_number+"','"+department+"','"+receiver_phone_number+"','"+event_date+"');"
	#query ="select * from ats_requests"
	cursor.execute(query)
	conn.commit()

async def sdp_bid_create(request):
	# print('\n======= sdp create by ats:',datetime.datetime.now())
	logger.info('======= sdp create by ats')
	created_by 				= request.rel_url.query['created_by']				# Петров М.В.
	caller_phone_number		= request.rel_url.query['caller_phone_number']		# 2001 - имя хоста от Nagios	
	department				= request.rel_url.query['department']				# MRM
	receiver_phone_number	= request.rel_url.query['receiver_phone_number']	# SIP/1611 - звонок принят	
	queue_create(created_by, caller_phone_number, department, receiver_phone_number)
	response = 'k'
	return web.Response(text=response,content_type="text/html")