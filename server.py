import web
import csv
import json
from local_settings import *
import requests
from urlparse import parse_qs
import random
urls = (
	'/store_token/(.*)', 'store_token',
	)


def get_long_token(short_token):
	data = {
		'grant_type':'fb_exchange_token',
		'client_id': APP_ID,
		'client_secret': APP_SECRET,
		'fb_exchange_token':short_token
	}
	r = requests.get('https://graph.facebook.com/oauth/access_token', params = data)
	parsed_response = parse_qs(r.text)
	# this returns a dict where the values are lists
	# the important keys are 'access_token' and 'expires'
	return parsed_response['access_token'][0], parsed_response['expires'][0]

def store_response_data(response):
	# important attributes are .accessToken and .expiresIn and .userID
	access_token = response.accessToken
	fb_user_id = response.userID
	# this accessToken is a shortlived token
	# we can use it to get a long lived one that the server can use
	long_token, long_token_expire = get_long_token(access_token)
	# store these to database along with user id
	print '\n\n'
	print long_token, long_token_expire
	# for now
	return long_token


def refresh_token(old_token):
	# not sure about this
	# confirmed no go
	data = {
		'grant_type':'fb_exchange_token',
		'client_id': APP_ID,
		'client_secret': APP_SECRET,
		'fb_exchange_token':old_token
	}
	r = requests.get('https://graph.facebook.com/oauth/access_token', params = data)
	print r.text
	parsed_response = parse_qs(r.text)
	# this returns a dict where the values are lists
	# the important keys are 'access_token' and 'expires'
	return parsed_response['access_token'][0], parsed_response['expires'][0]

def post_message(long_token):
	print '\n\nposting message with token: ',long_token
	payload = {
		'message':'Hello World {}'.format(random.random()),
		'access_token':long_token
	}
	r = requests.post('https://graph.facebook.com/me/feed', data=payload)

class store_token:
	def GET(self,name):
		pass
	def POST(self,name):
		post_data = web.input()
		print 11111
		long_token = store_response_data(post_data)
		print 22222
		post_message(long_token)
		print 33333
		new_token, new_expire = refresh_token(long_token)
		print 44444
		print new_token,new_expire
		post_message(new_token)
		print 55555
		# post_data = json.loads(web.data())
		# print post_data
		# lines = post_data['history']
		# with open('history.csv','wb') as f:
		# 	writer = csv.writer(f)
		# 	for line in lines:
		# 		writer.writerow(line)
		
		web.header('Access-Control-Allow-Origin','*')
		web.header('Access-Control-Allow-Credentials', 'true')
		# # # web.header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
		# web.header("Access-Control-Expose-Headers: Access-Control-Allow-Origin")
		# web.header("Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept")
		return json.dumps({'message':'Hey'})

	def OPTIONS(self,name):
		web.header('Access-Control-Allow-Credentials', 'true')
		web.header('Access-Control-Allow-Origin','*')
		# web.header('Access-Control-Allow-Headers','Content-Type')
		web.header('Access-Control-Allow-Methods','GET,POST')
		web.header("Access-Control-Expose-Headers: Access-Control-Allow-Origin")
		web.header("Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept")
		return ''

if __name__ == '__main__':
	app = web.application(urls,globals())
	app.run()
